"""Verifier's own conditioned-DRW p-values for a subset of objects. No solver code imported."""
import sys, numpy as np, pandas as pd
from scipy import optimize, linalg
LC, TABLE = sys.argv[1], sys.argv[2]; ids = sys.argv[3:]
tab = pd.read_csv(TABLE).set_index("id")

def bins(d):
    if len(d) >= 20:
        x = (d.mjd - d.mjd.mean()) / (d.mjd.max() - d.mjd.min()) * 2
        c = np.polynomial.legendre.legfit(x, d.mag, 15)
        r = d.mag - np.polynomial.legendre.legval(x, c)
        d = d[np.abs(r) <= 3 * r.std()]
    g = d.groupby(np.floor((d.mjd - 58194.0) / 20.0))
    n = g.mag.count().values
    e = np.where(n > 1, g.mag.std(ddof=1).fillna(0).values / np.sqrt(n), g.magerr.first().values)
    return g.mjd.mean().values, g.mag.mean().values, np.maximum(e, 1e-3)

def load(path):
    d = pd.read_csv(path)
    for c in ("mjd", "mag", "magerr", "catflags", "programid"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[(d.filtercode == "zr") & (d.catflags == 0) & (d.magerr > 0)].sort_values("mjd")
    tr = d[(d.mjd >= 58194) & (((d.programid == 1) & (d.mjd <= 59647)) | (d.programid.isin([2, 3]) & (d.mjd <= 59159)))]
    te = d[(d.mjd > 59647) & (d.mjd <= 60970)]
    return bins(tr), bins(te)

def nll(p, t, y, e):
    s2, tau = np.exp(2*p[0]), np.exp(p[1])
    K = s2*np.exp(-np.abs(t[:, None]-t[None, :])/tau) + np.diag(e**2)
    cf = linalg.cho_factor(K, lower=True)
    one = np.ones_like(y); a = linalg.cho_solve(cf, one); b = linalg.cho_solve(cf, y)
    mu = one@b/(one@a); r = y-mu
    return 0.5*r@linalg.cho_solve(cf, r) + np.log(np.diag(cf[0])).sum()

def gls(t, Y, f):
    """returns best P, coef(a,b), xi for each row"""
    Yc = Y - Y.mean(1, keepdims=True)
    best = np.full(len(Y), -1.0); bi = np.zeros(len(Y), int)
    for j, ff in enumerate(f):
        X = np.c_[np.cos(2*np.pi*ff*t), np.sin(2*np.pi*ff*t)]; X = X - X.mean(0)
        Q, _ = np.linalg.qr(X)
        pw = ((Yc@Q)**2).sum(1)
        u = pw > best; best[u] = pw[u]; bi[u] = j
    P = 1/f[bi]
    w = 2*np.pi*t[None, :]/P[:, None]
    C, S = np.cos(w), np.sin(w); C -= C.mean(1, keepdims=True); S -= S.mean(1, keepdims=True)
    cc, ss, cs = (C*C).sum(1), (S*S).sum(1), (C*S).sum(1); yc, ys = (Yc*C).sum(1), (Yc*S).sum(1)
    det = cc*ss-cs**2; a = (ss*yc-cs*ys)/det; b = (cc*ys-cs*yc)/det
    res = Yc - a[:, None]*C - b[:, None]*S
    return P, a, b, (a*a+b*b)/(2*res.var(1))

def kscore(tt, Yt, P, a, b):
    w = 2*np.pi*tt[None, :]/P[:, None]; s = a[:, None]*np.cos(w)+b[:, None]*np.sin(w)
    s -= s.mean(1, keepdims=True); Yc = Yt - Yt.mean(1, keepdims=True)
    return (s*Yc).sum(1)/(s*s).sum(1)

rng = np.random.default_rng(7)
for oid in ids:
    (t, y, e), (tt, yt, et) = load(f"{LC}/{oid}.csv")
    T = t.max()-t.min(); f = np.arange(1/T, 1/50, 1/(10*T))
    P, a, b, xi = gls(t, y[None], f); k = kscore(tt, yt[None], P, a, b)[0]
    best = min((optimize.minimize(nll, [np.log(y.std()), np.log(t0)], args=(t, y, e), method="Nelder-Mead") for t0 in (50, 300, 1500)), key=lambda r: r.fun)
    sig, tau = np.exp(best.x[0]), float(np.clip(np.exp(best.x[1]), 10, 20000))
    ta = np.r_[t, tt]; ea = np.r_[e, et]
    L = np.linalg.cholesky(sig**2*np.exp(-np.abs(ta[:, None]-ta[None, :])/tau) + 1e-12*np.eye(len(ta)))
    acc = []; n = 0; unc = None
    while n < 300000 and sum(map(len, acc)) < 1000:
        Y = rng.normal(size=(20000, len(ta)))@L.T + rng.normal(size=(20000, len(ta)))*ea + y.mean()
        Pm, am, bm, xim = gls(t, Y[:, :len(t)], f); km = kscore(tt, Y[:, len(t):], Pm, am, bm)
        acc.append(km[(xim >= min(xi[0], 4.0)) & (np.abs(Pm/P[0]-1) < 0.2)])
        if unc is None: unc = km
        n += 20000
    acc = np.concatenate(acc); use = acc if len(acc) >= 200 else unc
    p = (1+(use >= k).sum())/(1+len(use))
    s = tab.loc[oid]
    print(f"{oid} P {P[0]:.0f}/{s.P:.0f} k {k:.3f}/{s.k:.3f} sig {sig:.3f}/{s.drw_sigma:.3f} tau {tau:.0f}/{s.drw_tau:.0f} nacc {len(acc)}/{s.drw_n_acc:.0f} p_mine {p:.4f} p_solver {s.p_drw:.4f}", flush=True)
