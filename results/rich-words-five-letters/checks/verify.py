#!/usr/bin/env python3
"""Computer-assisted check that z = pi(u_9) is rich and has E(z) = E*(u_9).

u_9 is the fixed point of phi: i -> 0(i+1) (i <= 7), 8 -> 088.
pi is a morphism Sigma_9 -> Sigma_5 with pi(i) = '0' + x_i, x_i a 0-free palindrome
(class P_ret with marker '0').

The method (see PROOF.md for the mathematics):
  E(z) = 1 + sup |v|/|r| over bispecial v of z and return words r of v
  (Theorem 7.2 of the source = [13, Thm 3]).
  We show |v|/|r| < q := 1/(3 - Lam), Lam the dominant root of t^5 - 2t^4 - 1,
  for every bispecial v, and that the ratio tends to q along one chain.

All comparisons with q in the finite checks are exact: for integers a, b > 0,
  a/b < q  <=>  P5(3 - b/a) < 0,  P5(t) = t^5 - 2t^4 - 1  (Lemma in PROOF.md).
The only floating-point step is the bound on the 4 eigenvalue terms with |mu| < 1
in the tail of each infinite chain; it uses mpmath with 60 digits, and the margins are large.
Whether the dominant (Lam) coefficient is exactly zero is decided exactly in Q(Lam).

Usage: python3 checks/verify.py [A|B|C]
"""
import sys, itertools, time, json, os
from fractions import Fraction
import sympy as sp
import mpmath as mp

T0 = time.time()
CANDIDATES = {
    'A': '01 011 0 02 0232 023432 02343223432 0234344343343443432 023434434334344343234344343343443432',
    'B': '01 011 0 02 0232 023432 02343443432 0234344343343443432 023434434334344343234344343343443432',
    'C': '01 011 0 02 022322 02234322 0223434434322 022343443433434434322 02234344343343443432343443433434434322',
}
name = sys.argv[1] if len(sys.argv) > 1 else 'A'
PI = CANDIDATES[name].split()
D = 9
SIG = '012345678'
h = [len(b) for b in PI]
print(f"candidate {name}: pi =", PI)
print("h =", h)

FAIL = []
def check(cond, msg):
    if not cond:
        FAIL.append(msg)
        print("FAIL:", msg)
    return cond

# ---------------------------------------------------------------- pi is P_ret
for i, b in enumerate(PI):
    x = b[1:]
    check(b[0] == '0' and '0' not in x and x == x[::-1], f"pi({i}) not of form 0x with x 0-free palindrome")
check(len(set(PI)) == D, "pi not injective on letters")

# ---------------------------------------------------------------- phi, u_9
def phi_letter(c):
    i = int(c)
    return '0' + str(i + 1) if i < D - 1 else '0' + str(D - 1) * 2
PHI = {c: phi_letter(c) for c in SIG}
def phi(w): return ''.join(PHI[c] for c in w)
def piw(w): return ''.join(PI[int(c)] for c in w)
def parikh(w):
    v = [0] * D
    for c in w: v[int(c)] += 1
    return v
def hlen(vec): return sum(h[i] * vec[i] for i in range(D))

# exact comparison a/b < q
def P5(s): return s**5 - 2 * s**4 - 1
def ratio_lt_q(a, b):
    """True iff a/b < q = 1/(3-Lam). a >= 0, b > 0 integers."""
    if a == 0: return True
    return P5(Fraction(3) - Fraction(b, a)) < 0

# ---------------------------------------------------------------- language of u
# L2 closure: 2-letter factors of u. u starts with 01; L2(u) is the closure of {'01'}
# under ab -> 2-factors of phi(ab) (every 2-factor of u = phi(u) lies in phi(ab), ab in L2).
L2 = {'01'}
while True:
    new = set(L2)
    for ab in L2:
        s = phi(ab)
        new |= {s[i:i+2] for i in range(len(s) - 1)}
    if new == L2: break
    L2 = new
pre = '0'; j0 = 0
while not all(ab in pre for ab in L2):
    pre = phi(pre); j0 += 1
