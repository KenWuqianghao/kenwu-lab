"""Round 3: (624) Hektor on Heidelberg (HDAP) plates. Usage:
  hdap.py predict   -> data/hdap/predictions.json  (Horizons, site 024 Heidelberg-Konigstuhl, start..end of exposure)
  hdap.py fetch     -> data/hdap/cutouts/*.fits (SODA, radius 0.2 deg), data/hdap/refcat.json (ATLAS via DASCH, 900")
  hdap.py measure   -> data/hdap/results.json
Measurement (pre-registered, PROTOCOL.md round 3):
 - Image polarity: the sign for which z peaks match more catalogued stars (m < 15) in the shift search.
 - z image: Gaussian(3") minus Gaussian(30") of the signal image, divided by 1.4826 * MAD.
 - Astrometric refit to ATLAS stars (proper motion to the epoch): integer shift search +-60", then affine if >= 6
   matches, shift if 3-5, plate WCS if < 3.
 - Trail: predicted positions from exposure start to end. Statistic S = max over time shifts dt in -60..+60 min
   (5-min steps) of the mean z along the trail shifted by dt (1-px sampling), unmasked points only.
 - Mask: ATLAS stars m < 16.5, radius 8" + 6" * max(0, 15.5 - m). A plate is not measurable if > 30% of the
   nominal (dt = 0) trail is masked.
 - Null: 2000 random translations (90"-600") of the whole trail family inside the cutout with <= 30% masked;
   p = (1 + #(S_ctrl >= S)) / 2001.
Decision: set A = plates with mid-exposure before 1904-09-13; set B = all plates. For each set, "detected" if the
Fisher combination of p over measurable plates is < 0.001 and at least 2 plates have p < 0.01."""
import csv, json, math, os, random, sys, time, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np

