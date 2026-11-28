"""Download ZTF data for SDSS J0159+0105 and run the pre-registered test in PROTOCOL.md.
Usage: rerun.py [--write] [--cache]
  --write  store data/expected.json (default: compare with it)
  --cache  use work/ztf_raw.csv and work/src/src.tgz instead of fresh downloads"""
import sys, json, csv, io, re, tarfile, hashlib, urllib.request, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
URL = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%2029.791908%201.087369%200.0006&FORMAT=csv"
P, T0, AMP, TAU, NSIM, SEED = 741.0, 53413.09, 0.1, 210.0, 5000, 20261128
BANDS = ('zg', 'zr')
SRC_URL = "https://arxiv.org/src/1512.08730"
SEED2 = 20261129
MJD_END = 60970.0   # write stage: last epoch of the analysed data is MJD 60969.34; later ZTF epochs are ignored


def template(t, P=P, shift=0.0):
    return AMP * np.sin(2 * np.pi * ((t - T0) / P - shift))


def raw_csv():
    f = ROOT / 'work/ztf_raw.csv'
    if '--cache' in sys.argv and f.exists():
        return f.read_text()
    raw = urllib.request.urlopen(URL, timeout=180).read().decode()
    f.parent.mkdir(exist_ok=True); f.write_text(raw)
    return raw


def load(raw, bands=BANDS):
    rows = [r for r in csv.DictReader(io.StringIO(raw)) if r['filtercode'] in bands and r['catflags'] == '0'
            and float(r['mjd']) <= MJD_END]
    t = np.array([float(r['mjd']) for r in rows]); m = np.array([float(r['mag']) for r in rows])
    e = np.array([float(r['magerr']) for r in rows]); oid = np.array([r['oid'] for r in rows])
    return t, m, e, oid


def design(oid):
    u = sorted(set(oid)); return np.column_stack([(oid == k).astype(float) for k in u])


def lsq(m, e, Xo, cols):
    X = np.column_stack(cols + [Xo]); w = 1 / e
    return np.linalg.lstsq(X * w[:, None], m * w, rcond=None)[0]


def coef(m, e, Xo, x):
    return lsq(m, e, Xo, [x])[0]


def coef_many(M, e, Xo, x):
    """Fitted a for each row of M (same design), via one projection."""
    X = np.column_stack([x, Xo]); w = 1 / e
    pinv = np.linalg.pinv(X * w[:, None])
    return (M * w) @ pinv[0]


def drw(t, sig, rng, n, tau):
    o = np.argsort(t); ts = t[o]; out = np.empty((n, len(t)))
    x = rng.normal(0, sig, n); out[:, o[0]] = x
    for i in range(1, len(ts)):
        r = np.exp(-(ts[i] - ts[i - 1]) / tau)
        x = r * x + rng.normal(0, sig * np.sqrt(1 - r * r), n); out[:, o[i]] = x
    return out


def sims(t, e, Xo, x, sig, tau, n=NSIM):
    rng = np.random.default_rng(SEED)
    D = drw(t, sig, rng, n, tau); N = rng.normal(0, 1, (n, len(t))) * e
    return coef_many(D + N, e, Xo, x), coef_many(D + N + x, e, Xo, x)


def free_phase(t, m, e, Xo, PP):
    s, c = np.sin(2 * np.pi * (t - T0) / PP), np.cos(2 * np.pi * (t - T0) / PP)
    a, b = lsq(m, e, Xo, [s, c])[:2]
    # a*sin + b*cos = A*sin(2pi((t-T0)/P) + phi); phase shift in cycles relative to the published curve
    return float(np.hypot(a, b)), float((np.arctan2(b, a) / (2 * np.pi)) % 1.0)


def lc_eps():
    f = ROOT / 'work/src/src.tgz'
    if not ('--cache' in sys.argv and f.exists()):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(urllib.request.urlopen(SRC_URL, timeout=180).read())
    with tarfile.open(f) as tf:
        return tf.extractfile('lc.eps').read()


