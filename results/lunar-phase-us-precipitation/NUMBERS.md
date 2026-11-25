# Numbers in the paper and their sources

Each number of `paper/paper.tex` and `README.md` is listed with its source. A script compared each number from the data files with its rounded value in the paper: 107 of 107 agree (run on 2026-11-25; the script was a scratch check and is not kept). Table 4 of the paper (timing) was printed directly from `data/timing.json` by a script, so its 90 values agree by construction. `RESULT.md` of the solve stage gives the same values.

## Values from the data files

`results:` = `data/results.json`, `exploratory:` = `data/exploratory.json`, `timing:` = `data/timing.json`. Percentages are the stored fraction × 100. `injection/i` is the i-th value of c (0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10).

| Value in paper | Source |
|---|---|
| 1217 | `results:A/n_stations` |
| 980 | `results:B/n_stations` |
| 1218 | `results:n_archive_stations` |
| 41.0 | `results:A/n_station_days` |
| 5.5 | `results:B/n_station_days` |
| 0.399 | `results:B/observed/r2` |
| 0.40 | `results:B/observed/r2` |
| 0.41 | `results:B/null/p_r2` |
| 3.23 | `results:B/observed/phase_d` |
| 5.2 | `results:B/observed/S` |
| 51 | `results:B/observed/n_sig` |
| 0.57 | `results:B/null/p_S` |
| 0.0096 | `results:decision/c_equiv_of_A_amp` |
| 0.05 | `results:decision/power_B_nat_at_A_amp` |
| 0.045 | `results:decision/power_B_S_at_A_amp` |
| 0.494 | `results:A/observed/r2` |
| 0.49 | `results:A/observed/r2` |
| 4.49 | `results:A/observed/phase_d` |
| 4.5 | `results:A/observed/phase_d` |
| 0.092 | `results:A/observed/p_F` |
| 0.09 | `results:A/observed/p_F` |
| 0.124 | `results:A/null/p_r2` |
| 0.12 | `results:A/null/p_r2` |
| 8.05 | `results:A/observed/S` |
| 98 | `results:A/observed/n_sig` |
| 0.099 | `results:A/null/p_S` |
| 0.10 | `results:A/null/p_S` |
| 5.5 | `results:A/null/S_mean` |
| 9.0 | `results:A/null/S_q95` |
| 3.9e-06 | `exploratory:A/F/binom_indep_p` |
| 0.088 | `exploratory:A/F/yrr_p` |
| 0.084 | `timing:A/12UTC_d/yrr_p_n_sig_F` |
| 15 | `results:A/scan/rank_r2_among_far` |
| 161 | `results:A/scan/n_far` |
| 6 | `results:A/scan/rank_S_among_far` |
| 7.5 | `results:A/scan/far_S_q95` |
| 13.7 | `results:A/scan/far_S_max` |
| 28.25 | `results:A/scan/far_S_max_P` |
| 40 | `results:B/scan/rank_r2_among_far` |
| 94 | `results:B/scan/rank_S_among_far` |
| 0.00362 | `results:A/observed/amp` |
| 0.00244 | `results:A/injection/0/amp_mean` |
| 285 | `exploratory:A/t2/n_sig` |
| 23.4 | `exploratory:A/t2/S` |
| 16.8 | `exploratory:beta_null_rate_t2` |
| 17.8 | `exploratory:A/t2/yrr_mean` |
| 24.8 | `exploratory:A/t2/yrr_q95` |
| 0.092 | `exploratory:A/t2/yrr_p` |
| 20.4 | `exploratory:B/t2/S` |
| 0.25 | `exploratory:B/t2/yrr_p` |
| 0.399 | `exploratory:thr_t2` |
| 0.641 | `exploratory:AB/r2` |
| 4.24 | `exploratory:AB/phase_d` |
| 0.049 | `exploratory:AB/yrr_p_r2` |
| 105 | `exploratory:AB/n_sig` |
| 8.6 | `exploratory:AB/S` |
| 0.055 | `exploratory:AB/yrr_p_S` |
| 5.4 | `exploratory:AB/yrr_mean_S` |
| 87.9 | `exploratory:AB/share_station_days_A` |
| 0.139 | `results:A/placebo/27.3/r2` |
| 5.4 | `results:A/placebo/27.3/S` |
| 0.193 | `results:B/placebo/27.3/r2` |
| 6.9 | `results:B/placebo/27.3/S` |
| 0.115 | `results:A/placebo/28.5/r2` |
| 5.2 | `results:A/placebo/28.5/S` |
| 0.063 | `results:B/placebo/28.5/r2` |
| 7.8 | `results:B/placebo/28.5/S` |
| 0.525 | `results:A/placebo/29.530589/r2` |
| 8.3 | `results:A/placebo/29.530589/S` |
| 0.406 | `results:B/placebo/29.530589/r2` |
| 5.9 | `results:B/placebo/29.530589/S` |
| 0.660 | `results:A/placebo/30.5/r2` |
| 7.6 | `results:A/placebo/30.5/S` |
| 0.092 | `results:B/placebo/30.5/r2` |
| 7.4 | `results:B/placebo/30.5/S` |
| 0.277 | `results:A/placebo/31.0/r2` |
| 5.8 | `results:A/placebo/31.0/S` |
| 0.041 | `results:B/placebo/31.0/r2` |
| 4.7 | `results:B/placebo/31.0/S` |
| 0.03 | `results:A/injection/0/power_nat` |
| 0.04 | `results:A/injection/0/power_S` |
| 0.025 | `results:B/injection/0/power_nat` |
| 0.04 | `results:B/injection/0/power_S` |
| 0.08 | `results:A/injection/1/power_nat` |
| 0.05 | `results:A/injection/1/power_S` |
| 0.04 | `results:B/injection/1/power_nat` |
| 0.045 | `results:B/injection/1/power_S` |
| 0.185 | `results:A/injection/2/power_nat` |
| 0.075 | `results:A/injection/2/power_S` |
| 0.05 | `results:B/injection/2/power_nat` |
| 0.045 | `results:B/injection/2/power_S` |
| 0.58 | `results:A/injection/3/power_nat` |
| 0.34 | `results:A/injection/3/power_S` |
| 0.095 | `results:B/injection/3/power_nat` |
| 0.06 | `results:B/injection/3/power_S` |
| 0.87 | `results:A/injection/4/power_nat` |
| 0.745 | `results:A/injection/4/power_S` |
| 0.205 | `results:B/injection/4/power_nat` |
| 0.115 | `results:B/injection/4/power_S` |
| 1.0 | `results:A/injection/5/power_nat` |
| 1.0 | `results:A/injection/5/power_S` |
| 0.52 | `results:B/injection/5/power_nat` |
| 0.355 | `results:B/injection/5/power_S` |
| 1.0 | `results:A/injection/6/power_nat` |
| 1.0 | `results:A/injection/6/power_S` |
| 0.985 | `results:B/injection/6/power_nat` |
| 0.97 | `results:B/injection/6/power_S` |
| Table 4, all 90 values | `timing:{A,B,AB}/{12UTC_d,00UTC_d,18UTC_d,12UTC_d-1,12UTC_d+1,adjusted}/*` |
| 2000 replicates, seeds 20261124 / 20261125 / 20261126 / 20261127 | `PROTOCOL.md` sections 5 and addenda; `timing:seed`, `timing:n_rep` |
| 252 compared values; tolerances ±0.01 (R²_2), ±3 (station counts), ±0.02 (p) | `data/expected.json` (`_tolerance`) |

