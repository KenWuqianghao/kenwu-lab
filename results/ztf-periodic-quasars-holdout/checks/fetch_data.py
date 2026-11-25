"""Download the public inputs.

1. SDSS DR14Q catalogue (Paris et al. 2018) from the SDSS SAS: redshift and PSF r
   magnitude for the 86 SPL candidates of Chen et al. (2024), names from
   data/candidate_names.txt.
2. A matched placebo set of DR14Q quasars (4 per candidate, matched in r magnitude
   and redshift, fixed seed).
3. ZTF r-band light curves (IRSA nph_light_curves, 3 arcsec radius, all epochs).

Outputs go to work/ (raw) and data/ (small tables). Re-running skips files that
already exist.
"""
import concurrent.futures as cf
import io
import os
import re
import sys
import time

import numpy as np
import pandas as pd
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
LCDIR = os.path.join(WORK, "lc")
DATA = os.path.join(ROOT, "data")
TWOQZ_URL = "http://www.2dfquasar.org/Spec_Cat/cat/2QZ_6QZ_pubcat.txt"
DR14Q_URL = "https://data.sdss.org/sas/dr14/eboss/qso/DR14Q/DR14Q_v4_4.fits"
IRSA = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
SEED = 20261124
N_PLACEBO_PER = 4


def parse_sdss(name):
    m = re.match(r"SDSS J(\d\d)(\d\d)(\d\d\.\d\d)([+-])(\d\d)(\d\d)(\d\d\.\d)", name)
    h, mi, s, sg, d, dm, ds = m.groups()
    ra = 15 * (int(h) + int(mi) / 60 + float(s) / 3600)
    dec = int(d) + int(dm) / 60 + float(ds) / 3600
    return ra, (-dec if sg == "-" else dec)


