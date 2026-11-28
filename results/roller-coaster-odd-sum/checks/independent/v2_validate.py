# Verifier round 2: compare v2_bb with brute force over all permutations (own evaluator), n = 5..9,
# both modes, several thresholds. Usage: python3 -I v2_validate.py <path to v2_bb>
import sys, itertools, subprocess
def t_formula(p):
    n = len(p); s = (1 << n) - 1 - n - n*(n-1)//2
    for a in range(n):
        for b in range(a+1, n):
            for c in range(b+1, n):
                if (p[b] > p[a]) == (p[b] > p[c]): s += (1 << a) * (1 << (n-1-c))
    return s
def t_brute(p):
    n = len(p); s = 0
    for mask in range(1 << n):
        tau = [p[i] for i in range(n) if mask >> i & 1]
        if len(tau) >= 3:
            runs = prev = 0
            for x, y in zip(tau, tau[1:]):
                d = 1 if y > x else -1
                if d != prev: runs += 1
                prev = d
            s += runs
    return s
ok = True; nsets = 0
for n in range(5, 10):
    vals = {}
    for p in itertools.permutations(range(1, n+1)):
        vals[p] = t_formula(p)
        if n <= 7: assert vals[p] == t_brute(p)
    for mode in (0, 1):
        def good(p): return mode == 0 or all((p[j] + p[n-1-j]) % 2 == 1 for j in range(n//2))
        cand = sorted({v for p, v in vals.items() if good(p)}, reverse=True)
        for T in (cand[0] + 1, cand[0], cand[1], cand[3], cand[min(10, len(cand)-1)]):
            want = {p for p, v in vals.items() if v >= T and good(p)}
            out = subprocess.run([sys.argv[1], str(n), str(T), str(mode), "1", str(n)], capture_output=True, text=True).stdout
            got = set()
            for line in out.splitlines():
                if line.startswith("PERM"):
                    tv = int(line.split()[1][2:]); p = tuple(map(int, line.split(":")[1].split()))
                    assert vals[p] == tv; assert p not in got; got.add(p)
            nsets += 1; same = got == want; ok &= same
            print(f"n={n} mode={mode} T={T} brute={len(want)} search={len(got)} {'EQUAL' if same else 'DIFFERENT'}")
print(nsets, "sets;", "ALL EQUAL" if ok else "FAILED")
sys.exit(0 if ok else 1)
