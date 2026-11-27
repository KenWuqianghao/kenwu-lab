#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. checks/prefix.py: finite checks of PSQ and h(PSQ), two constructions of PSQ, controls.
# 2. checks/controls.py: decide.py must find a real square in each of 32 changed DFAOs.
# 3. checks/decide.py: the decision procedure proves that the whole word PSQ is squarefree.
# 4. The formula in checks/walnut/hb.txt encodes h; the numbers occur in paper/paper.tex.
# Each result must equal data/expected.json. The Walnut rerun (checks/walnut/run_walnut.sh)
# is separate, because it needs a JDK and builds Walnut from source.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
mkdir -p "${TMPDIR:-/tmp}"
out=$(mktemp -d)
python3 -I checks/prefix.py data/PSQ.txt | tee "$out/prefix.out"
python3 -I checks/controls.py data/PSQ.txt | tee "$out/controls.out"
python3 -I checks/decide.py data/PSQ.txt square | tee "$out/decide.out"
python3 -I - "$out" <<'PY'
import json, re, sys
d = sys.argv[1]
exp = json.load(open("data/expected.json"))
bad = []
pre = json.loads(open(f"{d}/prefix.out").read().strip().splitlines()[-1])
for k, v in exp["prefix"].items():
    if pre.get(k) != v:
        bad.append(f"prefix.py {k}: {pre.get(k)!r} != {v!r}")
ctl = json.loads(open(f"{d}/controls.out").read().strip().splitlines()[-1])
for k in ("controls_run", "controls_detected", "controls_period_ge_2", "controls_no_square_in_prefix"):
    if ctl[k] != exp[k]:
        bad.append(f"controls.py {k}: {ctl[k]} != {exp[k]}")
dec = open(f"{d}/decide.out").read()
m = re.search(r"RESULT square : (.*)\. reachable top states: (\d+)", dec)
if not m or m.group(1) != exp["decide_square"] or int(m.group(2)) != exp["decide_top_states"]:
    bad.append(f"decide.py: {m.groups() if m else dec[-200:]}")
if f"D_M states: {exp['decide_D_M_states']}" not in dec:
    bad.append("decide.py: D_M states differ")
H = ["011010011001001101001", "100101100100110010110", "100101100110110010110", "011010011011001101001"]
hb = open("checks/walnut/hb.txt").read()
for a in range(4):
    m = re.search(r"PSQ\[q\]=@%d & \(([^)]*)\)" % a, hb)
    rs = sorted(int(x) for x in re.findall(r"r=(\d+)", m.group(1))) if m else None
    if rs != [i for i, c in enumerate(H[a]) if c == "1"]:
        bad.append(f"checks/walnut/hb.txt: positions for letter {a} differ from h({a})")
tex = re.sub(r"\\,|\{,\}|~|\\ ", "", open("paper/paper.tex").read())
need = [exp["prefix"]["psq_prefix60"], "442377", "151", "50000", "200000", "100000",
        "200", "32", "33", "11", "1518"] + H
need += [str(x) for x in exp["prefix"]["h_first_73_factor"]]
miss = [n for n in need if n not in tex]
if miss:
    bad.append(f"missing in paper.tex: {miss}")
print("\n".join(bad) if bad else "all numbers equal data/expected.json and occur in paper.tex")
sys.exit(1 if bad else 0)
PY
echo "ci.sh: all checks passed"
