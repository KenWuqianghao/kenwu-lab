"""Heidelberg (HDAP, GAVO lsw.plates) plates 1895-1907 that contain (624) Hektor.
Input: data/hdap/plates_1895_1907.csv (TAP query in data/hdap/README). Ephemeris: JPL Horizons, geocentric, daily.
Output: data/hdap/hektor_cover.csv: plate, instrument, start/end UT, exposure, Hektor RA/Dec/V at mid-exposure,
offset from the plate centre and distance to the plate edge (deg)."""
import csv, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import hz
import numpy as np
D = Path(__file__).resolve().parent.parent / "data" / "hdap"
rows = hz.eph("624;", "1895-01-01", "1907-02-12", "1d", quantities="1,9")
E = [(float(r["Date_________JDUT"]) - 2400000.5, float(r["R.A._(ICRF)"]), float(r["DEC_(ICRF)"]), hz.num(r["APmag"])) for r in rows
     if hz.num(r["APmag"]) is not None]
em = np.array([e[0] for e in E]); era = np.unwrap(np.radians([e[1] for e in E])); ede = np.array([e[2] for e in E]); ev = np.array([e[3] for e in E])
def tan(ra, dec, ra0, dec0):
    ra, dec, ra0, dec0 = map(np.radians, (ra, dec, ra0, dec0))
    c = np.sin(dec) * np.sin(dec0) + np.cos(dec) * np.cos(dec0) * np.cos(ra - ra0)
    return np.degrees(np.cos(dec) * np.sin(ra - ra0) / c), np.degrees((np.sin(dec) * np.cos(dec0) - np.cos(dec) * np.sin(dec0) * np.cos(ra - ra0)) / c)
def inside(px, py, xs, ys):
    ins = False
    for i in range(len(xs)):
        j = i - 1
        if (ys[i] > py) != (ys[j] > py) and px < (xs[j] - xs[i]) * (py - ys[i]) / (ys[j] - ys[i]) + xs[i]: ins = not ins
    return ins
def edge(px, py, xs, ys):
    d = []
    for i in range(len(xs)):
        x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]; vx, vy = x1 - x0, y1 - y0
        t = max(0, min(1, ((px - x0) * vx + (py - y0) * vy) / (vx * vx + vy * vy))); d.append(math.hypot(px - x0 - t * vx, py - y0 - t * vy))
    return min(d)
out = []
for r in csv.DictReader(open(D / "plates_1895_1907.csv")):
    if not (r["dateObs"] and r["centerAlpha"] and r["centerDelta"]): continue  # plates without a position solution
    m = float(r["dateObs"]); ra0, de0 = float(r["centerAlpha"]), float(r["centerDelta"])
    if not (em[0] <= m <= em[-1]) or not r["coverage"]: continue
    ra = math.degrees(np.interp(m, em, era)) % 360; de = float(np.interp(m, em, ede)); V = float(np.interp(m, em, ev))
    sep = math.degrees(math.acos(min(1, math.sin(math.radians(de)) * math.sin(math.radians(de0)) + math.cos(math.radians(de)) * math.cos(math.radians(de0)) * math.cos(math.radians(ra - ra0)))))
    if sep > 15: continue
    p = json.loads(r["coverage"]); xs, ys = tan(np.array(p[0::2]), np.array(p[1::2]), ra0, de0); x, y = tan(ra, de, ra0, de0)
    if inside(x, y, xs, ys):
        out.append({"plate": r["plateID"], "inst": r["instId"].split(",")[-1].strip(), "start": r["startTime"], "end": r["endTime"],
                    "exposure_s": r["exposure"], "object": r["object"], "accref": r["accref"], "mjd_mid": m, "ra": round(ra, 5), "dec": round(de, 5),
                    "V": round(V, 2), "offset_deg": round(sep, 2), "edge_deg": round(edge(x, y, xs, ys), 2)})
w = csv.DictWriter(open(D / "hektor_cover.csv", "w", newline=""), fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out), "plates contain Hektor")
for o in out: print(o["plate"], o["start"], o["inst"], o["exposure_s"], o["V"], o["offset_deg"], o["edge_deg"], o["object"])
