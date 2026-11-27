#!/usr/bin/env bash
# CI entry point. Downloads the JPL Horizons predictions, the 18 DASCH cutouts, the 15 HDAP cutout requests and the
# ATLAS reference stars again, reruns rounds 1-3, the astrometry, the shapes and the Hektor motion check, and compares
# 295 values with data/expected.json (checks/rerun.py). Exits non-zero when a value differs.
# It then reports whether the new cutouts are byte-identical to the ones used for the paper (data/cutouts.sha256).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
work=$(mktemp -d)
python3 -I checks/rerun.py --data "$work"
(cd "$work" && sha256sum cutouts/*.fits.gz hdap/cutouts/*.fits) > "$work/sha256.txt"
same=$(comm -12 <(sort data/cutouts.sha256) <(sort "$work/sha256.txt") | wc -l)
echo "cutouts byte-identical to the paper's: $same of $(wc -l < data/cutouts.sha256)"
echo "ci: all checks passed"