def crts_points(eps):
    """Panel (a) of Fig. 1 of the paper: raw CRTS diamonds and the green fit curve, in (MJD, V)."""
    body = eps.decode('latin-1').split('(Catalina V-band Light-Curve)')[0]
    body = body[body.index('%%EndPageSetup'):].replace('\n', ' ')
    X = lambda x: 54000 + (x - 4554) * 500.0 / (8431 - 4554)
    Y = lambda y: 16.7 - (y - 12839) * 0.5 / (14437 - 12839)
    parts = re.split(r'([\d.]+ [\d.]+ [\d.]+) setrgbcolor', body)
    dia, green = [], None
    for col, txt in zip(parts[1::2], parts[2::2]):
        if col == '0.000 0.000 0.000':
            for a, b in re.findall(r'(\d+) (\d+) M 111 -111 R -111 -111 R -111 111 R 111 111 R D', txt):
                dia.append((X(int(a)), Y(int(b) - 111)))
        elif col == '0.000 1.000 0.000' and green is None:
            tok = re.findall(r'(-?\d+) (-?\d+) ([MR])', txt)
            x0, y0 = int(tok[0][0]), int(tok[0][1]); pts = [(x0, y0)]
            for a, b, k in tok[1:]:
                if k == 'M': break
                x0 += int(a); y0 += int(b); pts.append((x0, y0))
            green = np.array([(X(x), Y(y)) for x, y in pts])
    return np.array(dia), green


def sin_basis(tt, PP):
    ph = 2 * np.pi * (tt - T0) / PP
    return np.column_stack([np.sin(ph), np.cos(ph), np.ones_like(tt)])


def resid_oid(Y, e, oid_idx, k):
    """Remove the weighted mean per oid from each row of Y (weights 1/e^2)."""
    w2 = 1 / e ** 2; out = Y.copy()
    for j in range(k):
        s = oid_idx == j
        out[..., s] -= (Y[..., s] * w2[s]).sum(-1, keepdims=True) / w2[s].sum()
    return out


