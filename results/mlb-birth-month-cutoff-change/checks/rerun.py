"""Reproduce every number of the pre-registered test in PROTOCOL.md.

Usage: python3 -I checks/rerun.py [--cache DIR] [--write-expected]
Downloads MLB Stats API season player lists 1985-2026 and the CDC monthly birth counts
(or reads them from DIR as s1985.json ... s2026.json and cdc_births.csv),
computes the tables and tests, and compares with data/expected.json.
"""
import json, math, os, random, sys, urllib.request
from datetime import date
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASONS = range(1985, 2027)
URL = "https://statsapi.mlb.com/api/v1/sports/1/players?season={}"
# CDC natality counts by year, month, sex (1969-2008), compiled by J. VanderPlas from the
# NCHS natality public-use files. Used only for the exploratory birth-seasonality control.
CDC_URL = "https://raw.githubusercontent.com/jakevdp/data-CDCbirths/master/births.csv"


def load(cache):
    people = {}
    for y in SEASONS:
        path = os.path.join(cache, f"s{y}.json") if cache else None
        if path and os.path.exists(path):
            data = json.load(open(path))
        else:
            data = json.load(urllib.request.urlopen(URL.format(y), timeout=60))
        for p in data["people"]:
            people[p["id"]] = p
    return people


def d(s):
    return date.fromisoformat(s[:10])


def add_years(b, n):
    try:
        return b.replace(year=b.year + n)
    except ValueError:  # Feb 29
        return date(b.year + n, 3, 1)


def cohort(players, lo, hi):
    return [p for p in players if lo <= p["b"] <= hi]


def counts(ps, months):
    return sum(1 for p in ps if p["b"].month in months)


def fisher_greater(a, b, c, e):
    """One-sided Fisher exact p for OR>1 in table [[a,b],[c,e]], exact rationals."""
    r1, c1, n = a + b, a + c, a + b + c + e
    tot = math.comb(n, c1)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    num = sum(math.comb(r1, k) * math.comb(n - r1, c1 - k) for k in range(a, hi + 1))
    return Fraction(num, tot)


def fisher_two(a, b, c, e):
    r1, c1, n = a + b, a + c, a + b + c + e
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    pk = {k: math.comb(r1, k) * math.comb(n - r1, c1 - k) for k in range(lo, hi + 1)}
    obs = pk[a]
    return Fraction(sum(v for v in pk.values() if v <= obs), math.comb(n, c1))


def binom_two(x, n):
    pk = [math.comb(n, k) for k in range(n + 1)]
    return Fraction(sum(v for v in pk if v <= pk[x]), 2 ** n)


def ortest(tA, tB, cA, cB):
    lor = math.log((tA / tB) / (cA / cB))
    se = math.sqrt(1 / tA + 1 / tB + 1 / cA + 1 / cB)
    return lor, lor - 1.96 * se, lor + 1.96 * se


def us_male_births(cache):
    import csv, io
    path = os.path.join(cache, "cdc_births.csv") if cache else None
    if path and os.path.exists(path):
        text = open(path).read()
    else:
        text = urllib.request.urlopen(CDC_URL, timeout=60).read().decode()
    m = {}
    for r in csv.DictReader(io.StringIO(text)):
        if r["gender"] == "M":
            k = (int(r["year"]), int(r["month"]))
            m[k] = m.get(k, 0) + int(r["births"])
    return m


def seasonality(m, A, B):
    """Expected OR if MLB players were drawn in proportion to US male births by month."""
    def win(lo, hi):
        a = sum(v for k, v in m.items() if lo <= k <= hi and k[1] in A)
        b = sum(v for k, v in m.items() if lo <= k <= hi and k[1] in B)
        return a, b
    cA, cB = win((1976, 8), (1992, 7))
    tA, tB = win((1996, 5), (2001, 4))
    return {"births_B_over_A_C": round(cB / cA, 4), "births_B_over_A_T": round(tB / tA, 4),
            "expected_OR_from_births": round((tA / tB) / (cA / cB), 4)}


def ab(bs, A, B):
    return sum(b.month in A for b in bs), sum(b.month in B for b in bs)


def sel(rows, lo, hi, age=25, us=True):
    return [b for u, b, deb in rows if u == us and lo <= b <= hi and deb < add_years(b, age)]


def table(T, C, A, B, two=False):
    ta, tb = ab(T, A, B)
    ca, cb = ab(C, A, B)
    lor, lo, hi = ortest(ta, tb, ca, cb)
    f = fisher_two if two else fisher_greater
    return {"A_T": ta, "B_T": tb, "A_C": ca, "B_C": cb, "OR": round(math.exp(lor), 3),
            "ci95_OR": [round(math.exp(lo), 3), round(math.exp(hi), 3)],
            ("fisher_p_two" if two else "fisher_p_greater"): round(float(f(ta, tb, ca, cb)), 4)}


