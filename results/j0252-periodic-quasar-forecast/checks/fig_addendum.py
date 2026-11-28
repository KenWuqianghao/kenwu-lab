"""Figure for Addendum 1: p_sig of the censored model across the paper's published r-band DRW posterior.
Reads data/drw_posterior_r.json and data/expected.json; writes data/fig_addendum.png."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
post = json.load(open(ROOT / 'data/drw_posterior_r.json'))
a = json.load(open(ROOT / 'data/expected.json'))['addendum1']
fig, ax = plt.subplots(figsize=(6.4, 4.6))
for name, ls in (('c95', ':'), ('c68', '-')):
    lt, s = np.array(post[name]['log10_tau']), np.array(post[name]['sigma'])
    ax.plot(lt, s, ls, color='#8a8a8a', lw=1.2, label='paper DRW posterior %s%%' % name[1:])
pts = [r for c in ('c95', 'c68') for r in a['posterior_contours'][c]['rows']]
pts += [[np.log10(g['tau']), g['sigma'], g['p_sig']] for g in a['grid_tau716']]
pts = np.array([p[:3] for p in pts])
ok = pts[:, 2] < 0.01
ax.scatter(pts[ok, 0], pts[ok, 1], s=42, marker='o', color='#257de0', edgecolor='white', lw=1, zorder=3, label='p_sig < 0.01 (uninflated)')
ax.scatter(pts[~ok, 0], pts[~ok, 1], s=56, marker='^', color='#f47230', edgecolor='white', lw=1, zorder=3, label='p_sig >= 0.01 (uninflated)')
b = a['best_fit_drw']
ax.scatter([2.9], [0.15], s=140, marker='*', color='#1a1a1a', zorder=4,
           label='paper best fit: p_sig %.4f; inflated %.3f' % (b['p_sig'], b['p_sig_inflated']))
ax.set_xlabel('log10 DRW tau (days, observed frame)')
ax.set_ylabel('DRW sigma (mag)')
ax.set_title('Censored model: chance of T <= %.2f if the forecast is true' % a['T_obs'], fontsize=10)
ax.grid(color='#e6e6e6', lw=0.6); ax.set_axisbelow(True)
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False)
ax.legend(fontsize=7.5, frameon=False, loc='upper left')
fig.tight_layout(); fig.savefig(ROOT / 'data/fig_addendum.png', dpi=150)
print('wrote data/fig_addendum.png')
