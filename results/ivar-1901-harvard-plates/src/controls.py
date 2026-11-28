"""Other-date control plates (rule fixed before any control image was seen; first run in the solve stage as
checks/controls.py). For each passing 1901 plate, take the 2 other b-series plates (solnum 0, other date,
limMagAtlas >= the target plate's, exptime within a factor 2 of it, edgedist > 0.5 deg) nearest in time that contain
the Ivar midpoint position. Ivar was not there on those dates. Statistic: max z within 5" of the position after the
same astrometric refit as src/measure.py, on the target plate and on the controls.
Reads predictions.json, results.json and cutouts/ from the data directory (PRECOVERY_DATA, default data/).
Writes controls/ (control cutouts) and controls.json there."""
import base64, csv, gzip, io, json, os, sys, warnings
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent)); import measure as M, dasch
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
OUT = D / "controls"; OUT.mkdir(parents=True, exist_ok=True)
preds = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
res = json.load(open(D / "results.json"))["plates"]
def fl(x):
    try: return float(x)
    except (TypeError, ValueError): return None
def z5(path, ra, dec, lim, jd):
    h = fits.open(io.BytesIO(gzip.decompress(path.read_bytes()))); z = M.zimage(h[0].data.astype(float)); w = WCS(h[0].header)
    cat = dasch.querycat(ra, dec, 700); stars = M.stars_at_epoch(cat, jd)
    s2p, fit = M.refit(z, w, stars, lim); x, y = s2p(np.array([ra]), np.array([dec]))[0]
    Y, X = np.mgrid[0:z.shape[0], 0:z.shape[1]]; m = np.hypot(X - x, Y - y) <= 5 / 1.44
    return float(z[m].max()), fit
out = {}
for r in res:
    if not r["pass"] or not r["mid"].startswith("1901"): continue
    p = preds[r["plate"]]; ra, dec = p["ra"], p["dec"]
    rows = list(csv.DictReader(io.StringIO("\n".join(dasch._post("/dasch/dr7/queryexps", {"ra_deg": ra, "dec_deg": dec}, timeout=240)))))
    c = [e for e in rows if e["series"] == "b" and e["solnum"] == "0" and "b" + e["platenum"].zfill(5) != p["plate"]
         and (fl(e["limMagAtlas"]) or 0) >= p["lim"] and p["exptime_min"] / 2 <= (fl(e["exptime"]) or 0) <= p["exptime_min"] * 2
         and (fl(e["edgedist"]) or 0) > 0.5 and e["expdate"][:10] != p["mid"][:10]]
    tj = Time(p["mid"] + ":00").jd
    c.sort(key=lambda e: abs(Time(e["expdate"].rstrip("Z")[:19]).jd - tj))
    zt, _ = z5(D / "cutouts" / f"{p['plate']}_s0.fits.gz", ra, dec, p["lim"], tj)
    ent = {"target": {"plate": p["plate"], "z5": zt}, "controls": []}
    for e in c[:2]:
        pid = "b" + e["platenum"].zfill(5); f = OUT / f"{p['plate']}_ctrl_{pid}.fits.gz"
        if not f.exists():
            raw = base64.b64decode(dasch._post("/dasch/dr7/cutout", {"plate_id": pid, "solution_number": 0, "center_ra_deg": ra, "center_dec_deg": dec}, timeout=240))
            gzip.decompress(raw); f.write_bytes(raw)
        zc, fit = z5(f, ra, dec, fl(e["limMagAtlas"]), Time(e["expdate"].rstrip("Z")[:19]).jd)
        ent["controls"].append({"plate": pid, "expdate": e["expdate"], "exptime": e["exptime"], "lim": e["limMagAtlas"], "z5": zc, "fit": fit.get("kind"), "nstars": fit["n"]})
    out[p["plate"]] = ent; print(p["plate"], json.dumps(ent), flush=True)
(D / "controls.json").write_text(json.dumps(out, indent=1))
