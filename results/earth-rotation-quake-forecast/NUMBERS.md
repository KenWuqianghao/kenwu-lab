# Numbers in the paper and their sources

A scratch script (not kept) read `results.json` from `python3 -I checks/rerun.py --work /tmp/erq-w1 --offline` (2026-11-25, "checked 647 values, 0 mismatches"). It printed the rounded value of each source key. Each printed value equals the number in `paper/paper.tex`, `README.md` and `result.json`. `RESULT.md` of the solve stage gives the same values. The exceptions are the values that are new at the write stage (`write_additions`) and the P2 power, which now uses 10 000 simulations.

## Values from `checks/rerun.py`

| Value in paper | Source key in `results.json` | Value from the rerun |
|---|---|---|
| 1607 | `n_events_total_1900_2025` | 1607 |
| 1395 | `n_events_declustered_1900_2025` | 1395 |
| 1496 | `baseline/N` | 1496 |
| 12.68 / 12.7 | `baseline/lambda0` | 12.68 / 12.7 |
| 17.35 | `baseline/var` | 17.35 |
| 34.4 | `baseline/k` | 34.4 |
| 15.8 (forecast level per year) | `1.25 × baseline/lambda0` | 15.8 |
| 17, 10, 9, 19, 11 | `P1/per_year` | 17, 10, 9, 19, 11 |
| 66 | `P1/N` | 66 |
| 13.2 | `P1/rate` | 13.2 |
| 1.04 | `P1/ratio` | 1.04 |
| 0.78–1.39 | `P1/ratio_95ci` | 0.78–1.39 |
| 0.115 | `P1/p_refute` | 0.115 |
| 0.399 / 0.40 | `P1/p_support` | 0.399 / 0.40 |
| INCONCLUSIVE | `P1/verdict` | INCONCLUSIVE |
| 61 | `write_additions/P1_refuted_if_N_le` | 61 |
| 80 | `write_additions/P1_supported_if_N_ge` | 80 |
| 0.38, 0.31, 0.18, 0.070 | `write_additions/p_refute_by_level 1.10, 1.13, 1.20, 1.30` | 0.38, 0.31, 0.18, 0.070 |
| about 1.34 (first level with p_refute < 0.05) | `write_additions/p_refute_by_level 1.33, 1.34` | 0.0504 (1.33), 0.0451 (1.34) |
| 1.34 (17 per year as ratio) | `write_additions/level_17_as_ratio` | 1.34 |
| Poisson 0.073 / 0.388 | `P1_secondary/poisson` | 0.073 / 0.388 |
| M≥7.1: 51, 9.92, 1.03, 0.124, 0.443 | `P1_secondary/m7.1` | 51, 9.92, 1.03, 0.124, 0.443 |
| Declustered: 59, 11.02, 1.07, 0.153, 0.327 | `P1_secondary/declustered` | 59, 11.02, 1.07, 0.153, 0.327 |
| 1973–2017: 13.73, 0.96, 0.019, 0.637 | `P1_secondary/baseline_1973_2017` | 13.73, 0.96, 0.019, 0.637 |
| 618 (1973–2017 events) | `45 × baseline_1973_2017/lambda0` | 618 |
| 12.0 (1900–1972 rate) | `write_additions/rate_1900_1972` | 12.0 |
| Window 2017–2021: 62, 0.98, 0.054, 0.569 | `P1_secondary/window_2017_2021` | 62, 0.98, 0.054, 0.569 |
| Level 17: 0.045, 0.399 | `P1_secondary/level_17_per_year` | 0.045, 0.399 |
| Sliding sums: 114, 63.4, 12.4, 0.21, 0.42 | `P1_secondary/empirical_5yr_sums` | 114, 63.4, 12.4, 0.21, 0.42 |
| 73 (2013–2017), binomial p 0.61 | `P1_secondary/vs_2013_2017` | 73, 0.61 |
| Placebo 52 / 12 / 50 | `P1_placebo_windows_1900_2013` | 52 / 12 / 50 |
| 10.5% | `write_additions/placebo_supported_fraction` | 10.5% |
| Injection 43.4/4.6, 4.4/47.9, 2.5/59.1 % | `P1_injection` | 43.4/4.6, 4.4/47.9, 2.5/59.1 |
| 2018–2025: 17, 10, 9, 19, 11, 19, 10, 16 (111) | `P2/counts` | 17, 10, 9, 19, 11, 19, 10, 16 (111) |
| enhanced 2018–2021 | `P2/enhanced_years` | [2018, 2019, 2020, 2021] |
| 13.75 and 14.0 per year | `P2/counts (means of 2018–2021 and 2022–2025)` | 13.75 and 14.0 |
| Lag 5: 0.495/0.500, 0.98, 0.614 (70) | `P2` | 0.495/0.500, 0.98, 0.614 (70) |
| Lag 6: 2018–2022, 0.595/0.625, 0.88, 0.714 (56) | `P2_secondary/L6` | [2018, 2019, 2020, 2021, 2022], 0.595/0.625, 0.88, 0.714 (56) |
| Lag 5 declustered: 0.516/0.500, 1.07, 0.429 (70) | `P2_secondary/declustered_L5` | 0.516/0.500, 1.07, 0.429 (70) |
| Lag 5 M≥7.1: 0.541/0.500, 1.18, 0.286 (70) | `P2_secondary/m7.1_L5` | 0.541/0.500, 1.18, 0.286 (70) |
| Power 0.170 / 17%, false-positive 0.034 | `write_additions/P2_power_x1.25_nsim10000, ..._false_positive_...` | 0.170, 0.034 |
| Solve-stage 2000 simulations: 0.172, 0.028 | `P2_power_x1.25, P2_false_positive_x1.00` | 0.172, 0.028 |
| C04 mask differs 1983, 1997, 2008, 2014 | `write_additions/c04_mask_years_differ_1963_2024` | [1983, 1997, 2008, 2014] |
| C04 lag-5 years 2018, 2020, 2021; p = 0.39 | `write_additions/P2_L5_c04_mask` | [2018, 2020, 2021], 0.39 |
| 0.003 ms (2013→2014 LOD) | `write_additions/c02_annual_lod_ms_2010_2025` | 0.003 |
| LOD rises each year 2011–2016, falls 2017–2022 | `lod/mask_2005_2025` | [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0] |
| 48% (deceleration years 1900–2017) | `lod/share_dec_years_1900_2017` | 48% |
| 0.9991 (C02–C04 correlation) | `lod/c02_vs_c04_annual_corr_1962_2024` | 0.9991 |
| P3 lag 0 | `P3_raw/0` | 0.504, 0.483, 1.09, 0.90 |
| P3 lag 1 | `P3_raw/1` | 0.470, 0.492, 0.92, 0.12 |
| P3 lag 2 | `P3_raw/2` | 0.481, 0.492, 0.96, 0.32 |
| P3 lag 3 | `P3_raw/3` | 0.495, 0.492, 1.02, 0.57 |
| P3 lag 4 | `P3_raw/4` | 0.511, 0.492, 1.08, 0.87 |
| P3 lag 5 | `P3_raw/5` | 0.502, 0.492, 1.04, 0.75 |
| P3 lag 6 | `P3_raw/6` | 0.521, 0.492, 1.12, 1.00 |
| P3 lag 7 | `P3_raw/7` | 0.523, 0.492, 1.14, 1.00 |
| P3 lag 8 | `P3_raw/8` | 0.525, 0.500, 1.10, 0.94 |
| P3 lag 9 | `P3_raw/9` | 0.507, 0.500, 1.03, 0.65 |
| Random-catalog pct lag 5, 6, 7: 0.78, 0.99, 0.99 | `P3_raw/L/random_pct` | 0.78, 0.99, 0.99 |
| Max over lags raw 0.032 / 97th | `P3_raw/max_over_lags_*` | 0.032 / 0.97 |
| Max over lags declustered 0.029 / 86th | `P3_declustered/max_over_lags_*` | 0.029 / 0.86 |
| Synthetic lag-5 catalog: peak 1.22 at lag 5 | `P3_injection_*` | 1.22 at lag 5 |

