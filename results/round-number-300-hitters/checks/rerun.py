"""Reproduce every number of the paper (PROTOCOL.md, addendum 2 included) from public data.

Downloads (cached in DIR, default work/ in the result folder): Retrosheet event files
2009-2025, MLB Stats API season hitting totals 2009-2025, the Chadwick Bureau register
(pinned commit), Lahman Batting/People (mirror, pinned commit). Compares the result with data/expected.json.

Usage: python3 -I checks/rerun.py [--cache DIR] [--write-expected]

Integers and strings must be equal to data/expected.json. Floats must agree to a relative
tolerance of 1e-9 (the last bits of a p-value can depend on the platform).
"""
import csv, hashlib, io, json, math, os, sys, urllib.request, zipfile
from collections import Counter, defaultdict
from scipy.stats import binomtest, fisher_exact, norm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = (sys.argv[sys.argv.index("--cache") + 1] if "--cache" in sys.argv
        else os.path.join(ROOT, "work"))
YEARS = range(2009, 2026)
NO_PA = ("NP", "SB", "CS", "POCS", "PO", "WP", "PB", "BK", "DI", "OA", "FLE")
REGISTER = ("https://raw.githubusercontent.com/chadwickbureau/register/"
            "ba48ce101349a2156c7a5420f54d13e8ef3a4256/data/people-{}.csv")
LAHMAN = ("https://raw.githubusercontent.com/cbwinslow/baseballdatabank/"
          "8a908d51833ee99b56fce165c93dc99ee8886d6f/core/{}.csv")
MLB = ("https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={}"
       "&sportId=1&gameType=R&limit=3000&playerPool=ALL")


