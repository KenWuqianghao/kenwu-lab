# Numbers in the paper and their sources

Every held-out number below comes from `data/expected.json` (written by `checks/rerun.py`, reproduced by `bash checks/ci.sh` on a clean copy, 2026-11-28: `MATCH expected.json`). A percentage is the quotient of the two counts named. Each row was checked by a script that evaluates the key or the quotient and prints it in the paper's format; every value equals the text.

## Held-out numbers (MLB 2009–2025)

| Number in the paper | Source (key in `expected.json`) | Place |
|---|---|---|
| 5,447 eligible batter-seasons | `n_eligible` | Abstract, §3.1, §4 |
| 5,446 of 5,447 agree with MLB Stats API | `validation_mlb_api.n_compared` − `.n_mismatch` | Abstract, §4 |
| 0 of 4,082 differ from Lahman | `validation_lahman` | §4 |
| Luis Gonzalez (`gonzl005`) 2022: 79 vs 78 H, 311 AB; .254 | `validation_mlb_api.mismatches[0]`; 79/311 | §4 |
| 81 PAs changed by rule 9.15(b) | `n_rule_9_15b_reassigned` | §2 |
| 80 batter-seasons differ from Lahman without the rule; verifier parser 86 reassignments, 2 mismatches | `VERIFY.md` round 1 and round 2 (`checks/verify/out_no_fix.txt`, `out_rule_9_15b_fix.txt`) | §2, §4 |
| 47 at .300, 20 at .299; 0.86%, 0.37% | `T1.300.n_x0`, `T1.300.n_x9`; /5,447 | Abstract, §3.1 |
| ratio 2.35, CI 1.37–4.19 | `T1.300.ratio`, `T1.ratio_ci95` | Abstract, §3.1 |
| p = 0.00065 | `T1.binom_p_300_vs_299` (0.000654) | Abstract, §3.1 |
| .330: 8 vs 3, ratio 2.67 | `T1.330` | Abstract, §3.1, Table 1 |
| Table 1 (all counts and ratios), .349/.350 empty | `T1.250` … `T1.350` | Table 1, Figure 1a |
| MLB totals alone: 47 vs 20, 8 vs 3 | `S1_T1_official` | §3.1, §4 |
| P1: 44 vs 70; 0.81% vs 1.29%; p = 0.0094 | `paper_comparisons.P1_end_298_299_vs_300_301` | §3.1 |
| 23 last PAs at .299, 3 walks, 13.0% | `L299.PA`, `L299.BB` | Abstract, §3.2 |
| Fielder 2009, 2011; Diaz 2024 | `L299_walkers` (`fielp001`, `diazy004`; names from the Chadwick register) | §3.2 |
| p = 0.019 (0 of 61 vs 3 of 23) | `C2_original_0_of_61_vs_heldout_fisher_two_sided` (0.0186) | §3.2 |
| LC 89/1,092 = 8.2% | `LC.BB`, `LC.PA` | §3.2 |
| T2 p = 0.89 | `T2_fisher_p` (0.886) | Abstract, §3.2 |
| 8 for 19 (.421), 4 for 20 (.200), T3 p = 0.125 | `L299`, `L300`, `T3_fisher_p` | Abstract, §3.2 |
| T4: 62 for 217 (.286), 14 for 67 (.209), p = 0.139 | `T4_B_below`, `T4_A_above`, `T4_hit_fisher_p` | §3.3 |
| T4 walks: 19/242 = 7.9%, 5/74 = 6.8%, p = 0.70 | `T4_*.BB`, `T4_*.PA`, `T4_walk_fisher_p` | §3.3 |
| P2: 16/58 (27.6%) vs 8/55 (14.5%), Holm 0.21, Z 1.69 (0.090) | `paper_comparisons.P2_hit_298_299_vs_300_301` | Table 2, Figure 1b |
| P3: 8/23 (34.8%) vs 229/1,112 (20.6%), Holm 0.21, Z 1.66 (0.097) | `paper_comparisons.P3_hit_299_vs_others` | Table 2 |
| P4: 3/58 (5.2%) vs 2/55 (3.6%), Holm 0.80, Z 0.40 (0.69) | `paper_comparisons.P4_walk_298_299_vs_300_301` | Table 2, Figure 1b |
| P5: 1/58 (1.7%) vs 11/55 (20.0%), Holm 0.006, Z −3.15 (0.0016) | `paper_comparisons.P5_sub_298_299_vs_300_301` | Table 2, §3.4, Figure 1b |
| P6: 9/30 (30.0%) vs 63/1,105 (5.7%), Holm 0.0002, Z 5.39 (7×10⁻⁸) | `paper_comparisons.P6_sub_300_vs_others` (Holm 0.000246) | Abstract, Table 2, §3.4 |
| 30% of last scheduled PAs at .300 are substitutions (P3 caveat) | P6: 9/30 | §3.4 |
| Exit: 38 of 105 (36.2%); 17.1%–26.1% at .297–.303 except .300 | `exit_share_batter` (.297 26.1, .298 20.4, .299 17.1, .301 18.6, .302 23.5, .303 23.5) | §3.5 |
| 17 Retrosheet files, about 133 MB of downloads | `retrosheet_sha256`; `RESULT.md` (download size) | §4, README |
| 23 to 30 last PAs at .299 and .300 | `L299.PA` = `L300.PA` = 23; P6 n1 = 30 (scheduled at .300); P3 n1 = 23 | §5 |
| Run time 125 s | clean-copy `bash checks/ci.sh`, fresh venv, 2026-11-28 (this stage); 258 s in `VERIFY.md` round 2 | README, `checks/README.md`, §4 ("about 2 to 5 minutes") |

