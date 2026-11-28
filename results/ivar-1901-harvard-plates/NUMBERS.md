# Numbers in the paper and their sources

`E` = `data/expected.json` (reproduced by `checks/rerun.py`; key given). `R` = `RESULT.md` of the solve stage.
`V` = `VERIFY.md` of the verification stage (round 1, commit `fe1b19c` of the problem repository; section number
follows). `P` = `PROTOCOL.md`. `G` = `data/GIT_LOG.txt` and `data/cutouts/log.jsonl`. `W` = sources opened in the
write stage on 2026-11-28 (SBDB API, MPC `get-obs` API, Wikipedia raw text, crossref, arXiv API, doi.org).

## Introduction and data

| Number in paper | Where | Source |
|---|---|---|
| discovery 1929 Sep 25, Hertzsprung, Johannesburg; `first_obs` 1929-09-25; 1929 SH | Abstract, Sect. 1 | W: `sbdb.api?sstr=1627&discovery=1`; V 1 |
| H = 12.79, diameter about 9 km (9.12) | Sect. 1 | W: `sbdb.api?sstr=1627&phys-par=1` |
| 14 675 observations, 35 488 days | Sect. 1 | W: SBDB `n_obs_used`, `data_arc`; V 1 |
| MPC 18 813 lines, earliest 1929 Sep 25.96 | Sect. 1 | W: `get-obs` (OBS80); V 1 |
| Wikipedia: arc begins with the discovery, no precoveries | Sect. 1 | W: `en.wikipedia.org/w/index.php?title=1627_Ivar&action=raw` |
| orbit solution JPL#1545 | Sect. 2, 5, 8 | E `hz.<plate>.solution`; W: SBDB `orbit_id` 1545 |
| 835 x 835 px, 1.44"/px | Sect. 2 | `src/measure.py` (1.44"/px), `src/posthoc.py` output (shape 835 x 835) |
| 28.2 years (1901-07-18 to 1929-09-25); 28.1 years (from 1901-08-25) | Title, abstract, Sect. 4 | date arithmetic: 28 y 69 d = 28.19 y; 28 y 31 d = 28.08 y |

## Method

| Number in paper | Where | Source |
|---|---|---|
| `46da2c1` 01:04:15; `3e78161` 01:12:01; first request 01:12:05 CET; `7c3db31` 01:04:21 | Sect. 3.1 | G (commits; log entry 1, 00:12:05Z); V 2 |
| apparitions 1901 May 1-Oct 20, 1906 Jul 25-Sep 15, 1929 May 1-Sep 24; V < 12.6 | Sect. 3.2 | `src/coverage.py` docstring; P |
| Sun < -12 deg, altitude > 15 deg, margin 0.3, B-V 0.8, 30" | Sect. 3.2 | `src/coverage.py`; P |
| 25 candidate plates, 6 kept (5 b of 1901, 1 ac of 1929), no 1906 candidate | Sect. 3.2 | `data/coverage.json`; V 4 |
| 5-min steps, -2 h to +2 h | Sect. 3.3 | `src/predict.py`; P |
| Gaussians 1.5 and 15 px, 1.4826 MAD, 3 / 6 matches, buffer 15", threshold 10, 300 regions at 90"-420", P < 1e-3 | Sect. 3.4 | `src/measure.py`; P |
| control rule: 2 nearest b plates, limit >= target, exposure within factor 2, edge > 0.5 deg, 5" | Sect. 3.5 | `src/controls.py` docstring |
| SkyBoT radius 0.1 deg | Sect. 3.5 | `src/skybot.py` |
| background 41 px, smoothing 1 px, centroid; 6" track window | Sect. 3.6 | `src/posthoc.py` |

## Result

