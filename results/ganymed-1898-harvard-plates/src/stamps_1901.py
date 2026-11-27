"""Post hoc figure: Hektor on 1901-08-23, Harvard b28276 and Heidelberg G2281-G2283. Each panel 4' x 4', centred on
Hektor's own-epoch position; red: predicted trail (exposure start..end); cyan circle: Hektor's position at the other
observatory's epoch (no source expected there)."""
import json, gzip, io, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import gaussian_filter
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
D = M.D
H = {p["plate"]: p for p in json.load(open(D / "hdap" / "predictions.json"))}; R1 = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
res = {r["plate"]: r for r in json.load(open(D / "hdap" / "results.json"))["plates"]}
def at(track, jd):
    tj = [t["jd"] for t in track]; return float(np.interp(jd, tj, [t["ra"] for t in track])), float(np.interp(jd, tj, [t["dec"] for t in track]))
fig, axs = plt.subplots(1, 4, figsize=(16, 4.6))
# Harvard
p = R1["b28276"]; h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / "b28276_s0.fits.gz").read_bytes())))[0]
img = h.data.astype(float); w = WCS(h.header); z = M.zimage(img)
jdh = min(p["track"], key=lambda t: abs(t["jd"] - 2415619.754))["jd"]
s2p, _ = M.refit(z, w, M.stars_at_epoch(json.load(open(D / "refcat.json"))["b28276"], jdh), p["lim"])
G = H["G2281"]; oth = s2p(*[np.array([v]) for v in at(G["track"], (G["jd_start"] + G["jd_end"]) / 2)])[0]
c = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]; half = int(120 / 1.44)
tr = [t for t in p["track"] if abs(t["jd"] - jdh) * 24 <= 0.5]; T = s2p(np.array([t["ra"] for t in tr]), np.array([t["dec"] for t in tr]))
st = gaussian_filter(img, 1)[int(c[1]) - half:int(c[1]) + half, int(c[0]) - half:int(c[0]) + half]; lo, hi = np.percentile(st, [2, 99.7])
ax = axs[0]; ax.imshow(st, origin="lower", cmap="gray_r", vmin=lo, vmax=hi, extent=[-half * 1.44, half * 1.44, -half * 1.44, half * 1.44])
ax.plot((T[:, 0] - c[0]) * 1.44, (T[:, 1] - c[1]) * 1.44, "r-", lw=0.8); ax.add_patch(plt.Circle(((oth[0] - c[0]) * 1.44, (oth[1] - c[1]) * 1.44), 10, fill=False, color="c"))
ax.set_title("Harvard b28276, Arequipa\n1901-08-23 06:06 UT, 60 min", fontsize=9)
for ax, pid in zip(axs[1:], ("G2281", "G2282", "G2283")):
    G = H[pid]; f = fits.open(D / "hdap" / "cutouts" / f"{pid}.fits")[0]; img = f.data.astype(float); w = WCS(f.header)
    sc = float(np.sqrt(abs(np.linalg.det(w.celestial.pixel_scale_matrix))) * 3600); sh = np.array(res[pid]["fit"]["shift_px_at_centre"])
    ts = np.linspace(G["jd_start"], G["jd_end"], 30); pts = [at(G["track"], t) for t in ts]
    T = np.array(w.world_to_pixel_values([q[0] for q in pts], [q[1] for q in pts])).T + sh; c = T[len(T) // 2]
    o = np.array(w.world_to_pixel_values(R1["b28276"]["ra"], R1["b28276"]["dec"])) + sh
    half = int(120 / sc); st = gaussian_filter(img, 0.7)[int(c[1]) - half:int(c[1]) + half, int(c[0]) - half:int(c[0]) + half]
    lo, hi = np.percentile(st, [2, 99.7])
    ax.imshow(st, origin="lower", cmap="gray_r", vmin=lo, vmax=hi, extent=[-half * sc, half * sc, -half * sc, half * sc])
    ax.plot((T[:, 0] - c[0]) * sc, (T[:, 1] - c[1]) * sc, "r-", lw=0.8)
    if abs(o[0] - c[0]) < half and abs(o[1] - c[1]) < half: ax.add_patch(plt.Circle(((o[0] - c[0]) * sc, (o[1] - c[1]) * sc), 10, fill=False, color="c"))
    ax.set_title(f"Heidelberg {pid}, Konigstuhl\n{G['start'][:16].replace('T', ' ')} UT, {(G['jd_end'] - G['jd_start']) * 1440:.0f} min, p={res[pid]['p']:.4f}", fontsize=9)
for ax in axs: ax.tick_params(labelsize=7)
fig.suptitle("(624) Hektor on 1901 Aug 23: red = predicted trail at each plate's epoch; cyan = Hektor's position at the other observatory's epoch (outside the panel when not drawn)", fontsize=9)
fig.tight_layout(); fig.savefig(D / "hektor_1901-08-23.png", dpi=110)
