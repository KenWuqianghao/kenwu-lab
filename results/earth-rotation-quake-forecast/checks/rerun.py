"""Reproduce every number of the Bilham-Bendick 2017 forecast score.

Usage:
  python3 checks/rerun.py [--work DIR]            # download ComCat, C02, C04; compute; compare with data/expected.json
  python3 checks/rerun.py --work DIR --offline    # catalog from data/comcat_m7_1900_2025.csv, LOD files from DIR
  python3 checks/rerun.py --write-expected

Downloads and data/results-style output go to the work folder DIR (default: a new temporary folder).
Implements the pre-registered protocol (see the paper, Section 3). The block "write_additions" holds
computations added at the write stage (2026-11-25): the P2 power with the pre-registered 10 000
simulations, the P1 decision thresholds, the forecast-level sensitivity, and the C04 mask check.
They use their own random generator, so the other numbers stay identical to the solve-stage run.
"""
import argparse, csv, datetime, hashlib, io, itertools, json, math, sys, tempfile, urllib.request
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COMCAT = ("https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&eventtype=earthquake"
          "&minmagnitude=7&orderby=time-asc&starttime=1900-01-01T00:00:00&endtime=2026-01-01T00:00:00")
C02 = "https://hpiers.obspm.fr/eoppc/series/longterm/eopc02.1830-now"
C04 = "https://datacenter.iers.org/data/latestVersion/EOP_20_C04_one_file_1962-now.txt"
Y0, Y1 = 1900, 2017            # baseline
WIN = (2018, 2022)             # forecast window
HOLD = (2018, 2025)            # held-out years for P2
NSIM = 10_000
rng = np.random.default_rng(20171022)


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read().decode()


# ---------- data ----------
def load_catalog(offline, work):
    snap = DATA / "comcat_m7_1900_2025.csv"
    if offline:
        text = snap.read_text()
    else:
        raw = fetch(COMCAT)
        rows = list(csv.DictReader(io.StringIO(raw)))
        out = io.StringIO()
        w = csv.writer(out, lineterminator="\n")
        w.writerow(["id", "time", "latitude", "longitude", "depth", "mag", "magType"])
        for r in rows:
            w.writerow([r["id"], r["time"], r["latitude"], r["longitude"], r["depth"], r["mag"], r["magType"]])
        text = out.getvalue()
        (work / "comcat_m7_1900_2025.csv").write_text(text)
        if text != snap.read_text():
            print("NOTE the new ComCat download differs from data/comcat_m7_1900_2025.csv")
    ev = []
    for r in csv.DictReader(io.StringIO(text)):
        t = datetime.datetime.fromisoformat(r["time"].replace("Z", "+00:00"))
        ev.append((t, float(r["latitude"]), float(r["longitude"]), float(r["mag"]), r["id"]))
    ev.sort()
    return ev, hashlib.sha256(text.encode()).hexdigest()


def load_lod(offline, work):
    p02, p04 = work / "eopc02.txt", work / "c04.txt"
    if not offline:
        p02.write_text(fetch(C02))
        p04.write_text(fetch(C04))
    d = np.loadtxt(p02, comments="#", usecols=(0, 21))
    mjd, lod = d[:, 0], d[:, 1] * 1e3  # ms
    day = np.arange(mjd[0], mjd[-1] + 1)
    lday = np.interp(day, mjd, lod)
    base = datetime.date(1858, 11, 17)
    yrs = np.array([(base + datetime.timedelta(days=int(x))).year for x in day])
    annual = {int(y): float(lday[yrs == y].mean()) for y in range(1831, 2026)}
    c04 = np.loadtxt(p04, comments="#", usecols=(0, 12))
    a04 = {y: float(c04[c04[:, 0] == y, 1].mean() * 1e3) for y in range(1962, 2025)}
    ys = sorted(a04)
    r = float(np.corrcoef([annual[y] for y in ys], [a04[y] for y in ys])[0, 1])
    mask = {y: int(annual[y] > annual[y - 1]) for y in range(1832, 2026)}
    mask04 = {y: int(a04[y] > a04[y - 1]) for y in range(1963, 2025)}
    h = hashlib.sha256(p02.read_bytes()).hexdigest()
    return annual, mask, r, h, mask04


