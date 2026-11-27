"""Core routines: sort/LCP counting, node-weight histograms, estimator E, model chains."""
import numpy as np

D = 40


def sort_lcp(get_col, n):
    """LSD radix sort of n keys of D uint16 columns. get_col(c) returns column c (length n).
    Returns perm (int64) and lcp (uint8): lcp[i] = common prefix length of sorted keys i-1 and i."""
    perm = np.arange(n, dtype=np.int64)
    for c in range(D - 1, -1, -1):
        key = np.asarray(get_col(c))[perm]
        perm = perm[np.argsort(key, kind="stable")]
    lcp = np.full(n, D, dtype=np.uint8)
    lcp[0] = 0
    for c in range(D):
        s = np.asarray(get_col(c))[perm]
        hit = (s[1:] != s[:-1]) & (lcp[1:] == D)
        lcp[1:][hit] = c
    return perm, lcp


def subset_lcp(lcp, sel):
    """LCP between neighbours of a sorted subset (sel ascending)."""
    out = np.zeros(len(sel), dtype=np.uint8)
    if len(sel) > 1:
        out[1:] = np.minimum.reduceat(lcp[: sel[-1] + 1], sel[:-1] + 1)
    return out


def depth_hists(lcp_sel, L_sel):
    """S_d(n) for d = 1..D from sorted-subset LCP and game lengths.
    Returns dict d -> (n values, node counts)."""
    m = len(lcp_sel)
    out = {}
    for d in range(1, D + 1):
        starts = np.flatnonzero(lcp_sel < d)
        sizes = np.diff(np.append(starts, m))
        keep = L_sel[starts] >= d
        v, c = np.unique(sizes[keep], return_counts=True)
        out[d] = (v, c.astype(np.float64))
    return out


def pooled(hists):
    v = np.concatenate([hists[d][0] for d in hists])
    c = np.concatenate([hists[d][1] for d in hists])
    u, inv = np.unique(v, return_inverse=True)
    return u, np.bincount(inv, weights=c)


def bin_edges(nmax):
    e = sorted({int(np.floor(2 ** (k / 2))) for k in range(0, int(2 * np.log2(max(nmax, 2))) + 4)})
    return np.array(e, dtype=np.float64)


def estimator_E(v, c, N, return_bins=False):
    """Log-binned least-squares exponent (PROTOCOL.md section 3). Returns alpha or nan."""
    v = np.asarray(v, dtype=np.float64)
    c = np.asarray(c, dtype=np.float64)
    e = bin_edges(max(v.max() if len(v) else 2, N))
    k = np.searchsorted(e, v, side="right") - 1
    cnt = np.bincount(k, weights=c, minlength=len(e))[: len(e) - 1]
    lo, hi = e[:-1], e[1:]
    ok = (hi - 1 <= N / 100) & (cnt >= 5)
    if ok.sum() < 4:
        return (np.nan, None) if return_bins else np.nan
    x = np.log10(np.sqrt(lo[ok] * (hi[ok] - 1)))
    y = np.log10(cnt[ok] / (hi[ok] - lo[ok]))
    slope = np.polyfit(x, y, 1)[0]
    if return_bins:
        return -slope, (x, y)
    return -slope


def summarize(hists, N):
    """alpha_d for d=1..D, alpha_pool, b(N), d_cr(N), rho."""
    ad = np.array([estimator_E(*hists[d], N) if len(hists[d][0]) else np.nan for d in range(1, D + 1)])
    ap = estimator_E(*pooled(hists), N)
    ds = np.arange(3, int(np.floor(np.log(N))) + 1)
    y = ad[ds - 1]
    ok = np.isfinite(y)
    b = np.polyfit(ds[ok], y[ok], 1)[0] if ok.sum() >= 3 else np.nan
    dcr = np.nan
    for d in range(2, D + 1):
        a0, a1 = ad[d - 2], ad[d - 1]
        if np.isfinite(a1) and a1 >= 2:
            if np.isfinite(a0) and a0 < 2:
                dcr = (d - 1) + (2 - a0) / (a1 - a0)
            else:
                dcr = float(d)
            break
    return {"alpha_d": ad.tolist(), "alpha_pool": float(ap), "b": float(b),
            "rho": float(b * np.log(N)), "d_cr": float(dcr)}


def model_hists(N, M, seed):
    """Expected S_d(n) of the Eq. (3) chains with arcsine q(r) = 2/(pi sqrt(1-r^2))."""
    rng = np.random.default_rng(seed)
    n = np.full(M, float(N))
    out = {}
    for d in range(1, D + 1):
        r = np.sin(0.5 * np.pi * rng.random(M))
        n = np.maximum(1.0, np.round(n * r))
        v, c = np.unique(n, return_counts=True)
        out[d] = (v, (N / M) * c / v)
    return out
