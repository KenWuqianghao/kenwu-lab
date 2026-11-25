"""Draw paper/figures/fig1.pdf from data/results.json. Needs matplotlib (not used by CI)."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "..", "..", "data", "results.json")))
SYN = 29.530589
COL = {"A": "#1f4e8c", "B": "#d9822b"}
LAB = {"A": "1895–2008 (A)", "B": "2009–2026 (B, held out)"}
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))

k = np.arange(10)
th = 2 * np.pi * (k + 0.5) / 10
x = (k + 0.5) / 10 * SYN
tt = np.linspace(0, 2 * np.pi, 400)
for p in "AB":
    o = r[p]["observed"]
    m = np.array(o["m"]) * 1000
    fit = m.mean() + 1000 * (o["a2"] * np.cos(2 * tt) + o["b2"] * np.sin(2 * tt))
    ax[0].plot(x, m, "o", color=COL[p], label=f"{LAB[p]}, $R^2_2$ = {o['r2']:.2f}")
    ax[0].plot(tt / (2 * np.pi) * SYN, fit, "-", color=COL[p], lw=1)
ax[0].axvline(SYN / 2, color="grey", lw=0.6, ls=":")
ax[0].text(SYN / 2 + 0.3, 9.5, "full moon", color="grey", fontsize=8)
ax[0].set_xlabel("days after new moon (class centre)")
ax[0].set_ylabel("mean standardized precipitation (×10$^{-3}$)")
ax[0].set_title("a. National class means and second harmonic", fontsize=10, loc="left")
ax[0].set_ylim(-19, 11)
ax[0].legend(fontsize=8, frameon=False, loc="lower left")

for p in "AB":
    v = r[p]["scan"]["values"]
    P = np.array([d["P"] for d in v])
    S = np.array([d["S"] for d in v]) * 100
    ax[1].plot(P, S, "-", color=COL[p], lw=1, label=LAB[p] + ", fixed-period pseudo-phase")
    ax[1].plot([SYN], [r[p]["observed"]["S"] * 100], "*", color=COL[p], ms=12, mec="k", mew=0.5)
ax[1].axvspan(SYN - 1, SYN + 1, color="grey", alpha=0.15, lw=0)
ax[1].axhline(5, color="grey", lw=0.6, ls=":")
ax[1].set_xlabel("period of the pseudo-phase (days)")
ax[1].set_ylabel("stations with significant $R^2_2$ (%)")
ax[1].set_title("b. Station rate S: period scan; ★ = true lunar phase", fontsize=10, loc="left")
ax[1].legend(fontsize=8, frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig1.pdf"))
fig.savefig(os.path.join(HERE, "fig1.png"), dpi=150)