| Number in paper | Where | Source |
|---|---|---|
| S = 28.6, 31.9, 62.7, 42.8, 4.3 | Abstract (pass/fail), Table 1 | E `plate.<plate>.S`; R; V 3 |
| p0 = 0.243, 0.003, 0.030, 0.050, 0.000 | Table 1, Sect. 4 | E `plate.<plate>.p0` (0.2433, 0.0033, 0.03, 0.05, 0.0) |
| 73 of 300 (b27907) | Sect. 4 | 0.2433 x 300 = 73 |
| midpoints, exposures, limits, V | Table 1 | `data/predictions.json`; `data/coverage.json` |
| b27808 not covered (HTTP 422) | Abstract, Table 1 | E `plate.b27808.covered` = false; G log entry 1; V 3 |
| set E 4 of 4, P_null = 1.2e-6; set A 4 of 5 | Abstract, Sect. 4 | E `set.E.*`, `set.A.*` (1.22e-6) |
| upper 95 % limits 0.288, 0.016, 0.052, 0.076; bound 1.8e-5 | Abstract, Sect. 4, 8 | E `set.E.p0_cp95`, `set.E.P_null_cp95` (1.78e-5); V 6 |
| P_null without b27907 = 5.0e-6 | Sect. 4 | E `set.E_without_b27907.P_null`; V 6 |
| ac27730 fit "none" (no star matched) | Sect. 4 | E `plate.ac27730.fit`; `data/results.json` (n = 0) |
| 13 days (1929-09-12 to 1929-09-25) | Abstract, Sect. 4 | date arithmetic |
| positions RA 4.0 deg / Dec +5.9 deg to RA 24.3 deg / Dec -15.9 deg; up to 29.6 deg apart | Sect. 4 | `data/predictions.json`; E `max_separation_1901_deg`; R |
| b27907 peak 58.6" from midpoint, 146" trail, -0.42 h | Sect. 4 | E `plate.b27907.peak_from_mid_arcsec`; `data/results.json` `peak_track_hours`; P Addendum 1 |
| peak pixels 4.0", 2.5", 0.5" | Sect. 6 | E `plate.<plate>.peak_from_mid_arcsec` |

## Controls

| Number in paper | Where | Source |
|---|---|---|
| target max z within 5": 17.0, 31.9, 62.7, 42.8 | Table 2 | E `ctrl.<plate>.target_z5` |
| control plates and max z 0.71, 0.33, 0.90, 0.66, 0.76, 1.19 (range 0.33-1.19) | Abstract, Table 2, Sect. 5 | E `ctrl.<plate>.<control>.z5`; V 3 and 6 |
| control dates | Table 2 | `data/controls.json` `expdate` |
| nearest ATLAS star < 16 mag: 81.7", 33.0", 320", 152" | Sect. 5 | E `post.<plate>.nearest_star_brighter_16_arcsec` (320.4, 152.1) |
| no star brighter than 19 within 20" | Sect. 5 | V 5 |
| SkyBoT: only Ivar within 180"; (7388) at 254", V 18.7; Ivar 23.3", 32.6", 19.2", 26.5" | Sect. 5 | E `skybot.<plate>.*`; `data/skybot.json`; V 6 |
| fresh Horizons 0.0"; site 802 20"-34"; geocentre 5"-14" | Sect. 5 | E `hz.<plate>.*` (1901 plates: 802 20.39-34.32, geocentre 5.16-13.8); V 4 |

## Measurements after the decision

