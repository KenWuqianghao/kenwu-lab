#!/usr/bin/env bash
# CI entry point. Downloads ComCat (M>=7, 1900-2025) and the EOP C02 and C04 LOD series,
# recomputes every number of the paper, and compares 647 values with data/expected.json.
# Exits non-zero on any difference.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
python3 -I checks/rerun.py --work "$work"
