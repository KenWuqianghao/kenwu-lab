"""Exploratory analyses of PROTOCOL.md addendum 1. Usage: exploratory.py <cachedir> <out.json>
Needs the cache written by run_all.py (prcp.npz, elong.npy)."""
import datetime as dt
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
import lunar as L  # noqa: E402

cache, outp = sys.argv[1:3]
d = np.load(os.path.join(cache, "prcp.npz"))
P = d["P"]
E = np.load(os.path.join(cache, "elong.npy"))
fbin = np.minimum((E / 3.6).astype(np.int64), 99)
TONE = stats.t.isf(0.05, 8) ** 2 / (stats.t.isf(0.05, 8) ** 2 + 8)
TTWO = stats.t.isf(0.025, 8) ** 2 / (stats.t.isf(0.025, 8) ** 2 + 8)
TF = L.f_p  # protocol test
L.PERIODS["AB"] = (dt.date(1895, 1, 1), dt.date(2026, 10, 31), 3650)


def rates(Fz, Fn):
    r2s, _, _ = L.harm(L.to_class(Fz) / L.to_class(Fn))
    return {"F": float((TF(r2s) < 0.05).mean()), "t1": float((r2s > TONE).mean()), "t2": float((r2s > TTWO).mean())}


res = {"thr_t1": float(TONE), "thr_t2": float(TTWO),
       "beta_null_rate_t1": float(stats.beta.sf(TONE, 1, 3.5)),
       "beta_null_rate_t2": float(stats.beta.sf(TTWO, 1, 3.5)),
       "beta_null_rate_F": float(stats.beta.sf(0.5751093795080316, 1, 3.5))}
for name in ("A", "B"):
    per = L.Period(name, P, fbin)
    Fz, Fn = per.rotated_fine(np.zeros(per.ny, int))
    obs = rates(Fz, Fn)
    n = int(per.keep.sum())
    rng = np.random.default_rng(20261126)
    null = {k: [] for k in obs}
    for _ in range(2000):
        x = rates(*per.rotated_fine(rng.integers(0, 100, per.ny)))
        for k in x:
            null[k].append(x[k])
    r = {"n_stations": n}
    for k in obs:
        a = np.array(null[k])
        nsig = round(obs[k] * n)
        r[k] = {"S": obs[k], "n_sig": nsig, "yrr_p": float((1 + (a >= obs[k]).sum()) / 2001),
                "yrr_mean": float(a.mean()), "yrr_q95": float(np.quantile(a, 0.95))}
    r["F"]["binom_indep_p"] = float(stats.binom.sf(r["F"]["n_sig"] - 1, n, 0.05))
    res[name] = r
    print(name, json.dumps(r), flush=True)
    del per
per = L.Period("AB", P, fbin)
Fz, Fn = per.rotated_fine(np.zeros(per.ny, int))
obs = L.summarize(L.to_class(Fz), L.to_class(Fn))
rng = np.random.default_rng(20261127)
nul = [L.summarize(*map(L.to_class, per.rotated_fine(rng.integers(0, 100, per.ny)))) for _ in range(2000)]
nr2 = np.array([x["r2"] for x in nul])
nS = np.array([x["S"] for x in nul])
res["AB"] = {"n_stations": int(per.keep.sum()), "r2": obs["r2"], "phase_d": obs["phase_d"], "amp": obs["amp"],
             "yrr_p_r2": float((1 + (nr2 >= obs["r2"]).sum()) / 2001), "S": obs["S"], "n_sig": obs["n_sig"],
             "yrr_p_S": float((1 + (nS >= obs["S"]).sum()) / 2001), "yrr_mean_S": float(nS.mean()),
             "yrr_q95_S": float(np.quantile(nS, 0.95)),
             "share_station_days_A": float(per.v[:, :L.day_index(dt.date(2009, 1, 1)) - L.day_index(dt.date(1895, 1, 1))].sum() / per.v.sum())}
print("AB", json.dumps(res["AB"]))
json.dump(res, open(outp, "w"), indent=1)
