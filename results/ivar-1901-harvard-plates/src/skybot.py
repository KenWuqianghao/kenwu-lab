"""IMCCE SkyBoT cone search (radius 0.1 deg = 360") at the Horizons midpoint position of Ivar on each passing 1901
plate, MPC site 800, epoch = DASCH midpoint (JD, UTC). Lists every known asteroid or comet in the cone, with its
distance from the search centre. A check made in the solve and verify stages, not a registered test.
Reads predictions.json and results.json from the data directory (PRECOVERY_DATA, default data/).
Writes skybot.json there. The service sometimes fails (the verify stage saw a server crash, and the write stage saw
answers with no object list). A query is tried up to 4 times until the answer has "# Flag: 1" (objects found);
otherwise the script stops with an error, and checks/rerun.py skips the SkyBoT values."""
import json, os, time
from pathlib import Path
import requests
from astropy.time import Time
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
URL = "https://ssp.imcce.fr/webservices/skybot/api/conesearch.php"
preds = {p["plate"]: p for p in json.load(open(D / "predictions.json"))}
out = {}
for r in json.load(open(D / "results.json"))["plates"]:
    if not r["pass"] or not r["mid"].startswith("1901"): continue
    p = preds[r["plate"]]; jd = round(Time(p["mid"] + ":00", scale="utc").jd, 6)
    q = {"-ep": jd, "-ra": p["ra"], "-dec": p["dec"], "-rd": 0.1, "-mime": "text", "-output": "basic", "-loc": "800", "-objFilter": "110"}
    for a in range(4):
        try:
            txt = requests.get(URL, params=q, timeout=120).text
            if "# Flag: 1" in txt: break
        except requests.RequestException:
            pass
        time.sleep(15)
    else:
        raise RuntimeError(f"SkyBoT failed for {r['plate']}")
    objs = []
    for line in txt.splitlines():
        if line.startswith("#") or "|" not in line: continue
        f = [x.strip() for x in line.split("|")]
        objs.append({"num": f[0], "name": f[1], "class": f[4], "Mv": float(f[5]), "d_arcsec": round(float(f[7]), 1)})
    objs.sort(key=lambda o: o["d_arcsec"])
    out[r["plate"]] = {"jd": jd, "objects": objs}; print(r["plate"], json.dumps(out[r["plate"]]), flush=True)
    time.sleep(2)
(D / "skybot.json").write_text(json.dumps(out, indent=1))
