"""Astrometry of the source at the predicted position (after the pre-registered decision; a measurement, no test).
Usage: astrometry.py PLATE [PLATE ...]  -> data/astrometry.json
Two centroid methods, each used for the reference stars and for the source in the same way:
  region (main): intensity-weighted centroid of the whole connected region above half of the local peak (trails and
          asymmetric images included); reference stars brighter than lim - 1 mag; star match tolerance 12 px.
  box: the method of commit 2201781: iterated 11 x 11 px box centroid; stars lim - 6 < m < lim + 0.3; tolerance 4 px.
Per plate: ATLAS stars (proper motion moved to the plate epoch, m > lim - 6) on the background-subtracted cutout;
affine fit pixel -> tangent-plane offsets about the prediction if >= 6 stars, otherwise a shift on the DASCH grid
(1.44"/px, no rotation); 3-sigma clipping; then the RA/Dec of the source and its O-C against JPL Horizons
(topocentric, MPC site of the plate) at the DASCH midpoint. The along-track residual divided by the rate gives the
time offset that would remove it."""
import gzip, io, json, math, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import measure as M
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import gaussian_filter, label

warnings.filterwarnings("ignore")
D = M.D


def centroid_region(img, x, y, search):
    """Intensity-weighted centroid of the connected region above half of the local peak. The peak is the maximum of
    the smoothed image within `search` px of (x, y). The region is the whole image or trail, not a box."""
    sm = gaussian_filter(img, 1.5); R = search + 40
    xi, yi = int(round(x)), int(round(y))
    if not (R <= xi < img.shape[1] - R and R <= yi < img.shape[0] - R):
        return None
    sub = sm[yi - R:yi + R + 1, xi - R:xi + R + 1]
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    near = np.hypot(xx, yy) <= search
    k = np.argmax(np.where(near, sub, -np.inf)); py, px = np.unravel_index(k, sub.shape)
    if sub[py, px] <= 0:
        return None
    lab, _ = label(sub > 0.5 * sub[py, px]); reg = lab == lab[py, px]
    if reg[0].any() or reg[-1].any() or reg[:, 0].any() or reg[:, -1].any():
        return None  # region runs out of the window: blended or not isolated
    wgt = np.clip(img[yi - R:yi + R + 1, xi - R:xi + R + 1], 0, None) * reg
    if wgt.sum() <= 0:
        return None
    return float(xi + (wgt * xx).sum() / wgt.sum()), float(yi + (wgt * yy).sum() / wgt.sum())


def centroid_box(img, x, y, search=None, h=5, it=3):
    for _ in range(it):
        xi, yi = int(round(x)), int(round(y))
        if not (h < xi < img.shape[1] - h - 1 and h < yi < img.shape[0] - h - 1):
            return None
        s = img[yi - h:yi + h + 1, xi - h:xi + h + 1]; s = np.clip(s - np.median(s), 0, None)
        if s.sum() <= 0:
            return None
        yy, xx = np.mgrid[yi - h:yi + h + 1, xi - h:xi + h + 1]
        x, y = float((s * xx).sum() / s.sum()), float((s * yy).sum() / s.sum())
    return x, y


# name: (centroid function, star magnitude window relative to lim, star match tolerance in px)
METHODS = {"region": (centroid_region, (-6, -1), 12), "box": (centroid_box, (-6, 0.3), 4)}


def tan(ra, dec, ra0, dec0):
    ra, dec, ra0, dec0 = map(np.radians, (ra, dec, ra0, dec0))
    c = np.sin(dec) * np.sin(dec0) + np.cos(dec) * np.cos(dec0) * np.cos(ra - ra0)
    xi = np.cos(dec) * np.sin(ra - ra0) / c
    eta = (np.sin(dec) * np.cos(dec0) - np.cos(dec) * np.sin(dec0) * np.cos(ra - ra0)) / c
    return np.degrees(xi) * 3600, np.degrees(eta) * 3600


def untan(xi, eta, ra0, dec0):
    xi, eta, ra0, dec0 = np.radians(xi / 3600), np.radians(eta / 3600), np.radians(ra0), np.radians(dec0)
    d = np.cos(dec0) - eta * np.sin(dec0)
    ra = ra0 + np.arctan2(xi, d)
    dec = np.arctan2(np.sin(dec0) + eta * np.cos(dec0), np.hypot(xi, d))
    return float(np.degrees(ra) % 360), float(np.degrees(dec))


def main(plates):
    out = {m: {} for m in METHODS}
    for name, (centroid, (mlo, mhi), tol) in METHODS.items():
        measure_all(plates, out[name], centroid, mlo, mhi, tol, name)
    (D / "astrometry.json").write_text(json.dumps(out, indent=1))
    # sensitivity of the region method to its two free choices (exploratory): O-C total per plate
    var = {}
    for tol in (4, 8, 12):
        for mhi in (0.3, -1):
            o = {}; measure_all(plates, o, centroid_region, -6, mhi, tol, f"t{tol}m{mhi:+}")
            var[f"tol{tol}px_mag<lim{mhi:+}"] = {pid: v["o_c_total_arcsec"] for pid, v in o.items()}
    (D / "astrometry_variants.json").write_text(json.dumps(var, indent=1))


