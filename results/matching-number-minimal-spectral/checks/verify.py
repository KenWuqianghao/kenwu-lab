"""Independent checker (stdlib only, exact integer arithmetic).

Claim: for every k >= 3, the family T'_{2k,k} of Hou-Tan (arXiv:2607.11061v2,
Construction 9) has no tree of order 2k, while G_{2k,k} (connected graphs of order 2k
with matching number k) contains the path P_{2k}. So G_{2k,k} has spectrally minimal
graphs (it is a finite non-empty family), and none of them lies in T'_{2k,k}.

The general proof is in RESULT.md. This script checks the finite statements for
k = 3..KMAX by brute force over all labelled trees T1 on k vertices (Pruefer codes),
and the matching number of P_{2k} by brute force over edge subsets.
"""
import itertools
import sys

KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 8


def pruefer_trees(k):
    """Yield the degree sequence of every labelled tree on {0..k-1}."""
    if k == 1:
        yield (0,)
        return
    if k == 2:
        yield (1, 1)
        return
    for code in itertools.product(range(k), repeat=k - 2):
        deg = [1] * k
        for v in code:
            deg[v] += 1
        yield tuple(deg)


def tprime_order_n_members(n, k):
    """Count (T1 degree sequence, f) pairs that satisfy Construction 9 and give order n."""
    c = (n + 2 * k - 3) // k  # floor, exact integer division
    count = 0
    for deg in set(pruefer_trees(k)):
        choices = [[f for f in (c - 2 * d, c + 1 - 2 * d) if f >= 0] for d in deg]
        for fs in itertools.product(*choices):
            order = k + (k - 1) + sum(fs)  # X, subdivision vertices Y, pendant leaves
            if order == n:
                count += 1
    return count


def matching_number_bruteforce(n, edges):
    best = 0
    for r in range(len(edges) + 1):
        for sub in itertools.combinations(edges, r):
            used = [v for e in sub for v in e]
            if len(used) == len(set(used)):
                best = max(best, r)
    return best


ok = True
for k in range(3, KMAX + 1):
    n = 2 * k
    members = tprime_order_n_members(n, k)
    path_edges = [(i, i + 1) for i in range(n - 1)]
    nu = matching_number_bruteforce(n, path_edges)
    line_ok = members == 0 and nu == k
    ok &= line_ok
    print(f"k={k} n={n} c={(n + 2*k - 3)//k} |T'_(n,k) of order n|={members} "
          f"matching_number(P_{n})={nu} {'OK' if line_ok else 'FAIL'}")

# Control: the checker must find members where the family is non-empty (n = 2k+1: the path).
for k in range(3, KMAX + 1):
    m = tprime_order_n_members(2 * k + 1, k)
    print(f"control k={k} n={2*k+1} members={m} {'OK' if m > 0 else 'FAIL'}")
    ok &= m > 0

print("ALL OK" if ok else "SOME CHECK FAILED")
sys.exit(0 if ok else 1)
