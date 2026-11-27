#!/bin/bash
# Download all APPLAUSE DR4 exposure columns for the Vatican archive (archive_id 501).
out=${1:-work/raw}; mkdir -p "$out"
curl -sS -f -m 600 "https://www.plate-archive.org/tap/sync" --data-urlencode "REQUEST=doQuery" --data-urlencode "LANG=ADQL" --data-urlencode "FORMAT=csv" --data-urlencode "MAXREC=1000000" --data-urlencode "QUERY=SELECT * FROM applause_dr4.exposure WHERE archive_id=501" > "$out/exposure501.xml"
