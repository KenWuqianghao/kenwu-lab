#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. Quick exact checks of the certificate, with positive and negative controls.
# 2. The figure files equal a fresh drawing from the certificate.
# 3. The length-35 search for all 7 multiplier groups; counts must equal data/expected.json.
# 4. Every number in data/expected.json occurs in paper/paper.tex.
# The Lean file is compiled by a separate CI job (lake env lean lean/TernaryLP35.lean).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/check.py
python3 -I checks/draw_pair.py --check
python3 -I checks/search.py
python3 -I - <<'PY'
import json, re, sys
tex = open("paper/paper.tex").read()
flat = re.sub(r"\\,|\{,\}|~", "", tex)
exp = json.load(open("data/expected.json"))
need = [exp["certificate"]["A"], exp["certificate"]["B"], "(22, 24, 24)", "(11, 12, 12)"]
for g, v in exp["search_35"].items():
    need += [str(v["sequences"]), f"\\langle {g}\\rangle"]
need.append("2400")
missing = [n for n in need if n not in flat.replace("(22,24,24)", "(22, 24, 24)").replace("(11,12,12)", "(11, 12, 12)")]
print("paper numbers match data/expected.json" if not missing else f"missing in paper.tex: {missing}")
sys.exit(1 if missing else 0)
PY
echo "ci.sh: all checks passed"
