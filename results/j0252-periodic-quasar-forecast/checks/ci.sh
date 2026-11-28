#!/usr/bin/env bash
# CI entry point. Installs the pinned packages, downloads the public ZTF light curves from IRSA,
# reruns the pre-registered test and Addendum 1 (checks/rerun.py), and compares every value with
# data/expected.json (relative tolerance 1e-6). Exits non-zero on any difference. Then redraws both figures.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p work
python3 -I checks/rerun.py > work/rerun.log 2>&1 || { tail -n 40 work/rerun.log; exit 1; }
grep -E '^(MISMATCH|OK|FAIL)' work/rerun.log
grep -qx OK work/rerun.log
python3 -I checks/fig_addendum.py
python3 -I checks/plot_forecast.py
echo "ci: all checks passed"
