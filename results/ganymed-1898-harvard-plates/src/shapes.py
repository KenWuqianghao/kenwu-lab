"""Post hoc: shape of the source at the prediction against the predicted trail and against stars on the same plate.
Usage: shapes.py PLATE [PLATE ...]  -> data/shapes.json
Region: the connected region above half of the local peak of the smoothed (1.5 px), background-subtracted cutout,
as in src/astrometry.py (method "region"). Per region: position angle of the major axis from the second moments
(degrees, image x/y axes, x = -RA, y = +Dec on the cutout TAN grid, folded to 0-180) and the full length and width
(extent of the region pixels along the major and minor axes, arcsec). Predicted trail: the track over the exposure,
PA on the same axes and length = rate x exposure. Stars: isolated catalogued stars lim-3 < m < lim-0.5 (no other
catalogued star with m < lim+1 within 30"), at most 40, regions that do not reach the 85 px window edge."""
import json, gzip, io, math, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import gaussian_filter, label
warnings.filterwarnings("ignore")
D = M.D; PX = 1.44


def region_shape(sm, x, y, search, R=42):
    xi, yi = int(round(x)), int(round(y))
    if not (R <= xi < sm.shape[1] - R and R <= yi < sm.shape[0] - R):
        return None
    sub = sm[yi - R:yi + R + 1, xi - R:xi + R + 1]; yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    k = np.argmax(np.where(np.hypot(xx, yy) <= search, sub, -np.inf)); py, px = np.unravel_index(k, sub.shape)
    if sub[py, px] <= 0:
        return None
    lab, _ = label(sub > 0.5 * sub[py, px]); reg = lab == lab[py, px]
    if reg[0].any() or reg[-1].any() or reg[:, 0].any() or reg[:, -1].any():
        return None
    wt = sub * reg; m = wt.sum(); cx, cy = (wt * xx).sum() / m, (wt * yy).sum() / m
    a, b, c = (wt * (xx - cx) ** 2).sum() / m, (wt * (yy - cy) ** 2).sum() / m, (wt * (xx - cx) * (yy - cy)).sum() / m
    pa = math.degrees(0.5 * math.atan2(2 * c, a - b)) % 180
    u = np.array([math.cos(math.radians(pa)), math.sin(math.radians(pa))])
    ys, xs = np.nonzero(reg); along = (xs - R) * u[0] + (ys - R) * u[1]; cross = -(xs - R) * u[1] + (ys - R) * u[0]
    return {"pa_deg": pa, "length_arcsec": float(np.ptp(along) + 1) * PX, "width_arcsec": float(np.ptp(cross) + 1) * PX}


def main(plates):
    preds = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}; cats = json.load(open(D / "refcat.json"))
    out = {}
    for pid in plates:
        p = preds[pid]
        h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / f"{pid}_s{p['solnum']}.fits.gz").read_bytes())))
        img = h[0].data.astype(float); w = WCS(h[0].header)
        sm = gaussian_filter(img - gaussian_filter(img, 25), 1.5)
        jd = Time(p["mid"] + ":00").jd
        stars = M.stars_at_epoch(cats[pid], jd); s2p, fit = M.refit(M.zimage(img), w, stars, p["lim"])
        half = p["exptime_min"] / 120
        tr = [t for t in p["track"] if abs(t["jd"] - jd) * 24 <= half + 1e-4] or [min(p["track"], key=lambda t: abs(t["jd"] - jd))]
        tp = s2p(np.array([t["ra"] for t in tr]), np.array([t["dec"] for t in tr]))
        tpa = math.degrees(math.atan2(tp[-1][1] - tp[0][1], tp[-1][0] - tp[0][0])) % 180 if len(tp) > 1 else None
        mid = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
        src = region_shape(sm, *mid, 12)
        bright = [s for s in stars if s[2] < p["lim"] + 1]
        bp = s2p(np.array([s[0] for s in bright]), np.array([s[1] for s in bright]))
        st = []
        for (ra, de, m), q in zip(bright, bp):
            if not (p["lim"] - 3 < m < p["lim"] - 0.5):
                continue
            if np.sum(np.hypot(bp[:, 0] - q[0], bp[:, 1] - q[1]) < 30 / PX) > 1:
                continue
            r = region_shape(sm, *q, 3)
            if r:
                st.append(r)
            if len(st) == 40:
                break
        pas = np.array([r["pa_deg"] for r in st])
        cm = math.degrees(0.5 * math.atan2(np.mean(np.sin(np.radians(2 * pas))), np.mean(np.cos(np.radians(2 * pas))))) % 180 if len(st) else None
        out[pid] = {"exptime_min": p["exptime_min"], "trail_pred_pa_deg": tpa, "trail_pred_length_arcsec": p["trail_arcsec"],
                    "source": src,
                    "stars_n": len(st), "stars_pa_mean_deg": cm,
                    "stars_length_median_arcsec": float(np.median([r["length_arcsec"] for r in st])) if st else None,
                    "stars_width_median_arcsec": float(np.median([r["width_arcsec"] for r in st])) if st else None}
        o = out[pid]; f = lambda v: "-" if v is None else f"{v:.0f}"
        print(f"{pid}: trail PA {f(tpa)} len {o['trail_pred_length_arcsec']:.0f}\"; source PA {src['pa_deg']:.0f} "
              f"len {src['length_arcsec']:.0f}\" wid {src['width_arcsec']:.0f}\"; stars n={len(st)} PA {f(cm)} "
              f"len {f(o['stars_length_median_arcsec'])}\" wid {f(o['stars_width_median_arcsec'])}\"")
    (D / "shapes.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
