# Numbers in the paper and their sources

`E` = `data/expected.json` (reproduced by `checks/rerun.py`). `C` = `data/vatican_corrected.csv`. `V` = `VERIFY.md` of the verify stage (independent astropy code in `checks/independent/`). `R` = `RESULT.md` of the solve stage. `D` = APPLAUSE web pages (THIRD_PARTY.md). `G` = `data/GIT_LOG.txt`.

| Number in paper | Where | Source |
|---|---|---|
| 94,090 plates, 139,539 exposures | Abstract, Sect. 1 | D: DR4 documentation page |
| 18,681 / 93 / 38 / 870 plates; 19,682 in total | Abstract, Sect. 3, Table 2 | E `n_plates_*_swapped`; sum |
| 49.8845, 10.8881, 46.5217, 9.9025, 46.8014, 9.8147, -34.5567, -58.7317 | Sect. 3, Table 2 | E keys of `checks/rerun.py` (exact string match); V check 4 |
| 31 site records; 3 records with no coordinates, 53 plates | Sect. 3 | plate group-by on the rerun download (21 + 26 + 6 = 53); V check 4 |
| Bonn 7.068 E, 50.163 N; 0.57 deg south | Sect. 3 | plate group-by; 50.73 - 50.163 = 0.567 |
| 26 blocks; Table 1 (n, D6, D0, M, placebo) | Sect. 2, Table 1 | E `blocks` |
| +2.60 h, +1.61 h | Sect. 3.1 | P (2.5998, 1.6117); E `blocks` key `Delta_h` in `analyze.py` output |
| Bamberg n = 18,947, D6 0.13 %, 10.7 % shifted, 2,004 vs 7, M = -0.97 h | Abstract, Sect. 3.1 | E `bamberg_*`; V check 5 |
| San Miguel n = 858, D6 0.0 %, 3.5 % shifted, M = -0.07 h | Abstract, Sect. 3.1 | E `sanmiguel_*`, `blocks` |
| Muottas Muragl n = 93, D6 1.1 %, M = -3.25 h, inconclusive | Sect. 3.1 | E `blocks` |
| injection: 0.8 % -> 9.2 %; M -1.26 -> +1.34 h | Sect. 3.1 | E `injection_D6`, `injection_M`, `blocks` (101) |
| placebo D6 50 % to 66 % | Sect. 3.1 | E `blocks` (min 0.496, max 0.655) |
| 12 of 23 control blocks with abs(M) >= 1 h; M from -1.71 to -1.20 h without 4, 5, 501 | Sect. 3.1 | E `blocks` (computed from the table). R says "11 of 21" and "-1.7 h to -0.98 h"; that count is not reproduced, and the paper uses the table. |
| 6.0 % of archive-208 exposures (n = 19,078) with recorded coordinates | Abstract, Sect. 3.1 | E `bamberg_D6_recorded_site`; n from `explore_rules.py` output; V check 5 (0.0602) |
| Vatican n = 544, D6 40.8 %, D0 32.4 % | Abstract, Sect. 4 | E `vatican_n`, `vatican_D6`, `vatican_D0`; V check 7 |
| site 12.6505 E, 41.7472 N | Sect. 4 | plate table (asserted single site in `vatican.py`) |
| ut_mid differs from logged midpoint by at most 0.4 s | Abstract, Sect. 4.1 | V "New controls" (first item) |
| H_B: 222 day -> night, 1 night -> day, D6 0.2 % | Abstract, Sect. 4.1 | E `vatican_HB_b`, `vatican_HB_c`, `vatican_D6_HB`, `vatican_D6_near` |
| H_A: D6 48.7 % | Sect. 4.1 | E `vatican_D6_HA` |
| hour angle 70.2 % vs 27.4 %, 241 vs 8, p = 7e-61 | Sect. 4.2 | E `vatican_frac_HA_*`, `vatican_ha_b`, `vatican_ha_c`, `vatican_ha_p_lt_1e-50`; p = 7.48e-61 from the `hourangle2.py` output (`data/hourangle2.json` of the solve stage) |
| control 101: n = 13,785, difference 0.006, 97 vs 13, p = 5e-17 | Sect. 4.2 | E `control101_ha_*`; n and p = 4.70e-17 from the `hourangle2.py` output |
| 101: H_B moves 107 daylight midpoints to night, 0 back | Sect. 4.2 | E `control101_HB_b`, `control101_HB_c` |
| permuted HA: 63.5 % mean, 65.8 % max (200) | Sect. 4.2 | E `vatican_perm_HA_lt3_mean` (0.6352), `_max` (0.6581); V gives 63.6 % with another seed |
| permuted Sun D6: 41.6 % mean, 38.2 % min (50) | Abstract, Sect. 4.2 | E `vatican_perm_D6_mean`, `_min`; V: 41.4 %, 37.5 % |
| target below 0 deg: 28.1 % DR4, 0.2 % H_B; below 20 deg: 51.3 %, 0.7 % | Abstract, Sect. 4.2 | E `vatican_target_below_*`; V: 28.3 %, 0.2 %, 51.3 %, 0.7 % |
| permuted target below 20 deg: 9.3 % mean, 7.0 % min (1,000) | Abstract, Sect. 4.2 | E `vatican_perm_target_below_20_*`; V: 9.3 %, 7.4 % |
| 322 night exposures; target below horizon 23.9 % vs 0.3 %; median correction 3.6 h; 20 % below 1 h | Sect. 4.2 | E `vatican_n_night_dr4`, `vatican_night_*`; V: 24.5 %, 0.3 %, 3.6 h, 20 % |
| astropy within 0.6 percentage points | Sect. 4.2 | largest difference: 24.5 - 23.9 (V vs E) |
| 543 dated, 1951 May 19 to 1953 Dec 26; exposure 139402, plate 96272 | Abstract, Sect. 4.3 | E `vatican_n_dated`, `vatican_first_date`, `vatican_last_date`, `vatican_placeholder_exposure_id`; C |
| median correction 4.9 h, max 11.8 h, 98.2 % above 10 min | Abstract, Sect. 4.3 | E `vatican_median_abs_correction_h`, `_max_`, `vatican_frac_dated_correction_gt_10min` |
| 222 of 544 records differ by one sidereal day between rules; both D6 0.2 % | Sect. 4.3 | E `vatican_n_near_vs_same_differ_by_a_day`, `vatican_D6_same`; V: 225 (UT date of jd_mid) |
| exposure 139045, plate 95915, Sun +50 deg | Sect. 4.3 | C (sun_alt_nearest_deg 49.8) |
| 542 of 543 at night under H_B | Sect. 7 | E `vatican_D6_near` x 544 = 1 |
| 1951-1999 in the archive paper | Sect. 4.3 | Enke et al. 2024, arXiv:2404.17355 Table 1 (pdftotext); V issue W2 |
| Potsdam 4: n = 98, D6 27.6 %; 5: n = 61, 67.2 %; H_A and H_B do not lower D6 (ut_mid decade counts: 4: 2 in 1940s, 40 in 1950s, 56 in 1960s; 5: 61 in 1950s) | Sect. 5 | E `potsdam4_D6`, `potsdam5_D6`, `blocks`, `potsdam4_explore` [0.31, 0.586, 0.31], `potsdam5_explore` [0.672, 0.902, 0.672] |
| Hamburg 102: 7.8 %, 110: 8.0 % | Sect. 5 | E `blocks` |
| 70 values compared | Sect. 6 | `len(data/expected.json)` |
| commit 53538d8 09:22:22, 1b7f1f7 09:24:02, 3d66c29 | Sect. 3.1, 4.2, 6 | G |
| astropy 8.0.3 | Sect. 6 | V check 5 |

