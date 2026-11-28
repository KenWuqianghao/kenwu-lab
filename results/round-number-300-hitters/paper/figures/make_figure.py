"""Draw Figure 1 from data/expected.json. Needs matplotlib (3.11.2 was used). CI does not run it.

Usage: python3 -I paper/figures/make_figure.py   (from the result folder)
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E = json.load(open(os.path.join(ROOT, "data", "expected.json")))
X9, X0 = "#257de0", "#f47230"   # slot 1 blue (x9), slot 2 orange (x0)
INK, MUTED = "#1f1f1f", "#6b6b6b"

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1.35, 1]})
for ax in (a, b):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
    ax.grid(axis="y", color="#e6e6e6", lw=0.6)
    ax.set_axisbelow(True)

# Panel a: season-end counts just below (x9) and at (x0) each threshold.
ths = [t for t in range(250, 350, 10)]
w = 0.38
for i, t in enumerate(ths):
    r = E["T1"][str(t)]
    a.bar(i - w / 2 - 0.01, r["n_x9"], w, color=X9, edgecolor="white", lw=1)
    a.bar(i + w / 2 + 0.01, r["n_x0"], w, color=X0, edgecolor="white", lw=1)
    if r["ratio"] is not None:
        a.text(i, max(r["n_x9"], r["n_x0"]) + 2, f"{r['ratio']:.2f}", ha="center",
               fontsize=7.5, color=INK, fontweight="bold" if t in (300, 330) else "normal")
a.set_xticks(range(len(ths)))
a.set_xticklabels([f".{t - 1:03d}/.{t:03d}" for t in ths], rotation=45, ha="right")
a.set_ylabel("batter-seasons", color=INK, fontsize=9)
a.set_title("a. Season-end averages, MLB 2009–2025 (number = ratio)", fontsize=9.5,
            color=INK, loc="left")
a.legend(handles=[Patch(color=X9, label="ends at .xx9"), Patch(color=X0, label="ends at .xx0")],
         frameon=False, fontsize=8, loc="upper right")

# Panel b: last scheduled PA at .298/.299 against .300/.301 (paper's unit), with paper's values.
P = E["paper_comparisons"]
rows = [("hit", P["P2_hit_298_299_vs_300_301"], (35.2, 22.4)),
        ("walk", P["P4_walk_298_299_vs_300_301"], (2.5, 8.6)),
        ("pinch hitter", P["P5_sub_298_299_vs_300_301"], (4.1, 19.7))]
for i, (nm, r, pap) in enumerate(rows):
    v1, v2 = 100 * r["x1"] / r["n1"], 100 * r["x2"] / r["n2"]
    b.bar(i - w / 2 - 0.01, v1, w, color=X9, edgecolor="white", lw=1)
    b.bar(i + w / 2 + 0.01, v2, w, color=X0, edgecolor="white", lw=1)
    b.text(i - w / 2, v1 + 0.8, f"{r['x1']}/{r['n1']}", ha="center", fontsize=7, color=INK)
    b.text(i + w / 2, v2 + 0.8, f"{r['x2']}/{r['n2']}", ha="center", fontsize=7, color=INK)
    b.scatter([i - w / 2, i + w / 2], pap, marker="D", s=22, color="white",
              edgecolor=INK, lw=1.2, zorder=3)
paper = Line2D([], [], marker="D", ls="", ms=5, mfc="white", mec=INK, mew=1.2,
               label="Pope & Simonsohn, 1975–2008")
b.set_xticks(range(3))
b.set_xticklabels([r[0] for r in rows], fontsize=8.5)
b.set_ylabel("% of last scheduled PAs", color=INK, fontsize=9)
b.set_title("b. Last scheduled PA by entering average (post hoc)", fontsize=9.5, color=INK,
            loc="left")
b.set_ylim(0, 40)
b.legend(handles=[Patch(color=X9, label=".298/.299"), Patch(color=X0, label=".300/.301"), paper],
         frameon=False, fontsize=7.5, loc="upper right")
fig.tight_layout()
out = os.path.join(ROOT, "paper", "figures", "fig1.png")
fig.savefig(out, dpi=200)
print(out)
