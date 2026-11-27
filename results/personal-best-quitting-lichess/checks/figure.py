"""Figure: Blitz quit rate (no game within 60 min) by rating minus personal best, from results JSON.
Error bars: 95% binomial intervals of each bin (normal approximation; they ignore clustering by player).
Usage: python figure.py RESULTS_JSON OUT_FILE [RESULTS_JSON_B]"""
import sys, json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.0))
inputs = sys.argv[1:2] + sys.argv[3:4]
for i, (path, label, color) in enumerate(zip(inputs, ["2013-2015", "2016-02 to 2016-12"], ["#1f5fa8", "#c4572a"])):
    r = json.load(open(path))
    b = {int(k): v for k, v in r["bins_blitz"].items()}
    xs = sorted(k for k in b if -30 <= k <= 15)
    ys = [100 * b[k][0] for k in xs]
    es = [196 * math.sqrt(b[k][0] * (1 - b[k][0]) / b[k][1]) for k in xs]
    p = r["primary"]
    lab = f"{label}: jump {100*p['jump']:+.2f} pp [{100*p['ci'][0]:+.2f}, {100*p['ci'][1]:+.2f}]"
    off = 0.15 * (i - 0.5) * (len(inputs) > 1)
    ax.errorbar([x + off for x in xs], ys, yerr=es, fmt="o", ms=3, lw=0.8, color=color, label=lab)
ax.axvline(0.5, color="0.4", lw=0.8, ls="--")
ax.set_xlabel("rating after the game minus personal best before it")
ax.set_ylabel("quit rate, % (no game within 60 min)")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8, frameon=False, ncol=1)
fig.tight_layout()
fig.savefig(sys.argv[2], dpi=150)
