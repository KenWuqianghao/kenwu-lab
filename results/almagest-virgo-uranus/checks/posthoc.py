"""Post hoc limits, NOT pre-registered. Added at the write stage to answer the issues of the
verification round (VERIFY.md). It uses the frame of checks/analysis.py and changes no
pre-registered number. Usage: python -I checks/posthoc.py RAWDIR OUTJSON"""
import sys, json, runpy, io, contextlib, os
import numpy as np
raw, outp = sys.argv[1], sys.argv[2]
sys.argv = ['x', raw, outp + '.tmp']
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analysis.py'))
os.remove(outp + '.tmp')
h = g['out_d']['hipparchus']; sep = g['sep']; P = g['P']; hip = g['hip']; V = g['V']
slon, slat = g['star_ecl'](h['jd0']); idx = {x: i for i, x in enumerate(hip)}
dL, dB = h['dL_deg'], h['dB_deg']
C = [e for e in P if e['I'] == '1' and e['HIP'] in idx and abs(e['bet']) <= 10 and e['P'] != 513]
res = np.array([sep(e['lam']-dL, e['bet']-dB, slon[idx[e['HIP']]], slat[idx[e['HIP']]]) for e in C]) * 60
vp = np.array([e['VP'] or 0 for e in C]); faint = vp >= 5; R = res[faint]
U = g['uranus'](f"{raw}/uranus_hipparchus.txt"); Ug = U[U[:, 1] >= 120]
lines = open(f"{raw}/uranus_hipparchus.txt").read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
cal = {float(x.split(',')[1]): x.split(',')[0].strip() for x in lines}
pct = lambda v, RR=R: float(100 * np.mean(RR <= v))
o = {'n_hip_stars': int(len(V)), 'n_ptolemy_entries': len(P)}
# Issue 1: placebo restricted to the longitude range of the Uranus track (1 deg margin)
lo, hi = float(Ug[:, 2].min()), float(Ug[:, 2].max()); o['U_lon_range_deg'] = [lo, hi]
band = [e for e in C if abs(e['bet']) <= 3]
dUb = np.array([sep(e['lam']-dL, e['bet']-dB, Ug[:, 2], Ug[:, 3]).min() * 60 for e in band])
inr = np.array([lo - 1 <= e['lam'] - dL <= hi + 1 for e in band])
match = dUb <= h['d_U_arcmin']
o['n_band'] = len(band); o['n_band_in_track'] = int(inr.sum()); o['n_match_in_track'] = int((match & inr).sum())
o['n_match_outside_track'] = int((match & ~inr).sum())
o['F_in_track'] = o['n_match_in_track'] / o['n_band_in_track']
o['match_entries'] = [int(e['P']) for e, m in zip(band, match) if m]
# Issue 2: magnitude codes in R; percentiles without code 9
o['R_VP_counts'] = {str(k): int((vp[faint] == k).sum()) for k in sorted(set(vp[faint]))}
o['R_code9_entries'] = [int(e['P']) for e, f in zip(C, faint) if f and e['VP'] == 9]
R59 = res[(vp == 5) | (vp == 6)]
o['no_code9'] = {'n': len(R59), 'Q_S': pct(h['r_star_arcmin'], R59), 'Q_U': pct(h['d_U_arcmin'], R59)}
R6 = res[vp == 6]
o['mag6_only'] = {'n': len(R6), 'Q_S': pct(h['r_star_arcmin'], R6), 'Q_U': pct(h['d_U_arcmin'], R6)}
# Issue 3: longitude 177;00 (Hertzog's preference, Swerdlow n. 4) with latitude +0;10 and -0;10
for name, L, B in (('lon177_00_lat_p0_10', 177.0, 1/6), ('lon177_00_lat_m0_10', 177.0, -1/6)):
    x, y = L - dL, B - dB
    ds = sep(x, y, slon, slat) * 60; j = int(np.argmin(np.where(V <= 6.0, ds, 1e9)))
    du = float(sep(x, y, Ug[:, 2], Ug[:, 3]).min() * 60)
    o[name] = {'r_star_arcmin': float(ds[j]), 'r_star_HIP': int(hip[j]), 'Q_S': pct(float(ds[j])),
               'd_U_arcmin': du, 'Q_U': pct(du)}
# Issue 4: bootstrap of R (5000 resamples, seed 1)
rng = np.random.default_rng(1); qs, qu = [], []
for _ in range(5000):
    r = rng.choice(R, len(R)); qs.append(100 * np.mean(r <= h['r_star_arcmin'])); qu.append(100 * np.mean(r <= h['d_U_arcmin']))
o['bootstrap'] = {'Q_S_2.5_97.5': [float(v) for v in np.percentile(qs, [2.5, 97.5])],
                  'Q_U_2.5_97.5': [float(v) for v in np.percentile(qu, [2.5, 97.5])],
                  'frac_Q_S_gt_95': float(np.mean(np.array(qs) > 95))}
# Issue 5: identification flag of entry 513 in the source table
e513 = next(e for e in P if e['P'] == 513); o['e513_I'] = e513['I']; o['e513_HIP'] = e513['HIP']
o['e513_VvG_dist_arcmin'] = float(e513['dist'])
# Issue 6: dates in the Horizons calendar (b = BC); astronomical year = 1 - BC year
o['date_jd0'] = cal.get(h['jd0']); o['date_best'] = cal.get(h['d_U_jd'])
o['window'] = [cal[U[0, 0]], cal[U[-1, 0]]]
k = int(np.argmin(np.abs(U[:, 0] - 1674754.5)))  # 128 BC Mar 25 = -127 Mar 25 (Julian), 0h TT
o['uranus_m127_mar25'] = {'date': cal[U[k, 0]], 'lon': float(U[k, 2]), 'lat': float(U[k, 3]), 'SOT': float(U[k, 1])}
# Elongation cut sensitivity
U_all = g['uranus'](f"{raw}/uranus_hipparchus.txt"); x, y = h['e513_frame']
o['d_U_by_elong_cut'] = {str(c): float(sep(x, y, U_all[U_all[:, 1] >= c, 2], U_all[U_all[:, 1] >= c, 3]).min() * 60) for c in (0, 90, 150)}
# Latitude and longitude parts of the two distances (entry minus object), arcmin
o['uranus_dlat_arcmin'] = (y - h['uranus_at_best'][1]) * 60
o['vir76_dlat_arcmin'] = (y - slat[idx[66098]]) * 60
o['vir76_dlon_arcmin'] = ((x - slon[idx[66098]] + 180) % 360 - 180) * 60
json.dump(o, open(outp, 'w'), indent=1); print(json.dumps(o, indent=1))
