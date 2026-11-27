"""After the pre-registered run (exploratory, post hoc): image stamps and a position-specific null test.
Position test: for each plate, the fraction of 2000 random unmasked points (90"-420" from the prediction) where the
max z within R of the point is >= the max z within R of the measured peak's predicted point (R = 4")."""
import json, gzip, io, math, random, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
D = M.D; preds = json.load(open(D / "predictions.json")); cats = json.load(open(D / "refcat.json"))
res = {r["plate"]: r for r in json.load(open(D / "results.json"))["plates"]}
fig, axs = plt.subplots(2, 6, figsize=(18, 6.6)); axs = axs.ravel(); rng = random.Random(2); out = {}
for ax, p in zip(axs, preds):
    h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / f"{p['plate']}_s{p['solnum']}.fits.gz").read_bytes())))
    img = h[0].data.astype(float); w = WCS(h[0].header); z = M.zimage(img)
    jd = min(p["track"], key=lambda t: abs(t["jd"] - Time(p["mid"] + ":00").jd))["jd"]
    stars = M.stars_at_epoch(cats[p["plate"]], jd); s2p, fit = M.refit(z, w, stars, p["lim"])
    tr = [t for t in p["track"] if abs(t["jd"] - jd) * 24 <= 1.0001]
    tp = s2p(np.array([t["ra"] for t in tr]), np.array([t["dec"] for t in tr]))
    mid = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
    R = 4 / 1.44; Y, X = np.mgrid[0:835, 0:835]
    def zmax(x, y):
        x0, y0 = int(x), int(y); sub = z[y0-4:y0+5, x0-4:x0+5]; yy, xx = np.mgrid[y0-4:y0+5, x0-4:x0+5]
        return float(sub[np.hypot(xx - x, yy - y) <= R].max())
    obs = zmax(*mid)
    vis = [s for s in stars if s[2] < p["lim"] + 1]
    sp = s2p(np.array([s[0] for s in vis]), np.array([s[1] for s in vis])) if vis else np.zeros((0, 2))
    sr = [(8 + 6 * max(0, p["lim"] - s[2])) / 1.44 for s in vis]
    ctrl = []
    while len(ctrl) < 2000:
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(90, 420) / 1.44
        x, y = mid[0] + r * math.cos(a), mid[1] + r * math.sin(a)
        if not (30 < x < 805 and 30 < y < 805): continue
        if len(sp) and np.any(np.hypot(sp[:, 0] - x, sp[:, 1] - y) < np.array(sr)): continue
        ctrl.append(zmax(x, y))
    frac = float(np.mean(np.array(ctrl) >= obs)); out[p["plate"]] = {"z_at_prediction_4arcsec": obs, "frac_random_ge": frac}
    half = 60
    cx, cy = mid
    st = img[int(cy)-half:int(cy)+half, int(cx)-half:int(cx)+half]
    lo, hi = np.percentile(st, [5, 99.5])
    ax.imshow(st, origin="lower", cmap="gray_r", vmin=lo, vmax=hi, extent=[-half*1.44, half*1.44, -half*1.44, half*1.44])
    ax.plot((tp[:, 0] - cx) * 1.44, (tp[:, 1] - cy) * 1.44, "r-", lw=0.6, alpha=0.6)
    ax.add_patch(plt.Circle((0, 0), 10, fill=False, color="r", lw=0.8))
    r_ = res[p["plate"]]
    ax.set_title(f"{p['object']} {p['plate']} {p['mid'][:10]}\nV={p['V']:.1f} lim={p['lim']:.1f} S={r_['S']:.1f} {'PASS' if r_['pass'] else 'no'}", fontsize=9)
    ax.tick_params(labelsize=6)
    print(p["plate"], f"z(4\" of prediction)={obs:.1f}  fraction of random points >= : {frac:.4f}")
axs[-1].axis("off")
fig.suptitle("DASCH cutouts, 173\" x 173\", centred on the predicted midpoint position (red circle r=10\", red line = track +-1 h)", fontsize=10)
fig.tight_layout(); fig.savefig(D / "stamps.png", dpi=110)
(D / "posthoc_position_test.json").write_text(json.dumps(out, indent=1))
