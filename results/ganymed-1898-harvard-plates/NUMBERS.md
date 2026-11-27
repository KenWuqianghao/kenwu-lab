# Numbers in the paper and their sources

`E` = `data/expected.json` (reproduced by `checks/rerun.py`; key given). `R` = `RESULT.md` of the solve stage. `V1` = verification round 1 (`git show 19daea5:VERIFY.md` in the problem repository), `V2` = verification round 2 (`VERIFY.md`, commit 49358e0); the check number follows. `P` = `PROTOCOL.md`. `G` = `data/GIT_LOG.txt` and `data/cutouts/log.jsonl`. `W` = sources opened in the write stage (SBDB API, crossref, arXiv API, doi.org, 2026-11-27).

## Introduction and data

| Number in paper | Where | Source |
|---|---|---|
| Ganymed discovered 1924 Oct 23, Baade, Bergedorf, A924 UB; `first_obs` 1924-10-23 | Abstract, Sect. 1 | W: `sbdb.api?sstr=1036&discovery=1`; V1 check 1 |
| MPC earliest Ganymed observation 1924 Oct 23.809 | Sect. 1 | V1 check 2 (1924 10 23.80940) |
| MP3C years observed 1924-2023 | Sect. 1 | `PRIOR_ART.md` |
| Hektor discovered 1907 Feb 10, Kopff, Heidelberg, A907 CF; `first_obs` 1907-02-11 | Abstract, Sect. 1 | W: `sbdb.api?sstr=624&discovery=1`; V2 check 1 |
| 4 Trojans with `first_obs` before 1907 Mar 1; Chersidamas 1904-09-13; Achilles, Patroclus | Abstract, Sect. 1 | `PRIOR_ART.md`; V2 check 1; W: `sbdb.api?sstr=12126` |
| MPC: Hektor 1907 Feb 11.021, Chersidamas 1904 Sep 13.174, nothing earlier | Sect. 1 | V2 check 2 (1907 02 11.0208, 1904 09 13.17427) |
| 26 years | Title, abstract | 1924 - 1898 |
| 835 x 835 px, 1.44"/px | Sect. 2 | `src/stamps.py` (835-px grid, 1.44"/px) |
| sites 800, 802, 024 | Sect. 2 | `src/plates.py`, `src/hdap.py` |

## Method

| Number in paper | Where | Source |
|---|---|---|
| c64fc2c 14:07:44; first request 14:07:49 | Table 1 | G (commit; log entry 1, 13:07:49Z); V1 check 3 |
| 907bdc5 14:28:05; first request 14:28:05 | Table 1 | G (commit; log entry 12, 13:28:05Z); V1 check 3 |
| a01e3ff author 15:00:43, committer 16:01:23; 69a64b8; first cutout 15:01:22 | Table 1 caption | G; V2 check 5 |
| 6 Ganymed plates, 5 Hektor plates; magnitude rule 0.3, B-V 0.8 | Sect. 3.2 | `src/plates.py` |
| 5-min steps, -2 h to +2 h; Sun below -24 deg | Sect. 3.2 | P "Predictions (fixed)" |
| Gaussians 1.5 and 15 px; buffers 15"/10"; thresholds 10/6; 300 regions at 90"-420"; P < 1e-3 | Sect. 3.3 | `src/measure.py` (`zimage`, docstring); P |
| round 2: 8 plates, 5", 2000 points, p_comb < 1e-3 and 2 plates p < 0.01 | Sect. 3.4 | P "Round 2"; `src/measure2.py` |
| 18 of 3857 plates; 3 removed (< 0.1 deg); 15 | Sect. 3.4 | P "Round 3" |
| G2392 header UT vs ST 45 min | Sect. 3.4, Sect. 7 | P "Round 3" |
| time shift -60..+60 min; 2000 translations 90"-600" | Sect. 3.4 | P "Round 3"; V2 check 7 |
| i21780 prediction 5 min late, 5.5" | Sect. 3.5 | P Addendum 4; V1 check 8 |
| region / box methods; lim - 1, lim + 0.3; 11 x 11 px; shift below 6 stars | Sect. 3.6 | P Addenda 3 and 4; R "Astrometry" |

## Ganymed

