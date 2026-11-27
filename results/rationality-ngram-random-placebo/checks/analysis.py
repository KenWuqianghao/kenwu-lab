"""Pre-registered analysis (PROTOCOL.md). Usage: python analysis.py <table.npz> <out.json> [authors_repo_dir] [figdir]"""
import sys, json, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wordsets import A, B, A_ALL, B_ALL, NOT_IN_5000

TAB, OUT = sys.argv[1], sys.argv[2]
REPO = sys.argv[3] if len(sys.argv) > 3 else None
FIG = sys.argv[4] if len(sys.argv) > 4 else None
YEARS = np.arange(1850, 2020)
NPOOL, NPL = 20000, 10000
K = int(os.environ.get("MATCH_K", "40"))  # pre-registered value 40; other values only for post-hoc sensitivity
POSN = ["NOUN", "VERB", "ADJ", "ADV", "OTHER"]

z = np.load(TAB)
words = list(z["words"]); idx = {w: i for i, w in enumerate(words)}
E = z["eng"].astype(np.float64); Fc = z["fic"].astype(np.float64)
Ne, Nf = z["Neng"], z["Nfic"]
res = {}

# POS class
Pt = z["pos"]
cls = np.where(Pt[:, 4] > Pt[:, :4].max(1), 4, Pt[:, :4].argmax(1))

# corpora
NF = E - Fc; Nn = Ne - Nf
flag_rows = [idx[w] for w in A + B]
# pool
flags_all = set(A_ALL) | set(B_ALL)
ok = [i for i, w in enumerate(words) if w not in flags_all and w != "an" and len(w) >= 2
      and (E[i] > 0).all() and (Fc[i] > 0).all()]
pool = np.array(ok[:NPOOL])
assert len(pool) == NPOOL
res["pool_size"] = int(len(pool)); res["pool_last_word"] = words[pool[-1]]
res["pool_min_total_eng"] = float(E[pool[-1]].sum())
nonneg = bool((NF[pool] >= 0).all() and (NF[flag_rows] >= 0).all() and (Nn > 0).all())
res["nonfiction_subset_check"] = nonneg
corpora = {"eng": E / Ne, "fiction": Fc / Nf}
if nonneg:
    corpora["nonfiction"] = NF / Nn

# features
Pe = E / Ne
Fw = np.log10(Pe.mean(1))
ref = YEARS <= 1974
with np.errstate(divide='ignore'):
    Sw = np.log(Fc[:, ref].sum(1) / Nf[ref].sum()) - np.log(E[:, ref].sum(1) / Ne[ref].sum())
sdF, sdS = Fw[pool].std(), Sw[pool].std()

def feat(ws):
    r = [idx[w] for w in ws]
    return dict(F=float(Fw[r].mean()), S=float(Sw[r].mean()),
                pos={POSN[c]: int((cls[r] == c).sum()) for c in range(5)})
res["features"] = {"A": feat(A), "B": feat(B),
                   "pool": dict(F=float(Fw[pool].mean()), S=float(Sw[pool].mean()), sdF=float(sdF), sdS=float(sdS))}
res["flag_words"] = {w: dict(F=round(float(Fw[idx[w]]), 4), S=round(float(Sw[idx[w]]), 4), pos=POSN[cls[idx[w]]]) for w in A + B}

# design / statistics
def design(tau):
    t = YEARS - tau
    return np.column_stack([np.ones_like(t), t, np.maximum(0, t)]).astype(float)
X80 = design(1980); PINV = np.linalg.pinv(X80)
TAUS = np.arange(1900, 2001)
QS = np.stack([np.linalg.qr(design(tau))[0] for tau in TAUS])  # (T,170,3)

def stats(L):  # L: (n,170)
    co = L @ PINV.T  # (n,3): a,b,g
    sse = (L ** 2).sum(1)[None, :] - ((np.einsum("tyk,ny->tnk", QS, L)) ** 2).sum(2)
    tau = TAUS[sse.argmin(0)]
    return co[:, 1], co[:, 2], tau

def Lof(Pc, ia, ib):
    return np.log(Pc[ia].mean(0)) - np.log(Pc[ib].mean(0))

iA = np.array([idx[w] for w in A]); iB = np.array([idx[w] for w in B])
obs = {}
for c, Pc in corpora.items():
    L = Lof(Pc, iA, iB)[None]
    b, g, tau = stats(L)
    obs[c] = dict(b=float(b[0]), g=float(g[0]), b_plus_g=float(b[0] + g[0]), tau=int(tau[0]),
                  reversal=bool(b[0] > 0 and b[0] + g[0] < 0), L=L[0].tolist())

# matching
def neighbours(control):
    out = []
    for w in A + B:
        i = idx[w]
        cand = pool[cls[pool] == cls[i]]
        d = np.abs(Fw[cand] - Fw[i]) / sdF
        if control == "FPS":
            d = np.sqrt(d ** 2 + ((Sw[cand] - Sw[i]) / sdS) ** 2)
        out.append(cand[np.argsort(d, kind="stable")[:K]])
    return out

def draw_pairs(control, seed):
    rng = np.random.default_rng(seed); nb = neighbours(control)
    pairs = np.empty((NPL, len(A) + len(B)), dtype=np.int64)
    for k in range(NPL):
        used = set()
        for j, c in enumerate(nb):
            while True:
                w = int(c[rng.integers(len(c))])
                if w not in used: break
            used.add(w); pairs[k, j] = w
    return pairs

