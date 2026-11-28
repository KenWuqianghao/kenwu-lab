import json, sys, requests, math
R = sys.argv[1]
preds = json.load(open(R + "/data/predictions.json"))
def hz(cmd, t, center):
    p = {"format": "json", "COMMAND": f"'{cmd}'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER",
         "CENTER": f"'{center}'", "TLIST": f"'{t}'", "QUANTITIES": "'1,9,3'", "CSV_FORMAT": "YES", "ANG_FORMAT": "DEG"}
    r = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=p, timeout=120).json()["result"]
    body = r[r.index("$$SOE") + 5:r.index("$$EOE")].strip().split(",")
    return [x.strip() for x in body], r
for p in preds:
    t = p["mid"].replace("T", " ")
    for c in ("800@399", "500@399", "802@399"):
        v, raw = hz("1627;", t, c)
        ra, dec = float(v[3]), float(v[4])
        d = math.hypot((ra - p["ra"]) * math.cos(math.radians(dec)), dec - p["dec"]) * 3600
        print(p["plate"], p["mid"], c, ra, dec, "V", v[7], "diff from committed pred arcsec %.1f" % d)
print([l for l in raw.splitlines() if "Center-site" in l or "Target body" in l or "Center geodetic" in l])
