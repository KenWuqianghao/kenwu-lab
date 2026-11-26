"""Independent checker (verify stage). Written from the definitions and from PROOF.md,
without reading checks/verify.py.  Usage: own_check.py A|B|C"""
import sys, itertools
from fractions import Fraction
import numpy as np
import sympy as sp
import mpmath as mp

CANDS = {
 'A': ['01','011','0','02','0232','023432','02343223432','0234344343343443432',
       '023434434334344343234344343343443432'],
 'B': ['01','011','0','02','0232','023432','02343443432','0234344343343443432',
       '023434434334344343234344343343443432'],
 'C': ['01','011','0','02','022322','02234322','0223434434322','022343443433434434322',
       '02234344343343443432343443433434434322'],
}
name = sys.argv[1]
PI = CANDS[name]
PHI = ['0'+str(i+1) for i in range(8)] + ['088']
ok_all = True
def check(cond, msg):
    global ok_all
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: ok_all = False

# ---------- 0. basic facts
check(set(''.join(PI)) == set('01234'), 'pi uses exactly the letters 0..4')
check(len(set(PI)) == 9, 'pi injective on letters')
check(all(p[0]=='0' and '0' not in p[1:] and p[1:]==p[1:][::-1] for p in PI),
      'each pi(i)0 is a palindrome and a complete return word to 0 (class P_ret, marker 0)')
h = [len(p) for p in PI]

t = sp.symbols('t')
M = sp.zeros(9,9)          # M[j,i] = number of j in phi(i)
for i,im in enumerate(PHI):
    for ch in im: M[int(ch), i] += 1
P5 = sp.Poly(t**5-2*t**4-1, t); Q4 = sp.Poly(t**4-t**3-t**2-t-1, t)
cp = sp.Poly((M - t*sp.eye(9)).det(), t)
check(sp.expand(cp.as_expr() + (P5*Q4).as_expr()) == 0 or sp.expand(cp.as_expr() - (P5*Q4).as_expr()) == 0,
      'charpoly(M) = +-P5*Q4')
check(P5.is_irreducible and Q4.is_irreducible, 'P5 and Q4 irreducible over Q')
mp.mp.dps = 80
roots = [mp.mpc(r) for r in mp.polyroots([1,-2,0,0,0,-1], maxsteps=500, extraprec=400)]
rootsQ = [mp.mpc(r) for r in mp.polyroots([1,-1,-1,-1,-1], maxsteps=500, extraprec=400)]
Lam = max(roots, key=lambda r: r.real).real
check(2 < Lam < 3 and abs(Lam**5-2*Lam**4-1) < mp.mpf(10)**-60, 'Lam = %s in (2,3)' % mp.nstr(Lam, 12))
check(all(abs(r) < Lam for r in roots+rootsQ if abs(r-Lam) > 1e-9), 'Lam is the spectral radius of M')
rho = max(abs(r) for r in roots if abs(r-Lam) > 1e-9)
print('     rho (other P5 roots) = %s ; max |Q4 root| = %s' % (mp.nstr(rho, 8), mp.nstr(max(abs(r) for r in rootsQ), 8)))
q = 1/(3-Lam)
print('     q = %s, E* = %s' % (mp.nstr(q, 14), mp.nstr(1+q, 14)))

def lt_q(a, b):
    """exact: a/b < q  <=>  3 - b/a < Lam  <=>  P5(3-b/a) < 0"""
    s = Fraction(3*a-b, a)
    return s**5 - 2*s**4 - 1 < 0
# sanity of lt_q against floats on both sides
check(lt_q(10592, 10000) and not lt_q(10593, 10000), 'exact comparison agrees with q on a sample')

# ---------- 1. certified prefixes
def iterate(k):
    s = '0'
    tr = {ord(str(i)): PHI[i] for i in range(9)}
    for _ in range(k): s = s.translate(tr)
    return s
u9 = iterate(9)
L2 = {'01'}; frontier = ['01']
while frontier:
    ab = frontier.pop(); im = PHI[int(ab[0])] + PHI[int(ab[1])]
    for i in range(len(im)-1):
        f = im[i:i+2]
        if f not in L2: L2.add(f); frontier.append(f)
