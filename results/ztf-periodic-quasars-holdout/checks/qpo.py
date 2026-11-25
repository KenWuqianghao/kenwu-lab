"""Core methods for the forward test (see PROTOCOL.md).

All light-curve work is on 20-day binned ZTF r-band magnitudes.
Training window = the ZTF DR11 public selection; test window = MJD > 59647.
"""
import numpy as np
import pandas as pd
from scipy import optimize

# ZTF DR11 release notes (2022-05-09): programid 1 epochs MJD 58194.0-59647.0,
# programid 2/3 epochs MJD 58194.0-59159.0.
MJD0 = 58194.0
DR11_END_PUBLIC = 59647.0
DR11_END_PRIVATE = 59159.0
# Last epoch served by IRSA on 2026-11-24 was MJD 60969.55. Fixing the end keeps reruns identical
# after a new ZTF release.
TEST_END = 60970.0
BIN = 20.0
PMIN = 50.0
MIN_TRAIN_BINS = 40
MIN_TEST_BINS = 10
XI_CUT = 4.0
NCYC_CUT = 1.5


# ---------------------------------------------------------------- data
def load_raw(path):
    df = pd.read_csv(path)
    for c in ("mjd", "mag", "magerr", "catflags", "programid"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[(df.filtercode == "zr") & (df.catflags == 0) & (df.magerr > 0) & np.isfinite(df.mag)]
    return df[["mjd", "mag", "magerr", "programid"]].sort_values("mjd").reset_index(drop=True)


def split(df):
    tr = (df.mjd >= MJD0) & (((df.programid == 1) & (df.mjd <= DR11_END_PUBLIC)) |
                             ((df.programid.isin([2, 3])) & (df.mjd <= DR11_END_PRIVATE)))
    te = (df.mjd > DR11_END_PUBLIC) & (df.mjd <= TEST_END)
    return df[tr].reset_index(drop=True), df[te].reset_index(drop=True)


def clip_poly15(df):
    """Paper recipe: 15th-order polynomial fit, drop points beyond 3 sigma (one pass)."""
    if len(df) < 20:
        return df
    p = np.polynomial.Polynomial.fit(df.mjd.values, df.mag.values, 15)
    r = df.mag.values - p(df.mjd.values)
    return df[np.abs(r) <= 3 * np.std(r)].reset_index(drop=True)


def bin20(df):
    """20-day bins on a fixed grid starting at MJD0. Mean mag, standard error, mean time."""
    if len(df) == 0:
        return np.zeros(0), np.zeros(0), np.zeros(0)
    idx = np.floor((df.mjd.values - MJD0) / BIN).astype(int)
    t, m, e = [], [], []
    for i in np.unique(idx):
        s = idx == i
        mm = df.mag.values[s]
        t.append(df.mjd.values[s].mean())
        m.append(mm.mean())
        e.append(mm.std(ddof=1) / np.sqrt(s.sum()) if s.sum() > 1 else df.magerr.values[s][0])
    return np.array(t), np.array(m), np.array(e)


def prepare(path):
    raw = load_raw(path)
    tr, te = split(raw)
    tr, te = clip_poly15(tr), clip_poly15(te)
    return dict(train=bin20(tr), test=bin20(te), n_raw_train=len(tr), n_raw_test=len(te))


# ---------------------------------------------------------------- GLS (vectorised over many series)
def freq_grid(t):
    T = t.max() - t.min()
    return np.arange(1.0 / T, 1.0 / PMIN, 1.0 / (10 * T))


def gls_batch(t, Y, freqs):
    """Unweighted generalised Lomb-Scargle (offset + sinusoid) for each row of Y.

    Returns best period, coefficients (c, a, b) at the best period, power, xi, Ncycle.
    Model: y = c + a cos(2 pi t/P) + b sin(2 pi t/P).
    """
    Y = np.atleast_2d(Y)
    M, N = Y.shape
    Yc = Y - Y.mean(1, keepdims=True)
    ss0 = (Yc ** 2).sum(1)
    best = np.full(M, -np.inf)
    bestf = np.zeros(M)
    for f in freqs:
        w = 2 * np.pi * f * t
        X = np.vstack([np.cos(w), np.sin(w)])
        X = X - X.mean(1, keepdims=True)
        C = X @ X.T
        v = Yc @ X.T  # (M,2)
        red = np.einsum("mi,ij,mj->m", v, np.linalg.inv(C), v)
        upd = red > best
        best[upd] = red[upd]
        bestf[upd] = f
    power = best / ss0
    coef, xi = fit_at(t, Y, 1.0 / bestf)
    return dict(P=1.0 / bestf, coef=coef, power=power, xi=xi, ncyc=(t.max() - t.min()) * bestf)


def fit_at(t, Y, P):
    """Least-squares offset+sinusoid at a given period per row. Returns coef (M,3) and xi."""
    Y = np.atleast_2d(Y)
    P = np.broadcast_to(np.asarray(P, float), (Y.shape[0],))
    w = 2 * np.pi * t[None, :] / P[:, None]
    X = np.stack([np.ones_like(w), np.cos(w), np.sin(w)], -1)  # (M,N,3)
    A = np.einsum("mni,mnj->mij", X, X)
    bvec = np.einsum("mni,mn->mi", X, Y)
    coef = np.linalg.solve(A, bvec[..., None])[..., 0]
    res = Y - np.einsum("mni,mi->mn", X, coef)
    a0 = np.hypot(coef[:, 1], coef[:, 2])
    xi = a0 ** 2 / (2 * res.var(1))
    return coef, xi


def template(t, P, coef):
    """Zero-mean frozen sinusoid a cos + b sin, for each row (P (M,), coef (M,3))."""
    w = 2 * np.pi * t[None, :] / np.asarray(P)[:, None]
    return coef[:, 1:2] * np.cos(w) + coef[:, 2:3] * np.sin(w)


def score_k(t_test, Ytest, P, coef):
    """Primary score k: OLS slope of test-window magnitudes on the frozen template (free offset)."""
    S = template(t_test, P, coef)
    Sc = S - S.mean(1, keepdims=True)
    Yc = np.atleast_2d(Ytest) - np.atleast_2d(Ytest).mean(1, keepdims=True)
    return (Sc * Yc).sum(1) / (Sc ** 2).sum(1)


def phase_shift(t_test, ytest, P, coef_train):
    """Refit the test window at the frozen period; return phase difference (cycles, in [-0.5,0.5)) and amplitude ratio."""
    c2, _ = fit_at(t_test, ytest[None, :], np.array([P]))
    ph1 = np.arctan2(coef_train[2], coef_train[1])
    ph2 = np.arctan2(c2[0, 2], c2[0, 1])
    d = ((ph2 - ph1) / (2 * np.pi) + 0.5) % 1.0 - 0.5
    return d, np.hypot(c2[0, 1], c2[0, 2]) / np.hypot(coef_train[1], coef_train[2])


# ---------------------------------------------------------------- DRW
def drw_nll(params, t, y, e, mean_fn=None):
    ls, lt = params
    s2, tau = np.exp(2 * ls), np.exp(lt)
    K = s2 * np.exp(-np.abs(t[:, None] - t[None, :]) / tau) + np.diag(e ** 2)
    try:
        L = np.linalg.cholesky(K)
    except np.linalg.LinAlgError:
        return 1e10
    one = np.ones_like(y)
    Ki1 = np.linalg.solve(L.T, np.linalg.solve(L, one))
    Kiy = np.linalg.solve(L.T, np.linalg.solve(L, y))
    q = (one @ Kiy) / (one @ Ki1)
    r = y - q
    Kir = np.linalg.solve(L.T, np.linalg.solve(L, r))
    return 0.5 * r @ Kir + np.log(np.diag(L)).sum()


def fit_drw(t, y, e):
    """Maximum-likelihood DRW (sigma_d, tau_d) with profiled mean; tau in [10, 20000] d."""
    best = None
    for lt0 in np.log([50.0, 200.0, 1000.0]):
        r = optimize.minimize(drw_nll, x0=[np.log(np.std(y) + 1e-3), lt0], args=(t, y, e), method="L-BFGS-B",
                              bounds=[(np.log(1e-3), np.log(3.0)), (np.log(10.0), np.log(20000.0))])
        if best is None or r.fun < best.fun:
            best = r
    return float(np.exp(best.x[0])), float(np.exp(best.x[1]))


def sim_drw(t, sigma, tau, M, rng):
    """Exact Ornstein-Uhlenbeck draws at sorted times t, M series, zero mean."""
    x = np.empty((M, len(t)))
    x[:, 0] = rng.normal(0, sigma, M)
    for i in range(1, len(t)):
        a = np.exp(-(t[i] - t[i - 1]) / tau)
        x[:, i] = a * x[:, i - 1] + rng.normal(0, sigma * np.sqrt(1 - a * a), M)
    return x


# ---------------------------------------------------------------- SPL (Timmer & Koenig)
def sim_spl(t, beta, M, rng, dt=5.0, pad=5, batch=2000):
    """Power-law PSD ~ f^-beta noise (Timmer & Koenig 1995) on a dt grid of length pad x span,
    sampled at times t (nearest grid point), random start. Unit-free; scaled by the caller."""
    span = t.max() - t.min()
    n = int(2 ** np.ceil(np.log2(span * pad / dt)))
    f = np.fft.rfftfreq(n, dt)[1:]
    amp = f ** (-beta / 2.0)
    gi = np.round((t - t.min()) / dt).astype(int)
    out = np.empty((M, len(t)))
    for s0 in range(0, M, batch):
        m = min(batch, M - s0)
        spec = np.zeros((m, len(f) + 1), complex)
        spec[:, 1:] = (rng.normal(size=(m, len(f))) + 1j * rng.normal(size=(m, len(f)))) * amp
        x = np.fft.irfft(spec, n, axis=1)
        start = rng.integers(0, n - gi.max() - 1, m)
        out[s0:s0 + m] = x[np.arange(m)[:, None], start[:, None] + gi[None, :]]
    return out