def load_dr14q():
    """Columns needed from the SDSS DR14Q catalogue (Paris et al. 2018), as a DataFrame."""
    out = os.path.join(WORK, "dr14q_slim.csv")
    if os.path.exists(out):
        return pd.read_csv(out)
    from astropy.io import fits
    fz = os.path.join(WORK, "sdss", "DR14Q_v4_4.fits")
    if not os.path.exists(fz):
        os.makedirs(os.path.dirname(fz), exist_ok=True)
        with requests.get(DR14Q_URL, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(fz + ".tmp", "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        os.replace(fz + ".tmp", fz)
    with fits.open(os.path.join(WORK, "sdss", "DR14Q_v4_4.fits"), memmap=True) as h:
        d = h[1].data
        df = pd.DataFrame(dict(sdss_name=np.asarray(d["SDSS_NAME"]).astype(str), ra=np.asarray(d["RA"], float),
                               dec=np.asarray(d["DEC"], float), z=np.asarray(d["Z"], float),
                               rmag=np.asarray(d["PSFMAG"][:, 2], float), plate=np.asarray(d["PLATE"]).astype(np.int64),
                               fiber=np.asarray(d["FIBERID"]).astype(np.int64), mjd=np.asarray(d["MJD"]).astype(np.int64)))
    df.to_csv(out, index=False)
    return df


def nearest(q, ra, dec):
    d = np.hypot((q.ra.values - ra) * np.cos(np.radians(dec)), q.dec.values - dec) * 3600
    i = int(np.argmin(d))
    return i, d[i]


def twoqz(ra_prefix, dec_prefix):
    """Position, z and r (= bJ - (bJ-r)) from the 2QZ/6QZ public catalogue (Croom et al. 2004)."""
    f = os.path.join(WORK, "2qz", "2QZ_6QZ_pubcat.txt")
    if not os.path.exists(f):
        os.makedirs(os.path.dirname(f), exist_ok=True)
        r = requests.get(TWOQZ_URL, timeout=600)
        r.raise_for_status()
        open(f, "w").write(r.text)
    hits = []
    for line in open(f):
        p = line.split()
        if p[0].startswith(ra_prefix) and p[0][9:14] == dec_prefix:
            hits.append(p)
    assert len(hits) == 1, hits
    p = hits[0]
    ra = 15 * (int(p[1]) + int(p[2]) / 60 + float(p[3]) / 3600)
    dec = (1 if p[4][0] == "+" else -1) * (abs(int(p[4])) + int(p[5]) / 60 + float(p[6]) / 3600)
    bj, bjr, z = float(p[21]), float(p[23]), float(p[25])
    return ra, dec, z, bj - bjr, p[0]


def candidates():
    """86 SPL candidates. Coordinates from the SDSS names; z and r from DR14Q (nearest within 2 arcsec)."""
    out = os.path.join(DATA, "candidates.csv")
    if os.path.exists(out):
        return pd.read_csv(out)
    names = [l.strip() for l in open(os.path.join(ROOT, "data/candidate_names.txt")) if l.strip()]
    q = load_dr14q()
    rows = []
    for n in names:
        if n.startswith("SDSS"):
            ra, dec = parse_sdss(n)
            i, d = nearest(q, ra, dec)
            ok = d < 2.0
        else:
            # 2QZJ131914+0027: truncated name; not in DR14Q. Unique 2QZ catalogue match J131914.8+002709.
            ra, dec, z, rmag, nm = twoqz("J131914", "+0027")
            rows.append(dict(id="C%02d" % len(rows), name=n, ra=ra, dec=dec, z=z, rmag=rmag, dr14q="2QZ " + nm))
            continue
        rows.append(dict(id="C%02d" % len(rows), name=n, ra=ra, dec=dec, z=q.z[i] if ok else np.nan,
                         rmag=q.rmag[i] if ok else np.nan, dr14q=q.sdss_name[i] if ok else ""))
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    return df


def placebo(cand):
    """4 DR14Q quasars per candidate with |dr|<0.3 mag and |dz|<0.3, not within 10 arcsec of a candidate,
    r<=20, Dec>-28; drawn without replacement with a fixed seed."""
    out = os.path.join(DATA, "placebo.csv")
    if os.path.exists(out):
        return pd.read_csv(out)
    pool = load_dr14q()
    pool = pool[(pool.rmag > 14) & (pool.rmag <= 20.0) & (pool.dec > -28) & (pool.z > 0)].reset_index(drop=True)
    keep = np.ones(len(pool), bool)
    for _, c in cand.iterrows():
        if np.isfinite(c.ra):
            d = np.hypot((pool.ra - c.ra) * np.cos(np.radians(c.dec)), pool.dec - c.dec) * 3600
            keep &= d.values > 10
    pool = pool[keep].reset_index(drop=True)
    rng = np.random.default_rng(SEED)
    used = set()
    rows = []
    for _, c in cand.iterrows():
        rmag = c.rmag if np.isfinite(c.rmag) else 18.5
        z = c.z if np.isfinite(c.z) else 1.0
        ok = np.where((abs(pool.rmag - rmag) < 0.3) & (abs(pool.z - z) < 0.3))[0]
        ok = np.array([i for i in ok if i not in used])
        pick = rng.choice(ok, size=N_PLACEBO_PER, replace=False)
        for i in pick:
            used.add(int(i))
            p = pool.iloc[i]
            rows.append(dict(id="P%03d" % len(rows), match=c.id, sdss_name=p.sdss_name, ra=p.ra, dec=p.dec,
                             z=p.z, rmag=p.rmag))
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    return df


def fetch_lc(oid, ra, dec):
    f = os.path.join(LCDIR, oid + ".csv")
    if os.path.exists(f) and os.path.getsize(f) > 0:
        return oid, "cached"
    for k in range(6):
        try:
            r = requests.get(IRSA, params={"POS": "CIRCLE %.7f %.7f 0.000833" % (ra, dec), "BANDNAME": "r",
                                           "FORMAT": "csv"}, timeout=180)
            r.raise_for_status()
            if not r.text.startswith("oid"):
                raise RuntimeError(r.text[:200])
            with open(f + ".tmp", "w") as fh:
                fh.write(r.text)
            os.replace(f + ".tmp", f)
            return oid, "ok %d lines" % r.text.count("\n")
        except Exception as e:
            time.sleep(10 * (k + 1))
            err = e
    return oid, "FAILED %s" % err


def main():
    os.makedirs(LCDIR, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "names-only":
        names = [l.strip() for l in open(os.path.join(ROOT, "data/candidate_names.txt")) if l.strip()]
        jobs = [("C%02d" % i, *parse_sdss(n)) for i, n in enumerate(names) if n.startswith("SDSS")]
    else:
        cand = candidates()
        plac = placebo(cand)
        jobs = [(r.id, r.ra, r.dec) for r in cand.itertuples() if np.isfinite(r.ra)]
        jobs += [(r.id, r.ra, r.dec) for r in plac.itertuples()]
    with cf.ThreadPoolExecutor(4) as ex:
        for oid, st in ex.map(lambda a: fetch_lc(*a), jobs):
            print(oid, st, flush=True)


if __name__ == "__main__":
    main()
