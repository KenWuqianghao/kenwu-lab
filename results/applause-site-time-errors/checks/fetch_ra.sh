#!/bin/bash
out=${1:-work/raw}
curl -sS -f -m 600 "https://www.plate-archive.org/tap/sync" --data-urlencode "REQUEST=doQuery" --data-urlencode "LANG=ADQL" --data-urlencode "FORMAT=csv" --data-urlencode "MAXREC=1000000" --data-urlencode "QUERY=SELECT exposure_id, archive_id, ra_orig, ra_icrs, object_name FROM applause_dr4.exposure WHERE archive_id IN (101, 501)" > "$out/exposure_ra.xml"
