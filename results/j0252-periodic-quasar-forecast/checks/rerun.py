"""Download held-out ZTF data for SDSS J0252-0028 and run the pre-registered test in PROTOCOL.md.
Also runs Addendum 1 (censored forward model, checks/censored.py) on a 0.08 deg zr cone around the quasar.
Usage: rerun.py [--write]  (--write stores data/expected.json; default compares with it)."""
import sys, json, csv, io, urllib.request, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
URL = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%2043.061125%20-0.470472%200.0006&FORMAT=csv"
URL_CONE = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%2043.061125%20-0.470472%200.08&BANDNAME=r&FORMAT=csv"
P, TAU, CUT, NSIM, SEED = 1466.0, 716.0, 58927.0, 5000, 20261128
END = 60970.0  # end of the analysed window (last epoch MJD 60968.34); later ZTF releases do not change the result

def template_fn(P=P, lo=0, hi=1e9):
    d = json.load(open(ROOT / 'data/model_r_digitized.json'))
    t, m = np.array(d['mjd']), np.array(d['mag'])
    k = (t >= lo) & (t <= hi); t, m = t[k], m[k]
    ph = (t % P) / P
    bins = np.linspace(0, 1, 51); idx = np.digitize(ph, bins) - 1
    med = np.array([np.median(m[idx == k]) if np.any(idx == k) else np.nan for k in range(50)])
    ok = ~np.isnan(med); med = np.interp(np.arange(50), np.where(ok)[0], med[ok])
    med -= med.mean(); cen = (bins[:-1] + bins[1:]) / 2
    xp = np.concatenate([cen - 1, cen, cen + 1]); fp = np.tile(med, 3)
    return lambda tt, shift=0.0: np.interp(((tt % P) / P + shift) % 1.0, xp, fp)

_RAW = None
def load(band, lo=CUT, hi=END):
    global _RAW
    if _RAW is None:
        _RAW = urllib.request.urlopen(URL, timeout=120).read().decode()
        (ROOT / 'work').mkdir(exist_ok=True); (ROOT / 'work/ztf_raw.csv').write_text(_RAW)
    raw = _RAW
    rows = [r for r in csv.DictReader(io.StringIO(raw)) if r['filtercode'] == band and r['catflags'] == '0' and lo < float(r['mjd']) <= hi]
    t = np.array([float(r['mjd']) for r in rows]); m = np.array([float(r['mag']) for r in rows])
    e = np.array([float(r['magerr']) for r in rows]); oid = np.array([r['oid'] for r in rows])
    return t, m, e, oid

def coef(m, e, oid, x):
    # weighted LS: m = c_oid + a*x ; returns a
    u = sorted(set(oid)); X = np.column_stack([x] + [(oid == k).astype(float) for k in u])
    w = 1 / e; sol = np.linalg.lstsq(X * w[:, None], m * w, rcond=None)[0]
    return sol[0]

def drw(t, sig, rng, n, TAU=TAU):
    o = np.argsort(t); ts = t[o]; out = np.empty((n, len(t)))
    x = rng.normal(0, sig, n)
    out[:, o[0]] = x
    for i in range(1, len(ts)):
        r = np.exp(-(ts[i] - ts[i-1]) / TAU)
        x = r * x + rng.normal(0, sig * np.sqrt(1 - r * r), n); out[:, o[i]] = x
    return out

def run(band):
    tpl = template_fn(); t, m, e, oid = load(band)
    x = tpl(t); T = coef(m, e, oid, x)
    sig = np.sqrt(max(np.var(m) - np.mean(e**2), 0.01**2))
    rng = np.random.default_rng(SEED)
    D = drw(t, sig, rng, NSIM); N = rng.normal(0, 1, (NSIM, len(t))) * e
    Tn = np.array([coef(D[k] + N[k], e, oid, x) for k in range(NSIM)])
    Ts = np.array([coef(D[k] + N[k] + x, e, oid, x) for k in range(NSIM)])
    crit = np.quantile(Tn, 0.99)
    scan = [float(coef(m, e, oid, tpl(t, s))) for s in np.arange(0, 1, 0.05)]
    rank = int(1 + sum(v > scan[0] for v in scan))
    return {'band': band, 'n_points': int(len(t)), 'n_oid': len(set(oid)), 'mjd_min': float(t.min()), 'mjd_max': float(t.max()),
            'template_ptp_mag': float(x.max() - x.min()), 'sigma_drw': float(sig), 'T_obs': float(T),
            'p_null': float(np.mean(Tn >= T)), 'p_sig': float(np.mean(Ts <= T)),
            'null_T_q01_q50_q99': [float(np.quantile(Tn, q)) for q in (0.01, 0.5, 0.99)],
            'sig_T_q01_q50_q99': [float(np.quantile(Ts, q)) for q in (0.01, 0.5, 0.99)],
            'power_at_0.01': float(np.mean(Ts >= crit)),
            'phase_scan_T': [round(v, 4) for v in scan], 'phase_rank_of_zero': rank,
            'best_phase_shift': float(np.arange(0, 1, 0.05)[int(np.argmax(scan))])}