| Number in paper | Where | Source |
|---|---|---|
| S = 23.3, 3.6, 33.1, 16.0, 9.3, 5.4; p0 = 0.043, 0, 0.163, 0.030, 0.023, 0 | Abstract, Table 2 | E `r1.<plate>.S`, `r1.<plate>.p0`; `data/prereg/results.json` (identical S except i21780 16.004 vs 15.98, both 16.0) |
| V, limit, exposure, midpoints | Table 2 | `src/plates.py`; `data/results.json` (V) |
| P = 5.07e-4 (5.1e-4) | Abstract, Sect. 4 | E `r1.Ganymed.P_null`; V1 check 7 |
| P = 6.25e-4 with floor 1/300 | Sect. 4 | E `r1.Ganymed.P_null_p0_floor_1_300`; V1 check 7 (0.00062) |
| positions and O-C (Table 3); 0.36"-2.36"; time offsets -2.0 to +1.3 min | Abstract, Table 3, Sect. 4 | E `ast.region.<plate>.*` |
| box O-C 1.26, 0.92, 3.12, 4.24, 1.06; time offsets -4.8 to +2.3 min | Sect. 4 | E `ast.box.<plate>.o_c_total_arcsec`, `.time_offset_min` |
| ac00115 box 16" vs 52" trail | Sect. 4 | R "Astrometry"; E `shape.ac00115.trail_length_arcsec` = 52 |
| variants 2.36-13.47, 0.36-1.59, 1.66-2.40, 1.28-1.50, 1.65-1.91 | Abstract (2.4"-13.5"), Sect. 4 | E `astvar.<plate>.o_c_min_arcsec`, `.o_c_max_arcsec` |
| centroid shifts i21050 by up to 11" | Sect. 4 | R "Astrometry" |
| Horizons 3-sigma below 0.7" RA, below 0.2" Dec | Sect. 4 | V1 check 11 (0.14"-0.69", 0.02"-0.19") |
| separation 97.0 deg | Abstract, Sect. 4 | E `ast.max_separation_deg` |
| no catalogued star brighter than 13.8 mag within 30" | Sect. 4 | V1 check 14 (13.82 mag at 29.9") |
| four control plates, max z 1.5-2.3 within 17" | Sect. 4 | V1 check 13 |
| shapes: trail 11", 15", 9"; i21576 39" PA 72 vs 35" PA 69; ac00115 54" PA 10 vs 52" PA 19; 1 and 3 comparison stars; i21050 stars 43" PA 28 | Sect. 4, Fig. 1 caption | E `shape.<plate>.*` |
| ac00044: 189" trail, star images about 20" | Sect. 4 | R "The other three plates" |
| i22152 O-C 1.9" | Sect. 4 | E `ast.region.i22152.o_c_total_arcsec` = 1.91 |

## Hektor

