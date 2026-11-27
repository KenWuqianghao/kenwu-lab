#!/usr/bin/env bash
# Download one Lichess monthly file into DEST (if missing) and check its SHA-256.
# Usage: download.sh DEST FILE        (FILE as listed in data/sha256sums_2013_2015.txt)
set -u
DEST=$1; f=$2; HERE=$(cd "$(dirname "$0")/.." && pwd); SUMS=$HERE/data/sha256sums_2013_2015.txt
mkdir -p "$DEST"
want=$(grep " $f\$" "$SUMS" | cut -d' ' -f1)
if [ -f "$DEST/$f" ] && [ "$(shasum -a 256 "$DEST/$f" | cut -d' ' -f1)" = "$want" ]; then echo "have $f (SHA-256 ok)"; exit 0; fi
curl -sf --retry 5 -o "$DEST/$f.part" "https://database.lichess.org/standard/$f" && mv "$DEST/$f.part" "$DEST/$f"
got=$(shasum -a 256 "$DEST/$f" | cut -d' ' -f1)
if [ "$got" = "$want" ]; then echo "ok $f (downloaded, SHA-256 ok)"; else echo "SHA MISMATCH $f"; exit 1; fi
