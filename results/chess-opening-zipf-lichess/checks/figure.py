"""Figure 1 from data/results.json and the full-N histograms. Usage: python -I figure.py RESULTS_JSON HISTS_NPZ OUT_PNG"""
import json, sys, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zipflib import D, pooled, bin_edges

r = json.load(open(sys.argv[1])); t = r["tests"]; nf = t["N_full"]
Ns = np.array(sorted(int(k) for k in t["grid_mean"]))
g = lambda f: np.array([t["grid_mean"][str(N)][f] for N in Ns])
m = lambda f: np.array([t["model"][str(N)][f] for N in Ns])
DATA, MODEL, THEORY = "#1f5fa8", "#c8641e", "#555555"
fig, ax = plt.subplots(2, 2, figsize=(10, 8))
a = ax[0, 0]
z = np.load(sys.argv[2]); h = {d: (z[f"v{d}"], z[f"c{d}"]) for d in range(1, D + 1)}
v, c = pooled(h)
e = bin_edges(nf); k = np.searchsorted(e, v, side="right") - 1
cnt = np.bincount(k, weights=c, minlength=len(e))[: len(e) - 1]; ok = cnt > 0
x = np.sqrt(e[:-1] * (e[1:] - 1))[ok]; y = (cnt / (e[1:] - e[:-1]))[ok]
a.loglog(x, y, "o", ms=3, color=DATA, label=f"Lichess, N = {nf:.3g} (log bins)")
xx = np.logspace(0, np.log10(nf / 10), 50)
a.loglog(xx, nf / (np.log(2) * xx ** 2), "-", color=THEORY, label=r"Eq. 8, arcsine: $N/(\mu n^2)$, $\mu=\ln 2$")
mu = json.load(open(os.path.join(os.path.dirname(sys.argv[1]), "explore.json")))["N10^6.5"]["mu_pooled"]
a.loglog(xx, nf / (mu * xx ** 2), "--", color=THEORY, label=rf"same, measured $\mu={mu:.2f}$ (exploratory)")
a.set_xlabel("popularity n"); a.set_ylabel("S(n), pooled d = 1..40"); a.legend(frameon=False); a.set_title("A  pooled weights")
a = ax[0, 1]
gd = [x for x in r["grid"] if x["N"] == nf][0]["alpha_d"]; md = [x for x in r["model"] if x["N"] == nf][0]["alpha_d"]
d = np.arange(1, D + 1)
a.plot(d, gd, "o", ms=3, color=DATA, label="Lichess")
a.plot(d, md, "s", ms=3, color=MODEL, label="Eq. 3 model, arcsine q(r)")
a.plot(d, 1 + (d - 1) / np.log(nf), "-", color=THEORY, label=r"Eq. 6: $1+(d-1)/\ln N$")
a.axhline(2, color="#999999", lw=0.8, ls=":")
a.set_xlabel("depth d (plies)"); a.set_ylabel(r"$\alpha_d$"); a.set_xlim(0, 30); a.set_ylim(0.8, 4); a.legend(frameon=False); a.set_title(f"B  depth exponents, N = {nf:.3g}")
a = ax[1, 0]
a.semilogx(Ns, g("rho"), "o-", color=DATA, label="Lichess")
a.semilogx(Ns, m("rho"), "s-", color=MODEL, label="model")
a.axhline(1, color=THEORY, label="Eq. 6")
a.set_xlabel("N (games)"); a.set_ylabel(r"$\rho = b(N)\,\ln N$"); a.legend(frameon=False); a.set_title("C  slope of $\\alpha_d$ times ln N")
a = ax[1, 1]
a.plot(np.log(Ns), g("d_cr"), "o-", color=DATA, label="Lichess")
a.plot(np.log(Ns), m("d_cr"), "s-", color=MODEL, label="model")
a.plot(np.log(Ns), 1 + np.log(Ns), "-", color=THEORY, label="Eq. 9: 1 + ln N")
a.plot([np.log(1.4e6)], [15], "*", ms=12, color="#000000", label="source (ScidBase)")
a.set_xlabel("ln N"); a.set_ylabel(r"$d_{cr}$"); a.legend(frameon=False); a.set_title("D  critical depth")
for a in ax.flat:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(sys.argv[3], dpi=130)