# every factor t of u with |t| <= min_c |phi^k(c)| + 1 lies in phi^k(ab) for some ab in L2,
# hence in phi^(k+j0)(0).
K_EXTRA = 12
k = K_EXTRA
Pu = '0'
for _ in range(k + j0): Pu = phi(Pu)
def iterate(w, n):
    for _ in range(n): w = phi(w)
    return w
M_U = min(len(iterate(c, k)) for c in SIG) + 1  # all factors of u of length <= M_U occur in Pu
def prefix_for(m):
    """Shortest phi^(kk+j0)(0) that provably contains all factors of u of length <= m."""
    kk = 0
    while min(len(iterate(c, kk)) for c in SIG) + 1 < m: kk += 1
    return iterate('0', kk + j0)
print(f"|L2(u)| = {len(L2)}, j0 = {j0}, Pu = phi^{k+j0}(0), |Pu| = {len(Pu)}, contains all factors of length <= {M_U}")

# ---------------------------------------------------------------- matrices
Mm = sp.zeros(D, D)
for j in range(D):
    for c in PHI[str(j)]: Mm[int(c), j] += 1
def Mvec(v):
    return [sum(int(Mm[i, j]) * v[j] for j in range(D)) for i in range(D)]
t = sp.symbols('t')
P5poly = t**5 - 2 * t**4 - 1
Q4poly = t**4 - t**3 - t**2 - t - 1
check(sp.expand(Mm.charpoly(t).as_expr() - P5poly * Q4poly) == 0, "charpoly of M")
check(sp.gcd(P5poly, Q4poly) == 1 and sp.discriminant(P5poly * Q4poly, t) != 0, "eigenvalues distinct")
# right eigenvector v_lam = (lam^7(lam-2), ..., lam(lam-2), lam-2, 1)
hv = sum(h[i] * t**(7 - i) * (t - 2) for i in range(8)) + h[8]
check(sp.rem(sp.expand(hv), Q4poly, t) == 0, "h orthogonal to beta-eigenvectors (h.v_lam = 0 for roots of Q4)")
print("h . v_lam vanishes on roots of t^4-t^3-t^2-t-1:", sp.rem(sp.expand(hv), Q4poly, t) == 0)

# ---------------------------------------------------------------- bispecial factors of u
# Bext(w) as frozenset of (a,b) letter pairs.
def bext_direct(w):
    s = set(); i = Pu.find(w, 1)
    while i != -1 and i + len(w) < len(Pu):
        s.add((Pu[i - 1], Pu[i + len(w)])); i = Pu.find(w, i + 1)
    return frozenset(s)
ALPHA = {c: PHI[c][-1] for c in SIG}            # last letter of phi(c)
BETA = {c: PHI[c][1] for c in SIG}              # second letter of phi(c)
ALPHA8 = {'7': '0', '8': '8'}                   # letter before the final 8 of phi(c), c in {7,8}
BETA8 = {'7': '0', '8': '8'}                    # letter after '08' prefix of phi(c)0, c in {7,8}
def child(w, E, s, tt):
    """Word s phi(w) 0 tt and its Bext, computed from Bext(w) = E (Lemma D1)."""
    word = s + phi(w) + '0' + tt
    F = set()
    for (a, b) in E:
        if s == '8' and a not in '78': continue
        if tt == '8' and b not in '78': continue
        la = ALPHA8[a] if s == '8' else ALPHA[a]
        rb = BETA8[b] if tt == '8' else BETA[b]
        F.add((la, rb))
    return word, frozenset(F)
def lext(E): return {a for a, b in E}
def rext(E): return {b for a, b in E}
def is_bisp(E): return len(lext(E)) >= 2 and len(rext(E)) >= 2

# roots: bispecials of length <= 1 are eps, '0', '8' ('1'..'7' are always preceded by 0).
for c in '1234567':
    check(lext(bext_direct(c)) == {'0'}, f"letter {c} only preceded by 0")
E_eps = frozenset((ab[0], ab[1]) for ab in L2)
roots = [('', E_eps), ('8', bext_direct('8'))]
check(bext_direct('0') == child('', E_eps, '', '')[1], "Bext(0) = child formula")

