"""Per-object forward test (PROTOCOL.md).

Usage: python checks/analysis.py <part> <nparts> [--blind]
Writes work/results/<id>.json for each object in this part.
--blind: do not score the real test window (for timing and debugging only).
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qpo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LCDIR = os.path.join(ROOT, "work", "lc")
OUT = os.path.join(ROOT, "work", "results")

CHUNK = 20000
MAX_MOCKS = 300000
TARGET_ACC = 1000
MIN_ACC = 200
N_ALT = 2000
SPL_BETA = 3.0


def accept(g, P_obs, xi_obs):
    return (g["xi"] >= min(xi_obs, qpo.XI_CUT)) & (np.abs(g["P"] / P_obs - 1) < 0.2)


def null_k(kind, ttr, ytr, etr, tte, ete, P_obs, xi_obs, freqs, rng, drw=None):
    """k distribution of red-noise mocks that look at least as periodic as the object (conditioned null)."""
    t_all = np.concatenate([ttr, tte])
    e_all = np.concatenate([etr, ete])
    ntr = len(ttr)
    sig_target = np.sqrt(max(np.var(ytr) - np.mean(etr ** 2), 1e-6))
    k_acc, k_unc = [], []
    n = 0
    while n < MAX_MOCKS:
        if kind == "drw":
            x = qpo.sim_drw(t_all, drw[0], drw[1], CHUNK, rng)
        else:
            x = qpo.sim_spl(t_all, SPL_BETA, CHUNK, rng)
            x = x / x[:, :ntr].std(1, keepdims=True) * sig_target
        Y = x + rng.normal(size=x.shape) * e_all[None, :] + ytr.mean()
        g = qpo.gls_batch(ttr, Y[:, :ntr], freqs)
        k = qpo.score_k(tte, Y[:, ntr:], g["P"], g["coef"])
        a = accept(g, P_obs, xi_obs)
        k_acc.append(k[a])
        if n == 0:
            k_unc = k
        n += CHUNK
        if sum(len(v) for v in k_acc) >= TARGET_ACC:
            break
    k_acc = np.concatenate(k_acc)
    return dict(k_acc=k_acc, k_unc=k_unc, n_mocks=n, n_acc=len(k_acc))


def pval(k_obs, ks):
    return float((1 + np.sum(ks >= k_obs)) / (1 + len(ks)))


def analyze(lc, seed, blind=False, power=False):
    ttr, ytr, etr = lc["train"]
    tte, yte, ete = lc["test"]
    res = dict(n_train_bins=int(len(ttr)), n_test_bins=int(len(tte)))
    if len(ttr) < qpo.MIN_TRAIN_BINS or len(tte) < qpo.MIN_TEST_BINS:
        res["status"] = "too_few_bins"
        return res
    etr = np.maximum(etr, 1e-3)
    ete = np.maximum(ete, 1e-3)
    rng = np.random.default_rng(seed)
    freqs = qpo.freq_grid(ttr)
    g = qpo.gls_batch(ttr, ytr[None, :], freqs)
    P, coef, xi = float(g["P"][0]), g["coef"][0], float(g["xi"][0])
    res.update(status="ok", P=P, amp=float(np.hypot(coef[1], coef[2])), xi=xi, ncyc=float(g["ncyc"][0]),
               power=float(g["power"][0]), T_train=float(ttr.max() - ttr.min()), T_test=float(tte.max() - tte.min()),
               t_test_end=float(tte.max()), coef=[float(c) for c in coef])
    sd, tau = qpo.fit_drw(ttr, ytr, etr)
    res.update(drw_sigma=sd, drw_tau=tau)
    nd = null_k("drw", ttr, ytr, etr, tte, ete, P, xi, freqs, rng, drw=(sd, tau))
    ns = null_k("spl", ttr, ytr, etr, tte, ete, P, xi, freqs, rng)
    for name, nn in (("drw", nd), ("spl", ns)):
        use = nn["k_acc"] if nn["n_acc"] >= MIN_ACC else nn["k_unc"]
        res[name] = dict(n_mocks=nn["n_mocks"], n_acc=nn["n_acc"], conditioned=bool(nn["n_acc"] >= MIN_ACC),
                         k95=float(np.quantile(use, 0.95)), k50=float(np.median(use)),
                         k_unc95=float(np.quantile(nn["k_unc"], 0.95)))
        res[name]["_use"] = use
        res[name]["_unc"] = nn["k_unc"]
    if power:
        # alternative: the fitted sinusoid is real; DRW fitted to the training residuals
        resid = ytr - qpo.template(ttr, np.array([P]), coef[None, :])[0]
        sd2, tau2 = qpo.fit_drw(ttr, resid, etr)
        t_all = np.concatenate([ttr, tte])
        e_all = np.concatenate([etr, ete])
        x = qpo.sim_drw(t_all, sd2, tau2, N_ALT, rng)
        Y = x + qpo.template(t_all, np.array([P]), coef[None, :]) + rng.normal(size=x.shape) * e_all + ytr.mean()
        ga = qpo.gls_batch(ttr, Y[:, :len(ttr)], freqs)
        ka = qpo.score_k(tte, Y[:, len(ttr):], ga["P"], ga["coef"])
        res["alt"] = dict(drw_sigma=sd2, drw_tau=tau2, k50=float(np.median(ka)),
                          power_drw=float(np.mean(ka >= res["drw"]["k95"])),
                          power_spl=float(np.mean(ka >= res["spl"]["k95"])))
    if not blind:
        k_obs = float(qpo.score_k(tte, yte[None, :], np.array([P]), coef[None, :])[0])
        dphi, aratio = qpo.phase_shift(tte, yte, P, coef)
        res.update(k=k_obs, dphi=float(dphi), amp_ratio=float(aratio),
                   p_drw=pval(k_obs, res["drw"]["_use"]), p_spl=pval(k_obs, res["spl"]["_use"]),
                   p_drw_unc=pval(k_obs, res["drw"]["_unc"]), p_spl_unc=pval(k_obs, res["spl"]["_unc"]))
    for name in ("drw", "spl"):
        res[name].pop("_use")
        res[name].pop("_unc")
    return res


def inject(df_raw, P, coef):
    d = df_raw.copy()
    d["mag"] = d["mag"] + qpo.template(d.mjd.values, np.array([P]), np.asarray(coef)[None, :])[0]
    return d


def prepare_df(raw):
    tr, te = qpo.split(raw)
    tr, te = qpo.clip_poly15(tr), qpo.clip_poly15(te)
    return dict(train=qpo.bin20(tr), test=qpo.bin20(te))


def jobs():
    cand = pd.read_csv(os.path.join(ROOT, "data", "candidates.csv"))
    plac = pd.read_csv(os.path.join(ROOT, "data", "placebo.csv"))
    out = [("cand", r.id, None) for r in cand.itertuples()]
    out += [("plac", r.id, None) for r in plac.itertuples()]
    # injection: each candidate's fitted sinusoid into the raw curve of its first matched placebo
    first = plac.groupby("match").first().reset_index()
    out += [("inj", "I" + r.match[1:], (r.id, r.match)) for r in first.itertuples()]
    return out


def candidate_stale(cid):
    """True if the candidate's cached result is no_lightcurve but its light curve now exists."""
    cf = os.path.join(OUT, cid + ".json")
    return (os.path.exists(cf) and os.path.exists(os.path.join(LCDIR, cid + ".csv"))
            and json.load(open(cf)).get("status") == "no_lightcurve")


