# Reproducing the results

Run all commands from the result folder. `bash checks/ci.sh` is the full check. It needs Python 3.13 and network access to `ssd.jpl.nasa.gov`, `api.starglass.cfa.harvard.edu` and `dc.g-vo.org`. It installs `checks/requirements.txt` (numpy, scipy, astropy, requests; pinned versions).

## Steps of `checks/rerun.py`

All downloads go into a new directory (`--data DIR` names it; `ci.sh` uses a new temporary directory). The scripts in `src/` read and write that directory through the environment variable `PRECOVERY_DATA`.

1. `src/predict.py 1` and `src/predict.py 2`: JPL Horizons tracks for the 11 round-1 plates and the 8 round-2 plates (`src/plates.py`). Horizons answers are cached in `hz_cache/`.
2. `src/fetch.py 1` and `src/fetch.py 2`: one DASCH cutout per plate (3 s between requests) and the ATLAS stars within 700". a06535 returns HTTP 422 (the plate does not cover the position).
3. `src/measure.py`: round 1, the registered test (`results.json`).
4. `src/measure2.py`: round 2 (`results2.json`).
5. `src/astrometry.py`: positions of the Ganymed source, two centroid methods and six variants (`astrometry.json`, `astrometry_variants.json`).
6. `src/shapes.py`: shapes of the source, the predicted trail and the stars (`shapes.json`).
7. `src/hdap.py predict | fetch | measure`: round 3 on the 15 Heidelberg plates of `data/hdap/hektor_cover.csv` (`hdap/results.json`). B262a returns HTTP 204 (no data).
8. `src/motion_check.py`: the post hoc motion check of 1901 Aug 23 (`hdap/motion_check.json`).
9. The script compares 295 values with `data/expected.json`: positions to 2e-5 deg, p values to 2 % relative, other numbers to 0.051 absolute, and flags exactly. It also checks that each Harvard prediction is the Horizons row at the DASCH midpoint (offset 0 min) and that the Heidelberg tracks have 2-min steps throughout. It prints `295 of 295 checks match` and exits 1 on any difference.

`ci.sh` then compares the SHA-256 sums of the new cutouts with `data/cutouts.sha256` (the cutouts used for the paper) and prints the number that are identical. This line is for information; it does not fail the check.

Options of `rerun.py`: `--data DIR` reuses or fills `DIR`; `--write-expected` rewrites `data/expected.json` (for the authors only).

## Files

| File | Content |
|---|---|
| `src/plates.py` | round-1 and round-2 plate lists and the selection rule |
| `src/hz.py` | JPL Horizons client and parser (rows with a rise/transit/set mark are read, not dropped) |
| `src/dasch.py` | DASCH API client; logs each cutout request with its SHA-256 |
| `src/predict.py`, `src/fetch.py` | predictions and downloads, rounds 1 and 2 |
| `src/measure.py`, `src/measure2.py` | registered statistics of rounds 1 and 2 |
| `src/hdap_cover.py` | round-3 plate selection from `data/hdap/plates_1895_1907.csv` (not run by the check) |
| `src/hdap.py` | round 3: predictions, cutouts, statistic and decision |
| `src/astrometry.py`, `src/shapes.py`, `src/motion_check.py` | measurements after the decisions |
| `src/stamps.py`, `src/stamps_1901.py` | exploratory stamps of the solve stage (need matplotlib; not run by the check) |
| `checks/figure.py` | Figure 1 of the paper (needs matplotlib; not run by the check): `PRECOVERY_DATA=DIR python3 checks/figure.py paper/fig_ganymed.png` |
| `checks/verify/`, `checks/verify2/` | independent code of the two verification rounds (not run by the check; each docstring gives its input and output paths) |
| `data/prereg/` | the registered predictions and results of rounds 1 and 2, before the i21780 parser fix (PROTOCOL.md, Addendum 4) |
| `data/predictions*.json`, `data/hdap/predictions.json` | the corrected predictions used for the paper |
| `data/results*.json`, `data/astrometry*.json`, `data/shapes.json`, `data/hdap/results.json`, `data/hdap/motion_check.json` | the results of record |
| `data/GIT_LOG.txt` | commit list with author and committer times (registration evidence) |

## Known sensitivities

- JPL Horizons serves the current orbit. If JPL updates the orbit of Ganymed or Hektor, the predicted positions change slightly, and position values can fail the 2e-5 deg (0.07") tolerance. The predictions used for the paper are stored in `data/predictions.json`, `data/predictions2.json` and `data/hdap/predictions.json`.
- DASCH and HDAP can reprocess their scans. Then the cutouts are not byte-identical, and the numbers can change.
- The random controls use fixed seeds of Python's `random` module (1, 3, 4 and 5). The values were checked with Python 3.13 and the pinned package versions.
