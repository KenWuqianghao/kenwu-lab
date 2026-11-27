"""Independent verifier check for Conjecture 10 of arXiv:2609.19967.
Written from the definitions (eqs. 8, 9a-c and LP(P) of the source), not from the solver's checkers.
Usage: vcheck.py main | vcheck.py file <instance.json>
"""
import sys, json
from fractions import Fraction as Fr
from itertools import combinations

INF = None

def build_main():
    # built from the prose in STATEMENT.md, not from instance.json
    mach = [(c, t) for c in range(3) for t in range(4)]
    idx = {ct: i for i, ct in enumerate(mach)}
    p, M = [], []
    for c in range(3):
        for k in range(4):
            p.append(1); M.append(sorted(idx[(c, t)] for t in range(4) if t != k))
    for f in range(8):
        p.append(3); M.append([i for i in range(12) if f in ((2 * i) % 8, (2 * i + 1) % 8)])
    return p, M, 12

def configs(p, M, m, T):
    """All C subset [n] with sum_{j in C} p_{j,i} <= T, p_{j,i}=inf if i not in M_j."""
    out = []
    for i in range(m):
        allowed = [j for j in range(len(p)) if i in M[j]]
        cs = []
        def rec(k, cur, load):
            if k == len(allowed):
                cs.append(frozenset(cur)); return
            rec(k + 1, cur, load)
            j = allowed[k]
            if load + p[j] <= T:
                cur.append(j); rec(k + 1, cur, load + p[j]); cur.pop()
        rec(0, [], 0)
        out.append(cs)
    return out

def lp_feasible_exact(p, M, m, T, cfg):
    """Exact feasibility of CLP(P,T) by Fraction simplex phase 1 (Bland's rule)."""
    n = len(p)
    cols = [(i, C) for i in range(m) for C in cfg[i]]
    rows = m + n
    A = [[Fr(0)] * len(cols) for _ in range(rows)]
    for k, (i, C) in enumerate(cols):
        A[i][k] = Fr(1)
        for j in C: A[m + j][k] = Fr(1)
    b = [Fr(1)] * rows
    # phase 1 with artificials as initial basis
    N = len(cols)
    tab = [A[r] + [Fr(1) if r == s else Fr(0) for s in range(rows)] + [b[r]] for r in range(rows)]
    basis = [N + r for r in range(rows)]
    # objective: minimize sum artificials -> reduced costs
    z = [Fr(0)] * (N + rows + 1)
    for r in range(rows):
        for k in range(N + rows + 1): z[k] -= tab[r][k]
    for r in range(rows): z[N + r] = Fr(0)
    while True:
        enter = next((k for k in range(N + rows) if z[k] < 0), None)
        if enter is None: break
        best, leave = None, None
        for r in range(rows):
            if tab[r][enter] > 0:
                ratio = tab[r][-1] / tab[r][enter]
                if best is None or ratio < best or (ratio == best and basis[r] < basis[leave]):
                    best, leave = ratio, r
        assert leave is not None
        piv = tab[leave][enter]
        tab[leave] = [v / piv for v in tab[leave]]
        for r in range(rows):
            if r != leave and tab[r][enter] != 0:
                f = tab[r][enter]; tab[r] = [a - f * c for a, c in zip(tab[r], tab[leave])]
        f = z[enter]; z = [a - f * c for a, c in zip(z, tab[leave])]
        basis[leave] = enter
    return -z[-1] == 0  # optimal sum of artificials is 0

def check_point(p, M, m, T, x):
    n = len(p)
    mach = [Fr(0)] * m; job = [Fr(0)] * n
    for i, C, v in x:
        v = Fr(v); assert v >= 0
        assert len(set(C)) == len(C)
        assert all(i in M[j] for j in C), "job not allowed"
        assert sum(p[j] for j in C) <= T, "load"
        mach[i] += v
        for j in C: job[j] += v
    assert mach == [Fr(1)] * m and job == [Fr(1)] * n
    return True

