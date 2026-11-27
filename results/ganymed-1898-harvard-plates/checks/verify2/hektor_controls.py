"""Verifier round 2: control plates for the Hektor claim. Rule fixed here before any download:
all Wolf Doppelastrograph plates of 1902-1903 in the three-plate pattern (short, long, short) whose HDAP coverage
contains the 1901-08-23 Hektor position: G2698, G2699, G2700 (1902-09-03), G3040, G3041, G3042 (1903-08-24),
G3043, G3044, G3045 (1903-08-25, same field name "h Aqr"). Hektor is far away on these dates.
On each control plate: trail-mean z at the 1901 sky positions of the G2281, G2282 and G2283 trails (dt = 0) and the
maximum over time shifts of -60..+60 min, with p from 4000 random translations. Expected if the 1901 signal is a
moving object: no excess. The same code is run on G2281-G2283 for comparison.
Usage: python hektor_controls.py <repo-data-dir> <work-dir> <out.json>"""
import json, sys, re, math, time
from pathlib import Path
import numpy as np, requests
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import gaussian_filter, map_coordinates, maximum_filter
D = Path(sys.argv[1]); W = Path(sys.argv[2]); OUT = Path(sys.argv[3]); W.mkdir(parents=True, exist_ok=True)
CTRL = ["G2698", "G2699", "G2700", "G3040", "G3041", "G3042", "G3043", "G3044", "G3045"]
txt = (OUT.parent / "horizons_624_19010823.txt").read_text(); body = txt.split("$$SOE")[1].split("$$EOE")[0]; eph = []
for l in body.strip().splitlines():
    nums = re.findall(r"-?\d+\.\d+", l); eph.append((float(nums[0]), float(nums[-2]), float(nums[-1])))
eph = np.array(eph); pos = lambda jd: (np.interp(jd, eph[:, 0], eph[:, 1]), np.interp(jd, eph[:, 0], eph[:, 2]))
preds = {p["plate"]: p for p in json.load(open(D / "hdap" / "predictions.json"))}; cat = json.load(open(D / "hdap" / "refcat.json"))["G2282"]
RA0, DE0 = 343.40176, -8.69742
for pid in CTRL:
    f = W / f"{pid}.fits"
    if not f.exists():
        r = requests.get("http://dc.g-vo.org/lswscans/res/positions/dl/dlget", params={"ID": f"ivo://org.gavo.dc/~?lswscans/data/part2/Wolf/FITS/{pid}.fits",
                         "CIRCLE": f"{RA0} {DE0} 0.2"}, timeout=600)
        print(pid, r.status_code, len(r.content), flush=True)
        if r.status_code == 200 and r.content[:6] == b"SIMPLE": f.write_bytes(r.content)
        time.sleep(3)
