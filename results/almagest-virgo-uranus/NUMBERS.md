# Numbers and their sources

All keys refer to `data/expected.json`. `checks/rerun.py` recomputes each of them from a fresh download. "VERIFY" means the independent recomputation of the verification stage (`checks/verify/indep.py`, numbers copied from the verification report; not rerun by `ci.sh`).

## Registered result (Hipparchus window), key `analysis.hipparchus`

| Number in the paper | Value in expected.json | Key |
|---|---|---|
| 266 calibration entries | 266 | `n_C` |
| Δλ = +2.545°, Δβ = +0.022° | 2.54548, 0.02198 | `dL_deg`, `dB_deg` |
| entry in Hipparchus frame (174.705°, +0.145°) | 174.70452, 0.14468 | `e513_frame` |
| R: 103 entries, median 32.1', 95th percentile 88.5' | 103, 32.106, 88.545 | `n_R`, `R_median_arcmin`, `R_p95_arcmin` |
| nearest star 76 Vir, HIP 66098, V = 5.21 | 66098, 5.21 | `r_star_HIP`, `r_star_V` |
| r_star = 63.7', Q_S = 88.3 | 63.727, 88.350 | `r_star_arcmin`, `Q_S` |
| d_U = 36.6', Q_U = 56.3 | 36.565, 56.311 | `d_U_arcmin`, `Q_U` |
| best night JD 1674767.5, elongation 161° | 1674767.5, 161.16 | `d_U_jd`, `d_U_SOT` |
| Uranus on that night 174.704°, +0.754° | 174.70354, 0.75410 | `uranus_at_best` |
| placebo 6 of 108, F = 0.056 | 6, 108, 0.0556 | `n_band_match`, `n_band`, `F` |
| injection max 5e-5' | 5.12e-5 | `injection_max_arcmin` |
| Spearman ρ = 0.93 | 0.9295 | `spearman_vs_VvG` |
| 2491 window days with elongation ≥ 120° | 2491 | `n_uranus_days` |
| verdict inconclusive | INCONCLUSIVE | `analysis.verdict` |

## Ptolemy window (descriptive), key `analysis.ptolemy`

| Number | Value | Key |
|---|---|---|
| Δλ = −1.110°, Δβ = +0.048° | −1.11049, 0.04829 | `dL_deg`, `dB_deg` |
| 76 Vir 63.8', Q = 87.4 | 63.847, 87.379 | `r_star_arcmin`, `Q_S` |
| Uranus 37.7', Q = 56.3, AD 125 Mar 24 | 37.727, 56.311, JD 1766796.5 | `d_U_arcmin`, `Q_U`, `d_U_jd` |
| placebo 8 of 108 | 8 | `n_band_match` |
| epoch JD 1771088.5 = AD 136 Dec 23 | 1771088.5 | `jd0`; calendar from the Horizons file row |

## Exploratory, key `exploratory`

| Number | Value | Key |
|---|---|---|
| 12 of 103 reference entries have a larger error than 76 Vir | 12 | `n_R_ge_76Vir` |
| Uranus latitude near the entry +0.73° to +0.76° | 0.7337, 0.7575 | `uranus_lat_range_near_entry` |
| variant −0;10: Uranus 56.6', 76 Vir 58.7' | 56.565, 58.723 | `variant_south_lat` |
| density ratio 7.0 (limits section; not used as evidence) | 6.971 | `LR_uranus_over_76Vir_density` |

## Post hoc, key `posthoc`

