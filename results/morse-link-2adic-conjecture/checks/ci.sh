#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. The k = 2 certificate (exact values, exhaustive 2-adic test, k = 1 control).
# 2. The original checker (three methods to compute L_n) and a separate checker.
# 3. The survey for k <= 24, n <= 200; output must equal data/survey_N200_K24.txt.
# 4. The 2-adic fits of Section 5.
# 5. Every number of data/expected.json that the paper states occurs in paper/paper.tex.
# The Lean file is compiled by a separate CI job (axiom audit and lake comparator).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/certificate.py
python3 -I checks/verify_k2.py
python3 -I checks/independent_check.py
python3 -I checks/survey.py 200 24 > /tmp/morse-link-survey.txt
diff /tmp/morse-link-survey.txt data/survey_N200_K24.txt
echo "survey output equals data/survey_N200_K24.txt"
python3 -I checks/fit.py
python3 -I - <<'PY'
import json, re, sys
tex = open("paper/paper.tex").read()
flat = re.sub(r"\s+", " ", tex)
e = json.load(open("data/expected.json"))
v = e["values"]
need = [
    "$80=2^4\\cdot 5$", "$57344=2^{13}\\cdot 7$", "$2^4\\cdot 10127819$",
    v["19"]["L"][:45], v["19"]["L"][45:], "$C_{19}=1767263190$",
    f"{len(v['19']['L'])}-digit", f"{len(v['19']['odd_part'])} digits",
    "$L^{(2)}_2=82$", "=57349", "$C_3=5$", "$C_2=2$",
    "\\xi_2(2-\\alpha)+c=3", "\\xi_2(3-\\alpha)+c=11", "\\xi_2(19-\\alpha)+c=8",
    "$\\alpha_2\\equiv " + e["fits"]["k2_n4"]["alpha_binary"] + "_2 \\pmod{2^{10}}$",
    "$\\alpha_1\\equiv " + e["fits"]["k1_n2"]["alpha_binary"] + "_2\\pmod{2^{9}}$",
    "$k=2,6,10,14,18,22$",
]
for n in ("2", "3", "4", "19"):
    need.append(f"{n} & ")
    need.append(f"& {v[n]['v2']} & {v[n]['s2']} & {v[n]['d']}\\\\")
missing = [x for x in need if x not in flat]
print("paper numbers match data/expected.json" if not missing else f"missing in paper.tex: {missing}")
sys.exit(1 if missing else 0)
PY
# The survey file: failures exactly for k = 2 (mod 4), all fit from n >= 4, c_k = xi_2(k) + 2.
python3 -I - <<'PY'
import re, sys
bad = []
for line in open("data/survey_N200_K24.txt"):
    k = int(re.search(r"k=\s*(\d+)", line).group(1))
    fails = "n>=2: FAILS" in line
    c4 = int(re.search(r"n>=4: consistent c=(\d+)", line).group(1))
    xi = (k & -k).bit_length() - 1
    if fails != (k % 4 == 2) or c4 != xi + 2:
        bad.append(k)
print("survey pattern as stated in the paper" if not bad else f"pattern differs at k = {bad}")
sys.exit(1 if bad else 0)
PY
echo "ci.sh: all checks passed"
