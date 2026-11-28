#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. Fact (i) from the definition (all 2^17 subsequences); the 32 Lean part lemmas match a fresh run.
# 2. The data lists (RC(17), the 96 best Odd Sum permutations, n <= 14) are re-evaluated.
# 3. The figure equals a fresh drawing.
# 4. Both search programs agree with brute force for small n.
# 5. Fact (ii): both programs search all Odd Sum permutations of [17] (checks/run_n17.py).
# 6. RC(15) by both programs (checks/run_rc.py 15).
# 7. Every number that the paper takes from data/expected.json occurs in paper/paper.tex.
# The Lean file is compiled by a separate CI job (axiom audit and lake comparator).
# Needs a C compiler (cc, gcc, clang or leanc; or set CC). Run time on 4 cores: see checks/README.md.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
CC="${CC:-$(command -v cc || command -v gcc || command -v clang || command -v leanc)}"
export CC
build="$(mktemp -d)"
python3 -I checks/t_definition.py | tee "$build/t.txt"
grep -qx 't = 798783' "$build/t.txt"
python3 -I checks/gen_lean_split.py --check
python3 -I checks/check_lists.py
python3 -I checks/draw_witness.py --check
"$CC" -O2 -o "$build/oddsum_bb" checks/oddsum_bb.c
"$CC" -O2 -o "$build/v2_bb" checks/independent/v2_bb.c
python3 -I checks/validate_bb.py "$build/oddsum_bb"
python3 -I checks/independent/v2_validate.py "$build/v2_bb"
python3 -I checks/run_n17.py --out "$build/n17"
python3 -I checks/run_rc.py 15 174954 --out "$build/n15"
python3 -I - <<'PY'
import json, re, sys
flat = re.sub(r"\s+", " ", re.sub(r"\\,|\{,\}|~", " ", open("paper/paper.tex").read()))
e = json.load(open("data/expected.json"))
need = [", ".join(map(str, e["witness"])), str(e["fact_i"]["t"]), str(e["fact_ii"]["max_t_odd_sum"]),
        str(e["rc17"]["tmax"]), str(e["literature_n17"]["ahmed_snevily_lower_bound"]),
        f"$|\\mathrm{{RC}}(17)| = {e['rc17']['size']}$", f"{e['fact_ii']['found_pi1_at_most_9']} permutations",
        f"{e['fact_ii']['with_complements']} Odd Sum permutations"]
for n in map(str, range(3, 15)):
    need.append(f"{n} & {e['tmax_3_14'][n]} & {e['rc_counts_3_14'][n]} \\\\")
need += [f"{n} & {d['tmax']} & {d['size']} \\\\" for n, d in e["larger_n"].items()]
missing = [x for x in need if x not in flat]
print("paper numbers match data/expected.json" if not missing else f"missing in paper.tex: {missing}")
sys.exit(1 if missing else 0)
PY
echo "ci.sh: all checks passed"
