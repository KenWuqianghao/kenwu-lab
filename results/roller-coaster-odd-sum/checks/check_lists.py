"""Fast checks of the data lists (no search). Exits 1 if any check fails.

1. data/rc17.txt: 128 distinct permutations of [17], each with t = 798783 (turn identity; the first
   one also from the definition), none with the Odd Sum property, closed under reversal and complement,
   and the witness is in the list.
2. data/oddsum17_t798775.txt: 96 distinct Odd Sum permutations of [17] with pi_1 <= 9 and t = 798775;
   with complements there are 128.
3. The permutations of the literature that the paper quotes have the values it states.
4. data/rc15.txt, data/rc16.txt: RC(15) and RC(16) (from checks/run_rc.py); Conjecture 2.4 holds.
5. data/logs/rc_exact_n3_to_14.txt: exact RC(n) for n = 3..14 (n = 14: pi_1 <= 7, with complements);
   Conjecture 2.4 holds for each n = 3..14.
Prints one line per check and a JSON summary on the last line."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rc_lib import t_turn, odd_sum, complement, read_list
from t_definition import t_def

root = Path(__file__).resolve().parent.parent
ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + msg)

W = (8, 14, 3, 15, 6, 10, 2, 17, 7, 12, 1, 16, 5, 11, 4, 13, 9)
rc = read_list(root / "data/rc17.txt")
S = set(rc)
check(len(rc) == 128 and len(S) == 128, f"rc17: {len(S)} distinct permutations")
check(all(sorted(p) == list(range(1, 18)) for p in rc), "rc17: all are permutations of [17]")
check(all(t_turn(p) == 798783 for p in rc), "rc17: every t = 798783 (turn identity)")
check(t_def(list(rc[0])) == 798783, "rc17: first entry t = 798783 from the definition")
check(sum(odd_sum(p) for p in rc) == 0, "rc17: no element has the Odd Sum property")
check(all(p[::-1] in S and complement(p) in S for p in rc), "rc17: closed under reversal and complement")
check(W in S, "rc17: contains the witness")
check(sum(p[0] <= 9 for p in rc) == 96, "rc17: 96 elements with pi_1 <= 9")
bad = {tuple(j + 1 for j in range(8) if (p[j] + p[16 - j]) % 2 == 0) for p in rc}
check(bad == {(4, 6)}, f"rc17: the even sums pi_j + pi_(18-j) are at j in {sorted(bad)} for every element")
alt = lambda p: all((p[i] - p[i - 1]) * (p[i + 1] - p[i]) < 0 for i in range(1, len(p) - 1))
check(all(alt(p) for p in rc), "rc17: every element is alternating or reverse-alternating (Conjecture 2.1)")
check(all(abs(p[0] - p[-1]) == 1 for p in rc), "rc17: |pi_1 - pi_17| = 1 for every element")
check(sum(p[0] == 8 and p[-1] == 9 for p in rc) == 32, "rc17: 32 elements with pi_1 = 8, pi_17 = 9 (Conjecture 2.2)")
def g(p, L):  # Ahmed-Snevily g_L: swap pi_i and pi_(n-i+1) for each i in L
    q = list(p)
    for i in L:
        q[i - 1], q[17 - i] = q[17 - i], q[i - 1]
    return tuple(q)
gW = {h(g(W, [i + 1 for i in range(8) if m >> i & 1])) for m in range(256) for h in (lambda x: x, complement)}
check(len(gW) == 512 and S <= gW and {p for p in gW if t_turn(p) == 798783} == S,
      "rc17: RC(17) is the set of maximisers of t in g(witness) (512 permutations)")

os_ = read_list(root / "data/oddsum17_t798775.txt")
check(len(set(os_)) == 96 and all(sorted(p) == list(range(1, 18)) and p[0] <= 9 for p in os_), "oddsum17: 96 distinct permutations, pi_1 <= 9")
check(all(odd_sum(p) and t_turn(p) == 798775 for p in os_), "oddsum17: all Odd Sum, all t = 798775")
full = set(os_) | {complement(p) for p in os_}
check(len(full) == 128, f"oddsum17: {len(full)} with complements")
check(not (full & S), "oddsum17 and rc17 are disjoint")

lit = {  # permutation: (t, Odd Sum?) as stated in the paper
    (8, 13, 3, 12, 5, 16, 1, 10, 7, 17, 2, 11, 6, 15, 4, 14, 9): (798471, True),   # Ahmed-Snevily, n = 17
    W: (798783, False),                                                               # Botler-Netto / Netto, n = 17
    (7, 11, 3, 13, 5, 9, 1, 14, 6, 10, 2, 12, 4, 8): (81350, True),                   # n = 14
    (7, 12, 3, 14, 5, 10, 1, 15, 6, 9, 2, 13, 4, 11, 8): (174954, True),              # Netto, n = 15
    (8, 12, 4, 14, 2, 10, 6, 16, 1, 11, 7, 15, 3, 13, 5, 9): (374409, True),          # n = 16
}
for p, (t, o) in lit.items():
    check(t_turn(p) == t and odd_sum(p) == o, f"n={len(p)} {','.join(map(str, p))}: t = {t}, Odd Sum = {o}")
check(t_def(list(W)) == 798783, "witness: t = 798783 from the definition (2^17 subsequences)")

# exact data n = 3..14 (checks/rc4.c output)
small = {}; cur = None
for line in open(root / "data/logs/rc_exact_n3_to_14.txt"):
    if line.startswith("BEGIN n="):
        cur = int(line.split("=")[1]); small[cur] = []
    elif line.startswith("t=") and cur:
        a, b = line.split(); small[cur].append((int(a[2:]), tuple(map(int, b.split(",")))))
counts, tmax = {}, {}
for n, rows in small.items():
    perms = {p for _, p in rows}
    assert all(t_turn(p) == t for t, p in rows)
    if n == 14:
        perms |= {complement(p) for p in perms}
    tmax[n] = max(t for t, _ in rows)
    counts[n] = len(perms)
    check(all(odd_sum(p) for p in perms), f"n={n}: |RC(n)| = {len(perms)}, tmax = {tmax[n]}, Conjecture 2.4 holds")
for n, (tm, size) in {15: (174954, 128), 16: (374409, 4)}.items():
    L = read_list(root / f"data/rc{n}.txt"); Sn = set(L)
    check(len(Sn) == len(L) == size and all(sorted(p) == list(range(1, n + 1)) and t_turn(p) == tm for p in L)
          and all(p[::-1] in Sn and complement(p) in Sn for p in L) and all(odd_sum(p) for p in L),
          f"rc{n}: {size} permutations, t = {tm}, closed under reversal and complement, Conjecture 2.4 holds")
res = {"rc17": len(S), "oddsum17_with_complements": len(full), "rc_counts_3_14": counts, "tmax_3_14": tmax}
print(json.dumps(res))
print("check_lists: ALL PASS" if ok else "check_lists: FAILED")
sys.exit(0 if ok else 1)
