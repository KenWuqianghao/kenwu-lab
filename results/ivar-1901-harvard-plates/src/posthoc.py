"""Shape, position and brightness of the source on the four 1901 plates. A measurement made after the registered
decision, not a test. The method is the verification stage's independent code (checks/verify/indep.py), unchanged
in its numbers: median-filter background (41 px), Gaussian smoothing (1 px), DASCH WCS plus the median offset of
matched ATLAS stars, flux-weighted centroid in a 13 x 13 px box, magnitude from a linear fit of ATLAS magnitude on
log flux, and the second moments of the connected region above max(5, 0.3 peak).
Reads predictions.json, refcat.json and cutouts/ from the data directory (PRECOVERY_DATA, default data/).
Writes posthoc.json there. Usage: posthoc.py PLATE..."""
import gzip, io, json, math, os, sys, warnings
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import median_filter, gaussian_filter, label
warnings.filterwarnings("ignore")
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
preds = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
cats = json.load(open(D / "refcat.json"))
def sep(ra1, d1, ra2, d2):
    return math.hypot((ra1 - ra2) * math.cos(math.radians(d1)), d1 - d2) * 3600
out = {}
for pl in sys.argv[1:]:
    p = preds[pl]
    h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / f"{pl}_s0.fits.gz").read_bytes())))
    img = h[0].data.astype(float); w = WCS(h[0].header)
    scale = np.sqrt(abs(np.linalg.det(w.pixel_scale_matrix))) * 3600
    bg = median_filter(img, 41); d = gaussian_filter(img - bg, 1.0)
    sig = 1.4826 * np.median(np.abs(d - np.median(d))); z = d / sig
    def centroid(x0, y0, r=6):
        x0, y0 = int(round(x0)), int(round(y0))
        if not (r < x0 < img.shape[1] - r and r < y0 < img.shape[0] - r): return None
        sub = np.clip(d[y0 - r:y0 + r + 1, x0 - r:x0 + r + 1], 0, None)
        if sub.sum() <= 0: return None
        Y, X = np.mgrid[-r:r + 1, -r:r + 1]
        return x0 + (X * sub).sum() / sub.sum(), y0 + (Y * sub).sum() / sub.sum(), sub.sum()
    offs = []; phot = []
    for s in cats[pl]:
        try: ra, de, m = float(s["ra_deg"]), float(s["dec_deg"]), float(s["stdmag"])
        except ValueError: continue
        if m > p["lim"] - 0.5: continue
        x, y = w.world_to_pixel_values(ra, de)
        if not (30 < x < img.shape[1] - 30 and 30 < y < img.shape[0] - 30): continue
        sub = z[int(y) - 10:int(y) + 11, int(x) - 10:int(x) + 11]
        k = np.argmax(sub); py, px = int(y) - 10 + k // 21, int(x) - 10 + k % 21
        if sub.flat[k] < 8: continue
        c = centroid(px, py)
        if c: offs.append((c[0] - x, c[1] - y)); phot.append((m, c[2], sub.flat[k]))
    offs = np.array(offs)
    med = np.median(offs, axis=0) if len(offs) else np.zeros(2)
    x, y = w.world_to_pixel_values(p["ra"], p["dec"]); x += med[0]; y += med[1]
    Y, X = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    ent = {"n_stars_matched": len(offs)}
    for rad in (10, 40):
        m_ = np.hypot(X - x, Y - y) <= rad / scale
        k = np.argmax(np.where(m_, z, -np.inf)); py, px = np.unravel_index(k, z.shape)
        c = centroid(px, py)
        ent[f"r{rad}"] = {"peak_z": round(float(z[py, px]), 1), "centroid_offset_arcsec": round(math.hypot(c[0] - x, c[1] - y) * scale, 1)}
    bright = [sep(float(s["ra_deg"]), float(s["dec_deg"]), p["ra"], p["dec"]) for s in cats[pl]
              if s["stdmag"] not in ("", None) and float(s["stdmag"]) < 16]
    ent["nearest_star_brighter_16_arcsec"] = round(min(bright), 1) if bright else None
    if len(phot) >= 4:
        ph = np.array(phot); A = np.polyfit(np.log10(ph[:, 1]), ph[:, 0], 1)
        res = ph[:, 0] - np.polyval(A, np.log10(ph[:, 1]))
        ent["mag_estimate"] = round(float(np.polyval(A, math.log10(c[2]))), 2); ent["mag_rms"] = round(float(res.std()), 2); ent["mag_n"] = len(ph)
    tr = p["track"]; jm = min(tr, key=lambda t: abs(t["ra"] - p["ra"]) + abs(t["dec"] - p["dec"]))["jd"]
    prof = []
    for t in tr:
        dt = (t["jd"] - jm) * 24
        if abs(dt) > 1.01: continue
        tx, ty = w.world_to_pixel_values(t["ra"], t["dec"]); tx += med[0]; ty += med[1]
        prof.append((round(dt, 2), round(float(z[np.hypot(X - tx, Y - ty) <= 6 / scale].max()), 1)))
    ent["track_z_6arcsec"] = prof
    hi = [dt for dt, v in prof if v >= 10]
    ent["track_hours_z_ge_10"] = [min(hi), max(hi)] if hi else None
    lab, n = label(z > max(5, 0.3 * z[py, px])); reg = lab == lab[py, px]
    ys, xs = np.nonzero(reg); wt = z[reg]
    cx, cy = np.average(xs, weights=wt), np.average(ys, weights=wt)
    cov = np.cov(np.vstack([xs - cx, ys - cy]), aweights=wt); ev, evec = np.linalg.eigh(cov)
    t0, t1 = tr[0], tr[-1]; a0 = np.array(w.world_to_pixel_values(t0["ra"], t0["dec"])); a1 = np.array(w.world_to_pixel_values(t1["ra"], t1["dec"]))
    mv = (a1 - a0) / np.linalg.norm(a1 - a0); ang = math.degrees(math.acos(min(1, abs(float(evec[:, 1] @ mv)))))
    ext = (xs - cx) * evec[0, 1] + (ys - cy) * evec[1, 1]
    ent["shape"] = {"n_px": int(reg.sum()), "major_extent_arcsec": round(float((ext.max() - ext.min()) * scale)),
                    "axis_ratio": round(math.sqrt(ev[1] / max(ev[0], 1e-9)), 1), "angle_to_motion_deg": round(ang),
                    "predicted_trail_arcsec": round(p["trail_arcsec"])}
    out[pl] = ent; print(pl, json.dumps({k: v for k, v in ent.items() if k != "track_z_6arcsec"}), flush=True)
(D / "posthoc.json").write_text(json.dumps(out, indent=1))
