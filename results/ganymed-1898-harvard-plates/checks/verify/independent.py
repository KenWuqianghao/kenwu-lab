"""Verifier's independent measurement (written without reuse of src/measure.py or src/astrometry.py).
Usage: independent.py DATA_DIR CTRL_DIR OUT.json [PNG]
For each Ganymed plate:
  1. Horizons position at the DASCH midpoint by a direct TLIST query (not from predictions.json), topocentric 802,
     plus positions at midpoint +- exposure/2 (the trail that the object makes during the exposure).
  2. Image: cutout minus a 31-px median background, divided by 1.4826*MAD -> z.
  3. Plate shift: catalogue stars (ATLAS via DASCH, proper motion applied, m < lim) vs. half-max blob centroids; coarse
     vote on a 1-px grid in +-30 px, then the median offset of the matched stars (shift only).
  4. Source: connected region above half of the local peak nearest the predicted pixel (within 12 px); its
     intensity-weighted centroid, major-axis position angle (image axes), full length and width at half maximum.
  5. O-C of the blob centroid against Horizons at the midpoint; trail PA and length predicted from the two end points.
Control plates (other dates, same sky position): the same shift fit; max z within 12 px of the same sky position.
ac00044: mean z in the predicted trail strip (track during the exposure, +-12 px) vs. 2000 strips with random
centre and random orientation on the same cutout.
Also: brute-force recomputation of the Poisson-binomial tail from data/results.json."""
import gzip, io, itertools, json, math, random, sys, time, warnings
from pathlib import Path
import numpy as np, requests
from astropy.io import fits
from astropy.wcs import WCS
from scipy import ndimage as ndi
warnings.filterwarnings("ignore")
DATA, CTRL, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
PX = 1.44
PL = {  # plate: (midpoint UT, exposure min, DASCH limMag)  -- from src/plates.py
    "i21050": ("1898-08-14 07:12", 14, 13.873), "ac00044": ("1898-09-21 05:31", 94, 12.360),
    "i21576": ("1898-11-01 05:01", 12, 13.630), "i21780": ("1898-11-26 02:12", 13, 13.410),
    "ac00115": ("1898-12-10 01:45", 63, 13.629), "i22152": ("1899-01-20 01:07", 10, 13.625)}

def jd_of(s):
    y, mo, d = map(int, s[:10].split("-")); h, mi = map(int, s[11:16].split(":"))
    a = (14 - mo) // 12; yy = y + 4800 - a; mm = mo + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045
    return jdn - 0.5 + (h + mi / 60) / 24

def horizons(jds):
    p = {"format": "json", "COMMAND": "'1036;'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER",
         "CENTER": "'802@399'", "TLIST": " ".join("'%.8f'" % j for j in jds), "QUANTITIES": "'1,9'", "CSV_FORMAT": "YES",
         "ANG_FORMAT": "DEG", "EXTRA_PREC": "YES"}
    for _ in range(3):
        try:
            t = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=p, timeout=120).json()["result"]; break
        except Exception:
            time.sleep(10)
    L = t.splitlines(); i, j = L.index("$$SOE"), L.index("$$EOE"); out = []
    for l in L[i + 1:j]:
        v = [x.strip() for x in l.split(",")]; out.append((float(v[3]), float(v[4]), float(v[5])))
    assert len(out) == len(jds), t[:800]
    return out

def load(f):
    h = fits.open(io.BytesIO(gzip.decompress(Path(f).read_bytes())))[0]
    img = h.data.astype(float); d = img - ndi.median_filter(img, size=31)
    c = d[60:-60, 60:-60]; return d / (1.4826 * np.median(np.abs(c - np.median(c)))), WCS(h.header)

