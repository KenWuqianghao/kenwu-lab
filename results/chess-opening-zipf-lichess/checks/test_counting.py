"""Code check: sort/LCP node counts equal direct prefix-dictionary counts (synthetic games)."""
import sys
from collections import Counter
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from zipflib import D, sort_lcp, subset_lcp, depth_hists

rng = np.random.default_rng(1)
n = 100_000
p = 1.0 / np.arange(1, 9) ** 1.5; p /= p.sum()
tok = rng.choice(np.arange(1, 9), size=(n, D), p=p).astype(np.uint16)
L = rng.integers(1, D + 1, size=n).astype(np.uint8)
L[rng.random(n) < 0.5] = D
for i in range(n):
    tok[i, L[i]:] = 0
perm, lcp = sort_lcp(lambda c: tok[:, c], n)
for name, sel in [("all", np.arange(n)), ("subset", np.sort(rng.choice(n, 30_000, replace=False)))]:
    h = depth_hists(subset_lcp(lcp, sel), L[perm][sel])
    games = perm[sel]
    bad = 0
    for d in range(1, D + 1):
        cnt = Counter(tuple(tok[g, :d]) for g in games if L[g] >= d)
        ref = Counter(cnt.values())
        got = dict(zip(h[d][0].tolist(), h[d][1].astype(int).tolist()))
        bad += ref != got
    print(name, "depths with a mismatch:", bad)
    assert bad == 0
print("PASS")
