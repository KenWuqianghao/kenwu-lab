# Protocol: held-out test of the ".300 hitter" round-number claims (2009–2025)

Pre-registered 2026-11-28, before any outcome was computed. The commit time is the evidence.

## Claim
Pope, D. G. and Simonsohn, U. (2011), "Round Numbers as Goals: Evidence From Baseball,
SAT Takers, and the Lab", Psychological Science 22(1):71-79. Sample: MLB 1975–2008, hitters
with at least 200 at-bats. Statements as quoted in secondary sources (the full text was
not accessible in this session):
- C1 (bunching): "batters are nearly 4 times as likely to end the season with a .300
  batting average as they are to end the season with a .299 average" (quoted in SABR
  By the Numbers, Summer 2023, abstract of H. Krabbenhoft).
- C2 (no walks): no .299 hitter drew a walk in his final plate appearance of the season
  (as reported by Deadspin and The Daily Pennsylvanian, 2010–2011).
- C3 (hits): in the final plate appearance, .299 hitters hit about .430 and .300 hitters
  about .230 (same press sources).
- Critique: Scott and Birnbaum (SABR, 2010/2011) state that "sampling bias fully accounts
  for Pope and Simonsohn's findings" for C3, because a player who reaches .300 is often
  removed. In the team's last two games, without conditioning on "last PA", they find
  .299 (155/517) for batters just below .300 and .297 (43/145) for batters at .300.