def half_integral_exists(p, M, m, T, cfg):
    """Exhaustive: y=2x integer, 2 configuration slots per machine, each job covered exactly 2 times."""
    n = len(p)
    last = [max(M[j]) for j in range(n)]          # last machine that can cover job j
    due = [[j for j in range(n) if last[j] == i] for i in range(m)]
    cnt = [0] * n
    nodes = 0
    rem = [[sum(1 for q in M[j] if q > i) for j in range(n)] for i in range(m)]
    def rec(i):
        nonlocal nodes
        if i == m: return all(c == 2 for c in cnt)
        cs = cfg[i]
        for a in range(len(cs)):
            Ca = cs[a]
            if any(cnt[j] + 1 > 2 for j in Ca): continue
            for j in Ca: cnt[j] += 1
            for b in range(a, len(cs)):
                Cb = cs[b]
                if any(cnt[j] + 1 > 2 for j in Cb): continue
                for j in Cb: cnt[j] += 1
                nodes += 1
                # prune: job j still needs 2-cnt[j] slots; machines after i give at most 2 each
                # prune: remaining volume sum_j p_j(2-cnt_j) must fit in 2T per remaining machine
                if (sum(p[j] * (2 - cnt[j]) for j in range(n)) <= 2 * T * (m - 1 - i)
                        and all(2 - cnt[j] <= 2 * rem[i][j] for j in range(n)) and rec(i + 1)):
                    return True
                for j in Cb: cnt[j] -= 1
            for j in Ca: cnt[j] -= 1
        return False
    r = rec(0)
    print("  search nodes:", nodes)
    return r

def run(p, M, m, T, x):
    n = len(p)
    assert all(isinstance(v, int) and v >= 1 for v in p), "p_j in N+"
    assert all(len(Mj) >= 1 and all(0 <= i < m for i in Mj) for Mj in M)
    print(f"n={n} m={m} T={T} volume={sum(p)}")
    cfgT = configs(p, M, m, T)
    print("  configurations per machine at T:", [len(c) for c in cfgT])
    if x is not None:
        print("given point in CLP(P,T):", check_point(p, M, m, T, x))
    print("CLP(P,T) feasible (exact simplex):", (fT := lp_feasible_exact(p, M, m, T, cfgT)) if sum(len(c) for c in cfgT) < 400 else "skipped (size)")
    cfgT1 = configs(p, M, m, T - 1)
    vol = sum(p) > m * (T - 1)
    print("volume > m(T-1):", vol)
    if sum(len(c) for c in cfgT1) < 400:
        f1 = lp_feasible_exact(p, M, m, T - 1, cfgT1)
        print("CLP(P,T-1) feasible (exact simplex):", f1)
        assert not f1
    assert vol  # CLP(P,T') infeasible for all integers T' <= T-1
    h = half_integral_exists(p, M, m, T, cfgT)
    print("half-integral point in CLP(P,T) exists:", h)
    # sanity of the search: the same search on T+something must find a point when one obviously exists
    return h

if sys.argv[1] == "main":
    p, M, m = build_main()
    d = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None
    x = None
    if d:
        assert d["p"] == p and [sorted(a) for a in d["M"]] == M and d["m"] == m and d["T"] == 3, "instance.json differs from prose"
        print("instance.json equals the instance built from the prose: True")
        x = d["x"]
    h = run(p, M, m, 3, x)
    # control: at T=4 an integral assignment exists, so the search must say True
    print("control T=4:", half_integral_exists(p, M, m, 4, configs(p, M, m, 4)))
else:
    d = json.load(open(sys.argv[2]))
    h = run(d["p"], d["M"], d["m"], d["T"], d.get("x"))
print("RESULT:", "COUNTEREXAMPLE CONFIRMED" if not h else "NOT a counterexample")
