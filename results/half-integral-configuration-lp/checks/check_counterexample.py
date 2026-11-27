"""Exact checker for a counterexample to Conjecture 10 of arXiv:2609.19967.

Input JSON: {"p": [...], "M": [[machines of job j], ...], "m": m, "T": T,
             "x": [[i, [jobs], "num/den"], ...]}  (a rational point of CLP(P,T)).
Checks (exact, no floating point):
 1. x is in CLP(P,T): configurations fit in T, machine sums = 1, job sums = 1, x >= 0.
 2. CLP(P,T) has no point with entries in {0,1/2,1}: exhaustive depth-first search
    over multisets of 2 configurations per machine that cover every job exactly twice.
Since CLP(P,LP(P)) is a subset of CLP(P,T) for T >= LP(P), (1)+(2) disprove the conjecture.
"""
import json, sys
from fractions import Fraction


def check_point(p, M, m, T, x):
    msum = [Fraction(0)] * m
    jsum = [Fraction(0)] * len(p)
    for i, C, v in x:
        v = Fraction(v)
        assert v >= 0
        assert all(i in M[j] for j in C), "job not allowed on machine"
        assert len(set(C)) == len(C)
        assert sum(p[j] for j in C) <= T, "configuration too large"
        msum[i] += v
        for j in C:
            jsum[j] += v
    assert all(s == 1 for s in msum), msum
    assert all(s == 1 for s in jsum), jsum


def no_half_integral(p, M, m, T):
    n = len(p)
    # Half-integral point <=> each machine gets 2 slots of capacity T; each job has
    # 2 copies in 2 different slots (a configuration is a set), slots of allowed machines.
    slots = [(i, s) for i in range(m) for s in range(2)]
    load = [0] * len(slots)
    content = [set() for _ in slots]
    order = sorted(range(n), key=lambda j: -p[j])
    copies = [(j, c) for j in order for c in range(2)]

    def dfs(k):
        if k == len(copies):
            return True
        j, c = copies[k]
        tried = set()
        for t, (i, s) in enumerate(slots):
            if i not in M[j] or j in content[t] or load[t] + p[j] > T:
                continue
            if c == 1 and t <= first[j]:
                continue  # symmetry: second copy in a later slot
            sig = (i, load[t], frozenset(content[t]))
            if sig in tried:
                continue  # identical slots of the same machine
            tried.add(sig)
            load[t] += p[j]; content[t].add(j)
            if c == 0:
                first[j] = t
            if dfs(k + 1):
                return True
            load[t] -= p[j]; content[t].discard(j)
        return False

    first = {}
    return not dfs(0)


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    p, M, m, T = d["p"], [set(q) for q in d["M"]], d["m"], d["T"]
    check_point(p, M, m, T, d["x"])
    print("CLP(P,T) point: verified")
    assert no_half_integral(p, M, m, T)
    print("no half-integral point in CLP(P,T): verified")
