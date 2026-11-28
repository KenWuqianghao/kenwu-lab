"""Fresh JPL Horizons positions of (1627) Ivar at each plate midpoint, compared with the fixed predictions.
For each plate: topocentric for the series site (800 Arequipa for b, 802 Cambridge for ac), geocentric (500), and
the other site. Reads predictions.json from the data directory (PRECOVERY_DATA, default data/). Writes
horizons_check.json there: offsets in arcsec and the orbit solution that Horizons served. Adapted from the
verification script checks/verify/hzcheck.py."""
import json, math, os, re, time
from pathlib import Path
import requests
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
def hz(t, center):
    p = {"format": "json", "COMMAND": "'1627;'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER",
         "CENTER": f"'{center}'", "TLIST": f"'{t}'", "QUANTITIES": "'1,9,3'", "CSV_FORMAT": "YES", "ANG_FORMAT": "DEG"}
    for a in range(3):
        try:
            r = requests.get(URL, params=p, timeout=120); r.raise_for_status(); txt = r.json()["result"]; break
        except Exception:
            if a == 2: raise
            time.sleep(10)
    v = [x.strip() for x in txt[txt.index("$$SOE") + 5:txt.index("$$EOE")].strip().split(",")]
    soln = re.search(r"Target body name: 1627 Ivar.*\{source: (\S+)\}", txt)
    return float(v[3]), float(v[4]), float(v[5]), soln.group(1) if soln else None
def sep(ra1, d1, ra2, d2):
    return math.hypot((ra1 - ra2) * math.cos(math.radians(d2)), d1 - d2) * 3600
out = {}
for p in json.load(open(D / "predictions.json")):
    t = p["mid"].replace("T", " "); other = "802" if p["site"] == "800" else "800"
    ent = {}
    for name, c in (("site", p["site"]), ("geocentre", "500"), ("other_site", other)):
        ra, dec, V, soln = hz(t, f"{c}@399")
        ent[name] = {"center": c, "offset_arcsec": round(sep(ra, dec, p["ra"], p["dec"]), 2), "V": V}
        ent["solution"] = soln
        time.sleep(0.5)
    out[p["plate"]] = ent; print(p["plate"], json.dumps(ent), flush=True)
(D / "horizons_check.json").write_text(json.dumps(out, indent=1))
