#!/usr/bin/env bash
# Usage: fetch_month.sh YYYY-MM OUTDIR
# Streams the Lichess monthly file (not stored), keeps only header rows as zstd TSV,
# and writes the sha256 of the downloaded .pgn.zst to OUTDIR/YYYY-MM.sha256.
set -euo pipefail
M=$1; OUT=$2; mkdir -p "$OUT"
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-python3}
[ -s "$OUT/$M.tsv.zst" ] && [ -s "$OUT/$M.sha256" ] && exit 0
curl -sSf --retry 5 "https://database.lichess.org/standard/lichess_db_standard_rated_$M.pgn.zst" \
 | tee >(shasum -a 256 | cut -d' ' -f1 > "$OUT/$M.sha256.part") \
 | zstd -dc \
 | LC_ALL=C grep -E '^\[(Event|Site|White|Black|Result|UTCDate|UTCTime|WhiteElo|BlackElo|WhiteRatingDiff|BlackRatingDiff|TimeControl|Termination) ' \
 | "$PY" -I "$HERE/extract_headers.py" | zstd -q -f -3 -o "$OUT/$M.tsv.zst.part"
sleep 1
mv "$OUT/$M.sha256.part" "$OUT/$M.sha256"
mv "$OUT/$M.tsv.zst.part" "$OUT/$M.tsv.zst"
