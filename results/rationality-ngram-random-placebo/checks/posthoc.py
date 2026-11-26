"""Post-hoc numbers (not pre-registered). They describe the sensitivity of the primary test.
Usage: python posthoc.py <table.npz> <out.json> [figure.png]

It runs the pre-registered analysis.py unchanged (K = 40, 20, 80) and reuses its placebo
pairs. Outputs:
  K sensitivity: p-values for K = 20 and K = 80 (same seeds).
  Detectable size: share of the 10,000 FPS null g values (eng) below the null 5% quantile
    after a specific extra hinge of f * g_obs is added.
  Skew gap: mean skew of A' minus mean skew of B' in the FPS pairs against the observed gap,
    and the p-value after a linear adjustment of g to the observed gap.
  Fiction share: eng-fiction tokens / eng tokens in 1850, 1975, 2019.
  Neighbours: the 10 nearest FPS candidates of some flag words.
"""
import sys, os, json, runpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TAB, OUT = sys.argv[1], sys.argv[2]
FIG = sys.argv[3] if len(sys.argv) > 3 else None


def run_analysis(K):
    os.environ["MATCH_K"] = str(K)
    tmp = OUT + f".K{K}.tmp.json"
    sys.argv = [os.path.join(HERE, "analysis.py"), TAB, tmp]
    g = runpy.run_path(os.path.join(HERE, "analysis.py"), run_name="__main__")
    os.remove(tmp)
    return g


res = {"K_sensitivity": {}}
for K in (20, 80):
    G = run_analysis(K)
    res["K_sensitivity"][f"K={K}"] = {
        "FPS_p": {c: G["tests"]["FPS"][c]["p_one_sided"] for c in G["corpora"]},
        "FP_p_max": max(G["tests"]["FP"][c]["p_one_sided"] for c in G["corpora"]),
    }
G = run_analysis(40)  # pre-registered K; the globals are the ones of the primary analysis

obs, keep, Sw, nA = G["obs"], G["keep"], G["Sw"], len(G["A"])
iA, iB = G["iA"], G["iB"]
gobs = obs["eng"]["g"]
L, b, g, tau = keep[("FPS", "eng")]
q05 = np.quantile(g, 0.05)
res["detectable"] = {
    "g_obs_per_decade": 10 * gobs,
    "null_median_per_decade": 10 * float(np.median(g)),
    "null_q05_per_decade": 10 * float(q05),
    "null_sd_per_decade": 10 * float(g.std()),
    "excess_over_median_per_decade": 10 * float(gobs - np.median(g)),
    "excess_over_median_share_of_g_obs": float((gobs - np.median(g)) / gobs),
    "power_extra_hinge": {f"{f:.2f}": float(((g + f * gobs) <= q05).mean())
                          for f in (0.10, 0.15, 0.20, 0.25, 0.30)},
}

pairs = G["draw_pairs"]("FPS", 20261127)  # same seed, so the same pairs as the primary test
dS = Sw[pairs[:, :nA]].mean(1) - Sw[pairs[:, nA:]].mean(1)
dobs = float(Sw[iA].mean() - Sw[iB].mean())
sl, ic = np.polyfit(dS, g, 1)
adj = gobs - (ic + sl * dobs)
resid = g - (ic + sl * dS)
res["skew_gap"] = {
    "observed": dobs,
    "placebo_mean": float(dS.mean()),
    "placebo_sd": float(dS.std()),
    "corr_gap_g": float(np.corrcoef(dS, g)[0, 1]),
    "p_after_linear_adjustment": float((1 + (resid <= adj).sum()) / (len(g) + 1)),
}

Ne, Nf, YEARS = G["Ne"], G["Nf"], G["YEARS"]
res["fiction_share_of_tokens"] = {str(y): float(Nf[YEARS == y][0] / Ne[YEARS == y][0]) for y in (1850, 1975, 2019)}

nb = G["neighbours"]("FPS")
words = G["words"]
res["neighbours_FPS"] = {w: [str(words[i]) for i in nb[(G["A"] + G["B"]).index(w)][:10]]
                         for w in ("data", "science", "fact", "soul", "feel", "god")}

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))

if FIG:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    YEARS = G["YEARS"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    Lo = np.array(obs["eng"]["L"]); Lo = Lo - Lo.mean()
    for j, (ctrl, name) in enumerate([("FP", "frequency + POS"), ("FPS", "frequency + POS + fiction skew")]):
        Lc = keep[(ctrl, "eng")][0]; Lc = Lc - Lc.mean(1, keepdims=True)
        lo, mid, hi = np.quantile(Lc, [0.025, 0.5, 0.975], axis=0)
        ax[j].fill_between(YEARS, lo, hi, color="0.85", label="placebo pairs, 95% band")
        ax[j].plot(YEARS, mid, color="0.5", lw=1, label="placebo median")
        ax[j].plot(YEARS, Lo, "k", lw=1.6, label="rationality / intuition")
        ax[j].axvline(1980, ls=":", c="r")
        ax[j].set_title(f"eng, placebo matched on {name}", fontsize=10)
        ax[j].set_xlabel("year")
    ax[0].set_ylabel("L(t), centred")
    ax[0].legend(fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(FIG, dpi=150)
