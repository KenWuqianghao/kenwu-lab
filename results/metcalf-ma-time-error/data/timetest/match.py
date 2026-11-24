"""Time test, step 2-3: for each MPC observation from Taunton (803) or Winchester (799), 1905-1913,
find DASCH exposures that night whose field contains the observed position, and compare the
DASCH exposure midpoint with the MPC time.

Prediction under convention A (Metcalf logged local mean time counted from noon; DASCH read the
value as local sidereal time): the DASCH time t_D is the UT near the MPC time at which
LST(t_D) = LMT_true - 12 h. Shift_A = t_D - t_MPC. Null: shift ~ 0 (within half an exposure).
Metadata only (queryexps); raw replies in timetest/raw/. Output: timetest/matches.csv."""
import csv, json, sys, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore")
from astropy.utils import iers
iers.conf.auto_download = False
from astropy.time import Time
import astropy.units as u

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from pluto_dasch import dasch  # noqa: E402

LON = {"803": -71.10, "799": -71.14}  # Taunton, Winchester (MPC codes), deg east


def parse(line):
    y, mo, d = int(line[15:19]), int(line[20:22]), float(line[23:32])
    t = Time(f"{y:04d}-{mo:02d}-01T00:00:00", scale="utc") + (d - 1) * u.day
    rah = line[32:44].split(); ded = line[44:56].split()
    ra = 15 * (float(rah[0]) + float(rah[1]) / 60 + (float(rah[2]) if len(rah) > 2 else 0) / 3600)
    sg = -1 if ded[0].startswith("-") else 1
    de = sg * (abs(float(ded[0])) + float(ded[1]) / 60 + (float(ded[2]) if len(ded) > 2 else 0) / 3600)
    return dict(obj=line[:12].strip(), disc=line[12] == "*", t=t, ra=ra, dec=de, code=line[77:80],
                tprec=len(line[23:32].strip().split(".")[1]) if "." in line[23:32] else 0)


def lst(t, lon):
    return t.sidereal_time("mean", longitude=lon * u.deg).hour % 24


def shift_A(t, lon):
    lmt = (t.datetime.hour + t.datetime.minute / 60 + t.datetime.second / 3600 + lon / 15) % 24
    target = (lmt - 12) % 24
    ks = np.arange(-14, 14, 0.002)
    tt = t + ks * u.hour
    d = (lst(tt, lon) - target + 12) % 24 - 12
    return float(ks[np.argmin(np.abs(d))])


def main():
    lines = [l.rstrip("\n") for l in open(HERE / "mpc_obs80.txt") if not l.startswith("#")]
    obs = []
    for l in lines:
        if len(l) >= 80 and l[77:80] in LON and l[14] in "AX":
            o = parse(l)
            if 1905 <= o["t"].datetime.year <= 1913:
                obs.append(o)
    print(f"{len(obs)} observations from 803/799, 1905-1913", flush=True)
    raw = HERE / "raw"; raw.mkdir(exist_ok=True)
    rows = []
    for i, o in enumerate(sorted(obs, key=lambda o: o["t"].jd)):
        key = f"{o['t'].jd:.4f}_{o['ra']:.3f}_{o['dec']:.3f}"
        f = raw / f"{key}.json"
        if f.exists():
            res = json.loads(f.read_text())
        else:
            a = (o["t"] - 1.0 * u.day).isot + "Z"; b = (o["t"] + 1.0 * u.day).isot + "Z"
            res = dasch.queryexps(o["ra"], o["dec"], a, b)
            f.write_text(json.dumps(res))
        sA = shift_A(o["t"], LON[o["code"]])
        hits = [r for r in res if r["series"].startswith("m")]
        print(f"[{i+1}/{len(obs)}] {o['obj']:12s} {o['t'].isot[:16]} {o['code']} all={len(res)} m-series={len(hits)} "
              f"predA={sA:+.2f}h", flush=True)
        for r in res:
            try:
                tD = Time(r["expdate"].rstrip("Z"), format="isot", scale="utc")
            except Exception:
                continue
            rows.append(dict(obj=o["obj"], disc=o["disc"], code=o["code"], t_mpc=o["t"].isot[:19], t_prec_dec=o["tprec"],
                             ra=round(o["ra"], 4), dec=round(o["dec"], 4), series=r["series"], platenum=r["platenum"],
                             solnum=r["solnum"], expnum=r["expnum"], wcssource=r["wcssource"], t_dasch=r["expdate"],
                             exptime_min=r["exptime"], lim=r["limMagApass"], edgedist_cm=r["edgedist"],
                             offset_h=round((tD - o["t"]).to(u.hour).value, 3), pred_A_h=round(sA, 3)))
    with open(HERE / "matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} exposure matches", flush=True)


if __name__ == "__main__":
    main()
