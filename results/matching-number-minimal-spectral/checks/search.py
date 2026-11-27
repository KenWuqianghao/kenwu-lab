"""Search all trees of order n for the spectrally minimal trees with matching number k,
and test membership in the family T'_{n,k} of Hou-Tan (arXiv:2607.11061, Construction 9).
Floating point here is a diagnostic only; checks/verify.py certifies the result exactly."""
import sys, itertools, json
import numpy as np
import networkx as nx


def canon(adj, root=None):
    """Canonical string of an unlabelled tree (AHU encoding at the centre)."""
    n = len(adj)
    if n == 1:
        return "()"
    deg = [len(a) for a in adj]
    leaves = [v for v in range(n) if deg[v] <= 1]
    rem = n
    removed = [False] * n
    while rem > 2:
        nl = []
        for v in leaves:
            removed[v] = True
            rem -= 1
            for u in adj[v]:
                if not removed[u]:
                    deg[u] -= 1
                    if deg[u] == 1:
                        nl.append(u)
        leaves = nl
    centres = [v for v in range(n) if not removed[v]]

    def enc(v, p):
        return "(" + "".join(sorted(enc(u, v) for u in adj[v] if u != p)) + ")"

    return min(enc(c, -1) for c in centres)


def matching_number(adj):
    n = len(adj)
    # greedy leaf matching is optimal on trees
    matched = [False] * n
    parent = [-1] * n
    seen = [False] * n
    st = [0]
    seen[0] = True
    order = []
    while st:
        v = st.pop()
        order.append(v)
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True
                parent[u] = v
                st.append(u)
    m = 0
    for v in reversed(order):
        p = parent[v]
        if p >= 0 and not matched[v] and not matched[p]:
            matched[v] = matched[p] = True
            m += 1
    return m


def tprime(n, k):
    """All trees in T'_{n,k} as canonical strings, with their adjacency lists."""
    out = {}
    if n < 2 * k:
        return out
    c = (n + 2 * k - 3) // k
    nf = n - (2 * k - 1)
    t1s = list(nx.nonisomorphic_trees(k)) if k >= 2 else [nx.empty_graph(1)]
    for T1 in t1s:
        X = list(T1.nodes())
        d = [T1.degree(x) for x in X]
        choices = []
        for x in X:
            choices.append([f for f in (c - 2 * d[x], c + 1 - 2 * d[x]) if f >= 0])
        for fs in itertools.product(*choices):
            if sum(fs) != nf:
                continue
            adj = [[] for _ in range(k)]
            for (a, b) in T1.edges():
                y = len(adj)
                adj.append([a, b])
                adj[a].append(y)
                adj[b].append(y)
            for i, f in enumerate(fs):
                for _ in range(f):
                    l = len(adj)
                    adj.append([i])
                    adj[i].append(l)
            assert len(adj) == n
            out[canon(adj)] = adj
    return out


def rho(adj):
    n = len(adj)
    A = np.zeros((n, n))
    for v in range(n):
        for u in adj[v]:
            A[v, u] = 1
    return float(np.linalg.eigvalsh(A)[-1])


def main(nmax):
    report = []
    for n in range(2, nmax + 1):
        best = {}  # k -> (rho, [adj])
        for T in nx.nonisomorphic_trees(n):
            adj = [list(T.neighbors(v)) for v in range(n)]
            k = matching_number(adj)
            r = rho(adj)
            if k not in best or r < best[k][0] - 1e-9:
                best[k] = (r, [adj])
            elif abs(r - best[k][0]) <= 1e-9:
                best[k][1].append(adj)
        for k in sorted(best):
            r, mins = best[k]
            tp = tprime(n, k)
            inside = [canon(a) in tp for a in mins]
            tpr = min((rho(a) for a in tp.values()), default=None)
            row = dict(n=n, k=k, rho_min=r, n_min=len(mins), n_min_in_Tp=sum(inside),
                       size_Tp=len(tp), rho_min_Tp=tpr,
                       outside=[canon(a) for a, i in zip(mins, inside) if not i])
            report.append(row)
            if not all(inside):
                print(json.dumps(row), flush=True)
    json.dump(report, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main(int(sys.argv[1]))
