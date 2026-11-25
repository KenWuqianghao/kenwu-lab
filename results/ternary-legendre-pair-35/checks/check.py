"""Quick checks of the length-35 certificate (standard library only, under 1 s).

Run from the result folder:  python3 -I checks/check.py
Exit code 0 only if every check passes.

1. The words in data/lp35.txt equal the words eA, eB in lean/TernaryLP35.lean.
2. Both words have composition (11, 12, 12) and are invariant under j -> 6j (mod 35).
3. Two separate exact checkers accept the pair:
   check_pair.py (integer counts M_r(s) and Z[w] sums) and check_pair_zw.py (Z[w] products).
   The combined counts are (22, 24, 24) at every lag s = 1, ..., 34.
4. Positive controls: both checkers accept the published pairs of the source
   (lengths 5, 11, 14, 17, 20, 23, 29, 32).
5. Negative controls: both checkers reject each of the 140 pairs that differ
   from the certificate in one entry.
6. Each of the 15 subgroups H != {1} of Z_35^* contains <34>, <6>, <29> or <11>,
   and <6> is the only one of them that contains none of <34>, <29>, <11>.
"""
import re
import sys
import pathlib
from math import gcd

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from check_pair import check as check_counts  # noqa: E402
from check_pair_zw import is_pair as check_zw  # noqa: E402

failures = []


def report(name, ok):
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        failures.append(name)


def both_accept(A, B):
    ok1 = check_counts([int(c) for c in A], [int(c) for c in B])[0]
    ok2 = check_zw(A, B) and check_zw(A, B, full=True)
    return ok1, ok2


# 1. certificate = Lean words
cert = {}
for line in (ROOT / "data/lp35.txt").read_text().splitlines():
    if line and not line.startswith("#"):
        k, w = line.split()
        cert[k] = w
lean = (ROOT / "lean/TernaryLP35.lean").read_text()
lean_words = {}
for k in "AB":
    m = re.search(r"def e" + k + r" : Fin 35 → Fin 3 :=\s*!\[([0-9,]+)\]", lean)
    lean_words[k] = "".join(m.group(1).split(",")) if m else None
report("certificate words equal the Lean words eA, eB", lean_words == cert)
A, B = cert["A"], cert["B"]
print(f"      A = {A}\n      B = {B}")

# 2. composition and multiplier invariance
comp = [tuple(X.count(c) for c in "012") for X in (A, B)]
report(f"compositions {comp[0]} and {comp[1]} equal (11, 12, 12)", comp == [(11, 12, 12)] * 2)
report("A and B are invariant under j -> 6j mod 35",
       all(X[(6 * j) % 35] == X[j] for X in (A, B) for j in range(35)))
report("A and B are not invariant under j -> -j mod 35",
       all(any(X[(-j) % 35] != X[j] for j in range(35)) for X in (A, B)))

# 3. the pair
counts = set()
for s in range(1, 35):
    M = [0, 0, 0]
    for X in (A, B):
        for j in range(35):
            M[(int(X[j]) - int(X[(j + s) % 35])) % 3] += 1
    counts.add(tuple(M))
report(f"combined counts (M0, M1, M2)(s) for s = 1..34: {sorted(counts)}", counts == {(22, 24, 24)})
ok1, ok2 = both_accept(A, B)
report("check_pair.py accepts the pair", ok1)
report("check_pair_zw.py accepts the pair (s = 1..17 and s = 1..34)", ok2)

# 4. positive controls: pairs printed in arXiv:2611.31067v1
SOURCE_PAIRS = {
    5: ("12021", "12021"),
    11: ("00120211212", "00021122121"),
    14: ("00120202121121", "00112211022201"),
    17: ("01212201010221210", "12110220002201121"),
    20: ("01002201121212110220", "01021112010022121220"),
    23: ("01122100120211202121002", "01112122112110002202020"),
    29: ("00101212022112021122021210100", "12112000211022022011200021121"),
    32: ("01000010221121210110221201021222", "00121000222200120112121102112201"),
}
for l, (X, Y) in SOURCE_PAIRS.items():
    assert len(X) == len(Y) == l
    report(f"source pair of length {l} accepted by both checkers", all(both_accept(X, Y)))

# 5. negative controls: every single-entry change
rejected = 0
for which in "AB":
    for j in range(35):
        for d in (1, 2):
            X, Y = list(A), list(B)
            Z = X if which == "A" else Y
            Z[j] = str((int(Z[j]) + d) % 3)
            X, Y = "".join(X), "".join(Y)
            if not any(both_accept(X, Y)):
                rejected += 1
# Each position has 2 other symbols; count the 140 = 2 * 35 * 2 changed pairs.
report(f"single-entry changes rejected by both checkers: {rejected} of 140", rejected == 140)

# 6. subgroup coverage
units = [u for u in range(1, 35) if gcd(u, 35) == 1]


def gen(gs):
    S = {1}
    while True:
        T = S | {(a * g) % 35 for a in S for g in gs}
        if T == S:
            return frozenset(S)
        S = T


subs = {gen([a, b]) for a in units for b in units} - {frozenset({1})}
prime = {g: gen([g]) for g in (34, 6, 29, 11)}
covered = all(any(P <= H for P in prime.values()) for H in subs)
only6 = [sorted(H) for H in subs if not any(prime[g] <= H for g in (34, 29, 11))]
report(f"{len(subs)} subgroups H != {{1}}; each contains <34>, <6>, <29> or <11>", len(subs) == 15 and covered)
report(f"subgroups that contain none of <34>, <29>, <11>: {only6}", only6 == [[1, 6]])

print("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED")
sys.exit(1 if failures else 0)