def blob(z, x, y, search=12):
    """Half-max connected region around the brightest pixel within `search` px of (x, y)."""
    xi, yi = int(round(x)), int(round(y)); H = 60
    if not (H < xi < z.shape[1] - H and H < yi < z.shape[0] - H): return None
    sub = ndi.gaussian_filter(z, 1.0)[yi - H:yi + H + 1, xi - H:xi + H + 1]
    yy, xx = np.mgrid[-H:H + 1, -H:H + 1]
    near = np.hypot(xx - (x - xi), yy - (y - yi)) <= search
    k = np.argmax(np.where(near, sub, -np.inf)); py, px = np.unravel_index(k, sub.shape); peak = sub[py, px]
    lab, _ = ndi.label(sub > 0.5 * peak); m = lab == lab[py, px]
    w = np.where(m, sub, 0); s = w.sum(); cx, cy = (w * xx).sum() / s, (w * yy).sum() / s
    a, b, c = (w * (xx - cx) ** 2).sum() / s, (w * (yy - cy) ** 2).sum() / s, (w * (xx - cx) * (yy - cy)).sum() / s
    pa = math.degrees(0.5 * math.atan2(2 * c, a - b)) % 180
    u = (xx - cx) * math.cos(math.radians(pa)) + (yy - cy) * math.sin(math.radians(pa))
    v = -(xx - cx) * math.sin(math.radians(pa)) + (yy - cy) * math.cos(math.radians(pa))
    return {"x": xi + cx, "y": yi + cy, "peak_z": float(peak), "pa": pa, "len_px": float(u[m].max() - u[m].min() + 1),
            "wid_px": float(v[m].max() - v[m].min() + 1), "npix": int(m.sum())}

def stars(cat, year, lim):
    out = []
    for s in cat:
        try: ra, de, m = float(s["ra_deg"]), float(s["dec_deg"]), float(s["stdmag"])
        except ValueError: continue
        if m >= lim: continue
        dt = year - float(s.get("pos_epoch") or 2000)
        de2 = de + float(s.get("pm_dec_masyr") or 0) * dt / 3.6e6
        out.append((ra + float(s.get("pm_ra_masyr") or 0) * dt / 3.6e6 / math.cos(math.radians(de)), de2, m))
    return out

def shift(z, w, st):
    """Median pixel offset (plate - WCS) from catalogue stars; coarse vote first."""
    P = np.array([w.world_to_pixel_values(r, d) for r, d, _ in st], float)
    P = P[(P[:, 0] > 70) & (P[:, 0] < 765) & (P[:, 1] > 70) & (P[:, 1] < 765)]
    if len(P) == 0: return (0.0, 0.0), 0, None
    zs = ndi.gaussian_filter(z, 1.5); mx = ndi.maximum_filter(zs, 7); ys, xs = np.nonzero((zs == mx) & (zs > 5))
    best = (0, 0, 0)
    for dx in range(-30, 31):
        for dy in range(-30, 31):
            n = int(np.sum(np.min(np.hypot(xs[None] - P[:, :1] - dx, ys[None] - P[:, 1:] - dy), axis=1) < 3)) if len(xs) else 0
            if n > best[0]: best = (n, dx, dy)
    off = []
    for x, y in P:
        b = blob(z, x + best[1], y + best[2], search=5)
        if b and b["peak_z"] > 5: off.append((b["x"] - x, b["y"] - y))
    if len(off) < 2: return (float(best[1]), float(best[2])), len(off), None
    off = np.array(off); med = np.median(off, axis=0)
    return (float(med[0]), float(med[1])), len(off), float(np.sqrt(np.mean(np.sum((off - med) ** 2, axis=1))) * PX)

