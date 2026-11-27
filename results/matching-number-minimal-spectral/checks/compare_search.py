"""Compare a fresh run of checks/search.py with data/search20.json and data/expected.json.

Usage: python3 -I checks/compare_search.py NEW.json

The search uses floating point (numpy eigvalsh, tie tolerance 1e-9). So the spectral
radii are compared with a tolerance of 1e-9, and every other field must be equal.
The script also checks the facts that the paper states about the search.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location("search", HERE / "search.py")
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)

new = json.load(open(sys.argv[1]))
old = json.load(open(ROOT / "data" / "search20.json"))
exp = json.load(open(ROOT / "data" / "expected.json"))
errors = []


def close(a, b):
    if a is None or b is None:
        return a is b
    return abs(a - b) <= 1e-9


if len(new) != len(old):
    errors.append(f"number of rows {len(new)} != {len(old)}")
for a, b in zip(new, old):
    for key in a:
        same = close(a[key], b[key]) if key.startswith("rho") else a[key] == b[key]
        if not same:
            errors.append(f"(n,k)=({a['n']},{a['k']}) field {key}: {a[key]} != {b[key]}")

rows = new
nmax = exp["search"]["nmax"]
fail = [(r["n"], r["k"]) for r in rows if r["n_min_in_Tp"] != r["n_min"]]
upper = [r for r in rows if r["n"] >= 2 * r["k"] + 1]
ties = sorted([r["n"], r["k"], r["n_min"]] for r in rows if r["n_min"] > 1)
facts = {
    "pairs": len(rows),
    "pairs_with_minimiser_outside": len(fail),
    "pairs_all_minimisers_inside": len(rows) - len(fail),
    "pairs_n_at_least_2k_plus_1": len(upper),
    "pairs_n_at_least_2k_plus_1_all_inside": sum(r["n_min_in_Tp"] == r["n_min"] for r in upper),
    "failing_pairs": [list(p) for p in fail],
    "ties": ties,
}
for key, value in facts.items():
    if exp["search"][key] != value:
        errors.append(f"search fact {key}: {value} != expected {exp['search'][key]}")
if max(r["n"] for r in rows) != nmax:
    errors.append("search range differs from expected nmax")

# Each failing pair: T'_{2k,k} is empty, the unique minimiser is the path P_{2k},
# and its spectral radius is 2 cos(pi/(2k+1)).
for r in rows:
    if (r["n"], r["k"]) not in fail:
        continue
    n = r["n"]
    path = [[u for u in (v - 1, v + 1) if 0 <= u < n] for v in range(n)]
    ok = (r["size_Tp"] == 0 and r["n_min"] == 1 and r["outside"] == [search.canon(path)]
          and close(r["rho_min"], 2 * math.cos(math.pi / (n + 1))))
    want = exp["path_rho"].get(str(n))
    if not ok or f"{r['rho_min']:.6f}" != want:
        errors.append(f"failing pair (n,k)=({n},{r['k']}): not the expected path minimiser")

print("\n".join(errors) if errors else
      f"search output matches data/search20.json and data/expected.json ({len(rows)} pairs)")
sys.exit(1 if errors else 0)
