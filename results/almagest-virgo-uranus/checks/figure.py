"""Figure 1 of the paper (needs matplotlib; not run by ci.sh).
Usage: python -I checks/figure.py RAWDIR paper/fig_virgo17.png"""
import sys, io, os, runpy, contextlib
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
raw, png = sys.argv[1], sys.argv[2]
tmp = png + '.json'; sys.argv = ['x', raw, tmp]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analysis.py'))
os.remove(tmp)
h = g['out_d']['hipparchus']; sep = g['sep']; P = g['P']; V = g['V']; hip = g['hip']
slon, slat = g['star_ecl'](h['jd0']); idx = {x: i for i, x in enumerate(hip)}
dL, dB = h['dL_deg'], h['dB_deg']; x0, y0 = h['e513_frame']
U = g['uranus'](f"{raw}/uranus_hipparchus.txt"); Ug = U[U[:, 1] >= 120]
C = [e for e in P if e['I'] == '1' and e['HIP'] in idx and abs(e['bet']) <= 10 and e['P'] != 513 and e['VP'] and e['VP'] >= 5]
R = np.sort(np.array([sep(e['lam']-dL, e['bet']-dB, slon[idx[e['HIP']]], slat[idx[e['HIP']]]) for e in C]) * 60)

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={'width_ratios': [1.15, 1]})
box = 2.5
m = (np.abs(slon - x0) < box) & (np.abs(slat - y0) < box) & (V <= 6.0)
a.scatter(slon[m], slat[m], s=(7 - V[m]) ** 2 * 6, c='0.35', zorder=2, label='stars, V <= 6.0')
u = (np.abs(Ug[:, 2] - x0) < box) & (np.abs(Ug[:, 3] - y0) < box)
a.plot(Ug[u, 2], Ug[u, 3], '.', ms=1.5, c='tab:blue', zorder=1, label='Uranus, elongation >= 120 deg')
a.plot(*h['uranus_at_best'], 'o', mfc='none', mec='tab:blue', ms=9, zorder=3)
i76 = idx[66098]
a.annotate('76 Vir', (slon[i76], slat[i76]), xytext=(6, -12), textcoords='offset points')
if 65474 in idx: a.annotate('Spica', (slon[idx[65474]], slat[idx[65474]]), xytext=(10, -4), textcoords='offset points')
a.plot(x0, y0, 'x', c='tab:red', ms=10, mew=2, zorder=4, label='Virgo 17, Hipparchus frame')
a.add_patch(plt.Circle((x0, y0), h['d_U_arcmin'] / 60, fill=False, ls=':', ec='tab:blue'))
a.add_patch(plt.Circle((x0, y0), h['r_star_arcmin'] / 60, fill=False, ls=':', ec='0.35'))
a.set_xlim(x0 + box, x0 - box); a.set_ylim(y0 - box, y0 + box); a.set_aspect('equal')
a.set_xlabel('ecliptic longitude of date, -128 (deg)'); a.set_ylabel('ecliptic latitude (deg)')
a.legend(loc='upper right', fontsize=7.5, framealpha=0.9)
b.step(R, np.arange(1, len(R) + 1) / len(R) * 100, where='post', c='k')
for v, q, c, t in ((h['d_U_arcmin'], h['Q_U'], 'tab:blue', 'Uranus'), (h['r_star_arcmin'], h['Q_S'], '0.35', '76 Vir')):
    b.axvline(v, c=c, ls='--'); b.text(v + 2, q - 9, f"{t}\n{v:.1f}', {q:.1f} %", color=c, fontsize=8.5)
b.axhline(95, c='tab:red', lw=0.8, ls=':'); b.axhline(50, c='tab:red', lw=0.8, ls=':')
b.set_xlabel("distance of entry from its identified star (arcmin)"); b.set_ylabel('percent of the 103 reference entries')
b.set_xlim(0, 160); b.set_ylim(0, 101)
fig.tight_layout(); fig.savefig(png, dpi=150)
