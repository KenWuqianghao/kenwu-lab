#!/usr/bin/env bash
# CI entry point: rebuild every number of the paper from the raw Lichess files and compare
# with data/expected.json (1950 numbers, relative tolerance 1e-6). Exit code 1 on any difference.
# Needs: python3 (3.13), curl, zstd, grep, shasum; about 8 GB of free disk and 2 GB of RAM.
# Env: PYTHON (default python3); CHESSZIPF_WORK (default: a new temporary folder);
#      CHESSZIPF_RAW (a folder that already holds the 36 .pgn.zst files; they are SHA-256 checked
#      and kept); CHESSZIPF_WORKERS (default 4).
set -euo pipefail
cd "$(dirname "$0")/.."
"${PYTHON:-python3}" -m venv .venv
.venv/bin/python -m pip install -q -r checks/requirements.txt
.venv/bin/python -I checks/test_counting.py
WORK=${CHESSZIPF_WORK:-$(mktemp -d)}
mkdir -p "$WORK"
if [ -n "${CHESSZIPF_RAW:-}" ]; then
  ln -s "$CHESSZIPF_RAW" "$WORK/raw"
else
  export CHESSZIPF_DELETE_RAW=1
fi
export CHESSZIPF_WORKERS=${CHESSZIPF_WORKERS:-4}
df -h "$WORK" | tail -1
.venv/bin/python -I checks/rerun.py "$WORK"
