#!/usr/bin/env bash
# Rerun the time test from the committed inputs and compare with the committed output.
# Then, if this version is archived, compare paper/paper.pdf with the PDF in its Zenodo record.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r checks/requirements.txt
expected=$(mktemp)
cp data/results/time_test.txt "$expected"
(cd data/timetest && python3 analyze.py > /dev/null)
diff -u "$expected" data/results/time_test.txt
echo "time test: output matches data/results/time_test.txt"
python3 - <<'PY'
import hashlib, json, urllib.request
meta = json.load(open("result.json"))
if meta.get("doi_version") != meta["version"]:
    print(f"paper.pdf: v{meta['version']} is not archived yet; the Zenodo comparison runs after the release")
    raise SystemExit(0)
url = f"https://zenodo.org/api/records/{meta['zenodo_id']}"
rec = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "kenwu-lab-ci/1.0"}), timeout=60))
remote = {f["checksum"].removeprefix("md5:") for f in rec["files"] if f["key"].endswith(".pdf")}
local = hashlib.md5(open("paper/paper.pdf", "rb").read()).hexdigest()
assert local in remote, f"paper/paper.pdf md5 {local} is not in the Zenodo record {remote}"
print(f"paper.pdf: md5 {local} matches Zenodo record {meta['zenodo_id']}")
PY
