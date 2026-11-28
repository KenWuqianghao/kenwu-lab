#!/usr/bin/env bash
# CI entry point. Installs the pinned packages, downloads the ZTF light curves (IRSA) and the arXiv source of
# Zheng et al. 2016, reruns the pre-registered test and Addendum 1 (checks/rerun.py), and compares every value with
# data/expected.json (relative tolerance 1e-6). Exits non-zero on any difference. Then redraws the figure.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-2} MKL_NUM_THREADS=${MKL_NUM_THREADS:-2}
mkdir -p work
python3 -I checks/rerun.py > work/rerun.log 2>&1 || { tail -n 40 work/rerun.log; exit 1; }
grep -E '^(NOTE|MISMATCH|OK|FAIL)' work/rerun.log || true
grep -qx OK work/rerun.log
python3 -I checks/plot.py
echo "ci: all checks passed"
