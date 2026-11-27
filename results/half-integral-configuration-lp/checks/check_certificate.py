"""Exact certificate check (integers and Fractions only, no solver).

Usage: python check_certificate.py instance.json
1. x is a point of CLP(P,T)  (reuses check_point from check_counterexample.py).
2. LP(P) = T: sum p > m (T-1), so CLP(P,T-1) is empty (volume argument).
3. sum p = m T, so every configuration in the support of any point of CLP(P,T) has load T.
4. Enumerates every configuration of load exactly T on every machine and checks that it
   contains 0 or 3 points of copy 0 (w = indicator of P(0,k)), so w(C) = 0 mod 3.
5. A half-integral point y = 2x is integer with sum_C y_C w(C) = 2 sum_j w_j = 8,
   which is not 0 mod 3: contradiction. So CLP(P,T) = CLP(P,LP(P)) has no half-integral point.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itertools, json, sys
from check_counterexample import check_point

d = json.load(open(sys.argv[1]))
p, M, m, T = d["p"], [set(q) for q in d["M"]], d["m"], d["T"]
n = len(p)
check_point(p, M, m, T, d["x"])
print("1. x is a point of CLP(P,T): verified")
assert sum(p) > m * (T - 1)
print(f"2. sum p = {sum(p)} > m(T-1) = {m*(T-1)}: CLP(P,T-1) empty, LP(P) = {T}: verified")
assert sum(p) == m * T
print(f"3. sum p = m T = {m*T}: support configurations are full: verified")
w = [1 if d["names"][j].startswith("P0") else 0 for j in range(n)]
full = 0
for i in range(m):
    J = [j for j in range(n) if i in M[j]]
    for r in range(len(J) + 1):
        for C in itertools.combinations(J, r):
            if sum(p[j] for j in C) == T:
                full += 1
                assert sum(w[j] for j in C) % 3 == 0, (i, C)
print(f"4. all {full} full configurations have w(C) = 0 mod 3: verified")
assert (2 * sum(w)) % 3 != 0
print(f"5. 2 * sum w = {2*sum(w)} != 0 mod 3: no half-integral point in CLP(P,LP(P)): verified")
