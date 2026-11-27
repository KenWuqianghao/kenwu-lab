# Checks

All commands run from the result folder. The scripts need Python 3.13, `curl`, `zstd`, `grep` and `shasum`.

| Script | What it does |
|---|---|
| `ci.sh` | CI entry point. Makes `.venv`, installs `requirements.txt`, runs `test_counting.py`, then `rerun.py` on a new work folder. Exit code 0 only if all 1950 numbers match. |
| `rerun.py WORKDIR` | Full pipeline: download (if missing) and SHA-256 check, parse, build, analysis, exploratory analysis, robustness, figure, comparison with `data/expected.json` (relative tolerance 1e-6). It stops if `WORKDIR` already holds `parsed/`, `build/` or `out/`, so each run starts from the raw files. `WORKDIR/raw` can be a link to downloaded files. |
| `rerun.py --compare-only R E B` | Compares the three output files `results.json`, `explore.json`, `robustness.json` with `data/expected.json`. |
| `download.sh DEST FILE` | Downloads one month if it is missing and checks its SHA-256 against `data/sha256sums_2013_2015.txt`. |
| `parse_all.sh RAW OUT [W NW]` | Worker `W` of `NW`: download.sh, then `parse_month.py`, for its months. With `CHESSZIPF_DELETE_RAW=1` it deletes each raw file after the parse. |
| `parse_month.py` | One month of PGN to 40-ply token keys, game length, speed and mean rating. |
| `build.py` | Merges the months, sorts the keys and computes the longest common prefix of neighbours. |
| `zipflib.py` | Counting, estimator E, the authors' model (Eq. 3 with arcsine q(r)), summaries. |
| `analyze.py` | All pre-registered stages: N grid, model control, T1-T3, CSN fit, strata, placebo. Output `results.json`. |
| `explore.py` | Exploratory branching-ratio analysis (not pre-registered). Output `explore.json`. |
| `robustness.py` | Fit-range robustness of T2 and T3, written by the verifying agent (not pre-registered). Output `robustness.json`. |
| `figure.py` | Figure 1 of the paper. |
| `test_counting.py` | Code check: the sort/LCP counts equal direct prefix counts on 10^5 synthetic games. About 6 s. |
| `independent_count.py RAW TMP OUT` | Independent parser and counter for depths 1 to 12 on all 36 months, written by the verifying agent. Its output is `data/independent_count.json`. Not run by `ci.sh`. |

Environment variables of `ci.sh`: `PYTHON` (default `python3`), `CHESSZIPF_WORK` (default: a new temporary folder), `CHESSZIPF_RAW` (a folder that already holds the 36 files; they are checked and kept), `CHESSZIPF_WORKERS` (default 4).

Resources: about 8 GB of free disk when the raw files are deleted after each parse (15 GB if they are kept), 2 GB of RAM. The compressed download is 6.9 GB.

The `data/` folder holds the committed outputs of one full run (`results.json`, `explore.json`, `robustness.json`), the expected numbers (`expected.json`), and the Lichess SHA-256 sums and game counts of the 36 months.
