#!/bin/bash
# Download APPLAUSE DR4 exposure and plate metadata (anonymous TAP, CSV).
out=${1:-work/raw}; mkdir -p "$out"
tap(){ curl -sS -f -m 600 "https://www.plate-archive.org/tap/sync" --data-urlencode "REQUEST=doQuery" --data-urlencode "LANG=ADQL" --data-urlencode "FORMAT=csv" --data-urlencode "MAXREC=1000000" --data-urlencode "QUERY=$1"; }
tap "SELECT plate_id, archive_id, site_name, site_longitude, site_latitude FROM applause_dr4.plate" > "$out/plate.xml"
tap "SELECT exposure_id, plate_id, archive_id, jd_mid, ut_mid, exptime, time_orig_start, time_orig_end, flag_time FROM applause_dr4.exposure" > "$out/exposure.xml"
