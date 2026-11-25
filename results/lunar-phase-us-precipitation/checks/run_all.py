"""Compute every number of the study. Usage: run_all.py <rawdir> <cachedir> <out.json> [--fast]"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__file__))
import lunar as L  # noqa: E402

raw, cache, outp = sys.argv[1:4]
FAST = "--fast" in sys.argv
NNULL = 200 if FAST else 2000
NINJ = 40 if FAST else 200
CS = [0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10]
t0 = time.time()
import os  # noqa: E402
os.makedirs(cache, exist_ok=True)
pc = os.path.join(cache, "prcp.npz")
if os.path.exists(pc):
    d = np.load(pc, allow_pickle=False)
    ids, P = list(d["ids"]), d["P"]
else:
    ids, P, _ = L.parse_archive(os.path.join(raw, "ghcnd_hcn.tar.gz"), os.path.join(raw, "ghcnd-stations.txt"))
    np.savez(pc, ids=np.array(ids), P=P)
print(f"parsed {len(ids)} stations in {time.time()-t0:.0f}s", flush=True)
ec = os.path.join(cache, "elong.npy")
if os.path.exists(ec):
    E = np.load(ec)
else:
    E = L.elongation_deg(os.path.join(raw, "de440s.bsp"))
    np.save(ec, E)
fbin = np.minimum((E / 3.6).astype(np.int64), 99)
print(f"ephemeris done {time.time()-t0:.0f}s", flush=True)

res = {"n_archive_stations": len(ids), "fast": FAST}
for name in ("A", "B"):
    per = L.Period(name, P, fbin)
    r = {"n_stations": int(per.keep.sum()), "n_years": int(per.ny),
         "n_station_days": int(per.v.sum())}
    Fz, Fn = per.rotated_fine(np.zeros(per.ny, int))
    obs = L.summarize(L.to_class(Fz), L.to_class(Fn))
    r["observed"] = obs
    # YRR null
    rng = np.random.default_rng(20261124)
    nr2, nS, nph = [], [], []
    for i in range(NNULL):
        u = rng.integers(0, 100, per.ny)
        Fz, Fn = per.rotated_fine(u)
        s = L.summarize(L.to_class(Fz), L.to_class(Fn))
        nr2.append(s["r2"]); nS.append(s["S"]); nph.append(s["phase_ok"])
    nr2, nS = np.array(nr2), np.array(nS)
    q_r2, q_S = float(np.quantile(nr2, 0.95)), float(np.quantile(nS, 0.95))
    r["null"] = {"n": NNULL, "r2_q95": q_r2, "S_q95": q_S, "S_mean": float(nS.mean()),
                 "S_median": float(np.median(nS)), "r2_mean": float(nr2.mean()),
                 "p_r2": float((1 + (nr2 >= obs["r2"]).sum()) / (1 + NNULL)),
                 "p_S": float((1 + (nS >= obs["S"]).sum()) / (1 + NNULL)),
                 "S_hist": np.histogram(nS, bins=20, range=(0, 0.5))[0].tolist()}
    print(f"{name}: obs r2={obs['r2']:.4f} S={obs['S']:.4f} null done {time.time()-t0:.0f}s", flush=True)
    # injections
    rng = np.random.default_rng(20261125)
    inj = {c: {"r2": [], "S": [], "amp": [], "hit_nat": 0, "hit_S": 0} for c in CS}
    for i in range(NINJ):
        u = rng.integers(0, 100, per.ny)
        Fz, Fn, Fp = per.rotated_fine(u, with_p=True)
        Cn = L.to_class(Fn)
        for c in CS:
            s = L.summarize(L.to_class(L.inject(Fz, Fp, c)), Cn)
            d = inj[c]
            d["r2"].append(s["r2"]); d["S"].append(s["S"]); d["amp"].append(s["amp"])
            d["hit_nat"] += int(s["r2"] > q_r2 and s["phase_ok"])
            d["hit_S"] += int(s["S"] > q_S)
    r["injection"] = [{"c": c, "n": NINJ, "power_nat": inj[c]["hit_nat"] / NINJ,
                       "power_S": inj[c]["hit_S"] / NINJ,
                       "amp_mean": float(np.mean(inj[c]["amp"])), "r2_mean": float(np.mean(inj[c]["r2"])),
                       "S_mean": float(np.mean(inj[c]["S"]))} for c in CS]
    print(f"{name}: injection done {time.time()-t0:.0f}s", flush=True)
    # placebo periods and scan
    def stat_for(bins):
        C, N = per.classes_from_bins(bins)
        s = L.summarize(C, N)
        return {"r2": s["r2"], "S": s["S"], "phase_d": s["phase_d"]}
    r["placebo"] = {str(p): stat_for(L.pseudo_bins(p)) for p in (27.3, 28.5, 30.5, 31.0, L.SYN)}
    scan = np.round(np.arange(25.0, 35.0001, 0.05), 2)
    sc = [dict(P=float(p), **stat_for(L.pseudo_bins(p))) for p in scan]
    far = [x for x in sc if abs(x["P"] - 29.53) > 1]
    q95r = float(np.quantile([x["r2"] for x in far], 0.95))
    q95S = float(np.quantile([x["S"] for x in far], 0.95))
    r["scan"] = {"values": sc, "far_r2_q95": q95r, "far_S_q95": q95S,
                 "synodic_r2_distinct": bool(obs["r2"] > q95r), "synodic_S_distinct": bool(obs["S"] > q95S),
                 "rank_r2_among_far": int(sum(x["r2"] >= obs["r2"] for x in far)),
                 "rank_S_among_far": int(sum(x["S"] >= obs["S"] for x in far)), "n_far": len(far),
                 "n_scan": len(sc), "far_S_max": max(x["S"] for x in far),
                 "far_S_max_P": max(far, key=lambda x: x["S"])["P"]}
    res[name] = r
    print(f"{name}: placebo done {time.time()-t0:.0f}s", flush=True)
    del per

B, A = res["B"], res["A"]
H1 = B["null"]["p_r2"] < 0.05 and B["observed"]["phase_ok"]
H2 = B["null"]["p_S"] < 0.05
# power at the period-A amplitude: interpolate c from mean injected amplitude in B, read power
injB, injA = B["injection"], A["injection"]
# map the period-A observed amplitude to an equivalent c with the period-A injection curve
cA = float(np.interp(A["observed"]["amp"], [x["amp_mean"] for x in injA], [x["c"] for x in injA]))
powA_nat = float(np.interp(cA, [x["c"] for x in injB], [x["power_nat"] for x in injB]))
powA_S = float(np.interp(cA, [x["c"] for x in injB], [x["power_S"] for x in injB]))
res["decision"] = {"H1": bool(H1), "H2": bool(H2),
                   "verdict": "supported" if H1 and H2 else ("fails to replicate" if not (H1 or H2) else "mixed"),
                   "c_equiv_of_A_amp": cA, "power_B_nat_at_A_amp": powA_nat, "power_B_S_at_A_amp": powA_S}
res["runtime_s"] = round(time.time() - t0)
json.dump(res, open(outp, "w"), indent=1)
print(json.dumps(res["decision"]), flush=True)
