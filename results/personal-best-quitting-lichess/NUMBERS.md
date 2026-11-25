# Numbers in the paper and their sources

`python3 checks/paper_numbers.py` checks each row of table 1 automatically: it formats the source value as the paper prints it and finds the text in `paper/paper.tex`. It also checks that `data/results.json` and `data/addendum/addendum.json` equal `data/expected.json`, which `checks/rerun.py` reproduces from the raw data. Last run: 77 numbers, 0 mismatches.

## 1. Numbers checked by script

| Quantity | Text in the paper | Source |
|---|---|---|
| primary jump | `$+0.51$` | `data/results.json primary.jump` |
| primary SE | `(standard error 0.45` | `primary.se` |
| primary CI | `$[-0.38, +1.39]$` | `primary.ci` |
| primary left limit | `18.55\%` | `primary.left_limit` |
| primary relative | `$+2.7\%$` | `primary.relative` |
| primary n | `$n = 185{,}385$ (14,903 players)` | `primary.n, players` |
| MDE | `& 1.26 &` | `injection.mde_80pct_power` |
| sample size | `10,755,282` | `sample.blitz_after_pb_filter` |
| new PBs | `37,391` | `sample.blitz_new_pb_events` |
| players | `26,722` | `sample.blitz_players` |
| round number | `$+2.83$ & 0.10 & $z = 28.6$; relative $+23.5\%$; $n = 3{,}406{,}437$` | `round_number` |
| injection | `$+5.17$ & 0.48 & returned addition $+4.66$~pp` | `injection` |
| placebo PB-50 | `Placebo PB$-50$ & $-0.04$ & 0.15 & $z=-0.26$` | `placebo.PB-50` |
| placebo PB-35 | `Placebo PB$-35$ & $+0.09$ & 0.18 & $z=0.48$` | `placebo.PB-35` |
| placebo PB-25 | `Placebo PB$-25$ & $+0.13$ & 0.20 & $z=0.62$` | `placebo.PB-25` |
| placebo PB+10 | `Placebo PB$+10$ & $+2.45$ & 1.31 & $z=1.88$` | `placebo.PB+10` |
| shuffle | `mean $+0.24$, SD 0.38; $p=0.28$` | `shuffle` |
| balance gain | `($-0.29$ points, $z=-2.37$)` | `balance.gain` |
| balance oppdiff | `$-13.9$ points, $z=-4.38$` | `balance.oppdiff` |
| balance log_idx | `$+0.054$, $z=3.74$` | `balance.log_idx` |
| balance prior_games | `$+69.6$ prior blitz games, $z=3.90$` | `balance.prior_games` |
| balance log_prev_gap | `($z=0.44$)` | `balance.log_prev_gap` |
| robustness quit_24h | `Quit = no new game within 24 h (left limit 3.84\%) & $+0.12$ & 0.22 \\` | `robustness.quit_24h` |
| robustness quit_90min_start_to_start | `Quit = next start more than 90 min after this start & $+0.54$ & 0.44 \\` | `robustness.quit_90min_start_to_start` |
| robustness h10 | `Bandwidth $h = 10$ & $+0.49$ & 0.53 \\` | `robustness.h10` |
| robustness h25 | `Bandwidth $h = 25$ & $+0.92$ & 0.39 \\` | `robustness.h25` |
| robustness no_tournament | `Without tournament games & $+0.52$ & 0.52 \\` | `robustness.no_tournament` |
| robustness gain_covariate | `Rating gain as a covariate & $+0.54$ & 0.45 \\` | `robustness.gain_covariate` |
| robustness bullet | `Bullet & $+0.53$ & 0.37 \\` | `robustness.bullet` |
| robustness classical | `Classical & $+0.19$ & 0.65 \\` | `robustness.classical` |
| 24 h left limit | `(left limit 3.84\%)` | `robustness.quit_24h.left_limit` |
| adjacent bins | `Adjacent bins, $x=0$ versus $x=1$ & $+0.81$ & 0.69 \\` | `robustness.adjacent_bins_x0_x1` |
| adjacent bin rates | `18.46\% at $x=0$ and 19.27\% at $x=1$` | `robustness.adjacent_bins_x0_x1` |
| adjacent upper bound | `2.17~pp (adjacent bins)` | `robustness.adjacent_bins_x0_x1` |
| period A row | `$+0.51$ (0.45) & $[-0.38, +1.39]$` | `data/addendum/addendum.json A.primary` |
| period B row | `$+0.88$ (0.32) & $[+0.25, +1.52]$` | `addendum.json B.primary` |
| period B left, n | `left limit 19.86\%; $n=407{,}350$ (37,708 players)` | `addendum.json B.primary` |
| B-A row | `$+0.37$ (0.55) & $[-0.71, +1.46]$` | `addendum.json difference_B_minus_A` |
| period B relative | `$+4.4\%$ relative` | `period_B.json primary.relative` |
| period B primary | `Primary ($h=15$) & $+0.88$ & 0.32 & 2.73 \\` | `data/addendum/period_B.json primary` |
| period B h10 | `Bandwidth $h = 10$ & $+0.59$ & 0.39 & 1.49 \\` | `period_B.json robustness.h10` |
| period B h25 | `Bandwidth $h = 25$ & $+1.18$ & 0.27 & 4.34 \\` | `period_B.json robustness.h25` |
| period B quit_24h | `Quit = no new game within 24 h & $+0.19$ & 0.15 & 1.28 \\` | `period_B.json robustness.quit_24h` |
| period B quit_90min_start_to_start | `Quit = next start more than 90 min after this start & $+0.94$ & 0.32 & 2.97 \\` | `period_B.json robustness.quit_90min_start_to_start` |
| period B no_tournament | `Without tournament games & $+0.86$ & 0.36 & 2.39 \\` | `period_B.json robustness.no_tournament` |
| period B gain_covariate | `Rating gain as a covariate & $+0.90$ & 0.33 & 2.77 \\` | `period_B.json robustness.gain_covariate` |
| period B bullet | `Bullet & $+1.48$ & 0.37 & 3.99 \\` | `period_B.json robustness.bullet` |
| period B classical | `Classical & $+1.11$ & 0.43 & 2.59 \\` | `period_B.json robustness.classical` |
| period B adjacent bins | `Adjacent bins, $x=0$ versus $x=1$ & $+1.11$ & 0.49 & 2.27 \\` | `period_B.json robustness.adjacent_bins_x0_x1` |
| period B placebo PB-50 | `Placebo PB$-50$ & $-0.27$ & 0.11 & $-2.51$ \\` | `period_B.json placebo.PB-50` |
| period B placebo PB-35 | `Placebo PB$-35$ & $-0.08$ & 0.13 & $-0.66$ \\` | `period_B.json placebo.PB-35` |
| period B placebo PB-25 | `Placebo PB$-25$ & $+0.16$ & 0.15 & 1.07 \\` | `period_B.json placebo.PB-25` |
| period B placebo PB+10 | `Placebo PB$+10$ & $-0.50$ & 0.87 & $-0.57$ \\` | `period_B.json placebo.PB+10` |
| period B round_number | `Round-number control & $+3.46$ & 0.07 & 47.86 \\` | `period_B.json round_number` |
| period B injection | `Injected 4.5~pp step & $+5.53$ & 0.34 & 16.38 \\` | `period_B.json injection` |
| period B shuffle | `($p<0.005$)` | `period_B.json shuffle.p_two_sided` |
| period B balance | `(gain $z=-4.38$, opponent rating difference $z=-3.44$, prior blitz games $z=3.09$, log game index $z=3.39$)` | `period_B.json balance` |
| independent primary | `$+0.5083$~pp (SE 0.4509)` | `checks/independent/rdcheck_2013_2015.log` |
| independent period B | `$+0.8833$~pp (SE 0.3235)` | `checks/independent/rdcheck_period_B.log` |
| independent round number | `$+2.8344$~pp` | `checks/independent/rdcheck_2013_2015.log` |
| independent counts | `90,085,152 player-games, 917 self-play games` | `checks/independent/stream_2013_2015.log` |
| no RatingDiff | `447,358 player-games (0.5\%)` | `checks/independent/stream_2013_2015.log` |
| games | `45,043,493 games` | `checks/independent/stream_2013_2015.log` |
| round number 2013 | `$+0.38$~pp (SE 0.39) in 2013` | `checks/independent/extra_2013_2015.log` |
| round number 2014 | `$+1.54$ (0.17) in 2014` | `checks/independent/extra_2013_2015.log` |
| round number 2015 | `$+3.42$ (0.12) in 2015` | `checks/independent/extra_2013_2015.log` |
| variant: ALT PB (max of pre and post) | `($+0.46$~pp, SE 0.47)` | `checks/independent/rdcheck_2013_2015.log` |
| variant: ALT r (next blitz pre) | `($+0.52$~pp, SE 0.45)` | `checks/independent/rdcheck_2013_2015.log` |
| variant: rows with confirmed r | `($+0.56$~pp, SE 0.45)` | `checks/independent/rdcheck_2013_2015.log` |
| extra: primary + covariates | `it is $+0.65$~pp (0.46)` | `checks/independent/extra_2013_2015.log` |
| extra: player fixed effects | `it is $+0.24$~pp (0.44)` | `checks/independent/extra_2013_2015.log` |
| primary by year 2013 | `$+2.42$~pp (SE 2.03) in 2013` | `checks/independent/rdcheck_2013_2015.log` |
| primary by year 2014 | `$+1.31$ (1.05) in 2014` | `checks/independent/rdcheck_2013_2015.log` |
| primary by year 2015 | `$+0.15$ (0.51) in 2015` | `checks/independent/rdcheck_2013_2015.log` |
| 2015 rows in bandwidth | `143,186 of 185,385` | `rdcheck_2013_2015.log` |
| rating chain | `96.1\% of cases in 2013, 95.5\% in 2014 and 98.5\% in 2015. In 3.4\%, 4.1\% and 1.3\%` | `checks/independent/stream_2013_2015.log` |
| round-number bins | `12.07\% at ratings that end in 99 and 14.58\% at ratings that end in 00` | `checks/independent/rdcheck_2013_2015.log` |