nodes_multi = []   # bispecials with >2 left or >2 right letters (finite part)
seeds = []         # 2x2 bispecials whose parent is not 2x2 (start of infinite chains)
stack = list(roots)
seen = set()
while stack:
    w, E = stack.pop()
    if w in seen: continue
    seen.add(w)
    if len(lext(E)) == 2 and len(rext(E)) == 2:
        seeds.append((w, E)); continue
    nodes_multi.append((w, E))
    check(len(w) < 2000, "multi-extension bispecials stay short")
    for s in ('', '8'):
        for tt in ('', '8'):
            cw, cE = child(w, E, s, tt)
            if is_bisp(cE): stack.append((cw, cE))
print(f"multi-extension bispecial factors of u: {len(nodes_multi)}, lengths {sorted(len(w) for w,_ in nodes_multi)}")
print(f"chain seeds (2x2 bispecials with non-2x2 parent): {len(seeds)}, lengths {sorted(len(w) for w,_ in seeds)}")

# cross-check Bext formula against direct computation where the word is short enough
for w, E in nodes_multi + seeds:
    if len(w) + 2 <= M_U:
        check(bext_direct(w) == E, f"Bext formula vs direct for |w|={len(w)}")
# cross-check: all bispecials of u up to length 60 found directly are in the tree
def all_bisp_direct(maxlen):
    out = {}
    for L in range(0, maxlen + 1):
        facs = {}
        for i in range(1, len(Pd) - L - 1):
            f = Pd[i:i+L]
            facs.setdefault(f, set()).add((Pd[i-1], Pd[i+L]))
        for f, E in facs.items():
            if is_bisp(E): out[f] = frozenset(E)
    return out
tree_words = {}
def tree_upto(maxlen):
    res = {}
    st = list(roots)
    while st:
        w, E = st.pop()
        if len(w) > maxlen: continue
        res[w] = E
        for s in ('', '8'):
            for tt in ('', '8'):
                cw, cE = child(w, E, s, tt)
                if is_bisp(cE): st.append((cw, cE))
    return res
DL = 40
Pd = prefix_for(DL + 2)
direct = all_bisp_direct(DL)
tw = tree_upto(DL)
check(set(direct) == set(tw) and all(direct[w] == tw[w] for w in direct), "bispecials up to length 40: tree = direct")
print(f"bispecials of u of length <= {DL}: direct {len(direct)}, tree {len(tw)}")

# ---------------------------------------------------------------- occurrences and return words in u
def occurrences(w):
    occ = []; i = Pu.find(w, 1)
    while i != -1 and i + len(w) < len(Pu):
        occ.append(i); i = Pu.find(w, i + 1)
    return occ

def return_words_all(w):
    """All return words of w in u (Parikh vectors), certified from the prefix Pu alone.
    Let W be the length of the longest window of Pu that contains no occurrence of w.
    Every factor of u of length W + 1 <= M_U occurs in Pu, so it contains w. A return word r
    gives the factor r w, whose inner part of length |r| + |w| - 2 contains no w; so
    |r| + |w| - 2 <= W. If W + 2 <= M_U, then r w occurs in Pu, and r is the gap between two
    consecutive occurrences of w in Pu. So the gaps in Pu give every return word."""
    occ = []; i = Pu.find(w)
    while i != -1: occ.append(i); i = Pu.find(w, i + 1)
    W = max([occ[0] + len(w) - 1, len(Pu) - 1 - occ[-1]] +
            [p2 - p1 + len(w) - 2 for p1, p2 in zip(occ, occ[1:])])
    check(W + 2 <= M_U, f"return-word certificate for seed |w|={len(w)}: W+2={W+2} > {M_U}")
    R = {Pu[p1:p2] for p1, p2 in zip(occ, occ[1:])}
    check(len(R) == D, f"seed |w|={len(w)} has {len(R)} return words (expected 9)")
    return [parikh(r) for r in sorted(R, key=lambda r: (len(r), r))]

# ---------------------------------------------------------------- z-offspring of a bispecial of u
def lcs(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1-n] == b[-1-n]: n += 1
    return a[len(a)-n:]
def lcp(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]: n += 1
    return a[:n]

