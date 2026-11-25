"""Independent exact check of a ternary Legendre pair given as exponent words.

Usage: python3 checks/check_pair.py <A-word> <B-word>
Entry r in {0,1,2} means xi_3^r. The pair condition PAF(A,s)+PAF(B,s) = -2 for
1 <= s <= l-1 is checked in two exact ways:
 (1) integer counts M_r(s) = #{j: a_j*conj(a_{j+s}) = xi^r} (A and B together)
     must equal (2h-2, 2h, 2h), l = 3h-1;
 (2) arithmetic in Z[w]/(w^2+w+1) on pairs (x, y) = x + y*w.
"""
import sys

def check(A, B):
    l = len(A)
    assert len(B) == l and set(A) | set(B) <= {0, 1, 2}
    assert l % 3 == 2, "length must be = -1 mod 3"
    h = (l + 1) // 3
    target = (2 * h - 2, 2 * h, 2 * h)
    ok = True
    for s in range(1, l):
        M = [0, 0, 0]
        for X in (A, B):
            for j in range(l):
                # a_j * conj(a_{j+s}) = xi^(e_j - e_{j+s})
                M[(X[j] - X[(j + s) % l]) % 3] += 1
        if tuple(M) != target:
            ok = False
        # Z[w] arithmetic: w^0=(1,0), w^1=(0,1), w^2=-1-w=(-1,-1)
        pw = [(1, 0), (0, 1), (-1, -1)]
        x = sum(M[r] * pw[r][0] for r in range(3))
        y = sum(M[r] * pw[r][1] for r in range(3))
        if (x, y) != (-2, 0):
            ok = False
    comp = lambda X: tuple(X.count(r) for r in range(3))
    return ok, comp(A), comp(B), target

if __name__ == "__main__":
    A = [int(c) for c in sys.argv[1]]
    B = [int(c) for c in sys.argv[2]]
    ok, cA, cB, t = check(A, B)
    print(f"length {len(A)}; composition A {cA}, B {cB}; target counts {t}")
    print("LEGENDRE PAIR: YES" if ok else "LEGENDRE PAIR: NO")
    sys.exit(0 if ok else 1)
