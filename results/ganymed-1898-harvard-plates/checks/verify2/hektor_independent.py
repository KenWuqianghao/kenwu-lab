"""Verifier round 2: independent look at (624) Hektor on HDAP plates G2281, G2282, G2283 (1901-08-23).
Own code: direct Horizons query (site 024, 1-min steps), own z image, own star fit.
A. Trail-mean z as a function of time shift (along track) and cross-track offset: where is the peak?
B. Catalogue stars (any magnitude) near the track.
C. Expected trail-mean z of a trailed object, from stacked star images in magnitude bins.
Usage: python checks/verify2/hektor_independent.py <repo-data-dir> <out.json>"""
import json, sys, re, math
from pathlib import Path
import numpy as np, requests
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import gaussian_filter, map_coordinates, maximum_filter
D = Path(sys.argv[1]); OUT = Path(sys.argv[2]); cache = OUT.parent / "horizons_624_19010823.txt"
if cache.exists():
    txt = cache.read_text()
else:
    r = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params={"format": "text", "COMMAND": "'624;'", "OBJ_DATA": "NO",
        "EPHEM_TYPE": "OBSERVER", "CENTER": "'024@399'", "START_TIME": "'1901-08-23 03:00'", "STOP_TIME": "'1901-08-24 04:00'",
        "STEP_SIZE": "'1m'", "QUANTITIES": "'1'", "ANG_FORMAT": "DEG", "CAL_FORMAT": "JD", "CSV_FORMAT": "NO"}, timeout=180)
    txt = r.text; cache.write_text(txt)
body = txt.split("$$SOE")[1].split("$$EOE")[0]
eph = []
for l in body.strip().splitlines():
    nums = re.findall(r"-?\d+\.\d+", l); eph.append((float(nums[0]), float(nums[-2]), float(nums[-1])))
