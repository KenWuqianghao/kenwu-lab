# Independent measurement: DASCH WCS only (no refit by the author's code), my own background and centroid.
import gzip, io, json, sys, math
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import median_filter, gaussian_filter, label
R = sys.argv[1]
preds = {p["plate"]: p for p in json.load(open(R + "/data/predictions.json"))}
cats = json.load(open(R + "/data/refcat.json"))
def sep(ra1, d1, ra2, d2):
    return math.hypot((ra1 - ra2) * math.cos(math.radians(d1)), d1 - d2) * 3600
for pl in sys.argv[2:]:
    p = preds[pl]
    h = fits.open(io.BytesIO(gzip.decompress(open(f"{R}/data/cutouts/{pl}_s0.fits.gz", "rb").read())))
    img = h[0].data.astype(float); w = WCS(h[0].header)
    scale = np.sqrt(abs(np.linalg.det(w.pixel_scale_matrix))) * 3600
    bg = median_filter(img, 41); d = gaussian_filter(img - bg, 1.0)
    sig = 1.4826 * np.median(np.abs(d - np.median(d))); z = d / sig
    print(f"\n== {pl} shape {img.shape} scale {scale:.2f}\"/px  mid {p['mid']} exp {p['exptime_min']} min; raw median {np.median(img):.0f}")
    # star offsets of DASCH WCS: bright ATLAS stars -> nearest peak centroid
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
        yy, xx = np.mgrid[-10:11, -10:11]; sub = z[int(y) - 10:int(y) + 11, int(x) - 10:int(x) + 11]
        k = np.argmax(sub); py, px = int(y) - 10 + k // 21, int(x) - 10 + k % 21
        if sub.flat[k] < 8: continue
        c = centroid(px, py)
        if c: offs.append((c[0] - x, c[1] - y)); phot.append((m, c[2], sub.flat[k]))
    offs = np.array(offs)
    med = np.median(offs, axis=0) if len(offs) else np.zeros(2)
    print(f" stars matched {len(offs)}; median WCS offset px {med.round(2)}; scatter px {offs.std(axis=0).round(2) if len(offs) else None}")
    # brightest source within 40" of predicted midpoint (WCS corrected by the median star offset)
    x, y = w.world_to_pixel_values(p["ra"], p["dec"]); x += med[0]; y += med[1]
    Y, X = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    for rad in (10, 40):
        m_ = np.hypot(X - x, Y - y) <= rad / scale
        k = np.argmax(np.where(m_, z, -np.inf)); py, px = np.unravel_index(k, z.shape)
        c = centroid(px, py)
        ra_s, de_s = w.pixel_to_world_values(c[0] - med[0], c[1] - med[1])
        print(f" within {rad}\": peak z {z[py, px]:.1f} at px ({px},{py}); centroid offset from prediction {math.hypot(c[0]-x, c[1]-y)*scale:.1f}\" ; sky {float(ra_s):.5f} {float(de_s):.5f}; flux {c[2]:.0f}")
    near = sorted((sep(float(s["ra_deg"]), float(s["dec_deg"]), p["ra"], p["dec"]), s["stdmag"]) for s in cats[pl])[:4]
    print(" nearest ATLAS stars (arcsec, mag):", [(round(a, 1), b) for a, b in near])
    # magnitude estimate from flux-mag relation of matched stars
    if len(phot) >= 4:
        ph = np.array(phot); A = np.polyfit(np.log10(ph[:, 1]), ph[:, 0], 1)
        est = np.polyval(A, math.log10(c[2])); res = ph[:, 0] - np.polyval(A, np.log10(ph[:, 1]))
        print(f" magnitude estimate of the source from {len(ph)} stars: {est:.2f} (rms {res.std():.2f}); Horizons V {p['V']}")
    # z along the predicted track
    tr = p["track"]; jm = min(tr, key=lambda t: abs(t["ra"] - p["ra"]) + abs(t["dec"] - p["dec"]))["jd"]
    row = []
    for t in tr:
        dt = (t["jd"] - jm) * 24
        if abs(dt) > 1.01: continue
        tx, ty = w.world_to_pixel_values(t["ra"], t["dec"]); tx += med[0]; ty += med[1]
        m_ = np.hypot(X - tx, Y - ty) <= 6 / scale
        row.append(f"{dt:+.2f}h:{z[m_].max():.0f}")
    print(" max z within 6\" of track points:", " ".join(row))
    # shape of the source: second moments of connected region above 30% of peak
    lab, n = label(z > max(5, 0.3 * z[py, px])); reg = lab == lab[py, px]
    ys, xs = np.nonzero(reg); wt = z[reg]
    cx, cy = np.average(xs, weights=wt), np.average(ys, weights=wt)
    cov = np.cov(np.vstack([xs - cx, ys - cy]), aweights=wt); ev, evec = np.linalg.eigh(cov)
    t0, t1 = tr[0], tr[-1]; a0 = np.array(w.world_to_pixel_values(t0["ra"], t0["dec"])); a1 = np.array(w.world_to_pixel_values(t1["ra"], t1["dec"]))
    mv = (a1 - a0) / np.linalg.norm(a1 - a0); ang = math.degrees(math.acos(min(1, abs(float(evec[:, 1] @ mv)))))
    ext = (xs - cx) * evec[0, 1] + (ys - cy) * evec[1, 1]
    print(f" source region: {reg.sum()} px, full extent on major axis {(ext.max()-ext.min())*scale:.0f}\", axis ratio {math.sqrt(ev[1]/max(ev[0],1e-9)):.1f}, angle between major axis and predicted motion {ang:.0f} deg; predicted trail {p['trail_arcsec']:.0f}\"")