cats = json.load(open(DATA / "refcat.json")); res = {}; stamps = []
for pid, (mid, expm, lim) in PL.items():
    jd = jd_of(mid); (ra1, de1, _), (ra, de, V), (ra2, de2, _) = horizons([jd - expm / 2880, jd, jd + expm / 2880])  # Horizons sorts TLIST by time
    z, w = load(DATA / "cutouts" / f"{pid}_s0.fits.gz"); yr = 1900 + (jd - 2415020.5) / 365.25
    st = stars(cats[pid], yr, lim); (sx, sy), n, rms = shift(z, w, st)
    x, y = [float(v) for v in w.world_to_pixel_values(ra, de)]; x += sx; y += sy
    xa, ya = [float(v) for v in w.world_to_pixel_values(ra1, de1)]; xb, yb = [float(v) for v in w.world_to_pixel_values(ra2, de2)]
    tpa = math.degrees(math.atan2(yb - ya, xb - xa)) % 180; tlen = math.hypot(xb - xa, yb - ya)
    r = {"mid_ut": mid, "horizons_ra": ra, "horizons_dec": de, "V": V, "shift_px": [sx, sy], "n_stars": n, "shift_rms_arcsec": rms,
         "trail_pred_pa": tpa, "trail_pred_len_arcsec": tlen * PX}
    b = blob(z, x, y)
    if pid != "ac00044":
        ras, des = w.pixel_to_world_values(b["x"] - sx, b["y"] - sy)
        dra = (float(ras) - ra) * math.cos(math.radians(de)) * 3600; dde = (float(des) - de) * 3600
        ux, uy = (xb - xa) / tlen, (yb - ya) / tlen; ddx, ddy = b["x"] - x, b["y"] - y
        dpa = abs((b["pa"] - tpa + 90) % 180 - 90)
        r.update(blob_peak_z=b["peak_z"], blob_pa=b["pa"], blob_len_arcsec=b["len_px"] * PX, blob_wid_arcsec=b["wid_px"] * PX,
                 pa_diff_deg=dpa, ra_deg=float(ras), dec_deg=float(des), o_c_ra_cosdec=dra, o_c_dec=dde, o_c_total=math.hypot(dra, dde),
                 along_arcsec=(ddx * ux + ddy * uy) * PX, cross_arcsec=(-ddx * uy + ddy * ux) * PX)
        # shapes of catalogue stars on the same plate, for comparison
        sh = [blob(z, *(np.array(w.world_to_pixel_values(a, d_), float) + [sx, sy]), search=5) for a, d_, m in st]
        sh = [s for s in sh if s and s["peak_z"] > 8]
        if sh:
            r.update(star_n=len(sh), star_len_arcsec_median=float(np.median([s["len_px"] for s in sh]) * PX),
                     star_wid_arcsec_median=float(np.median([s["wid_px"] for s in sh]) * PX),
                     star_pa_list=[round(s["pa"]) for s in sh][:12])
    else:  # strip test for the 189" trail
        zs = z
        def strip(cx, cy, pa, L, hw=12):
            yy, xx = np.mgrid[0:z.shape[0], 0:z.shape[1]]; c, s_ = math.cos(math.radians(pa)), math.sin(math.radians(pa))
            u = (xx - cx) * c + (yy - cy) * s_; v = -(xx - cx) * s_ + (yy - cy) * c
            m = (np.abs(u) <= L / 2) & (np.abs(v) <= hw); return float(zs[m].mean())
        obs = strip((xa + xb) / 2 + sx, (ya + yb) / 2 + sy, tpa, tlen); rng = random.Random(7); ctrl = []
        while len(ctrl) < 2000:
            cx, cy = rng.uniform(110, 725), rng.uniform(110, 725)
            if math.hypot(cx - x, cy - y) < 140: continue
            ctrl.append(strip(cx, cy, rng.uniform(0, 180), tlen))
        ctrl = np.array(ctrl)
        r.update(strip_mean_z=obs, ctrl_max=float(ctrl.max()), ctrl_p99=float(np.percentile(ctrl, 99)), ctrl_sd=float(ctrl.std()),
                 frac_ctrl_ge=float(np.mean(ctrl >= obs)),
                 strip_other_pa={str(d): strip((xa + xb) / 2 + sx, (ya + yb) / 2 + sy, tpa + d, tlen) for d in (30, 60, 90, 120, 150)})
    res[pid] = r; stamps.append((pid, z, x, y, (xa + sx, ya + sy, xb + sx, yb + sy), f"{pid} {mid}"))
    for f in sorted(CTRL.glob(f"{pid}_ctrl_*.fits.gz")):
        zc, wc = load(f); cid = f.name.split("_ctrl_")[1][:6]; info = json.load(open(CTRL / "controls.json"))[f"{pid}_ctrl_{cid}"]
        yc = float(info["expdate"][:4]) + (float(info["expdate"][5:7]) - 0.5) / 12
        (cx_, cy_), nc, rc = shift(zc, wc, stars(cats[pid], yc, float(info["lim"])))
        xc, yc_ = [float(v) for v in wc.world_to_pixel_values(ra, de)]; xc += cx_; yc_ += cy_
        bc = blob(zc, xc, yc_)
        # brightest catalogue star (proper-motion ignored) within 12 px + 5 px of the position, for interpretation
        nearcat = sorted((float(s["stdmag"]), math.hypot(*(np.array(wc.world_to_pixel_values(float(s["ra_deg"]), float(s["dec_deg"])), float) + [cx_, cy_] - [xc, yc_])) * PX)
                         for s in cats[pid] if s["stdmag"] and math.hypot(*(np.array(wc.world_to_pixel_values(float(s["ra_deg"]), float(s["dec_deg"])), float) + [cx_, cy_] - [xc, yc_])) < 17)
        res[f"{pid}_ctrl_{cid}"] = {"expdate": info["expdate"], "lim": float(info["lim"]), "shift_px": [cx_, cy_], "n_stars": nc,
                                    "max_z_within_12px": bc["peak_z"], "brightest_cat_star_within_24arcsec": nearcat[:1]}
        stamps.append((f"{pid}_ctrl_{cid}", zc, xc, yc_, None, f"control {cid} {info['expdate'][:10]} lim {info['lim']}"))
