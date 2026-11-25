#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# 1. Check that every number in paper/paper.tex equals its source value (seconds, offline).
# 2. Rerun the primary computation (Lichess blitz 2013-2015) from the raw public data and
#    compare every number with data/expected.json (about 30-50 min; streams about 8.3 GB,
#    needs about 8 GB of free disk and under 4 GB of RAM).
# Set PBQ_FULL=1 to also rerun the 2016 addendum (12 more files, about 14 GB more download).
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON=${PYTHON:-python3}
W=$(mktemp -d "${RUNNER_TEMP:-/tmp}/pbq.XXXXXX")
trap 'rm -rf "$W"' EXIT
command -v zstd >/dev/null || { echo "zstd is required"; exit 1; }
command -v shasum >/dev/null || { echo "shasum is required"; exit 1; }
"$PYTHON" -m venv "$W/venv"
"$W/venv/bin/python" -m pip install -q -r checks/requirements.txt
"$W/venv/bin/python" -I checks/paper_numbers.py
if [ "${PBQ_FULL:-0}" = 1 ]; then
  "$W/venv/bin/python" -I checks/rerun.py --work "$W/work" --work2016 "$W/work2016"
else
  "$W/venv/bin/python" -I checks/rerun.py --skip-2016 --work "$W/work"
fi
