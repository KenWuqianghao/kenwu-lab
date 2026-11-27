"""EXPLORATORY (not pre-registered): where does the data depart from the Eq. (3) model?

Usage: python -I explore.py BUILD_DIR OUT_JSON
E1. Branching ratios r = n_d / n_(d-1) along each game's chain (parents with n_(d-1) >= 100,
    each edge weighted by r as in the source's Fig. 3A). Mean of -ln r per depth (arcsine: ln 2).
E2. Chain surrogates at N = 1.4e6 and N = 10^6.5 (memory limit): per-depth shuffle of the empirical r across
    games (keeps each depth's r distribution, removes correlation along a chain), and a pooled
    shuffle (one r distribution for all depths). Chains rebuilt with n_d = max(1, round(n_(d-1) r)).
    The estimator E and summarize() are applied to the expected node counts.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zipflib import D, subset_lcp, summarize


def chains(lcp_sel, L_sel):
    """n_d(i) for every game i of the sorted subset, d = 0..D (0 if L_i < d)."""
    m = len(lcp_sel)
    out = np.zeros((D + 1, m), dtype=np.int32)
    out[0] = m
    for d in range(1, D + 1):
        starts = np.flatnonzero(lcp_sel < d)
        sizes = np.diff(np.append(starts, m))
        nd = np.repeat(sizes, sizes)
        nd[L_sel < d] = 0
        out[d] = nd
    return out


def hists_from_chains(n, N):
    out = {}
    for d in range(1, D + 1):
        x = n[d][n[d] > 0].astype(np.float64)
        v, c = np.unique(x, return_counts=True)
        out[d] = (v, c / v)
    return out


def q_stats(n):
    res = {}
    allr, allw = [], []
    for d in range(1, D + 1):
        p, ch = n[d - 1].astype(float), n[d].astype(float)
        k = (p >= 100) & (ch > 0)
        if k.sum() == 0:
            continue
        r = ch[k] / p[k]
        # Each game is one draw of the size-biased child; weight 1/p gives each parent total weight 1, i.e. edges weighted by r.
        w = 1.0 / p[k]
        mu = float(np.sum(w * -np.log(r)) / np.sum(w))
        res[d] = {"mu": mu, "frac_r_lt_0.01": float(np.sum(w * (r < 0.01)) / np.sum(w)), "n_parents_weight": float(np.sum(w))}
        allr.append(r); allw.append(w)
    r, w = np.concatenate(allr), np.concatenate(allw)
    hist, edges = np.histogram(r, bins=100, range=(0, 1), weights=w, density=True)
    return res, {"mu_pooled": float(np.sum(w * -np.log(r)) / np.sum(w)), "q_hist": hist.tolist(),
                 "arcsine_at_centres": (2 / (np.pi * np.sqrt(1 - ((edges[:-1] + edges[1:]) / 2) ** 2))).tolist()}


def surrogate(n, N, seed, pooled_r):
    rng = np.random.default_rng(seed)
    m = n.shape[1]
    keep = n[D] > 0  # games with L = 40 only, so every chain has all depths
    c = n[:, keep].astype(np.float64)
    r = c[1:] / c[:-1]
    if pooled_r:
        flatr = r.ravel()
        r = flatr[rng.integers(0, flatr.size, size=r.shape)]
    else:
        r = np.stack([row[rng.permutation(row.size)] for row in r])
    x = np.full(r.shape[1], float(N))
    out = {}
    w = N / r.shape[1]
    for d in range(1, D + 1):
        x = np.maximum(1.0, np.round(x * r[d - 1]))
        v, cnt = np.unique(x, return_counts=True)
        out[d] = (v, w * cnt / v)
    return out


def main(build_dir, out_json):
    S = dict(np.load(os.path.join(build_dir, "sorted.npz")))
    nf = len(S["lcp"])
    res = {}
    for N, tag in [(1_400_000, "N1.4e6"), (int(round(10 ** 6.5)), "N10^6.5")]:
        sel = np.arange(nf) if N >= nf else np.sort(np.random.default_rng(7).choice(nf, N, replace=False))
        n = chains(subset_lcp(S["lcp"], sel), S["L"][sel])
        qd, qp = q_stats(n)
        r = {"q_by_depth": qd, **qp}
        r["data_check"] = {k: v for k, v in summarize(hists_from_chains(n, N), N).items() if k != "alpha_d"}
        for name, pr in [("shuffle_within_depth", False), ("shuffle_pooled", True)]:
            s = summarize(surrogate(n, N, 11, pr), N)
            r[name] = s
            print(tag, name, s["alpha_pool"], s["b"], s["rho"], s["d_cr"], flush=True)
        res[tag] = r
        del n
    json.dump(res, open(out_json, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
