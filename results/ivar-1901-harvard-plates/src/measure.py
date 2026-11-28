"""Pre-registered measurement (PROTOCOL.md). Usage: measure.py  -> data/results.json, prints a table.
For each plate:
 1. z image: (Gaussian(1.5 px) - Gaussian(15 px)) of the cutout, divided by 1.4826 * MAD.
 2. Astrometric refit: ATLAS stars (proper motion moved to the plate epoch) brighter than the plate limit are
    matched to z peaks; best integer shift on a +-25 px grid, then least-squares shift (< 6 matches) or affine.
 3. Search region: pixels within BUFFER of the predicted track from midpoint - W to midpoint + W.
    Masked: pixels within r(m) = 8" + 6" * max(0, lim - m) of an ATLAS star with m < lim + 1.
 4. Statistic S = max z over unmasked region pixels. Pass if S >= THRESH (Hektor 6, Ganymed 10).
 5. Null rate p0: the same region and mask rule, moved by 300 random offsets (90"-420", seed 1), inside the cutout.
Decision per object: detected if >= 2 plates pass and the Poisson-binomial P(N_pass >= k | p0 per plate) < 0.001."""
import gzip, io, json, math, os, random, sys, warnings
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import gaussian_filter, maximum_filter

warnings.filterwarnings("ignore")
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
W_H = 1.0
BUFFER = {"Ivar": 15.0}
THRESH = {"Ivar": 10.0}
NCTRL = 300


def zimage(img):
    z = gaussian_filter(img, 1.5) - gaussian_filter(img, 15)
    c = z[100:-100, 100:-100]
    return z / (1.4826 * np.median(np.abs(c - np.median(c))))


def stars_at_epoch(cat, jd):
    yr = Time(jd, format="jd").jyear
    out = []
    for s in cat:
        try:
            ra, dec, m = float(s["ra_deg"]), float(s["dec_deg"]), float(s["stdmag"])
        except ValueError:
            continue
        dt = yr - float(s.get("pos_epoch") or 2000)
        pmra = float(s.get("pm_ra_masyr") or 0); pmde = float(s.get("pm_dec_masyr") or 0)
        dec2 = dec + pmde * dt / 3.6e6
        ra2 = ra + pmra * dt / 3.6e6 / max(math.cos(math.radians(dec)), 1e-6)
        out.append((ra2, dec2, m))
    return out


def peaks(z, thr=6.0):
    mx = maximum_filter(z, size=5)
    ys, xs = np.nonzero((z == mx) & (z > thr))
    return np.column_stack([xs, ys]).astype(float)


def refit(z, w, stars, lim):
    """Return a function sky -> corrected pixel, plus fit info."""
    bright = [(ra, de) for ra, de, m in stars if m < lim]
    if not bright:
        return (lambda ra, de: np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T)), {"n": 0, "kind": "none"}
    sp = np.array([w.world_to_pixel_values(ra, de) for ra, de in bright], dtype=float)
    pk = peaks(z)
    if len(pk) == 0:
        return (lambda ra, de: np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T)), {"n": 0, "kind": "none"}
    best = (-1, 0, 0)
    for dx in range(-25, 26):
        for dy in range(-25, 26):
            q = sp + [dx, dy]
            d = np.min(np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]), axis=0)
            n = int(np.sum(d < 3))
            if n > best[0]:
                best = (n, dx, dy)
    q = sp + [best[1], best[2]]
    dd = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1])
    j = np.argmin(dd, axis=0); ok = dd[j, np.arange(len(q))] < 3
    src, dst = sp[ok], pk[j[ok]]
    if len(src) < 3:  # too few matches: keep the DASCH WCS
        return (lambda ra, de: np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T)), {"n": int(len(src)), "kind": "none"}
    if len(src) >= 6:
        A = np.column_stack([src, np.ones(len(src))])
        M, *_ = np.linalg.lstsq(A, dst, rcond=None)
        f = lambda P: np.column_stack([P, np.ones(len(P))]) @ M
        kind = "affine"
    else:
        sh = np.mean(dst - src, axis=0); f = lambda P: P + sh; kind = "shift"
    rms = float(np.sqrt(np.mean(np.sum((f(src) - dst) ** 2, axis=1)))) * 1.44

    def sky2pix(ra, de):
        P = np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T)
        return f(P)
    return sky2pix, {"n": int(len(src)), "kind": kind, "rms_arcsec": rms,
                     "shift_px": [float(x) for x in (f(np.array([[417.0, 417.0]])) - 417.0)[0]]}


