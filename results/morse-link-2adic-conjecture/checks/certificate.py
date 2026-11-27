"""Exact certificate for the k = 2 counterexample to Gao-Gu Conjecture 4.12.

Standard library only. Run from the result folder: python3 -I checks/certificate.py
1. Computes L^(2)_n and C_n by a height transfer over Dyck paths, and checks the
   transfer against brute-force path enumeration for n <= 10.
2. Checks the values at n = 2, 3, 4, 19 against data/expected.json.
3. Checks the short proof: for every c >= 0 and every 2-adic integer alpha, the identity
   of Conjecture 4.12 fails at n = 2, 3 or 19. The test is exhaustive over alpha mod 2^12.
"""
import json
import os
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED = json.load(open(os.path.join(HERE, "..", "data", "expected.json")))


def transfer(b, N):
    """[C^b_0, ..., C^b_N]; an up step from height h has weight b(h), a down step 1."""
    cur = {0: 1}
    out = [1]
    for step in range(1, 2 * N + 1):
        nxt = {}
        for h, v in cur.items():
            nxt[h + 1] = nxt.get(h + 1, 0) + v * b(h)
            if h > 0:
                nxt[h - 1] = nxt.get(h - 1, 0) + v
        cur = nxt
        if step % 2 == 0:
            out.append(cur.get(0, 0))
    return out


def brute(b, n):
    tot = 0
    for steps in product((1, -1), repeat=2 * n):
        y, w = 0, 1
        for s in steps:
            if s == 1:
                w *= b(y)
            y += s
            if y < 0:
                break
        else:
            if y == 0:
                tot += w
    return tot


def v2(x):
    assert x != 0
    c = 0
    while x % 2 == 0:
        x //= 2
        c += 1
    return c


def s2(n):
    return bin(n).count("1")


b2 = lambda h: (2 * h + 1) ** 4
one = lambda h: 1
N = 40
L = transfer(b2, N)
C = transfer(one, N)
for n in range(11):
    assert L[n] == brute(b2, n) and C[n] == brute(one, n), n
print("transfer = brute-force enumeration for n <= 10: OK")

for key, e in EXPECTED["values"].items():
    n = int(key)
    diff = L[n] - C[n]
    got = {"L": str(L[n]), "C": str(C[n]), "v2": v2(diff), "odd_part": str(diff >> v2(diff)),
           "s2": s2(n), "d": v2(diff) - s2(n)}
    assert got == e, (n, got, e)
    print(f"n={n:2d}: v2(L-C)={got['v2']:2d}  s2(n)={got['s2']}  d(n)={got['d']:2d}  "
          f"L-C = 2^{got['v2']} * {got['odd_part'][:20]}{'...' if len(got['odd_part']) > 20 else ''}")
assert L[3] - C[3] == 57344 == 7 * 2 ** 13

# The identity at n reads d(n) = v2(n - alpha) + c, with v2(n - alpha) >= 0 finite.
# c > d(2) = 3 fails at n = 2. For c <= 3 every value v2(n - alpha) that the identity
# needs at n = 2, 3, 19 is at most 11, so alpha mod 2^12 decides whether it holds.
d = {n: v2(L[n] - C[n]) - s2(n) for n in (2, 3, 19)}
M = 2 ** 12
def holds(n, a, c):
    m = d[n] - c
    return 0 <= m < 12 and (n - a) % 2 ** (m + 1) == 2 ** m
fits = [(a, c) for c in range(d[2] + 1) for a in range(M) if all(holds(n, a, c) for n in (2, 3, 19))]
assert fits == [], fits
print(f"No (alpha mod 2^12, c) with 0 <= c <= {d[2]} satisfies the identity at n = 2, 3, 19.")

# Remark 3 of the paper: n = 2, 3 force c = 3 and alpha = 3 + 2^8 (mod 2^9). With these,
# the identity holds for 2 <= n <= 18 and fails first at n = 19.
dd = {n: v2(L[n] - C[n]) - s2(n) for n in range(2, N + 1)}
forced = [(a, c) for c in range(4) for a in range(2 ** 9)
          if all(0 <= dd[n] - c < 9 and (n - a) % 2 ** (dd[n] - c + 1) == 2 ** (dd[n] - c) for n in (2, 3))]
assert forced == [(3 + 2 ** 8, 3)], forced
a = 3 + 2 ** 8   # v2(n - alpha) = v2(n - a) for every n <= 40 with n != 3, as alpha = a (mod 2^9)
first_bad = [n for n in range(2, N + 1) if n != 3 and dd[n] - 3 != v2(n - a)]
assert first_bad[0] == 19, first_bad
print("n = 2, 3 force c = 3, alpha = 3 + 2^8 (mod 2^9); the identity then holds for n <= 18 and fails at n = 19.")

# Positive control: k = 1 (Postnikov's case) fits n = 2..40 with c = 2.
L1 = transfer(lambda h: (2 * h + 1) ** 2, N)
d1 = {n: v2(L1[n] - C[n]) - s2(n) for n in range(2, N + 1)}
ok1 = [a for a in range(2 ** 16) if all(0 <= d1[n] - 2 < 16 and (n - a) % 2 ** (d1[n] - 1) == 2 ** (d1[n] - 2)
                                         for n in range(2, N + 1))]
assert ok1, "control failed"
print(f"Control k=1, c=2: {len(ok1)} residues alpha mod 2^16 fit n = 2..40, e.g. {bin(ok1[0])}.")
print("CERTIFICATE VERIFIED: Conjecture 4.12 fails for k = 2.")
