"""Addendum 1 of PROTOCOL.md: censored forward model of the held-out ZTF zr data, DRW amplitude scan over the
paper's published posterior, placebo calibration, depth diagnostics, other periods.
Called by rerun.py (function addendum). Inputs: the quasar light curve (2.2 arcsec cone) and the 0.08 deg zr cone."""
import csv, io, json, collections
import numpy as np

CUT, END, TAU0, P0 = 58927.0, 60970.0, 716.0, 1466.0
QSO = ('402215400006773', '1446205400014195')
K_DET, NMOCK, SEED = 4.0, 4000, 20261128
F = lambda m: 10 ** (-0.4 * (np.asarray(m) - 21.0))


def quad_index(rows):
    """(field, ccd, quadrant) -> expid -> rows, post cutoff."""
    ix = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if float(r['mjd']) > CUT:
            ix[(r['field'], r['ccdid'], r['qid'])][r['expid']].append(r)
    return ix


def epochs(ix, rows, oids):
    """Good post-cutoff exposures of the quadrants of the given objects (one group per object), sorted by time.
    Good: at least 5 other objects with catflags = 0. Exposures where the object's row is flagged are dropped."""
    out = []
    for gi, qo in enumerate(oids):
        q = {r['expid']: r for r in rows if r['oid'] == qo and float(r['mjd']) > CUT}
        key = next((r['field'], r['ccdid'], r['qid']) for r in rows if r['oid'] == qo)
        for e, v in ix[key].items():
            if sum(x['catflags'] == '0' and x['oid'] not in oids for x in v) < 5:
                continue
            if e in q and q[e]['catflags'] != '0':
                continue
            det = e in q
            out.append((float(v[0]['mjd']), float(v[0]['limitmag']), gi, det,
                        float(q[e]['mag']) if det else np.nan, float(q[e]['magerr']) if det else np.nan))
    a = np.array(sorted(out))
    return {'t': a[:, 0], 'L': a[:, 1], 'g': a[:, 2].astype(int), 'det': a[:, 3] > 0.5, 'mag': a[:, 4], 'err': a[:, 5]}


def tstat(M, W, X, G, ng):
    """Weighted LS coefficient of X in M = c_group + a X, rows = mocks. W = weights (0 for unlisted points)."""
    num = np.zeros(len(M)); den = np.zeros(len(M))
    for k in range(ng):
        gk = (G == k)[None, :] * W
        sw = gk.sum(1); sw = np.where(sw > 0, sw, 1)
        xb = (gk * X).sum(1) / sw; mb = (gk * M).sum(1) / sw
        dx = X - xb[:, None]
        num += (gk * dx * (M - mb[:, None])).sum(1); den += (gk * dx * dx).sum(1)
    return num / np.where(den > 0, den, np.nan)


def drw(t, sig, tau, rng, n):
    out = np.empty((n, len(t))); v = rng.normal(0, sig, n); out[:, 0] = v
    for i in range(1, len(t)):
        r = np.exp(-(t[i] - t[i - 1]) / tau)
        v = r * v + rng.normal(0, sig * np.sqrt(1 - r * r), n); out[:, i] = v
    return out


