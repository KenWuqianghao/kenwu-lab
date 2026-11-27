"""Figure 1: annual M>=7 counts in ComCat. Usage: python3 paper/figures/make_figure.py WORK/results.json"""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
r = json.loads(Path(sys.argv[1]).read_text())
c = r["counts_1900_2025"]; ys = [int(y) for y in c]; n = [c[str(y)] for y in ys]
lam0 = r["baseline"]["lambda0"]
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.axvspan(2017.5, 2022.5, color="#f2d9a6", lw=0, label="forecast window 2018–2022")
ax.bar(ys, n, width=0.85, color="#4a6fa5")
ax.axhline(lam0, color="k", lw=1, label=f"1900–2017 mean {lam0:.1f}/yr")
ax.axhline(1.25 * lam0, color="#c0392b", lw=1, ls="--", label=f"forecast +25 % = {1.25*lam0:.1f}/yr")
ax.plot([2017.5, 2022.5], [r["P1"]["rate"]] * 2, color="#e67e22", lw=2.5, label=f"observed 2018–2022 {r['P1']['rate']:.1f}/yr")
ax.set_xlim(1899, 2026); ax.set_ylim(0, 30); ax.set_ylabel("M≥7 events per year (ComCat)")
ax.legend(fontsize=7.5, loc="upper left", ncol=2, frameon=False)
fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent / "fig1_counts.png", dpi=150)
print("wrote paper/figures/fig1_counts.png")