# ---------- declustering ----------
def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[1], a[2], b[1], b[2]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def decluster_gk(ev):
    """Gardner-Knopoff windows within the M>=7 set. Larger events are processed first (ties: earlier first).
    Each later-processed event inside the window of a kept event is removed."""
    order = sorted(range(len(ev)), key=lambda i: (-ev[i][3], ev[i][0]))
    pos = {i: r for r, i in enumerate(order)}
    tsec = np.array([e[0].timestamp() for e in ev])
    removed = set()
    for i in order:
        if i in removed:
            continue
        m = ev[i][3]
        dkm = 10 ** (0.1238 * m + 0.983)
        tday = 10 ** (0.032 * m + 2.7389)
        near = np.nonzero(np.abs(tsec - tsec[i]) <= tday * 86400)[0]
        for j in near:
            j = int(j)
            if j != i and j not in removed and pos[j] > pos[i] and haversine(ev[i], ev[j]) <= dkm:
                removed.add(j)
    return [e for k, e in enumerate(ev) if k not in removed]


# ---------- helpers ----------
def annual_counts(ev, minmag, y0, y1):
    c = {y: 0 for y in range(y0, y1 + 1)}
    for e in ev:
        if e[3] >= minmag - 1e-9 and y0 <= e[0].year <= y1:
            c[e[0].year] += 1
    return c


def nb_k(x):
    m, v = float(np.mean(x)), float(np.var(x, ddof=1))
    return (m * m / (v - m)) if v > m else math.inf


def nb_cdf(n, mean, size):
    if math.isinf(size):
        return float(stats.poisson.cdf(n, mean))
    return float(stats.nbinom.cdf(n, size, size / (size + mean)))


def nb_sf_ge(n, mean, size):  # P(X >= n)
    return 1.0 - nb_cdf(n - 1, mean, size)


def nb_rvs(mean, size, shape):
    if math.isinf(size):
        return rng.poisson(mean, shape)
    return rng.negative_binomial(size, size / (size + mean), shape)


def p1(N, lam0, k, years=5, level=None):
    lamF = 1.25 * lam0 if level is None else level
    pr = nb_cdf(N, years * lamF, years * k)
    ps = nb_sf_ge(N, years * lam0, years * k)
    verdict = "REFUTED" if pr < 0.05 else ("SUPPORTED" if ps < 0.05 else "INCONCLUSIVE")
    return pr, ps, verdict


def ratio_ci(N, lam0, k, years=5):
    # 95% interval for the true rate ratio r: values of r not rejected two-sided at 2.5% each
    rs = np.linspace(0.3, 2.5, 2201)
    ok = [r for r in rs if nb_cdf(N, years * lam0 * r, years * k) > 0.025 and nb_sf_ge(N, years * lam0 * r, years * k) > 0.025]
    return float(min(ok)), float(max(ok))


def p1_block(ev, minmag, lam0, k, base=(Y0, Y1), win=WIN, level=None):
    c = annual_counts(ev, minmag, base[0], base[1])
    w = annual_counts(ev, minmag, win[0], win[1])
    N = sum(w.values())
    pr, ps, v = p1(N, lam0, k, years=win[1] - win[0] + 1, level=level)
    return {"N": N, "per_year": {str(y): w[y] for y in w}, "rate": N / (win[1] - win[0] + 1),
            "lambda0": lam0, "k": k, "ratio": N / (win[1] - win[0] + 1) / lam0,
            "p_refute": pr, "p_support": ps, "verdict": v}


