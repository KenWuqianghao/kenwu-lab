"""Tests of PROTOCOL.md Sections 8-9 from work/results/*.json. Writes data/results_table.csv and data/summary.json."""
import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMED = {"SDSS J083111.23+123107.8": "J083111", "SDSS J155304.40+240255.1": "J155304",
         "SDSS J135830.46-012255.7": "J135830"}
PUBLISHED_P = {"SDSS J002500.42-031238.5": 788.8, "SDSS J002504.53+213224.6": 736.2,
               "SDSS J003858.53+020132.8": 736.2, "SDSS J004039.79+150321.2": 626.6,
               "SDSS J004744.03+190338.5": 688.6}


def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "work", "results", "*.json"))):
        r = json.load(open(f))
        flat = {k: v for k, v in r.items() if not isinstance(v, (dict, list))}
        for sub in ("drw", "spl", "alt"):
            for k, v in (r.get(sub) or {}).items():
                flat[f"{sub}_{k}"] = v
        rows.append(flat)
    return pd.DataFrame(rows)


def binom_upper(n_obs, powers, alpha=0.05):
    """Smallest f with P(X <= n_obs) <= 0.05, X ~ Binomial(n, mean_i[f power_i + (1-f) alpha])."""
    n = len(powers)
    for f in np.linspace(0, 1, 1001):
        p = np.mean(f * powers + (1 - f) * alpha)
        if stats.binom.cdf(n_obs, n, p) <= 0.05:
            return float(f)
    return 1.0


def block(df, col):
    c = df[(df.kind == "cand") & (df.status == "ok")]
    p = df[(df.kind == "plac") & (df.status == "ok")]
    nC, NC = len(c), int((c[col] < 0.05).sum())
    nP, NP = len(p), int((p[col] < 0.05).sum())
    t1 = float(stats.binomtest(NC, nC, 0.05, alternative="greater").pvalue)
    t2 = float(stats.fisher_exact([[NC, nC - NC], [NP, nP - NP]], alternative="greater")[1])
    z = lambda s: float(stats.norm.isf(np.clip(s, 1e-12, 1 - 1e-12)).sum() / np.sqrt(len(s)))
    return dict(n_cand=nC, N_cand_sig=NC, frac_cand=NC / nC, n_plac=nP, N_plac_sig=NP, frac_plac=NP / nP,
                T1_binom_p=t1, T2_fisher_p=t2, stouffer_cand=z(c[col]), stouffer_plac=z(p[col]))


