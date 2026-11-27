"""Independent verifier check (written without reading checks/verify.py).

Part A (generative): for n = 2k, build every graph of Construction 9 of Hou-Tan
(arXiv:2607.11061v2) as an explicit graph, from every labelled tree T1 on k vertices
and every admissible f. Record the orders. Claim: no order equals 2k.
Part B (structural, different method): for every tree G of order n (networkx
nonisomorphic_trees) with matching number k, decide membership in T'_{n,k} by searching
for the set X directly in G. Claim: for n = 2k, k >= 3 no tree is a member, and the
tree of minimum spectral radius is the path. Controls: n = 2k+1 and (n,k) = (4,2).
Part C: both floor and ceiling readings of c, as a robustness test.
"""
import itertools, sys
import networkx as nx
import numpy as np


def labelled_trees(k):
    if k == 1:
        g = nx.Graph(); g.add_node(0); yield g; return
    if k == 2:
        yield nx.Graph([(0, 1)]); return
    for code in itertools.product(range(k), repeat=k - 2):
        yield nx.from_prufer_sequence(list(code))


def build(T1, f):
    """Steps 1 and 2 of Construction 9, as an explicit graph."""
    G = nx.Graph()
    G.add_nodes_from(("x", i) for i in T1.nodes)
    for (i, j) in T1.edges:
        y = ("y", min(i, j), max(i, j))
        G.add_edge(("x", i), y); G.add_edge(("x", j), y)
    for i in T1.nodes:
        for t in range(f[i]):
            G.add_edge(("x", i), ("l", i, t))
    return G


def part_a(k, n, c):
    orders = {}
    seen_deg = set()
    for T1 in labelled_trees(k):
        d = [T1.degree(i) for i in range(k)]
        opts = [[v - 2 * d[i] for v in (c, c + 1) if v - 2 * d[i] >= 0] for i in range(k)]
        if any(not o for o in opts):
            continue
        key = tuple(d)
        full = key not in seen_deg  # build explicit graphs once per degree sequence + always count
        seen_deg.add(key)
        for f in itertools.product(*opts):
            if full:
                G = build(T1, f)
                assert nx.is_tree(G)
                order = G.number_of_nodes()
                assert order == k + (k - 1) + sum(f)
                assert len(nx.max_weight_matching(G, maxcardinality=True)) == k
            else:
                order = 2 * k - 1 + sum(f)
            orders[order] = orders.get(order, 0) + 1
    return orders


def member(G, n, k, c):
    """Is the tree G a graph of Construction 9 for (n,k)? Search X directly."""
    if G.number_of_nodes() != n:
        return False
    nodes = list(G.nodes)
    for X in itertools.combinations(nodes, k):
        Xs = set(X)
        if any(G.has_edge(a, b) for a, b in itertools.combinations(X, 2)):
            continue
        ok = True
        ycount = {x: 0 for x in X}; lcount = {x: 0 for x in X}
        ny = 0
        for v in nodes:
            if v in Xs:
                continue
            nb = list(G[v])
            if any(u not in Xs for u in nb):
                ok = False; break
            if len(nb) == 2:
                ny += 1
                for u in nb: ycount[u] += 1
            elif len(nb) == 1:
                lcount[nb[0]] += 1
            else:
                ok = False; break
        if not ok or ny != k - 1:
            continue
        if all(2 * ycount[x] + lcount[x] in (c, c + 1) for x in X):
            return True
    return False


def rho(G):
    return float(np.linalg.eigvalsh(nx.to_numpy_array(G))[-1])


def part_b(n, k, c):
    best = None; mins = []; members = 0; total = 0
    for G in nx.nonisomorphic_trees(n):
        if len(nx.max_weight_matching(G, maxcardinality=True)) != k:
            continue
        total += 1
        m = member(G, n, k, c)
        members += m
        r = rho(G)
        if best is None or r < best - 1e-9:
            best, mins = r, [(G, m)]
        elif abs(r - best) <= 1e-9:
            mins.append((G, m))
    return total, members, best, mins


ok = True
KA = int(sys.argv[1]) if len(sys.argv) > 1 else 8
KB = int(sys.argv[2]) if len(sys.argv) > 2 else 6
for k in range(3, KA + 1):
    n = 2 * k
    for name, c in (("floor", (n + 2 * k - 3) // k), ("ceil", -(-(n + 2 * k - 3) // k))):
        orders = part_a(k, n, c)
        good = n not in orders
        ok &= good
        print(f"A k={k} n={n} c[{name}]={c} min order built={min(orders) if orders else None} "
              f"count(order=n)={orders.get(n, 0)} {'OK' if good else 'FAIL'}")
    c1 = (2 * k + 1 + 2 * k - 3) // k
    o1 = part_a(k, 2 * k + 1, c1)
    good = o1.get(2 * k + 1, 0) > 0
    ok &= good
    print(f"A control k={k} n={2*k+1} c={c1} count(order=n)={o1.get(2*k+1, 0)} {'OK' if good else 'FAIL'}")
for k in range(3, KB + 1):
    n = 2 * k
    c = (n + 2 * k - 3) // k
    total, members, best, mins = part_b(n, k, c)
    path_min = len(mins) == 1 and max(d for _, d in mins[0][0].degree) == 2
    good = total > 0 and members == 0 and path_min
    ok &= good
    print(f"B k={k} n={n} trees with nu=k: {total}, members of T': {members}, "
          f"rho_min={best:.6f}, unique minimiser is path: {path_min} {'OK' if good else 'FAIL'}")
    n = 2 * k + 1
    c = (n + 2 * k - 3) // k
    total, members, best, mins = part_b(n, k, c)
    good = members > 0 and all(m for _, m in mins)
    ok &= good
    print(f"B control k={k} n={n} trees with nu=k: {total}, members: {members}, "
          f"minimisers: {len(mins)}, all minimisers in T': {all(m for _, m in mins)} {'OK' if good else 'FAIL'}")
# k = 2, n = 4: P4 must be a member (the claim is not made for k = 2)
P4 = nx.path_graph(4)
m = member(P4, 4, 2, (4 + 4 - 3) // 2)
ok &= m
print(f"B control k=2 n=4: P4 in T'_(4,2): {m} {'OK' if m else 'FAIL'}")
# exact: path P_{2k} has a perfect matching
for k in range(3, 11):
    assert len(nx.max_weight_matching(nx.path_graph(2 * k), maxcardinality=True)) == k
print("P_2k matching number = k for k=3..10: OK")
print("ALL OK" if ok else "SOME FAIL")
sys.exit(0 if ok else 1)