res = {}
for pid in CTRL + ["G2281", "G2282", "G2283"]:
    f = W / f"{pid}.fits" if pid in CTRL else D / "hdap" / "cutouts" / f"{pid}.fits"
    if not f.exists(): res[pid] = {"status": "no cutout"}; continue
    h = fits.open(f)[0]; img = h.data.astype(float); w = WCS(h.header); sc = float(np.sqrt(abs(np.linalg.det(w.celestial.pixel_scale_matrix))) * 3600)
    yr = float(h.header.get("YEAR", 0)) or (1902.7 if pid < "G3000" else 1903.65) if pid in CTRL else 1901.64
    S = []
    for s in cat:
        try: ra, de, m = float(s["ra_deg"]), float(s["dec_deg"]), float(s["stdmag"])
        except ValueError: continue
        dt = yr - 2000
        S.append((ra + float(s.get("pm_ra_masyr") or 0) * dt / 3.6e6 / math.cos(math.radians(de)), de + float(s.get("pm_dec_masyr") or 0) * dt / 3.6e6, m))
    S = np.array(S); sxy = np.array(w.world_to_pixel_values(S[:, 0], S[:, 1])).T
    def zim(sig):
        z = gaussian_filter(sig, 2.5 / sc) - gaussian_filter(sig, 40 / sc); c = z[30:-30, 30:-30]
        return z / (1.4826 * np.median(np.abs(c - np.median(c))))
    inb = lambda P, b=25: (P[:, 0] > b) & (P[:, 0] < img.shape[1] - b) & (P[:, 1] > b) & (P[:, 1] < img.shape[0] - b)
    zz = zim(img); mx = maximum_filter(np.abs(zz), size=7)
    # polarity and shift together: the sign and integer shift with most z > 5 peaks next to stars m < 14.5
    ref = sxy[(S[:, 2] < 15.5) & inb(sxy)]; best = None
    for pol in (1, -1):
        z = pol * zz; m7 = maximum_filter(z, size=7); ys, xs = np.nonzero((z == m7) & (z > 5)); pk = np.column_stack([xs, ys]).astype(float)
        if len(pk) < 3: continue
        g = int(60 / sc)
        for dx in range(-g, g + 1):
            for dy in range(-g, g + 1):
                q = ref + [dx, dy]; d = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]).min(0); n = int((d < 2).sum())
                if best is None or n > best[0]: best = (n, pol, dx, dy, pk)
    n0, pol, dx, dy, pk = best; z = pol * zz
    A = np.array([[1, 0], [0, 1], [dx, dy]], float); T = lambda P: np.column_stack([P, np.ones(len(P))]) @ A
    for _ in range(3):
        q = T(ref); dd = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]); j = dd.argmin(0); ok = dd[j, np.arange(len(q))] < 5 / sc
        if ok.sum() >= 6: A, *_ = np.linalg.lstsq(np.column_stack([ref[ok], np.ones(ok.sum())]), pk[j[ok]], rcond=None)
    q = T(ref); dd = np.hypot(pk[:, None, 0] - q[None, :, 0], pk[:, None, 1] - q[None, :, 1]); j = dd.argmin(0); ok = dd[j, np.arange(len(q))] < 5 / sc
    rms = float(np.sqrt(np.mean(np.sum((q[ok] - pk[j[ok]]) ** 2, axis=1))) * sc) if ok.sum() else None
    s2p = lambda ra, de: T(np.atleast_2d(np.array(w.world_to_pixel_values(ra, de), dtype=float).T))
    val = lambda P: float(map_coordinates(z, [P[:, 1], P[:, 0]], order=1).mean())
    # depth: median peak z of stars 14.75-15.25
    st = T(sxy[(np.abs(S[:, 2] - 15.0) < 0.25) & inb(sxy, 40)]); k = int(6 / sc) + 1
    depth = float(np.median([z[int(round(y)) - k:int(round(y)) + k + 1, int(round(x)) - k:int(round(x)) + k + 1].max() for x, y in st])) if len(st) else None
    row = {"scale": round(sc, 3), "polarity": pol, "n_fit": int(ok.sum()), "fit_rms_arcsec": rms and round(rms, 2), "median_peak_z_stars_mag15": depth and round(depth, 1), "trails": {}}
    rng = np.random.default_rng(12)
    targets = ["G2281", "G2282", "G2283"] if pid in CTRL else [pid]
    for tp in targets:
        p = preds[tp]; jd0, jd1 = Time(p["start"], scale="utc").jd, Time(p["end"], scale="utc").jd
        fam = []
        for d in range(-60, 61, 5):
            ra, de = pos(np.linspace(jd0, jd1, 60) + d / 1440); fam.append(s2p(ra, de))
        allp = np.vstack(fam)
        def stat(o):
            if (allp + o).min() < 15 or (allp[:, 0] + o[0]).max() > z.shape[1] - 15 or (allp[:, 1] + o[1]).max() > z.shape[0] - 15: return None
            v = [val(P + o) for P in fam]; return v[12], max(v)
        obs = stat(np.zeros(2))
        if obs is None: row["trails"][tp] = None; continue
        c = []
        while len(c) < 4000:
            o = rng.uniform(-230, 230, 2)
            if np.hypot(*o) * sc < 90: continue
            v = stat(o)
            if v: c.append(v)
        c = np.array(c)
        row["trails"][tp] = {"z_dt0": round(obs[0], 2), "p_dt0": round(float((1 + (c[:, 0] >= obs[0]).sum()) / 4001), 4),
                             "z_max_dt": round(obs[1], 2), "p_max_dt": round(float((1 + (c[:, 1] >= obs[1]).sum()) / 4001), 4)}
    res[pid] = row; print(pid, json.dumps(row), flush=True)
OUT.write_text(json.dumps(res, indent=1))
