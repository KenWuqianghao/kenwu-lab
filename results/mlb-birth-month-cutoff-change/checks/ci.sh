#!/usr/bin/env bash
# CI entry point. Downloads the public data (MLB Stats API season lists 1985-2026 and the
# CDC monthly birth counts), recomputes every number of the paper, and compares all of
# them with data/expected.json. Exits non-zero on any difference.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/rerun.py
