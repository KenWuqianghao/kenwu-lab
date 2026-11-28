#!/usr/bin/env bash
# CI entry point. Installs the pinned packages, downloads the DASCH cutouts, ATLAS stars, control plates, Horizons
# positions and SkyBoT lists again, reruns the registered test, the controls and the post hoc measurements, and
# compares the values with data/expected.json (checks/rerun.py). Exits non-zero when a value differs.
# It then reports whether the new cutouts are byte-identical to the ones used for the paper.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
work=$(mktemp -d)
python3 -I checks/rerun.py --data "$work"
(cd "$work" && sha256sum cutouts/*.fits.gz) > "$work/sha256.txt"
(cd "$work" && sha256sum controls/*.fits.gz) > "$work/sha256_ctrl.txt"
same=$(comm -12 <(sort data/cutouts.sha256) <(sort "$work/sha256.txt") | wc -l)
same_c=$(comm -12 <(sort data/controls.sha256) <(sort "$work/sha256_ctrl.txt") | wc -l)
echo "cutouts byte-identical to the paper's: $same of $(wc -l < data/cutouts.sha256); control cutouts: $same_c of $(wc -l < data/controls.sha256)"
echo "ci: all checks passed"