## 2. Other numbers (checked by hand)

| Number in the paper | Source |
|---|---|
| 4.5 pp, 20%, 3.5 pp (ratings ending in 01 vs 99), 133 million games, 1 h quit rule, 200 games, 20 games, computer accounts excluded | Anderson & Green full text, Europe PMC XML PMC5828569 (string search in this session and in VERIFY.md check 1) |
| "∼1 percentage point" (effort sentence) | same |
| 36 works (Semantic Scholar), 40 works (OpenAlex) | PRIOR_ART.md table rows 1-2 |
| Bobev record posted 2026-11-03, deleted 2026-11-09, reason "retracted" | prior_art/zenodo_23921614_tombstone.json; PRIOR_ART.md section 3 |
| Bobev round-number range 1200 to 2100 | PRIOR_ART.md section 3 |
| Protocol commit 03:00 CET; first outcome file 13 min later; 917 self-play games; addenda A and B | VERIFY.md check 2; `git log` of the problem repository (`60b7e1f`, `cc343da`, `ccd1822`) |
| End of 2015-12 file 2015-12-31 22:59:57 UTC; window 23 h | VERIFY.md check 4 and issue W6 |
| 48 files, about 22 GB; rerun 44 min and about 53 min; 0 mismatches | RESULT.md "Rerun record"; data/rerun_log.txt; checks/independent/rerun_clean_clone.log; VERIFY.md check 3 |
| lila commits 5e9fde4a (2015-12-26), 4dacb459 (2016-01-10) | VERIFY.md check 9 (GitHub API) |
| Figure: quit rate about 15.5% at x = -30, about 18.5% at x = 0 | data/results.json bins_blitz: -30 → 15.53%, 0 → 18.46% |
| Period B "none of the 200 permutations" | data/addendum/period_B.json shuffle.p_two_sided = 0.0 with n_perm 200 |
| Upper bounds 1.39 pp and 1.52 pp "about one third" of 4.5 pp | 1.392 / 4.5 = 0.31; 1.517 / 4.5 = 0.34 |
| h = 25 "about one fifth of the FICS jump" | 0.92 / 4.5 = 0.20 |
| Independent counts 10,755,282 / 37,391 / 26,722 | checks/independent/rdcheck_2013_2015.log line 2 |

