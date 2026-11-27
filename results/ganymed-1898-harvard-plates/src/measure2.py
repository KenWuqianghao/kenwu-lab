"""Round 2, pre-registered (PROTOCOL.md, Round 2). Usage: measure2.py PREDICTIONS.json OUT.json
Per plate: astrometric refit as in measure.py; P = predicted midpoint position (corrected pixels).
 - Not measurable if P lies inside the mask of a catalogued star (m < lim + 1, r = 8" + 6" * max(0, lim - m)).
 - z5 = max z within 5" of P.
 - Null: 2000 random unmasked points 90"-420" from P inside the cutout (seed 3); p = (1 + #(z5_ctrl >= z5)) / 2001.
Decision: Fisher combination over measurable plates; "detected" if p_comb < 0.001 and >= 2 plates have p < 0.01."""
import gzip, io, json, math, random, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.stats import chi2

warnings.filterwarnings("ignore")
R_ARCSEC = 5.0
NCTRL = 2000


def zmax(z, x, y, r):
    x0, y0, k = int(x), int(y), int(math.ceil(r)) + 1
    yy, xx = np.mgrid[y0 - k:y0 + k + 1, x0 - k:x0 + k + 1]
    sub = z[y0 - k:y0 + k + 1, x0 - k:x0 + k + 1]
    return float(sub[np.hypot(xx - x, yy - y) <= r].max())


def main(pred_file, out_file):
    preds = json.load(open(pred_file)); cats = json.load(open(M.D / "refcat.json"))
    rng = random.Random(3); rows = []
    for p in preds:
        cf = M.D / "cutouts" / f"{p['plate']}_s{p['solnum']}.fits.gz"
        if not cf.exists():
            rows.append({"plate": p["plate"], "mid": p["mid"], "measurable": False, "reason": "no cutout (plate does not cover the position)"})
            print(f"{p['plate']} {p['mid']} not covered"); continue
        h = fits.open(io.BytesIO(gzip.decompress((M.D / "cutouts" / f"{p['plate']}_s{p['solnum']}.fits.gz").read_bytes())))
        img = h[0].data.astype(float); w = WCS(h[0].header); z = M.zimage(img)
        jd = min(p["track"], key=lambda t: abs(t["jd"] - Time(p["mid"] + ":00").jd))["jd"]
        stars = M.stars_at_epoch(cats[p["plate"]], jd)
        s2p, fit = M.refit(z, w, stars, p["lim"])
        P = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
        vis = [s for s in stars if s[2] < p["lim"] + 1]
        sp = s2p(np.array([s[0] for s in vis]), np.array([s[1] for s in vis])) if vis else np.zeros((0, 2))
        sr = np.array([(8 + 6 * max(0, p["lim"] - s[2])) / 1.44 for s in vis])
        masked = lambda x, y: bool(len(sp)) and bool(np.any(np.hypot(sp[:, 0] - x, sp[:, 1] - y) < sr))
        row = {"plate": p["plate"], "mid": p["mid"], "V": p["V"], "lim": p["lim"], "fit": fit}
        if masked(*P):
            row.update(measurable=False); rows.append(row)
            print(f"{p['plate']} {p['mid']} not measurable (catalogued star mask)"); continue
        r = R_ARCSEC / 1.44; obs = zmax(z, *P, r); ctrl = []
        while len(ctrl) < NCTRL:
            a = rng.uniform(0, 2 * math.pi); d = rng.uniform(90, 420) / 1.44
            x, y = P[0] + d * math.cos(a), P[1] + d * math.sin(a)
            if 30 < x < 805 and 30 < y < 805 and not masked(x, y):
                ctrl.append(zmax(z, x, y, r))
        pv = (1 + sum(c >= obs for c in ctrl)) / (NCTRL + 1)
        row.update(measurable=True, z5=obs, p=pv); rows.append(row)
        print(f"{p['plate']} {p['mid']} V={p['V']:.2f} lim={p['lim']} fit={fit.get('kind')} n={fit['n']} rms={fit.get('rms_arcsec')} z5={obs:.1f} p={pv:.4f}")
    ms = [r for r in rows if r["measurable"]]
    X = -2 * sum(math.log(r["p"]) for r in ms); pc = float(chi2.sf(X, 2 * len(ms))) if ms else 1.0
    strong = [r for r in ms if r["p"] < 0.01]
    summary = {"n_measurable": len(ms), "fisher_X": X, "p_comb": pc, "n_p_lt_0.01": len(strong),
               "detected": pc < 0.001 and len(strong) >= 2,
               "earliest_p_lt_0.01": min((r["mid"] for r in strong), default=None)}
    print(summary)
    Path(out_file).write_text(json.dumps({"plates": rows, "summary": summary}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
