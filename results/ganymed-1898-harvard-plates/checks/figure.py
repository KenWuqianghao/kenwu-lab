"""Figure 1 of the paper: the six Ganymed plates of round 1, centred on the predicted midpoint position.
Red line: predicted track during the exposure. Red circle: r = 10". Blue cross: measured position (region method).
Usage: PRECOVERY_DATA=DIR python3 checks/figure.py OUT.png   (DIR = a data directory written by checks/rerun.py --data DIR)
Needs matplotlib in addition to checks/requirements.txt. Not run by CI."""
import gzip, io, json, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
D = M.D; SCALE = 1.44; HALF = 45  # px; 1.44"/px on the DASCH cutouts, stamp 130" x 130"
preds = [p for p in json.load(open(D / "predictions.json")) if p["object"] == "Ganymed"]
cats = json.load(open(D / "refcat.json")); res = {r["plate"]: r for r in json.load(open(D / "results.json"))["plates"]}
ast = json.load(open(D / "astrometry.json"))["region"]
fig, axs = plt.subplots(2, 3, figsize=(10, 7.2))
for ax, p in zip(axs.ravel(), sorted(preds, key=lambda q: q["mid"])):
    h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / f"{p['plate']}_s{p['solnum']}.fits.gz").read_bytes())))
    img = h[0].data.astype(float); w = WCS(h[0].header); z = M.zimage(img)
    jd = Time(p["mid"] + ":00").jd
    s2p, _ = M.refit(z, w, M.stars_at_epoch(cats[p["plate"]], jd), p["lim"])
    tr = [t for t in p["track"] if abs(t["jd"] - jd) * 1440 <= p["exptime_min"] / 2 + 1e-6]
    tp = s2p(np.array([t["ra"] for t in tr]), np.array([t["dec"] for t in tr]))
    cx, cy = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
    x0, x1 = max(int(cx) - HALF, 0), min(int(cx) + HALF, img.shape[1]); y0, y1 = max(int(cy) - HALF, 0), min(int(cy) + HALF, img.shape[0])
    st = img[y0:y1, x0:x1]; lo, hi = np.percentile(st, [5, 99.7])
    ax.imshow(st, origin="lower", cmap="gray_r", vmin=lo, vmax=hi,
              extent=[(x0 - cx) * SCALE, (x1 - cx) * SCALE, (y0 - cy) * SCALE, (y1 - cy) * SCALE])
    ax.plot((tp[:, 0] - cx) * SCALE, (tp[:, 1] - cy) * SCALE, "r-", lw=1.2)
    ax.add_patch(plt.Circle((0, 0), 10, fill=False, color="r", lw=0.8))
    if p["plate"] in ast:
        mx, my = s2p(np.array([ast[p["plate"]]["ra_deg"]]), np.array([ast[p["plate"]]["dec_deg"]]))[0]
        ax.plot([(mx - cx) * SCALE], [(my - cy) * SCALE], "+", color="tab:blue", ms=9, mew=1.2)
    r = res[p["plate"]]
    ax.set_title(f"{p['plate']}  {p['mid'][:10]}  {p['exptime_min']} min\nV = {p['V']:.1f}, S = {r['S']:.1f} ({'pass' if r['pass'] else 'no pass'})", fontsize=9)
    ax.set_xlim(-HALF * SCALE, HALF * SCALE); ax.set_ylim(-HALF * SCALE, HALF * SCALE); ax.tick_params(labelsize=7)
fig.supxlabel("arcsec (cutout x axis)", fontsize=9); fig.supylabel("arcsec (cutout y axis)", fontsize=9)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=150)
print("wrote", sys.argv[1])