warnings.filterwarnings("ignore")
D = (Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data") / "hdap"
MIN_EDGE = 0.1
RECORD_DATE = "1904-09-13"


def selected():
    rows = list(csv.DictReader(open(Path(__file__).resolve().parent.parent / "data" / "hdap" / "hektor_cover.csv")))
    return [r for r in rows if float(r["edge_deg"]) >= MIN_EDGE]


def predict():
    import hz
    from astropy.time import Time, TimeDelta
    out = []
    for r in selected():
        t0 = Time(r["start"], scale="utc"); t1 = Time(r["end"], scale="utc") if r["end"] else t0 + TimeDelta(float(r["exposure_s"]), format="sec")
        a = (t0 - TimeDelta(3900, format="sec")).iso[:16]; b = (t1 + TimeDelta(3900, format="sec")).iso[:16]
        eph = hz.eph("624;", a, b, "2m", center="024@399", quantities="1,9")
        tr = [{"jd": float(e["Date_________JDUT"]), "ra": float(e["R.A._(ICRF)"]), "dec": float(e["DEC_(ICRF)"]), "V": hz.num(e["APmag"])}
              for e in eph]
        assert all(t["V"] is not None for t in tr), r["plate"]
        mid = (t0.jd + t1.jd) / 2; m = min(tr, key=lambda x: abs(x["jd"] - mid))
        out.append({"plate": r["plate"], "inst": r["inst"], "start": r["start"], "end": t1.isot[:19], "jd_start": t0.jd, "jd_end": t1.jd,
                    "accref": r["accref"], "ra": m["ra"], "dec": m["dec"], "V": m["V"], "offset_deg": float(r["offset_deg"]),
                    "edge_deg": float(r["edge_deg"]), "track": tr})
        print(r["plate"], r["start"], f"V={m['V']:.2f}", f"{(t1.jd - t0.jd) * 24:.2f} h")
    D.mkdir(parents=True, exist_ok=True)
    (D / "predictions.json").write_text(json.dumps(out, indent=1))


def fetch():
    import requests, dasch
    preds = json.load(open(D / "predictions.json")); (D / "cutouts").mkdir(parents=True, exist_ok=True)
    cat = json.load(open(D / "refcat.json")) if (D / "refcat.json").exists() else {}
    for p in preds:
        f = D / "cutouts" / f"{p['plate']}.fits"
        if not f.exists():
            path = p["accref"].split("/getproduct/")[1]
            r = requests.get("http://dc.g-vo.org/lswscans/res/positions/dl/dlget",
                             params={"ID": "ivo://org.gavo.dc/~?" + path, "CIRCLE": f"{p['ra']} {p['dec']} 0.2"}, timeout=600)
            ok = r.status_code == 200 and r.content[:6] == b"SIMPLE"
            with open(D / "cutouts" / "log.jsonl", "a") as lg:
                lg.write(json.dumps({"plate": p["plate"], "url": r.url, "status": r.status_code, "bytes": len(r.content), "ok": ok}) + "\n")
            if ok:
                f.write_bytes(r.content)
            print(p["plate"], r.status_code, len(r.content)); time.sleep(3)
        if p["plate"] not in cat:
            cat[p["plate"]] = dasch.querycat(p["ra"], p["dec"], 900); (D / "refcat.json").write_text(json.dumps(cat))


def measure():
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.time import Time
    from scipy.ndimage import gaussian_filter, maximum_filter, map_coordinates
    from scipy.stats import chi2
    import measure as M
    preds = json.load(open(D / "predictions.json")); cats = json.load(open(D / "refcat.json")); rng = random.Random(4); rows = []
    for p in preds:
        f = D / "cutouts" / f"{p['plate']}.fits"
        if not f.exists():
            rows.append({"plate": p["plate"], "start": p["start"], "measurable": False, "reason": "no cutout"}); continue
        h = fits.open(f); img = h[0].data.astype(float); w = WCS(h[0].header)
        scale = float(np.sqrt(abs(np.linalg.det(w.celestial.pixel_scale_matrix))) * 3600)
        mid = (p["jd_start"] + p["jd_end"]) / 2
        stars = M.stars_at_epoch(cats[p["plate"]], mid)
        sxy = np.array(w.world_to_pixel_values([s[0] for s in stars], [s[1] for s in stars])).T if stars else np.zeros((0, 2))
        smag = np.array([s[2] for s in stars])

        def zimg(sig):
            z = gaussian_filter(sig, 3 / scale) - gaussian_filter(sig, 30 / scale)
            c = z[20:-20, 20:-20]
            return z / (1.4826 * np.median(np.abs(c - np.median(c))))

        def match(z, pts):
            mx = maximum_filter(z, size=5); ys, xs = np.nonzero((z == mx) & (z > 6)); pk = np.column_stack([xs, ys]).astype(float)
            if len(pk) == 0 or len(pts) == 0:
                return (0, 0, 0), pk
            g = int(round(60 / scale)); best = (-1, 0, 0)
            for dx in range(-g, g + 1, max(1, g // 30)):
                for dy in range(-g, g + 1, max(1, g // 30)):
                    q = pts + [dx, dy]
                    d = np.min(np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]), axis=0)
                    n = int(np.sum(d < max(2, 3 / scale)))
                    if n > best[0]:
                        best = (n, dx, dy)
            return best, pk
        bright = sxy[smag < 15] if len(sxy) else sxy
        cand = []
        for sgn in (1, -1):
            z = zimg(sgn * img); (n, dx, dy), pk = match(z, bright); cand.append((n, sgn, z, dx, dy, pk))
        n, sgn, z, dx, dy, pk = max(cand, key=lambda c: c[0])
        # refine
        q = bright + [dx, dy]
        if n >= 3:
            dd = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]); j = np.argmin(dd, axis=0)
            ok = dd[j, np.arange(len(q))] < max(2, 3 / scale); src, dst = bright[ok], pk[j[ok]]
            if len(src) >= 6:
                Mx, *_ = np.linalg.lstsq(np.column_stack([src, np.ones(len(src))]), dst, rcond=None)
                T = lambda P: np.column_stack([P, np.ones(len(P))]) @ Mx; kind = "affine"
            else:
                sh = np.mean(dst - src, axis=0); T = lambda P: P + sh; kind = "shift"
            rms = float(np.sqrt(np.mean(np.sum((T(src) - dst) ** 2, axis=1))) * scale); nfit = int(len(src))
        else:
            T = lambda P: P; kind = "none"; rms = None; nfit = int(n)
        s2p = lambda ra, de: T(np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T))
        mpts = s2p(np.array([s[0] for s in stars]), np.array([s[1] for s in stars])) if stars else np.zeros((0, 2))
        keepm = smag < 16.5; mpts = mpts[keepm] if len(mpts) else mpts
        mr = np.array([(8 + 6 * max(0, 15.5 - m)) / scale for m in smag[keepm]])
        tr = p["track"]; tj = np.array([t["jd"] for t in tr])

        def trail(dt_min):
            a, b = p["jd_start"] + dt_min / 1440, p["jd_end"] + dt_min / 1440
            ts = np.linspace(a, b, 50)
            ra = np.interp(ts, tj, np.unwrap(np.radians([t["ra"] for t in tr]))); de = np.interp(ts, tj, [t["dec"] for t in tr])
            P = s2p(np.degrees(ra) % 360, de)
            L = float(np.sum(np.hypot(*np.diff(P, axis=0).T))); n = max(2, int(L) + 1)
            u = np.linspace(0, 1, n); x = np.interp(u, np.linspace(0, 1, len(P)), P[:, 0]); y = np.interp(u, np.linspace(0, 1, len(P)), P[:, 1])
            return np.column_stack([x, y])
        fam = [trail(d) for d in range(-60, 61, 5)]
        nominal = fam[12]

        def masked(P):
            if len(mpts) == 0:
                return np.zeros(len(P), bool)
            d = np.hypot(P[:, None, 0] - mpts[None, :, 0], P[:, None, 1] - mpts[None, :, 1])
            return np.any(d < mr[None, :], axis=1)

        def S(off):
            vals = []
            for P in fam:
                Q = P + off
                if Q[:, 0].min() < 10 or Q[:, 1].min() < 10 or Q[:, 0].max() > z.shape[1] - 10 or Q[:, 1].max() > z.shape[0] - 10:
                    return None
                mk = masked(Q)
                if mk.mean() > 0.3 and P is nominal:
                    return None
                if (~mk).sum() == 0:
                    continue
                vals.append(float(map_coordinates(z, [Q[~mk, 1], Q[~mk, 0]], order=1).mean()))
            return max(vals) if vals else None
        obs = S(np.zeros(2))
        row = {"plate": p["plate"], "inst": p["inst"], "start": p["start"], "V": p["V"], "scale_arcsec_px": scale, "polarity": sgn,
               "fit": {"kind": kind, "n": nfit, "rms_arcsec": rms,
                       "shift_px_at_centre": [float(v) for v in (T(np.array([[img.shape[1] / 2, img.shape[0] / 2]])) - [img.shape[1] / 2, img.shape[0] / 2])[0]]}, "trail_arcsec": float(np.sum(np.hypot(*np.diff(nominal, axis=0).T)) * scale)}
        if obs is None:
            row.update(measurable=False, reason="trail > 30% masked or outside cutout"); rows.append(row)
            print(p["plate"], "not measurable"); continue
        ctrl = []; tries = 0
        while len(ctrl) < 2000 and tries < 20000:
            tries += 1; a = rng.uniform(0, 2 * math.pi); r = rng.uniform(90, 600) / scale
            v = S(np.array([r * math.cos(a), r * math.sin(a)]))
            if v is not None:
                ctrl.append(v)
        pv = (1 + sum(c >= obs for c in ctrl)) / (len(ctrl) + 1)
        row.update(measurable=True, S=obs, n_ctrl=len(ctrl), p=pv); rows.append(row)
        print(f"{p['plate']} {p['start']} {p['inst'][:12]} V={p['V']:.2f} pol={sgn} fit={kind} n={nfit} rms={rms} "
              f"trail={row['trail_arcsec']:.0f}\" S={obs:.2f} p={pv:.4f} (n_ctrl={len(ctrl)})")
    summ = {}
    for name, sel in (("A_before_1904-09-13", lambda r: r["start"] < RECORD_DATE), ("B_all", lambda r: True)):
        ms = [r for r in rows if r.get("measurable") and sel(r)]
        X = -2 * sum(math.log(r["p"]) for r in ms); pc = float(chi2.sf(X, 2 * len(ms))) if ms else 1.0
        strong = [r for r in ms if r["p"] < 0.01]
        summ[name] = {"n_measurable": len(ms), "p_comb": pc, "n_p_lt_0.01": len(strong), "detected": pc < 0.001 and len(strong) >= 2,
                      "earliest_p_lt_0.01": min((r["start"] for r in strong), default=None)}
        print(name, summ[name])
    (D / "results.json").write_text(json.dumps({"plates": rows, "summary": summ}, indent=1))


if __name__ == "__main__":
    {"predict": predict, "fetch": fetch, "measure": measure}[sys.argv[1]]()
