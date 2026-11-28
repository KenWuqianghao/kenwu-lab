"""Draw Figure 1 from data/expected.json. Needs matplotlib (not installed by CI).

Usage: python3 paper/figures/make_figure.py   (from the result folder)
"""
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E = json.load(open(os.path.join(ROOT, "data", "expected.json")))
X = E["exploratory_verify_round1"]
OUT = os.path.join(ROOT, "paper", "figures")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))

# Left: Aug-Oct / May-Jul by four-year birth bin, with a 95% interval (log scale, Woolf).
bins = X["bins_4yr"]
xs = list(range(len(bins)))
r = [b["B"] / b["A"] for b in bins]
se = [math.sqrt(1 / b["A"] + 1 / b["B"]) for b in bins]
lo = [ri - ri * math.exp(-1.96 * s) for ri, s in zip(r, se)]
hi = [ri * math.exp(1.96 * s) - ri for ri, s in zip(r, se)]
colors = ["#7a7a7a" if i < 2 else "#1f5fa8" if i < 6 else "#c0392b" for i in xs]
for i in xs:
    ax1.errorbar(i, r[i], yerr=[[lo[i]], [hi[i]]], fmt="o", color=colors[i], capsize=3)
ax1.axhline(1.0, color="black", lw=0.8, ls=":")
ax1.axvline(5.5, color="black", lw=0.8, ls="--")
ax1.text(5.62, 2.38, "born from 1992-08:\nleague age 13 or less in 2006", fontsize=6.5, va="top")
ax1.set_xticks(xs)
ax1.set_xticklabels([b["born"][:4] + "-" + b["born"][-7:-3] for b in bins], rotation=40, fontsize=7)
ax1.set_xlabel("Birth years (August to July)")
ax1.set_ylabel("Aug-Oct births / May-Jul births")
ax1.set_ylim(0.5, 2.45)
ax1.set_title("US-born, MLB debut before 25", fontsize=9)

# Right: monthly share in cohorts C and T.
months = "JFMAMJJASOND"
c, t = E["months_C"], E["months_T"]
w = 0.4
ax2.bar([i - w / 2 for i in range(12)], [v / sum(c) for v in c], w, color="#1f5fa8",
        label=f"C, born 1976-08..1992-07 (n = {E['n_C']})")
ax2.bar([i + w / 2 for i in range(12)], [v / sum(t) for v in t], w, color="#c0392b",
        label=f"T, born 1996-05..2001-04 (n = {E['n_T']})")
ax2.axhline(1 / 12, color="black", lw=0.8, ls=":")
ax2.set_xticks(range(12))
ax2.set_xticklabels(list(months))
ax2.set_xlabel("Birth month")
ax2.set_ylabel("Share of cohort")
ax2.legend(fontsize=7, frameon=False, loc="upper left")
ax2.set_title("Birth months by cohort", fontsize=9)

fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1.pdf"))
fig.savefig(os.path.join(OUT, "fig1.png"), dpi=150)
