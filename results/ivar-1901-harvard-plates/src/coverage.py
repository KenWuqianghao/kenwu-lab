"""Plate selection for (1627) Ivar before its first observation (1929-09-25). Run before any image is seen.
Rule (fixed): apparitions with geocentric V < 12.6 (src/apps.py): 1901-05-01..1901-10-20, 1906-07-25..1906-09-15,
1929-05-01..1929-09-24. Sample the geocentric track every 4 days; at each sample, DASCH /queryexps; keep exposures
with |expdate - sample| <= 2.0 d, series in SITE (a, b: Arequipa 800; i, ac, me: Cambridge 802), solnum 0,
limMagAtlas present. Then compute the topocentric position at the DASCH midpoint. (No second coverage query: a plate whose cutout
request returns 422 "does not overlap" is recorded as "not covered".) Keep if sun alt < -12, object alt > 15, and
lim - (V + 0.8 + 2.5 log10(max(1, trail/30"))) >= 0.3 (0.8 = assumed B-V; trail = rate x exptime)."""
import csv, io, json, math, sys, time
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).parent)); import hz
from astropy.time import Time, TimeDelta
BASE = "https://api.starglass.cfa.harvard.edu/public/dasch/dr7"
SITE = {"a": "800", "b": "800", "i": "802", "ac": "802", "me": "802"}
APPS = [("1901-05-01", "1901-10-20"), ("1906-07-25", "1906-09-15"), ("1929-05-01", "1929-09-24")]
D = Path(__file__).resolve().parent.parent / "data"
def q(ra, dec):
    time.sleep(2)
    for a in range(3):
        try:
            r = requests.post(BASE + "/queryexps", json={"ra_deg": ra % 360, "dec_deg": dec}, timeout=240); r.raise_for_status()
            return list(csv.DictReader(io.StringIO("\n".join(r.json()))))
        except Exception as e:
            print("retry", e); time.sleep(30)
    raise RuntimeError("queryexps failed")
def fl(x):
    try: return float(x)
    except: return None
cand = {}
from concurrent.futures import ThreadPoolExecutor
samples = [(float(r["Date_________JDUT"]), float(r["R.A._(ICRF)"]), float(r["DEC_(ICRF)"])) for a, b in APPS for r in hz.eph("1627;", a, b, "4d")]
print("samples", len(samples), flush=True)
with ThreadPoolExecutor(4) as ex:
    results = list(ex.map(lambda s: q(s[1], s[2]), samples))
for (jd, ra, de), res in zip(samples, results):
        for e in res:
            if e["series"] not in SITE or e["solnum"] != "0" or not fl(e["limMagAtlas"]) or e["expdate"][:4] not in ("1901", "1906", "1929"): continue
            t = Time(e["expdate"].rstrip("Z")[:19], format="isot", scale="utc")
            if abs(t.jd - jd) <= 2.0:
                pid = e["series"] + e["platenum"].zfill(5)
                cand[pid] = e
print("candidates", len(cand), flush=True)
sel = []
for pid, e in sorted(cand.items(), key=lambda kv: kv[1]["expdate"]):
    site = SITE[e["series"]]; t = Time(e["expdate"].rstrip("Z")[:19], format="isot", scale="utc")
    mid = t.iso[:16]
    rows = hz.eph("1627;", mid, (t + TimeDelta(60, format="sec")).iso[:16], "1m", center=f"{site}@399", quantities="1,3,4,9")
    m = rows[0]; ra, de = float(m["R.A._(ICRF)"]), float(m["DEC_(ICRF)"]); V = hz.num(m["APmag"]); alt = hz.num(m["Elev_(a-app)"])
    rate = math.hypot(hz.num(m["dRA*cosD"]), hz.num(m["d(DEC)/dt"]))
    sun = hz.num(hz.eph("10", mid, (t + TimeDelta(60, format="sec")).iso[:16], "1m", center=f"{site}@399", quantities="4")[0]["Elev_(a-app)"])
    exp = fl(e["exptime"]) or 0; trail = rate * exp / 60; lim = fl(e["limMagAtlas"])
    veff = V + 0.8 + 2.5 * math.log10(max(1, trail / 30))
    edge = None
    ok = sun < -12 and alt > 15 and lim - veff >= 0.3
    row = dict(plate=pid, mid=e["expdate"], exptime=exp, lim=lim, site=site, ra=ra, dec=de, V=V, alt=alt, sun=sun,
               rate=rate, trail=trail, veff=veff, edge=edge, selected=ok)
    sel.append(row); print(row, flush=True)
(D / "coverage.json").write_text(json.dumps(sel, indent=1))
print("selected", sum(r["selected"] for r in sel), "of", len(sel))
