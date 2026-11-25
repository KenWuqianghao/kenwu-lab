#!/usr/bin/env bash
# CI entry point. Downloads the public ZTF light curves, reruns the full forward test,
# and compares every number of the paper (data/expected.json) and every per-object value
# (data/results_table.csv) with the committed values. Exits non-zero on any difference.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
jobs="${JOBS:-$(getconf _NPROCESSORS_ONLN)}"
committed=$(mktemp)
cp data/results_table.csv "$committed"
python3 checks/rerun.py --jobs "$jobs"
python3 - "$committed" data/results_table.csv <<'PY'
import math, sys
import pandas as pd
a, b = pd.read_csv(sys.argv[1]), pd.read_csv(sys.argv[2])
assert list(a.columns) == list(b.columns) and list(a.id) == list(b.id), "table layout differs"
bad = 0
for col in a.columns:
    for i, (x, y) in enumerate(zip(a[col], b[col])):
        if isinstance(x, float) and isinstance(y, float):
            ok = (math.isnan(x) and math.isnan(y)) or math.isclose(x, y, rel_tol=1e-3, abs_tol=1e-6)
        else:
            ok = x == y
        if not ok:
            bad += 1
            print(f"MISMATCH {a.id[i]} {col}: committed {x!r}, rerun {y!r}")
print(f"results_table.csv: {a.size - bad}/{a.size} values reproduced")
sys.exit(1 if bad else 0)
PY
python3 checks/plot.py 2>/dev/null
echo "ci: all checks passed"