eph = np.array(eph); assert np.allclose(np.diff(eph[:, 0]) * 1440, 1, atol=1e-3), "missing rows"
pos = lambda jd: (np.interp(jd, eph[:, 0], eph[:, 1]), np.interp(jd, eph[:, 0], eph[:, 2]))
cats = json.load(open(D / "hdap" / "refcat.json")); preds = {p["plate"]: p for p in json.load(open(D / "hdap" / "predictions.json"))}
res = {}
for pid in ("G2281", "G2282", "G2283"):
    p = preds[pid]; h = fits.open(D / "hdap" / "cutouts" / f"{pid}.fits")[0]; img = h.data.astype(float); w = WCS(h.header)
    sc = float(np.sqrt(abs(np.linalg.det(w.celestial.pixel_scale_matrix))) * 3600)
    jd0, jd1 = Time(p["start"], scale="utc").jd, Time(p["end"], scale="utc").jd; mid = (jd0 + jd1) / 2
    # compare my ephemeris with the solver's midpoint
    mra, mde = pos(mid); dpred = math.hypot((mra - p["ra"]) * math.cos(math.radians(mde)), mde - p["dec"]) * 3600
    yr = Time(mid, format="jd").jyear; S = []
    for s in cats[pid]:
        try: ra, de, m = float(s["ra_deg"]), float(s["dec_deg"]), float(s["stdmag"])
        except ValueError: continue
        dt = yr - float(s.get("pos_epoch") or 2000)
        S.append((ra + float(s.get("pm_ra_masyr") or 0) * dt / 3.6e6 / math.cos(math.radians(de)), de + float(s.get("pm_dec_masyr") or 0) * dt / 3.6e6, m))
    S = np.array(S); sxy = np.array(w.world_to_pixel_values(S[:, 0], S[:, 1])).T
    def zim(sig):
        z = gaussian_filter(sig, 2.5 / sc) - gaussian_filter(sig, 40 / sc); c = z[30:-30, 30:-30]
        return z / (1.4826 * np.median(np.abs(c - np.median(c))))
    # polarity: stars m < 14 must be positive
    inb = lambda P, b=25: (P[:, 0] > b) & (P[:, 0] < img.shape[1] - b) & (P[:, 1] > b) & (P[:, 1] < img.shape[0] - b)
    br = sxy[(S[:, 2] < 14) & inb(sxy)]
    zz = zim(img); k = int(8 / sc)
    def near_max(z, P, k=k):
        return np.array([z[int(round(y)) - k:int(round(y)) + k + 1, int(round(x)) - k:int(round(x)) + k + 1].max() for x, y in P])
    pol = 1 if np.median(near_max(zz, br)) > np.median(near_max(-zz, br)) else -1
    z = zim(pol * img)
    # star fit: peaks near stars m < 15.5, iterative affine
    mx = maximum_filter(z, size=7); ys, xs = np.nonzero((z == mx) & (z > 5)); pk = np.column_stack([xs, ys]).astype(float)
    ref = sxy[(S[:, 2] < 15.5) & inb(sxy)]
    A = np.array([[1, 0], [0, 1], [0, 0]], float)
    T = lambda P: np.column_stack([P, np.ones(len(P))]) @ A
    for tol in (40 / sc, 15 / sc, 8 / sc, 5 / sc, 5 / sc):
        q = T(ref); dd = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]); j = dd.argmin(0); ok = dd[j, np.arange(len(q))] < tol
        if tol > 10 / sc:
            sh = np.median(pk[j[ok]] - q[ok], axis=0); A[2] += sh
        else:
            A, *_ = np.linalg.lstsq(np.column_stack([ref[ok], np.ones(ok.sum())]), pk[j[ok]], rcond=None)
    q = T(ref); dd = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]); j = dd.argmin(0); ok = dd[j, np.arange(len(q))] < 5 / sc
    rms = float(np.sqrt(np.mean(np.sum((q[ok] - pk[j[ok]]) ** 2, axis=1))) * sc)
    s2p = lambda ra, de: T(np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T))
    def trail(dt_min, cross_as=0.0):
        ts = np.linspace(jd0, jd1, 60) + dt_min / 1440; ra, de = pos(ts); P = s2p(ra, de)
        v = P[-1] - P[0]; n = np.array([-v[1], v[0]]) / np.hypot(*v)
        return P + n * cross_as / sc
    val = lambda P: float(map_coordinates(z, [P[:, 1], P[:, 0]], order=1).mean())
    # A. map
    dts = np.arange(-180, 181, 5); crs = np.arange(-40, 41, 4)
    Mp = np.array([[val(trail(d, c)) for d in dts] for c in crs])
    i, jx = np.unravel_index(Mp.argmax(), Mp.shape)
    on = [val(trail(d)) for d in dts]
    # null for the nominal trail: random translations
    rng = np.random.default_rng(11); nom = trail(0); ctrl = []
    while len(ctrl) < 4000:
        o = rng.uniform(-220, 220, 2); Q = nom + o
        if np.hypot(*o) * sc < 80 or Q.min() < 15 or Q[:, 0].max() > z.shape[1] - 15 or Q[:, 1].max() > z.shape[0] - 15: continue
        ctrl.append(val(Q))
    ctrl = np.array(ctrl)
    # B. catalogue stars near the track family (-60..+60 min)
    fam = np.vstack([trail(d) for d in range(-60, 61, 5)]); allp = T(sxy)
    dmin = np.hypot(allp[:, None, 0] - fam[None, :, 0], allp[:, None, 1] - fam[None, :, 1]).min(1) * sc
    nearb = sorted([(round(float(d), 1), float(m)) for d, m in zip(dmin, S[:, 2]) if d < 20], key=lambda t: t[1])
    # C. expected signal of a trailed object from star stacks
    L = nom[-1] - nom[0]; exp = {}
    for m0 in (13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5):
        sel = (np.abs(S[:, 2] - m0) < 0.25) & inb(allp, 40)
        # isolated: no other star m < m0 + 1.5 within 40"
        st = []
        for ii in np.nonzero(sel)[0]:
            d = np.hypot(*(allp - allp[ii]).T) * sc
            if np.sum((d < 40) & (S[:, 2] < m0 + 1.5)) == 1: st.append(ii)
        if len(st) < 3: exp[m0] = None; continue
        vals = []; pkv = []
        for ii in st:
            c = allp[ii]
            # recentre on the local z maximum within 6"
            kk = int(6 / sc) + 1; x0, y0 = int(round(c[0])), int(round(c[1])); sub = z[y0 - kk:y0 + kk + 1, x0 - kk:x0 + kk + 1]
            yy, xx = np.unravel_index(sub.argmax(), sub.shape); c = np.array([x0 - kk + xx, y0 - kk + yy], float); pkv.append(sub.max())
            # mean over object positions u (trail) of the mean along the trail samples v: z(c + v - u)
            u = np.linspace(-0.5, 0.5, 25)[:, None] * L[None, :]
            acc = [float(map_coordinates(z, [c[1] + u[:, 1] - uu[1], c[0] + u[:, 0] - uu[0]], order=1).mean()) for uu in u]
            vals.append(np.mean(acc))
        exp[m0] = {"n_stars": len(st), "median_peak_z": round(float(np.median(pkv)), 1), "expected_trail_mean_z": round(float(np.median(vals)), 2)}
    res[pid] = {"scale": round(sc, 3), "polarity": pol, "n_fit": int(ok.sum()), "fit_rms_arcsec": round(rms, 2),
                "my_minus_solver_midpoint_arcsec": round(dpred, 2), "trail_arcsec": round(float(np.hypot(*L) * sc), 1),
                "trail_mean_z_dt0": round(val(nom), 2), "p_dt0_random_translations": float((1 + np.sum(ctrl >= val(nom))) / (len(ctrl) + 1)),
                "ctrl_sd": round(float(ctrl.std()), 3),
                "on_track_by_dt": {int(d): round(v, 2) for d, v in zip(dts, on)},
                "map_peak": {"dt_min": int(dts[jx]), "cross_arcsec": int(crs[i]), "z": round(float(Mp[i, jx]), 2)},
                "map_cross_at_dt0": {int(c): round(float(Mp[a, list(dts).index(0)]), 2) for a, c in enumerate(crs)},
                "catalogue_stars_within_20arcsec_of_track_family": nearb, "expected_by_mag": exp}
    np.save(OUT.parent / f"map_{pid}.npy", Mp)
OUT.write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
