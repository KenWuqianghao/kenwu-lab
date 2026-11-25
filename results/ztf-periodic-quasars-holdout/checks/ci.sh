#!/usr/bin/env bash
# CI entry point. Downloads the public ZTF light curves, reruns the full forward test,
# and compares every number of the paper (data/expected.json) and every per-object value
# (data/results_table.csv) with the committed values. Monte Carlo values have a tolerance
# (checks/README.md, Platforms). Exits non-zero on any other difference.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
jobs="${JOBS:-$(getconf _NPROCESSORS_ONLN)}"
rm -rf work/results  # cached analyses must not stand in for a rerun; light curves stay
committed=$(mktemp)
cp data/results_table.csv "$committed"
python3 checks/rerun.py --jobs "$jobs"
python3 - "$committed" data/results_table.csv <<'PY'
import math, sys
import pandas as pd
a, b = pd.read_csv(sys.argv[1]), pd.read_csv(sys.argv[2])
assert list(a.columns) == list(b.columns) and list(a.id) == list(b.id), "table layout differs"
# Monte Carlo columns can differ slightly between platforms (see checks/README.md):
# p-values must agree within 0.03 and on the same side of 0.05; accepted-mock counts are not compared.
MC_P = {"p_drw", "p_spl", "p_drw_unc", "p_spl_unc"}
SKIP = {c for c in a.columns if c.endswith("_n_acc")}
bad = 0
for col in a.columns:
    if col in SKIP:
        continue
    for i, (x, y) in enumerate(zip(a[col], b[col])):
        if isinstance(x, float) and isinstance(y, float):
            if math.isnan(x) or math.isnan(y):
                ok = math.isnan(x) and math.isnan(y)
            elif col in MC_P:
                ok = abs(x - y) <= 0.03 and (x < 0.05) == (y < 0.05)
            else:
                ok = math.isclose(x, y, rel_tol=1e-3, abs_tol=1e-6)
        else:
            ok = x == y
        if not ok:
            bad += 1
            print(f"MISMATCH {a.id[i]} {col}: committed {x!r}, rerun {y!r}")
n = a.size - len(SKIP) * len(a)
print(f"results_table.csv: {n - bad}/{n} values reproduced")
sys.exit(1 if bad else 0)
PY
python3 checks/plot.py 2>/dev/null
echo "ci: all checks passed"
