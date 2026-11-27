"""Brute-force check of each counting step of the Lean proof (lean/Solution.lean).

For every N = 8n+6 <= LIMIT it computes, by direct enumeration:
  X  = {(k,a,b) >= 1 : k^2 + ab = N},  X1 (k odd), X0 (k even)
  Zs = {(k,x,y,z): k odd, x,y,z >= 1, k^2 + x^2 + 4yz = N}
and checks: |X| = S(N); |X1| = 2|X1, a<b|; |X1, a<b| = |Zs, x=y|;
|Zs| = |Zs, x=y| (mod 2) (Zagier); |Zs| = |Zs, y=z| (mod 2);
|Zs, y=z| = |Zs, y=z, k=x| (mod 2); |X0| = 2|X0, b even|;
|X0, b even| = |X0, b even, b=2a| (mod 2); |Zs, y=z, k=x| = |X0, b even, b=2a|;
|X| = 0 (mod 4).
Usage: python3 checks/check_lean_route.py LIMIT
"""
import sys
from math import isqrt


def d(n):
    return sum(1 for i in range(1, n + 1) if n % i == 0)


def check(N):
    X = []
    for k in range(1, isqrt(N - 1) + 1):
        n = N - k * k
        for a in range(1, n + 1):
            if n % a == 0:
                X.append((k, a, n // a))
    S = sum(d(N - k * k) for k in range(1, isqrt(N - 1) + 1))
    X1 = [t for t in X if t[0] % 2 == 1]
    X0 = [t for t in X if t[0] % 2 == 0]
    Z = []
    for k in range(1, isqrt(N) + 1, 2):
        for x in range(1, isqrt(N) + 1):
            r = N - k * k - x * x
            if r <= 0 or r % 4:
                continue
            r //= 4
            for y in range(1, r + 1):
                if r % y == 0:
                    Z.append((k, x, y, r // y))
    X1lt = [t for t in X1 if t[1] < t[2]]
    Zxy = [t for t in Z if t[1] == t[2]]
    Zyz = [t for t in Z if t[2] == t[3]]
    Zyzkx = [t for t in Zyz if t[0] == t[1]]
    Xb = [t for t in X0 if t[2] % 2 == 0]
    Xbf = [t for t in Xb if t[2] == 2 * t[1]]
    ok = [
        len(X) == S,
        len(X1) == 2 * len(X1lt),
        len(X1lt) == len(Zxy),
        (len(Z) - len(Zxy)) % 2 == 0,
        (len(Z) - len(Zyz)) % 2 == 0,
        (len(Zyz) - len(Zyzkx)) % 2 == 0,
        len(X0) == 2 * len(Xb),
        (len(Xb) - len(Xbf)) % 2 == 0,
        len(Zyzkx) == len(Xbf),
        len(X) % 4 == 0,
    ]
    return all(ok)


def main():
    limit = int(sys.argv[1])
    bad = [N for N in range(6, limit + 1, 8) if not check(N)]
    print(f"checked {len(range(6, limit + 1, 8))} values N=8n+6 <= {limit}; failures: {len(bad)} {bad[:5]}")


if __name__ == "__main__":
    main()
