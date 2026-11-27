"""Independent checker: Gao-Gu Conjecture 4.12 (arXiv:1908.03914v1) fails for k = 2.

Exact integer arithmetic only. Three independent ways compute weighted Catalan numbers:
  (A) brute-force enumeration of Dyck paths (n <= 10),
  (B) transfer over heights (dynamic programming on lattice paths),
  (C) first-return recursion F_h = 1 + b(h) x F_{h+1} F_h (the continued fraction of Prop. 1.2).
Then the 2-adic argument in STATEMENT.md / RESULT.md is checked step by step.
"""
from itertools import product
from math import comb
from functools import lru_cache

def b_k(k):
    return lambda h: (2*h+1)**(2*k)

def brute(b, n):
    tot = 0
    for steps in product((1, -1), repeat=2*n):
        y, w, ok = 0, 1, True
        for s in steps:
            if s == 1:
                w *= b(y)          # height of an up step = y-coordinate of its start
            y += s
            if y < 0: ok = False; break
        if ok and y == 0: tot += w
    return tot

def transfer(b, N):
    cur = [0]*(N+2); cur[0] = 1; out = [1]
    for step in range(1, 2*N+1):
        nxt = [0]*(N+2)
        for h in range(N+1):
            v = cur[h]
            if v:
                if h+1 <= N: nxt[h+1] += v*b(h)
                if h > 0: nxt[h-1] += v
        cur = nxt
        if step % 2 == 0: out.append(cur[0])
    return out

def first_return(b, N):
    @lru_cache(None)
    def F(h, n):          # weighted count of Dyck paths of semilength n raised to base height h
        if n == 0: return 1
        return b(h)*sum(F(h+1, i)*F(h, n-1-i) for i in range(n))
    return [F(0, n) for n in range(N+1)]

def v2(x):
    assert x != 0
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c

def s2(n): return bin(n).count('1')

N = 40
one = lambda h: 1
C_A = [brute(one, n) for n in range(11)]
assert C_A == [comb(2*n, n)//(n+1) for n in range(11)]
C = first_return(one, N)
assert C == transfer(one, N) == [comb(2*n, n)//(n+1) for n in range(N+1)]

b = b_k(2)
LB = transfer(b, N); LC = first_return(b, N)
assert LB == LC, "transfer and first-return disagree"
assert [brute(b, n) for n in range(11)] == LB[:11], "brute force disagrees"
L = LB

d = {n: v2(L[n]-C[n]) - s2(n) for n in range(2, N+1)}
print("L_3 - C_3 =", L[3]-C[3], "= 7 * 2^13:", L[3]-C[3] == 7*2**13)
for n in (2, 3, 4, 19):
    print(f"n={n}: v2(L_n - C_n) = {v2(L[n]-C[n])}, s2(n) = {s2(n)}, d(n) = {d[n]}")
assert (d[2], d[3], d[4], d[19]) == (3, 11, 3, 8)

# Step 1: d(2)=d(4)=3 forces v2(2-a)=v2(4-a)=3-c, so v2(2-a)=v2(4-a).
#   No 2-adic integer a has v2(2-a)=v2(4-a)=m>=1: check every residue a mod 2^(m+2) for m<=20.
for m in range(1, 21):
    M = 2**(m+2)
    for a in range(M):
        x, y = (2-a) % M, (4-a) % M
        # v2(.) = m  <=>  residue mod 2^(m+1) equals 2^m
        assert not (x % 2**(m+1) == 2**m and y % 2**(m+1) == 2**m)
#   m >= 21 would need c = 3 - m < 0. Hence m = 0, c = 3, and a is odd.
c = 3
# Step 2: n=3 gives v2(3-a) = d(3)-c = 8, so a = 3 + 2^8 (mod 2^9); in particular a = 3 (mod 32).
# Step 3: n=19 gives v2(19-a) = d(19)-c = 5, so a = 19 + 2^5 (mod 2^6); in particular a = 19 (mod 32).
e3, e19 = d[3]-c, d[19]-c
assert (e3, e19) == (8, 5)
sols3 = {a for a in range(2**6) if any(((3-A) % 2**9) == 2**8 for A in range(a, 2**9, 2**6))}
sols19 = {a for a in range(2**6) if ((19-a) % 2**6) == 2**5}
print("a mod 64 allowed by n=3:", sorted(sols3), " by n=19:", sorted(sols19))
assert sols3.isdisjoint(sols19)
print("No 2-adic integer alpha_2 and no c_2 >= 0 satisfy Conjecture 4.12 at n = 2, 3, 4, 19. VERIFIED.")