def measure_all(plates, out, centroid, mlo, mhi, tol, name):
    preds = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
    cats = json.load(open(D / "refcat.json"))
    for pid in plates:
        p = preds[pid]
        h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / f"{pid}_s{p['solnum']}.fits.gz").read_bytes())))
        img = h[0].data.astype(float); w = WCS(h[0].header)
        img = img - gaussian_filter(img, 25)
        jd = Time(p["mid"] + ":00").jd
        assert abs(min(p["track"], key=lambda t: abs(t["jd"] - jd))["jd"] - jd) * 1440 < 0.01, pid
        stars = M.stars_at_epoch(cats[pid], jd)
        z = M.zimage(h[0].data.astype(float)); s2p, fit0 = M.refit(z, w, stars, p["lim"])
        ra0, dec0 = p["ra"], p["dec"]
        X, Y, XI, ETA, MAG = [], [], [], [], []
        for ra, de, m in stars:
            if not (p["lim"] + mlo < m < p["lim"] + mhi):
                continue
            x, y = s2p(np.array([ra]), np.array([de]))[0]
            c = centroid(img, x, y, 3)
            if c is None or math.hypot(c[0] - x, c[1] - y) > tol:
                continue
            xi, eta = tan(ra, de, ra0, dec0)
            X.append(c[0]); Y.append(c[1]); XI.append(xi); ETA.append(eta); MAG.append(m)
        X, Y, XI, ETA = map(np.array, (X, Y, XI, ETA))
        keep = np.ones(len(X), bool)
        model = "affine" if len(X) >= 6 else "shift"
        for _ in range(3):
            if model == "affine":
                A = np.column_stack([X[keep], Y[keep], np.ones(keep.sum())])
                cx, *_ = np.linalg.lstsq(A, XI[keep], rcond=None); cy, *_ = np.linalg.lstsq(A, ETA[keep], rcond=None)
            else:  # tangent plane: xi = -1.44 (x - 417) + a, eta = 1.44 (y - 417) + b (cutout grid is TAN, centre pixel 418 in FITS)
                a0 = np.mean(XI[keep] + 1.44 * (X[keep] - 417)); b0 = np.mean(ETA[keep] - 1.44 * (Y[keep] - 417))
                cx = np.array([-1.44, 0, a0 + 1.44 * 417]); cy = np.array([0, 1.44, b0 - 1.44 * 417])
            Af = np.column_stack([X, Y, np.ones(len(X))])
            res = np.hypot(Af @ cx - XI, Af @ cy - ETA)
            sig = np.sqrt(np.mean(res[keep] ** 2))
            keep = res < 3 * sig
        n = int(keep.sum()); rms = float(np.sqrt(np.mean(res[keep] ** 2)))
        # source: the image within 12 px (17") of the predicted pixel
        px, py = s2p(np.array([p["ra"]]), np.array([p["dec"]]))[0]
        c = centroid(img, px, py, 12)
        sxi, seta = np.array([c[0], c[1], 1.0]) @ cx, np.array([c[0], c[1], 1.0]) @ cy
        ra_m, dec_m = untan(sxi, seta, ra0, dec0)
        dra = (ra_m - p["ra"]) * math.cos(math.radians(p["dec"])) * 3600; ddec = (dec_m - p["dec"]) * 3600
        i = min(range(len(p["track"])), key=lambda k: abs(p["track"][k]["jd"] - jd))
        a, b = p["track"][max(i - 1, 0)], p["track"][min(i + 1, len(p["track"]) - 1)]
        vx = (b["ra"] - a["ra"]) * math.cos(math.radians(p["dec"])) * 3600; vy = (b["dec"] - a["dec"]) * 3600
        dt_h = (b["jd"] - a["jd"]) * 24; v = math.hypot(vx, vy)
        along = (dra * vx + ddec * vy) / v; cross = (-dra * vy + ddec * vx) / v
        out[pid] = {"mid_ut": p["mid"], "model": model, "n_ref": n, "fit_rms_arcsec": rms, "ra_deg": ra_m, "dec_deg": dec_m,
                    "o_c_ra_cosdec_arcsec": dra, "o_c_dec_arcsec": ddec, "o_c_total_arcsec": math.hypot(dra, ddec),
                    "along_track_arcsec": along, "cross_track_arcsec": cross, "rate_arcsec_per_h": v / dt_h,
                    "time_offset_min": along / (v / dt_h) * 60}
        o = out[pid]
        print(f"{name:6s} {pid} {p['mid']}  {model} n_ref={n} rms={rms:.2f}\"  RA={ra_m:.5f} Dec={dec_m:+.5f}  O-C=({dra:+.2f}, {ddec:+.2f})\" "
              f"|{o['o_c_total_arcsec']:.2f}\"|  along {along:+.2f}\" cross {cross:+.2f}\"  dt {o['time_offset_min']:+.1f} min")


if __name__ == "__main__":
    main(sys.argv[1:])
