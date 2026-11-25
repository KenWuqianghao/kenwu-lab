"""Pre-registered analysis (PROTOCOL.md sections 5-7).

Usage: python analyze.py PLAYER_GAMES_PARQUET OUT_JSON
Env: TS_FROM, TS_TO (optional start-time window of the observations, for addendum A).
"""
import sys, os, json
import numpy as np
import duckdb

src, out = sys.argv[1], sys.argv[2]
SEED = 12345
FICS_JUMP = 0.045

TS_FROM = os.environ.get("TS_FROM", "2000-01-01 00:00:00")
TS_TO = os.environ.get("TS_TO", "2100-01-01 00:00:00")
con = duckdb.connect()
con.execute("SET memory_limit='1000MB'; SET threads=1")
WHERE = f"ts >= TIMESTAMP '{TS_FROM}' AND ts <= TIMESTAMP '{TS_TO}'"
# Sample counts over all rows of the window.
SAMPLE = con.sql(f"""SELECT count(*), count(*) FILTER (WHERE speed = 'Blitz' AND pb_prev20 = 0 AND dsec IS NOT NULL),
  count(*) FILTER (WHERE speed = 'Blitz' AND pb_prev20 = 0 AND dsec IS NOT NULL AND x >= 1),
  count(DISTINCT pid) FILTER (WHERE speed = 'Blitz' AND pb_prev20 = 0 AND dsec IS NOT NULL)
  FROM '{src}' WHERE {WHERE}""").fetchall()[0]


def load(cond):
    """Rows of the window that satisfy cond, sorted by player and game, with derived columns."""
    d = con.sql(f"""SELECT pid, speed, tourn, dsec, pre, r, opp, idx, pb_prev20, x, prev_gap_min, next_gap_min
      FROM '{src}' WHERE {WHERE} AND dsec IS NOT NULL AND {cond}""").to_arrow_table().to_pandas()
    d = d.sort_values(["pid", "speed", "idx"], kind="stable").reset_index(drop=True)
    d["quit60"] = (d.next_gap_min.isna() | (d.next_gap_min > 60 + d.dsec / 60.0)).astype(float)
    d["quit24h"] = (d.next_gap_min.isna() | (d.next_gap_min > 1440 + d.dsec / 60.0)).astype(float)
    d["quit90s"] = (d.next_gap_min.isna() | (d.next_gap_min > 90)).astype(float)
    d["gain"] = (d.r - d.pre).astype(float)
    d["oppdiff"] = (d.opp - d.pre).astype(float)
    d["log_prev_gap"] = np.log1p(d.prev_gap_min)
    d["log_idx"] = np.log(d.idx.astype(float))
    return d.drop(columns=["dsec", "pre", "opp", "idx", "prev_gap_min", "next_gap_min", "pb_prev20"])


# Only rows that some estimate uses are loaded. PB sample: x in [-70, 30] holds all PB estimates,
# placebos and bins. Round-number control: Blitz rows within 15 points of a round number.
df = load("pb_prev20 = 0 AND x BETWEEN -70 AND 30")
rn = con.sql(f"""SELECT pid, ((r + 50) % 100) - 50 d,
      (next_gap_min IS NULL OR next_gap_min > 60 + dsec / 60.0)::DOUBLE quit60
    FROM '{src}' WHERE {WHERE} AND dsec IS NOT NULL AND speed = 'Blitz'
      AND abs(((r + 50) % 100) - 50 + 0.5) < 15
    ORDER BY pid, idx""").fetchnumpy()
rn_d, rn_y, rn_g = rn["d"].astype(float), rn["quit60"], rn["pid"]
del rn


def rd(c, y, groups, h, covar=None, chunk=1_000_000):
    """Local linear RD at c = 0 with a triangular kernel; treatment is c > 0.
    Standard error clustered by groups (rows must be sorted by group). Sums are taken in chunks
    of about `chunk` rows, split at group boundaries, to bound memory.
    Returns jump, clustered SE, left limit, n, number of clusters."""
    m = np.abs(c) < h
    c, y, g = c[m], y[m], groups[m]
    cv = None if covar is None else covar[m]
    N = len(y)
    starts = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    G = len(starts)
    cuts = [0]
    while cuts[-1] < N:
        nxt = cuts[-1] + chunk
        cuts.append(N if nxt >= N else int(starts[np.searchsorted(starts, nxt)]) if nxt <= starts[-1] else N)

    def design(i, j):
        cc = c[i:j]
        t = (cc > 0).astype(float)
        cols = [np.ones_like(cc), t, cc, t * cc]
        if cv is not None:
            cols.append(cv[i:j])
        X = np.column_stack(cols)
        return X, X * (1 - np.abs(cc) / h)[:, None]

    XWX = XWy = 0
    for i, j in zip(cuts[:-1], cuts[1:]):
        X, Xw = design(i, j)
        XWX = XWX + X.T @ Xw
        XWy = XWy + Xw.T @ y[i:j]
    A = np.linalg.inv(XWX)
    beta = A @ XWy
    K = len(beta)
    SS = 0
    for i, j in zip(cuts[:-1], cuts[1:]):
        X, Xw = design(i, j)
        s = Xw * (y[i:j] - X @ beta)[:, None]
        st = starts[(starts >= i) & (starts < j)] - i
        S = np.add.reduceat(s, st, axis=0)
        SS = SS + S.T @ S
    V = A @ SS @ A * (G / (G - 1)) * ((N - 1) / (N - K))
    se = float(np.sqrt(V[1, 1]))
    return {"jump": float(beta[1]), "se": se, "ci": [float(beta[1] - 1.96 * se), float(beta[1] + 1.96 * se)],
            "z": float(beta[1] / se), "left_limit": float(beta[0]),
            "relative": float(beta[1] / beta[0]), "n": int(N), "players": int(G)}


