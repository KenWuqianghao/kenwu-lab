# Checks

All commands run from the result folder.

## Scripts

| Script | What it does |
|---|---|
| `ci.sh` | CI entry point. Makes a temporary venv with `requirements.txt`, runs `paper_numbers.py`, then `rerun.py --skip-2016`. With `PBQ_FULL=1`, it runs the full `rerun.py`. |
| `paper_numbers.py` | Offline. Checks that each of 77 numbers in `paper/paper.tex` equals its value in `data/*.json` or in `independent/*.log`, and that `data/results.json` and `data/addendum/addendum.json` equal `data/expected.json`. `--markdown` prints the table of `NUMBERS.md`. |
| `rerun.py` | Streams the monthly files from database.lichess.org, checks each SHA-256 against the published list, runs `build.py` and `analyze.py` (and `addendum.py` without `--skip-2016`), and compares every number with `data/expected.json` (relative tolerance 1e-9). |
| `fetch_month.sh`, `extract_headers.py` | Stream one monthly `.pgn.zst` file. Keep 13 header tags as a zstd TSV. The PGN is not stored. |
| `build.py` | Builds the player-game table (DuckDB): post-game rating, personal best, game index, gap to the next game, sample rules 2, 3, 5, 6, 7 of `PROTOCOL.md`, and the personal-best filter (rule 4) as a column. |
| `analyze.py` | Primary estimate, placebos, covariate balance, within-player shuffle, injected jump, round-number control, robustness variants, bins for the figure. |
| `addendum.py` | Addendum A: periods A and B from the 2013-2016 table, and the difference B - A. |
| `figure.py` | `python3 checks/figure.py data/results.json paper/fig_quit_pb.pdf data/addendum/period_B.json` (needs matplotlib). |

## Run times and records

| Run | Command | Result |
|---|---|---|
| Solve stage, fresh clone, macOS M1 Pro | `rerun.py` (2013-2016) | 48 SHA-256 match, 0 mismatches, 44 min. Log: `data/rerun_log.txt`. |
| Verify stage, second clean clone | `rerun.py` (2013-2016) | 48 SHA-256 match, 0 mismatches, about 53 min. Log: `independent/rerun_clean_clone.log`. |
| Write stage, clean copy of this folder, new venv (Python 3.13) | `bash checks/ci.sh` | 76 paper numbers match; 36 SHA-256 match; 0 mismatches; `RERUN PASS`; 12 min 42 s. Log: `data/ci_log.txt`. |

The 2013-2015 rerun was not run on Linux before release. DuckDB uses integer arithmetic for the personal best and the game order, and `analyze.py` sorts all rows by player and game before the regression and the shuffle. So the result does not depend on the order of rows, but this is not verified on Linux.

## Independent check

`independent/` holds a second implementation that the verifier wrote before it read `build.py` and `analyze.py` in detail.

- `stream.py OUT_NPZ "2015-12-30 23:59:59" HDR_DIR [HDR_DIR2]` reads the header TSVs of `fetch_month.sh` in time order and keeps one state per player in plain Python.
- `rdcheck.py OUT_NPZ` fits each estimate with `statsmodels` WLS (clustered errors) and with plain numpy. It also prints the rating-chain variants, the estimates by year and the round-number bins.
- `extra.py` gives the round-number control by year, the estimate with three covariates, the estimate with player fixed effects, and the estimate without the bins `x = 0` and `x = 1`.

These scripts need `statsmodels` in addition to `requirements.txt`. They are not part of CI. Their logs are the source of the numbers in Section 6 and limits 8 and 9 of the paper.

## Definitions in one place

- Post-game rating `r = pre + RatingDiff`. If `RatingDiff` is absent, `r` is the pre-game rating of the next game at the same speed.
- Personal best `PB` = maximum of `r` over earlier games at the same speed. Running variable `x = r - PB`.
- Quit = the next rated game (any speed) starts more than `60 min + 2 * (base + 40 * increment)` after this start, or there is no next game.
- Estimator: local linear, triangular kernel, `h = 15`, cutoff between `x = 0` and `x = 1`, errors clustered by player.

`PROTOCOL.md` has the full rules, the decision rule and the two addenda.
