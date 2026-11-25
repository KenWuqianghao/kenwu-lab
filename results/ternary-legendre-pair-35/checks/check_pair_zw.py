# Second exact checker, written from the source definition only (by the verifier,
# before it read check_pair.py). Usage: python3 checks/check_pair_zw.py <A-word> <B-word>
# PAF(A,s) = sum_j a_j * conj(a_{j+s}), indices mod l. Pair iff PAF(A,s)+PAF(B,s) = -2 for s=1..floor(l/2).
# Exact arithmetic in Z[x]/(x^2+x+1): element (p,q) = p + q*w, w = exp(2 pi i/3).
import sys, cmath
def mul(u, v):
    (a, b), (c, d) = u, v
    # (a+bw)(c+dw) = ac + (ad+bc)w + bd w^2, w^2 = -1 - w
    return (a*c - b*d, a*d + b*c - b*d)
def conj(u):
    a, b = u            # conj(w) = w^2 = -1 - w
    return (a - b, -b)
W = [(1, 0), (0, 1), (-1, -1)]
def paf(x, s):
    l = len(x); p = q = 0
    for j in range(l):
        t = mul(x[j], conj(x[(j + s) % l])); p += t[0]; q += t[1]
    return (p, q)
def is_pair(A, B, full=False):
    l = len(A)
    assert len(B) == l and l >= 2
    a = [W[int(c)] for c in A]; b = [W[int(c)] for c in B]
    rng = range(1, l) if full else range(1, l // 2 + 1)
    return all((paf(a, s)[0] + paf(b, s)[0], paf(a, s)[1] + paf(b, s)[1]) == (-2, 0) for s in rng)
def is_pair_float(A, B):
    l = len(A); w = cmath.exp(2j * cmath.pi / 3)
    a = [w ** int(c) for c in A]; b = [w ** int(c) for c in B]
    return max(abs(sum(a[j] * a[(j+s) % l].conjugate() + b[j] * b[(j+s) % l].conjugate() for j in range(l)) + 2)
               for s in range(1, l // 2 + 1))
if __name__ == "__main__":
    A, B = sys.argv[1], sys.argv[2]
    assert set(A + B) <= set("012")
    print("len", len(A), len(B), "comp", [A.count(c) for c in "012"], [B.count(c) for c in "012"])
    half, full = is_pair(A, B), is_pair(A, B, True)
    print("exact s=1..l/2:", half, " exact s=1..l-1:", full, " float max err: %.1e" % is_pair_float(A, B))
    sys.exit(0 if half and full else 1)
