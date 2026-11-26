# Checks

`checks/rerun.py` reproduces every number of the paper from the raw public data. `checks/ci.sh` runs it in a temporary directory after it installs `checks/requirements.txt` (numpy 2.5.5, pandas 3.1.1, matplotlib 3.11.2). Both exit non-zero if a number differs.

## Steps

1. `extract.c` (compiled with `cc -O2`) reads Ngram v3 1-gram lines and keeps alphabetic forms, their yearly counts for 1850-2019, and the totals of their part-of-speech tagged forms. It drops an untagged form with a total below 2,000 and a tagged form below 1,000 (a deviation from the protocol; see the paper, Table 2).
2. `fetch_extract.sh` streams each shard with `curl | gzip -dc | extract`. The raw files are not stored.
3. The script clones `jbollen/rise_and_fall_of_rationality_in_language` (about 355 MB) for the known-answer check.
4. `build.py` merges the extracts into `table.npz` (40,079 words, case-insensitive counts in `eng` and `eng-fiction`, part-of-speech totals, total token counts).
5. `analysis.py` is the pre-registered analysis (protocol: `PROTOCOL.md`, committed as `1bd3e8c` before any statistic was computed). It writes `results.json`, which is compared with `data/expected.json` (332 values). With a fourth argument (a directory) it also draws `placebo.png`.
6. `posthoc.py` runs `analysis.py` unchanged for K = 20, 80 and 40 and computes the post-hoc numbers: K sensitivity, the detectable size of an extra hinge, the skew gap and its linear adjustment, the fiction share of tokens and the nearest FPS candidates. It writes `posthoc.json`, which is compared with `data/expected_posthoc.json` (87 values). With a third argument (a file name) it draws `placebo_bands.png`.

`wordsets.py` holds the authors' word lists.

Floats are compared with a relative tolerance of 1e-9. All random draws use `numpy.random.default_rng` with fixed seeds (20261126 FP, 20261127 FPS, 20261128 label shuffle).

## Figures

```sh
.venv/bin/python -I checks/analysis.py work/table.npz /tmp/r.json work/authors_repo paper/
.venv/bin/python -I checks/posthoc.py work/table.npz /tmp/p.json paper/placebo_bands.png
```

## What the checks do not cover

- The comparison with the Google Ngram Viewer (six words, eng ratio 0.9998 to 1.0000) and the independent implementation (FPS p = 0.128 to 0.130) were done in the verification stage. They are not part of the rerun.
- The Ngram data can change on the server. The rerun found no change on 2026-11-26.

## Recorded runs (2026-11-26)

- `ci_clean_copy.log`: `bash checks/ci.sh` in a clean copy of this folder with a new Python 3.13 venv on an M1 Pro laptop. Full download, 8 min 35 s, exit 0, `compared 419 values; mismatches: 0`.
- `readme_check_reuse.log`: the "Check it" commands of `README.md` in another clean copy with a new venv, with the extracts copied in and `--reuse`. Exit 0, `compared 419 values; mismatches: 0`, about 75 to 110 s.