def seg_dist(X, Y, pts):
    """Distance (px) of each pixel to the polyline pts."""
    d = np.full(X.shape, np.inf)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        vx, vy = x1 - x0, y1 - y0; L2 = vx * vx + vy * vy or 1e-9
        t = np.clip(((X - x0) * vx + (Y - y0) * vy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(X - (x0 + t * vx), Y - (y0 + t * vy)))
    return d


def stat(z, track_px, buf_px, star_px, star_r, off=(0.0, 0.0)):
    tp = track_px + off
    x0, y0 = np.floor(tp.min(axis=0) - buf_px - 1).astype(int); x1, y1 = np.ceil(tp.max(axis=0) + buf_px + 1).astype(int)
    if x0 < 20 or y0 < 20 or x1 > z.shape[1] - 20 or y1 > z.shape[0] - 20:
        return None
    Y, X = np.mgrid[y0:y1, x0:x1]
    reg = seg_dist(X, Y, tp) <= buf_px
    sp = star_px + off
    for (sx, sy), r in zip(sp, star_r):
        if x0 - r <= sx <= x1 + r and y0 - r <= sy <= y1 + r:
            reg &= np.hypot(X - sx, Y - sy) > r
    if not reg.any():
        return None
    sub = z[y0:y1, x0:x1]
    k = np.argmax(np.where(reg, sub, -np.inf))
    return float(sub.flat[k]), (float(X.flat[k]), float(Y.flat[k]))


def poisson_binomial_tail(ps, k):
    dist = np.zeros(len(ps) + 1); dist[0] = 1
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p; dist[0] *= (1 - p)
    return float(dist[k:].sum())


def main():
    preds = json.load(open(D / "predictions.json")); cats = json.load(open(D / "refcat.json"))
    rng = random.Random(1); res = []
    for p in preds:
        if not (D / "cutouts" / f"{p['plate']}_s{p['solnum']}.fits.gz").exists():
            print(p["plate"], "not covered (no cutout)"); continue
        h = fits.open(io.BytesIO(gzip.decompress((D / "cutouts" / f"{p['plate']}_s{p['solnum']}.fits.gz").read_bytes())))
        img = h[0].data.astype(float); w = WCS(h[0].header); z = zimage(img)
        jd_mid = min(p["track"], key=lambda t: abs(t["jd"] - Time(p["mid"] + ":00").jd))["jd"]
        stars = stars_at_epoch(cats[p["plate"]], jd_mid)
        sky2pix, fit = refit(z, w, stars, p["lim"])
        tr = [t for t in p["track"] if abs(t["jd"] - jd_mid) * 24 <= W_H + 1e-6]
        track_px = sky2pix(np.array([t["ra"] for t in tr]), np.array([t["dec"] for t in tr]))
        vis = [(ra, de, m) for ra, de, m in stars if m < p["lim"] + 1]
        star_px = sky2pix(np.array([s[0] for s in vis]), np.array([s[1] for s in vis])) if vis else np.zeros((0, 2))
        star_r = [(8 + 6 * max(0, p["lim"] - m)) / 1.44 for _, _, m in vis]
        buf = BUFFER[p["object"]] / 1.44
        S, (px, py) = stat(z, track_px, buf, star_px, star_r)
        ctrl = []
        while len(ctrl) < NCTRL:
            a = rng.uniform(0, 2 * math.pi); r = rng.uniform(90, 420) / 1.44
            v = stat(z, track_px, buf, star_px, star_r, (r * math.cos(a), r * math.sin(a)))
            if v is not None:
                ctrl.append(v[0])
        p0 = sum(c >= THRESH[p["object"]] for c in ctrl) / len(ctrl)
        # where along the track is the peak (hours from midpoint), and cross-track distance
        mid_px = sky2pix(np.array([p["ra"]]), np.array([p["dec"]]))[0]
        dists = np.hypot(track_px[:, 0] - px, track_px[:, 1] - py); i = int(np.argmin(dists))
        res.append({"object": p["object"], "plate": p["plate"], "mid": p["mid"], "V": p["V"], "lim": p["lim"],
                    "fit": fit, "S": S, "pass": S >= THRESH[p["object"]], "p0": p0, "ctrl_median": float(np.median(ctrl)),
                    "peak_px": [px, py], "peak_from_mid_arcsec": float(np.hypot(px - mid_px[0], py - mid_px[1]) * 1.44),
                    "peak_track_hours": (tr[i]["jd"] - jd_mid) * 24, "peak_cross_arcsec": float(dists[i] * 1.44)})
        r = res[-1]
        print(f"{r['object']:8s} {r['plate']:8s} {r['mid']} S={S:6.1f} pass={r['pass']!s:5s} p0={p0:.3f} "
              f"fit={fit.get('kind')} n={fit['n']} rms={fit.get('rms_arcsec')} peak: {r['peak_track_hours']:+.2f} h, "
              f"{r['peak_cross_arcsec']:.1f}\" cross, {r['peak_from_mid_arcsec']:.1f}\" from mid")
    out = {"plates": res, "objects": {}}
    for obj in sorted({r["object"] for r in res}):
        rs = [r for r in res if r["object"] == obj]; k = sum(r["pass"] for r in rs)
        P = poisson_binomial_tail([r["p0"] for r in rs], k)
        out["objects"][obj] = {"n": len(rs), "k_pass": k, "P_null": P, "detected": k >= 2 and P < 0.001,
                               "earliest_pass": min((r["mid"] for r in rs if r["pass"]), default=None)}
        print(obj, out["objects"][obj])
    (D / "results.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
