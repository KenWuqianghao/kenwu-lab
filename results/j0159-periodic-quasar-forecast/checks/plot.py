"""Draw data/fig_forecast.png: (a) the CRTS points of Fig. 1a of Zheng et al. 2016 with the published curve and our refit;
(b) ZTF data (30 d medians, per-object offsets removed) with both curves continued.
Descriptive only; no number in the paper comes from this figure. Needs work/ztf_raw.csv and work/src/src.tgz from rerun.py."""
import sys
from pathlib import Path
sys.argv.append('--cache')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import rerun

dia, _ = rerun.crts_points(rerun.lc_eps())
tc, mc = dia[:, 0], dia[:, 1]
good = np.abs(mc - np.median(mc)) < 0.3
tc, mc = tc[good], mc[good]
P_REFIT = rerun.json.load(open(rerun.ROOT / 'data/expected.json'))['addendum1']['crts_refit']['P']
c = np.linalg.lstsq(rerun.sin_basis(tc, P_REFIT), mc, rcond=None)[0]
refit = lambda tt: rerun.sin_basis(tt, P_REFIT)[:, :2] @ c[:2]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={'width_ratios': [1, 1]}, sharey=True)
a1.plot(tc, mc - c[2], 'o', mfc='none', mec='0.4', ms=3, label='CRTS V, read from Fig. 1a')
tt = np.linspace(53600, 56650, 1500)
a1.plot(tt, rerun.template(tt), 'k-', lw=1.2, label='published: 0.1 sin(2π(t−53413.09)/741)')
a1.plot(tt, refit(tt), '-', color='#d95f02', lw=1.2, label=f'refit to these points: {P_REFIT:.0f} d, {np.hypot(*c[:2]):.3f} mag')
a1.set_title('(a) CRTS 2005-2013 (data of the paper)', fontsize=9)
a1.set_xlabel('MJD'); a1.set_ylabel('magnitude − mean')
a1.legend(fontsize=7, loc='lower left')

raw = rerun.raw_csv()
for b, col in (('zg', '#1b9e77'), ('zr', '#7570b3')):
    t, m, e, oid = rerun.load(raw, (b,)); Xo = rerun.design(oid)
    r = m - Xo @ rerun.lsq(m, e, Xo, [])
    edges = np.arange(t.min(), t.max() + 30, 30); idx = np.digitize(t, edges)
    ks = sorted(set(idx))
    a2.plot([t[idx == k].mean() for k in ks], [np.median(r[idx == k]) for k in ks], 'o', color=col, ms=3,
            label=f'ZTF {b[1]}, 30 d medians')
tz = np.linspace(58250, 61000, 1500)
a2.plot(tz, rerun.template(tz), 'k-', lw=1.2, label='published curve, continued')
a2.plot(tz, refit(tz), '-', color='#d95f02', lw=1.2, label='CRTS refit, continued')
a2.set_title('(b) ZTF 2018-2025 (held out)', fontsize=9)
a2.set_xlabel('MJD'); a2.legend(fontsize=7, loc='lower left')
a2.set_ylim(0.36, -0.25)
fig.tight_layout()
fig.savefig(rerun.ROOT / 'data/fig_forecast.png', dpi=130)