class Model:
    def __init__(self, E, k, x):
        self.E, self.k, self.x = E, k, x
        self.s = k * F(E['L']) / 5.0

    def mock(self, a, m0, sig, tau, rng, n):
        E = self.E
        mu = m0 + a * self.x + (drw(E['t'], sig, tau, rng, n) if sig > 0 else 0.0)
        f = F(mu) + self.s * rng.normal(size=(n, len(E['t'])))
        det = f / self.s >= K_DET
        fs = np.where(det, f, 1.0)
        mag = np.where(det, 21.0 - 2.5 * np.log10(fs), np.nan)
        err = np.where(det, 1.0857 * self.s / fs, np.nan)
        return mag, err, det

    def T(self, mag, err, det):
        W = np.where(det, 1 / np.where(det, err, 1) ** 2, 0.0)
        return tstat(np.nan_to_num(mag), W, np.broadcast_to(self.x, mag.shape), self.E['g'], 2)

    def match_m0(self, a, sig, tau, ndet, seed):
        lo, hi = 19.5, 23.5
        for _ in range(22):
            mid = (lo + hi) / 2
            _, _, d = self.mock(a, mid, sig, tau, np.random.default_rng(seed), 600)
            lo, hi = (mid, hi) if d.sum(1).mean() > ndet else (lo, mid)
        return (lo + hi) / 2

    def run(self, a, sig, tau, ndet, seed, n=NMOCK):
        m0 = self.match_m0(a, sig, tau, ndet, seed)
        mag, err, det = self.mock(a, m0, sig, tau, np.random.default_rng(seed + 1), n)
        return m0, self.T(mag, err, det), mag, err, det


def resid_sd(mag, det, g):
    """sd of listed mags after subtracting the mean of each ZTF object, per row."""
    r = np.where(det, mag, np.nan).copy()
    for k in (0, 1):
        c = (g == k)[None, :] & det
        mk = np.nanmean(np.where(c, r, np.nan), axis=1)
        r = np.where(c, r - np.nan_to_num(mk)[:, None], r)
    return np.nanstd(r, axis=1)