def offspring_all(w, E):
    """All bispecial v of z with v = x pi(w) 0 y (x suffix of some x_a, y prefix of some x_b),
    with the set of admissible (a,b) pairs. Returns list of (|v|, x, y, admissible pairs)."""
    res = []
    xs = set(); ys = set()
    for a in lext(E):
        xa = PI[int(a)][1:]
        for L in range(len(xa) + 1): xs.add(xa[len(xa)-L:])
    for b in rext(E):
        xb = PI[int(b)][1:]
        for L in range(len(xb) + 1): ys.add(xb[:L])
    for x in xs:
        for y in ys:
            pairs = set(); ext = set()
            for (a, b) in E:
                blk_a = PI[int(a)]; xb = PI[int(b)][1:] + '0'
                if not blk_a.endswith(x) or len(x) >= len(blk_a): continue
                if not xb.startswith(y): continue
                ext.add((blk_a[len(blk_a)-len(x)-1], xb[len(y)]))
                pairs.add((a, b))
            if len({e[0] for e in ext}) >= 2 and len({e[1] for e in ext}) >= 2:
                res.append((len(x) + len(piw(w)) + 1 + len(y), x, y, pairs, frozenset(ext)))
    return res

def min_filtered_return(w, pairs, vlen):
    """Shortest return word of v (|v| = vlen) = min |pi(u[p1:p2])| over consecutive occurrences
    of w in u whose (left,right) letters lie in `pairs`. Exact if the u-factor spanning the
    two occurrences with their extension letters has length <= M_U."""
    occ = occurrences(w)
    good = [p for p in occ if (Pu[p-1], Pu[p+len(w)]) in pairs]
    best = None; bestu = None
    for p1, p2 in zip(good, good[1:]):
        L = len(piw(Pu[p1:p2]))
        if best is None or L < best: best, bestu = L, p2 - p1
    check(best is not None, "filtered return word exists")
    # any return word r with |pi(r)| <= best has |r| <= best, so its u-factor
    # (with extension letters) has length <= best + |w| + 2.
    check(best + len(w) + 2 <= M_U, f"certificate length for filtered return (|w|={len(w)})")
    return best

def bilateral_ok(is_pal, E, info):
    """Richness criterion ([21, Thm 4, item 3]): b(v) = 0 for non-palindromes,
    b(v) = #Pext(v) - 1 for palindromes."""
    b = len(E) - len({a for a, _ in E}) - len({c for _, c in E}) + 1
    target = (len({a for a, c in E if a == c}) - 1) if is_pal else 0
    return check(b == target, f"bilateral order: {info}: b={b}, target={target}")
N_BILAT = [0]
worst = (Fraction(0), None)
DUMP = []
def record(a, b, info):
    global worst
    ok = ratio_lt_q(a, b)
    check(ok, f"ratio {a}/{b} = {a/b:.8f} not < q ({info})")
    if Fraction(a, b) > worst[0]: worst = (Fraction(a, b), info)

# ---------------------------------------------------------------- finite part 1: multi-extension w
n_fin = 0
for w, E in nodes_multi:
    for vlen, x, y, pairs, extv in offspring_all(w, E):
        vstr = x + piw(w) + '0' + y
        bilateral_ok(vstr == vstr[::-1], extv, f"multi-ext offspring |v|={vlen}")
        r = min_filtered_return(w, pairs, vlen)
        record(vlen, r, f"multi-ext w (|w|={len(w)}), x={x}, y={y}")
        DUMP.append({'v': x + piw(w) + '0' + y, 'r': r, 'src': 'multi'})
        n_fin += 1
print(f"finite part: {n_fin} bispecial factors of z from multi-extension bispecials of u")

# ---------------------------------------------------------------- finite part 2: 0-free bispecials of z
Pz_blocks = PI
zfree = {}
for c in range(D):
    ctx = PI[c] + '0'   # '0' x_c '0'
    xc = PI[c][1:]
    for i in range(len(xc)):
        for j in range(i + 1, len(xc) + 1):
            v = xc[i:j]
            zfree.setdefault(v, set()).add((ctx[i], ctx[j + 1]))
# Bext(v) for 0-free v: v occurs only inside some x_c; occurrences of v in 0x_c0 give all extensions.
# (Each letter c occurs in u, and every block is followed by '0'.)
def full_bext_zfree(v):
    s = set()
    for c in range(D):
        ctx = PI[c] + '0'
        i = ctx.find(v, 1)
        while i != -1:
            s.add((ctx[i-1], ctx[i+len(v)])); i = ctx.find(v, i + 1)
    return s