# Poisson-binomial by brute force
r1 = json.load(open(DATA / "results.json")); g = [p for p in r1["plates"] if p["object"] == "Ganymed"]
ps = [p["p0"] for p in g]; k = sum(p["pass"] for p in g)
P = sum(np.prod([p if o else 1 - p for p, o in zip(ps, c)]) for c in itertools.product([0, 1], repeat=len(ps)) if sum(c) >= k)
ps2 = [max(p, 1 / 300) for p in ps]
P2 = sum(np.prod([p if o else 1 - p for p, o in zip(ps2, c)]) for c in itertools.product([0, 1], repeat=len(ps2)) if sum(c) >= k)
res["poisson_binomial"] = {"p0": ps, "k": k, "P": float(P), "P_with_p0_floor_1_in_300": float(P2)}
OUT.write_text(json.dumps(res, indent=1))
for k_, v in res.items(): print(k_, json.dumps({a: (float('%.6g' % b) if isinstance(b, float) else b) for a, b in v.items()}))
if len(sys.argv) > 4:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 5, figsize=(20, 8.4)); axs = axs.ravel()
    for ax, (name, z, x, y, tr, title) in zip(axs, stamps):
        H = 110 if name == "ac00044" else 45; xi, yi = int(x), int(y)
        ax.imshow(z[yi - H:yi + H + 1, xi - H:xi + H + 1], origin="lower", cmap="gray_r", vmin=-3, vmax=12 if "ac" not in name else 6,
                  extent=[xi - H - .5, xi + H + .5, yi - H - .5, yi + H + .5], interpolation="nearest")
        ax.plot([x], [y], "r+", ms=16)
        if tr: ax.plot([tr[0], tr[2]], [tr[1], tr[3]], "r-", lw=1.2, alpha=.6)
        ax.set_title(title, fontsize=10)
    fig.suptitle("Verifier stamps. Red cross: Horizons midpoint position after star shift. Red line: predicted motion during the exposure.")
    fig.tight_layout(); fig.savefig(sys.argv[4], dpi=70)
