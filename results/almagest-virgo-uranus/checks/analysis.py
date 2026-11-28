"""Pre-registered test (PROTOCOL.md): Almagest entry 513 (Vir 17) versus Uranus.
Usage: python -I checks/analysis.py RAWDIR OUTJSON"""
import sys, json, warnings
import numpy as np
from astropy.coordinates import SkyCoord, GeocentricMeanEcliptic
from astropy.time import Time
import astropy.units as u
warnings.filterwarnings("ignore")
raw, out = sys.argv[1], sys.argv[2]

def dm(s):
    s = s.strip(); sg = -1 if s.startswith('-') else 1
    d, m = s.lstrip('+-').split(':'); return sg * (float(d) + float(m) / 60)

def rows(path):
    lines = [l.rstrip('\n') for l in open(path) if l.strip() and not l.startswith('#')]
    hdr = lines[0].split('\t'); data = [l.split('\t') for l in lines[3:]]
    return [dict(zip(hdr, [x.strip() for x in r])) for r in data if len(r) == len(hdr)]

def sep(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, (l1, b1, l2, b2))
    c = np.sin(b1)*np.sin(b2) + np.cos(b1)*np.cos(b2)*np.cos(l1-l2)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))

def wrap(x): return (x + 180) % 360 - 180

P = rows(f"{raw}/ptolemy.tsv")
for e in P:
    e['P'] = int(e['P']); e['lam'] = dm(e['Elon']); e['bet'] = dm(e['Elat'])
    e['HIP'] = int(e['HIP']) if e['HIP'] else None; e['VP'] = int(e['VP']) if e['VP'] else None
H = [h for h in rows(f"{raw}/hip_v65.tsv") if h["RAICRS"] and h["Vmag"]]
hip = np.array([int(h['HIP']) for h in H]); V = np.array([float(h['Vmag']) for h in H])
plx = np.array([float(h['Plx']) if h['Plx'] else 0.1 for h in H]); plx[plx <= 0] = 0.1
def star_ecl(jd_tt):
    t = Time(jd_tt, format='jd', scale='tt')
    c = SkyCoord(ra=[float(h['RAICRS']) for h in H]*u.deg, dec=[float(h['DEICRS']) for h in H]*u.deg,
                 pm_ra_cosdec=[float(h['pmRA'] or 0) for h in H]*u.mas/u.yr,
                 pm_dec=[float(h['pmDE'] or 0) for h in H]*u.mas/u.yr,
                 distance=(1000/plx)*u.pc, radial_velocity=0*u.km/u.s,
                 obstime=Time(2448349.0625, format='jd', scale='tt'), frame='icrs')
    e = c.apply_space_motion(new_obstime=t).transform_to(GeocentricMeanEcliptic(equinox=t, obstime=t))
    return e.lon.deg, e.lat.deg

def uranus(path):
    L = open(path).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
    a = np.array([[float(x.split(',')[1]), float(x.split(',')[6]), float(x.split(',')[8]), float(x.split(',')[9])] for x in L])
    return a  # jd, SOT, lon, lat

def run(jd0, ufile, label):
    slon, slat = star_ecl(jd0)
    idx = {h: i for i, h in enumerate(hip)}
    C = [e for e in P if e['I'] == '1' and e['HIP'] in idx and abs(e['bet']) <= 10 and e['P'] != 513]
    dl = np.array([wrap(e['lam'] - slon[idx[e['HIP']]]) for e in C]); db = np.array([e['bet'] - slat[idx[e['HIP']]] for e in C])
    dL, dB = float(np.median(dl)), float(np.median(db))
    res = {e['P']: float(sep(e['lam']-dL, e['bet']-dB, slon[idx[e['HIP']]], slat[idx[e['HIP']]])) for e in C}
    R = np.array([res[e['P']] for e in C if e['VP'] and e['VP'] >= 5])
    U = uranus(ufile); Ug = U[U[:, 1] >= 120]
    e513 = next(e for e in P if e['P'] == 513)
    x, y = e513['lam'] - dL, e513['bet'] - dB
    dstar = sep(x, y, slon, slat); bright = V <= 6.0
    j = np.argmin(np.where(bright, dstar, 99)); r_star = float(dstar[j])
    du = sep(x, y, Ug[:, 2], Ug[:, 3]); k = int(np.argmin(du)); d_U = float(du[k])
    pct = lambda v: float(100 * np.mean(R <= v))
    band = [e for e in C if abs(e['bet']) <= 3]
    dUb = np.array([sep(e['lam']-dL, e['bet']-dB, Ug[:, 2], Ug[:, 3]).min() for e in band])
    rng = np.random.default_rng(20261128); pick = rng.choice(len(Ug), 200)
    inj = [float(sep(Ug[i, 2], Ug[i, 3], Ug[:, 2], Ug[:, 3]).min()) * 60 for i in pick]
    # consistency with Verbunt & van Gent dist
    from scipy.stats import spearmanr
    vv = [(res[e['P']], float(e['dist'])) for e in C if e['dist']]
    rho = float(spearmanr([a for a, b in vv], [b for a, b in vv])[0])
    r76 = float(dstar[idx[66098]])
    return dict(label=label, jd0=jd0, n_C=len(C), dL_deg=dL, dB_deg=dB, n_R=len(R),
                R_median_arcmin=float(np.median(R))*60, R_p95_arcmin=float(np.percentile(R, 95))*60,
                e513_frame=[x, y], r_star_arcmin=r_star*60, r_star_HIP=int(hip[j]), r_star_V=float(V[j]),
                r_76Vir_arcmin=r76*60, d_U_arcmin=d_U*60, d_U_jd=float(Ug[k, 0]), d_U_SOT=float(Ug[k, 1]),
                uranus_at_best=[float(Ug[k, 2]), float(Ug[k, 3])], Q_S=pct(r_star), Q_U=pct(d_U), Q_76Vir=pct(r76),
                n_band=len(band), F=float(np.mean(dUb <= d_U)), n_band_match=int(np.sum(dUb <= d_U)),
                injection_max_arcmin=max(inj), spearman_vs_VvG=rho, n_uranus_days=len(Ug))

out_d = {'hipparchus': run(1674487.5, f"{raw}/uranus_hipparchus.txt", 'Hipparchus window'),
         'ptolemy': run(1771088.5, f"{raw}/uranus_ptolemy.txt", 'Ptolemy window (secondary)')}
h = out_d['hipparchus']
if h['Q_S'] > 95 and h['Q_U'] <= 50: v = 'SUPPORT'
elif h['Q_S'] <= h['Q_U'] or h['Q_U'] > 95: v = 'REFUTE'
else: v = 'INCONCLUSIVE'
out_d['verdict'] = v
json.dump(out_d, open(out, 'w'), indent=1); print(json.dumps(out_d, indent=1))
