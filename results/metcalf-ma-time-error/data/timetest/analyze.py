"""Time test, step 3. Reads timetest/matches.csv (from match.py) and writes results/time_test.txt.

For each Metcalf observation in the MPC (Taunton 803 / Winchester 799, 1905-1913):
  offset   = DASCH exposure midpoint - MPC time (h)
  predA    = shift predicted if Metcalf's log gave local mean time counted from noon and DASCH read
             it as local sidereal time (computed per date by match.py; no fitted parameter)
  res_null = offset of the ma plate nearest to 0 h
  res_A    = offset - predA of the ma plate nearest to predA
Both hypotheses pick their own best plate from the same candidates (same freedom). Residuals wrap to
[-12, 12) h because DASCH dates and the 24 h cycle can differ by a day. Only ma plates count;
DASCH times of exactly 00:00:00 (date only) are excluded. Observations at the same time and site
(several objects on one plate) count once.

Chance test: shuffle predA among the observations (10,000 times) and count how often as many
observations fall within 1.5 h as with the true predA.
Fine structure: res_A + 0.26 h (Eastern Standard Time, 75 deg W, in place of Taunton local mean
time, 71.1 deg W) and res_A + 0.26 h + exposure time."""
import csv
from pathlib import Path
import numpy as np
import match
from astropy.time import Time
import astropy.units as u

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "results" / "time_test.txt"
EST = 0.26  # h; (75 - 71.1) deg / 15 = 0.26 h
wrap = lambda h: (h + 12) % 24 - 12