def trend(groups):
    """Cochran-Armitage trend test: share of A among A+B against the score of each group."""
    N = sum(a + b for _, a, b in groups)
    pbar = sum(a for _, a, _ in groups) / N
    sbar = sum(s * (a + b) for s, a, b in groups) / N
    T = sum(s * a for s, a, _ in groups) - pbar * sum(s * (a + b) for s, a, b in groups)
    V = pbar * (1 - pbar) * sum((a + b) * (s - sbar) ** 2 for s, a, b in groups)
    z = T / math.sqrt(V)
    return {"z": round(z, 3), "p_two": round(math.erfc(abs(z) / math.sqrt(2)), 4)}


def exploratory(rows, A, B):
    """Exploratory numbers added after verify round 1. Not pre-registered."""
    Clo, Chi, Tlo, Thi = date(1976, 8, 1), date(1992, 7, 31), date(1996, 5, 1), date(2001, 4, 30)
    C, T = sel(rows, Clo, Chi), sel(rows, Tlo, Thi)
    G = sel(rows, date(1992, 8, 1), date(1995, 7, 31))
    e = {}
    e["bins_4yr"] = []
    for y in range(1968, 1997, 4):
        a, b = ab(sel(rows, date(y, 8, 1), date(y + 4, 7, 31)), A, B)
        e["bins_4yr"].append({"born": f"{y}-08..{y + 4}-07", "A": a, "B": b, "B_over_A": round(b / a, 2)})
    e["single_years"] = []
    for y in range(1988, 2000):
        a, b = ab(sel(rows, date(y, 8, 1), date(y + 1, 7, 31)), A, B)
        e["single_years"].append({"born": f"{y}-08..{y + 1}-07", "A": a, "B": b})
    e["gap_vs_C"] = table(G, C, A, B)
    e["T_vs_gap"] = table(T, G, A, B)
    e["T_vs_lateC_1984_92"] = table(T, sel(rows, date(1984, 8, 1), Chi), A, B)
    ta, tb = ab(T, A, B)
    se = math.sqrt(1 / ta + 1 / tb)
    e["T_ratio_B_over_A"] = {"ratio": round(tb / ta, 3),
                             "ci95": [round(tb / ta * math.exp(-1.96 * se), 3),
                                      round(tb / ta * math.exp(1.96 * se), 3)]}
    e["debut_age"] = {}
    for age, thi in ((22, Thi), (23, Thi), (24, Thi), (25, Thi),
                     (26, date(2000, 4, 30)), (27, date(1999, 4, 30))):
        e["debut_age"][f"before_{age}"] = table(sel(rows, Tlo, thi, age), sel(rows, Clo, Chi, age), A, B)
    e["non_us_born"] = table(sel(rows, Tlo, Thi, us=False), sel(rows, Clo, Chi, us=False), A, B, two=True)
    e["month_groups"] = {"Jul_vs_Aug": table(T, C, {7}, {8}),
                         "JunJul_vs_AugSep": table(T, C, {6, 7}, {8, 9}),
                         "AprJul_vs_AugNov": table(T, C, {4, 5, 6, 7}, {8, 9, 10, 11})}
    e["leave_one_T_year_out_p"] = {}
    for y in range(1996, 2001):
        Tm = [b for b in T if not (date(y, 5, 1) <= b <= date(y + 1, 4, 30))]
        e["leave_one_T_year_out_p"][f"drop_{y}-05..{y + 1}-04"] = table(Tm, C, A, B)["fisher_p_greater"]
    groups = []
    for y in range(1976, 1992):
        a, b = ab(sel(rows, date(y, 8, 1), date(y + 1, 7, 31)), A, B)
        groups.append((y, a, b))
    e["pretrend_C_single_years"] = trend(groups)
    return e