## Values that `checks/rerun.py` does not compute

| Value in paper | Source |
|---|---|
| NB p-values from 2 million gamma–Poisson draws: 0.1152, 0.3989 | `RESULT.md` §2 (solve-stage check) |
| ComCat `count` endpoint: 1496, 66, 73, 111, 618 | `VERIFY.md` §1.4 and `RESULT.md` §2 |
| A mutation of one expected count gives a failure | `VERIFY.md` §1.3 |
| Run time 22 s for `bash checks/ci.sh` | clean-copy run of 2026-11-25 (this stage, below) |
| Protocol commit 2026-11-25 18:04 CET | `git log`, commit 027f1bc |
| Counts seen before the protocol: 17, 10, 9, 19; 66 | `PROTOCOL.md` §0 |
| 51.7 ± 1.3 % (random-catalog level in Bilham et al. 2022) | `PRIOR_ART.md` §2 |
| "17 to 20", "two to five more", quotes | Science article, fetched 2026-11-25 (this stage) |
| Gardner–Knopoff window formula | van Stiphout et al. 2012 (CORSSA), equation 1, read 2026-11-25 (this stage) |

## Issues of `VERIFY.md` and where the paper fixes them

| Issue | Fix |
|---|---|
| W1: P2 power used 2000 simulations, protocol says 10 000 | `checks/rerun.py` now also runs 10 000 simulations (`write_additions`, own seed). Paper §3, paragraph "A deviation, found after the results", and Table 2 caption report 0.170 and 0.034 and name the 2000-simulation values as the solve-stage run. `PROTOCOL.md` Addendum 1 (dated) records it. |
| W2: the level 1.25 λ0 is a reading; the "17 per year" and 1973–2017 rows; equatorial band | Paper §4.1, paragraph "The forecast level is a reading of the source" (direction and p_refute for other levels); paragraph "Secondary analyses" (neither row read as a refutation; 17 per year = 1.34 λ0); Table 1 labels them "below 0.05", not "refuted"; §1 quotes the 10°N–30°S sentence and §6 lists it as a limit. |
| W3: "did not appear" claims too much; "inconclusive" in title and abstract | Title and abstract carry "inconclusive". §4.1: "The observed rate is near the baseline. The data cannot separate 'no increase' from '+25%'." The interval 0.78–1.39 is given next to the ratio. |
| W4: P2 power next to the verdict; mask fragility; mask is a re-implementation | Abstract, §4.2 text and Table 2 caption give the power with the verdict. §4.2 gives the 0.003 ms change of 2013–2014, the C04 mask check (4 years differ, p = 0.39), and the 48–49 % vs 51.7 % comparison. |
| W5: P3 must not read as a confirmation | §4.3 gives the lag-5 values (0.502 vs 0.492, 75th percentile), the lag 6–8 values, the max-over-lags percentiles (97th raw, 86th declustered, 99 shifts), and says P3 is in-sample and not a test. The phrase "near the published 5–6 years" is not used. |
| W6: offline note; model false-verdict rate next to placebo; pre-registration disclosure | `--offline` now reads the LOD files from the work folder, and `checks/README.md` says so. §4.1 "Controls" gives the ~5 % model rate and 12 of 114 (10.5 %) placebo windows together. §3 keeps the disclosure of `PROTOCOL.md` §0 and the limit of the commit-order evidence; §6 repeats it. |

