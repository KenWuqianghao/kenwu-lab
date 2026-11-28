#!/usr/bin/env bash
# Download the raw public data into directory $1.
set -euo pipefail; d=$1; mkdir -p "$d"
V=https://vizier.cfa.harvard.edu/viz-bin/asu-tsv
curl -sS -m 180 -o "$d/ptolemy.tsv" "$V?-source=J/A%2BA/544/A31/ptolema&-out.max=unlimited&-out=P,C,cst,N,f_N,Elon,Elat,VP,q_VP,HIP,I,T,Vmag,Dl,Db,dist,Flag"
curl -sS -m 180 -o "$d/hip_v65.tsv" "$V?-source=I/239/hip_main&-out.max=unlimited&-out=HIP,Vmag,RAICRS,DEICRS,Plx,pmRA,pmDE&Vmag=<6.6"
q(){ curl -sS -m 180 -G "https://ssd.jpl.nasa.gov/api/horizons.api" --data-urlencode "format=text" --data-urlencode "COMMAND='7'" --data-urlencode "CENTER='500@399'" --data-urlencode "EPHEM_TYPE='OBSERVER'" --data-urlencode "START_TIME='JD $1'" --data-urlencode "STOP_TIME='JD $2'" --data-urlencode "STEP_SIZE='1 d'" --data-urlencode "QUANTITIES='9,23,31'" --data-urlencode "CSV_FORMAT='YES'" --data-urlencode "TIME_TYPE='TT'" --data-urlencode "CAL_FORMAT='BOTH'" -o "$3"; }
q 1667365.5 1675400.5 "$d/uranus_hipparchus.txt"
q 1764887.5 1774384.5 "$d/uranus_ptolemy.txt"
