#!/usr/bin/env bash
# CI entry point. Downloads the Ptolemy catalogue (VizieR J/A+A/544/A31), the Hipparcos stars with V < 6.6
# (VizieR I/239) and the Uranus ephemeris (JPL Horizons) again, reruns the registered test
# (checks/analysis.py), the exploratory numbers (checks/exploratory.py) and the post hoc limits
# (checks/posthoc.py), and compares every value with data/expected.json (checks/rerun.py).
# Exits non-zero when a value differs.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
python3 -I checks/rerun.py
echo "ci: all checks passed"
