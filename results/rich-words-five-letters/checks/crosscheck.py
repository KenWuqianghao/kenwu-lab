#!/usr/bin/env python3
"""Independent brute-force cross-check of checks/verify.py.

It uses only the definitions (phi, pi) and finite prefixes of z = pi(u_9) that provably
contain every factor of z up to a given length. It does not use the bispecial theory.

(a) Finds every bispecial factor v of z with |v| <= 60 and its shortest return word length
    by brute force, and compares this list with the predicted list of verify.py.
(b) For every predicted bispecial factor with |v| <= 3000, confirms in z that v is
    bispecial and that its shortest return word has the predicted length.

Usage: python3 checks/crosscheck.py [A|B|C]
"""
import json, os, sys, time
T0 = time.time()
name = sys.argv[1] if len(sys.argv) > 1 else 'A'
here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, 'out', f'predicted_{name}.json')))
PI = data['pi']
pred = data['bispecials']

PHI = {str(i): '0' + str(i + 1) for i in range(8)}
PHI['8'] = '088'
def phi(w): return ''.join(PHI[c] for c in w)
def it(w, n):
    for _ in range(n): w = phi(w)
    return w
# j0: phi^j0(0) contains all 2-letter factors of u (closure of {01} under phi)
L2 = {'01'}
while True:
    new = set(L2)
    for ab in L2:
        s = phi(ab); new |= {s[i:i+2] for i in range(len(s) - 1)}
    if new == L2: break
    L2 = new
j0 = 0; p = '0'
while not all(ab in p for ab in L2): p = phi(p); j0 += 1
TRANS = {ord(str(i)): PI[i] for i in range(9)}
_cache = {}
def zprefix(m):
    """Prefix of z containing every factor of z of length <= m.
    A factor of z of length m lies in pi(t) with t a factor of u, |t| <= m; every factor of u
    of length <= min_c |phi^k(c)| + 1 lies in phi^(k+j0)(0)."""
    k = 0
    while min(len(it(c, k)) for c in '012345678') + 1 < m: k += 1
    if k not in _cache:
        _cache[k] = it('0', k + j0).translate(TRANS)
    return _cache[k]

def occ(Z, v):
    out = []; i = Z.find(v)
    while i != -1: out.append(i); i = Z.find(v, i + 1)
    return out

# (a) brute force, |v| <= 60
LMAX = 60
Z = zprefix(2 * LMAX + 120)
print(f"(a) brute force on a prefix of z of length {len(Z)}")
brute = {}
for L in range(1, LMAX + 1):
    ext = {}
    for i in range(1, len(Z) - L - 1):
        f = Z[i:i+L]
        e = ext.get(f)
        if e is None: e = ext[f] = (set(), set())
        e[0].add(Z[i-1]); e[1].add(Z[i+L])
    for f, (le, ri) in ext.items():
        if len(le) >= 2 and len(ri) >= 2:
            o = occ(Z, f)
            r = min(b - a for a, b in zip(o, o[1:]))
            m = 2 * LMAX + 120
            while r + L + 2 > m:   # enlarge the certified prefix until it covers r
                m = r + L + 2
                Zl = zprefix(m); o = occ(Zl, f)
                r = min(b - a for a, b in zip(o, o[1:]))
            brute[f] = r
predA = {d['v']: d['r'] for d in pred if len(d['v']) <= LMAX}
ok_a = (brute == predA)
print(f"    brute-force bispecials with |v| <= {LMAX}: {len(brute)}; predicted: {len(predA)}; equal: {ok_a}")
if not ok_a:
    print("    only brute:", sorted(set(brute) - set(predA), key=len)[:10])
    print("    only predicted:", sorted(set(predA) - set(brute), key=len)[:10])
    print("    different r:", [(v, brute[v], predA[v]) for v in brute if v in predA and brute[v] != predA[v]][:10])
best = max(brute.items(), key=lambda kv: len(kv[0]) / kv[1])
print(f"    max |v|/|r| among them: {len(best[0])}/{best[1]} = {len(best[0])/best[1]:.6f}")

# (b) every predicted bispecial with |v| <= 3000
nb = 0; bad = []
for d in sorted(pred, key=lambda d: len(d['v'])):
    v, r = d['v'], d['r']
    if len(v) > 3000: continue
    Zb = zprefix(len(v) + r + 2)
    o = occ(Zb, v)
    le = {Zb[i-1] for i in o if i > 0}
    ri = {Zb[i+len(v)] for i in o if i + len(v) < len(Zb)}
    rmin = min(b - a for a, b in zip(o, o[1:]))
    if not (len(le) >= 2 and len(ri) >= 2 and rmin == r):
        bad.append((d['src'], len(v), r, rmin, le, ri))
    nb += 1
print(f"(b) predicted bispecials with |v| <= 3000 confirmed in z: {nb - len(bad)}/{nb}")
for b in bad[:10]: print("    mismatch:", b)
print(f"time {time.time() - T0:.1f} s")
print("RESULT:", "CROSS-CHECK PASSED" if ok_a and not bad else "CROSS-CHECK FAILED")