M_Z = 400
Pz = piw(prefix_for(M_Z + 1))  # contains every factor of z of length <= M_Z
zfree_bisp = []
for v in zfree:
    E = full_bext_zfree(v)
    if len({a for a, b in E}) >= 2 and len({b for a, b in E}) >= 2:
        zfree_bisp.append((v, E))
# richness criterion (Prop 7.4 of the source): bilateral orders of 0-free bispecials
for v, E in zfree_bisp:
    b = len(E) - len({a for a, _ in E}) - len({c for _, c in E}) + 1
    if v == v[::-1]:
        pext = len({a for a, c in E if a == c})
        check(b == pext - 1, f"richness: palindrome bispecial {v}: b={b}, #Pext={pext}")
    else:
        check(b == 0, f"richness: non-palindrome bispecial {v}: b={b}")
    # shortest return word of v in z
    occ = []; i = Pz.find(v)
    while i != -1: occ.append(i); i = Pz.find(v, i + 1)
    r = min(p2 - p1 for p1, p2 in zip(occ, occ[1:]))
    # Pz is a prefix of pi(Pu); any return of length <= r is inside a factor of length r+|v| <= M_Z
    check(r + len(v) <= M_Z, "certificate for 0-free return word")
    record(len(v), r, f"0-free v={v}")
    DUMP.append({'v': v, 'r': r, 'src': '0free'})
# empty word: Bext(eps) = 2-letter factors of z (Pz contains all factors of length <= M_Z)
E_eps_z = {(Pz[i], Pz[i+1]) for i in range(len(Pz) - 1)}
bilateral_ok(True, E_eps_z, "empty word of z")
print(f"0-free bispecial factors of z: {len(zfree_bisp)}: {[v for v,_ in zfree_bisp]}")
print("richness criterion ([21, Prop 19] = source Prop 7.4) on them:", not any('richness' in f for f in FAIL))

# ---------------------------------------------------------------- infinite chains
mp.mp.dps = 60
def LamR_check(x): return x.real
lam_roots = [mp.mpc(r) for r in mp.polyroots([1, -2, 0, 0, 0, -1], maxsteps=200, extraprec=200)]
Lam = max(lam_roots, key=lambda r: r.real)
check(abs(Lam.imag) < mp.mpf(10)**-50 and 2 < LamR_check(Lam) < 3, "Lam real, in (2,3)")
LamR = Lam.real
others = [r for r in lam_roots if abs(r - Lam) > mp.mpf(10)**-30]
check(len(others) == 4, "4 other roots")
rho = max(abs(r) for r in others)
check(rho < 1, "other roots of P5 inside unit disc")
print(f"Lam = {mp.nstr(LamR, 20)}, other roots of P5 have modulus <= {mp.nstr(rho, 8)}")
qn = 1 / (3 - LamR)

# left eigenvector u_lam (polynomial in lam): u_i = lam^i - sum_{j<i} lam^j; right v_lam.
uL_poly = [t**i - sum(t**j for j in range(i)) for i in range(D)]
vR_poly = [t**(7 - i) * (t - 2) for i in range(8)] + [sp.Integer(1)]
Msym = sp.Matrix(Mm)
uM = (sp.Matrix([uL_poly]) * Msym)
check(all(sp.rem(sp.expand(uM[j] - t * uL_poly[j]), P5poly, t) == 0 for j in range(D)), "u_lam M = lam u_lam mod P5")
Mv = Msym * sp.Matrix(vR_poly)
check(all(sp.rem(sp.expand(Mv[i] - t * vR_poly[i]), P5poly * Q4poly, t) == 0 for i in range(D)), "M v_lam = lam v_lam mod P5*Q4 (all 9 eigenvalues)")
def ev(poly, lam): return mp.polyval([mp.mpf(int(c.p)) / int(c.q) for c in sp.Poly(poly, t).all_coeffs()], lam)
UL = {i: [ev(p, lam) for p in uL_poly] for i, lam in enumerate(lam_roots)}
VR = {i: [ev(p, lam) for p in vR_poly] for i, lam in enumerate(lam_roots)}
iLam = lam_roots.index(Lam)
def red(p): return sp.rem(sp.expand(p), P5poly, t)

