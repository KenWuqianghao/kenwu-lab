"""Figure 1 of the paper: the digitized r-band model of Liao et al. (2021), our continuation at P = 1466 d,
and the ZTF zr light curve in 60-day bins. Descriptive only; no number of the paper comes from this figure.
Reads work/ztf_raw.csv (written by checks/rerun.py) and data/model_r_digitized.json; writes data/fig_forecast.png.
Each ZTF object is shifted so that its median before the cutoff equals the median of the digitized model
over the same dates (MJD 58300-58889)."""
import csv, json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'checks'))
from rerun import template_fn, CUT, END

d = json.load(open(ROOT / 'data/model_r_digitized.json'))
tm, mm = np.array(d['mjd']), np.array(d['mag'])
rows = [r for r in csv.DictReader(open(ROOT / 'work/ztf_raw.csv'))
        if r['filtercode'] == 'zr' and r['catflags'] == '0' and float(r['mjd']) <= END]
t = np.array([float(r['mjd']) for r in rows]); m = np.array([float(r['mag']) for r in rows])
e = np.array([float(r['magerr']) for r in rows]); oid = np.array([r['oid'] for r in rows])
ref = np.median(mm[(tm >= 58300) & (tm <= 58889)])
for k in set(oid):
    s = oid == k
    pre = s & (t <= CUT)
    m[s] += ref - np.median(m[pre] if pre.sum() >= 5 else m[s])

def bins(sel):
    out = []
    for lo in np.arange(t[sel].min(), t[sel].max() + 60, 60):
        k = sel & (t >= lo) & (t < lo + 60)
        if k.sum() >= 2:
            w = 1 / e[k] ** 2
            mu = np.sum(w * m[k]) / w.sum()
            se = max(np.std(m[k]) / np.sqrt(k.sum() - 1), 1 / np.sqrt(w.sum()))
            out.append((np.mean(t[k]), mu, se))
    return np.array(out)

tpl = template_fn()
tc = np.linspace(58889, END, 600)
fig, ax = plt.subplots(figsize=(9.6, 3.8))
ax.plot(tm, mm, '.', ms=1.5, color='#9a9a9a', label='Liao et al. (2021) Fig. 1, r-band q = 0.11 model (digitized)')
ax.plot(tc, ref + tpl(tc), '-', color='#1a1a1a', lw=1.6, label='our continuation at P = 1466 d')
for sel, col, lab in ((t <= CUT, '#257de0', 'ZTF zr before 2020-03-19 (60-d bins)'),
                      (t > CUT, '#d62728', 'ZTF zr held out, 2020-2025 (60-d bins)')):
    b = bins(sel)
    ax.errorbar(b[:, 0], b[:, 1], yerr=b[:, 2], fmt='o', ms=4, color=col, lw=1, label=lab)
ax.axvline(CUT, ls=':', color='#1a1a1a', lw=1)
ax.set_xlim(50700, 61200); ax.set_ylim(21.5, 20.1)
ax.set_xlabel('MJD'); ax.set_ylabel('r (mag)')
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False)
ax.legend(fontsize=7.5, frameon=False, loc='upper left', ncol=2)
fig.tight_layout(); fig.savefig(ROOT / 'data/fig_forecast.png', dpi=150)
print('wrote data/fig_forecast.png')
