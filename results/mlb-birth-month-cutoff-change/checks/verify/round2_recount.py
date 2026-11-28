"""Verifier round 2: independent recount of the exploratory numbers that solve round 2 added.
Usage: python3 -I checks/verify/round2_recount.py RAWDIR EXPECTED_JSON
RAWDIR holds s1985.json..s2026.json (MLB Stats API), cdc_births.csv (jakevdp) and
538_1994_2003.csv (FiveThirtyEight US_births_1994-2003_CDC_NCHS.csv).
Standard library only. Written without the helper functions of checks/rerun.py.
"""
import csv, glob, json, math, os, sys
from datetime import date
from math import comb, log, exp, sqrt

raw, exp_path = sys.argv[1], sys.argv[2]
E = json.load(open(exp_path))
X = E["exploratory_verify_round1"]
P = {}
for f in sorted(glob.glob(os.path.join(raw, "s*.json"))):
    for p in json.load(open(f))["people"]:
        P[p["id"]] = p
recs = []
for p in P.values():
    if p.get("birthDate") and p.get("mlbDebutDate"):
        b = date.fromisoformat(p["birthDate"][:10]); db = date.fromisoformat(p["mlbDebutDate"][:10])
        # age at debut in completed years
        age = db.year - b.year - ((db.month, db.day) < (b.month, b.day))
        recs.append((p.get("birthCountry") == "USA", b, age))

def ym(b): return b.year * 12 + b.month - 1
def pick(lo, hi, lim=25, us=True):
    """lo, hi are (year, month) inclusive; debut at completed age < lim."""
    l, h = lo[0] * 12 + lo[1] - 1, hi[0] * 12 + hi[1] - 1
    return [b.month for u, b, a in recs if u == us and l <= ym(b) <= h and a < lim]
def ab(ms, A=(5, 6, 7), B=(8, 9, 10)):
    return sum(m in A for m in ms), sum(m in B for m in ms)
def hyp_tail(a, b, c, d):  # P(X >= a)
    n1, k, n = a + b, a + c, a + b + c + d
    return sum(comb(n1, x) * comb(n - n1, k - x) for x in range(a, min(n1, k) + 1)) / comb(n, k)
def hyp_two(a, b, c, d):
    n1, k, n = a + b, a + c, a + b + c + d
    w = [comb(n1, x) * comb(n - n1, k - x) for x in range(max(0, k - (n - n1)), min(n1, k) + 1)]
    o = comb(n1, a) * comb(n - n1, k - a)
    return sum(v for v in w if v <= o) / comb(n, k)
def tab(T, C, A=(5, 6, 7), B=(8, 9, 10), two=False):
    a, b = ab(T, A, B); c, d = ab(C, A, B)
    lor = log(a * d / (b * c)); se = sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return (a, b, c, d, round(exp(lor), 3), round(exp(lor - 1.96 * se), 3), round(exp(lor + 1.96 * se), 3),
            round(hyp_two(a, b, c, d) if two else hyp_tail(a, b, c, d), 4))
bad = 0
def cmp(name, mine, e):
    global bad
    key = "fisher_p_two" if "fisher_p_two" in e else "fisher_p_greater"
    theirs = (e["A_T"], e["B_T"], e["A_C"], e["B_C"], e["OR"], e["ci95_OR"][0], e["ci95_OR"][1], e[key])
    ok = mine == theirs
    bad += not ok
    print(("OK  " if ok else "DIFF"), name, mine, "" if ok else theirs)

Cw, Tw, Gw = ((1976, 8), (1992, 7)), ((1996, 5), (2001, 4)), ((1992, 8), (1995, 7))
C, T, G = pick(*Cw), pick(*Tw), pick(*Gw)
cmp("gap_vs_C", tab(G, C), X["gap_vs_C"])
cmp("T_vs_gap", tab(T, G), X["T_vs_gap"])
cmp("T_vs_lateC", tab(T, pick((1984, 8), (1992, 7))), X["T_vs_lateC_1984_92"])
for lim, thi in ((22, (2001, 4)), (23, (2001, 4)), (24, (2001, 4)), (25, (2001, 4)), (26, (2000, 4)), (27, (1999, 4))):
    cmp(f"debut<{lim}", tab(pick((1996, 5), thi, lim), pick(*Cw, lim)), X["debut_age"][f"before_{lim}"])
