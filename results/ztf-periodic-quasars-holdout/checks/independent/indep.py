"""Independent recomputation (verifier). Does not import the solver's code."""
import sys, json, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
from scipy import stats
LC, TABLE = sys.argv[1], sys.argv[2]
tab = pd.read_csv(TABLE)

def bins(d):
    d = d.copy()
    if len(d) >= 20:
        x = (d.mjd - d.mjd.mean()) / (d.mjd.max() - d.mjd.min()) * 2
        c = np.polynomial.legendre.legfit(x, d.mag, 15)
        r = d.mag - np.polynomial.legendre.legval(x, c)
        d = d[np.abs(r) <= 3 * r.std()]
    g = d.groupby(np.floor((d.mjd - 58194.0) / 20.0))
    return g.mjd.mean().values, g.mag.mean().values

def one(path, inj=None):
    d = pd.read_csv(path)
    for c in ("mjd", "mag", "magerr", "catflags", "programid"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[(d.filtercode == "zr") & (d.catflags == 0) & (d.magerr > 0)].sort_values("mjd")
    if inj is not None:
        P0, a, b = inj
        d = d.assign(mag=d.mag + a*np.cos(2*np.pi*d.mjd/P0) + b*np.sin(2*np.pi*d.mjd/P0))
    tr = d[(d.mjd >= 58194) & (((d.programid == 1) & (d.mjd <= 59647)) | (d.programid.isin([2, 3]) & (d.mjd <= 59159)))]
    te = d[(d.mjd > 59647) & (d.mjd <= 60970)]
    leak = int(((tr.mjd > 59647).sum()))
    t, y = bins(tr); tt, yt = bins(te)
    if len(t) < 40 or len(tt) < 10:
        return dict(ntr=len(t), nte=len(tt), ok=False)
    T = t.max() - t.min()
    f = np.arange(1/T, 1/50, 1/(10*T))
    pw = LombScargle(t, y, fit_mean=True, center_data=True).power(f)
    P = 1/f[np.argmax(pw)]
    X = np.c_[np.ones_like(t), np.cos(2*np.pi*t/P), np.sin(2*np.pi*t/P)]
    co, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ co
    xi = (co[1]**2 + co[2]**2) / (2*res.var())
    s = co[1]*np.cos(2*np.pi*tt/P) + co[2]*np.sin(2*np.pi*tt/P)
    k = stats.linregress(s, yt).slope
    r = stats.pearsonr(s, yt)[0]
    return dict(ntr=len(t), nte=len(tt), ok=True, P=P, amp=np.hypot(co[1], co[2]), xi=xi, k=k, r=r,
                tmax_tr=t.max(), tmin_te=tt.min(), tmax_te=te.mjd.max(), leak=leak, co=co)

rows = []
for r_ in tab[tab.kind.isin(["cand", "plac"])].itertuples():
    try:
        o = one(f"{LC}/{r_.id}.csv")
    except Exception as e:
        o = dict(ok=False, err=str(e)[:60])
    o.update(id=r_.id, kind=r_.kind, status=r_.status, P_s=r_.P, k_s=r_.k, xi_s=r_.xi, amp_s=r_.amp, p_drw=r_.p_drw)
    rows.append(o)
df = pd.DataFrame(rows)
ok = df[df.ok == True]
print("status agreement:", ((df.ok == True) == (df.status == "ok")).mean(), "n ok", len(ok), ok.kind.value_counts().to_dict())
for c, s in (("P", "P_s"), ("k", "k_s"), ("xi", "xi_s"), ("amp", "amp_s")):
    rel = np.abs(ok[c] - ok[s]) / np.maximum(np.abs(ok[s]), 1e-9)
    print(c, "max rel diff %.3g" % rel.max(), "median %.3g" % rel.median(), "n>1e-3:", int((rel > 1e-3).sum()), "max abs diff %.3g" % np.abs(ok[c]-ok[s]).max())
print("train leak epochs:", ok.leak.sum(), " max train bin t:", ok.tmax_tr.max(), " min test bin t:", ok.tmin_te.min(), " max test epoch:", ok.tmax_te.max())
c, p = ok[ok.kind == "cand"], ok[ok.kind == "plac"]
NC, NP = int((c.p_drw < 0.05).sum()), int((p.p_drw < 0.05).sum())
print("T1", NC, len(c), stats.binomtest(NC, len(c), 0.05, alternative="greater").pvalue)
print("T2", NP, len(p), stats.fisher_exact([[NC, len(c)-NC], [NP, len(p)-NP]], alternative="greater")[1])
print("median k cand/plac", c.k.median(), p.k.median(), "MW", stats.mannwhitneyu(c.k, p.k, alternative="greater").pvalue)
print("median r cand/plac", c.r.median(), p.r.median(), "MW r", stats.mannwhitneyu(c.r, p.r, alternative="greater").pvalue)
print("frac k>0 cand", (c.k > 0).mean(), "binom vs 0.5:", stats.binomtest(int((c.k > 0).sum()), len(c), 0.5, alternative="greater").pvalue)
# model-free permutation null: time-reverse / sign-flip of template gives symmetric null; Wilcoxon signed-rank on k
print("Wilcoxon signed-rank k>0 cand:", stats.wilcoxon(c.k, alternative="greater").pvalue, " plac:", stats.wilcoxon(p.k, alternative="greater").pvalue)
# my own injection: candidate template into first matched placebo; report P recovery
plac = pd.read_csv(sys.argv[3]); first = plac.groupby("match").first().reset_index()
cm = df.set_index("id")
out = []
for r_ in first.itertuples():
    cr = cm.loc[r_.match]
    if not cr.ok: continue
    o = one(f"{LC}/{r_.id}.csv", inj=(cr.P, cr.co[1], cr.co[2]))
    if o["ok"]:
        out.append(dict(P0=cr.P, P=o["P"], k=o["k"], amp0=cr.amp, amp=o["amp"]))
inj = pd.DataFrame(out)
rec = np.abs(inj.P/inj.P0 - 1) < 0.1
print("injection n", len(inj), "median k", inj.k.median(), "P recovered within 10%:", rec.mean(), "median k | recovered", inj.k[rec].median(), "| not", inj.k[~rec].median(), "median amp/amp0", (inj.amp/inj.amp0).median())
sinj = tab[tab.kind == "inj"]; sinj = sinj[sinj.status == "ok"]
print("solver injection n", len(sinj), "median k", sinj.k.median())
rel = np.abs(ok.k - ok.k_s)
print("objects with |dk|>1e-3:", ok[rel > 1e-3][["id", "k", "k_s", "p_drw"]].round(4).values.tolist())
