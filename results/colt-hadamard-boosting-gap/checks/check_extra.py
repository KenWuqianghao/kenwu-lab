#!/usr/bin/env python3
"""Extra exact checks (standard library only).

Usage: python3 -I checks/check_extra.py checks/certificate.json checks/had.16.3.txt

1. had.16.3.txt (N. J. A. Sloane's library of Hadamard matrices) is a 16 x 16 Hadamard
   matrix, and its row 0 is all +1.
2. U in the certificate is that matrix with row 0 deleted.
3. Equality: for S = {0,1,2,3,4,12} and w = (1,1,1,1,1,2)/7, ||U_S w||_inf = 3/7.
   With the certificate bound, max over 6-column sets of valD(U_S) = -3/7 exactly.
4. Sylvester witness by the hand formula: for row r != 0 of H and
   S0 = {0,1,2,4,8,15}, the row sum is 1 + (4 - 2|r|) + (-1)^|r| = +-2.
"""
from fractions import Fraction as F
import json, sys

cert = json.load(open(sys.argv[1]))
rows = [l.strip() for l in open(sys.argv[2]) if len(l.strip()) == 16 and set(l.strip()) <= set("+-")]
H = [[1 if ch == "+" else -1 for ch in r] for r in rows]
assert len(H) == 16 and all(len(r) == 16 for r in H)
assert all(sum(a * b for a, b in zip(H[i], H[j])) == (16 if i == j else 0)
           for i in range(16) for j in range(16))
assert all(x == 1 for x in H[0])
print("had.16.3: 16 x 16, H H^T = 16 I, row 0 all +1: PASS")
assert rows[1:] == cert["U"]
print("U = had.16.3 without row 0: PASS")
U = [[1 if ch == "+" else -1 for ch in r] for r in cert["U"]]
S, w = (0, 1, 2, 3, 4, 12), [F(1, 7)] * 5 + [F(2, 7)]
v = max(abs(sum(U[i][c] * x for c, x in zip(S, w))) for i in range(15))
assert v == F(3, 7) and sum(w) == 1
print("U, S = (0, 1, 2, 3, 4, 12), w = (1,1,1,1,1,2)/7: ||U_S w||_inf =", v, ": PASS")
for r in range(1, 16):
    k = bin(r).count("1")
    s = sum((-1) ** bin(r & c).count("1") for c in (0, 1, 2, 4, 8, 15))
    assert s == 1 + (4 - 2 * k) + (-1) ** k and abs(s) == 2
print("Sylvester rows 1..15 on S0 = (0, 1, 2, 4, 8, 15): row sums are +-2: PASS")