## Clean-copy runs (2026-11-25)

Commands, from a copy of `release/` named `/tmp/erq-ci/earth-rotation-quake-forecast`, with a new venv (`uv venv --seed --python 3.13`, Python 3.13.18):

```
$ bash checks/ci.sh            # exit 0, 21.5 s wall time
checked 647 values, 0 mismatches
P1: N=66 lambda0=12.678 k=34.41 ratio=1.041 p_refute=1.15e-01 p_support=0.399 -> INCONCLUSIVE
P2: L=5 enhanced=[2018, 2019, 2020, 2021] p_perm=0.6142857142857143 -> NOT SUPPORTED
P2 power x1.25 (10 000 simulations) = 0.1697; false-positive rate = 0.0336
$ python3 /Users/kenwu/research/kenwu-lab/tools/check_result.py /tmp/erq-ci/earth-rotation-quake-forecast
ok: 1 result(s)
$ python3 -I checks/rerun.py --work /tmp/erq-ci/w             # checked 647 values, 0 mismatches
$ python3 -I checks/rerun.py --work /tmp/erq-ci/w --offline   # checked 647 values, 0 mismatches
$ python3 -I paper/figures/make_figure.py /tmp/erq-ci/w/results.json   # byte-identical to paper/figures/fig1_counts.png
```

No `NOTE` line was printed, so the new ComCat download equals `data/comcat_m7_1900_2025.csv`. After the runs, `diff -rq` showed no change in the copy.
