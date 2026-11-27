#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. check.py: exact check of the 8008 certificates and the Sylvester witness.
# 2. check_extra.py: U = Had.16.3 without row 0, the equality case 3/7, the Sylvester row sums.
# 3. vcheck.py --lp: second exact checker; it also makes its own dual vectors with HiGHS.
# 4. make_lean.py: lean/Solution.lean equals a fresh build from checks/certificate.json.
# 5. draw.py --check: the figure files equal a fresh drawing.
# 6. The numbers that the paper states occur in paper/paper.tex.
# The Lean file is compiled by a separate CI job (axiom audit and lake comparator).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
out="$(mktemp -d)"
python3 -I checks/check.py checks/certificate.json > "$out/check.txt"
python3 -I checks/check_extra.py checks/certificate.json checks/had.16.3.txt > "$out/extra.txt"
for n in check extra; do
  diff "$out/$n.txt" "checks/expected/$n.txt"
  echo "$n: output equals checks/expected/$n.txt"
done
python3 -I checks/vcheck.py checks/certificate.json --lp | tee "$out/vcheck.txt"
python3 -I checks/make_lean.py checks/certificate.json checks/lean-src/head.lean "$out/Solution.lean" 2> "$out/make_lean.txt"
cmp "$out/Solution.lean" lean/Solution.lean
read -r pairs entries < "$out/make_lean.txt"
echo "make_lean: output equals lean/Solution.lean ($pairs pairs, $entries list entries)"
python3 -I checks/draw.py --check
python3 -I - "$out" <<'PY'
import json, re, sys
out = sys.argv[1]
r = lambda n: open(f"{out}/{n}.txt").read()
tex = re.sub(r"\s+", " ", open("paper/paper.tex").read())
fail = []
v = r("vcheck")
for k in range(1, 8):
    line = next((l for l in v.splitlines() if l.startswith(f"{k}. ")), "")
    if not (line.endswith("PASS") or (k == 1 and line.endswith("True"))):
        fail.append(f"vcheck item {k}: {line!r}")
if "failures = 0 of 8008" not in v:
    fail.append("vcheck: own LP duals failed")
if "S = (0, 1, 2, 3, 4, 12)" not in v or "exact ||U_S w||_inf = 3/7" not in v:
    fail.append("vcheck: equality case differs")
syl = float(re.search(r"at t=6: ([0-9.]+)", v).group(1))
if f"{syl:.6f}" != "0.333333":
    fail.append(f"vcheck: Sylvester float value {syl}")
pairs, entries = r("make_lean").split()
d = json.load(open("checks/certificate.json"))
need = [
    "\\max_{U_6}\\valD(U_6)=-3/7",
    "\\max_{\\Hh_6}\\valD(\\Hh_6)\\ge-1/3",
    "8008 exact dual certificates",
    f"there are {pairs} such pairs and {entries} list entries in total",
    "$\\min_{S}\\min_w\\|\\Hh_S w\\|_\\infty=0.333333$",
    "$S=\\{0,1,2,3,4,12\\}$ and $w=(1,1,1,1,1,2)/7$",
    "$S_0=\\{0,1,2,4,8,15\\}$",
]
U = d["U"]
rows = " ".join(" & ".join(U[i:i + 3]) + ("\\\\" if i < 12 else "") for i in range(0, 15, 3))
need.append(rows)
fr = __import__("fractions").Fraction
ys = [[fr(x) for x in c["y"]] for c in d["subset_certificates"]]
one = sum(1 for y in ys if sum(1 for x in y if x) == 1)
most = max(sum(1 for x in y if x) for y in ys)
need.append(f"{one} of them have one nonzero entry, and none has more than {['zero','one','two','three','four','five','six'][most]}")
fail += [f"missing in paper.tex: {x}" for x in need if x not in tex]
print("paper numbers match the check output" if not fail else "\n".join(fail))
sys.exit(1 if fail else 0)
PY
echo "ci.sh: all checks passed"
