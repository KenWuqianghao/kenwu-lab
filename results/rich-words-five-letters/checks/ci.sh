#!/usr/bin/env bash
# CI entry point. Run from the result folder: bash checks/ci.sh
# Reruns every check and compares each output with the saved output in checks/expected/.
# Lines that give a run time are ignored. Exits non-zero on any difference or failure.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
mkdir -p checks/out
strip() { grep -v -E '^(time |real |user |sys )' "$1"; }
compare() {  # compare <name>
  diff -u <(strip "checks/expected/$1.txt") <(strip "checks/out/$1.txt")
  echo "ok: checks/out/$1.txt matches checks/expected/$1.txt"
}

for c in A B C; do
  python3 checks/verify.py "$c" > "checks/out/verify_$c.txt"
  tail -1 "checks/out/verify_$c.txt"
  grep -qx 'RESULT: ALL CHECKS PASSED' "checks/out/verify_$c.txt"
  compare "verify_$c"
done

python3 checks/crosscheck.py A > checks/out/crosscheck_A.txt
grep -qx 'RESULT: CROSS-CHECK PASSED' checks/out/crosscheck_A.txt
compare crosscheck_A

python3 checks/independent_check.py A > checks/out/independent_check_A.txt
grep -qx 'RESULT: ALL OWN CHECKS PASSED' checks/out/independent_check_A.txt
compare independent_check_A

cc -O2 -o checks/out/prefix_check checks/prefix_check.c
checks/out/prefix_check 01 011 0 02 0232 023432 02343223432 0234344343343443432 \
  023434434334344343234344343343443432 3000000 > checks/out/prefix_check_A.txt
grep -q 'rich prefix: YES' checks/out/prefix_check_A.txt
compare prefix_check_A

echo "ci: all checks passed"