## Numbers of the original paper and of earlier work

| Number | Source |
|---|---|
| 8,817 player-seasons; 1.40% vs 0.38%; "nearly 4 times"; 0.97% vs 2.30% | Pope and Simonsohn (2011), Study 1, full text (archive URL in the paper) |
| 35.2% vs 22.4%; 43% vs 22.8%; 2.5% vs 8.6%; 0 of 61; 4.1% vs 19.7%; 34.3% vs 7.0%; note 4 | same, Study 1 and note 4 |
| ratio 3.7 | 1.40/0.38 |
| .299 (155/517), .297 (43/145); "sampling bias fully accounts…" | Scott and Birnbaum, SABR web page (read 2026-11-28) |
| "supported Pope and Simonsohn (2011)"; seasons from 1957 | Tanji (2021), PDF read 2026-11-28 |
| 22 for .299, 57 for .300, 2005–2018 | Nakamura (2019), PDF read in solve round 2 |
| 1920–2022; "essentially confirm…"; "significant chronological effect" | Krabbenhoft, SABR Baseball Records Committee newsletter, Summer 2023, PDF read 2026-11-28 |
| Lombardi blog post, 1 October 2011 | Title, author, date and URL from a web search on 2026-11-28; the page body was behind a Cloudflare check and was not read. `PRIOR_ART.md` (sprint) names the same post. |
| 131 citing papers | `PRIOR_ART.md` (Semantic Scholar) |

## VERIFY.md (round 2) issues and where the paper fixes them

| # | Issue | Fix |
|---|---|---|
| 1 | C1 is a re-test | Abstract ("is a re-test: three earlier studies re-tested it, and one already reports a smaller ratio for 2005–2018"); §1 paragraph 3 ("So our season-end result is a re-test"); §3.1 title "(T1, re-test)"; README bullet "(a re-test)". The new parts are listed in §1 paragraph 4. |
| 2 | Substitution result is post hoc, exploratory everywhere | Abstract ("In a post hoc, exploratory analysis"); §2 "Post hoc comparisons"; §3.4 title and last sentence; Table 2 caption; Figure 1 caption; §5 item 2; §6; README bullet and figure caption; `result.json` summary ("post hoc"). The word "replicates" is not used for it. |
| 3 | P3 includes .300 in the comparison group | §3.4: "The P3 comparison group follows the paper's design and includes batters at .300; … So a part of the P3 gap can come from substitution." |
| 4 | Exit check has no test; batters counted at more than one value; exact T4 group A | §3.5: "This check has no test. One batter can count at more than one value, so the groups overlap."; §2 T4 definition: "Group A: the displayed average is .300 or more, and an out would drop it below .300." |
| 5 | Run time approximate; MLB API values can change | README "Check it" (125 s here, "expect about 2 to 5 minutes", MLB corrections paragraph); `checks/README.md` (125 s and 258 s); §4 "about 2 to 5 minutes"; §5 item 5. |

## Correction of the record

`PRIOR_ART.md` names the Krabbenhoft abstract as part of the SABR Statistical Analysis Committee newsletter. The PDF is the SABR Baseball Records Committee newsletter, Summer 2023 (editor Trent McCotter). The paper cites the correct newsletter.
