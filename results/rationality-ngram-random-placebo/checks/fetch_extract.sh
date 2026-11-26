#!/usr/bin/env bash
# Stream Google Books Ngram v3 (20200217) 1-gram shards through the extractor.
# Usage: fetch_extract.sh <outdir> <corpus: eng|eng-fiction> <shard indices...>
set -euo pipefail
OUT=$1; CORP=$2; shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
EXT=${EXTRACT_BIN:-$HERE/../work/extract}
B=https://storage.googleapis.com/books/ngrams/books/20200217/$CORP
mkdir -p "$OUT"
if [ "$CORP" = eng ]; then N=24; else N=1; fi
for i in "$@"; do
  f=$(printf '1-%05d-of-%05d.gz' "$i" "$N")
  o="$OUT/${CORP}_$i.tsv.gz"
  [ -s "$o.done" ] && continue
  curl -sSf --retry 5 "$B/$f" | gzip -dc | "$EXT" | gzip -1 > "$o.tmp"
  mv "$o.tmp" "$o"; date > "$o.done"; echo "done $CORP $i"
done
curl -sSf "$B/totalcounts-1" -o "$OUT/${CORP}_totalcounts-1"
