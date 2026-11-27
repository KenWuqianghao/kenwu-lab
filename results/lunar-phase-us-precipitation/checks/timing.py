"""Exploratory E5 of PROTOCOL.md addendum 3: sensitivity to the hour of the lunar phase.

Usage: timing.py <rawdir> <cachedir> <out.json>
Needs the cache written by run_all.py (prcp.npz) and de440s.bsp in <rawdir>.
"""
import datetime as dt
import json
import os
import sys

import numpy as np
from scipy import sparse, stats

sys.path.insert(0, os.path.dirname(__file__))
import lunar as L  # noqa: E402

raw, cache, outp = sys.argv[1:4]
P = np.load(os.path.join(cache, "prcp.npz"))["P"]
TIMINGS = {"12UTC_d": (12, 0), "00UTC_d": (0, 0), "18UTC_d": (18, 0),
           "12UTC_d-1": (12, -1), "12UTC_d+1": (12, 1)}
FBIN = {}
for k, (h, s) in TIMINGS.items():
    cp = os.path.join(cache, f"elong_{k}.npy")
    if not os.path.exists(cp):
        np.save(cp, L.elongation_deg(os.path.join(raw, "de440s.bsp"), hour=h, day_shift=s))
    FBIN[k] = np.minimum((np.load(cp) / 3.6).astype(np.int64), 99)
    print("elongation", k, flush=True)
assert np.array_equal(FBIN["12UTC_d"], np.minimum((np.load(os.path.join(cache, "elong.npy")) / 3.6).astype(np.int64), 99))
TTWO = stats.t.isf(0.025, 8) ** 2 / (stats.t.isf(0.025, 8) ** 2 + 8)
L.PERIODS["AB"] = (dt.date(1895, 1, 1), dt.date(2026, 10, 31), 3650)
NREP, SEED = 2000, 20261125
STATS = ("r2", "n_sig_F", "n_sig_t2")


def hist(per, fbin):
    """(S, ny, 100) fine-bin totals of z and of valid counts for one fine-bin series."""
    f = fbin[per.i0:per.i1]
    key = per.yidx * 100 + f
    oh = sparse.csr_matrix((np.ones(len(key)), (np.arange(len(key)), key)), shape=(len(key), per.ny * 100))
    S = per.z.shape[0]
    return (np.asarray((oh.T @ per.z.T).T).reshape(S, per.ny, 100),
            np.asarray((oh.T @ per.v.T).T).reshape(S, per.ny, 100))


def stat(Fz, Fn):
    C, N = L.to_class(Fz), L.to_class(Fn)
    r2, _, _ = L.harm(C.sum(0) / N.sum(0))
    r2s, _, _ = L.harm(C / N)
    return np.array([r2, (L.f_p(r2s) < 0.05).sum(), (r2s > TTWO).sum()], float)


res = {"seed": SEED, "n_rep": NREP, "timings": {k: list(v) for k, v in TIMINGS.items()}}
for name in ("A", "B", "AB"):
    per = L.Period(name, P, FBIN["12UTC_d"])
    H = {}
    for k in TIMINGS:
        per.Hz, per.Hn = hist(per, FBIN[k])
        H[k] = (per.Hz, per.Hn)
    del per.pz, per.Hp
    obs = {}
    for k in TIMINGS:
        per.Hz, per.Hn = H[k]
        obs[k] = stat(*per.rotated_fine(np.zeros(per.ny, int)))
    rng = np.random.default_rng(SEED)
    null = {k: np.empty((NREP, len(STATS))) for k in TIMINGS}
    for r in range(NREP):
        u = rng.integers(0, 100, per.ny)
        for k in TIMINGS:
            per.Hz, per.Hn = H[k]
            null[k][r] = stat(*per.rotated_fine(u))
    out = {"n_stations": int(per.keep.sum())}
    pobs = np.empty((len(TIMINGS), len(STATS)))
    prep = np.empty((len(TIMINGS), NREP, len(STATS)))
    for i, k in enumerate(TIMINGS):
        nk = null[k]
        pobs[i] = (1 + (nk >= obs[k][None, :]).sum(0)) / (NREP + 1)
        # p of each replicate within its own timing's null: share of replicates >= it
        prep[i] = (nk[None, :, :] >= nk[:, None, :]).sum(1) / NREP
        out[k] = {s: (float(obs[k][j]) if s == "r2" else int(obs[k][j])) for j, s in enumerate(STATS)}
        out[k].update({f"yrr_p_{s}": float(pobs[i, j]) for j, s in enumerate(STATS)})
    minobs, minrep = pobs.min(0), prep.min(0)
    out["adjusted"] = {f"yrr_p_{s}": float((1 + (minrep[:, j] <= minobs[j]).sum()) / (NREP + 1))
                       for j, s in enumerate(STATS)}
    res[name] = out
    print(name, json.dumps(out), flush=True)
    del per, H
json.dump(res, open(outp, "w"), indent=1)
