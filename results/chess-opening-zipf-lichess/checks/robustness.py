"""Verifier's robustness check (not pre-registered): do the T2 and T3 decisions depend on the fit range?

Usage: python -I robustness.py BUILD_DIR OUT.json
Uses the solver's sorted key set (checked by checks/test_counting.py and by checks/independent_count.py)
with new random subsets (seeds 9000+), and a separately written log-binned estimator with options:
  nmin   lowest weight n in the fit (protocol: 1)
  frac   highest weight in the fit is N*frac (protocol: 0.01)
The slope b of alpha_d on d is fitted on the protocol window d = 3..floor(ln N), on the fixed window
d = 3..9 (available at every N), and on d = 8..floor(ln N) (N >= 1e5.5 only).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from zipflib import D, subset_lcp, model_hists

def hists(lcp, L):
    m = len(lcp); out = {}
    for d in range(1, D + 1):
        st = np.flatnonzero(lcp < d)
        sz = np.diff(np.append(st, m))[L[st] >= d]
        bc = np.bincount(sz); v = np.flatnonzero(bc)
        out[d] = (v.astype(float), bc[v].astype(float))
    return out

def alpha(v, c, N, nmin, frac):
    edges = np.unique(np.floor(2 ** (np.arange(0, 60) / 2)))
    k = np.digitize(v, edges) - 1
    cnt = np.zeros(len(edges) - 1)
    np.add.at(cnt, k, c)
    lo, hi = edges[:-1], edges[1:]
    ok = (lo >= nmin) & (hi - 1 <= N * frac) & (cnt >= 5)
    if ok.sum() < 4:
        return np.nan
    x = np.log10(np.sqrt(lo[ok] * (hi[ok] - 1))); y = np.log10(cnt[ok] / (hi[ok] - lo[ok]))
    A = np.vstack([x, np.ones_like(x)]).T
    return -np.linalg.lstsq(A, y, rcond=None)[0][0]

def slope(ad, d0, d1):
    ds = np.arange(d0, d1 + 1); y = ad[ds - 1]; ok = np.isfinite(y)
    if ok.sum() < 3: return np.nan
    return float(np.polyfit(ds[ok], y[ok], 1)[0])

def dcr(ad):
    for d in range(2, D + 1):
        if np.isfinite(ad[d - 1]) and ad[d - 1] >= 2:
            a0 = ad[d - 2]
            return (d - 1) + (2 - a0) / (ad[d - 1] - a0) if np.isfinite(a0) and a0 < 2 else float(d)
    return np.nan

def summ(h, N, nmin, frac):
    ad = np.array([alpha(*h[d], N, nmin, frac) if len(h[d][0]) else np.nan for d in range(1, D + 1)])
    pv = np.concatenate([h[d][0] for d in h]); pc = np.concatenate([h[d][1] for d in h])
    fl = int(np.floor(np.log(N)))
    return {"alpha_pool": float(alpha(pv, pc, N, nmin, frac)), "b_protocol": slope(ad, 3, fl), "b_3_9": slope(ad, 3, 9),
            "b_8_up": slope(ad, 8, fl) if fl >= 12 else float("nan"), "d_cr": float(dcr(ad)), "alpha_d": ad.tolist()}

def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); ok = np.isfinite(x) & np.isfinite(y) & (y > -1e300)
    return float(np.polyfit(x[ok], y[ok], 1)[0])

def main(bdir, out):
    S = np.load(os.path.join(bdir, "sorted.npz")); lcp = S["lcp"]; L = S["L"]; nf = len(lcp)
    grid = [int(round(x)) for x in (1e4, 10 ** 4.5, 1e5, 10 ** 5.5, 1e6, 1.4e6, 10 ** 6.5, 1e7, 10 ** 7.5) if x < nf] + [nf]
    variants = {"protocol_n1_N100": (1, 0.01), "n2_N100": (2, 0.01), "n4_N100": (4, 0.01), "n1_N1000": (1, 0.001), "n2_N10": (2, 0.1)}
    H = {}; Hm = {}
    for i, N in enumerate(grid):
        reps = [0] if N == nf else [0, 1, 2]
        H[N] = []
        for s in reps:
            sel = np.arange(nf) if N == nf else np.sort(np.random.default_rng(9000 + s).choice(nf, N, replace=False))
            H[N].append(hists(subset_lcp(lcp, sel), L[sel]))
        Hm[N] = model_hists(N, 2_000_000, seed=7700 + i)
        print("hists", N, flush=True)
    res = {"grid": grid, "variants": {}}
    lnN = np.log(grid)
    for name, (nmin, frac) in variants.items():
        dat = {N: [summ(h, N, nmin, frac) for h in H[N]] for N in grid}
        mod = {N: summ(Hm[N], N, nmin, frac) for N in grid}
        mean = {N: {f: float(np.nanmean([r[f] for r in dat[N]])) for f in ("alpha_pool", "b_protocol", "b_3_9", "b_8_up", "d_cr")} for N in grid}
        r = {"data": {str(N): mean[N] for N in grid}, "model": {str(N): {f: mod[N][f] for f in mean[N]} for N in grid},
             "alpha_d_full": dat[nf][0]["alpha_d"], "alpha_d_model_full": mod[nf]["alpha_d"]}
        for key in ("b_protocol", "b_3_9", "b_8_up"):
            bd = [mean[N][key] for N in grid]; bm = [mod[N][key] for N in grid]
            r["gamma_" + key] = ols(np.log(lnN), np.log(bd)); r["gamma_model_" + key] = ols(np.log(lnN), np.log(bm))
            r["rho_full_" + key] = mean[nf][key] * lnN[-1]; r["rho_model_full_" + key] = mod[nf][key] * lnN[-1]
        r["dcr_slope"] = ols(lnN, [mean[N]["d_cr"] for N in grid]); r["dcr_slope_model"] = ols(lnN, [mod[N]["d_cr"] for N in grid])
        r["dcr_full"] = mean[nf]["d_cr"]; r["dcr_model_full"] = mod[nf]["d_cr"]
        dg = abs(r["gamma_b_protocol"] - r["gamma_model_b_protocol"]); dr = abs(r["rho_full_b_protocol"] / r["rho_model_full_b_protocol"] - 1)
        r["T2"] = "supported" if (dg <= 0.25 and dr <= 0.25) else ("refuted" if (dg > 0.5 or dr > 0.5) else "inconclusive")
        s = r["dcr_slope"]; dd = abs(r["dcr_full"] - r["dcr_model_full"])
        r["T3"] = "supported" if (0.75 <= s <= 1.25 and dd <= 2) else ("refuted" if (s < 0.5 or s > 1.5 or dd > 4) else "inconclusive")
        r["T1_alpha_pool_full"] = mean[nf]["alpha_pool"]
        res["variants"][name] = r
        print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if not isinstance(v, (dict, list))}, flush=True)
    json.dump(res, open(out, "w"), indent=1)

main(sys.argv[1], sys.argv[2])