## Values from other sources

| Value in paper | Source |
|---|---|
| 1218 stations, 1895–2008, 0.4106, p < 0.03, 4.04 d, 281, 23.1%; quotes of paragraphs [5], [11], [12], [13] | Cerveny et al. 2010, read on 2026-11-25 (Exa fetch of the Wiley full text); `PRIOR_ART.md` section 1 |
| F(2,7) p = 0.157 for r² = 0.4106; one-sided t(8) p = 0.023; Beta(1, 3.5) rate 16.8% | `PRIOR_ART.md` section 1; `RESULT.md`; recomputed with SciPy on 2026-11-25 (0.1572, 0.0230, 0.1680) |
| H1 window ±3.69 d; reproduction rule ±0.15 and ±1.5 d; inclusion 3650 / 2000 days; 12:00 UTC | `PROTOCOL.md` sections 3, 4, 6, 7 |
| 1544 stations, 1900–1949; 14.765-day wave; split halves; Greenwich noon | Brier and Bradley 1964 (PDF text via Exa, 2026-11-25); Bradley et al. 1962 (Crossref) |
| Lund quote | Camuffo 1999, Earth Moon Planets 85–86, p. 105 (text via Exa, 2026-11-25) |
| 111 stations; 20 of 48,152 days; 13-term series | `VERIFY.md` round 2 (`git show 45ff8cb:VERIFY.md`), check 7; `RESULT.md` |
| Verifier adjusted p 0.041 against 0.038; pooled run not finished; year-permutation null | `VERIFY.md` round 3, check 6; round 1 check 5 |
| Version 3.35-upd-2026112318, 316,612,378 bytes, SHA-256 `2f94aed8…81148`, 252/252, 46 values not bit-equal, 4.69% → 4.59%, 0.39925 → 0.39934 | `VERIFY.md` round 3, check 3; `../verify/rerun_clean_clone_round3.log` |
| Version 3.35-upd-2026111517, 316,596,781 bytes, SHA-256 `b327e62d…a2151`, de440s SHA-256 | `PROTOCOL.md` section 2; `RESULT.md` |
| 22 Semantic Scholar and 20 OpenAlex citing records | `PRIOR_ART.md` section 2, rows 1 and 2 |
| Rerun time and `252/252 match` of the release copy | `../data/ci_release_clean_copy_2026-11-25.log` (see "Clean-copy run" below) |