def main():
    allrows = list(csv.DictReader(open(HERE / "matches.csv")))
    discs = set()
    for l in open(HERE / "mpc_obs80.txt"):
        if len(l) >= 80 and l[12] == "*" and l[77:80] in match.LON:
            o = match.parse(l)
            discs.add((o["obj"], o["t"].isot[:16], o["code"]))
    log = [l.split() for l in open(HERE / "match.log") if l.startswith("[")]
    logobs = [(l[1], l[2], l[3], l[6].split("=")[1].rstrip("h")) for l in log]  # obj, t(min), code, predA
    rows = [r for r in allrows if r["series"] == "ma" and not r["t_dasch"].endswith("T00:00:00")]
    by = {}
    for r in rows:
        by.setdefault((r["obj"], r["t_mpc"][:16], r["code"]), []).append(r)

    L = []
    P = lambda s="": L.append(s)
    P("Time test: DASCH ma-plate times vs MPC times of Metcalf's own observations, 1905-1913")
    P("Sites: Taunton (MPC 803, 71.10 W), Winchester (MPC 799, 71.14 W). Telescope series: ma (DASCH).")
    P("offset = DASCH exposure midpoint - MPC time. predA = shift if 'local mean time from noon' was read as LST.")
    P("res_null = offset of the ma plate nearest 0 h; res_A = offset - predA for the ma plate nearest predA.")
    P("n = ma candidates (field contains the MPC position, within +-1 day). disc * = MPC discovery observation.")
    P("class: S = res_A within 0.15 h of -0.26 h; E = within 0.15 h of -0.26 h - exposure time; '-' = neither.")
    P()
    P(f"{'object':12s} d {'MPC time (UT)':16s} site  n {'plate':8s} {'DASCH midpoint':16s} {'exp':>4s} {'offset':>7s} {'predA':>7s} {'res_null':>8s} {'res_A':>7s} cl")
    seen, rn, ra, pa, cand, cls = set(), [], [], [], [], []
    for (obj, t, code, predA) in logobs:
        k = (obj, t, code)
        rs = by.get(k)
        disc = "*" if k in discs else " "
        if not rs:
            P(f"{obj:12s} {disc} {t:16s} {code}   0 (no ma plate with a time in DASCH metadata)")
            continue
        pA = float(predA)
        bn = min(rs, key=lambda r: abs(wrap(float(r["offset_h"]))))
        ba = min(rs, key=lambda r: abs(wrap(float(r["offset_h"]) - pA)))
        n0, a0 = wrap(float(bn["offset_h"])), wrap(float(ba["offset_h"]) - pA)
        ex = float(ba["exptime_min"]) / 60
        c = "S" if abs(a0 + EST) < 0.15 else "E" if abs(a0 + EST + ex) < 0.15 else "-"
        dup = (t, code) in seen
        seen.add((t, code))
        note = "  (same time as above, not counted)" if dup else ""
        if not dup:
            rn.append(n0); ra.append(a0); pa.append(pA); cls.append(c)
            cand.append([float(r["offset_h"]) for r in rs])
        P(f"{obj:12s} {disc} {t:16s} {code} {len(rs):2d} ma{int(ba['platenum']):05d}  {ba['t_dasch'][:16]} {float(ba['exptime_min']):4.0f} "
          f"{float(ba['offset_h']):+7.2f} {pA:+7.2f} {n0:+8.2f} {a0:+7.2f} {c}{note}")
    rn, ra, pa = map(np.array, (rn, ra, pa))
    n = len(ra)
    hit = lambda p: sum(min(abs(wrap(o - q)) for o in cs) <= 1.5 for cs, q in zip(cand, p))
    rng = np.random.default_rng(1)
    h_true = hit(pa)
    h_shuf = np.array([hit(rng.permutation(pa)) for _ in range(10000)])
    P()
    P(f"Independent observation times with an ma plate: {n}")
    P(f"null (DASCH time = MPC time): median |res| {np.median(np.abs(rn)):.2f} h; |res| <= 1.5 h for {np.sum(np.abs(rn) <= 1.5)}/{n}")
    P(f"A (LMT from noon read as LST): median |res| {np.median(np.abs(ra)):.2f} h; |res| <= 1.5 h for {np.sum(np.abs(ra) <= 1.5)}/{n}; "
      f"median res {np.median(ra):+.2f} h")
    P(f"chance test: shuffled predA gives |res| <= 1.5 h for mean {h_shuf.mean():.1f}/{n}, max {h_shuf.max()}/{n} in 10,000 shuffles; "
      f"true predA {h_true}/{n} (P < 1e-4)")
    P(f"fine structure: class S {cls.count('S')}, class E {cls.count('E')}, neither {cls.count('-')} (of {n})")
    P()
    P("Per series (same test for every DASCH series with a match; times of exactly 00:00:00 excluded):")
    P(f"  {'series':6s} {'obs':>4s} {'date-only':>9s} {'A<=1.5h':>8s} {'null<=1.5h':>10s} {'shuffle mean/max':>16s}")
    for ser in sorted({r["series"] for r in allrows}):
        sr = [r for r in allrows if r["series"] == ser]
        dated = [r for r in sr if not r["t_dasch"].endswith("T00:00:00")]
        g = {}
        for r in dated:
            g.setdefault((r["t_mpc"][:16], r["code"]), []).append(r)
        if not g:
            P(f"  {ser:6s} {len({(r['t_mpc'][:16], r['code']) for r in sr}):4d} {len(sr) - len(dated):9d}  (no exposure with a time)")
            continue
        cs = [[float(r["offset_h"]) for r in v] for v in g.values()]
        pp = np.array([float(v[0]["pred_A_h"]) for v in g.values()])
        hA = sum(min(abs(wrap(o - q)) for o in c) <= 1.5 for c, q in zip(cs, pp))
        h0 = sum(min(abs(wrap(o)) for o in c) <= 1.5 for c in cs)
        sh = [sum(min(abs(wrap(o - q)) for o in c) <= 1.5 for c, q in zip(cs, rng.permutation(pp))) for _ in range(1000)]
        P(f"  {ser:6s} {len(g):4d} {len(sr) - len(dated):9d} {hA:5d}/{len(g):<3d} {h0:6d}/{len(g):<3d} {np.mean(sh):9.1f}/{max(sh)}")
    P()
    P("Cutout check (cutouts.py; z = matched-filter significance at the Horizons position for each time;")
    P("'source' = brightest non-catalog source within 20\" of the track, expressed as a time along the track):")
    cf = HERE.parent / "results" / "time_test_cutouts.txt"
    L.extend(cf.read_text().splitlines() if cf.exists() else ["(not run)"])
    P()
    P("Link to the 1908 Pluto candidate: predicted shift (predA, DASCH time - true time) vs the measured along-track")
    P("offset of the candidate (results/candidate_1908.txt, steps 6-7). Pluto moves ~2.9\"/h, so +-2\" = +-0.7 h.")
    sel = {r["tag"]: r for r in csv.DictReader(open(HERE.parent / "lists" / "selected.csv"))}
    meas = {"ma00729_m0_s0": -6.30, "ma00731_m0_s0": -5.95, "ma00733_m0_s0": -5.43, "ma00937_m0_s0": -6.56}
    for t, m in meas.items():
        tD = Time(sel[t]["expdate"].rstrip("Z"), scale="utc")
        s = 6.0
        for _ in range(4):
            s = match.shift_A(tD - s * u.hour, match.LON["803"])
        P(f"  {t[:7]} DASCH {sel[t]['expdate'][:16]}: predA {s:+.2f} h; candidate offset {m:+.2f} h along track (plate time earlier)")
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
