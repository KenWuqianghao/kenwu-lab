"""Verifier control: for a Ganymed plate position, download cutouts of OTHER i-series plates (other dates) at the
same sky position. Ganymed was not there on those dates. Usage: controls_fetch.py OUTDIR"""
import base64, csv, gzip, io, json, sys, time
from pathlib import Path
import requests
BASE = "https://api.starglass.cfa.harvard.edu/public/dasch/dr7"
H = {"User-Agent": "precovery-verify (research script)", "Accept": "application/json"}
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
POS = {"i21050": (310.42111, 63.18767), "i21576": (18.10582, 13.42374), "i21780": (27.44411, -3.37448)}
LIM = {"i21050": 13.873, "i21576": 13.630, "i21780": 13.410}  # src/plates.py, used when queryexps has no limMagAtlas
def post(ep, payload):
    time.sleep(3); r = requests.post(BASE + ep, json=payload, headers=H, timeout=240); r.raise_for_status(); return r.json()
def fl(x):
    try: return float(x)
    except ValueError: return None
log = json.load(open(out / "controls.json")) if (out / "controls.json").exists() else {}
for target, (ra, dec) in POS.items():
    rows = list(csv.DictReader(io.StringIO("\n".join(post("/queryexps", {"ra_deg": ra, "dec_deg": dec})))))
    me = [r for r in rows if r["series"] + r["platenum"].zfill(5) == target and r["solnum"] == "0"][0]
    lim0 = fl(me["limMagAtlas"]) or LIM[target]
    # rule (fixed before any control image was seen): i series, solution 0, limMagAtlas >= target's, edge distance > 1 deg,
    # exposure 8-30 min, another date; take the 2 nearest in time (1 for i21576 and i21780)
    c = [r for r in rows if r["series"] == "i" and r["solnum"] == "0" and r["platenum"].zfill(5) != target[1:]
         and (fl(r["limMagAtlas"]) or 0) >= lim0 and (fl(r["edgedist"]) or 0) > 1 and 8 <= (fl(r["exptime"]) or 0) <= 30
         and r["expdate"][:10] != me["expdate"][:10]]
    c.sort(key=lambda r: abs(float(r["expdate"][:4]) + float(r["expdate"][5:7]) / 12 - float(me["expdate"][:4]) - float(me["expdate"][5:7]) / 12))
    for r in c[: 2 if target == "i21050" else 1]:
        pid = "i" + r["platenum"].zfill(5)
        if (out / f"{target}_ctrl_{pid}.fits.gz").exists(): continue
        raw = base64.b64decode(post("/cutout", {"plate_id": pid, "solution_number": 0, "center_ra_deg": ra, "center_dec_deg": dec}))
        gzip.decompress(raw); (out / f"{target}_ctrl_{pid}.fits.gz").write_bytes(raw)
        log[f"{target}_ctrl_{pid}"] = {"expdate": r["expdate"], "exptime": r["exptime"], "lim": r["limMagAtlas"], "target_lim": lim0}
        print(target, "control", pid, r["expdate"], r["exptime"], r["limMagAtlas"])
(out / "controls.json").write_text(json.dumps(log, indent=1))