def perm_test(counts, labels):
    counts, labels = np.array(counts, float), np.array(labels, int)
    n, kk = len(counts), int(labels.sum())
    if kk in (0, n):
        return None
    def D(lab):
        return counts[lab == 1].mean() - counts[lab == 0].mean()
    obs = D(labels)
    ds = []
    for comb in itertools.combinations(range(n), kk):
        lab = np.zeros(n, int); lab[list(comb)] = 1
        ds.append(D(lab))
    ds = np.array(ds)
    return float(obs), float(np.mean(ds >= obs - 1e-12)), len(ds), float(1 / len(ds))


def lag_share(years_of_events, mask, L, y0, y1):
    inm = sum(1 for y in years_of_events if mask[y - L] == 1)
    myears = sum(mask[y - L] for y in range(y0, y1 + 1))
    n = len(years_of_events)
    ny = y1 - y0 + 1
    rr = (inm / myears) / ((n - inm) / (ny - myears)) if 0 < myears < ny and n - inm > 0 else float("nan")
    return inm / n, myears / ny, rr


# ---------- main analysis ----------
def analyse(ev, mask):
    res = {}
    ev_d = decluster_gk(ev)
    res["n_events_total_1900_2025"] = len(ev)
    res["n_events_declustered_1900_2025"] = len(ev_d)

    def base_stats(e, mm, y0=Y0, y1=Y1):
        c = annual_counts(e, mm, y0, y1)
        x = np.array([c[y] for y in range(y0, y1 + 1)])
        return float(x.mean()), nb_k(x), float(x.var(ddof=1)), x

    lam0, k, var0, x0 = base_stats(ev, 7.0)
    res["baseline"] = {"lambda0": lam0, "var": var0, "k": k, "N": int(x0.sum())}

    # P1 primary
    res["P1"] = p1_block(ev, 7.0, lam0, k)
    res["P1"]["ratio_95ci"] = ratio_ci(res["P1"]["N"], lam0, k)

    # secondary
    sec = {}
    pr = stats.poisson.cdf(res["P1"]["N"], 5 * 1.25 * lam0); ps = stats.poisson.sf(res["P1"]["N"] - 1, 5 * lam0)
    sec["poisson"] = {"p_refute": float(pr), "p_support": float(ps)}
    l71, k71, _, _ = base_stats(ev, 7.1)
    sec["m7.1"] = p1_block(ev, 7.1, l71, k71)
    ld, kd, _, _ = base_stats(ev_d, 7.0)
    sec["declustered"] = p1_block(ev_d, 7.0, ld, kd)
    l73, k73, _, _ = base_stats(ev, 7.0, 1973, 2017)
    sec["baseline_1973_2017"] = p1_block(ev, 7.0, l73, k73)
    sec["window_2017_2021"] = p1_block(ev, 7.0, lam0, k, win=(2017, 2021))
    sec["level_17_per_year"] = p1_block(ev, 7.0, lam0, k, level=17.0)
    S = np.array([x0[i:i + 5].sum() for i in range(len(x0) - 4)])
    N = res["P1"]["N"]
    sec["empirical_5yr_sums"] = {"n_windows": len(S), "mean": float(S.mean()), "sd": float(S.std(ddof=1)),
                                 "min": int(S.min()), "max": int(S.max()),
                                 "frac_1.25S_le_N": float(np.mean(1.25 * S <= N)),
                                 "frac_S_ge_N": float(np.mean(S >= N))}
    prev = sum(annual_counts(ev, 7.0, 2013, 2017).values())
    sec["vs_2013_2017"] = {"N_2013_2017": prev, "N_2018_2022": N,
                           "binom_p_two_sided": float(stats.binomtest(N, N + prev, 0.5).pvalue)}
    res["P1_secondary"] = sec

    # P1 controls
    placebo = {"REFUTED": 0, "SUPPORTED": 0, "INCONCLUSIVE": 0}
    for s in range(1900, 2014):
        n = int(x0[s - 1900:s - 1895].sum())
        placebo[p1(n, lam0, k)[2]] += 1
    res["P1_placebo_windows_1900_2013"] = placebo
    inj = {}
    for r in (1.0, 1.25, 1.30):
        sims = nb_rvs(lam0 * r, k, (NSIM, 5)).sum(axis=1)
        v = [p1(int(n), lam0, k)[2] for n in sims]
        inj[str(r)] = {"REFUTED": v.count("REFUTED") / NSIM, "SUPPORTED": v.count("SUPPORTED") / NSIM}
    res["P1_injection"] = inj

    # P2 held-out lag test
    def p2(e, mm, L):
        c = annual_counts(e, mm, HOLD[0], HOLD[1])
        yrs = list(range(HOLD[0], HOLD[1] + 1))
        lab = [mask[y - L] for y in yrs]
        pt = perm_test([c[y] for y in yrs], lab)
        tot = sum(c.values())
        inm = sum(c[y] for y, l in zip(yrs, lab) if l)
        out = {"L": L, "counts": {str(y): c[y] for y in yrs}, "enhanced_years": [y for y, l in zip(yrs, lab) if l],
               "share_events_in_enhanced": inm / tot, "share_years_enhanced": sum(lab) / len(yrs)}
        if pt:
            d, p, nperm, pmin = pt
            ne = sum(lab)
            m1 = inm / ne; m0 = (tot - inm) / (len(yrs) - ne)
            out.update({"D": d, "p_perm": p, "n_perm": nperm, "p_min": pmin, "rate_ratio": m1 / m0,
                        "verdict": "SUPPORTED" if p < 0.05 else "NOT SUPPORTED"})
        return out

    res["P2"] = p2(ev, 7.0, 5)
    res["P2_secondary"] = {"L6": p2(ev, 7.0, 6), "declustered_L5": p2(ev_d, 7.0, 5), "m7.1_L5": p2(ev, 7.1, 5)}
    # P2 power
    yrs = list(range(HOLD[0], HOLD[1] + 1)); lab = np.array([mask[y - 5] for y in yrs])
    hits = 0
    for _ in range(2000):
        c = nb_rvs(lam0 * np.where(lab == 1, 1.25, 1.0), k, len(yrs))
        hits += perm_test(c, lab)[1] < 0.05
    res["P2_power_x1.25"] = hits / 2000
    hits0 = 0
    for _ in range(2000):
        c = nb_rvs(np.full(len(yrs), lam0), k, len(yrs))
        hits0 += perm_test(c, lab)[1] < 0.05
    res["P2_false_positive_x1.00"] = hits0 / 2000

    # P3 in-sample lag curve
    def p3(e, mm):
        yev = [x[0].year for x in e if x[3] >= mm - 1e-9 and Y0 <= x[0].year <= Y1]
        cnt = np.bincount(np.array(yev) - Y0, minlength=Y1 - Y0 + 1)
        out = {}
        maxobs = -1; maxnull = np.zeros(99)
        for L in range(10):
            m = np.array([mask[y - L] for y in range(Y0, Y1 + 1)])
            share = float((cnt * m).sum() / cnt.sum())
            null = []
            for s in range(10, 109):
                ms = np.roll(m, s)
                null.append((cnt * ms).sum() / cnt.sum())
            null = np.array(null)
            maxnull = np.maximum(maxnull, null)
            # random catalogs
            rc = rng.integers(0, len(cnt), size=(NSIM, len(yev)))
            rshare = m[rc].mean(axis=1)
            _, _, rr = lag_share(yev, mask, L, Y0, Y1)
            out[str(L)] = {"share": share, "share_years": float(m.mean()), "rate_ratio": rr,
                           "shift_pct": float(np.mean(null < share)),
                           "random_mean": float(rshare.mean()), "random_sd": float(rshare.std()),
                           "random_pct": float(np.mean(rshare < share))}
            maxobs = max(maxobs, share - m.mean())
        # max-over-lags (excess share over mask fraction) vs circular-shift null
        maxn = []
        for s in range(10, 109):
            best = -1
            for L in range(10):
                m = np.roll(np.array([mask[y - L] for y in range(Y0, Y1 + 1)]), s)
                best = max(best, (cnt * m).sum() / cnt.sum() - m.mean())
            maxn.append(best)
        out["max_over_lags_excess"] = float(maxobs)
        out["max_over_lags_shift_pct"] = float(np.mean(np.array(maxn) < maxobs))
        return out

    res["P3_raw"] = p3(ev, 7.0)
    res["P3_declustered"] = p3(ev_d, 7.0)

    # P3 known-answer: synthetic catalog with x1.25 rate at lag 5
    m5 = np.array([mask[y - 5] for y in range(Y0, Y1 + 1)])
    syn_counts = rng.poisson(lam0 * 20 * np.where(m5 == 1, 1.25, 1.0))  # large catalog to see the peak clearly
    syn_years = np.repeat(np.arange(Y0, Y1 + 1), syn_counts)
    curve = {}
    for L in range(10):
        s, f, rr = lag_share(list(syn_years), mask, L, Y0, Y1)
        curve[str(L)] = rr
    res["P3_injection_rate_ratio_by_lag"] = curve
    res["P3_injection_peak_lag"] = int(max(curve, key=lambda x: curve[x]))
    res["counts_1900_2025"] = {str(y): v for y, v in annual_counts(ev, 7.0, 1900, 2025).items()}
    res["counts_declustered_1900_2025"] = {str(y): v for y, v in annual_counts(ev_d, 7.0, 1900, 2025).items()}
    return res


