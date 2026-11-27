"""Verifier, exploratory (after seeing the image): is there a broad trail on ac00044 along the predicted motion?
Image minus a 204-px median background (computed on a 4x4-binned copy) (keeps structures up to ~100 px wide), / robust sigma of the 8-px-smoothed image.
Statistic: mean in a strip = predicted track during the 94-min exposure, half-width HW px. Controls: 3000 strips with a
random centre (>= 150 px from the prediction) and random orientation. Usage: ac00044_trail.py DATA_DIR"""
import gzip, io, json, math, random, sys
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy import ndimage as ndi
D = Path(sys.argv[1])
h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / "ac00044_s0.fits.gz").read_bytes())))[0]
img = h.data.astype(float); w = WCS(h.header)
small = img[:832, :832].reshape(208, 4, 208, 4).mean(axis=(1, 3))          # 4x4 binning, then a 51-bin (204-px) median
bg = ndi.zoom(ndi.median_filter(small, size=51), 835 / 208, order=1)[:835, :835]
d = ndi.gaussian_filter(img - bg, 8); d = d / (1.4826 * np.median(np.abs(d - np.median(d))))
p = [q for q in json.load(open(D / "predictions.json")) if q["plate"] == "ac00044"][0]
jd0 = min(p["track"], key=lambda t: abs(t["jd"] - (p["track"][0]["jd"] + p["track"][-1]["jd"]) / 2))["jd"]
tr = [t for t in p["track"] if abs(t["jd"] - jd0) * 1440 <= 47.5]
(xa, ya), (xb, yb) = [[float(v) for v in w.world_to_pixel_values(t["ra"], t["dec"])] for t in (tr[0], tr[-1])]
L = math.hypot(xb - xa, yb - ya); pa = math.degrees(math.atan2(yb - ya, xb - xa)); cx0, cy0 = (xa + xb) / 2, (ya + yb) / 2
yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
def strip(cx, cy, pa, hw):
    c, s = math.cos(math.radians(pa)), math.sin(math.radians(pa))
    u = (xx - cx) * c + (yy - cy) * s; v = -(xx - cx) * s + (yy - cy) * c
    return float(d[(np.abs(u) <= L / 2) & (np.abs(v) <= hw)].mean())
for hw in (10, 20):
    obs = strip(cx0, cy0, pa, hw); rng = random.Random(11); ctrl = []
    while len(ctrl) < 3000:
        cx, cy = rng.uniform(120, 715), rng.uniform(120, 715)
        if math.hypot(cx - cx0, cy - cy0) < 150: continue
        ctrl.append(strip(cx, cy, rng.uniform(0, 180), hw))
    ctrl = np.array(ctrl)
    rot = {a: round(strip(cx0, cy0, pa + a, hw), 1) for a in (30, 60, 90, 120, 150)}
    print(f"hw={hw}px L={L*1.44:.0f}\" PA={pa:.0f}: strip mean {obs:.1f}; controls median {np.median(ctrl):.1f}, max {ctrl.max():.1f}; "
          f"fraction of controls >= observed: {np.mean(ctrl >= obs):.4f}; same centre, rotated: {rot}")