cmp("non_us", tab(pick(*Tw, us=False), pick(*Cw, us=False), two=True), X["non_us_born"])
cmp("Jul_vs_Aug", tab(T, C, (7,), (8,)), X["month_groups"]["Jul_vs_Aug"])
cmp("JunJul_vs_AugSep", tab(T, C, (6, 7), (8, 9)), X["month_groups"]["JunJul_vs_AugSep"])
cmp("AprJul_vs_AugNov", tab(T, C, (4, 5, 6, 7), (8, 9, 10, 11)), X["month_groups"]["AprJul_vs_AugNov"])
for i, y in enumerate(range(1968, 1997, 4)):
    a, b = ab(pick((y, 8), (y + 4, 7))); e = X["bins_4yr"][i]
    ok = (a, b) == (e["A"], e["B"]); bad += not ok
    print("OK  " if ok else "DIFF", "bin", y, a, b, round(b / a, 2))
for i, y in enumerate(range(1988, 2000)):
    a, b = ab(pick((y, 8), (y + 1, 7))); e = X["single_years"][i]
    ok = (a, b) == (e["A"], e["B"]); bad += not ok
    print("OK  " if ok else "DIFF", "year", y, a, b)
for y in range(1996, 2001):
    Tm = pick((1996, 5), (y, 4)) + pick((y + 1, 5), (2001, 4)) if y > 1996 else pick((1997, 5), (2001, 4))
    p = tab(Tm, C)[7]; e = X["leave_one_T_year_out_p"][f"drop_{y}-05..{y + 1}-04"]
    ok = p == e; bad += not ok
    print("OK  " if ok else "DIFF", "leave out", y, p, e)
a, b = ab(T); se = sqrt(1 / a + 1 / b)
print("T ratio", b / a, round(b / a * exp(-1.96 * se), 3), round(b / a * exp(1.96 * se), 3), X["T_ratio_B_over_A"])
# trend inside C: score test of a logistic slope = Cochran-Armitage; computed here as
# z = sum (s_i - sbar)(a_i - n_i p) / sqrt(p(1-p) sum n_i (s_i - sbar)^2)
g = [(y, *ab(pick((y, 8), (y + 1, 7)))) for y in range(1976, 1992)]
N = sum(a + b for _, a, b in g); p = sum(a for _, a, _ in g) / N
sbar = sum(s * (a + b) for s, a, b in g) / N
z = sum((s - sbar) * (a - (a + b) * p) for s, a, b in g) / sqrt(p * (1 - p) * sum((a + b) * (s - sbar) ** 2 for s, a, b in g))
print("trend C z", round(z, 3), "p", round(math.erfc(abs(z) / sqrt(2)), 4), X["pretrend_C_single_years"])
# CDC births
m = {}; rows_per = {}
for r in csv.DictReader(open(os.path.join(raw, "cdc_births.csv"))):
    k = (int(r["year"]), int(r["month"]), r["gender"]); m[k] = m.get(k, 0) + int(r["births"])
def ratio(lo, hi, sexes=("M",), src=m):
    A = sum(v for (y, mo, s), v in src.items() if s in sexes and lo <= (y, mo) <= hi and mo in (5, 6, 7))
    B = sum(v for (y, mo, s), v in src.items() if s in sexes and lo <= (y, mo) <= hi and mo in (8, 9, 10))
    return B / A
rc, rt = ratio(*Cw), ratio(*Tw)
print("CDC male B/A  C", round(rc, 4), "T", round(rt, 4), "expected OR", round(rc / rt, 4), X["us_birth_seasonality"])
print("CDC months present 1976-2001:", all((y, mo, "M") in m for y in range(1976, 2002) for mo in range(1, 13)))
print("CDC male births per year 1976, 1990, 2000:", [sum(v for (y, mo, s), v in m.items() if y == yy and s == "M") for yy in (1976, 1990, 2000)])
f = {}
for r in csv.DictReader(open(os.path.join(raw, "538_1994_2003.csv"))):
    k = (int(r["year"]), int(r["month"]), "X"); f[k] = f.get(k, 0) + int(r["births"])
print("T window B/A, both sexes: jakevdp", round(ratio(*Tw, sexes=("M", "F")), 4), " FiveThirtyEight", round(ratio(*Tw, sexes=("X",), src=f), 4))
print("ALL MATCH" if not bad else f"{bad} DIFFERENCES")