# Issues of VERIFY.md (round 1) and their fixes

| Issue | Fix | Place |
|---|---|---|
| W1: all 543 dated exposures are affected, not only 222; list must cover all | The paper states that the sidereal reading changes all 543 dated midpoints (one, exposure 139045, stays in daylight) (median 4.9 h, 98.2 % above 10 min), including the 322 that DR4 puts at night. `data/vatican_corrected.csv` lists all 544 records. | Abstract; Sect. 4.2 (third post hoc control); Sect. 4.3; README |
| W2: date range 1951-1999 is wrong; name the placeholder record | Range 1951 May 19 to 1953 Dec 26; record 139402 / plate 96272 named as a placeholder; the archive paper's 1951-1999 explained. | Abstract; Sect. 4.3; CSV `note` column |
| W3: one-sidereal-day ambiguity; state the rule | The nearest rule and the same-UT-date rule are both defined and both given in the CSV; 222 differ by one sidereal day; D6 is the same; no result depends on the choice. | Sect. 4.3; checks/README.md |
| W4: p = 7e-61 is not the strength of evidence; add permutation controls, label post hoc; report 97 vs 13 | Sect. 4.2 says so, gives the permutation value 63.5 %, adds the Sun, target-altitude and night-subset controls under "post hoc", and reports 97 vs 13 (p = 5e-17) for Hamburg 101. | Sect. 4.2 |
| W5: claim 2 holds only for Bamberg and San Miguel; say "read as UT" | Abstract and Sect. 3.1 limit the verdict to Bamberg and San Miguel, give Muottas Muragl as inconclusive and Schatzalp as not tested. The paper says "DR4 read the logged value as UT". | Abstract; Sect. 3.1; Sect. 4.1 |
| W6a: protocol header time | The paper gives the commit time 09:22:22 and says the commit time is the evidence. PROTOCOL.md is not changed. | Sect. 3.1; Sect. 6 |
| W6b: Addendum 3 text and result in one commit | Stated. | Sect. 4.2 |
| W6c: committed `__pycache__` | Removed from the problem repository; not in `release/`. | git |
| W6d: DR4 licence | CC0 1.0, read on the DR4 landing page on 2026-11-27. | THIRD_PARTY.md |
| W6e: Vatican logbooks not seen | Stated as a limit; the sidereal reading is an inference, not confirmed. | Sect. 7 |