def fetch(url, sub, name):
    d = os.path.join(WORK, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    if not os.path.exists(p):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(p + ".part", "wb") as f:
            f.write(r.read())
        os.replace(p + ".part", p)
    return p


def classify(ev):
    """Return None (no PA), or (is_ab, is_hit, is_walk)."""
    main = ev.split(".")[0]
    parts = main.split("/")
    base = parts[0].split("+")[0]
    mods = parts[1:]
    if base.startswith(NO_PA):
        return None
    if base in ("W", "IW", "I") or base.startswith(("W", "IW")):
        return (False, False, True)
    if base.startswith("HP"):
        return (False, False, False)
    if base.startswith("C") and not base.startswith("CS"):  # catcher interference
        return (False, False, False)
    if any(m.startswith(("SH", "SF")) for m in mods):
        return (False, False, False)
    return (True, base.startswith(("S", "D", "T", "H")), False)


def disp(h, ab):
    """Batting average to 3 decimals, round half up, as an integer in thousandths."""
    return (2000 * h + ab) // (2 * ab) if ab else None


def load_events():
    """Per (year, batter): chronological list of (game_key, seq, team, kind, is_ab, is_hit, is_bb).
    kind 'PA' = plate appearance; kind 'SUB' = a pinch hitter took the batter's slot."""
    ev = defaultdict(list)
    team_games = defaultdict(set)
    sha = {}
    n_915b = 0
    for y in YEARS:
        path = fetch(f"https://www.retrosheet.org/events/{y}eve.zip", "raw", f"{y}eve.zip")
        sha[str(y)] = hashlib.sha256(open(path, "rb").read()).hexdigest()
        z = zipfile.ZipFile(path)
        for name in sorted(z.namelist()):
            if not name.endswith((".EVA", ".EVN")):
                continue
            seq = 0
            for f in csv.reader(io.TextIOWrapper(z.open(name), encoding="latin-1")):
                seq += 1
                if not f:
                    continue
                if f[0] == "id":
                    gid, teams, slot, last_np, pend = f[1], {}, {}, None, None
                    key = (gid[3:11], gid[11], gid)  # date, game number
                elif f[0] == "info" and f[1] in ("visteam", "hometeam"):
                    teams["0" if f[1] == "visteam" else "1"] = f[2]
                elif f[0] in ("start", "sub"):
                    pid, side, bo, pos = f[1], f[3], f[4], f[5]
                    if f[0] == "sub" and pos == "11" and bo != "0" and (side, bo) in slot:
                        old = slot[(side, bo)]
                        ev[(y, old)].append((key, seq, teams[side], "SUB", 0, 0, 0))
                        # Rule 9.15(b): pinch hitter enters with two strikes on the batter.
                        if last_np and last_np[0] == old and last_np[1] == side and last_np[2] == "2":
                            pend = (old, pid)
                    if bo != "0":
                        slot[(side, bo)] = pid
                elif f[0] == "play":
                    side, bat, event = f[2], f[3], f[6]
                    team_games[(y, teams[side])].add(key)
                    if event == "NP":
                        last_np = (bat, side, f[4][1:2]) if len(f[4]) == 2 else None
                        continue
                    last_np = None
                    if pend and pend[1] == bat:
                        if event.startswith("K"):
                            bat = pend[0]
                            n_915b += 1
                        pend = None
                    c = classify(event)
                    if c is not None:
                        ev[(y, bat)].append((key, seq, teams[side], "PA") + tuple(int(x) for x in c))
    for k in ev:
        ev[k].sort(key=lambda r: (r[0], r[1]))
    return ev, team_games, sha, n_915b


def official_totals():
    """MLB Stats API (H, AB) by (year, retro id); Lahman (H, AB) by (year, retro id)."""
    m2r = {}
    for h in "0123456789abcdef":
        for r in csv.DictReader(open(fetch(REGISTER.format(h), "val", f"people-{h}.csv"), encoding="utf-8")):
            if r["key_mlbam"] and r["key_retro"]:
                m2r[int(r["key_mlbam"])] = r["key_retro"]
    mlb, unmapped = {}, 0
    for y in YEARS:
        js = json.load(open(fetch(MLB.format(y), "val", f"mlb{y}.json")))
        for sp in js["stats"][0]["splits"]:
            rid = m2r.get(sp["player"]["id"])
            st = (sp["stat"]["hits"], sp["stat"]["atBats"])
            if rid is None:
                unmapped += st[1] >= 200
                continue
            mlb[(y, rid)] = st
    l2r = {r["playerID"]: r["retroID"] for r in
           csv.DictReader(open(fetch(LAHMAN.format("People"), "val", "People.csv"), encoding="latin-1"))}
    lah = defaultdict(lambda: [0, 0])
    for r in csv.DictReader(open(fetch(LAHMAN.format("Batting"), "val", "Batting.csv"), encoding="latin-1")):
        y = int(r["yearID"])
        if y >= 2009:
            t = lah[(y, l2r.get(r["playerID"]))]
            t[0] += int(r["H"] or 0); t[1] += int(r["AB"] or 0)
    return mlb, {k: tuple(v) for k, v in lah.items()}, unmapped


def compare(tot, ref, years):
    keys = sorted(k for k in set(tot) | set(ref) if k[0] in years and
                  max(tot.get(k, (0, 0))[1], ref.get(k, (0, 0))[1]) >= 200)
    bad = [[k[0], k[1], list(tot.get(k, (0, 0))), list(ref.get(k, (0, 0)))]
           for k in keys if tot.get(k, (0, 0)) != ref.get(k, (0, 0))]
    return {"n_compared": len(keys), "n_mismatch": len(bad), "mismatches": bad}


def ztest(x1, n1, x2, n2):
    """Two-proportion Z test, pooled variance, two-sided p."""
    p = (x1 + x2) / (n1 + n2)
    z = (x1 / n1 - x2 / n2) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return round(z, 4), 2 * norm.sf(abs(z))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def t1_block(fin):
    t1 = {}
    for t in range(250, 360, 10):
        t1[str(t)] = {"n_x0": fin[t], "n_x9": fin[t - 1],
                      "ratio": round(fin[t] / fin[t - 1], 4) if fin[t - 1] else None}
    n300, n299 = fin[300], fin[299]
    t1["binom_p_300_vs_299"] = binomtest(n300, n300 + n299, 0.5, alternative="greater").pvalue
    ci = binomtest(n300, n300 + n299).proportion_ci(method="exact")
    t1["ratio_ci95"] = [round(ci.low / (1 - ci.low), 4), round(ci.high / (1 - ci.high), 4)]
    t1["placebo_max_ratio"] = max(v["ratio"] for k, v in t1.items()
                                  if k not in ("300",) and isinstance(v, dict) and v["ratio"] is not None)
    return t1


def same(a, b):
    """Equal JSON values; floats agree to a relative tolerance of 1e-9."""
    if isinstance(a, float) or isinstance(b, float):
        return (isinstance(a, (int, float)) and isinstance(b, (int, float))
                and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-300))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def main():
    ev, team_games, sha, n_915b = load_events()
    pas = {k: [r for r in v if r[3] == "PA"] for k, v in ev.items()}
    pas = {k: v for k, v in pas.items() if v}
    tot = {k: (sum(r[5] for r in v), sum(r[4] for r in v)) for k, v in pas.items()}
    out = {"retrosheet_sha256": sha, "n_rule_9_15b_reassigned": n_915b}

    mlb, lah, unmapped = official_totals()
    out["validation_mlb_api"] = compare(tot, mlb, set(YEARS))
    out["validation_mlb_api"]["n_unmapped_200ab"] = unmapped
    out["validation_lahman"] = compare(tot, lah, set(range(2009, 2022)))

    elig = sorted(k for k, (h, ab) in tot.items() if ab >= 200)
    out["n_eligible"] = len(elig)
    fin = Counter(disp(*tot[k]) for k in elig)
    out["T1"] = t1_block(fin)
    # S1: T1 on official MLB totals
    out["S1_T1_official"] = t1_block(Counter(disp(h, ab) for (h, ab) in mlb.values() if ab >= 200))
    out["S1_T1_official"]["n_eligible"] = sum(1 for (h, ab) in mlb.values() if ab >= 200)

    # Registered T2/T3: last actual PA
    def groups(seqs):
        G = defaultdict(lambda: [0, 0, 0, 0, 0])  # n, AB, H, BB, SUB by entering displayed avg
        who = defaultdict(list)
        for k in elig:
            rows = seqs[k]
            h = sum(r[5] for r in rows[:-1]); ab = sum(r[4] for r in rows[:-1])
            d = disp(h, ab); r = rows[-1]; g = G[d]
            g[0] += 1; g[1] += r[4]; g[2] += r[5]; g[3] += r[6]; g[4] += r[3] == "SUB"
            if d == 299 and r[6]:
                who["walks_at_299"].append([k[0], k[1], r[0][2]])
        return G, who

    def agg(G, ds):
        return [sum(G[d][i] for d in ds) for i in range(5)]

    G, who = groups(pas)
    near = [d for d in range(280, 321)]
    l299, l300 = agg(G, [299]), agg(G, [300])
    lc = agg(G, [d for d in near if d not in (299, 300)])
    for nm, g in (("L299", l299), ("L300", l300), ("LC", lc)):
        out[nm] = dict(zip(["PA", "AB", "H", "BB"], g[:4]))
    out["L299_walkers"] = who["walks_at_299"]
    out["T2_fisher_p"] = fisher_exact([[l299[3], l299[0] - l299[3]], [lc[3], lc[0] - lc[3]]],
                                      alternative="less")[1]
    out["T3_fisher_p"] = fisher_exact([[l299[2], l299[1] - l299[2]], [l300[2], l300[1] - l300[2]]],
                                      alternative="greater")[1]
    # Descriptive: original 0 walks of 61 (paper p. 4) against the held-out walks at .299.
    out["C2_original_0_of_61_vs_heldout_fisher_two_sided"] = fisher_exact(
        [[0, 61], [l299[3], l299[0] - l299[3]]])[1]

    # Addendum 2, item 3: the paper's own comparisons, unit = last scheduled PA
    S, _ = groups(ev)
    a, b = fin[298] + fin[299], fin[300] + fin[301]
    P = {"P1_end_298_299_vs_300_301": {"n_298_299": a, "n_300_301": b, "n_eligible": len(elig),
                                       "binom_p": binomtest(b, a + b, 0.5, alternative="greater").pvalue}}
    spec = [("P2_hit_298_299_vs_300_301", 2, [298, 299], [300, 301], "greater"),
            ("P3_hit_299_vs_others", 2, [299], [d for d in near if d != 299], "greater"),
            ("P4_walk_298_299_vs_300_301", 3, [298, 299], [300, 301], "less"),
            ("P5_sub_298_299_vs_300_301", 4, [298, 299], [300, 301], "less"),
            ("P6_sub_300_vs_others", 4, [300], [d for d in near if d != 300], "greater")]
    fp = []
    for nm, i, d1, d2, alt in spec:
        g1, g2 = agg(S, d1), agg(S, d2)
        z, pz = ztest(g1[i], g1[0], g2[i], g2[0])
        f = fisher_exact([[g1[i], g1[0] - g1[i]], [g2[i], g2[0] - g2[i]]], alternative=alt)[1]
        fp.append(f)
        P[nm] = {"x1": g1[i], "n1": g1[0], "x2": g2[i], "n2": g2[0], "z": z, "z_p_two_sided": pz,
                 "fisher_p_one_sided": f}
    for (nm, *_), h in zip(spec, holm(fp)):
        P[nm]["fisher_p_holm"] = h
    out["paper_comparisons"] = P

    # T4 unbiased sample: all PAs in team's last 2 games
    last2 = {k: set(sorted(v)[-2:]) for k, v in team_games.items()}
    A = [0, 0, 0, 0]; B = [0, 0, 0, 0]
    for k in elig:
        h = ab = 0
        for key, _, team, _, is_ab, is_hit, is_bb in pas[k]:
            if key in last2[(k[0], team)] and ab > 0:
                d = disp(h, ab); g = None
                if d < 300 and disp(h + 1, ab + 1) >= 300:
                    g = B
                elif d >= 300 and disp(h, ab + 1) < 300:
                    g = A
                if g is not None:
                    g[0] += 1; g[1] += is_ab; g[2] += is_hit; g[3] += is_bb
            h += is_hit; ab += is_ab
    out["T4_B_below"] = dict(zip(["PA", "AB", "H", "BB"], B))
    out["T4_A_above"] = dict(zip(["PA", "AB", "H", "BB"], A))
    out["T4_hit_fisher_p"] = fisher_exact([[B[2], B[1] - B[2]], [A[2], A[1] - A[2]]],
                                          alternative="greater")[1]
    out["T4_walk_fisher_p"] = fisher_exact([[B[3], B[0] - B[3]], [A[3], A[0] - A[3]]],
                                           alternative="less")[1]

    # Exit check (descriptive), team's last 3 games, by displayed average after the PA.
    # exit_share_pa: [PAs after which the batter never batted again, PAs].
    # exit_share_batter: [batters whose final PA left them at d, batters who were at d after a PA].
    last3 = {k: set(sorted(v)[-3:]) for k, v in team_games.items()}
    ex = defaultdict(lambda: [0, 0]); exb = defaultdict(lambda: [0, 0])
    for k in elig:
        h = ab = 0; rows = pas[k]; seen = set()
        for i, (key, _, team, _, is_ab, is_hit, _) in enumerate(rows):
            h += is_hit; ab += is_ab
            d = disp(h, ab)
            if key in last3[(k[0], team)] and 280 <= d <= 320:
                ex[d][0] += 1; ex[d][1] += (i == len(rows) - 1)
                seen.add(d)
        for d in seen:
            exb[d][0] += 1; exb[d][1] += (disp(*tot[k]) == d)
    out["exit_share_pa"] = {str(d): [ex[d][1], ex[d][0]] for d in sorted(ex)}
    out["exit_share_batter"] = {str(d): [exb[d][1], exb[d][0]] for d in sorted(exb)}

    js = json.dumps(out, indent=1, sort_keys=True, default=float)
    print(js)
    exp = os.path.join(ROOT, "data", "expected.json")
    if "--write-expected" in sys.argv:
        open(exp, "w").write(js + "\n")
        return
    ok = same(json.loads(js), json.load(open(exp)))
    print("MATCH expected.json" if ok else "MISMATCH expected.json")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
