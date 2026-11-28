import json, sys, math, glob, os
from datetime import date
from collections import Counter
from scipy.stats import fisher_exact
raw = sys.argv[1]
P = {}
for f in sorted(glob.glob(os.path.join(raw, "s*.json"))):
    for p in json.load(open(f))["people"]:
        P[p["id"]] = p
print("unique players", len(P))
print("countries top", Counter(p.get("birthCountry") for p in P.values()).most_common(6))
print("missing birthDate", sum(1 for p in P.values() if not p.get("birthDate")), "missing debut", sum(1 for p in P.values() if not p.get("mlbDebutDate")))
def D(s): return date.fromisoformat(s[:10])
def addy(b, n):
    try: return b.replace(year=b.year+n)
    except ValueError: return date(b.year+n, 3, 1)
rows = []
for p in P.values():
    if not p.get("birthDate") or not p.get("mlbDebutDate"): continue
    rows.append((p.get("birthCountry"), D(p["birthDate"]), D(p["mlbDebutDate"])))
def sel(lo, hi, age=25, us=True):
    out = []
    for c, b, deb in rows:
        if (c == "USA") != us: continue
        if not (lo <= b <= hi): continue
        if age is not None and not deb < addy(b, age): continue
        out.append(b)
    return out
def ab(bs, A=(5,6,7), B=(8,9,10)):
    return sum(b.month in A for b in bs), sum(b.month in B for b in bs)
def test(T, C, A=(5,6,7), B=(8,9,10), alt="greater"):
    ta, tb = ab(T, A, B); ca, cb = ab(C, A, B)
    orr, p = fisher_exact([[ta, tb], [ca, cb]], alternative=alt)
    return f"T {ta}/{tb}  C {ca}/{cb}  OR {orr:.3f}  p({alt}) {p:.4f}"
Clo, Chi = date(1976,8,1), date(1992,7,31); Tlo, Thi = date(1996,5,1), date(2001,4,30)
C, T = sel(Clo, Chi), sel(Tlo, Thi)
print("n_C", len(C), "n_T", len(T))
print("months C", [sum(b.month==m for b in C) for m in range(1,13)])
print("months T", [sum(b.month==m for b in T) for m in range(1,13)])
print("PRIMARY", test(T, C))
print("placebo split", test(sel(date(1984,8,1), Chi), sel(Clo, date(1984,7,31))))
print("placebo months", test(T, C, (11,12,1), (2,3,4), "two-sided"))
print("--- robustness (not pre-registered) ---")
for age in (22, 23, 24, 25):
    print("age<", age, test(sel(Tlo, Thi, age), sel(Clo, Chi, age)))
print("age<26, T to 2000-04", test(sel(Tlo, date(2000,4,30), 26), sel(Clo, Chi, 26)))
print("age<27, T to 1999-04", test(sel(Tlo, date(1999,4,30), 27), sel(Clo, Chi, 27)))
print("Aug vs Jul only", test(T, C, (7,), (8,)))
print("Jun-Jul vs Aug-Sep", test(T, C, (6,7), (8,9)))
print("Apr-Jul vs Aug-Nov", test(T, C, (4,5,6,7), (8,9,10,11)))
print("Feb-Jul vs Aug-Jan", test(T, C, (2,3,4,5,6,7), (8,9,10,11,12,1)))
print("non-US born, same test", test(sel(Tlo, Thi, us=False), sel(Clo, Chi, us=False)), "two-sided:", test(sel(Tlo, Thi, us=False), sel(Clo, Chi, us=False), alt="two-sided"))
print("--- trend by birth-year bin (Aug..Jul years), US, debut<25: May-Jul / Aug-Oct ---")
for y in range(1964, 2001, 4):
    bs = sel(date(y,8,1), date(y+4,7,31)); a, b = ab(bs)
    print(f"born {y}-08..{y+4}-07 n={len(bs)} MJJ={a} ASO={b} ratio ASO/MJJ={b/a:.2f}" + ("  (right-censored)" if y+4 > 2001 else ""))
print("single years:")
for y in range(1988, 2001):
    bs = sel(date(y,8,1), date(y+1,7,31)); a, b = ab(bs)
    print(f"born {y}-08..{y+1}-07 n={len(bs)} MJJ={a} ASO={b}" + ("  (censored)" if y+1 > 2001 else ""))
G = sel(date(1992,8,1), date(1996,4,30)); print("gap cohort 1992-08..1996-04 (note: 45 months, lacks May-Jul 1996)", ab(G))
G2 = sel(date(1992,8,1), date(1995,7,31)); print("gap cohort 1992-08..1995-07", ab(G2), "vs C:", test(G2, C))
print("T vs late control 1984-08..1992-07:", test(T, sel(date(1984,8,1), Chi)))
print("T vs gap 1992-08..1995-07:", test(T, G2))
# early control: seasons from 1985 cover debuts>=1985; born>=1964 ok roughly
# leave-one-birth-year-out on T
print("--- leave one T birth-year (May..Apr) out ---")
for y in range(1996, 2001):
    Tm = [b for b in T if not (date(y,5,1) <= b <= date(y+1,4,30))]
    print(y, test(Tm, C))
