"""Figure: distribution of the forward score k and of p_DRW for candidates, placebo and injections."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import summarize  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = summarize.load()
ok = df[df.status == "ok"]
groups = [("cand", "86 candidates", "#c0392b"), ("plac", "placebo quasars", "#7f8c8d"),
          ("inj", "placebo + injected candidate sinusoid", "#2471a3")]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
bins = np.linspace(-2.5, 3, 34)
for kind, lab, col in groups:
    g = ok[ok.kind == kind]
    ax[0].hist(np.clip(g.k, -2.5, 3), bins, density=True, histtype="step", lw=2, color=col, label=f"{lab} (n={len(g)})")
    ax[1].hist(g.p_drw, np.linspace(0, 1, 21), density=True, histtype="step", lw=2, color=col)
ax[0].axvline(0, color="k", lw=0.8)
ax[0].axvline(1, color="k", lw=0.8, ls="--")
ax[0].set_xlabel("forward score k (1 = sinusoid continues, 0 = no skill)")
ax[0].set_ylabel("density")
ax[0].legend(fontsize=8)
ax[1].axhline(1, color="k", lw=0.8, ls="--")
ax[1].set_xlabel("per-object p-value against conditioned DRW null")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "data", "fig_forward_score.png"), dpi=130)

# Figure 2: the three named candidates. Binned training and test light curves and the frozen sinusoid.
import json  # noqa: E402

import analysis  # noqa: E402
import qpo  # noqa: E402

NAMED = [("C25", "SDSS J083111.23+123107.8"), ("C82", "SDSS J155304.40+240255.1"),
         ("C66", "SDSS J135830.46-012255.7")]
fig, ax = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
for a, (oid, name) in zip(ax, NAMED):
    r = json.load(open(os.path.join(ROOT, "work", "results", oid + ".json")))
    lc = analysis.prepare_df(qpo.load_raw(os.path.join(ROOT, "work", "lc", oid + ".csv")))
    (ttr, ytr, etr), (tte, yte, ete) = lc["train"], lc["test"]
    P, coef = r["P"], np.array(r["coef"])
    tt = np.linspace(ttr.min(), tte.max(), 2000)
    s = qpo.template(tt, np.array([P]), coef[None, :])[0]
    off = yte.mean() - qpo.template(tte, np.array([P]), coef[None, :])[0].mean()
    a.errorbar(ttr, ytr, etr, fmt="o", ms=3, color="k", label="training bins (DR11 epochs)")
    a.errorbar(tte, yte, ete, fmt="o", ms=3, color="#c0392b", label="test bins (after DR11)")
    a.plot(tt[tt <= qpo.DR11_END_PUBLIC], coef[0] + s[tt <= qpo.DR11_END_PUBLIC], color="#2471a3", lw=1.5,
           label="sinusoid fitted to training bins")
    a.plot(tt[tt > qpo.DR11_END_PUBLIC], off + s[tt > qpo.DR11_END_PUBLIC], color="#2471a3", lw=1.5, ls="--",
           label="frozen sinusoid, test offset")
    a.axvline(qpo.DR11_END_PUBLIC, color="0.5", lw=0.8)
    a.invert_yaxis()
    a.set_ylabel("r (mag)")
    a.set_title(f"{name}: P = {P:.0f} d, k = {r['k']:.2f}, p_DRW = {r['p_drw']:.2f}", fontsize=9)
ax[0].legend(fontsize=7, ncol=2, loc="lower left")
ax[-1].set_xlabel("MJD")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "data", "fig_named.png"), dpi=130)