def write_additions(ev, mask, mask04, res, annual):
    """Write-stage additions (2026-11-25). Own generator: the solve-stage numbers do not change."""
    g = np.random.default_rng(20261125)
    lam0, k, N = res["baseline"]["lambda0"], res["baseline"]["k"], res["P1"]["N"]
    out = {}
    # P1 decision thresholds: largest N that gives REFUTED, smallest N that gives SUPPORTED
    out["P1_refuted_if_N_le"] = max(n for n in range(200) if p1(n, lam0, k)[0] < 0.05)
    out["P1_supported_if_N_ge"] = min(n for n in range(200) if p1(n, lam0, k)[1] < 0.05)
    # forecast-level sensitivity of p_refute (primary baseline and window)
    out["p_refute_by_level"] = {f"{r:.2f}": p1(N, lam0, k, level=r * lam0)[0]
                                for r in (1.10, 1.13, 1.20, 1.25, 1.30, 1.33, 1.34)}
    out["level_17_as_ratio"] = 17.0 / lam0
    out["rate_1900_1972"] = sum(annual_counts(ev, 7.0, 1900, 1972).values()) / 73
    # P2 power and false-positive rate with the pre-registered 10 000 simulations (vectorised permutation test)
    yrs = list(range(HOLD[0], HOLD[1] + 1)); lab = np.array([mask[y - 5] for y in yrs])
    n, kk = len(yrs), int(lab.sum())
    L = np.zeros((math.comb(n, kk), n))
    for i, comb in enumerate(itertools.combinations(range(n), kk)):
        L[i, list(comb)] = 1
    def pvals(c):  # c: (sims, n) -> exact one-sided permutation p for the true labels
        D = c @ L.T / kk - c @ (1 - L).T / (n - kk)
        obs = c[:, lab == 1].mean(1) - c[:, lab == 0].mean(1)
        return (D >= obs[:, None] - 1e-12).mean(1)
    nsim = 10_000
    for name, mult in (("P2_power_x1.25_nsim10000", 1.25), ("P2_false_positive_x1.00_nsim10000", 1.0)):
        mean = lam0 * np.where(lab == 1, mult, 1.0)
        c = g.negative_binomial(k, k / (k + mean), (nsim, n)).astype(float)
        out[name] = float(np.mean(pvals(c) < 0.05))
    # placebo windows as a fraction
    pw = res["P1_placebo_windows_1900_2013"]
    out["placebo_supported_fraction"] = pw["SUPPORTED"] / sum(pw.values())
    # C04 mask: years where it differs from the C02 mask, and the P2 lag-5 test with it
    out["c04_mask_years_differ_1963_2024"] = [y for y in range(1963, 2025) if mask04[y] != mask[y]]
    c = annual_counts(ev, 7.0, HOLD[0], HOLD[1])
    lab04 = [mask04[y - 5] for y in yrs]
    d, p, nperm, _ = perm_test([c[y] for y in yrs], lab04)
    out["P2_L5_c04_mask"] = {"enhanced_years": [y for y, l in zip(yrs, lab04) if l], "p_perm": p, "n_perm": nperm}
    out["c02_annual_lod_ms_2010_2025"] = {str(y): annual[y] for y in range(2010, 2026)}
    return out