def addendum(qso_raw, cone_raw, template_fn, drw_post):
    rows = [r for r in csv.DictReader(io.StringIO(cone_raw)) if float(r['mjd']) <= END]
    ix = quad_index(rows)
    E = epochs(ix, rows, QSO)
    det = E['det']; t, L, m, e, g = E['t'], E['L'], E['mag'], E['err'], E['g']
    # check against the protocol's data set (2.2 arcsec cone, zr, catflags 0, post cutoff)
    qrows = [r for r in csv.DictReader(io.StringIO(qso_raw)) if r['filtercode'] == 'zr' and r['catflags'] == '0' and CUT < float(r['mjd']) <= END]
    out = {'n_epochs': int(len(t)), 'n_epochs_402': int((g == 0).sum()), 'n_epochs_1446': int((g == 1).sum()),
           'n_listed': int(det.sum()), 'n_listed_protocol_file': len(qrows)}
    x = template_fn()(t)
    td, md, ed, Ld, gd = t[det], m[det], e[det], L[det], g[det]
    k = float(np.median(ed * F(md) / (1.0857 * F(Ld) / 5)))
    out['k_noise'] = k
    M = Model(E, k, x)
    T_obs = float(M.T(m[None], e[None], det[None])[0])
    out['T_obs'] = T_obs
    ndet = int(det.sum())
    bins = (0, 20.5, 21.0, 21.3, 21.6, 99)
    lb = np.digitize(L, bins) - 1
    out['detfrac_by_limitmag_obs'] = [round(float(det[lb == b].mean()), 3) for b in range(5)]
    out['limitmag_bins'] = list(bins)

    # depth diagnostics on the data
    dd = {}
    dd['corr_mag_limitmag'] = float(np.corrcoef(md, Ld)[0, 1])
    dd['slope_mag_limitmag'] = float(np.polyfit(Ld, md, 1)[0])
    def wls(mask, extra=None):
        cols = [x[det][mask]] + ([extra[mask]] if extra is not None else []) + [(gd[mask] == u).astype(float) for u in sorted(set(gd[mask]))]
        X = np.column_stack(cols); w = 1 / ed[mask]
        return float(np.linalg.lstsq(X * w[:, None], md[mask] * w, rcond=None)[0][0])
    allm = np.ones(ndet, bool)
    dd['T_with_limitmag_covariate'] = wls(allm, Ld)
    dd['T_limitmag_gt_21.3'] = wls(Ld > 21.3); dd['n_limitmag_gt_21.3'] = int((Ld > 21.3).sum())
    out['depth'] = dd

    # best-fit DRW of the paper and the main censored result
    tau_b, sig_b = 10 ** 2.9, 0.15
    def one(sig, tau, seed, n=NMOCK, model=M, xT=T_obs):
        m0s, Ts, mag1, err1, det1 = model.run(1.0, sig, tau, ndet, seed, n)
        m0n, Tn, _, _, _ = model.run(0.0, sig, tau, ndet, seed + 7, n)
        # a mock with fewer than 2 listed points per object has no T; it is dropped and counted
        nan_frac = float(np.mean(~np.isfinite(Ts)) / 2 + np.mean(~np.isfinite(Tn)) / 2)
        Ts, Tn = Ts[np.isfinite(Ts)], Tn[np.isfinite(Tn)]
        crit = np.quantile(Tn, 0.99)
        return {'sigma': sig, 'tau': round(tau, 1), 'm0_sig': round(m0s, 3), 'm0_null': round(m0n, 3), 'frac_no_T': nan_frac,
                'p_sig': float(np.mean(Ts <= xT)), 'p_null': float(np.mean(Tn >= xT)),
                'median_T_sig': float(np.median(Ts)), 'sd_T_sig': float(np.std(Ts)), 'sd_T_null': float(np.std(Tn)),
                'power': float(np.mean(Ts >= crit))}, Ts, (mag1, det1)
    best, Ts_best, (mag1, det1) = one(sig_b, tau_b, SEED)
    Ts_best = Ts_best[np.isfinite(Ts_best)]
    # model checks at the best fit (a = 1 mocks)
    best['detfrac_by_limitmag_mock'] = [round(float(det1[:, lb == b].mean()), 3) for b in range(5)]
    sl = [np.polyfit(L[det1[i]], mag1[i, det1[i]], 1)[0] for i in range(300)]
    best['slope_mag_limitmag_mock_median'] = float(np.median(sl))
    out['best_fit_drw'] = best

    # tau = 716 sigma grid
    out['grid_tau716'] = [one(s, TAU0, SEED + 100 + i)[0] for i, s in enumerate((0.10, 0.119, 0.13, 0.15, 0.17, 0.20, 0.25, 0.30))]

    # published posterior contours
    cont = {}
    for name, npt in (('c95', 24), ('c68', 12)):
        lt, s = np.array(drw_post[name]['log10_tau']), np.array(drw_post[name]['sigma'])
        idx = np.linspace(0, len(lt) - 1, npt, endpoint=False).astype(int)
        res = []
        for j, i in enumerate(idx):
            r = one(float(s[i]), float(10 ** lt[i]), SEED + 1000 + 50 * j + (0 if name == 'c95' else 7), n=2000)[0]
            res.append([round(float(lt[i]), 3), round(float(s[i]), 3), r['p_sig'], round(r['median_T_sig'], 3), round(r['power'], 3)])
        cont[name] = {'cols': ['log10_tau', 'sigma', 'p_sig', 'median_T_sig', 'power'], 'rows': res,
                      'max_p_sig': max(r[2] for r in res)}
    out['posterior_contours'] = cont

    # data-based sigma (tau = 716): match sd of listed mags after per-object means
    sd_obs = float(resid_sd(m[None], det[None], g)[0]); out['sd_listed_obs'] = sd_obs
    est = {}
    for a in (0.0, 1.0):
        grid = np.arange(0.0, 0.41, 0.02); sds = []
        for s in grid:
            m0 = M.match_m0(a, s, TAU0, ndet, SEED + 5)
            mg, _, dt = M.mock(a, m0, s, TAU0, np.random.default_rng(SEED + 6), 800)
            sds.append(float(np.median(resid_sd(mg, dt, g))))
        sds = np.array(sds)
        est['a%d' % a] = {'sigma_grid': [round(v, 2) for v in grid], 'median_sd_listed': [round(v, 4) for v in sds],
                          'sigma_match': float(np.interp(sd_obs, sds, grid)) if sds.min() <= sd_obs <= sds.max() else None}
    out['data_sigma'] = est

    # placebo calibration (verifier's selection: field 402 objects, >= 40 held-out points, median mag 20.6-21.2)
    by = collections.defaultdict(list)
    for r in rows:
        if r['catflags'] == '0' and float(r['mjd']) > CUT and r['oid'] not in QSO:
            by[r['oid']].append(r)
    zs, pl = [], []
    for j, (oid, v) in enumerate(sorted(by.items())):
        if not oid.startswith('4022') or len(v) < 40:
            continue
        if not 20.6 <= np.median([float(r['mag']) for r in v]) <= 21.2:
            continue
        Eo = epochs(ix, rows, (oid,))
        d = Eo['det']
        if d.sum() < 40:
            continue
        xo = template_fn()(Eo['t'])
        ko = float(np.median(Eo['err'][d] * F(Eo['mag'][d]) / (1.0857 * F(Eo['L'][d]) / 5)))
        Mo = Model(Eo, ko, xo)
        To = float(Mo.T(Eo['mag'][None], Eo['err'][None], d[None])[0])
        _, Tm, _, _, _ = Mo.run(0.0, 0.0, TAU0, int(d.sum()), SEED + 3000 + j, n=1000)
        Tm = Tm[np.isfinite(Tm)]
        z = (To - np.median(Tm)) / np.std(Tm)
        sh = float(np.median([float(r['sharp']) for r in v]))
        zs.append(z); pl.append([oid, int(d.sum()), round(float(np.median(Eo['mag'][d])), 3), round(To, 3), round(float(np.std(Tm)), 3), round(float(z), 3), round(sh, 3)])
    zs = np.array(zs)
    rsd = float(1.4826 * np.median(np.abs(zs - np.median(zs))))
    out['placebo'] = {'n_objects': len(zs), 'z_sd': float(np.std(zs)), 'z_robust_sd': rsd, 'z_median': float(np.median(zs)),
                      'cols': ['oid', 'n', 'median_mag', 'T', 'sd_T_mock', 'z', 'median_sharp'], 'rows': pl}
    infl = rsd if rsd > 1.2 else None
    out['inflation_factor'] = infl
    if infl:
        med = np.median(Ts_best)
        out['best_fit_drw']['p_sig_inflated'] = float(np.mean(med + infl * (Ts_best - med) <= T_obs))
        # post hoc sensitivity, not part of the decision: inflate only the white-noise part of the T scatter
        _, Tw, _, _, _ = M.run(1.0, 0.0, TAU0, ndet, SEED + 11)
        sdw = float(np.std(Tw[np.isfinite(Tw)]))
        extra = np.sqrt(infl ** 2 - 1) * sdw * np.random.default_rng(SEED + 12).normal(size=len(Ts_best))
        out['best_fit_drw']['sd_T_white_only'] = sdw
        out['best_fit_drw']['p_sig_inflated_white_part_only_posthoc'] = float(np.mean(Ts_best + extra <= T_obs))

    # other periods (descriptive), censored model at the best-fit DRW
    per = []
    for i, PP in enumerate((1454.0, 1476.0, 1506.0, 1511.0, 1530.0, 1562.0, 1604.0, 1607.0)):
        xp = template_fn(PP)(t); Mp = Model(E, k, xp)
        Tp = float(Mp.T(m[None], e[None], det[None])[0])
        r = one(sig_b, tau_b, SEED + 5000 + 10 * i, n=2000, model=Mp, xT=Tp)[0]
        per.append([PP, round(Tp, 4), r['p_sig'], r['p_null'], round(r['median_T_sig'], 3)])
    out['other_periods'] = {'cols': ['P', 'T_obs', 'p_sig', 'p_null', 'median_T_sig'], 'rows': per}
    return out
