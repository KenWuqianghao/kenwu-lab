"""Draw data/fig_vatican.png and paper/fig_vatican.pdf from data/vatican_corrected.csv. Needs matplotlib (not used by ci.sh)."""
import csv, os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = [x for x in csv.DictReader(open(os.path.join(root, 'data', 'vatican_corrected.csv'))) if not x['note']]
a = [float(x['sun_alt_dr4_deg']) for x in r]; b = [float(x['sun_alt_nearest_deg']) for x in r]
bins = list(range(-76, 80, 5))
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.axvspan(-6, 75, color='#eeeeee', zorder=0)
ax.hist(a, bins=bins, histtype='step', lw=2, color='#c0392b', label='DR4 ut_mid (logged time read as UT)')
ax.hist(b, bins=bins, histtype='step', lw=2, color='#1f5fa8', label='logged time read as local sidereal time')
ax.text(-4, ax.get_ylim()[1] * 0.55, 'Sun above -6 deg', fontsize=8, color='#555555')
ax.set_xlabel('Sun altitude at the exposure midpoint (deg)'); ax.set_ylabel('exposures')
ax.set_title(f'Vatican Observatory archive 501, {len(r)} exposures, 1951-1953', fontsize=10)
ax.legend(fontsize=8, loc='upper right', frameon=False); ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(root, 'data', 'fig_vatican.png'), dpi=150)
fig.savefig(os.path.join(root, 'paper', 'fig_vatican.pdf'))
print(sum(x > -6 for x in a), sum(x > -6 for x in b), len(r))
