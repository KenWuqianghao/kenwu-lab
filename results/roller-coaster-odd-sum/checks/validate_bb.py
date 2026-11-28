"""Validate oddsum_bb against brute force for small n.
For each (n, mode, T): enumerate all permutations of [n] with numpy, compute t by the turn identity,
keep those with t >= T, pi_1 <= (n+1)/2 and (mode 1) the Odd Sum property; compare the set with the
output of the compiled search. Also checks the turn identity against the definition on random samples.
Usage: python validate_bb.py <path to compiled oddsum_bb>"""
import sys, subprocess, itertools, random
import numpy as np
from math import comb
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from t_definition import t_def

def t_all(P):
    n = P.shape[1]; base = sum(comb(n, m) for m in range(3, n + 1))
    t = np.full(P.shape[0], base, dtype=np.int64)
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                x, y, z = P[:, a], P[:, b], P[:, c]
                turn = ((y > x) & (y > z)) | ((y < x) & (y < z))
                t += turn.astype(np.int64) * (2 ** a) * (2 ** (n - 1 - c))
    return t

def brute(n, mode, T):
    P = np.array(list(itertools.permutations(range(1, n + 1))), dtype=np.int8)
    keep = P[:, 0] <= (n + 1) // 2
    if mode == 1:
        for j in range(n // 2):
            keep &= ((P[:, j].astype(int) + P[:, n - 1 - j]) % 2 == 1)
    P = P[keep]; t = t_all(P); sel = t >= T
    return {(int(tt), tuple(int(v) for v in row)) for tt, row in zip(t[sel], P[sel])}, int(t.max())

def prog(exe, n, mode, T):
    out = subprocess.run([exe, str(n), str(T), str(mode)], capture_output=True, text=True, check=True).stdout
    res = set()
    begun = False
    for line in out.splitlines():
        if line.startswith('BEGIN'): begun = True; continue
        if begun and line.startswith('t='):
            tt, perm = line[2:].split()
            res.add((int(tt), tuple(int(v) for v in perm.split(','))))
    return res

exe = sys.argv[1]
random.seed(1)
for n in range(4, 9):
    for _ in range(20):
        p = random.sample(range(1, n + 1), n)
        assert t_def(p) == t_all(np.array([p]))[0], p
print('identity = definition on 100 random permutations, n = 4..8')
cases = []
for n in range(5, 11):
    for mode in ([0, 1] if n % 2 else [0]):
        _, mx = brute(n, mode, 10 ** 18)
        for T in (mx, mx - 5, mx - 50, int(mx * 0.97)):
            cases.append((n, mode, T))
ok = True
for n, mode, T in cases:
    b, _ = brute(n, mode, T); q = prog(exe, n, mode, T)
    same = b == q
    ok &= same
    print(f'n={n} mode={mode} T={T}: brute {len(b)} program {len(q)} {"SAME" if same else "DIFFERENT"}')
print('ALL SAME' if ok else 'MISMATCH')
sys.exit(0 if ok else 1)