| Number in paper | Where | Source |
|---|---|---|
| round 1: 2 of 5 pass, b28276 1901 Aug 23, b28503 1901 Sep 10, P = 0.029 | Table 4 | E `r1.Hektor.k_pass`, `r1.Hektor.P_null`, `r1.b28276.pass`, `r1.b28503.pass`; date of b28503 from `src/plates.py` (1901-09-10T05:53). R gives "1901-09-24" for b28503; that is a typo in R. |
| round 2: p_comb = 0.0028, no plate p < 0.01; a06535 not covered, b23969 masked; 6 measurable | Table 4 | E `r2.p_comb`, `r2.<plate>.measurable`; P Addendum 2 |
| round 3 table: start, exposure, trail, fit stars, S, p | Table 5 | E `r3.<plate>.S`, `r3.<plate>.p`; `data/hdap/results.json` (start, exposure from `hektor_cover.csv`, trail); R table (fit stars) |
| set A p_comb = 1.49e-5 (1.5e-5), 3 plates p < 0.01; set B 3.2e-6; G3623 0.011 | Abstract, Sect. 5 | E `r3.A_before_1904-09-13.*`, `r3.B_all.p_comb`, `r3.G3623.p` |
| factor 3: 4.5e-5 | Sect. 5 | 3 x 1.49e-5; P Addendum 6 |
| B262a HTTP 204 | Sect. 5 | P Addendum 5 |
| verifier p 0.0087, 0.0232, 0.0402; without shift 0.0060, 0.0125, 0.0167 | Abstract (0.009, 0.023, 0.040), Table 5, Sect. 5 | V2 check 9 |
| verifier trail-mean z 2.35, 1.35, 1.56; 13-18 stars, rms 2.2"-2.7"; 4000 translations | Sect. 5 | V2 check 9 |
| Fisher 6.6e-4, 8.3e-4; without shift 1.3e-4, 2.0e-4 | Abstract, Sect. 5 | V2 check 15 |
| 4.6 to 6.2 times larger | Sect. 7 | 0.0087/0.0015 = 5.8, 0.0232/0.0050 = 4.6, 0.0402/0.0065 = 6.2 |
| profile maxima -20, +10, +5 min; widths 60-100 min; 1.5 to 2.4 times | Sect. 5 | V2 check 11 and issue 4 (0.0087/0.0060 = 1.45, 0.0232/0.0125 = 1.86, 0.0402/0.0167 = 2.41) |
| pixel scales 2.555" and 2.503"; started 5 s apart | Sect. 5 | V2 issue 5; `data/hdap/results.json` (22:11:20 and 22:11:25) |
| motion check z and fractions; 326" | Sect. 5 | E `motion.*` |
| controls: 6 plates, 18 values -0.70 to 1.09, smallest p 0.086 | Sect. 5 | V2 check 13 |
| stars 19.0 and 19.2 mag at 11" and 14"; 16.5 mag star peak z about 2 | Sect. 5 | V2 check 12 |
| cross-track 4" steps, half maximum at 12" | Sect. 5 | V2 check 10 |
| G2283 92 min after G2281; -112 min; 0.2 vs 1.6 | Sect. 5 | V2 check 11 |
| brightness 1.3, 1.0, 2.0 (15.0 mag); 3.5, 2.2, 4.2 (14.0 mag); V = 14.5 | Sect. 5 | V2 check 14 |
| trail-mean z 1.4 to 3.0 | Sect. 7 | E `r3.G2282.S` = 1.35, `r3.G2281.S` = 2.99 |

## Checks

| Number in paper | Where | Source |
|---|---|---|
| 295 values; 295 of 295 match from a clean copy | Sect. 6, README | write-stage run of `bash checks/ci.sh` on a clean copy of `release/` (log: `checks/out/ci_clean_copy.log` in the problem repository); V2 check 3 |
| 18 DASCH and 14 HDAP cutouts byte-identical | Sect. 6 | V2 check 4; write-stage CI run (`32 of 32`) |
| verifier Ganymed peak z 8.8-20, 3.4; O-C 3.0, 0.6, 2.3, 2.6, 2.1; within 1.3" | Sect. 6 | V1 check 12; V2 round-1 issue 2 |
| 64 outcomes | Sect. 6 | V1 check 7 |
| about 15 min | Data and code | write-stage CI run (see README "Check it") |

## Open issues of the last verification (V2) and where the paper fixes them

| Issue (V2) | Fix |
|---|---|
| 1. Hektor is a candidate; give both sets of p values | Title ("a candidate image of (624) Hektor"); abstract (both sets, "candidate detection only"); Table 5 (column "p (verifier)"); Sect. 5 "How much the result depends on the analysis"; Sect. 7. README introduction says "candidate only". |
| 2. Evidence for the round-3 registration time | Table 1 and its caption: author date 15:00:43 is the registration time, original commit 69a64b8 in the separate copy, first cutout 15:01:22, cherry-pick committer date 16:01:23. `data/GIT_LOG.txt` has both dates. |
| 3. Add the checks that make the Hektor claim stronger | Sect. 5 "Checks made after the result": control plates of 1902-1903, catalogued stars, cross-track profile, fixed vs moving source on G2283, brightness. All marked as verification-stage checks made after the result. |
| 4. Time shifts | Sect. 5 "Time shifts": profile maxima -20, +10, +5 min, widths 60-100 min, no measurable clock offset, p 1.5 to 2.4 times larger with the search. Sect. 7 no longer says the search "absorbs" the offset. |
| 5. G2281 and G2282 | Sect. 5 "Same night, two lenses": different pixel scales and star fits, two glass plates, independent grain noise, common light still possible. |
| 6. Records (MPC, title) | Sect. 1: the MPC list has no Hektor observation before 1907 Feb 11.021. Title and abstract keep Ganymed as the main claim and Hektor as the second, weaker claim. `PRIOR_ART.md` in the problem repository is updated in the same commit. |