def mpq(x):
    x = sp.Rational(x); return mp.mpf(int(x.p)) / int(x.q)

def analyse_chain(w0, E0, R0):
    # type sequence (Bext of the chain nodes) until it repeats
    states = []; E = E0; seenE = []
    while E not in seenE:
        seenE.append(E)
        Ls = sorted(lext(E)); Rs = sorted(rext(E))
        check(len(Ls) == 2 and len(Rs) == 2, "2x2 node")
        x = lcs(PI[int(Ls[0])], PI[int(Ls[1])])
        y0 = lcp(PI[int(Rs[0])] + '0', PI[int(Rs[1])] + '0')
        s = '8' if set(Ls) == {'7', '8'} else ''
        tt = '8' if set(Rs) == {'7', '8'} else ''
        _, cE = child('', E, s, tt)
        check(is_bisp(cE) and len(lext(cE)) == 2 and len(rext(cE)) == 2, "unique 2x2 child")
        for s2 in ('', '8'):
            for t2 in ('', '8'):
                if (s2, t2) != (s, tt): check(not is_bisp(child('', E, s2, t2)[1]), "child unique")
        extv = frozenset((PI[int(a)][len(PI[int(a)]) - len(x) - 1], (PI[int(b)] + '0')[len(y0)]) for a, b in E)
        states.append((len(x) + len(y0), s, tt, x, y0, extv))
        E = cE
    pre = seenE.index(E); per = len(states) - pre
    def st(n): return states[n] if n < pre else states[pre + (n - pre) % per]
    def step(wv, n):
        s, tt = st(n)[1], st(n)[2]
        wv = Mvec(wv); wv[0] += 1
        if s == '8': wv[8] += 1
        if tt == '8': wv[8] += 1
        return wv
    # base node nB = pre
    nB = pre
    wB = parikh(w0); RB = [list(r) for r in R0]
    for n in range(nB):
        wB = step(wB, n); RB = [Mvec(r) for r in RB]
    deltas = []; adds = []
    for tau in range(per):
        add, s, tt = st(nB + tau)[:3]
        d = [0] * D; d[0] = 1
        if s == '8': d[8] += 1
        if tt == '8': d[8] += 1
        deltas.append(sp.Matrix(d)); adds.append(add)
    Mpow = [sp.eye(D)]
    for _ in range(per): Mpow.append(Mpow[-1] * Msym)
    G = sp.zeros(D, 1)
    for tau in range(1, per + 1): G += Mpow[per - tau] * deltas[tau - 1]
    Inv = (Mpow[per] - sp.eye(D)).inv()
    hrow = sp.Matrix([h])
    cs = []
    for i in range(per):
        gp = sp.zeros(D, 1)
        for tau in range(1, i + 1): gp += Mpow[i - tau] * deltas[tau - 1]
        cs.append(sp.Rational((hrow * (Mpow[i] * Inv * G - gp))[0, 0] - adds[i]))
    Y = sp.Matrix(wB) + Inv * G
    results = []; mcut_max = 0
    for r in RB:
        rB = sp.Matrix(r)
        # (3-Lam) * u_Lam . X = u_Lam . rB - (3-Lam) u_Lam . Y   (exact, in Q(Lam))
        num = sum(uL_poly[i] * rB[i] for i in range(D)) - (3 - t) * sum(uL_poly[i] * Y[i] for i in range(D))
        exact_zero = (red(num) == 0)
        X = [qn * int(rB[i]) - mpq(Y[i]) for i in range(D)]
        kap = []
        for j in range(len(lam_roots)):
            hv = sum(h[i] * VR[j][i] for i in range(D))
            uX = sum(UL[j][i] * X[i] for i in range(D))
            uv = sum(UL[j][i] * VR[j][i] for i in range(D))
            kap.append(hv * uX / uv)
        kL = kap[iLam].real
        err0 = sum(abs(kap[j]) for j in range(len(lam_roots)) if j != iLam)
        cmin = mpq(min(cs))
        if exact_zero:
            check(cmin > 0, f"c_min > 0 on a chain with kappa_Lam = 0 (|w0|={len(w0)})")
            mcut = 0
            if cmin > 0:
                while err0 * rho**mcut >= cmin: mcut += 1
        else:
            check(abs(kL) > mp.mpf(10)**-30, "kappa_Lam numerically nonzero")
            check(kL > 0, f"kappa_Lam > 0 (|w0|={len(w0)})")
            mcut = 0
            if kL > 0:
                while not (kL * LamR**mcut + cmin - err0 * rho**mcut > 0): mcut += 1
        mcut_max = max(mcut_max, mcut)
        results.append((exact_zero, kL, cmin, err0, mcut, min(cs)))
    # exact check of every node n = 0 .. nB + mcut_max + per (and at least 60)
    Nexact = max(60, nB + mcut_max + per)
    wv = parikh(w0); Rv = [list(r) for r in R0]; wstr = w0
    pal = (w0 == w0[::-1])
    for n in range(Nexact + 1):
        xs_, ys_ = st(n)[3], st(n)[4]
        vpal = pal and (ys_[1:] == xs_[::-1])
        if wstr is not None:
            vs = xs_ + piw(wstr) + ys_
            check(vpal == (vs == vs[::-1]), "palindrome flag")
        bilateral_ok(vpal, st(n)[5], f"chain |w0|={len(w0)}, n={n}")
        N_BILAT[0] += 1
        pal = pal and (st(n)[1] == st(n)[2])
        a = hlen(wv) + st(n)[0]
        for r in Rv: record(a, hlen(r), f"chain |w0|={len(w0)}, n={n}")
        if wstr is not None:
            check(parikh(wstr) == wv, "chain word Parikh vector")
            if a <= 6000:
                DUMP.append({'v': st(n)[3] + piw(wstr) + st(n)[4], 'r': min(hlen(r) for r in Rv), 'src': f'chain{len(w0)}:{n}'})
            wstr = st(n)[1] + phi(wstr) + '0' + st(n)[2] if len(wstr) < 3000 else None
        wv = step(wv, n); Rv = [Mvec(r) for r in Rv]
    return pre, per, Nexact, results