def addendum1(t, m, e, Xo, sig, T, A_ztf):
    eps = lc_eps(); r = {'lc_eps_sha256': hashlib.sha256(eps).hexdigest()}
    dia, green = crts_points(eps)
    r['green_curve_n_vertices'] = int(len(green))
    r['green_curve_max_abs_dev_from_formula_mag'] = float(np.max(np.abs(green[:, 1] - 16.59 - template(green[:, 0]))))
    tc, mc = dia[:, 0], dia[:, 1]
    r['crts_n_points'] = int(len(tc)); r['crts_mjd_range'] = [float(tc.min()), float(tc.max())]
    one = np.ones_like(tc)
    r['T_crts_all'] = float(np.linalg.lstsq(np.column_stack([template(tc), one]), mc, rcond=None)[0][0])
    good = np.abs(mc - np.median(mc)) < 0.3; r['crts_n_outliers'] = int((~good).sum())
    tc, mc = tc[good], mc[good]
    r['T_crts_clean'] = float(np.linalg.lstsq(np.column_stack([template(tc), np.ones_like(tc)]), mc, rcond=None)[0][0])
    b = np.linalg.lstsq(sin_basis(tc, P), mc, rcond=None)[0]
    r['crts_free_phase_P741'] = {'amplitude_mag': float(np.hypot(b[0], b[1])),
                                 'phase_shift_cycles': float(((np.arctan2(b[1], b[0]) / (2 * np.pi)) + 0.5) % 1.0 - 0.5)}
    Pg = np.arange(600.0, 900.5, 2.0)
    BAS = [sin_basis(tc, PP) for PP in Pg]; PIN = [np.linalg.pinv(B) for B in BAS]; BZ = [sin_basis(t, PP)[:, :2] for PP in Pg]

    def refit(Yc):   # Yc: (n, Nc) -> period index and coefficients per row
        Yc = np.atleast_2d(Yc); best = np.full(len(Yc), np.inf); jb = np.zeros(len(Yc), int); cb = np.zeros((len(Yc), 3))
        for j in range(len(Pg)):
            c = Yc @ PIN[j].T; rss = ((Yc - c @ BAS[j].T) ** 2).sum(1); s = rss < best
            best[s], jb[s], cb[s] = rss[s], j, c[s]
        return jb, cb, best
    jb, cb, rss = refit(mc)
    oid_idx = np.argmax(Xo, 1); k = Xo.shape[1]; w2 = 1 / e ** 2
    mres = resid_oid(m, e, oid_idx, k)

    def Ccoef(Yres, F):   # Yres, F: (n, N); Yres already oid-residualized
        Fr = resid_oid(F, e, oid_idx, k)
        return (Fr * Yres * w2).sum(1) / (Fr * Fr * w2).sum(1)
    j0 = int(jb[0]); A_c = float(np.hypot(*cb[0, :2]))
    Fobs = BZ[j0] @ cb[0, :2]; C_obs = float(Ccoef(mres[None], Fobs[None])[0])
    resc = mc - BAS[j0] @ cb[0]
    night = np.floor(tc + 0.5).astype(int)
    v = [(np.sum((resc[night == n] - resc[night == n].mean()) ** 2), (night == n).sum() - 1) for n in set(night) if (night == n).sum() > 1]
    wn = float(np.sqrt(sum(a for a, _ in v) / sum(d for _, d in v)))
    sig_c = float(np.sqrt(max(np.var(resc) - wn ** 2, 1e-6)))
    r['crts_refit'] = {'P': float(Pg[j0]), 'amplitude_mag': A_c, 'rss': float(rss[0]),
                       'rss_at_741': float(((mc - BAS[int(np.argmin(abs(Pg - 741)))] @ PIN[int(np.argmin(abs(Pg - 741)))] @ mc) ** 2).sum()),
                       'rss_const': float(((mc - mc.mean()) ** 2).sum()), 'resid_rms': float(resc.std()),
                       'intra_night_rms': wn, 'sigma_drw_crts': sig_c}
    r['C_obs'] = C_obs
    # A3: period scan with a CRTS refit at each period
    scan = []
    for PP in np.arange(680.0, 811.0, 10.0):
        B = sin_basis(tc, PP); c = np.linalg.lstsq(B, mc, rcond=None)[0]
        F = sin_basis(t, PP)[:, :2] @ c[:2]
        scan.append([float(PP), round(float(Ccoef(mres[None], F[None])[0]), 4), round(float(((mc - B @ c) ** 2).sum()), 4),
                     round(float(np.hypot(c[0], c[1])), 4)])
    r['refit_scan_P_C_rss_amp'] = scan
    # A2: refit-world forward test
    rng = np.random.default_rng(SEED2); n = 2000
    dtc = np.abs(tc[:, None] - tc[None, :]); dtz = np.abs(t[:, None] - t[None, :])
    worlds = {}
    cases = [(a, sc, tau) for a in (0.1, A_c) for sc in (sig_c, sig) for tau in (210.0, 500.0)] + [(0.0, sig_c, 210.0)]
    for a, sc, tau in cases:
        Lc = np.linalg.cholesky(sc ** 2 * np.exp(-dtc / tau) + wn ** 2 * np.eye(len(tc)))
        Lz = np.linalg.cholesky(sig ** 2 * np.exp(-dtz / tau) + np.diag(e ** 2))
        Yc = 16.59 + a * np.sin(2 * np.pi * (tc - T0) / P) + (Lc @ rng.standard_normal((len(tc), n))).T
        Yz = a * np.sin(2 * np.pi * (t - T0) / P) + (Lz @ rng.standard_normal((len(t), n))).T
        jj, cc, _ = refit(Yc)
        F = np.stack([BZ[j] @ c[:2] for j, c in zip(jj, cc)])
        Cm = Ccoef(resid_oid(Yz, e, oid_idx, k), F)
        name = f'A{a:.3f}_sigc{sc:.3f}_tau{int(tau)}'
        worlds[name] = {'p_persist': float(np.mean(Cm <= C_obs)), 'frac_C_le_0': float(np.mean(Cm <= 0)),
                        'C_q01_q50_q99': [float(np.quantile(Cm, q)) for q in (0.01, 0.5, 0.99)],
                        'sd_P_hat': float(np.std(Pg[jj]))}
    r['refit_worlds'] = worlds
    sig_worlds = [v['p_persist'] for kk, v in worlds.items() if not kk.startswith('A0.000')]
    r['p_persist_min_max'] = [min(sig_worlds), max(sig_worlds)]
    r['persistent_sinusoid_refuted'] = bool(max(sig_worlds) < 0.01)
    # A4: power of the pre-registered test at the CRTS amplitude
    x = template(t); Tn, Ts = sims(t, e, Xo, x, sig, TAU); crit = np.quantile(Tn, 0.99); s = A_c / AMP
    Ta = Tn + s   # T is linear in the data: the signal adds exactly s to T
    r['preregistered_at_crts_amp'] = {'a': float(s), 'power_at_0.01': float(np.mean(Ta >= crit)), 'p_sig': float(np.mean(Ta <= T))}
    # A5: ZTF free-phase amplitude at 741 d against random-phase sinusoids
    rng = np.random.default_rng(SEED2 + 1)
    D = drw(t, sig, rng, 2000, TAU) + rng.normal(0, 1, (2000, len(t))) * e
    ph = rng.uniform(0, 1, 2000); a5 = {}
    for amp in (0.1, A_c):
        S = amp * np.sin(2 * np.pi * ((t[None] - T0) / P + ph[:, None]))
        Am = np.array([free_phase(t, D[i] + S[i], e, Xo, P)[0] for i in range(2000)])
        a5[f'{amp:.3f}'] = float(np.mean(Am <= A_ztf))
    r['ztf_free_amp_frac_le_obs_random_phase'] = a5
    return r


