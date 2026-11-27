#!/usr/bin/env bash
# CI entry point. Downloads the APPLAUSE DR4 metadata (about 90 MB, anonymous TAP),
# reruns the full analysis, and compares every number of the paper (data/expected.json)
# and the per-exposure Vatican table (data/vatican_corrected.csv) with the committed values.
# Exits non-zero on any difference.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/rerun.py
echo "ci: all checks passed"
