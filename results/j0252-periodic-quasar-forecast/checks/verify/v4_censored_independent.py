"""Verifier round 2, check: independent implementation of the censored forward model of PROTOCOL.md Addendum 1.
Written from the addendum text, not from checks/censored.py. Statistic by numpy lstsq, one mock at a time.
Usage: v4_censored_independent.py <cone.csv (0.08 deg, zr)> <model_r_digitized.json>"""
import csv, json, sys, collections
import numpy as np

cone, modelf = sys.argv[1], sys.argv[2]
P, CUT, END = 1466.0, 58927.0, 60970.0  # END added in the write stage: fixed analysis window
QSO = {'402215400006773': 0, '1446205400014195': 1}
d = json.load(open(modelf)); tm, mm = np.array(d['mjd']), np.array(d['mag'])
b = np.minimum(((tm % P) / P * 50).astype(int), 49)
med = np.array([np.median(mm[b == k]) for k in range(50)]); med -= med.mean(); cen = (np.arange(50) + 0.5) / 50
tpl = lambda t: np.interp((t % P) / P, np.r_[cen - 1, cen, cen + 1], np.tile(med, 3))
Fl = lambda m: 10 ** (-0.4 * (np.asarray(m, float) - 21.0))

rows = [r for r in csv.DictReader(open(cone)) if CUT < float(r['mjd']) <= END and r['filtercode'] == 'zr']
quad = {}
for r in rows:
    if r['oid'] in QSO:
        quad[(r['field'], r['ccdid'], r['qid'])] = QSO[r['oid']]
print('quasar quadrants', quad)
exp = collections.defaultdict(list)
for r in rows:
    key = (r['field'], r['ccdid'], r['qid'])
    if key in quad:
        exp[(quad[key], r['expid'])].append(r)


def build(target):
    """target: dict oid -> group. Returns arrays over good exposures."""
    T = []
    for (g, e), v in exp.items():
        if g not in target.values():
            continue
        others = sum(1 for r in v if r['oid'] not in target and r['catflags'] == '0')
        if others < 5:
            continue
        me = [r for r in v if r['oid'] in target and target[r['oid']] == g]
        if me and me[0]['catflags'] != '0':
            continue
        T.append((float(v[0]['mjd']), float(v[0]['limitmag']), g, 1 if me else 0,
                  float(me[0]['mag']) if me else np.nan, float(me[0]['magerr']) if me else np.nan))
    a = np.array(sorted(T))
    return a[:, 0], a[:, 1], a[:, 2].astype(int), a[:, 3] > 0, a[:, 4], a[:, 5]


def Tfit(t_x, m, e, g):
    cols = [t_x] + [(g == u).astype(float) for u in np.unique(g)]
    X = np.column_stack(cols); w = 1 / e
    return np.linalg.lstsq(X * w[:, None], m * w, rcond=None)[0][0]


def drw(t, sig, tau, rng, n):
    out = np.zeros((n, len(t)))
    if sig == 0:
        return out
    v = rng.normal(0, sig, n); out[:, 0] = v
    for i in range(1, len(t)):
        r = np.exp(-(t[i] - t[i - 1]) / tau)
        v = r * v + np.sqrt(1 - r * r) * sig * rng.normal(size=n); out[:, i] = v
    return out


def sim(t, L, g, x, k, a, sig, tau, ntarget, rng, n):
    s = k * Fl(L) / 5
    D = drw(t, sig, tau, rng, n); Z = rng.normal(size=(n, len(t)))
    def listed(m0):
        f = Fl(m0 + a * x + D) + s * Z
        return f, f / s >= 4
    lo, hi = 19.0, 24.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if listed(mid)[1].sum(1).mean() > ntarget: lo = mid
        else: hi = mid
    m0 = (lo + hi) / 2
    f, det = listed(m0)
    Ts = np.full(n, np.nan)
    for i in range(n):
        dd = det[i]
        if min(np.bincount(g[dd], minlength=g.max() + 1)[np.unique(g)]) < 2:
            continue
        mag = 21 - 2.5 * np.log10(f[i, dd]); err = 1.0857 * s[dd] / f[i, dd]
        Ts[i] = Tfit(x[dd], mag, err, g[dd])
    return m0, Ts[np.isfinite(Ts)], det, f