def evaluate(pairs, Pc):
    nA = len(A)
    L = np.log(Pc[pairs[:, :nA]].mean(1)) - np.log(Pc[pairs[:, nA:]].mean(1))
    return L, stats(L)

def summary(b, g, tau, gobs, bobs):
    return dict(posthoc_share_b_ge_obs=float((b >= bobs).mean()), p_one_sided=float((1 + (g <= gobs).sum()) / (len(g) + 1)),
                g_q05=float(np.quantile(g, 0.05)), g_median=float(np.median(g)), g_sd=float(g.std()),
                share_reversal=float(((b > 0) & (b + g < 0)).mean()),
                share_tau_1975_1990=float(((tau >= 1975) & (tau <= 1990)).mean()),
                share_g_le_obs=float((g <= gobs).mean()))

tests = {}; keep = {}
for control, seed in [("FP", 20261126), ("FPS", 20261127)]:
    pairs = draw_pairs(control, seed)
    nA = len(A)
    tests[control] = {"match": dict(
        F_A=float(Fw[pairs[:, :nA]].mean()), F_B=float(Fw[pairs[:, nA:]].mean()),
        S_A=float(Sw[pairs[:, :nA]].mean()), S_B=float(Sw[pairs[:, nA:]].mean()),
        distinct_words=int(len(np.unique(pairs))))}
    for c, Pc in corpora.items():
        L, (b, g, tau) = evaluate(pairs, Pc)
        tests[control][c] = summary(b, g, tau, obs[c]["g"], obs[c]["b"])
        keep[(control, c)] = (L, b, g, tau)

# label shuffle on eng
rng = np.random.default_rng(20261128); allf = np.concatenate([iA, iB]); Ls = []
for k in range(NPL):
    perm = rng.permutation(allf); Ls.append(Lof(corpora["eng"], perm[:len(A)], perm[len(A):]))
b, g, tau = stats(np.array(Ls))
tests["label_shuffle"] = {"eng": summary(b, g, tau, obs["eng"]["g"], obs["eng"]["b"])}

# power on eng FPS
L0, b0, g0, _ = keep[("FPS", "eng")]
q05 = np.quantile(g0, 0.05); hinge = np.maximum(0, YEARS - 1980)
power = {}
for name, d in [("d=g_obs", obs["eng"]["g"]), ("d=g_obs/2", obs["eng"]["g"] / 2)]:
    Li = L0[:1000] + d * hinge
    _, gi, _ = stats(Li)
    err = float(np.abs((gi - g0[:1000]) - d).max())
    assert err < 1e-9, err
    power[name] = dict(d=float(d), power=float((gi <= q05).mean()), max_recovery_error=err)
res["power_eng_FPS"] = power

res["observed"] = {c: {k: v for k, v in o.items() if k != "L"} for c, o in obs.items()}
res["tests"] = tests
res["primary"] = dict(corpus="eng", control="FPS", g_obs=obs["eng"]["g"],
                      p=tests["FPS"]["eng"]["p_one_sided"],
                      verdict="SUPPORT" if tests["FPS"]["eng"]["p_one_sided"] < 0.05 else "REFUTATION")

# reproduction checks against the authors' table
if REPO:
    import pandas as pd
    aw = set(pd.read_pickle(os.path.join(REPO, "most_frequent_words/most_frequent_words.pkl"))["eng"])
    assert {w for w in A_ALL + B_ALL if w not in aw} == NOT_IN_5000
    d = pd.read_pickle(os.path.join(REPO, "ngrams_data/words5000eng_all.pkl")).loc[1850:2019]
    rat = d[A].mean(axis=1) / d[B].mean(axis=1)
    ours = np.exp(np.array(obs["eng"]["L"]))
    res["repro"] = dict(r_ratio=float(np.corrcoef(rat.values, ours)[0, 1]),
                        mean_ratio_ours_over_authors=float((ours / rat.values).mean()),
                        words={w: float((E[idx[w]] / d[w].values).mean()) for w in ["an", "science", "god", "feel", "data"]})
    dfc = pd.read_pickle(os.path.join(REPO, "ngrams_data/words5000eng_fic.pkl")).loc[1850:2019]
    ratf = dfc[A].mean(axis=1) / dfc[B].mean(axis=1)
    res["repro"]["r_ratio_fiction"] = float(np.corrcoef(ratf.values, np.exp(np.array(obs["fiction"]["L"])))[0, 1])

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res["primary"], indent=1))

if FIG:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    cs = list(corpora)
    fig, ax = plt.subplots(2, len(cs), figsize=(4.5 * len(cs), 7))
    for j, c in enumerate(cs):
        L, b, g, tau = keep[("FPS", c)]
        Lc = L - L.mean(1, keepdims=True)
        lo, hi = np.quantile(Lc, [0.025, 0.975], axis=0)
        ax[0, j].fill_between(YEARS, lo, hi, color="0.85", label="FPS placebo 95%")
        for k in range(5): ax[0, j].plot(YEARS, Lc[k], color="0.6", lw=0.6)
        Lo = np.array(obs[c]["L"]); ax[0, j].plot(YEARS, Lo - Lo.mean(), "k", lw=1.6, label="rationality/intuition")
        ax[0, j].axvline(1980, ls=":", c="r"); ax[0, j].set_title(c); ax[0, j].set_ylabel("L(t), centred")
        ax[1, j].hist(g * 10, bins=80, color="0.6"); ax[1, j].axvline(obs[c]["g"] * 10, c="k", lw=1.6)
        ax[1, j].set_xlabel("g (slope change at 1980, per decade)")
    ax[0, 0].legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "placebo.png"), dpi=130)
