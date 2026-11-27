#!/usr/bin/env python3
"""Independent exact checker (pure Python, fractions only) for the counterexample to
Conjecture 2 of Nie, Warmuth, Vishwanathan, Zhang, COLT 2013 (PMLR 30:1076-1079).

valD(A) := -min_{w in simplex} ||A w||_inf.
Claim: n = 16, t = 6. U (15 x 16, entries +-1, valD(U) = 0) has
  max_{|S|=6} valD(U_S) <= -3/7 < -1/3 <= max_{|S|=6} valD(Hhat_S),
where Hhat is the 16 x 16 Sylvester Hadamard matrix with its first row removed.
So the inequality  max valD(Hhat_t) <= max valD(U_t)  of Conjecture 2 is false.
"""
import json, sys, itertools
from fractions import Fraction as F

cert = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "checks/certificate.json"))
n, t = 16, cert["t"]
assert t == 6
U = [[1 if ch == "+" else -1 for ch in row] for row in cert["U"]]

# 1. U is a (n-1) x n matrix with entries +-1.
assert len(U) == n - 1 and all(len(r) == n for r in U)

# 2. valD(U) = 0: valD <= 0 always (norm >= 0); the uniform w gives U w = 0 exactly.
assert all(sum(r) == 0 for r in U)

# 3. Lower bound 3/7 on min_{w in simplex_S} ||U_S w||_inf for every 6-subset S.
# Certificate y with sum|y_i| <= 1 and (U_S^T y)_j >= 3/7 for all j in S gives, for w in simplex_S,
# ||U_S w||_inf >= y^T U_S w = sum_j w_j (U_S^T y)_j >= 3/7  (Hoelder).
bound = F(3, 7)
by_S = {tuple(c["S"]): [F(v) for v in c["y"]] for c in cert["subset_certificates"]}
all_S = list(itertools.combinations(range(n), t))
assert set(by_S) == set(all_S) and len(all_S) == 8008
for S in all_S:
    y = by_S[S]
    assert len(y) == n - 1 and sum(abs(v) for v in y) <= 1
    for j in S:
        assert sum(y[i] * U[i][j] for i in range(n - 1)) >= bound, S

# 4. Sylvester side: Hhat[r][c] = (-1)^{popcount(r & c)}, r = 1..15, c = 0..15.
Hhat = [[(-1) ** bin(r & c).count("1") for c in range(n)] for r in range(1, n)]
S0 = (0, 1, 2, 4, 8, 15)
w = [F(1, 6)] * 6
norm = max(abs(sum(w[k] * Hhat[i][S0[k]] for k in range(6))) for i in range(n - 1))
assert norm == F(1, 3)
# Sanity: Hhat rows come from an orthogonal matrix (Sylvester Hadamard).
Hfull = [[1] * n] + Hhat
assert all(sum(Hfull[a][k] * Hfull[b][k] for k in range(n)) == (n if a == b else 0)
           for a in range(n) for b in range(n))

assert bound > norm
print(f"OK: max_S valD(U_S) <= -{bound} < -{norm} <= max_S valD(Hhat_S)  (n={n}, t={t})")
print("Conjecture 2 of Nie-Warmuth-Vishwanathan-Zhang (COLT 2013) fails at n=16, t=6.")
