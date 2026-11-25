"""Verifier's independent RD estimates from the stream.py output."""
import sys, numpy as np, pandas as pd, statsmodels.api as sm
z = np.load(sys.argv[1]); NONE = -10**9
d = pd.DataFrame({k: z[k] for k in z.files})
d = d[(d.elig == 1) & (d.dsec != NONE) & (d.r != NONE) & (d.pb != NONE)].copy()
import os, calendar, time
ep = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M:%S"))
if os.environ.get("TS_FROM"):
    d = d[(d.ts >= ep(os.environ["TS_FROM"])) & (d.ts <= ep(os.environ["TS_TO"]))].copy()
    print("window", os.environ["TS_FROM"], os.environ["TS_TO"])
d["x"] = d.r - d.pb
d["quit"] = ((d.next == NONE) | ((d.next - d.ts) > 3600 + d.dsec)).astype(float)
f = d[d.mask0 == 1]
print("blitz eligible rows (dsec known):", len(d))
print("after PB filter:", len(f), "new PBs:", int((f.x >= 1).sum()), "players:", f.pid.nunique())

def rd(c, y, g, h=15, label=""):
    m = np.abs(c) < h
    c, y, g = c[m], y[m], g[m]
    t = (c > 0).astype(float)
    X = np.column_stack([np.ones(len(c)), t, c, t * c])
    w = 1 - np.abs(c) / h
    fit = sm.WLS(y, X, weights=w).fit(cov_type="cluster", cov_kwds={"groups": g})
    # second route: plain numpy sandwich
    Xw = X * w[:, None]
    A = np.linalg.inv(X.T @ Xw); b = A @ (Xw.T @ y)
    s = pd.DataFrame(Xw * (y - X @ b)[:, None]).groupby(g).sum().to_numpy()
    G, N, K = len(s), len(y), 4
    V = A @ (s.T @ s) @ A * (G / (G - 1)) * ((N - 1) / (N - K))
    print(f"{label:34s} jump {100*fit.params[1]:+.4f} pp  se {100*fit.bse[1]:.4f} (numpy {100*b[1]:+.4f}, {100*np.sqrt(V[1,1]):.4f})  "
          f"CI [{100*(fit.params[1]-1.96*fit.bse[1]):+.3f}, {100*(fit.params[1]+1.96*fit.bse[1]):+.3f}]  left {100*fit.params[0]:.3f}  n {N}  players {G}")
    return fit.params[1], fit.bse[1]

a = lambda s: s.to_numpy(float)
rd(a(f.x) - 0.5, a(f.quit), f.pid.to_numpy(), label="PRIMARY (blitz, h=15)")
rd(a(f.x) - 0.5, a(f.quit), f.pid.to_numpy(), h=10, label="h=10")
rd(a(f.x) - 0.5, a(f.quit), f.pid.to_numpy(), h=25, label="h=25")
rn = ((d.r + 50) % 100) - 50
rd(a(rn) + 0.5, a(d.quit), d.pid.to_numpy(), label="round number control")
# unclustered-kernel-free view: adjacent bins
x0, x1 = f[f.x == 0].quit, f[f.x == 1].quit
print("adjacent bins x=0, x=1:", round(100*x0.mean(), 3), round(100*x1.mean(), 3), len(x0), len(x1))
# alternative 1: PB also counts every pre-game rating seen (catches peaks from games not in the chain)
d2 = d[(d.pb2 != NONE) & (d.mask20 == 1)]
rd(a(d2.r - d2.pb2) - 0.5, a(d2.quit), d2.pid.to_numpy(), label="ALT PB (max of pre and post)")
# alternative 2: post rating = next blitz pre-game rating (when it exists)
f3 = f[f.rnext != NONE]
print("share of bandwidth rows with next pre == pre+diff:",
      round(float((f3.rnext == f3.r)[(f3.x > -15) & (f3.x <= 15)].mean()), 4),
      " |diff|<=1:", round(float(((f3.rnext - f3.r).abs() <= 1)[(f3.x > -15) & (f3.x <= 15)].mean()), 4))
rd(a(f3.rnext - f3.pb) - 0.5, a(f3.quit), f3.pid.to_numpy(), label="ALT r (next blitz pre)")
# both sides consistent: keep only rows where the next pre confirms r
f4 = f3[f3.rnext == f3.r]
rd(a(f4.x) - 0.5, a(f4.quit), f4.pid.to_numpy(), label="rows with confirmed r")
# by year
yr = pd.to_datetime(f.ts, unit="s").dt.year
for y in sorted(yr.unique()):
    s = f[yr == y]
    if ((s.x - 0.5).abs() < 15).sum() > 5000:
        rd(a(s.x) - 0.5, a(s.quit), s.pid.to_numpy(), label=f"year {y}")
# round-number bins
b = d[(rn >= -8) & (rn <= 8)].groupby(rn[(rn >= -8) & (rn <= 8)]).quit.agg(["mean", "count"])
print((b.assign(mean=(100*b["mean"]).round(2))).T.to_string())
b = f[(f.x >= -8) & (f.x <= 8)].groupby("x").quit.agg(["mean", "count"])
print((b.assign(mean=(100*b["mean"]).round(2))).T.to_string())
