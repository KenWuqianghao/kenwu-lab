#!/usr/bin/env bash
# CI entry point. Streams the Google Books v3 1-grams (about 7.3 GB, not stored),
# rebuilds the word table, reruns the pre-registered analysis and the post-hoc numbers,
# and exits non-zero if any of the numbers differs from data/expected*.json.
# Needs: python3 (3.13), cc, curl, gzip, git, network. About 10 to 20 min.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
python3 -I checks/rerun.py --workdir "$work"
