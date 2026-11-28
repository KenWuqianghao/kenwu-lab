# Pre-registered protocol: did the 2006 youth-baseball cutoff change move the MLB birth-month peak?

Date: 2026-11-28. This file is committed before any birth month of the treatment cohort is computed.
The raw data files are downloaded, but no tabulation of birth months has been run.

## Claim under test
US-born major leaguers are over-represented in August births and under-represented in July
births. Published work attributes this to the July 31 age-cutoff date of Little League and
other US youth baseball (relative age effect). Sources: Thompson, Barnsley and Stebelsky,
"Born to play ball": the relative age effect and Major League Baseball, Sociology of Sport
Journal 8 (1991); G. Spira, "The Boys of Late Summer", Slate (2008), 503 August vs 313 July
births of US-born players born 1950 on. Bill James ("Why July Children Don't Make the Major
Leagues", billjamesonline.com article 1191) notes that the cutoff moved in 2006 and that no
player from the new regime had reached professional baseball when he wrote.

Little League history (littleleague.org news "update implementation little league baseball
age determination date"): July 31 for more than 55 years; April 30 from the 2006 season
(recommended by USA Baseball); August 31 from 2018.

Causal prediction: players who were league ages 9 to 12 entirely under the April 30 rule
must show a shift of relative excess from Aug-Oct births toward May-Jul births.

## Data
- MLB Stats API, `https://statsapi.mlb.com/api/v1/sports/1/players?season=YYYY`, seasons
  1985-2026, downloaded 2026-11-28. Fields: `id`, `birthDate`, `birthCountry`, `mlbDebutDate`.
- Union over seasons, deduplicated by `id`. Keep `birthCountry == "USA"` and a non-empty
  `mlbDebutDate` and `birthDate`.

## Cohorts (each window is a whole number of 12-month years, so the window does not bias months)
- Control C: born 1976-08-01 to 1992-07-31 (July 31 rule in force at league ages 9-12).
- Treatment T: born 1996-05-01 to 2001-04-30 (April 30 rule in force at league ages 9-12).
- Equal exposure rule for both cohorts: a player counts only if `mlbDebutDate` is before his
  25th birthday. The 25th birthday of every T player is on or before 2026-04-30, so every
  T player had his full window observed. This removes the bias where players born early in
  the last birth year have had more time to debut.

## Primary test
Groups: A = birth months May, Jun, Jul. B = birth months Aug, Sep, Oct.
2x2 table: cohort (T, C) x group (A, B). Odds ratio OR = (A_T/B_T)/(A_C/B_C).
One-sided Fisher exact test, alternative OR > 1. Threshold p < 0.05.
95% CI for log OR by the Woolf (normal) method.

## Controls
1. Placebo cohort split: C1 = born 1976-08-01..1984-07-31 vs C2 = 1984-08-01..1992-07-31
   (no cutoff change). Same test (C2 as "treatment"). Expect p >= 0.05.
2. Placebo months: groups Nov-Dec-Jan vs Feb-Mar-Apr, T vs C. No prediction from the
   cutoff change. Expect two-sided p >= 0.05.
3. Shuffle check: 20000 permutations of the cohort labels among the A+B players of T and C;
   report the permutation p for log OR (one-sided). Must agree with Fisher.
4. Known-answer replication on C: the count of August births must exceed July births
   (Spira's pattern). Report the counts and a binomial test (two-sided) of Aug vs Jul.

## Decision
- Let r_C = B_C/A_C (the Aug-Oct excess in the control cohort). Full transfer predicts
  log OR = 2 log r_C. Half transfer predicts log OR = log r_C.
- SUPPORT: Fisher p < 0.05 and placebo 1 p >= 0.05.
- REFUTE the hypothesis that the youth cutoff is the main cause: upper end of the 95% CI of
  log OR < log r_C. The data then exclude half transfer.
- Otherwise: INCONCLUSIVE. Report the CI.
- Both SUPPORT and REFUTE can be reported only as associations. Known confounds that this
  design does not remove: school-entry cutoffs (mostly Sep 1, not changed in 2006), drift in
  US birth seasonality, and travel-ball organizations with other cutoffs.

## Output
`checks/rerun.py` downloads the data, computes every number, and compares with
`data/expected.json`.

## Addendum, 2026-11-28 (after the primary result was computed)
- No rule above is changed.
- The Bill James sentence in "Claim under test" came from a search-engine summary. The page
  (billjamesonline.com article 1191) returned HTTP 404 on fetch, so that sentence is Not
  confirmed. The paper does not cite it.
- Spira (Slate, 2008-04-16) gives the date as an announcement by USA Baseball in 2005, and
  says that in 2008 "for the first time" all major youth organizations used April 30.
- One exploratory variant was added after the result: debut before age 26 instead of 25,
  with T born 1996-05-01..2000-04-30. It is labelled exploratory in `checks/rerun.py`.

## Addendum 2, 2026-11-28 (solve round 2, after verify round 1)
No rule above is changed. The pre-registered test, its threshold and its decision stay as they are.
What I saw before this addendum: the primary result, all of VERIFY.md (round 1), and the
exploratory numbers that VERIFY.md lists.
- Correction to control 2. The sentence "No prediction from the cutoff change" is wrong. An
  April 30 cutoff makes Feb-Apr births the youngest of the age group. So the change predicts a
  fall of Feb-Apr against Nov-Jan. Placebo 2 is therefore not a neutral placebo. The result text
  does not use it as evidence against a general change of month shares.
- Correction to the source of the cutoff history. The facts "July 31 for more than 55 years"
  and "April 30 from the 2006 season" come from the Little League release of October 2005,
  archived at http://web.archive.org/web/20051223154010/http://www.littleleague.org:80/media/age_change_Oct05.asp .
  The 2015 littleleague.org page supports only "August 31 from 2018".
- Evidence for the pre-registration. Only the commit order proves it: `0569aaa` (this file,
  02:23:35) is before `bfc9b7a` (rerun.py and expected.json, 02:26:30). The raw season files
  were on disk before the protocol commit. The sentence "no tabulation of birth months has been
  run" is the word of the sprint session only. No log proves it.
- Exploratory analyses added after the result (all labelled in `checks/rerun.py` under
  `exploratory_verify_round1`): birth-year table, gap cohort 1992-08-01..1995-07-31, debut-age
  limits 22 to 27, players not born in the USA, other month groups, leave-one-year-out, a
  trend test inside C, and the expected odds ratio from US male births by month (CDC).
