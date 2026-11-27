"""Post hoc motion check for 1901-08-23 (after the round-3 decision). Harvard b28276 (06:06 UT, Arequipa) and
Heidelberg G2281/G2282/G2283 (22:11-01:35 UT, Konigstuhl) are ~16 h apart; Hektor moves ~5' between them.
On each plate, z at Hektor's position for its own epoch ("own") and for the other observatory's epoch ("other"),
each compared with 2000 random points on the same plate (fraction of random points >= the value).
Writes data/hdap/motion_check.json.
For the Heidelberg plates the value is the trail-matched mean z (dt = 0); for b28276 the max z within 5"."""
import json, gzip, io, math, random, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import gaussian_filter, map_coordinates
warnings.filterwarnings("ignore")
D = M.D; rng = random.Random(5); out = {}
H = {p["plate"]: p for p in json.load(open(D / "hdap" / "predictions.json"))}
R1 = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
hcat = json.load(open(D / "hdap" / "refcat.json")); dcat = json.load(open(D / "refcat.json"))
def at(track, jd):
    tj = [t["jd"] for t in track]; return float(np.interp(jd, tj, [t["ra"] for t in track])), float(np.interp(jd, tj, [t["dec"] for t in track]))
# Harvard plate
p = R1["b28276"]; jdh = min(p["track"], key=lambda t: abs(t["jd"] - 2415619.754))["jd"]
h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / "b28276_s0.fits.gz").read_bytes())))
img = h[0].data.astype(float); w = WCS(h[0].header); z = M.zimage(img)
s2p, fit = M.refit(z, w, M.stars_at_epoch(dcat["b28276"], jdh), p["lim"])
G = H["G2281"]; jdg = (G["jd_start"] + G["jd_end"]) / 2
own = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
ora, ode = at(G["track"], jdg); other = s2p(np.array([ora]), np.array([ode]))[0]
def zmax(z, x, y, r=5 / 1.44):
    k = int(r) + 2; yy, xx = np.mgrid[int(y) - k:int(y) + k + 1, int(x) - k:int(x) + k + 1]
    return float(z[yy, xx][np.hypot(xx - x, yy - y) <= r].max())
ctrl = [zmax(z, rng.uniform(40, 795), rng.uniform(40, 795)) for _ in range(2000)]
for name, P in (("own (06:06 UT)", own), ("other (Heidelberg epoch)", other)):
    v = zmax(z, *P); fr = float(np.mean(np.array(ctrl) >= v)); out[f"b28276.{name.split()[0]}"] = {"z": v, "frac_random_ge": fr}
    print(f"b28276 {name}: pixel {P.round(1)} z={v:.1f} frac_random>= {fr:.4f}")
out["separation_arcsec"] = float(np.hypot(*(own - other)) * 1.44); print("separation own-other:", round(out["separation_arcsec"]), "arcsec")
# Heidelberg plates
for pid in ("G2281", "G2282", "G2283"):
    G = H[pid]; f = fits.open(D / "hdap" / "cutouts" / f"{pid}.fits")[0]; img = f.data.astype(float); w = WCS(f.header)
    sc = float(np.sqrt(abs(np.linalg.det(w.celestial.pixel_scale_matrix))) * 3600)
    zz = gaussian_filter(img, 3 / sc) - gaussian_filter(img, 30 / sc); c = zz[20:-20, 20:-20]; zz /= 1.4826 * np.median(np.abs(c - np.median(c)))
    res = json.load(open(D / "hdap" / "results.json")); sh = [r for r in res["plates"] if r["plate"] == pid][0]["fit"]["shift_px_at_centre"]
    def trailpix(jd0, jd1, dra=0.0, ddec=0.0):
        ts = np.linspace(jd0, jd1, 40); pts = [at(G["track"], t) for t in ts]
        P = np.array(w.world_to_pixel_values([q[0] + dra for q in pts], [q[1] + ddec for q in pts])).T + sh
        return P
    own = trailpix(G["jd_start"], G["jd_end"])
    # the same trail shape placed at Hektor's Harvard-epoch position
    hra, hde = R1["b28276"]["ra"], R1["b28276"]["dec"]; mra, mde = at(G["track"], (G["jd_start"] + G["jd_end"]) / 2)
    oth = trailpix(G["jd_start"], G["jd_end"], hra - mra, hde - mde)
    val = lambda P: float(map_coordinates(zz, [P[:, 1], P[:, 0]], order=1).mean())
    cs = []
    while len(cs) < 2000:
        o = np.array([rng.uniform(-250, 250), rng.uniform(-250, 250)])
        Q = own + o
        if Q.min() > 15 and Q[:, 0].max() < zz.shape[1] - 15 and Q[:, 1].max() < zz.shape[0] - 15: cs.append(val(Q))
    cs = np.array(cs)
    for name, P in (("own", own), ("other (Harvard epoch)", oth)):
        if P.min() < 5 or P[:, 0].max() > zz.shape[1] - 5 or P[:, 1].max() > zz.shape[0] - 5:
            out[f"{pid}.{name.split()[0]}"] = None; print(pid, name, "outside cutout"); continue
        v = val(P); fr = float(np.mean(cs >= v)); out[f"{pid}.{name.split()[0]}"] = {"z": v, "frac_random_ge": fr}
        print(f"{pid} {name}: mean z={v:.2f} frac_random>= {fr:.4f}")
(D / "hdap" / "motion_check.json").write_text(json.dumps(out, indent=1))