check(all(f in u9 for f in L2), '%d two-letter factors of u, all occur in phi^9(0)' % len(L2))
K = 12
def plen(k):
    v = sp.ones(1,9)
    for _ in range(k): v = v*M
    return [int(x) for x in v]
CERT = min(plen(K)) + 1
Ustr = iterate(K+9); Ubig = iterate(K+11)
print('     |phi^%d(0)| = %d ; contains every factor of u of length <= %d' % (K+9, len(Ustr), CERT))
U = np.frombuffer(Ustr.encode(), dtype=np.uint8) - 48
trpi = {ord(str(i)): PI[i] for i in range(9)}
Zstr = Ustr.translate(trpi)
Z = np.frombuffer(Zstr.encode(), dtype=np.uint8) - 48
print('     |Z| = %d ; contains every factor of z of length <= %d' % (len(Z), CERT))

# ---------- 2. brute force: bispecial factors, extensions, shortest return words
def bispecials(W, Lmax):
    """all bispecial factors of length <= Lmax seen in array W, with Bext and min gap."""
    N = len(W); out = []
    level = {b'': np.arange(0, N-1)}
    for n in range(0, Lmax+1):
        new = {}
        for w, P in level.items():
            P = P[P+n < N]
            Pl = P[P > 0]
            left = W[Pl-1]; right = W[Pl+n]
            lets = np.unique(left)
            if len(np.unique(right)) >= 2 and len(lets) >= 2:
                bext = set(zip((left.tolist()), (right.tolist()))) if len(Pl) < 200000 else \
                       set((int(c)//16, int(c)%16) for c in np.unique(left.astype(np.int64)*16+right))
                gap = int(np.diff(P).min())
                out.append((w, bext, gap, int(np.diff(P).max()), len(P)))
            for a in lets:
                Pa = Pl[left == a]
                if len(np.unique(W[Pa+n])) >= 2:
                    new[bytes([48+int(a)]) + w] = Pa-1
        level = new
    return out

LU = 300
bu = bispecials(U, LU)
print('     brute force: %d bispecial factors of u with length <= %d' % (len(bu), LU))
LZ = 2000
bz = bispecials(Z, LZ)
print('     brute force: %d bispecial factors of z with length <= %d' % (len(bz), LZ))

# richness condition (bilateral orders) and ratio on all brute-force bispecials of z
def bilateral_ok(w, bext):
    le = {a for a,b in bext}; ri = {b for a,b in bext}
    b = len(bext) - len(le) - len(ri) + 1
    if w == w[::-1]: return b == sum(1 for a,bb in bext if a == bb) - 1
    return b == 0
check(all(bilateral_ok(w, be) for w, be, g, gm, c in bz),
      'bilateral-order condition holds for all %d brute-force bispecial factors of z (|v| <= %d)' % (len(bz), LZ))
zf = [(w, be) for w, be, g, gm, c in bz if b'0' not in w]
allzf = {x[i:j].encode() for p in PI for x in [p[1:]] for i in range(len(x)+1) for j in range(i, len(x)+1)}
check(max(len(p) for p in PI) + 1 <= LZ and all(w in allzf for w, be in zf),
      'Prop 7.4 input: all 0-free bispecial factors of z (%d, with the empty word) are covered by the brute force and satisfy the condition' % len(zf))
exact = [(w, g) for w, be, g, gm, c in bz if g + len(w) <= CERT and len(w) > 0]
inexact = [(len(w), g) for w, be, g, gm, c in bz if g + len(w) > CERT]
check(all(lt_q(len(w), g) for w, g in exact),
      'ratio |v|/|r| < q for all %d brute-force bispecial factors with certified shortest return word' % len(exact))
print('     not certified by brute force (|v|+gap > %d): %d factors, (|v|,gap) = %s' % (CERT, len(inexact), inexact[:8]))
best = max(exact, key=lambda x: Fraction(len(x[0]), x[1]))
print('     largest brute-force ratio: %d/%d = %.10f' % (len(best[0]), best[1], len(best[0])/best[1]))

# ---------- 3. theory: tree of bispecial factors of u (Lemmas B, C, D)
al = lambda a: a+1 if a <= 7 else 8
LMAP = {'': (set(range(9)), al), '8': ({7,8}, lambda a: 0 if a == 7 else 8)}
def children(bext):
    res = []
    for s in ('', '8'):
        for tt in ('', '8'):
            A, Lf = LMAP[s]; B, Rf = LMAP[tt]
            nb = {(Lf(a), Rf(b)) for a, b in bext if a in A and b in B}
            if len({a for a,b in nb}) >= 2 and len({b for a,b in nb}) >= 2:
                res.append((s, tt, nb))
    return res
phis = lambda w: ''.join(PHI[int(c)] for c in w)
def is22(bext): return len({a for a,b in bext}) == 2 and len({b for a,b in bext}) == 2
bu_d = {w.decode(): be for w, be, g, gm, c in bu}
roots_ = [w for w in bu_d if len(w) <= 1]
check(sorted(roots_) == ['', '0', '8'], 'bispecial factors of u of length <= 1 are eps, 0, 8')
# the tree generated by the child formula from eps and 8 (0 = child of eps)
nodes = {}; multi = []; seeds = []
stack = [('', bu_d['']), ('8', bu_d['8'])]
while stack:
    w, be = stack.pop()
    nodes[w] = be
    if is22(be):
        continue
    multi.append(w)
    for s, tt, nb in children(be):
        c = s + phis(w) + '0' + tt
        if is22(nb): seeds.append((c, nb))
        else: stack.append((c, nb))
        assert len(c) > len(w)
seeds = [('8', bu_d['8'])] + seeds if is22(bu_d['8']) else seeds
multi = [w for w in multi if not is22(nodes[w])]
print('     multi nodes: lengths %s ; seeds: lengths %s' % (sorted(len(w) for w in multi), sorted(len(w) for w, b in seeds)))
check(all(len(w) <= LU for w in multi) and all(len(w) <= LU for w, b in seeds), 'tree expansion of multi nodes stops; all multi nodes and seeds have length <= %d' % LU)
# full tree up to LU, compare with brute force (strings and Bext)
tree = {w: nodes[w] for w in multi}
for w, be in seeds:
    while len(w) <= LU:
        tree[w] = be
        ch = children(be)
        assert len(ch) == 1 and is22(ch[0][2]), 'Lemma D violated'
        s, tt, be = ch[0]; w = s + phis(w) + '0' + tt
check(tree == bu_d, 'tree nodes of length <= %d equal the brute-force bispecial factors of u (strings and Bext): %d' % (LU, len(tree)))

# ---------- 4. return words of the seeds, certified complete
Ub = Ubig
def occurrences(s, w, limit):
    res = []; i = s.find(w)
    while i != -1 and (not res or res[-1] < limit):
        res.append(i); i = s.find(w, i+1)
    return res
seedinfo = []
for w, be in seeds:
    occ = occurrences(Ub, w, len(Ustr))       # every occurrence starting in U, plus the next one
    assert occ[-1] >= len(Ustr)
    gaps = np.diff(occ); G = int(gaps.max())
    good = occ[0] <= G and G + len(w) <= CERT
    rws = {Ub[occ[i]:occ[i+1]] for i in range(len(occ)-1)}
    seedinfo.append((w, be, rws, good))
check(all(g for *_, g in seedinfo), 'for each seed: max gap + |w| <= %d, so the return words found are all return words' % CERT)
check(all(len(r) == 9 for _, _, r, _ in seedinfo), 'each of the %d seeds has exactly 9 return words' % len(seedinfo))

# ---------- 5. offspring in z (Lemmas E, F)
def lcs(a, b):
    k = 0
    while k < min(len(a), len(b)) and a[-1-k] == b[-1-k]: k += 1
    return a[len(a)-k:] if k else ''
def lcp(a, b):
    k = 0
    while k < min(len(a), len(b)) and a[k] == b[k]: k += 1
    return a[:k]
pis = lambda w: ''.join(PI[int(c)] for c in w)
def add22(be):
    (a, a2) = sorted({a for a,b in be}); (b, b2) = sorted({b for a,b in be})
    x = lcs(PI[a], PI[a2]); y = lcp(PI[b][1:]+'0', PI[b2][1:]+'0')
    assert '0' not in x and '0' not in y
    return x, y
predicted = {}      # v string -> shortest return length (None if unknown)
# 5a multi nodes: every (x, y)
X = PI
multi_off = []
for w in multi:
    be = nodes[w]
    xs = {p[i:] for a in {a for a,b in be} for p in [PI[a]] for i in range(1, len(p)+1)}
    ys = {p[1:i] for b in {b for a,b in be} for p in [PI[b]] for i in range(1, len(p)+1)}
    for x in xs:
        for y in ys:
            ext = set()
            for a, b in be:
                if PI[a].endswith(x) and PI[b][1:].startswith(y):
                    ext.add((PI[a][len(PI[a])-len(x)-1], (PI[b][1:]+'0')[len(y)]))
            if len({l for l, r in ext}) >= 2 and len({r for l, r in ext}) >= 2:
                multi_off.append((x + pis(w) + '0' + y, ext))
print('     offspring of multi nodes: %d' % len(multi_off))
bz_d = {w.decode(): (be, g) for w, be, g, gm, c in bz}
check(all(len(v) <= LZ and v in bz_d for v, e in multi_off) and all(len(v) + bz_d[v][1] <= CERT for v, e in multi_off),
      'every offspring of a multi node has length <= %d, is in the brute-force list, and its shortest return word is certified (so its ratio < q is checked above)' % LZ)
for v, e in multi_off: predicted[v] = None
# 5b chains
Mi = [[int(M[i,j]) for j in range(9)] for i in range(9)]
def mulv(v): return [sum(Mi[i][j]*v[j] for j in range(9)) for i in range(9)]
def parikh(w): return [w.count(str(i)) for i in range(9)]
dot = lambda a, b: sum(x*y for x, y in zip(a, b))
NEX = 1000
worst = None; nchain_pred = 0
chains = []
for w, be, rws, _ in seedinfo:
    wv = parikh(w); rv = [parikh(r) for r in rws]; ws = w; b0 = be
    types = []; a_list = []; bmin = []
    okc = True
    for n in range(NEX+1):
        x, y = add22(be)
        a_n = dot(h, wv) + len(x) + 1 + len(y)
        bs = [dot(h, r) for r in rv]
        a_list.append(a_n); bmin.append(min(bs))
        for bb in bs:
            if not lt_q(a_n, bb): okc = False
        fr = Fraction(a_n, min(bs))
        if worst is None or fr > worst[0]: worst = (fr, len(w), n)
        if ws is not None:
            v = x + pis(ws) + '0' + y
            assert len(v) == a_n
            if len(v) <= LZ: predicted[v] = min(bs); nchain_pred += 1
        (s, tt, nb), = children(be)
        types.append((s, tt, frozenset(be)))
        wv = mulv(wv); wv[0] += 1; wv[8] += (s == '8') + (tt == '8')
        rv = [mulv(r) for r in rv]
        if ws is not None:
            ws = s + phis(ws) + '0' + tt
            if len(ws) > 3000: ws = None
        be = nb
    per = all(types[n] == types[n+8] for n in range(NEX-8))
    chains.append((w, b0, [parikh(r) for r in rws], types, okc, per))
check(all(c[4] for c in chains), 'chains: |v(w_n)|/|pi(r)| < q exactly for all 16 seeds, all 9 return words, n <= %d' % NEX)
check(all(c[5] for c in chains), 'chains: the type sequence (s, t, Bext) has period 8 from n = 0')
print('     largest chain ratio for n <= %d: %.15f at seed length %d, n = %d' % (NEX, float(worst[0]), worst[1], worst[2]))
# 5c the predicted list equals the brute-force list on z
pred_set = set(predicted) | {w.decode() for w, be in zf}
check(pred_set == set(bz_d), 'predicted bispecial factors of z with |v| <= %d equal the brute-force list (%d vs %d)' % (LZ, len(pred_set), len(bz_d)))
mism = [(len(v), r, bz_d[v][1]) for v, r in predicted.items() if r is not None and v in bz_d and len(v)+bz_d[v][1] <= CERT and r != bz_d[v][1]]
ncmp = sum(1 for v, r in predicted.items() if r is not None and v in bz_d and len(v)+bz_d[v][1] <= CERT)
check(not mism and ncmp > 0, 'predicted shortest return words of chain offspring equal brute force (%d compared)' % ncmp)
# bilateral orders of chain offspring for all n (type is periodic): done by brute force for |v|<=LZ; here for one period of every chain from Bext
def off_ext(be):
    x, y = add22(be)
    return {(PI[a][len(PI[a])-len(x)-1], (PI[b][1:]+'0')[len(y)]) for a, b in be}, x, y
badb = 0
for w, be0, rv, types, _, _ in chains:
    pal = (w == w[::-1])
    for n in range(0, 24):
        s, tt, be = types[n]
        ext, x, y = off_ext(be)
        le = {a for a,b in ext}; ri = {b for a,b in ext}
        bo = len(ext) - len(le) - len(ri) + 1
        vpal = pal and (y == x[::-1])
        if vpal: badb += (bo != sum(1 for a,b in ext if a == b) - 1)
        else: badb += (bo != 0)
        pal = pal and (s == tt)
check(badb == 0, 'bilateral-order condition for chain offspring over 3 periods of every chain (from Bext types)')

# ---------- 6. tail of the chains
mp.mp.dps = 60
Mm = mp.matrix(Mi)
E, EL, ER = mp.eig(Mm, left=True, right=True)
idxL = max(range(9), key=lambda j: E[j].real)
check(abs(E[idxL]-Lam) < mp.mpf(10)**-40, 'numeric eigenvalues: dominant = Lam')
hm = mp.matrix([h])
coefh = [(hm*ER[:, j])[0] / (EL[j, :]*ER[:, j])[0] for j in range(9)]
isQ = [min(abs(E[j]-r) for r in rootsQ) < mp.mpf(10)**-30 for j in range(9)]
check(sum(isQ) == 4 and all(abs(coefh[j]) < mp.mpf(10)**-40 for j in range(9) if isQ[j]),
      'h is orthogonal to the right eigenvectors of the 4 roots of Q4 (numeric, 1e-40)')
# exact version: adj(M - tI) columns are right eigenvectors
adj = (M - t*sp.eye(9)).adjugate()
col = None
for j in range(9):
    c = [sp.Poly(adj[i, j], t) for i in range(9)]
    if any(sp.rem(ci, Q4).as_expr() != 0 for ci in c) and any(sp.rem(ci, P5).as_expr() != 0 for ci in c):
        col = c; break
hv = sum((h[i]*col[i] for i in range(9)), sp.Poly(0, t))
check(sp.rem(hv, Q4).as_expr() == 0, 'exact: h . v_lambda = 0 modulo Q4 (v = nonzero column of adj(M - tI))')
# left eigenvector row for exact kappa test
row = None
for i in range(9):
    r_ = [sp.Poly(adj[i, j], t) for j in range(9)]
    if any(sp.rem(rj, P5).as_expr() != 0 for rj in r_): row = r_; break
qpoly = sp.Poly(sp.invert(3-t, P5.as_expr(), t), t)     # q = 1/(3-Lam) in Q(Lam)
I9 = sp.eye(9); M8 = M**8; INV = (M8 - I9).inv()
Msp = [M**i for i in range(9)]
n_zero = 0; minkappa = None; minc_zero = None; tail_ok = True; formula_ok = True; eps_max = 0
mp.mp.dps = 400
qhi = 1/(3 - mp.findroot(lambda x: x**5-2*x**4-1, mp.mpf(Lam), tol=mp.mpf(10)**-390, maxsteps=200))
mp.mp.dps = 60
for w, be0, rvs, types, _, _ in chains:
    # w_i vectors and adds for i = 0..7 ; G_i for the step n -> n+8 at residue i
    wv = [sp.Matrix(parikh(w))]
    delta = []
    for n in range(16):
        s, tt, _b = types[n]
        d = sp.zeros(9,1); d[0] = 1; d[8] = (s == '8') + (tt == '8'); delta.append(d)
        wv.append(M*wv[-1] + d)
    adds = [1 + sum(len(z_) for z_ in add22(types[i][2])) for i in range(8)]
    hs = sp.Matrix([h])
    for r in rvs:
        rvec = sp.Matrix(r)
        for i in range(8):
            G = wv[i+8] - M8*wv[i]
            Y = -INV*G                       # Y = M^8 Y + G
            c_i = -(hs*Y)[0] - adds[i]       # exact rational
            Xr = Msp[i]*rvec                 # X = q*Xr - wv[i] + Y
            Xc = -wv[i] + Y
            # exact test: row . X == 0 in Q(Lam)?
            val = sum((row[j]*(qpoly*int(Xr[j]) + sp.Poly(Xc[j], t)) for j in range(9)), sp.Poly(0, t))
            zero = sp.rem(val, P5).as_expr() == 0
            Xnum = mp.matrix([mp.mpf(q)*int(Xr[j]) + mp.mpf(int(Xc[j].p))/int(Xc[j].q) for j in range(9)])
            kap = [coefh[j] * (EL[j, :]*Xnum)[0] for j in range(9)]
            kL = kap[idxL].real
            eps = sum(abs(kap[j]) for j in range(9) if j != idxL and not isQ[j])
            eps_max = max(eps_max, eps)
            cf = mp.mpf(int(c_i.p))/int(c_i.q)
            if zero:
                n_zero += 1
                minc_zero = cf if minc_zero is None else min(minc_zero, cf)
                if not (c_i > 0 and abs(kL) < mp.mpf(10)**-30): tail_ok = False
            else:
                minkappa = kL if minkappa is None else min(minkappa, kL)
                if not kL > mp.mpf(10)**-6: tail_ok = False
            # tail: for n = i + 8N > NEX:  D_n >= kL*Lam^n' + c_i - eps*rho^(8N), need > 0
            N0 = (NEX - i)//8
            lowtail = (0 if zero else kL*Lam**(8*N0)) + cf - eps*rho**(8*N0)
            if not (lowtail > 0 and (zero or kL*Lam**(8*N0) + min(cf, 0) > 1)): tail_ok = False
            # validate the closed form against exact D_n for N = 0..12 (400-digit q)
            a_cur = wv[i]; b_cur = Xr
            for N in range(0, 13):
                n = i + 8*N
                Dn_exact = None
                a_n = int((hs*a_cur)[0]) + adds[i]; b_n = int((hs*b_cur)[0])
                with mp.workdps(400):
                    Dn_exact = qhi*b_n - a_n
                Dn_formula = sum(kap[j]*E[j]**(8*N) for j in range(9) if not isQ[j]) + cf
                with mp.workdps(60):
                    if abs(Dn_exact - Dn_formula) > mp.mpf(10)**-15 * max(1, abs(Dn_exact)): formula_ok = False
                a_cur = M8*a_cur + (wv[i+8] - M8*wv[i]); b_cur = M8*b_cur
check(formula_ok, 'closed form D_n = sum kappa_mu mu^(8N) + c_i agrees with exact D_n (N = 0..12, all seeds, return words, residues)')
check(tail_ok, 'tail n > %d: kappa_Lam = 0 exactly with c_i > 0, or kappa_Lam > 0; bound positive' % NEX)
print('     pairs (seed, return word, residue) with kappa_Lam = 0 exactly: %d ; min c_i there = %s ; smallest nonzero kappa_Lam = %s ; max eps = %s'
      % (n_zero, mp.nstr(minc_zero, 8), mp.nstr(minkappa, 8), mp.nstr(eps_max, 8)))
check(n_zero > 0, 'at least one chain has kappa_Lam = 0 (ratio tends to q, so E(z) >= 1 + q)')
print('RESULT:', 'ALL OWN CHECKS PASSED' if ok_all else 'SOME CHECK FAILED')
