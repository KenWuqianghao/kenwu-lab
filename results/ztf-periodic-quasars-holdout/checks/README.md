# Reproducing the forward test

Run all commands from the result folder. `checks/ci.sh` is the full check. It installs the pinned packages of `checks/requirements.txt` into the active Python 3.13, then runs `checks/rerun.py`, compares the per-object table and draws the figures. Set `JOBS=n` to choose the number of analysis processes (default: one per CPU core).

## Steps of `checks/rerun.py`

1. `fetch_data.py` downloads the ZTF r-band light curves of the 86 candidates and the 344 placebo quasars from the IRSA light-curve service (`nph_light_curves`, 3 arcsec circle) into `work/lc/`. Files that already exist are not downloaded again. Delete `work/` to force a fresh download.
2. `analysis.py` runs the per-object test of `PROTOCOL.md` and writes `work/results/<id>.json`. Each object has its own random seed, derived from its ID, so the result does not depend on the number of processes.
3. `summarize.py` computes the tests and writes `data/summary.json` and `data/results_table.csv`.
4. The script compares every value of `data/summary.json` with `data/expected.json` (relative tolerance 1e-3; absolute tolerance 0.01 for the Stouffer Z values) and prints `164/164 expected values reproduced` when all agree.

`python3 checks/rerun.py --compare` does only step 4.

## Sample tables

`data/candidates.csv` and `data/placebo.csv` are inputs. `fetch_data.py` uses them if they exist. To rebuild them from the source catalogues, delete both files and run `python3 checks/fetch_data.py`. This downloads SDSS DR14Q (792 MB) and the 2QZ catalogue (17 MB) into `work/`. The candidate names come from `data/candidate_names.txt`, which lists the labels of the Appendix C figures in the arXiv source of Chen et al. (arXiv:2206.11497v2). A rebuild in the verification stage gave byte-identical tables.

## Files

| File | Content |
|---|---|
| `qpo.py` | methods: windows, polynomial clip, 20-day bins, periodogram, score k, DRW and power-law mocks |
| `analysis.py` | per-object test: frozen sinusoid, conditioned nulls, power, injection |
| `summarize.py` | tests T1 and T2, controls, post hoc limits |
| `plot.py` | `data/fig_forward_score.png` and `data/fig_named.png` |
| `independent/indep.py` | independent recomputation of P, xi, k, T1, T2 and the injection by the verification stage (no import of the files above) |
| `independent/pcheck.py` | independent conditioned DRW p-values for the 21 objects in `independent/pcheck_ids.txt` |

The independent scripts read the downloaded light curves:

```sh
python3 -I checks/independent/indep.py work/lc data/results_table.csv data/placebo.csv
python3 -I checks/independent/pcheck.py work/lc data/results_table.csv $(cat checks/independent/pcheck_ids.txt)
```

## Known sensitivities

- Monte Carlo: two nominal passes (SDSS J110837.68+100333.1, SDSS J113543.22+592241.8) have p_DRW of 0.046 and 0.044. Other random draws give 0.050 and 0.052. The fixed seeds make the committed numbers exact.
- The 15th-order polynomial fit is poorly conditioned. numpy prints `RankWarning` lines; they are expected. Another polynomial basis moves k by up to 0.056 for 17 of 359 objects. The decision does not change.
- The test window ends at MJD 60970.0, so a later ZTF release does not change the result. A reprocessing of old ZTF photometry by IRSA would change the input data. The light curves that we used were downloaded on 2026-11-24 and 2026-11-25.

## Platforms

On one platform, the fixed seeds make every number exact. Between platforms, the Monte Carlo values can differ a little. A mock light curve is accepted when its fitted period and significance pass a threshold. A floating-point difference near the threshold can accept a different set of mocks, and the random stream then diverges. On Linux aarch64 with OpenBLAS, 6 of the 516 objects get p-values that differ from the committed macOS arm64 values by at most 0.016. This is within the Monte Carlo error of about 0.016 at 1,000 accepted mocks. All counts and all numbers in the paper are the same. The Stouffer Z of the placebo under the SPL null changes from -1.4039 to -1.4013. The CI runner (Linux x86_64) gives the same Stouffer Z to 15 digits.

So `checks/ci.sh` compares the Monte Carlo p-values of `data/results_table.csv` within 0.03 and requires each one to be on the same side of 0.05. It does not compare the accepted-mock counts (`*_n_acc`). `checks/rerun.py` compares the Stouffer Z values within 0.01. All other values use a relative tolerance of 1e-3.
