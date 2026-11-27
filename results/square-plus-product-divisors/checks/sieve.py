"""Sieve check of the statement for large N.

1. d[m] = number of positive divisors of m, for 1 <= m <= L, by a divisor sieve.
2. S(N) = sum over 1 <= k, k^2 < N of d[N - k^2], for every N = 6 (mod 8), N <= L.
   Prints the number of such N with S(N) % 4 != 0, separately for N = 6 and N = 14 (mod 16).
3. For M = L // 10 and each A in (16, 32, 64) and each 0 <= B < A, it tests whether
   S(N) = 0 (mod 4) for all N = B (mod A) with 1 <= N <= M, and prints the classes that pass.
Usage: python3 -I checks/sieve.py L
"""
import sys

import numpy as np


def main():
    L = int(sys.argv[1])
    d = np.zeros(L + 1, dtype=np.int64)
    for i in range(1, L + 1):
        d[i::i] += 1
    # S for N = 8j + 6 <= L
    J = (L - 6) // 8 + 1
    N8 = 8 * np.arange(J, dtype=np.int64) + 6
    S8 = np.zeros(J, dtype=np.int64)
    k = 1
    while k * k < L:
        ok = N8 > k * k
        S8[ok] += d[N8[ok] - k * k]
        k += 1
    bad = N8[S8 % 4 != 0]
    n16_6 = int(np.sum(N8 % 16 == 6))
    n16_14 = int(np.sum(N8 % 16 == 14))
    print(f"N=6 mod 16, N<={L}: tested={n16_6} bad={int(np.sum(bad % 16 == 6))}")
    print(f"N=14 mod 16, N<={L}: tested={n16_14} bad={int(np.sum(bad % 16 == 14))}")
    M = L // 10
    S = np.zeros(M + 1, dtype=np.int64)
    k = 1
    while k * k < M:
        S[k * k + 1:] += d[1:M + 1 - k * k]
        k += 1
    for A in (16, 32, 64):
        good = [B for B in range(A) if np.all(S[max(B, A) if B == 0 else B::A] % 4 == 0)]
        print(f"A={A}: classes B with S(N)=0 mod 4 for all N=B mod A, N<={M}: {good}")


if __name__ == "__main__":
    main()
