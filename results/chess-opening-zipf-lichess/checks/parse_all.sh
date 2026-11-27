#!/usr/bin/env bash
# Fetch (if needed) and parse the 36 months. Usage: parse_all.sh RAW OUT [WORKER NWORKERS]
# Worker W of NW handles months W, W+NW, ... For each month it calls download.sh, which
# downloads the file if it is missing and always checks its SHA-256, then parses it.
# With CHESSZIPF_DELETE_RAW=1 it deletes each raw file after the parse (low-disk mode for CI).
set -eu
RAW=$1; OUT=$2; W=${3:-0}; NW=${4:-1}; HERE=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$OUT"; i=0
for f in $(awk '{print $2}' "$HERE/data/sha256sums_2013_2015.txt"); do
  m=${f#lichess_db_standard_rated_}; m=${m%.pgn.zst}
  if [ $((i % NW)) -eq "$W" ]; then
    "$HERE/checks/download.sh" "$RAW" "$f"
    "$HERE/.venv/bin/python" -I "$HERE/checks/parse_month.py" "$RAW/$f" "$OUT/$m.tmp.npz"
    mv "$OUT/$m.tmp.npz" "$OUT/$m.npz"
    if [ "${CHESSZIPF_DELETE_RAW:-0}" = 1 ]; then rm -f "$RAW/$f"; fi
    echo "parsed $m"
  fi
  i=$((i+1))
done