def flatten(d, p=""):
    out = {}
    for k, v in d.items():
        key = f"{p}.{k}" if p else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--write-expected", action="store_true")
    ap.add_argument("--work", type=Path, default=None)
    a = ap.parse_args()
    work = a.work or Path(tempfile.mkdtemp(prefix="erq-"))
    work.mkdir(parents=True, exist_ok=True)
    ev, h_cat = load_catalog(a.offline, work)
    annual, mask, r04, h_lod, mask04 = load_lod(a.offline, work)
    res = analyse(ev, mask)
    res["lod"] = {"c02_vs_c04_annual_corr_1962_2024": r04,
                  "mask_2005_2025": {str(y): mask[y] for y in range(2005, 2026)},
                  "share_dec_years_1900_2017": float(np.mean([mask[y] for y in range(1900, 2018)]))}
    res["inputs"] = {"comcat_sha256": h_cat, "c02_sha256": h_lod, "n_events": len(ev)}
    res["write_additions"] = write_additions(ev, mask, mask04, res, annual)
    out = work / "results.json"
    out.write_text(json.dumps(res, indent=1, default=float))
    if a.write_expected:
        (DATA / "expected.json").write_text(json.dumps(res, indent=1, default=float))
        print("wrote data/expected.json")
        return 0
    exp = flatten(json.loads((DATA / "expected.json").read_text()))
    got = flatten(json.loads(out.read_text()))
    bad = []
    for key, v in exp.items():
        if key.startswith("inputs.") and "sha" in key:
            if got.get(key) != v:
                print(f"NOTE input changed: {key}")
            continue
        g = got.get(key)
        if isinstance(v, float) and isinstance(g, (float, int)):
            if not (math.isclose(v, g, rel_tol=1e-6, abs_tol=1e-9) or (math.isnan(v) and math.isnan(g))):
                bad.append((key, v, g))
        elif g != v:
            bad.append((key, v, g))
    for b in bad:
        print("MISMATCH", *b)
    print(f"checked {len(exp)} values, {len(bad)} mismatches")
    P = res["P1"]
    print(f"P1: N={P['N']} lambda0={P['lambda0']:.3f} k={P['k']:.2f} ratio={P['ratio']:.3f} "
          f"p_refute={P['p_refute']:.2e} p_support={P['p_support']:.3f} -> {P['verdict']}")
    Q = res["P2"]
    print(f"P2: L=5 enhanced={Q['enhanced_years']} p_perm={Q.get('p_perm')} -> {Q.get('verdict')}")
    W = res["write_additions"]
    print(f"P2 power x1.25 (10 000 simulations) = {W['P2_power_x1.25_nsim10000']:.4f}; "
          f"false-positive rate = {W['P2_false_positive_x1.00_nsim10000']:.4f}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