def main():
    df = load()
    cand = pd.read_csv(os.path.join(ROOT, "data", "candidates.csv"))
    plac = pd.read_csv(os.path.join(ROOT, "data", "placebo.csv"))
    names = dict(zip(cand.id, cand.name))
    names.update(dict(zip(plac.id, plac.sdss_name)))
    df["name"] = df.id.map(names)
    out = {}
    out["status_counts"] = {k: df[df.kind == k].status.value_counts().to_dict() for k in ("cand", "plac", "inj")}
    out["primary_drw"] = block(df, "p_drw")
    out["secondary_spl"] = block(df, "p_spl")
    out["secondary_drw_unconditioned"] = block(df, "p_drw_unc")
    c = df[(df.kind == "cand") & (df.status == "ok")]
    p = df[(df.kind == "plac") & (df.status == "ok")]
    inj = df[(df.kind == "inj") & (df.status == "ok")]
    T1, T2 = out["primary_drw"]["T1_binom_p"], out["primary_drw"]["T2_fisher_p"]
    out["decision"] = ("Supported" if (T1 < 0.01 and T2 < 0.01) else
                       "Not supported" if T1 >= 0.01 else "Inconclusive")
    out["n_cand_unconditioned_null_drw"] = int((~c.drw_conditioned.astype(bool)).sum())
    out["n_cand_unconditioned_null_spl"] = int((~c.spl_conditioned.astype(bool)).sum())
    out["power"] = dict(mean_power_drw=float(c.alt_power_drw.mean()), median_power_drw=float(c.alt_power_drw.median()),
                        mean_power_spl=float(c.alt_power_spl.mean()),
                        expected_N_if_all_periodic_drw=float(c.alt_power_drw.sum()),
                        f95_upper_drw=binom_upper(out["primary_drw"]["N_cand_sig"], c.alt_power_drw.values),
                        f95_upper_spl=binom_upper(out["secondary_spl"]["N_cand_sig"], c.alt_power_spl.values))
    # POST HOC (not in PROTOCOL.md): upper limit on f with the empirical injection recovery rate as the power,
    # and with the placebo false-positive rate as the chance rate.
    rec = float((inj.p_drw < 0.05).mean())
    fp = out["primary_drw"]["frac_plac"]
    NCs = out["primary_drw"]["N_cand_sig"]
    out["post_hoc"] = dict(
        f95_upper_injection_power=binom_upper(NCs, np.full(len(c), rec)),
        f95_upper_injection_power_placebo_alpha=binom_upper(NCs, np.full(len(c), rec), alpha=fp),
        min_p_drw_cand=float(c.p_drw.min()), bonferroni_threshold=0.05 / len(c),
        n_cand_p_drw_below_bonferroni=int((c.p_drw < 0.05 / len(c)).sum()),
        median_amp_cand=float(c.amp.median()), median_amp_inj_host_drw_sigma=float(inj.drw_sigma.median()),
        median_alt_drw_sigma_cand=float(c.alt_drw_sigma.median()), median_drw_sigma_cand=float(c.drw_sigma.median()))
    out["injection"] = dict(n=len(inj), N_sig_drw=int((inj.p_drw < 0.05).sum()),
                            frac_sig_drw=float((inj.p_drw < 0.05).mean()), median_k=float(inj.k.median()),
                            N_sig_spl=int((inj.p_spl < 0.05).sum()))
    psel = p[(p.xi > 4) & (p.ncyc > 1.5)]
    out["k_distribution"] = dict(
        median_k_cand=float(c.k.median()), mean_k_cand=float(c.k.mean()), median_k_plac=float(p.k.median()),
        median_k_inj=float(inj.k.median()), mw_cand_vs_plac_p=float(stats.mannwhitneyu(c.k, p.k, alternative="greater").pvalue),
        n_plac_xi4=len(psel), median_k_plac_xi4=float(psel.k.median()) if len(psel) else None,
        mw_cand_vs_plac_xi4_p=float(stats.mannwhitneyu(c.k, psel.k, alternative="greater").pvalue) if len(psel) > 2 else None,
        frac_cand_k_gt_0=float((c.k > 0).mean()), frac_plac_k_gt_0=float((p.k > 0).mean()),
        median_amp_ratio_cand=float(c.amp_ratio.median()),
        frac_cand_abs_dphi_lt_0p125=float((c.dphi.abs() < 0.125).mean()),
        frac_plac_abs_dphi_lt_0p125=float((p.dphi.abs() < 0.125).mean()))
    out["candidate_training"] = dict(median_P=float(c.P.median()), P_range=[float(c.P.min()), float(c.P.max())],
                                     median_xi=float(c.xi.median()), frac_xi_gt4=float((c.xi > 4).mean()),
                                     median_ncyc_test=float((c.T_test / c.P).median()),
                                     median_n_test_bins=float(c.n_test_bins.median()))
    out["named"] = {}
    for full, short in NAMED.items():
        r = df[(df.kind == "cand") & (df.name == full)]
        if len(r) and r.iloc[0].status == "ok":
            r = r.iloc[0]
            out["named"][short] = dict(P=r.P, xi=r.xi, k=r.k, p_drw=r.p_drw, p_spl=r.p_spl, dphi=r.dphi,
                                       amp_ratio=r.amp_ratio, power_drw=r.alt_power_drw,
                                       confirmed=bool(r.p_drw < 0.05 / 3))
        else:
            out["named"][short] = dict(status=None if not len(r) else r.iloc[0].status)
    out["period_check"] = {}
    for full, P0 in PUBLISHED_P.items():
        r = df[(df.kind == "cand") & (df.name == full)]
        out["period_check"][full] = dict(published=P0, refit=float(r.iloc[0].P) if len(r) else None)
    out["sig_candidates_drw"] = c[c.p_drw < 0.05][["id", "name", "P", "xi", "k", "p_drw", "p_spl"]].to_dict("records")
    cols = ["id", "kind", "name", "status", "n_train_bins", "n_test_bins", "P", "amp", "xi", "ncyc", "drw_sigma",
            "drw_tau", "k", "dphi", "amp_ratio", "p_drw", "p_spl", "p_drw_unc", "p_spl_unc", "drw_n_acc",
            "drw_conditioned", "spl_n_acc", "spl_conditioned", "alt_power_drw", "alt_power_spl"]
    df[[c_ for c_ in cols if c_ in df]].sort_values("id").to_csv(os.path.join(ROOT, "data", "results_table.csv"),
                                                                    index=False, float_format="%.5g")
    json.dump(out, open(os.path.join(ROOT, "data", "summary.json"), "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
