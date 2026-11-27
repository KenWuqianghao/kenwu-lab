"""Topocentric predicted track for each plate: Horizons astrometric RA/Dec every 5 min from midpoint -2 h to +2 h,
plus Sun and object altitude at the midpoint. Writes data/predictions.json."""
import os, json, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import hz
from plates import PLATES, PLATES2, SITE
ROUND = sys.argv[1] if len(sys.argv) > 1 else "1"
PLATES = PLATES2 if ROUND == "2" else PLATES
from astropy.time import Time, TimeDelta
out = []
for obj, hid, plate, sol, mid, expmin, lim in PLATES:
    series = plate.rstrip("0123456789")
    site = SITE[series]
    t = Time(mid + ":00", format="isot", scale="utc")
    t0 = (t - TimeDelta(7200, format="sec")).iso[:16]; t1 = (t + TimeDelta(7200, format="sec")).iso[:16]
    rows = hz.eph(hid, t0, t1, "5m", center=f"{site}@399", quantities="1,4,9,3")
    track = []
    for r in rows:
        track.append({"jd": float(r["Date_________JDUT"]), "ra": float(r["R.A._(ICRF)"]), "dec": float(r["DEC_(ICRF)"]),
                      "V": hz.num(r["APmag"]), "alt": hz.num(r["Elev_(a-app)"]),
                      "dra_cosd": hz.num(r["dRA*cosD"]), "ddec": hz.num(r["d(DEC)/dt"])})
    assert all(None not in (x["V"], x["alt"], x["ddec"]) for x in track), plate
    m = min(track, key=lambda x: abs(x["jd"] - t.jd))
    assert abs(m["jd"] - t.jd) * 1440 < 0.01, (plate, "no ephemeris row at the midpoint")
    sun = hz.eph("10", t.iso[:16], (t + TimeDelta(60, format="sec")).iso[:16], "1m", center=f"{site}@399", quantities="4")[0]
    i = track.index(m); a, b = track[max(i - 1, 0)], track[min(i + 1, len(track) - 1)]
    dt_h = (b["jd"] - a["jd"]) * 24
    rate = math.hypot((b["ra"] - a["ra"]) * math.cos(math.radians(m["dec"])), b["dec"] - a["dec"]) * 3600 / dt_h  # arcsec per hour
    out.append({"object": obj, "plate": plate, "solnum": sol, "site": site, "mid": mid, "exptime_min": expmin, "lim": lim,
                "ra": m["ra"], "dec": m["dec"], "V": m["V"], "obj_alt": m["alt"], "sun_alt": hz.num(sun["Elev_(a-app)"]),
                "rate_arcsec_per_h": rate, "trail_arcsec": rate * expmin / 60, "track": track})
    print(f"{obj:8s} {plate:8s} {mid} site {site} V={m['V']:.2f} lim={lim} alt={m['alt']:.0f} sun={sun['Elev_(a-app)']} rate={rate:.0f}\"/h trail={rate*expmin/60:.0f}\"")
(Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).parent.parent / "data").joinpath("predictions.json" if ROUND == "1" else "predictions2.json").write_text(json.dumps(out, indent=1))