## 3. Open issues of VERIFY.md and where the paper fixes them

| Issue | Fix in the paper |
|---|---|
| W1: effort sentence not tested | Section 1.1, paragraph after the quote: "We do not test this effort effect. This paper tests only the quitting jump." |
| W2: full period B table; describe the 2016 jump as small and not robust | Table 4 (all period B estimates, including h = 10, 24 h, all placebos); Section 5 text: "The evidence for this small jump is weak", with h = 10, 24 h and PB-50 named; abstract: "small and not robust to all variants" |
| W3: round-number control differs from the A&G statistic and is not constant in time | Section 3, Controls item 5 (00 on the right side, only player-games after a win, A&G compare 01 with 99); Section 4 "Controls" paragraph gives the values by year and cites `checks/independent/extra_2013_2015.log`; limit 9 |
| W4: rating chain in limits | Limit 8; Section 6 "Is the null caused by a wrong personal best?" (96.1/95.5/98.5% exact, 3.4/4.1/1.3% above 5 points, three variants +0.46, +0.52, +0.56 pp) |
| W5: injected jump is mechanical | Section 4 "Controls": "This control is mechanical: it shows that the estimator returns a step of 4.5 pp when one is added to the data. It does not show that the personal best is measured correctly." |
| W6: end time of the 2015-12 file | Section 3 "Sample", rule 7 sentence (2015-12-31 22:59:57 UTC, 23 hours); limit 11 |
| W7: wrong sentence about RatingDiff | Section 2: "447,358 player-games (0.5%) have no RatingDiff tag". The wrong sentence is not repeated. |
| W8: figure without intervals; legend over a point; change of slope | New figure with 95% bin intervals and the legend above the axes (`checks/figure.py`); Section 4 first paragraph: "Above the personal best it rises faster ... this change of slope does not count as a jump." |
| W9: 4.5 pp is the main-text number; estimator unknown; computer accounts | Section 3 "Estimator" (SI not read, FICS estimator unknown); limits 2 and 3 |

## 4. Release checks run in the write stage

| Check | Command | Result |
|---|---|---|
| CI script from a clean copy, new venv | `bash checks/ci.sh` in `/tmp/pbq_ci/personal-best-quitting-lichess` (via `run-heavy`, Python 3.13) | 76 numbers, 0 mismatches; `sha256 mismatches: none`; `mismatches: 0`; `RERUN PASS`; exit 0; 12 min 42 s. Log: `data/ci_log.txt`. |
| "Check it" quick command from a clean copy (`git archive` of the final commit) | `python3 checks/paper_numbers.py` | `paper numbers checked: 76, mismatches: 0` |
| Lab result checker on the same copy, named `personal-best-quitting-lichess` | `python3 /Users/kenwu/research/kenwu-lab/tools/check_result.py <copy>` | `ok: 1 result(s)` |
| Failure test of `paper_numbers.py` | changed one number in the paper text and one value in `data/results.json` in a scratch copy | exit 1 with the changed entries named |

The CI run used the release content before `README.md`, `result.json` and one sentence of the paper (the limit of the commit-order evidence) were added. These changes do not touch `checks/` or `data/`; the quick check was rerun on the final copy.
