"""Direct check of the statement from the definitions (no step of the proof is used).

S(N) = sum over integers k with 1 <= k and k^2 < N of d(N - k^2), where d(m) is the
number of positive divisors of m, found by trial division. For an integer k >= 0,
k < sqrt(N) is the same as k^2 < N.

Prints:
  1. S(N) for N = 6, 14, ..., 118.
     Control: S(N) mod 4 for N = 2, 10, 18, 26.
  2. The number of N = 6 (mod 8) with N <= LIMIT and S(N) % 4 != 0 (must be 0).
  3. For each residue r of N mod 16, the set of values of S(N) mod 4 for 1 <= N <= LIMIT.
  4. The number of N = 14 (mod 16), N <= LIMIT, with sigma1(N)/2 % 4 != 0 (must be 0).
  5. The sets of the proof for the example N = 22 (Section 3 of the paper).
Usage: python3 -I checks/check_statement.py LIMIT
"""
import sys
from math import isqrt


def d(m):
    return sum(1 for i in range(1, m + 1) if m % i == 0)


def S(N):
    return sum(d(N - k * k) for k in range(1, N) if k * k < N)


def example(N):
    X = [(k, a, (N - k * k) // a) for k in range(1, N) if k * k < N
         for a in range(1, N - k * k + 1) if (N - k * k) % a == 0]
    X1lt = [t for t in X if t[0] % 2 == 1 and t[1] < t[2]]
    Z = [(k, x, y, z) for k in range(1, N, 2) for x in range(1, N) for y in range(1, N)
         for z in range(1, N) if k * k + x * x + 4 * y * z == N]
    F = [t for t in Z if t[0] == t[1] and t[2] == t[3]]
    Xb = [t for t in X if t[0] % 2 == 0 and t[2] % 2 == 0]
    Xbf = [t for t in Xb if t[2] == 2 * t[1]]
    print(f"example N={N}: |X|={len(X)} |X1<|={len(X1lt)} X1<={X1lt}")
    print(f"example N={N}: |Zs|={len(Z)} Zs={Z}")
    print(f"example N={N}: F={F} |Xb|={len(Xb)} Xb={Xb} fixed={Xbf}")


def main():
    limit = int(sys.argv[1])
    print("S(N) for N=6..118 step 8:", [S(N) for N in range(6, 119, 8)])
    print("control: S(N) mod 4 for N=2,10,18,26:", [S(N) % 4 for N in (2, 10, 18, 26)])
    vals = {N: S(N) for N in range(1, limit + 1)}
    bad = [N for N in range(6, limit + 1, 8) if vals[N] % 4]
    print(f"N=6 mod 8, N<={limit}: {len(range(6, limit + 1, 8))} values, failures: {len(bad)}")
    res = {r: sorted({vals[N] % 4 for N in vals if N % 16 == r}) for r in range(16)}
    print("S(N) mod 4 by N mod 16:", res)
    s1 = [N for N in range(14, limit + 1, 16)
          if (sum(i for i in range(1, N + 1) if N % i == 0) // 2) % 4]
    print(f"sigma1(N)/2 = 0 mod 4 for N=14 mod 16, N<={limit}: failures: {len(s1)}")
    example(22)


if __name__ == "__main__":
    main()
