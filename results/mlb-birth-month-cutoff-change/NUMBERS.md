# Numbers in the paper and their sources

`E:` is `data/expected.json`. `X:` is `E:exploratory_verify_round1`. Each count, ratio, OR, CI and p-value in `paper/paper.tex` and `README.md` was compared with `data/expected.json` by a scratch script (2026-11-28; not kept). The script found every value of the paper in `expected.json`, except the values in the section "Values from other sources" below and literal values (dates, years, league ages, the seed 20261128, the debut limits). `RESULT.md` of the solve stage gives the same values.

Rounding: a value is rounded half up from the stored value. Three stored values end in 5 at the third decimal: 0.945 is printed 0.95, 1.095 is printed 1.10, 5.335 is printed 5.34.

## Pre-registered values

| Value in paper | Source |
|---|---|
| 1341, 394 | `E:n_C`, `E:n_T` |
| monthly counts C (98 ... 108) and T (22 ... 30) | `E:months_C`, `E:months_T` |
| 304, 445, 112, 112 | `E:primary/A_C`, `B_C`, `A_T`, `B_T` |
| 1.46 (ratio in C, OR) | `E:primary/r_C` = 1.4638; exp(`E:primary/log_OR`) |
| log OR 0.381 | `E:primary/log_OR` |
| CI 0.081 to 0.681; OR 1.08 to 1.98 | `E:primary/ci95` (0.0813, 0.6808); exp of the same |
| p = 0.0079 | `E:primary/fisher_p_greater` = 0.00788 |
| shuffle p = 0.0085 | `E:shuffle_p_greater` |
| 152/232, 152/213, -0.085, -0.377 to 0.206, p = 0.74 | `E:placebo_split` |
| 97/73, 302/290, 0.244, -0.100 to 0.588, p = 0.19 | `E:placebo_months` |
| 148, 92, p = 0.00036 | `E:known_answer` |
| SUPPORT | `E:decision` |

## Exploratory values

| Value in paper | Source |
|---|---|
| T ratio 1.00, interval 0.77 to 1.30 | `X:T_ratio_B_over_A` (1.0; 0.77, 1.299) |
| Table 2 (eight bins) | `X:bins_4yr` |
| single years 16/25 ... 22/17 | `X:single_years` |
| gap 77/77, OR 1.46, CI 1.03 to 2.07, p = 0.020 | `X:gap_vs_C` |
| T vs gap OR 1.00, CI 0.66 to 1.51, p = 0.54 | `X:T_vs_gap` |
| T vs late C 152/232, OR 1.53, CI 1.10 to 2.13, p = 0.0079 | `X:T_vs_lateC_1984_92` |
| Table 3 rows 22, 23, 24, 25, 27 | `X:debut_age/before_NN` |
| Table 3 row 26 (132/132, 424/596, 1.41, 1.07 to 1.84, 0.0085) | `X:debut_age/before_26`; same counts as `E:exploratory_age26` |
| 15 T players with limit 22 | 7 + 8 from `X:debut_age/before_22` |
| 224 T players in groups A and B | 112 + 112 |
| non-US 55/56, 143/155, OR 1.07, CI 0.69 to 1.65, p = 0.82 | `X:non_us_born` |
| Jul vs Aug 40/41, 92/148, 1.57, 0.95 to 2.61, 0.053 | `X:month_groups/Jul_vs_Aug` |
| Jun-Jul vs Aug-Sep 1.47, 1.02 to 2.11, 0.025 | `X:month_groups/JunJul_vs_AugSep` |
| Apr-Jul vs Aug-Nov 1.17, 0.90 to 1.52, 0.14 | `X:month_groups/AprJul_vs_AugNov` |
| leave one year out, p 0.0066 to 0.029 | `X:leave_one_T_year_out_p` (min 0.0066, max 0.0287) |
| trend z = -0.19, p = 0.85 | `X:pretrend_C_single_years` |
| births ratio 1.017, 1.015, expected OR 1.002 | `X:us_birth_seasonality` |
| 40 May, 41 August births in T | `E:months_T` [4], [7] |

## Values from other sources

