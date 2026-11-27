"""Control: the pruned search of vcheck.py against a search with no pruning, on random small instances."""
import sys, random, io, contextlib
from itertools import combinations_with_replacement, product
import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vcheck.py")).read().split("if sys.argv[1] ==")[0]
ns = {}; exec(src, ns)
def brute(p, M, m, T, cfg):
    n = len(p)
    for choice in product(*[list(combinations_with_replacement(range(len(c)), 2)) for c in cfg]):
        cnt = [0] * n
        for i, (a, b) in enumerate(choice):
            for j in cfg[i][a]: cnt[j] += 1
            for j in cfg[i][b]: cnt[j] += 1
        if all(c == 2 for c in cnt): return True
    return False
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
agree = yes = no = 0
for it in range(400):
    m = random.choice([2, 3]); n = random.randint(2, 5)
    p = [random.randint(1, 4) for _ in range(n)]
    M = [sorted(random.sample(range(m), random.randint(1, m))) for _ in range(n)]
    T = random.randint(max(p), max(p) + 3)
    cfg = ns["configs"](p, M, m, T)
    with contextlib.redirect_stdout(io.StringIO()):
        a = ns["half_integral_exists"](p, M, m, T, cfg)
    b = brute(p, M, m, T, cfg)
    assert a == b, (p, M, m, T)
    agree += 1; yes += b; no += (not b)
print("instances:", agree, "all agree; with half-integral point:", yes, "without:", no)