crit = 0
for w0, E0 in sorted(seeds, key=lambda x: len(x[0])):
    R0 = return_words_all(w0)
    pre, per, Nexact, results = analyse_chain(w0, E0, R0)
    nz = sum(1 for r in results if r[0])
    crit += nz
    print(f"seed |w0|={len(w0):4d} Bext={sorted(E0)}: preperiod {pre}, period {per}, exact up to n={Nexact}; "
          f"kappa_Lam=0 for {nz}/9 return words; min kappa_Lam(nonzero)="
          f"{mp.nstr(min([r[1] for r in results if not r[0]] or [mp.inf]), 4)}; "
          f"min c over zero-kappa returns={mp.nstr(min([r[2] for r in results if r[0]] or [mp.inf]), 6)}; "
          f"max err={mp.nstr(max(r[3] for r in results), 4)}" +
          "".join(f"; critical return: c_i = {sorted(set([r[5]]))[0]} (exact min), eps = {mp.nstr(r[3], 6)}, m = {r[4]}" for r in results if r[0]))

print(f"bilateral-order criterion ([21, Thm 4]) checked on: empty word, {len(zfree_bisp)} 0-free, "
      f"{n_fin} multi-extension offsprings, and chain nodes n <= Nexact (all Bext types of every chain): "
      f"{'ok' if not any('bilateral' in f for f in FAIL) else 'FAILED'}")
check(crit > 0, "some chain has ratio tending to q (lower bound E >= E*)")
print()
print(f"largest ratio |v|/|r| found: {worst[0]} = {float(worst[0]):.10f} at {worst[1]}")
print(f"q = 1/(3-Lam) = {mp.nstr(qn, 12)};  E*(u_9) = 1 + q = {mp.nstr(1 + qn, 12)}")
print(f"time {time.time() - T0:.1f} s")
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'), exist_ok=True)
json.dump({'pi': PI, 'bispecials': DUMP}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', f'predicted_{name}.json'), 'w'))
print(f"wrote {len(DUMP)} predicted bispecial factors of z (|v| <= 6000) to checks/out/predicted_{name}.json")
print("RESULT:", "ALL CHECKS PASSED" if not FAIL else f"{len(FAIL)} CHECKS FAILED")
