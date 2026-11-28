"""Exploratory, NOT pre-registered (see PROTOCOL.md addendum). Usage: python -I checks/exploratory.py RAWDIR OUTJSON"""
import sys, json, runpy, numpy as np
sys.argv = ['x', sys.argv[1], sys.argv[2] + '.tmp']; raw, outp = sys.argv[1], sys.argv[2][:-4]
g = runpy.run_path(__file__.replace('exploratory.py', 'analysis.py'))
h = g['out_d']['hipparchus']; sep = g['sep']; P = g['P']
slon, slat = g['star_ecl'](h['jd0']); idx = {x: i for i, x in enumerate(g['hip'])}
dL, dB = h['dL_deg'], h['dB_deg']
C = [e for e in P if e['I'] == '1' and e['HIP'] in idx and abs(e['bet']) <= 10 and e['P'] != 513 and e['VP'] and e['VP'] >= 5]
R = np.array([sep(e['lam']-dL, e['bet']-dB, slon[idx[e['HIP']]], slat[idx[e['HIP']]]) for e in C]) * 60
# 2-D residual density: Rayleigh-like empirical density per unit area, via counts in annuli of +-8 arcmin
def dens(r, w=8.0): return np.mean(np.abs(R - r) <= w) / (2 * np.pi * r * 2 * w)
U = g['uranus'](f"{raw}/uranus_hipparchus.txt"); Ug = U[U[:, 1] >= 120]
out = {'LR_uranus_over_76Vir_density': float(dens(h['d_U_arcmin']) / dens(h['r_76Vir_arcmin']))}
# textual variant: latitude south 0;10 instead of north
x, y = 177.25 - dL, -1/6 - dB
out['variant_south_lat'] = {'d_U_arcmin': float(sep(x, y, Ug[:, 2], Ug[:, 3]).min() * 60),
                            'r_76Vir_arcmin': float(sep(x, y, slon[idx[66098]], slat[idx[66098]]) * 60)}
# Uranus latitude range while within 2 deg of entry longitude
m = np.abs(((Ug[:, 2] - (177.25 - dL)) + 180) % 360 - 180) <= 2
out['uranus_lat_range_near_entry'] = [float(Ug[m, 3].min()), float(Ug[m, 3].max())]
out['n_R_ge_76Vir'] = int(np.sum(R >= h['r_76Vir_arcmin']))
json.dump(out, open(outp, 'w'), indent=1); print(json.dumps(out, indent=1))