def main():
    raw = raw_csv()
    t, m, e, oid = load(raw); Xo = design(oid)
    x = template(t); T = float(coef(m, e, Xo, x))
    resid = m - Xo @ lsq(m, e, Xo, [])
    sig = float(np.sqrt(max(np.var(resid) - np.mean(e ** 2), 0.01 ** 2)))
    out = {'n_points': int(len(t)), 'n_points_per_band': {b: int(len(load(raw, (b,))[0])) for b in BANDS},
           'n_oid': int(Xo.shape[1]), 'mjd_min': float(t.min()), 'mjd_max': float(t.max()),
           'median_mag': {b: float(np.median(load(raw, (b,))[1])) for b in BANDS},
           'sigma_drw': sig, 'T_obs': T}
    for tau in (TAU, 500.0):
        Tn, Ts = sims(t, e, Xo, x, sig, tau)
        crit = np.quantile(Tn, 0.99)
        out[f'tau{int(tau)}'] = {'p_null': float(np.mean(Tn >= T)), 'p_sig': float(np.mean(Ts <= T)),
                                 'null_T_q01_q50_q99': [float(np.quantile(Tn, q)) for q in (0.01, 0.5, 0.99)],
                                 'sig_T_q01_q50_q99': [float(np.quantile(Ts, q)) for q in (0.01, 0.5, 0.99)],
                                 'power_at_0.01': float(np.mean(Ts >= crit))}
    scan = [float(coef(m, e, Xo, template(t, shift=s))) for s in np.arange(0, 1, 0.05)]
    out['phase_scan_T'] = [round(v, 4) for v in scan]
    out['phase_rank_of_zero'] = int(1 + sum(v > scan[0] for v in scan))
    out['best_phase_shift'] = float(np.arange(0, 1, 0.05)[int(np.argmax(scan))])
    A, ph = free_phase(t, m, e, Xo, P)
    out['free_phase_P741'] = {'amplitude_mag': A, 'phase_shift_cycles': ph}
    for b in BANDS:
        tb, mb, eb, ob = load(raw, (b,)); Xb = design(ob)
        out[f'T_{b}_only'] = float(coef(mb, eb, Xb, template(tb)))
    per = np.arange(300.0, 1501.0, 5.0)
    amps = [free_phase(t, m, e, Xo, PP)[0] for PP in per]
    k = int(np.argmax(amps))
    out['period_scan_best'] = {'P': float(per[k]), 'amplitude_mag': float(amps[k])}
    out['period_scan_amp_at_741'] = float(amps[int(np.argmin(abs(per - 741)))])
    # Post hoc (not pre-registered; written after the primary result was seen).
    ph = {}
    rng = np.random.default_rng(SEED + 1)
    D = drw(t, sig, rng, 2000, TAU) + rng.normal(0, 1, (2000, len(t))) * e
    An = np.array([free_phase(t, D[k], e, Xo, P)[0] for k in range(2000)])
    ph['free_phase_amp_P741_p_null_tau210'] = float(np.mean(An >= A))
    ph['free_phase_amp_P741_null_q50_q99'] = [float(np.quantile(An, 0.5)), float(np.quantile(An, 0.99))]
    out['posthoc'] = ph
    out['ztf_csv_sha256'] = hashlib.sha256(raw.encode()).hexdigest()
    out['addendum1'] = addendum1(t, m, e, Xo, sig, T, A)
    return out, (t, m, e, oid, Xo, per, amps)


if __name__ == '__main__':
    res, _ = main()
    print(json.dumps(res, indent=1))
    f = ROOT / 'data/expected.json'
    if '--write' in sys.argv:
        json.dump(res, open(f, 'w'), indent=1); print('written')
    else:
        exp = json.load(open(f)); bad = []

        def cmp(path, a, b):
            if isinstance(b, dict):
                for kk in b: cmp(path + '.' + kk, a[kk], b[kk])
            elif isinstance(b, str) or isinstance(b, bool):
                if a != b: bad.append((path, b, a))
            elif not np.allclose(a, b, rtol=1e-6, atol=1e-9):
                bad.append((path, b, a))
        if res.get('ztf_csv_sha256') != exp.get('ztf_csv_sha256'):
            print('NOTE: the IRSA CSV checksum differs from data/expected.json; the ZTF release changed.')
        cmp('', res, exp)
        for p in bad: print('MISMATCH', *p)
        print('OK' if not bad else 'FAIL'); sys.exit(0 if not bad else 1)