| Number | Value | Key |
|---|---|---|
| 9827 Hipparcos stars; 1028 catalogue entries | 9827, 1028 | `n_hip_stars`, `n_ptolemy_entries` |
| Uranus track longitudes 79.2° to 182.1° | 79.248, 182.089 | `U_lon_range_deg` |
| 31 placebo entries in the track range, 6 match (0.19); 77 outside, 0 match | 31, 6, 0.1935, 0 | `n_band_in_track`, `n_match_in_track`, `F_in_track`, `n_match_outside_track` |
| the 6 matches B432, B456, B469, B485, B491, B502 | same | `match_entries` |
| R: 81 of mag 5, 21 of mag 6, 1 of code 9 (B577) | 81, 21, 1; 577 | `R_VP_counts`, `R_code9_entries` |
| without code 9: Q_S = 88.2, Q_U = 55.9 (102 entries) | 88.235, 55.882 | `no_code9` |
| mag 6 only: Q_S = 81.0, Q_U = 47.6 (21 entries) | 80.952, 47.619 | `mag6_only` |
| 177;00 +0;10: 76 Vir 77.7' (Q 91.3), Uranus 36.4' (Q 56.3) | 77.721, 91.262, 36.445, 56.311 | `lon177_00_lat_p0_10` |
| 177;00 −0;10: 76 Vir 73.7' (Q 90.3), Uranus 56.4' (Q 82.5) | 73.673, 90.291, 56.438, 82.524 | `lon177_00_lat_m0_10` |
| bootstrap Q_S 81.6 to 94.2, Q_U 46.6 to 66.0, Q_S > 95 in 1.2 % | 81.553, 94.175; 46.602, 66.019; 0.0124 | `bootstrap` |
| B513 flag I = 1 with HIP 66098, distance 71.2' (Verbunt–van Gent) | "1", 66098, 71.2 | `e513_I`, `e513_HIP`, `e513_VvG_dist_arcmin` |
| epoch = 129 BC Jul 1; best night = 128 BC Apr 7 | b0129-Jul-01, b0128-Apr-07 | `date_jd0`, `date_best` |
| window 149 BC Dec 31 to 127 BC Dec 31 | b0149-Dec-31, b0127-Dec-31 | `window` |
| 128 BC Mar 25: Uranus 175.24°, +0.757°, elongation 174° | 175.2407, 0.75684, 174.25 | `uranus_m127_mar25` |
| elongation cut 90° or 150°: 36.6'; no cut: 32.4' | 36.565, 36.565, 32.408 | `d_U_by_elong_cut` |
| entry 36.6' south of Uranus | −36.565 | `uranus_dlat_arcmin` |
| 76 Vir offset −58.5' in longitude, +25.3' in latitude | −58.482, 25.319 | `vir76_dlon_arcmin`, `vir76_dlat_arcmin` |

## Numbers from other sources

| Number | Source |
|---|---|
| VERIFY: Δλ = +2.549°, Δβ = +0.021°; R median 32.2', 95th percentile 88.4'; 76 Vir 64.0', Q_S = 89.3; Uranus 36.5', Q_U = 56.3; placebo 6 of 108; largest difference 0.3' | verification report, check 5 |
| VERIFY: bootstrap interval of Q_S 82.5 to 95.1 | verification report, sensitivity table |
| Swerdlow: Uranus 175;12°, +0;45°, elongation 173° on −127 Mar 25; 76 Vir 179;21°, −0;18°; shift −2;40° | Swerdlow 2020, p. 144 and n. 4 |
| Uranus magnitude 5.4 to 6 | Swerdlow 2020, p. 143 |
| registration times 01:02:27, 01:03:00, 01:04:42 | `data/GIT_LOG.txt`; first output time from the verification report, check 2 |
| 120/120 values, 26 to 35 s | `bash checks/ci.sh` in a clean copy, 2026-11-28 (see below) |

## Issues of the verification round and where the paper fixes them

| # | Issue | Fix |
|---|---|---|
| 1 | Placebo rate needs the track-range limit (6 of 31) | Abstract; Section 5 "Placebo inside the track"; Conclusion ("about one in five"); README |
| 2 | "mag 5-6" not exact: 81 + 21 + 1 of code 9 | Section 3.3 (composition, code 9 not confirmed); Section 5 "Reference set" (without B577: 88.2, 55.9); Limits |
| 3 | State Toomer's 177;15 against Hertzog's 177;00, with sensitivity | Section 5 "Longitude Virgo 27°" |
| 4 | "not an outlier" must be "not beyond the 95th percentile"; bootstrap reaches 95.1 | Section 4, first bullet; Section 5 "Sampling error" (own frame 81.6-94.2, verifier frame 82.5-95.1); Conclusion; README |
| 5 | R uses only I = 1; B513 itself has I = 1 with 76 Vir; Swerdlow calls it doubtful | Section 1 (paragraph 3); Section 5 "Identification flag" |
| 6 | One date convention; window 149 BC Dec 31 to 127 BC Dec 31 | Section 2 (convention stated, windows in historical years and JD); Section 3.2 (epoch 129 BC Jul 1); all dates in BC with the astronomical year given once for Hertzog's date |
| 7 | Density ratio 7.0 depends on an 8' window chosen after the result | Not in the result sections; named in Limits as not used as evidence, with the 8' window |
| 8 | Keep the limits: Hertzog not read; ADS citations not checked | Section 1 (paragraph 4); Limits bullet 1; bibliography entry of Hertzog |

## Clean-copy runs (2026-11-28)

Copy of `release/` to `$TMPDIR/ci-avu2/almagest-virgo-uranus`, new venv (`uv venv --seed --python 3.13`), then:

```
$ bash checks/ci.sh
120/120 values match
ci: all checks passed
(exit 0, 26 s wall time; a first run on an earlier copy took 35 s)

$ python3 lab-repo/tools/check_result.py almagest-virgo-uranus
ok: 1 result(s)
```
