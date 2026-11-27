#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. instance.py rebuilds checks/instance.json (must be byte-identical).
# 2. check_certificate.py: the proof of the main theorem, step by step, exact.
# 3. vcheck.py: second checker (exact simplex and exhaustive search), both instances.
# 4. check_small.py: the second counterexample with the first checker's search.
# 5. check_ip.py: an assignment with makespan 4 for the main instance.
# 6. control.py 1 and 2: the pruned search against a search with no pruning.
# Each output must equal the file in checks/expected/. Then the numbers that the paper
# states must occur in paper/paper.tex.
# The Lean file is compiled by a separate CI job (axiom audit and lake comparator).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
out="$(mktemp -d)"
python3 -I checks/instance.py | cmp - checks/instance.json
echo "instance: instance.py output equals checks/instance.json"
python3 -I checks/check_certificate.py checks/instance.json > "$out/certificate.txt"
python3 -I checks/vcheck.py main checks/instance.json > "$out/vcheck_main.txt"
python3 -I checks/vcheck.py file checks/instance_small.json > "$out/vcheck_small.txt"
python3 -I checks/check_small.py > "$out/small.txt"
python3 -I checks/check_ip.py checks/instance.json > "$out/ip.txt"
python3 -I checks/control.py 1 > "$out/control1.txt"
python3 -I checks/control.py 2 > "$out/control2.txt"
for n in certificate vcheck_main vcheck_small small ip control1 control2; do
  diff "$out/$n.txt" "checks/expected/$n.txt"
  echo "$n: output equals checks/expected/$n.txt"
done
python3 -I - "$out" <<'PY'
import json, re, sys
out = sys.argv[1]
r = lambda n: open(f"{out}/{n}.txt").read()
tex = re.sub(r"\s+", " ", open("paper/paper.tex").read())
fail = []
# The checks must report the counterexamples.
for name, pat in [("certificate", r"no half-integral point in CLP\(P,LP\(P\)\): verified"),
                  ("vcheck_main", r"RESULT: COUNTEREXAMPLE CONFIRMED"),
                  ("vcheck_small", r"RESULT: COUNTEREXAMPLE CONFIRMED"),
                  ("small", r"no half-integral point \(exhaustive search\): verified"),
                  ("vcheck_main", r"control T=4: True")]:
    if not re.search(pat, r(name)):
        fail.append(f"{name} lacks: {pat}")
d = json.load(open("checks/instance.json"))
s = json.load(open("checks/instance_small.json"))
cert, vm, vs, ip = r("certificate"), r("vcheck_main"), r("vcheck_small"), r("ip")
full = re.search(r"all (\d+) full configurations", cert).group(1)
cfg_main = set(re.search(r"configurations per machine at T: \[(.*)\]", vm).group(1).split(", "))
nodes_main = re.findall(r"search nodes: (\d+)", vm)[0]
cfg_small = re.search(r"configurations per machine at T: \[(.*)\]", vs).group(1).split(", ")
nodes_small = re.search(r"search nodes: (\d+)", vs).group(1)
c1 = re.search(r"with half-integral point: (\d+)", r("control1")).group(1)
c2 = re.search(r"with half-integral point: (\d+)", r("control2")).group(1)
mk = re.search(r"makespan (\d+)", ip).group(1)
vals = sorted({v for _, _, v in s["x"]})
assert len(cfg_main) == 1
need = [
    f"has {d['m']} machines, {len(d['p'])} jobs and $\\LP(P^\\ast)={d['T']}$",
    f"The total processing time is $12\\cdot 1+8\\cdot 3={sum(d['p'])}$",
    f"for all {full} configurations of load 3 (3 on each of the 12 machines)",
    f"({cfg_main.pop()} configurations per machine for $P^\\ast$ at $T=3$)",
    f"it visits {nodes_main} nodes and finds no point",
    f"it visits {nodes_small} nodes and finds no point",
    f"All answers agree ({c1} and {c2} of the instances",
    f"So $\\IP(P^\\ast)={mk}$",
    f"It has {s['m']} machines (indexed from 0), {len(s['p'])} jobs and $\\LP(P)={s['T']}$",
    "(p_0,\\dots,p_{13})=(" + ",".join(map(str, s["p"])) + ")",
    f"The total processing time is ${sum(s['p'])}>5\\cdot 13={5 * 13}$",
    f"with {len(s['x'])} nonzero entries",
    "The machines have " + ", ".join(cfg_small[:-1]) + " and " + cfg_small[-1] + " configurations",
]
if vals != ["1/3", "2/3"]:
    fail.append(f"values of the small point: {vals}")
fail += [f"missing in paper.tex: {x}" for x in need if x not in tex]
print("paper numbers match the check output" if not fail else "\n".join(fail))
sys.exit(1 if fail else 0)
PY
echo "ci.sh: all checks passed"