t, L, g, det, m, e = build(QSO)
x = tpl(t)
k = np.median(e[det] * Fl(m[det]) / (1.0857 * Fl(L[det]) / 5))
Tobs = Tfit(x[det], m[det], e[det], g[det])
print('exposures', len(t), 'by group', np.bincount(g), 'listed', det.sum(), 'k %.3f' % k, 'T_obs %.4f' % Tobs)
print('min S/N of listed points %.2f' % (1.0857 / e[det]).min())
deep = L > 21.6
print('deep exposures (limitmag > 21.6):', deep.sum(), 'listed', (deep & det).sum())
print('  MJD of deep non-detections:', np.round(t[deep & ~det]).astype(int).tolist())
print('  MJD of deep detections:', np.round(t[deep & det]).astype(int).tolist())
print('  template at deep non-det (mean) %.3f, at deep det %.3f' % (x[deep & ~det].mean(), x[deep & det].mean()))

N = 4000
rng = np.random.default_rng(424242)
res = {}
for name, tau, sig in (('paper best fit', 10 ** 2.9, 0.15), ('tau716 s0.15', 716., 0.15), ('tau716 s0.20', 716., 0.20), ('tau716 s0.25', 716., 0.25)):
    m1, T1, d1, _ = sim(t, L, g, x, k, 1.0, sig, tau, det.sum(), rng, N)
    m0, T0, d0, _ = sim(t, L, g, x, k, 0.0, sig, tau, det.sum(), rng, N)
    med1 = np.median(T1)
    print('%-15s m0(a=1) %.3f | median T %.3f sd %.3f | p_sig %.4f | p_null %.3f | power %.3f | p_sig x1.67 %.4f | x2.07 %.4f' % (
        name, m1, med1, T1.std(), np.mean(T1 <= Tobs), np.mean(T0 >= Tobs), np.mean(T1 >= np.quantile(T0, 0.99)),
        np.mean(med1 + 1.67 * (T1 - med1) <= Tobs), np.mean(med1 + 2.07 * (T1 - med1) <= Tobs)))
    if name == 'paper best fit':
        print('   listed fraction deep bin, mock %.3f' % d1[:, deep].mean())
        res['T1'] = T1

# placebo: z of each nearby object against its own sigma = 0 censored mocks
by = collections.defaultdict(list)
for r in rows:
    if r['catflags'] == '0' and r['oid'] not in QSO and r['oid'].startswith('4022'):
        by[r['oid']].append(float(r['mag']))
zs, Tp, ns = [], [], []
for oid, mags in sorted(by.items()):
    if len(mags) < 40 or not 20.6 <= np.median(mags) <= 21.2:
        continue
    to, Lo, go, do, mo, eo = build({oid: 0})
    if do.sum() < 40:
        continue
    xo = tpl(to)
    ko = np.median(eo[do] * Fl(mo[do]) / (1.0857 * Fl(Lo[do]) / 5))
    To = Tfit(xo[do], mo[do], eo[do], go[do])
    _, Tm, _, _ = sim(to, Lo, go, xo, ko, 0.0, 0.0, 716., do.sum(), rng, 500)
    zs.append((To - np.median(Tm)) / Tm.std()); Tp.append(To); ns.append(do.sum())
zs, Tp, ns = np.array(zs), np.array(Tp), np.array(ns)
rsd = 1.4826 * np.median(np.abs(zs - np.median(zs)))
print('placebo objects', len(zs), 'z median %.3f sd %.3f robust sd %.3f' % (np.median(zs), zs.std(), rsd))
print('placebo raw T: sd %.3f, robust sd %.3f, n with T <= T_obs: %d' % (Tp.std(), 1.4826 * np.median(np.abs(Tp - np.median(Tp))), (Tp <= Tobs).sum()))
sel = (ns >= 70) & (ns <= 130)
print('placebo with 70-130 points: n %d, raw T sd %.3f' % (sel.sum(), Tp[sel].std()))
# empirical alternative (post hoc, verifier): add the placebo T scatter of similar-n objects in quadrature to the DRW part
T1 = res['T1']; med1 = np.median(T1)
_, Tw, _, _ = sim(t, L, g, x, k, 1.0, 0.0, 716., det.sum(), rng, 2000)
sd_drw = np.sqrt(max(T1.std() ** 2 - Tw.std() ** 2, 0))
tot = np.sqrt(sd_drw ** 2 + Tp[sel].std() ** 2)
from math import erf, sqrt
zq = (Tobs - med1) / tot
print('white-only T sd %.3f, DRW part %.3f, placebo-based total sd %.3f, z %.2f, Gaussian p_sig %.4f' % (Tw.std(), sd_drw, tot, zq, 0.5 * (1 + erf(zq / sqrt(2)))))