def pb_sample(speed, extra=None):
    s = df[df.speed == speed]
    if extra is not None:
        s = s[extra(s)]
    return s


def pb_rd(s, y="quit60", h=15, k=0, side=None, covar=None):
    x = s.x.to_numpy(float)
    keep = np.ones(len(s), bool)
    if side == "left":
        keep = x <= 0
    elif side == "right":
        keep = x >= 1
    c = x[keep] - k - 0.5
    cv = None if covar is None else s[covar].to_numpy(float)[keep]
    return rd(c, s[y].to_numpy(float)[keep], s.pid.to_numpy()[keep], h, cv)


def decision(r):
    lo, hi = r["ci"]
    if lo > 0:
        return "Supported"
    if hi < 0:
        return "Opposite sign"
    if hi < FICS_JUMP:
        return "Null, smaller than FICS"
    return "Inconclusive"


res = {}
blitz = pb_sample("Blitz")
res["sample"] = {
    "player_games_all_speeds_after_rules_2_3_5_6_7": int(SAMPLE[0]),
    "blitz_after_pb_filter": int(SAMPLE[1]),
    "blitz_new_pb_events": int(SAMPLE[2]),
    "blitz_players": int(SAMPLE[3]),
}
prim = pb_rd(blitz)
res["primary"] = prim
res["primary"]["decision"] = decision(prim)
res["primary"]["fics_magnitude_rejected"] = bool(prim["ci"][1] < FICS_JUMP)

# Controls.
res["placebo"] = {f"PB{k:+d}": pb_rd(blitz, k=k, side="left" if k < 0 else "right") for k in (-50, -35, -25, 10)}
res["balance"] = {}
for cov in ("gain", "oppdiff", "log_prev_gap", "log_idx"):
    res["balance"][cov] = pb_rd(blitz, y=cov)

rng = np.random.default_rng(SEED)
m = np.abs(blitz.x.to_numpy(float) - 0.5) < 15
bw = blitz[m]
c = bw.x.to_numpy(float) - 0.5
y = bw.quit60.to_numpy(float)
g = bw.pid.to_numpy()
perm_jumps = []
for _ in range(200):
    order = np.lexsort((rng.random(len(y)), g))  # shuffle within player; g stays sorted
    perm_jumps.append(rd(c, y[order], g, 15)["jump"])
perm_jumps = np.array(perm_jumps)
res["shuffle"] = {"n_perm": 200, "mean": float(perm_jumps.mean()), "sd": float(perm_jumps.std(ddof=1)),
                  "p_two_sided": float((np.abs(perm_jumps) >= abs(prim["jump"])).mean())}

right = c > 0
q = FICS_JUMP / (1 - y[right].mean())
y_inj = y.copy()
flip = right & (y == 0) & (rng.random(len(y)) < q)
y_inj[flip] = 1
inj = rd(c, y_inj, g, 15)
inj["true_added_pp"] = FICS_JUMP
inj["recovered_minus_primary"] = inj["jump"] - prim["jump"]
inj["mde_80pct_power"] = 2.8 * prim["se"]
res["injection"] = inj

res["round_number"] = rd(rn_d + 0.5, rn_y, rn_g, 15)

# Robustness and secondary.
rob = {}
rob["quit_24h"] = pb_rd(blitz, y="quit24h")
rob["quit_90min_start_to_start"] = pb_rd(blitz, y="quit90s")
rob["h10"] = pb_rd(blitz, h=10)
rob["h25"] = pb_rd(blitz, h=25)
rob["no_tournament"] = pb_rd(pb_sample("Blitz", lambda s: ~s.tourn))
rob["gain_covariate"] = pb_rd(blitz, covar="gain")
rob["bullet"] = pb_rd(pb_sample("Bullet"))
rob["classical"] = pb_rd(pb_sample("Classical"))
a0 = blitz[blitz.x == 0].quit60
a1 = blitz[blitz.x == 1].quit60
rob["adjacent_bins_x0_x1"] = {"quit_x0": float(a0.mean()), "quit_x1": float(a1.mean()), "n_x0": int(len(a0)),
                              "n_x1": int(len(a1)), "diff": float(a1.mean() - a0.mean()),
                              "se": float(np.sqrt(a0.var() / len(a0) + a1.var() / len(a1)))}
res["robustness"] = rob

# Binned quit rates for the figure (not used for any decision).
bins = blitz[(blitz.x >= -30) & (blitz.x <= 20)].groupby("x").quit60.agg(["mean", "count"])
res["bins_blitz"] = {int(k): [float(v["mean"]), int(v["count"])] for k, v in bins.iterrows()}

json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("sample", "primary")}, indent=1))