## Data
Retrosheet regular-season event files, 2009–2025 (https://www.retrosheet.org/events/YYYYeve.zip),
downloaded 2026-11-28. These seasons are all after the original sample (held out).

## Definitions
- PA events are `play` records whose event is not a no-PA event (NP, SB, CS, PO, POCS, WP, PB,
  BK, DI, OA, FLE (error on a foul fly), and NP substitution records). Hit: S, D, DGR, T, H, HR.
  Walk: W, IW/I. No-AB PAs: W, IW, HP, sacrifice (SH or SF modifier), C/E2 interference.
  Every other PA is an at-bat.
- Validation gate: the season AB and H that the parser computes must match published
  totals for at least 3 named player-seasons (exact). If not, fix the parser before any test.
- Entering average of a PA = H/AB before the PA. Displayed average = round half up to 3 decimals.
- Eligible batter-season: at least 200 AB at season end (computed from the events).
- Last PA: the final PA of the batter's regular season.

## Tests (all one-sided, alpha = 0.05, no other tests count as confirmatory)
- T1 (C1): among eligible batter-seasons, n300 = count with final displayed average .300,
  n299 = count with .299. Binomial test of n300 vs n299 with p = 0.5 (H1: more .300).
  Placebo: the same ratio n(x0)/n(x9) for each other threshold .250 to .350 step .010
  except .300 (10 placebo thresholds). C1 is supported if p < 0.05 and the .300 ratio is
  larger than every placebo ratio. C1 is refuted if p >= 0.05.
- T2 (C2): group L299 = last PAs of eligible batters whose entering displayed average is
  .299. Report walks (W+IW) in L299. Fisher exact test: walk rate in L299 lower than in
  comparison group LC = last PAs of eligible batters with entering displayed average in
  .280–.320 except .299 and .300. C2 "never walk" is refuted if L299 has at least one walk.
  "Walk suppression" is supported if Fisher p < 0.05.
- T3 (C3): batting average (H/AB) in last PA, L299 vs L300 (entering .300). Fisher exact,
  H1: L299 higher.
- T4 (selection control, the test the paper did not run): unbiased sample = all PAs in
  the batter's team's last 2 regular-season games, for eligible batters, entering average
  not conditioned on being last. Group B = a hit would raise the displayed average to
  .300 or more and the current displayed average is below .300; group A = current displayed
  average is .300 or more and an out would drop it below .300. Compare hit rate (H/AB) B vs A
  (Fisher, H1: B higher) and walk rate (B lower than A, Fisher). If T3 is significant and
  T4 is not, we report that the held-out data agree with the Scott–Birnbaum selection account.
- Exit check: in L299, count the PAs that end with a hit and are followed by no more PA
  (by construction all) versus the share of .300+ batters who stop playing: fraction of
  eligible batters whose average reached displayed .300 in the team's last 3 games and
  who then had no further PA, compared with the same fraction for batters at other values
  .280–.320. Descriptive only.

## Outcome labels
Each of C1, C2, C3 gets one label: supported, refuted, or not significant. A null result
is a valid result.

## Addendum 2026-11-28 (written after the results were seen)
- The T1 rule has two conditions. The binomial test passed (p = 0.0009). The placebo condition
  failed: the .330 threshold gave 9 vs 2 (ratio 4.5), larger than .300 (46 vs 20, ratio 2.3).
  The three labels in "Outcome labels" do not cover this case. We report C1 as "not supported
  under the pre-registered rule; binomial test significant". We do not change the rule.
- The validation gate used published season totals that the author remembered (Baseball-Reference
  values); they were not fetched in this session.

## Addendum 2, 2026-11-28 (solve round 2, after verify round 1)
What I saw before I wrote this addendum: all of `VERIFY.md`. It gives the verifier's values with the
corrected parser (47 vs 20; L300 4/20 in 23 PAs; T3 p = 0.125; T4 62/217 vs 14/67) and post hoc values
for the paper's own comparisons. I also read the paper's full text (web.archive.org copy of the
Wharton in-press PDF, 10 pages). The original protocol was written without the full text. The raw
Retrosheet files were downloaded before the first protocol commit `fee506d`.

The pre-registered rules (T1 to T4, labels) do not change. These changes apply:

1. Parser correction. Official Baseball Rule 9.15(b): if a pinch hitter replaces a batter during a
   PA with two strikes and the PA ends in a strikeout, the strikeout and the at-bat go to the first
   batter. The parser applies this rule. Detection: a `play` record with event `NP` for batter X with
   a count of two strikes, then a `sub` record with position 11 into X's batting slot, then the next
   non-NP `play` record of the substitute starts with `K`. T1 to T4 are computed again with the
   corrected parser, and the labels follow the original rules. The uncorrected values stay in git
   history (commit `940a94e`).
2. Validation gate, extended. `checks/rerun.py` downloads the MLB Stats API season hitting totals
   (2009 to 2025) and the Chadwick Bureau register (ID map from MLBAM to Retrosheet), and compares
   (H, AB) for every batter-season with at least 200 AB in either source. A second comparison uses
   Lahman `Batting.csv` (2009 to 2021). Each mismatch is reported. Sensitivity check S1: T1 computed
   from the official MLB totals in place of the parsed totals.
3. The paper's own statements (full text, p. 2 and p. 4, note 4). The unit is the "last scheduled
   plate appearance": the last item in the chronological list of a batter's PAs and of the times a
   pinch hitter (`sub` record, position 11) took his batting slot. The denominator includes outs,
   hits, walks and substitutions. Entering average = average before this item. Exploratory
   comparisons (post hoc, not confirmatory; the verifier computed similar values first):
   - P1: season-end shares at .298/.299 vs .300/.301 (paper: 0.97% vs 2.30%). Binomial, p = 0.5.
   - P2: hit share, .298/.299 vs .300/.301 (paper: 35.2% vs 22.4%).
   - P3: hit share, .299 vs all other values .280 to .320 (paper: 43% vs 22.8%).
   - P4: walk share, .298/.299 vs .300/.301 (paper: 2.5% vs 8.6%).
   - P5: substitution share, .298/.299 vs .300/.301 (paper: 4.1% vs 19.7%).
   - P6: substitution share, .300 vs all other values .280 to .320 (paper: 34.3% vs 7.0%).
   For each: the two-proportion Z test (two-sided, as in the paper) and the Fisher exact test
   (one-sided, in the paper's direction), with a Holm correction over P2 to P6. "Same direction and
   significant" means the paper's direction and Holm-adjusted Fisher p < 0.05.
4. Exit check. The original text states a fraction of batters; the first `rerun.py` computed a share
   of PAs. Both are now reported. The check stays descriptive.
5. T1 interval: the Clopper-Pearson 95% interval for n300/(n300+n299), changed to a ratio, is added to
   `expected.json`.
