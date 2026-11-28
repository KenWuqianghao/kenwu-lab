# Reproducing the results

Run all commands from the result folder. `bash checks/ci.sh` is the full check. It needs Python 3.13 and network
access to `api.starglass.cfa.harvard.edu` (DASCH), `ssd.jpl.nasa.gov` (Horizons) and `ssp.imcce.fr` (SkyBoT). It
installs `checks/requirements.txt` (numpy, scipy, astropy, requests; pinned versions).

## Steps of `checks/rerun.py`

All downloads go into a new directory (`--data DIR` names it; `ci.sh` uses a new temporary directory). The scripts
in `src/` read and write that directory through the environment variable `PRECOVERY_DATA`.

1. Copy the registered predictions `data/predictions.json` into the directory. The plate list (`data/coverage.json`)
   and the predictions are fixed registered inputs. The check does not rerun `src/coverage.py` or `src/predict.py`.
2. `src/fetch.py`: one DASCH cutout per plate (3 s between requests) and the ATLAS stars within 700". b27808
   returns HTTP 422 (the plate does not cover the position).
3. `src/measure.py`, `src/decide.py`: the registered test (`results.json`, `decision.json`).
4. `src/controls.py`: the other-date control plates. It queries the DASCH plate list at each position, downloads
   6 control cutouts and writes `controls.json`.
5. `src/posthoc.py b27907 b28342 b28520 b28598`: centroid, shape, brightness and track profile of the source
   (`posthoc.json`). This is the verification stage's independent code (`checks/verify/indep.py`) with JSON output.
6. `src/horizons_check.py`: fresh Horizons positions at each midpoint for the series site, the geocentre and the
   other site, and the orbit solution (`horizons_check.json`).
7. `src/skybot.py`: SkyBoT cone searches at the four 1901 positions (`skybot.json`). If the service fails 4 times,
   the script says so and skips the SkyBoT values; all other values are still checked.
8. Compare the values with `data/expected.json`: S, p0 and other numbers to 2 % relative or 0.15 absolute, Horizons
   offsets to 0.1", flags, plate names and solution names exactly. The script also computes the one-sided upper 95 %
   Clopper-Pearson limits of p0, the bound on P_null, P_null without b27907 and the largest separation of the four
   1901 positions. It prints `N of N checks match` and exits 1 on any difference.

`ci.sh` then compares the SHA-256 sums of the new cutouts with `data/cutouts.sha256` and `data/controls.sha256` (the
cutouts used for the paper) and prints the number that are identical. This line is for information; it does not
fail the check.

Options of `rerun.py`: `--data DIR` reuses or fills `DIR`; `--write-expected` rewrites `data/expected.json` (for the
authors only).

## Files

| File | Content |
|---|---|
| `src/screen.py`, `src/apps.py` | choice of the target among near-Earth asteroids, and its bright apparitions (solve stage; not run by the check) |
| `src/coverage.py` | registered plate rule; wrote `data/coverage.json` (about 60 DASCH queries; not run by the check) |
| `src/predict.py`, `src/hz.py` | registered predictions; wrote `data/predictions.json` (not run by the check) |
| `src/dasch.py`, `src/fetch.py` | DASCH client and downloads; each cutout request is logged with its SHA-256 |
| `src/measure.py`, `src/decide.py` | registered statistic and decision |
| `src/controls.py` | other-date control plates |
| `src/posthoc.py`, `src/horizons_check.py`, `src/skybot.py` | checks made after the decision |
| `checks/figure.py` | Figure 1 of the paper (needs matplotlib; not run by the check): `PRECOVERY_DATA=DIR python3 checks/figure.py paper/fig_ivar.png` with a data directory of `rerun.py` |
| `checks/verify/` | the verification stage's own scripts (`indep.py`, `hzcheck.py`; not run by the check; they read a copy of the solve-stage repository with its cutouts) |
| `data/results.json`, `data/decision.json`, `data/controls.json` | results of record (solve stage) |
| `data/posthoc.json`, `data/horizons_check.json`, `data/skybot.json` | outputs of the checks after the decision (write stage) |
| `data/GIT_LOG.txt` | commit list of the problem repository with author and committer times (registration evidence) |

## Known sensitivities

- JPL Horizons serves the current orbit. If JPL updates the orbit of Ivar, the Horizons offsets can exceed 0.1" and
  the solution name changes. The predictions used for the test are stored in `data/predictions.json`.
- DASCH can reprocess its scans or change its plate metadata. Then the cutouts are not byte-identical, the control
  plate lists can change, and the numbers can change.
- The random placebo regions use a fixed seed of Python's `random` module (seed 1). The values were checked with
  Python 3.13 and the pinned package versions.
