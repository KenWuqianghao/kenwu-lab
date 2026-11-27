"""Independent verifier check (verify stage). Written from the source definitions,
without reading checks/check.py.

Usage: python -I vcheck.py <certificate.json> [--lp]

Exact part (fractions only):
  1. U is 15 x 16, entries +-1, every row sum 0  => val_D(U) = 0.
  2. H = Sylvester matrix of order 16, H H^T = 16 I, row 0 all +1, Hhat = rows 1..15.
  3. Witness: 6 distinct columns of Hhat and w in the simplex with ||Hhat_S w||_inf = 1/3.
  4. For all C(16,6) = 8008 column sets S: a vector y with sum |y_i| <= 1 and
     (U_S^T y)_j >= 3/7 for all j in S. Then ||U_S w||_inf >= y^T U_S w >= 3/7 on the simplex.
  5. 1/3 < 3/7.
With --lp (needs scipy): solve every LP in floating point, make my OWN dual vectors,
round them to rationals, and repeat check 4 with them. Also find a primal w that reaches
3/7 exactly, so that max_S val_D(U_S) = -3/7 exactly.
"""
import json
import sys
from fractions import Fraction as F
from itertools import combinations

N, T = 16, 6
BOUND = F(3, 7)


def load(path):
    d = json.load(open(path))
    U = [[1 if ch == '+' else -1 if ch == '-' else None for ch in row] for row in d["U"]]
    return d, U


def check_U(U):
    assert len(U) == N - 1
    for row in U:
        assert len(row) == N and all(x in (1, -1) for x in row)
        assert sum(row) == 0
    # extra fact (not needed for the claim): U with an all-ones row is a Hadamard matrix
    full = [[1] * N] + U
    had = all(sum(a * b for a, b in zip(full[i], full[j])) == (N if i == j else 0)
              for i in range(N) for j in range(N))
    return had


def sylvester():
    H = [[(-1) ** bin(r & c).count("1") for c in range(N)] for r in range(N)]
    for i in range(N):
        for j in range(N):
            assert sum(H[i][k] * H[j][k] for k in range(N)) == (N if i == j else 0)
    assert all(x == 1 for x in H[0])
    return H[1:]


def inf_norm(A, S, w):
    return max(abs(sum(F(row[j]) * wj for j, wj in zip(S, w))) for row in A)


def dual_ok(U, S, y):
    if sum(abs(v) for v in y) > 1:
        return False
    return all(sum(y[i] * U[i][j] for i in range(N - 1)) >= BOUND for j in S)


def main():
    path = sys.argv[1]
    d, U = load(path)
    assert d["t"] == T
    had = check_U(U)
    print("1. U: 15 x 16, +-1, all row sums 0: PASS. [1;U] is Hadamard:", had)

    Hhat = sylvester()
    print("2. Sylvester H of order 16, H H^T = 16 I, row 0 all +1: PASS")

    S0 = (0, 1, 2, 4, 8, 15)
    assert len(set(S0)) == T
    v = inf_norm(Hhat, S0, [F(1, T)] * T)
    assert v == F(1, 3), v
    print("3. Sylvester witness S0 =", S0, "uniform w: ||Hhat_S0 w||_inf =", v, ": PASS")

    certs = d["subset_certificates"]
    seen = set()
    for c in certs:
        S = tuple(c["S"])
        assert len(S) == T and len(set(S)) == T and all(0 <= j < N for j in S)
        y = [F(s) for s in c["y"]]
        assert len(y) == N - 1
        assert dual_ok(U, S, y), S
        seen.add(tuple(sorted(S)))
    allS = set(combinations(range(N), T))
    assert seen == allS and len(certs) == len(allS) == 8008
    print("4. author's certificates: 8008 distinct 6-subsets, all dual vectors valid: PASS")
    assert F(1, 3) < BOUND
    print("5. 1/3 < 3/7: PASS")

    if "--lp" in sys.argv:
        lp_part(U, Hhat)


def lp_solve(A, S):
    """min z s.t. -z <= A_S w <= z, w in simplex. Returns (z, w, y) in floats;
    y = signed row multipliers."""
    import numpy as np
    from scipy.optimize import linprog
    AS = np.array([[row[j] for j in S] for row in A], dtype=float)
    m, t = AS.shape
    c = np.zeros(t + 1); c[-1] = 1
    Aub = np.block([[AS, -np.ones((m, 1))], [-AS, -np.ones((m, 1))]])
    bub = np.zeros(2 * m)
    Aeq = np.zeros((1, t + 1)); Aeq[0, :t] = 1
    r = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=[1],
                bounds=[(0, None)] * t + [(0, None)], method="highs")
    assert r.status == 0
    lam = -r.ineqlin.marginals  # >= 0
    y = lam[:m] - lam[m:]
    # sign: we want U_S^T y >= bound; fix sign by test
    return r.fun, r.x[:t], y, AS


def lp_part(U, Hhat):
    import numpy as np
    worst = (9, None, None)
    nfail = 0
    for S in combinations(range(N), T):
        z, w, y, AS = lp_solve(U, S)
        if z < worst[0] - 1e-12:
            worst = (z, S, w)
        # my own dual: try both signs, rationalize, normalize
        ok = False
        for sgn in (1, -1):
            yr = [F(float(sgn * v)).limit_denominator(1000) for v in y]
            s = sum(abs(v) for v in yr)
            if s == 0:
                continue
            yr = [v / s for v in yr]
            if dual_ok(U, S, yr):
                ok = True
                break
        if not ok:
            nfail += 1
            print("   own dual failed for", S, "LP value", z)
    print("6. own LP duals (scipy HiGHS, rounded, exact check): failures =", nfail,
          "of 8008:", "PASS" if nfail == 0 else "FAIL")
    z, S, w = worst
    wr = [F(float(x)).limit_denominator(1000) for x in w]
    assert sum(wr) == 1 and all(x >= 0 for x in wr)
    v = inf_norm(U, S, wr)
    print("7. smallest LP value over S:", z, "at S =", S, "w =", [str(x) for x in wr],
          "exact ||U_S w||_inf =", v, ":", "PASS" if v == BOUND else "FAIL")
    # Sylvester side, floats only (information)
    best = min(lp_solve(Hhat, S)[0] for S in combinations(range(N), T))
    print("8. (float, information) Sylvester min_S min_w ||Hhat_S w||_inf at t=6:", best)


if __name__ == "__main__":
    main()
