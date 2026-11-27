#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. The exact checker (standard library): no tree of order 2k in T'_{2k,k}, k = 3..8.
# 2. The independent checker: explicit graphs (k = 3..7), membership test (k = 3..6).
# 3. The search over all trees of order <= 20; output must agree with data/search20.json.
# 4. The figure is the one that checks/draw_figure.py draws.
# 5. Every number that the paper takes from data/expected.json occurs in paper/paper.tex.
# The Lean file is compiled by a separate CI job (axiom audit and lake comparator).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/verify.py 8
python3 -I checks/verifier_check.py 7 6
out="$(mktemp -d)"
python3 -I checks/search.py 20 "$out/search20.json"
python3 -I checks/compare_search.py "$out/search20.json"
python3 -I checks/draw_figure.py --check
python3 -I - <<'PY'
import json, re, sys
flat = re.sub(r"\s+", " ", open("paper/paper.tex").read())
e = json.load(open("data/expected.json"))
s = e["search"]
need = [
    f"There are {s['pairs']} pairs",
    f"For {s['pairs_with_minimiser_outside']} pairs, a minimiser is outside",
    f"$k = 3,\\dots,{s['nmax'] // 2}$",
    f"For the other {s['pairs_all_minimisers_inside']} pairs",
    f"These are the {s['pairs_n_at_least_2k_plus_1']} pairs with $n \\ge 2k+1$",
    f"({s['pairs_n_at_least_2k_plus_1_all_inside']} pairs $(n,k)$)",
    "all trees of order at most 20", "every tree of order $n \\le 20$",
    "$(13,4)$ and $(17,4)$ with 3 trees, $(18,6)$ with 4 trees, and $(19,4)$ with 2 trees",
]
assert s["ties"] == [[13, 4, 3], [17, 4, 3], [18, 6, 4], [19, 4, 2]]
assert s["pairs_n_at_least_2k_plus_1"] == s["pairs_n_at_least_2k_plus_1_all_inside"]
for n, rho in e["path_rho"].items():
    need.append(f"{int(n) // 2} & {n} & 0 & {rho} \\\\")
missing = [x for x in need if x not in flat]
print("paper numbers match data/expected.json" if not missing else f"missing in paper.tex: {missing}")
sys.exit(1 if missing else 0)
PY
echo "ci.sh: all checks passed"
