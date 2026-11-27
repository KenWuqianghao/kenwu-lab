#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. check_statement.py 3000: the statement from the definitions, the values, the example N = 22.
# 2. check_lean_route.py 4000: each step of the proof (Section 3), by brute force.
# 3. check_nu2.py 700: nu2(N) = -sigma1(N)/2 (mod 4) for N = 6 (mod 8) (Section 4).
# 4. sieve.py 3000000: the statement for N <= 3e6, and the classes mod 16, 32, 64 to 3e5.
# Each output must equal the file in checks/expected/. Then every number of the paper
# that these checks give must occur in paper/paper.tex.
# The Lean file is compiled by a separate CI job (axiom audit and lake comparator).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
out="$(mktemp -d)"
python3 -I checks/check_statement.py 3000 > "$out/statement.txt"
python3 -I checks/check_lean_route.py 4000 > "$out/route.txt"
python3 -I checks/check_nu2.py 700 > "$out/nu2.txt"
python3 -I checks/sieve.py 3000000 > "$out/sieve.txt"
for n in statement route nu2 sieve; do
  diff "$out/$n.txt" "checks/expected/$n.txt"
  echo "$n: output equals checks/expected/$n.txt"
done
python3 -I - "$out" <<'PY'
import ast, re, sys
out = sys.argv[1]
st = open(f"{out}/statement.txt").read()
route = open(f"{out}/route.txt").read()
nu2 = open(f"{out}/nu2.txt").read()
sieve = open(f"{out}/sieve.txt").read()
tex = re.sub(r"\s+", " ", open("paper/paper.tex").read())
fail = []
# The proved statement holds in every check.
for text, pat in [(st, r"N=6 mod 8, N<=3000: 375 values, failures: 0"),
                  (st, r"sigma1\(N\)/2 = 0 mod 4 for N=14 mod 16, N<=3000: failures: 0"),
                  (route, r"checked 500 values N=8n\+6 <= 4000; failures: 0 \[\]"),
                  (nu2, r"checked N=8n\+6 <= 700 failures: 0"),
                  (sieve, r"N=6 mod 16, N<=3000000: tested=187500 bad=0"),
                  (sieve, r"N=14 mod 16, N<=3000000: tested=187500 bad=0")]:
    if not re.search(pat, text):
        fail.append(f"check output lacks: {pat}")
# Classes: mod 16 only 6, 14 (to 3000 and to 3e5); mod 32, 64 exactly B = 6 (mod 8).
res = ast.literal_eval(st.split("S(N) mod 4 by N mod 16: ")[1].splitlines()[0])
if [r for r in res if res[r] == [0]] != [6, 14]:
    fail.append("classes mod 16 differ from the paper")
for A in (16, 32, 64):
    got = ast.literal_eval(re.search(rf"A={A}: .*?: (\[.*\])", sieve).group(1))
    if got != [B for B in range(A) if B % 8 == 6]:
        fail.append(f"classes mod {A} differ from the paper")
# Numbers that the paper states.
S = ast.literal_eval(st.split("step 8: ")[1].splitlines()[0])
ctrl = ast.literal_eval(st.split("N=2,10,18,26: ")[1].splitlines()[0])
need = [
    "$S(N)$ & " + " & ".join(map(str, S[:8])) + "\\\\",
    "$S(N)$ & " + " & ".join(map(str, S[8:])) + " & \\\\",
    "$S(N)\\bmod 4=" + ", ".join(map(str, ctrl)) + "$",
    "all 375 values $N\\equiv 6\\pmod 8$ with $N\\le 3000$",
    "all 500 values $N\\equiv 6\\pmod 8$ with $N\\le 4000$",
    "$N\\le 3\\cdot 10^6$ (187\\,500 values",
    "For $N\\le 3\\cdot 10^5$ and moduli $A=16,32,64$",
    "for all $N\\equiv 6\\pmod 8$ with $N\\le 700$",
    "For $1\\le N\\le 3000$, the classes $N\\equiv 6$ and $N\\equiv 14\\pmod{16}$",
]
ex = {k: v for k, v in re.findall(r"\|(\w+<?)\|=(\d+)", st)}
X1lt = ast.literal_eval(re.search(r"X1<=(\[.*\])", st).group(1))
Z = ast.literal_eval(re.search(r"Zs=(\[.*\])", st).group(1))
F = ast.literal_eval(re.search(r"F=(\[.*?\])", st).group(1))
Xb = ast.literal_eval(re.search(r"Xb=(\[.*?\])", st).group(1))
fixed = ast.literal_eval(re.search(r"fixed=(\[.*?\])", st).group(1))
tup = lambda t: "(" + ",".join(map(str, t)) + ")"
need += [
    f"$|X|=S(22)={ex['X']}$",
    "$X_1^<$ is $\\{" + ",".join(map(tup, X1lt)) + "\\}$",
    f"$|X_1|={2 * len(X1lt)}$",
    f"The set $Z$ has {len(Z)} points",
    ", ".join(f"${tup(t)}$" for t in Z if t[1] == t[2]).replace(", $(3", " and $(3"),
    f"with $k=x$ and $y=z$ is ${tup(F[0])}$, so $F={len(F)}$",
    "$X_b$ is $\\{" + ",".join(map(tup, Xb)) + "\\}$",
    f"$|X_0|={2 * len(Xb)}$",
    f"The only fixed point of step~7 is ${tup(fixed[0])}$",
    f"$S(22)={2 * len(X1lt)}+{2 * len(Xb)}={ex['X']}$",
]
fail += [f"missing in paper.tex: {x}" for x in need if x not in tex]
print("paper numbers match the check output" if not fail else "\n".join(fail))
sys.exit(1 if fail else 0)
PY
echo "ci.sh: all checks passed"