def robustness():
    """Post-hoc checks (not pre-registered): positive control on pre-cutoff ZTF data, other periods, other template windows."""
    out = {}
    t, m, e, oid = load('zr', 0, CUT)
    out['control_preCUT_zr_T'] = float(coef(m, e, oid, template_fn()(t))); out['control_preCUT_zr_n'] = int(len(t))
    t, m, e, oid = load('zr')
    for PP in (1454.0, 1476.0, 1530.0, 1607.0):
        out[f'T_zr_P{int(PP)}'] = float(coef(m, e, oid, template_fn(PP)(t)))
    out['T_zr_last_cycle_template'] = float(coef(m, e, oid, template_fn(P, 58889 - P, 58889)(t)))
    sig = np.sqrt(max(np.var(m) - np.mean(e**2), 0.01**2)); x = template_fn()(t)
    for tau in (300.0, 1500.0):
        rng = np.random.default_rng(SEED); D = drw(t, sig, rng, 2000, tau); N = rng.normal(0, 1, (2000, len(t))) * e
        Ts = np.array([coef(D[k] + N[k] + x, e, oid, x) for k in range(2000)])
        out[f'p_sig_tau{int(tau)}'] = float(np.mean(Ts <= coef(m, e, oid, x)))
    rng = np.random.default_rng(SEED); D = drw(t, sig, rng, 2000); N = rng.normal(0, 1, (2000, len(t))) * e
    scan = []
    for PP in np.arange(1400.0, 1701.0, 10.0):
        xx = template_fn(PP)(t); To = coef(m, e, oid, xx)
        Tn = np.array([coef(D[k] + N[k], e, oid, xx) for k in range(2000)])
        scan.append([float(PP), round(float(To), 4), float(np.mean(Tn >= To)), float(np.mean(Tn + 1 <= To))])
    out['period_scan_P_T_pnull_psig'] = scan
    return out

def same(a, v):
    if isinstance(v, dict):
        return isinstance(a, dict) and set(a) == set(v) and all(same(a[k], v[k]) for k in v)
    if isinstance(v, list):
        return isinstance(a, list) and len(a) == len(v) and all(same(x, y) for x, y in zip(a, v))
    if v is None or isinstance(v, (str, bool)):
        return a == v
    return bool(np.allclose(a, v, rtol=1e-6, atol=1e-9, equal_nan=True))

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent)); import censored
    res = {b: run(b) for b in ('zr', 'zg')}
    res['robustness'] = robustness()
    cone = urllib.request.urlopen(URL_CONE, timeout=600).read().decode()
    (ROOT / 'work/placebo').mkdir(parents=True, exist_ok=True); (ROOT / 'work/placebo/cone.csv').write_text(cone)
    res['addendum1'] = censored.addendum(_RAW, cone, template_fn, json.load(open(ROOT / 'data/drw_posterior_r.json')))
    res = json.loads(json.dumps(res))
    print(json.dumps(res, indent=1))
    f = ROOT / 'data/expected.json'
    if '--write' in sys.argv:
        json.dump(res, open(f, 'w'), indent=1); print('written')
    else:
        exp = json.load(open(f)); ok = True
        for b in exp:
            for k, v in exp[b].items():
                if not same(res[b].get(k), v): ok = False; print('MISMATCH', b, k, v, res[b].get(k))
        print('OK' if ok else 'FAIL'); sys.exit(0 if ok else 1)