def main():
    cache = None
    if "--cache" in sys.argv:
        cache = sys.argv[sys.argv.index("--cache") + 1]
    raw = load(cache)
    players, players26 = [], []
    for p in raw.values():
        if p.get("birthCountry") != "USA" or not p.get("birthDate") or not p.get("mlbDebutDate"):
            continue
        b, deb = d(p["birthDate"]), d(p["mlbDebutDate"])
        if deb < add_years(b, 25):  # equal-exposure rule
            players.append({"b": b})
        if deb < add_years(b, 26):  # exploratory variant, not pre-registered
            players26.append({"b": b})
    rows = [(p.get("birthCountry") == "USA", d(p["birthDate"]), d(p["mlbDebutDate"]))
            for p in raw.values() if p.get("birthDate") and p.get("mlbDebutDate")]
    A, B = {5, 6, 7}, {8, 9, 10}
    PA, PB = {11, 12, 1}, {2, 3, 4}
    C = cohort(players, date(1976, 8, 1), date(1992, 7, 31))
    T = cohort(players, date(1996, 5, 1), date(2001, 4, 30))
    C1 = cohort(players, date(1976, 8, 1), date(1984, 7, 31))
    C2 = cohort(players, date(1984, 8, 1), date(1992, 7, 31))
    out = {"n_C": len(C), "n_T": len(T)}
    out["months_C"] = [counts(C, {m}) for m in range(1, 13)]
    out["months_T"] = [counts(T, {m}) for m in range(1, 13)]
    tA, tB, cA, cB = counts(T, A), counts(T, B), counts(C, A), counts(C, B)
    lor, lo, hi = ortest(tA, tB, cA, cB)
    rC = cB / cA
    out["primary"] = {"A_T": tA, "B_T": tB, "A_C": cA, "B_C": cB,
                      "log_OR": round(lor, 4), "ci95": [round(lo, 4), round(hi, 4)],
                      "fisher_p_greater": float(fisher_greater(tA, tB, cA, cB)),
                      "r_C": round(rC, 4), "log_rC_half_transfer": round(math.log(rC), 4),
                      "full_transfer_logOR": round(2 * math.log(rC), 4)}
    # placebo 1: split control
    a, b_, c, e = counts(C2, A), counts(C2, B), counts(C1, A), counts(C1, B)
    l1 = ortest(a, b_, c, e)
    out["placebo_split"] = {"A_C2": a, "B_C2": b_, "A_C1": c, "B_C1": e,
                            "log_OR": round(l1[0], 4), "ci95": [round(l1[1], 4), round(l1[2], 4)],
                            "fisher_p_greater": float(fisher_greater(a, b_, c, e))}
    # placebo 2: other months
    a, b_, c, e = counts(T, PA), counts(T, PB), counts(C, PA), counts(C, PB)
    l2 = ortest(a, b_, c, e)
    out["placebo_months"] = {"NDJ_T": a, "FMA_T": b_, "NDJ_C": c, "FMA_C": e,
                             "log_OR": round(l2[0], 4), "ci95": [round(l2[1], 4), round(l2[2], 4)],
                             "fisher_p_two": float(fisher_two(a, b_, c, e))}
    # shuffle
    labels = [1] * (tA + tB) + [0] * (cA + cB)
    grp = [1] * tA + [0] * tB + [1] * cA + [0] * cB
    rng = random.Random(20261128)
    ge = 0
    for _ in range(20000):
        rng.shuffle(labels)
        ta = sum(1 for l, g in zip(labels, grp) if l and g)
        tb = (tA + tB) - ta
        ca = (tA + cA) - ta
        cb = (tB + cB) - tb
        if min(ta, tb, ca, cb) > 0 and math.log((ta / tb) / (ca / cb)) >= lor - 1e-12:
            ge += 1
    out["shuffle_p_greater"] = round((ge + 1) / 20001, 4)
    aug, jul = out["months_C"][7], out["months_C"][6]
    out["known_answer"] = {"aug_C": aug, "jul_C": jul, "binom_p_two": float(binom_two(aug, aug + jul))}
    # exploratory (not pre-registered): debut before age 26, T born 1996-05-01..2000-04-30
    C26 = cohort(players26, date(1976, 8, 1), date(1992, 7, 31))
    T26 = cohort(players26, date(1996, 5, 1), date(2000, 4, 30))
    a, b_, c, e = counts(T26, A), counts(T26, B), counts(C26, A), counts(C26, B)
    l3 = ortest(a, b_, c, e)
    out["exploratory_age26"] = {"A_T": a, "B_T": b_, "A_C": c, "B_C": e,
                                "log_OR": round(l3[0], 4), "ci95": [round(l3[1], 4), round(l3[2], 4)],
                                "fisher_p_greater": float(fisher_greater(a, b_, c, e))}
    out["exploratory_verify_round1"] = exploratory(rows, A, B)
    out["exploratory_verify_round1"]["us_birth_seasonality"] = seasonality(us_male_births(cache), A, B)
    p = out["primary"]
    support = p["fisher_p_greater"] < 0.05 and out["placebo_split"]["fisher_p_greater"] >= 0.05
    refute = p["ci95"][1] < p["log_rC_half_transfer"]
    out["decision"] = "SUPPORT" if support else ("REFUTE" if refute else "INCONCLUSIVE")
    print(json.dumps(out, indent=1))
    exp_path = os.path.join(ROOT, "data", "expected.json")
    if "--write-expected" in sys.argv:
        os.makedirs(os.path.dirname(exp_path), exist_ok=True)
        json.dump(out, open(exp_path, "w"), indent=1)
        return
    exp = json.load(open(exp_path))
    ok = json.dumps(exp, sort_keys=True) == json.dumps(out, sort_keys=True)
    print("MATCH expected.json" if ok else "MISMATCH expected.json")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
