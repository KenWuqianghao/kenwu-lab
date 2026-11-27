"""Run every pre-registered test of PROTOCOL.md on a built key set.

Usage: python -I analyze.py BUILD_DIR OUT_JSON [stage ...]
Stages: grid model strata placebo csn tests (default: all). Each stage caches its output in
OUT_JSON's directory as stage_<name>.json, so a stage can be rerun alone.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zipflib import D, depth_hists, estimator_E, model_hists, pooled, sort_lcp, subset_lcp, summarize

SEEDS = range(5)
M_CHAINS = 2_000_000
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.0f}s]", *a, flush=True)


def grid_of(n_full):
    g = [1e4, 10 ** 4.5, 1e5, 10 ** 5.5, 1e6, 1.4e6, 10 ** 6.5, 1e7, 10 ** 7.5]
    return [int(round(x)) for x in g if x < n_full] + [n_full]


def fast_hists(lcp_sel, L_sel):
    """depth_hists with bincount (same output, faster for large m)."""
    m = len(lcp_sel)
    out = {}
    for d in range(1, D + 1):
        starts = np.flatnonzero(lcp_sel < d)
        sizes = np.diff(np.append(starts, m))[L_sel[starts] >= d]
        bc = np.bincount(sizes)
        v = np.flatnonzero(bc)
        out[d] = (v, bc[v].astype(np.float64))
    return out


def hists_for(S, sel):
    return fast_hists(subset_lcp(S["lcp"], sel), S["L"][sel])


def pick(rng, pool, n):
    return np.sort(pool[rng.choice(len(pool), n, replace=False)]) if n < len(pool) else pool


def stage_grid(S, outdir):
    n_full = len(S["lcp"])
    res = []
    allidx = np.arange(n_full)
    for N in grid_of(n_full):
        for s in (SEEDS if N < n_full else [0]):
            sel = pick(np.random.default_rng(1000 * s + 7), allidx, N)
            h = hists_for(S, sel)
            r = summarize(h, N)
            r.update(N=N, seed=s)
            res.append(r)
            log("grid", N, s, r["alpha_pool"], r["b"], r["d_cr"])
            if (N == n_full) or (N == 1_400_000 and s == 0):
                np.savez(os.path.join(outdir, f"hists_N{N}.npz"),
                         **{f"v{d}": h[d][0] for d in h}, **{f"c{d}": h[d][1] for d in h})
    return res


def stage_model(S, outdir):
    res = []
    for i, N in enumerate(grid_of(len(S["lcp"]))):
        h = model_hists(N, M_CHAINS, seed=500 + i)
        r = summarize(h, N)
        r.update(N=N)
        res.append(r)
        log("model", N, r["alpha_pool"], r["b"], r["d_cr"])
    return res


def stage_strata(S, outdir):
    N = 1_000_000
    elo = S["elo"]
    rated = elo > 0
    q1, q2 = np.quantile(elo[rated], [1 / 3, 2 / 3])
    nm = len(S["months"])
    y2015 = [i for i, m in enumerate(S["months"].tolist()) if m.startswith("2015")]
    masks = {
        "bullet": S["speed"] == 0, "blitz": S["speed"] == 1, "classical": S["speed"] == 2,
        "rating_low": rated & (elo < q1), "rating_mid": rated & (elo >= q1) & (elo < q2), "rating_high": rated & (elo >= q2),
        "2013-2014": S["month"] < (min(y2015) if y2015 else nm), "2015": np.isin(S["month"], y2015),
    }
    res = {"rating_cuts": [float(q1), float(q2)]}
    for k, m in masks.items():
        pool = np.flatnonzero(m)
        if len(pool) < N:
            res[k] = {"skipped": f"only {len(pool)} games"}
            log("strata", k, "skipped", len(pool))
            continue
        rs = []
        for s in SEEDS:
            sel = pick(np.random.default_rng(2000 + s), pool, N)
            rs.append(summarize(hists_for(S, sel), N))
        res[k] = {"n_games": int(len(pool)), "runs": rs,
                  **{f: float(np.nanmean([r[f] for r in rs])) for f in ("alpha_pool", "b", "rho", "d_cr")}}
        log("strata", k, res[k]["alpha_pool"], res[k]["rho"], res[k]["d_cr"])
    return res


def stage_placebo(S, outdir, build_dir):
    N = 1_400_000
    pool = np.flatnonzero(S["L"] == D)
    cols = [np.load(os.path.join(build_dir, f"col_{c:02d}.npy"), mmap_mode="r") for c in range(D)]
    res = {"n_games_L40": int(len(pool)), "real": [], "shuffled": []}
    for s in SEEDS:
        rng = np.random.default_rng(3000 + s)
        games = np.sort(S["perm"][pick(rng, pool, N)])
        tok = np.stack([np.asarray(cols[c][games]) for c in range(D)], axis=1)
        L = np.full(N, D, np.uint8)
        for name in ("real", "shuffled"):
            if name == "shuffled":
                for c in range(D):
                    tok[:, c] = tok[rng.permutation(N), c]
            perm, lcp = sort_lcp(lambda c: tok[:, c], N)
            r = summarize(fast_hists(lcp, L), N)
            res[name].append(r)
            log("placebo", s, name, r["alpha_pool"], r["b"], r["d_cr"])
    for name in ("real", "shuffled"):
        res[name + "_mean"] = {f: float(np.nanmean([r[f] for r in res[name]])) for f in ("alpha_pool", "b", "rho", "d_cr")}
    return res


def stage_csn(S, outdir):
    import powerlaw
    from scipy.special import zeta
    z = np.load(os.path.join(outdir, "hists_N1400000.npz"))
    h = {d: (z[f"v{d}"], z[f"c{d}"]) for d in range(1, D + 1)}
    v, c = pooled(h)
    c = c.astype(np.int64)
    best = None
    for xmin in [1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 64, 80, 100, 130, 160, 200, 250, 320, 400, 500, 640, 800, 1000]:
        k = v >= xmin
        x, w = v[k].astype(float), c[k]
        ntail = w.sum()
        if ntail < 1000:
            break
        # discrete MLE by 1-d search
        grid = np.linspace(1.3, 3.5, 2201)
        sl = (w * np.log(x)).sum()
        ll = -ntail * np.log(zeta(grid, xmin)) - grid * sl
        a = grid[np.argmax(ll)]
        # KS distance on the tail CDF
        cdf_emp = np.cumsum(w) / ntail
        cdf_mod = 1 - zeta(a, x + 1) / zeta(a, xmin)
        ks = np.max(np.abs(cdf_emp - cdf_mod))
        if best is None or ks < best["ks"]:
            best = {"xmin": xmin, "alpha": float(a), "ks": float(ks), "n_tail": int(ntail)}
    log("csn", best)
    data = np.repeat(v[v >= best["xmin"]], c[v >= best["xmin"]]).astype(float)
    fit = powerlaw.Fit(data, xmin=best["xmin"], discrete=True, verbose=False)
    out = dict(best, powerlaw_alpha=float(fit.power_law.alpha))
    for alt in ("lognormal", "truncated_power_law"):
        R, p = fit.distribution_compare("power_law", alt, normalized_ratio=True)
        out[f"LR_vs_{alt}"] = {"R": float(R), "p": float(p)}
        log("csn", alt, R, p)
    return out


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    s, c = np.polyfit(x[ok], y[ok], 1)
    return float(s), float(c)


def stage_tests(outdir):
    grid = json.load(open(os.path.join(outdir, "stage_grid.json")))
    model = json.load(open(os.path.join(outdir, "stage_model.json")))
    Ns = sorted({r["N"] for r in grid})
    nf = max(Ns)
    mean = {N: {f: float(np.nanmean([r[f] for r in grid if r["N"] == N])) for f in ("alpha_pool", "b", "rho", "d_cr")} for N in Ns}
    mod = {r["N"]: r for r in model}
    lnN = np.log(Ns)
    gam = ols(np.log(lnN), np.log([mean[N]["b"] for N in Ns]))[0]
    gam_seed = []
    for s in SEEDS:
        bs = [next(r["b"] for r in grid if r["N"] == N and (r["seed"] == s or N == nf)) for N in Ns]
        gam_seed.append(ols(np.log(lnN), np.log(bs))[0])
    gam_m = ols(np.log(lnN), np.log([mod[N]["b"] for N in Ns]))[0]
    rho, rho_m = mean[nf]["rho"], mod[nf]["rho"]
    dg, dr = abs(gam - gam_m), abs(rho - rho_m) / rho_m
    t2 = "supported" if (dg <= 0.25 and dr <= 0.25) else ("refuted" if (dg > 0.5 or dr > 0.5) else "inconclusive")
    s_d, c_d = ols(lnN, [mean[N]["d_cr"] for N in Ns])
    s_m, c_m = ols(lnN, [mod[N]["d_cr"] for N in Ns])
    ddc = abs(mean[nf]["d_cr"] - mod[nf]["d_cr"])
    t3 = "supported" if (0.75 <= s_d <= 1.25 and ddc <= 2) else ("refuted" if (s_d < 0.5 or s_d > 1.5 or ddc > 4) else "inconclusive")
    ap = mean[nf]["alpha_pool"]
    t1 = "supported" if abs(ap - 2) <= 0.10 else "not supported"
    return {
        "N_full": nf, "grid_mean": {str(N): mean[N] for N in Ns},
        "model": {str(N): {k: mod[N][k] for k in ("alpha_pool", "b", "rho", "d_cr")} for N in Ns},
        "T1": {"alpha_pool_full": ap, "decision": t1,
               "alpha_pool_by_N": {str(N): mean[N]["alpha_pool"] for N in Ns}},
        "T2": {"gamma": gam, "gamma_by_seed": gam_seed, "gamma_sd": float(np.std(gam_seed, ddof=1)),
               "gamma_model": gam_m, "rho_full": rho, "rho_model_full": rho_m,
               "abs_gamma_diff": dg, "rel_rho_diff": dr, "decision": t2},
        "T3": {"slope": s_d, "intercept": c_d, "slope_model": s_m, "intercept_model": c_m,
               "d_cr_full": mean[nf]["d_cr"], "d_cr_model_full": mod[nf]["d_cr"],
               "pred_eq9_full": float(1 + np.log(nf)), "d_cr_at_1.4e6": mean.get(1_400_000, {}).get("d_cr"),
               "abs_diff": ddc, "decision": t3},
    }


def main(build_dir, out_json, stages):
    outdir = os.path.dirname(os.path.abspath(out_json))
    stages = stages or ["meta", "grid", "model", "strata", "placebo", "csn", "tests"]
    S = None
    for st in stages:
        if st != "tests" and S is None:
            S = dict(np.load(os.path.join(build_dir, "sorted.npz")))
            log("loaded", len(S["lcp"]), "games")
        if st == "meta":
            cnt = np.bincount(S["month"], minlength=len(S["months"]))
            r = {m: int(k) for m, k in zip(S["months"].tolist(), cnt)}
        elif st == "grid":
            r = stage_grid(S, outdir)
        elif st == "model":
            r = stage_model(S, outdir)
        elif st == "strata":
            r = stage_strata(S, outdir)
        elif st == "placebo":
            r = stage_placebo(S, outdir, build_dir)
        elif st == "csn":
            r = stage_csn(S, outdir)
        elif st == "tests":
            r = stage_tests(outdir)
        json.dump(r, open(os.path.join(outdir, f"stage_{st}.json"), "w"), indent=1)
    parts = {}
    for st in ["meta", "grid", "model", "strata", "placebo", "csn", "tests"]:
        p = os.path.join(outdir, f"stage_{st}.json")
        if os.path.exists(p):
            parts[st] = json.load(open(p))
    json.dump(parts, open(out_json, "w"), indent=1)
    log("done", stages)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
