#!/usr/bin/env bash
# CI entry point. Downloads the public data (Retrosheet event files 2009-2025, MLB Stats API
# season hitting totals, Chadwick register, Lahman mirror), recomputes every number of the
# paper, and compares all of them with data/expected.json. Exits non-zero on any difference.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/rerun.py
