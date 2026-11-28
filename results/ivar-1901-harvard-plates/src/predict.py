"""Predicted topocentric track per selected plate (Horizons, every 5 min, midpoint +-2 h). Adapted from
ganymed-1898-harvard-plates/src/predict.py. Plates: data/coverage.json, selected == True; if more than 30, the 30
with the largest margin lim - veff. Writes data/predictions.json."""
import json, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import hz
from astropy.time import Time, TimeDelta
D = Path(__file__).resolve().parent.parent / "data"
cov = [r for r in json.load(open(D / "coverage.json")) if r["selected"]]
cov = sorted(cov, key=lambda r: -(r["lim"] - r["veff"]))[:30]
cov.sort(key=lambda r: r["mid"])
out = []
for c in cov:
    t = Time(c["mid"].rstrip("Z")[:19], format="isot", scale="utc"); t = Time(t.iso[:16] + ":00", scale="utc")
    t0 = (t - TimeDelta(7200, format="sec")).iso[:16]; t1 = (t + TimeDelta(7200, format="sec")).iso[:16]
    rows = hz.eph("1627;", t0, t1, "5m", center=f"{c['site']}@399", quantities="1,4,9,3")
    track = [{"jd": float(r["Date_________JDUT"]), "ra": float(r["R.A._(ICRF)"]), "dec": float(r["DEC_(ICRF)"]),
              "V": hz.num(r["APmag"])} for r in rows]
    m = min(track, key=lambda x: abs(x["jd"] - t.jd)); assert abs(m["jd"] - t.jd) * 1440 < 0.01, c["plate"]
    out.append({"object": "Ivar", "plate": c["plate"], "solnum": 0, "site": c["site"], "mid": t.iso[:16].replace(" ", "T"),
                "exptime_min": c["exptime"], "lim": c["lim"], "ra": m["ra"], "dec": m["dec"], "V": m["V"],
                "trail_arcsec": c["trail"], "track": track})
    print(c["plate"], out[-1]["mid"], f"V={m['V']:.2f} lim={c['lim']} trail={c['trail']:.0f}")
(D / "predictions.json").write_text(json.dumps(out, indent=1))