def run_one(kind, oid, extra, blind):
    f = os.path.join(OUT, oid + ".json")
    if kind == "inj" and candidate_stale(extra[1]):
        return "waiting"  # another worker will rerun the candidate first
    if os.path.exists(f):
        status = json.load(open(f)).get("status")
        if kind in ("cand", "plac"):
            stale = status == "no_lightcurve" and os.path.exists(os.path.join(LCDIR, oid + ".csv"))
        else:
            cf = os.path.join(OUT, extra[1] + ".json")
            stale = status == "candidate_not_ok" and os.path.exists(cf) and json.load(open(cf)).get("status") == "ok"
        if not stale:
            return "cached"
    seed = int.from_bytes(oid.encode(), "little") % (2 ** 32)
    t0 = time.time()
    if kind in ("cand", "plac"):
        path = os.path.join(LCDIR, oid + ".csv")
        if not os.path.exists(path):
            res = dict(status="no_lightcurve")
        else:
            res = analyze(prepare_df(qpo.load_raw(path)), seed, blind=blind, power=(kind == "cand"))
    else:
        pid, cid = extra
        cf = os.path.join(OUT, cid + ".json")
        path = os.path.join(LCDIR, pid + ".csv")
        if not os.path.exists(cf) or not os.path.exists(path):
            return "waiting"
        c = json.load(open(cf))
        if c.get("status") != "ok":
            res = dict(status="candidate_not_ok")
        else:
            res = analyze(prepare_df(inject(qpo.load_raw(path), c["P"], c["coef"])), seed, blind=blind)
            res.update(injected_P=c["P"], injected_amp=c["amp"], host=pid)
    res.update(id=oid, kind=kind, runtime_s=round(time.time() - t0, 1))
    if not blind:
        with open(f + ".tmp", "w") as fh:
            json.dump(res, fh, indent=1)
        os.replace(f + ".tmp", f)
    return res


if __name__ == "__main__":
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    blind = "--blind" in sys.argv
    only = [a for a in sys.argv[3:] if not a.startswith("--")]
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if blind:
        # Blind mode writes no result files, so an injection cannot read its candidate's fit.
        js = [j for j in js if j[0] != "inj"]
    if only:
        js = [j for j in js if j[1] in only]
    js = js[part::nparts]
    pending = []
    for j in js:
        r = run_one(*j, blind)
        if r == "waiting":
            pending.append(j)
        print(j[1], r if isinstance(r, str) else {k: r.get(k) for k in ("status", "P", "xi", "k", "p_drw", "runtime_s")},
              flush=True)
    stuck = []
    for j in pending:  # injections whose candidate was handled by another part
        for _ in range(360):
            r = run_one(*j, blind)
            if r != "waiting":
                break
            time.sleep(10)
        print(j[1], r if isinstance(r, str) else {k: r.get(k) for k in ("status", "k", "p_drw", "runtime_s")}, flush=True)
        if r == "waiting":
            stuck.append(j[1])
    if stuck:
        sys.exit(f"injections still waiting for their candidate after 1 h: {stuck}")
