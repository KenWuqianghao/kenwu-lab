"""The 2-adic fits of Section 5 of the paper (computed, not proved).

python3 -I checks/fit.py   Prints alpha mod 2^M for k = 2 (n >= 4, c = 3) and k = 1 (n >= 2, c = 2)
on n <= 200, and checks them against data/expected.json.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from explore_lib import wcat, v2, s2

N = 200
exp = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "expected.json")))["fits"]
C = wcat(lambda h: 1, N)
for key, (k, c, n0) in {"k2_n4": (2, 3, 4), "k1_n2": (1, 2, 2)}.items():
    L = wcat(lambda h: (2 * h + 1) ** (2 * k), N)
    d = {n: v2(L[n] - C[n]) - s2(n) for n in range(n0, N + 1)}
    cons = [((n + 2 ** (d[n] - c)) % 2 ** (d[n] - c + 1), d[n] - c + 1) for n in range(n0, N + 1)]
    M = max(m for _, m in cons)
    r = next(r for r, m in cons if m == M)
    assert all((r - rr) % 2 ** m == 0 for rr, m in cons), key
    got = {"modulus_exponent": M, "alpha_binary": bin(r)[2:]}
    print(f"{key}: c={c}, alpha = {got['alpha_binary']} (base 2) mod 2^{M}")
    assert got == exp[key], (got, exp[key])
print("fits match data/expected.json")