| Number in paper | Where | Source |
|---|---|---|
| centroids 0.7", 3.1", 4.0"; "within about 4"" | Abstract, Sect. 6, Table 3 | E `post.<plate>.centroid_offset_arcsec`; V 5 |
| peak z 27.1, 30.0, 73.0, 40.8 | Table 3 | E `post.<plate>.peak_z`; V 5 |
| b27907: 162", axis ratio 12, 7 deg, predicted 146" | Abstract, Sect. 6, Table 3 | E `post.b27907.*`; V 5 |
| z >= 10 on track: -0.50 to +0.42, -0.25 to +0.25, -0.33 to +0.58, -0.33 to +0.25 h | Sect. 6, Table 3 | E `post.<plate>.track_hours_z_ge_10`; `data/posthoc.json` `track_z_6arcsec` |
| shapes 25"/10", 42"/50", 19"/8"; ratios 1.2, 1.5, 1.3; angles 31, 72, 38 deg | Sect. 6, Table 3 | E `post.<plate>.*` |
| 50"-60" per hour | Sect. 6 | `data/coverage.json` `rate` (59.2, 49.8, 49.5 "/h) |
| V + 0.8 = 12.4, 12.6; estimates 12.3 (0.53), 11.8 (0.65), 13.3 (1.56) | Sect. 6 | `data/predictions.json` V; E `post.<plate>.mag_estimate`, `.mag_rms`; V 5 |

## Checks

| Number in paper | Where | Source |
|---|---|---|
| five fresh cutouts byte-identical (verify); rerun "OK" | Sect. 7 | V 3 |
| write-stage rerun: 11 of 11 cutouts byte-identical; `ci.sh` result | README "Check it" | see the section "Rerun from a clean copy" below |

# Issues of VERIFY.md (round 1) and where they are fixed

| Issue | Fix in the paper |
|---|---|
| W1: b27907 weak alone (p0 = 0.243, peak 58.6"); trail evidence marked post hoc; no control plate; 28.1 years without it | Sect. 4, paragraph "The earliest plate, b27907"; Sect. 6, "The trail on b27907"; Table 2 (no control); Sect. 8, item 3; abstract ("That plate alone is weak ... no control plate") |
| W2: MPC URL `tmp2/1627.txt` is dead | Reference [mpcobs] is the `get-obs` API with the designation and the date; `THIRD_PARTY.md` row |
| W3: rerun did not reproduce controls, selection, Horizons | `checks/rerun.py` now reruns `src/controls.py`, `src/horizons_check.py`, `src/skybot.py` and `src/posthoc.py`; Sect. 7, item 1 says that the plate list and predictions are fixed inputs |
| W4: P_null precision | Abstract and Sect. 4: "about 1e-6", bound 1.8e-5 with the upper 95 % limits; Sect. 8, item 5 |
| W5: the word "candidate"; no MPC report; no inspection | Title, abstract ("We report the four images as candidates. Nobody has examined the glass plates, and no position has been reported to the Minor Planet Center."); Sect. 3.4 last sentence; Sect. 8, items 1 and 2 |
| W6: SkyBoT not in THIRD_PARTY.md, no script | `THIRD_PARTY.md` row; `src/skybot.py`; ref. [skybot]; Sect. 5 keeps "the cause ... is not known" |
| W7: peak distances are not astrometry | Sect. 6, "Position": "within about 4""; "These values are not astrometry"; abstract "within about 4"" |
| W8: Horizons solution and date; no injection test; ac27730 is a failed plate | Sect. 2 (JPL#1545, 2026 Nov 28); Sect. 8, items 6 and 7; Table 1 and Sect. 4 (ac27730 "fail") |

# Rerun from a clean copy

Command (2026-11-28, write stage): copy `release/` to `$TMPDIR/ivarci/ivar-1901-harvard-plates`, make a new venv
(`uv venv --seed --python 3.13`), activate it, then `bash checks/ci.sh`. Output:

```
data dir: /home/deck/research/factory/.tmp/tmp.NUnsdTkQTN
run fetch.py
run measure.py
run decide.py
run controls.py
run posthoc.py b27907 b28342 b28520 b28598
run horizons_check.py
run skybot.py
132 of 132 checks match
cutouts byte-identical to the paper's: 5 of 5; control cutouts: 6 of 6
ci: all checks passed

real	5m3.153s
user	1m16.087s
sys	0m2.113s
exit=0
```

`python3 /home/deck/research/factory/lab-repo/tools/check_result.py $TMPDIR/ivarci/ivar-1901-harvard-plates`: see LOG.md
(write stage) for the output on the final copy.
