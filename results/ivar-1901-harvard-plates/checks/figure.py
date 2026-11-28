"""Figure 1 of the paper (needs matplotlib; not run by the check).
Usage: PRECOVERY_DATA=DIR python3 checks/figure.py paper/fig_ivar.png   (DIR = a data directory of checks/rerun.py)
Top row: the four passing 1901 plates, noise-normalised z image (src/measure.py), 240" x 240", centred on the
predicted midpoint position after the registered astrometric refit. Red line: predicted motion during the exposure.
Bottom row: one other-date control plate of src/controls.py at the same sky position (DASCH WCS, no refit)."""
import gzip, io, json, os, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src")); import measure as M
D = Path(os.environ["PRECOVERY_DATA"])
preds = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
cats = json.load(open(D / "refcat.json")); ctrl = json.load(open(D / "controls.json"))
plates = ["b27907", "b28342", "b28520", "b28598"]; H = 120 / 1.44
def load(f):
    h = fits.open(io.BytesIO(gzip.decompress(f.read_bytes()))); return M.zimage(h[0].data.astype(float)), WCS(h[0].header)
fig, ax = plt.subplots(2, 4, figsize=(12, 6.4))
for j, pl in enumerate(plates):
    p = preds[pl]; z, w = load(D / "cutouts" / f"{pl}_s0.fits.gz")
    jd = min(p["track"], key=lambda t: abs(t["jd"] - Time(p["mid"] + ":00").jd))["jd"]
    s2p, _ = M.refit(z, w, M.stars_at_epoch(cats[pl], jd), p["lim"])
    x0, y0 = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
    tr = [t for t in p["track"] if abs(t["jd"] - jd) * 1440 <= p["exptime_min"] / 2 + 1e-3]
    tp = s2p(np.array([t["ra"] for t in tr]), np.array([t["dec"] for t in tr]))
    a = ax[0, j]; ext = [-120, 120, -120, 120]
    sub = z[int(y0 - H):int(y0 + H), int(x0 - H):int(x0 + H)]
    a.imshow(sub, origin="lower", cmap="gray_r", vmin=-2, vmax=15, extent=ext)
    a.plot((tp[:, 0] - x0) * 1.44, (tp[:, 1] - y0) * 1.44, "r-", lw=1, alpha=0.7)
    a.set_title(f"{pl}  {p['mid'].replace('T', ' ')} UT\n{p['exptime_min']:.0f} min, V = {p['V']:.1f}", fontsize=9)
    a.tick_params(labelsize=7)
    b = ax[1, j]
    if ctrl[pl]["controls"]:
        c = ctrl[pl]["controls"][0]; zc, wc = load(D / "controls" / f"{pl}_ctrl_{c['plate']}.fits.gz")
        xc, yc = wc.world_to_pixel_values(p["ra"], p["dec"])
        b.imshow(zc[int(yc - H):int(yc + H), int(xc - H):int(xc + H)], origin="lower", cmap="gray_r", vmin=-2, vmax=15, extent=ext)
        b.add_patch(plt.Circle((0, 0), 10, fill=False, color="r", lw=1))
        b.set_title(f"control {c['plate']}  {c['expdate'][:10]}", fontsize=9)
    else:
        b.text(0.5, 0.5, "no control plate\nmet the rule", ha="center", va="center", transform=b.transAxes, fontsize=9)
        b.set_xticks([]); b.set_yticks([])
    b.tick_params(labelsize=7)
for a in ax.flat: a.set_aspect("equal")
fig.supxlabel("arcsec (x of the scan)", fontsize=9); fig.supylabel("arcsec (y of the scan)", fontsize=9)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("wrote", sys.argv[1])
