"""Verifier's extra checks on the stream.py output (2013-2015): round-number control by year,
primary with covariates, player fixed effects, and a donut. Not pre-registered. Usage: python extra.py A_NPZ"""
import sys, numpy as np, pandas as pd, statsmodels.api as sm
z = np.load(sys.argv[1]); NONE = -10**9
d = pd.DataFrame({k: z[k] for k in z.files})
d = d[(d.elig == 1) & (d.dsec != NONE) & (d.r != NONE) & (d.pb != NONE)].copy()
d["x"] = d.r - d.pb
d["quit"] = ((d.next == NONE) | ((d.next - d.ts) > 3600 + d.dsec)).astype(float)
d["yr"] = pd.to_datetime(d.ts, unit="s").dt.year

def rd(c, y, g, h=15, cov=None):
    m = np.abs(c) < h; c, y, g = c[m], y[m], g[m]; t = (c > 0) * 1.0
    cols = [np.ones(len(c)), t, c, t * c] + ([] if cov is None else [v[m] for v in cov])
    f = sm.WLS(y, np.column_stack(cols), weights=1 - np.abs(c) / h).fit(cov_type="cluster", cov_kwds={"groups": g})
    return f"{100*f.params[1]:+.3f} pp (se {100*f.bse[1]:.3f}) n {len(y)}"

rn = ((d.r + 50) % 100) - 50
for y in (2013, 2014, 2015):
    s = d[d.yr == y]
    print("round number", y, rd(rn[d.yr == y].to_numpy(float) + 0.5, s.quit.to_numpy(), s.pid.to_numpy()))
f = d[d.mask0 == 1]
a = lambda s: s.to_numpy(float)
print("primary + covariates gain, oppdiff, log idx:",
      rd(a(f.x) - 0.5, a(f.quit), f.pid.to_numpy(), cov=[a(f.r - f.pre), a(f.opp - f.pre), np.log(a(f.idx))]))
m = (f.x - 0.5).abs() < 15; g = f[m].copy(); c = a(g.x) - 0.5; w = 1 - np.abs(c) / 15; t = (c > 0) * 1.0
X = pd.DataFrame({"t": t, "c": c, "tc": t * c, "y": a(g.quit), "w": w, "pid": g.pid.to_numpy()})
for col in ("t", "c", "tc", "y"):
    X[col + "w"] = X[col] * X.w
sw = X.groupby("pid").w.transform("sum")
for col in ("t", "c", "tc", "y"):
    X[col] = X[col] - X.groupby("pid")[col + "w"].transform("sum") / sw
fit = sm.WLS(X.y, X[["t", "c", "tc"]], weights=X.w).fit(cov_type="cluster", cov_kwds={"groups": X.pid})
print("primary with player fixed effects: %+.3f pp (se %.3f)" % (100 * fit.params["t"], 100 * fit.bse["t"]))
k = (f.x != 0) & (f.x != 1)
print("donut (drop x=0,1):", rd(a(f.x[k]) - 0.5, a(f.quit[k]), f.pid[k].to_numpy()))