| Value in paper | Source |
|---|---|
| 503, 313, players born since 1950, data to 2005 | Spira (Slate, 2008); quote checked in VERIFY.md round 1, check 1 |
| July 31 for more than 55 years; April 30 from 2006 | Little League release, October 2005 (archived); fetched again by the write stage, 2026-11-28 |
| August 31 from 2018 | Little League news, 2015-11-13; fetched again by the write stage |
| 9876 players, 98 without debut date | VERIFY.md round 1, check 8 |
| commits 0569aaa (02:23:35) and bfc9b7a (02:26:30), 3 minutes | `git log`; VERIFY.md round 2, check 1 |
| SciPy recount 112/112, 304/445, OR 1.464, p 0.0079 | VERIFY.md round 1, check 6 |
| Retrosheet 113/112, 303/445, OR 1.48, p 0.0062; gap 77/77 | VERIFY.md round 1, check 7 |
| FiveThirtyEight 1.0179 against 1.0181 | VERIFY.md round 2, check 5 |
| 42 season lists | 1985..2026 in `checks/rerun.py` |
| Duda (2026): born from 1951, cutoff found at July 29, no MLB split by birth year | Zenodo 10.5281/zenodo.24348797, PDF read by the recheck stage, 2026-11-28 (Section on athletes, Figure 5); "no split" is from a text search of the PDF for MLB and baseball |
| Herring et al.: 7,078 draftees, 2013-2018, z = +4.45, z = -4.15 | Crossref and Europe PMC abstract |
| Zhang et al.: 16,122 players, 1871-2014, effect for born 1950-1970 | abstract at ijsp-online.com/abstract/view/49/448, fetched 2026-11-28 |
| Abel and Kruger: 1880-1999, over-represented from 1900, change after 1980 | Europe PMC abstract, PMID 17619630, fetched 2026-11-28 |
| Jedlovec: 2009-11-04, Dixie Youth to April 30 for 2006, school teams by grade | archived page, fetched 2026-11-28 |
| Collier: 2016-07-05, chi-squared test | r-bloggers.com page, fetched 2026-11-28 |
| run time 73 s | `bash checks/ci.sh` from a clean copy, 2026-11-28 (see below) |

## League ages (computed by hand, not by the script)

League age under April 30 = age on April 30 of the season. Born 1992-08-01 to 1993-04-30: 13 in 2006. Born 1993-05-01 to 1994-04-30: 12. Born 1994-05-01 to 1994-07-31: 11. So players born 1992-08 to 1994-07 were league age 11 to 13 in 2006 (paper, Section 5). A player born 1996-05-01 is 9 on 2006-04-30, so T starts there.

## VERIFY.md issues and where the paper fixes them

Round 2 (open issues for the write stage):

| # | Issue | Fix |
|---|---|---|
| 1 | Title says "absent" | Title: "is not seen". The T interval 0.77 to 1.30 is in the abstract, Section 4, Limits and Conclusion. The text does not say that the excess is removed. |
| 2 | Teen-age explanation not tested | Section 5 "Timing": stated as "One possibility ... We did not test this." with both weakening facts: (a) school-year grouping in high school and college did not change in 2006 (cited to Jedlovec 2009 for grouping by grade); (b) the single birth years are listed and called noisy. Limits, bullet 2. |
| 3 | Non-US wording | Section 5 "Players not born in the USA": "The data hold only the birth country. Our assumption is that most of these players did not play US youth baseball; some of them grew up in the USA." |
| 4 | Three prior-art sources | (a) The DOI 10.1080/19485565.2002.9989098 is Abel and Kruger, "Seasonality of birth in the majors, 1880-1999", Biodemography and Social Biology 52(1-2):47-55, 2005 (Crossref; abstract from Europe PMC). Cited in Section 1 "Prior work" [3]. It has no before/after test of 2006 (its data end in 1999). (b) The R-bloggers post (A. Collier, 2016-07-05) was fetched. It shows a chi-squared test of non-uniform birth months. The page does not give the range 1965-2012 and does not remark that a later count can test the change; the search summary in VERIFY.md was wrong on both points. Cited [8] for what it does. (c) The Bill James Online page article1191 returns HTTP 404 today. The archived copy of 2023-05-31 was fetched. Its author is Ben Jedlovec (2009-11-04), not Bill James. It confirms the Dixie Youth change for 2006, that some organizations did not move, and that school teams group by grade. Cited [7]. None of the three is a before/after test. |
| 5 | Debut-age rows nested | Section 5 "Debut-age limit" and the caption of Table 3: "The rows are nested samples of the same players; they are not independent tests." The text keeps that the result is not significant for the limits 22 and 24. |

Round 1 issues labelled FIXABLE (write); the solve stage fixed them in RESULT.md, and the paper keeps the fixes:

| # | Issue | Place in the paper |
|---|---|---|
| 4 | Placebo 2 not neutral | Section 4, "Control 2" bullet |
| 5 | "Disappeared" | Title, abstract and Section 4 give the interval 0.77 to 1.30 |
| 6 | Half-transfer identity | Section 4, paragraph after the list |
| 7 | Source of the cutoff history | Section 1 cites the archived 2005 release [10] for July 31 and April 30, and the 2015 page [11] only for August 31 |
| 8 | Pre-registration evidence | Section 3, first paragraph |
| 9 | Omni Calculator year | Section 1 and reference [9]: "The year of that article is not stated on the page." |

Round 1 issues 1 to 3 (FIXABLE (solve)) were fixed by the solve stage; their numbers are in Section 5 and the prior work in Section 1.

## Check-it runs (2026-11-28)

1. Clean copy of `release/` in `$TMPDIR/mlbclean/mlb-birth-month-cutoff-change`, new venv (`uv venv --python 3.13 --seed`, Python 3.13.18), command `run-heavy 900 bash checks/ci.sh`: last line `MATCH expected.json`, exit 0, wall time 73 s, fresh download.
2. `python3 /home/deck/research/factory/lab-repo/tools/check_result.py $TMPDIR/mlbclean/mlb-birth-month-cutoff-change`: `ok: 1 result(s)`, exit 0.
3. No Lean is used, so `lean-compare` does not apply (no `lean/` folder).