## VERIFY.md round 3 issues and where the paper fixes them

| Issue | Fix |
|---|---|
| 1. Cite the round 3 clean-clone rerun; say the numbers are from 3.35-upd-2026111517 and that a version one week newer changes 46 values inside the tolerances. | Paper, Section 6 "How the result was checked", last bullet (version, size, full SHA-256, 252/252, 46 values, largest changes, same verdict). Also `checks/README.md` "Raw data" and `THIRD_PARTY.md`. |
| 2. Do not give the wrong count "two of eight exploratory tests". | Paper, Section 4.3, first paragraph: "We do not correct them for the full number of exploratory comparisons." No count is given anywhere. |
| 3. Say next to each adjusted p-value that it corrects only for the five timings; the abstract gives the period-A station rate as exploratory and at the 0.05 boundary, not "significant" and not "not significant". | Paper, Section 4.3 "Timing of the phase" (italic sentence before Table 4), Table 4 caption, each bullet with an adjusted p-value, and Section 5 (Interpretation). Abstract: "In exploratory analyses, the 1895–2008 station rate is at the 0.05 boundary". The `result.json` summary uses the same words. |
| 4. Quote the source's phase definition ("the average angular difference ... for that day", no hour). | Paper, Section 3 "Lunar phase" (full quote, paragraph [11]) and Section 4.3 "Timing of the phase". |

## Clean-copy run

Commands, 2026-11-25:

```sh
rm -rf /tmp/ci-lunar && mkdir -p /tmp/ci-lunar
cp -R release /tmp/ci-lunar/lunar-phase-us-precipitation
uv venv /tmp/ci-lunar/venv --python 3.13 --seed            # new venv, Python 3.13.18
cd /tmp/ci-lunar/lunar-phase-us-precipitation
PATH=/tmp/ci-lunar/venv/bin:$PATH HEAVY_THREADS=2 run-heavy 7000 bash checks/ci.sh
python3 /Users/kenwu/research/kenwu-lab/tools/check_result.py /tmp/chk/lunar-phase-us-precipitation
```

- `bash checks/ci.sh`: `252/252 match`, exit 0, 1449 s wall time, 959 s user CPU. Fresh downloads: GHCN-Daily 3.35-upd-2026112318, `ghcnd_hcn.tar.gz` SHA-256 `2f94aed8…81148`, `de440s.bsp` SHA-256 `c1c7feea…a49f2`. Log: `../data/ci_release_clean_copy_2026-11-25.log`.
- `check_result.py` on a copy named `lunar-phase-us-precipitation`: `ok: 1 result(s)`.
- The README "Check it" command is `bash checks/ci.sh`; the run above is that command.
