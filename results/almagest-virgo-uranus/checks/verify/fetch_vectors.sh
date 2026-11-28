#!/usr/bin/env bash
# Verifier: download Horizons geocentric ICRF vectors (target 7 Uranus barycenter, light-time corrected; target 10 Sun) into $1.
set -euo pipefail; d=$1; mkdir -p "$d"
q(){ curl -sS -m 120 -G "https://ssd.jpl.nasa.gov/api/horizons.api" --data-urlencode "format=text" --data-urlencode "COMMAND='$1'" --data-urlencode "CENTER='500@399'" --data-urlencode "EPHEM_TYPE='VECTORS'" --data-urlencode "START_TIME='JD 1667365.5'" --data-urlencode "STOP_TIME='JD 1675400.5'" --data-urlencode "STEP_SIZE='1 d'" --data-urlencode "REF_PLANE='FRAME'" --data-urlencode "REF_SYSTEM='ICRF'" --data-urlencode "VEC_TABLE='1'" --data-urlencode "VEC_CORR='$2'" --data-urlencode "CSV_FORMAT='YES'" --data-urlencode "TIME_TYPE='TT'" -o "$3"; }
q 7 LT "$d/ura_vec.txt"; q 10 NONE "$d/sun_vec.txt"
