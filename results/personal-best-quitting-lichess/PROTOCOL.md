# Pre-registered protocol: personal-best quitting on Lichess, 2013-2015

Written 2026-11-25, before any outcome (quit rate by distance to the personal best) was computed.
Data seen before this commit: header format, rating-chain consistency per speed, and the
first-game rating of new players (all checks listed in section 8). No quit rate was computed.

## 1. Claim under test

Anderson & Green, PNAS 115(8):1772-1776 (2018), on FICS blitz 2000-2015:
"The probability of quitting jumps across the reference point—a 4.5 percentage point, or 20%,
increase. As predicted, players are discontinuously more likely to quit after setting a new
personal best."

Question: does the same discontinuity exist for Lichess blitz, 2013-2015?

Context fact: in 2013-2015 Lichess did not, to our knowledge, show a "highest rating" on the user
page. The per-speed stats page that shows it was developed in the `perfStats` branch of
lichess-org/lila in late December 2015 (commit `b928a2c8`, 2015-12-24). Not confirmed: that no
other page or notification showed the personal best before that. FICS showed the best rating and
sent a notification. So a null result here is a test of the claim on a platform with low
personal-best salience, not a plain failure of the original analysis.

## 2. Data

- Lichess open database, standard rated games, monthly files 2013-01 to 2015-12 (36 files),
  `https://database.lichess.org/standard/lichess_db_standard_rated_YYYY-MM.pgn.zst`, CC0.
  Accessed 2026-11-25. File checksums: `https://database.lichess.org/standard/sha256sums.txt`.
- Only PGN header tags are kept: Event, Site, White, Black, Result, UTCDate, UTCTime, WhiteElo,
  BlackElo, WhiteRatingDiff, BlackRatingDiff, TimeControl, Termination.
- Variant games and casual games are not in these files. This is a limitation for the quit
  outcome (section 3).

## 3. Definitions

Unit: player-game (two per game). Speed comes from the Event tag (second word: Bullet, Blitz,
Classical, Correspondence). Tournament games are included.

For each player, sort all games of all speeds by start time (UTCDate, UTCTime), ties by Site.

- Pre-game rating `pre_t`: WhiteElo or BlackElo.
- Post-game rating `r_t`: `pre_t + RatingDiff_t` when RatingDiff exists. Otherwise the pre-game
  rating of the player's next game in the same speed. If neither exists, `r_t` is missing; the game
  is not used as an observation and does not update the personal best.
- Personal best before game t, `PB_t`: the maximum of `r_s` over all earlier games s of the player
  in the same speed. Undefined for the first game.
- Running variable: `x_t = r_t - PB_t` (integer rating points). A new personal best is `x_t >= 1`.
- Quit: `quit_t = 1` if the player's next game (any speed) starts more than `60 min + D_t` after
  the start of game t, or if there is no next game in the data. `D_t = 2 * (base + 40 * increment)`
  seconds from TimeControl (an upper estimate of game length; the header has no end time).
  Correspondence games ("-" time control) have no D and are not observations.

## 4. Sample (primary: blitz)

A player-game is in the primary sample if all of these are true:
1. Speed is Blitz.
2. The player's first Blitz game in the data has `pre = 1500` (the Lichess start rating, so the
   history is complete; checked: 92% of new blitz players in 2013 start at 1500).
3. It is the player's 200th Blitz game or later (A&G: drop player-games before the 200th game).
4. No new personal best was set in the player's previous 20 Blitz games (A&G filter).
5. The player won game t (A&G: player-games that follow a win).
6. The previous Blitz game of the player started at most 30 days earlier. (Replaces the A&G
   filter RD < 80; Lichess headers have no RD, and Glicko-2 RD grows with inactivity.)
7. Game t started on or before 2015-12-30 23:59 UTC, so the next 24 h are inside the data.

## 5. Primary test

- Estimator: local linear regression of `quit` on `x`, separate slopes on each side, cutoff
  between x = 0 and x = 1 (center: `c = x - 0.5`), triangular kernel, bandwidth h = 15 rating
  points on each side (so x in [-14, 15]). Fixed in advance; no data-driven bandwidth.
- Jump = the coefficient on `1[x >= 1]`. Standard error clustered by player. 95% CI = estimate ± 1.96 SE.
- Relative jump = jump / left limit (the fitted value at c = 0 from the left).

Decision rule (one outcome, chosen by the primary 95% CI):
- **Supported**: CI lower bound > 0.
- **Opposite sign**: CI upper bound < 0.
- **Null, smaller than FICS**: CI contains 0 and CI upper bound < 4.5 percentage points.
- **Inconclusive**: CI contains 0 and CI upper bound >= 4.5 percentage points.
Also reported: if a supported jump is smaller than 4.5 pp with the upper bound below 4.5 pp, the
FICS magnitude is rejected.

## 6. Controls

1. **Placebo cutoffs.** The same estimator at fake cutoffs, using only data on the same side of
   the true cutoff: PB-50, PB-35, PB-25 (data x <= 0) and PB+10 (data x >= 1). For a
   placebo at PB+k, the fake treatment is `x >= k + 1` and the center is `x - k - 0.5`, the same as
   the true cutoff at k = 0. Expected: no jump. A placebo with |z| > 1.96 is reported and weakens the
   interpretation of the primary test; it does not change the decision rule.
2. **Covariate balance.** The same RD on predetermined covariates: rating gain of game t
   (`r_t - pre_t`), opponent rating minus own pre-game rating, log minutes since the previous game,
   and the player's number of prior Blitz games. Expected: no jump.
3. **Within-player shuffle.** Permute `quit` labels within each player inside the bandwidth
   sample, re-estimate the jump; 200 permutations, seed 12345. Report the permutation p-value
   (two-sided, share of |permuted jump| >= |observed jump|).
4. **Injected jump.** Copy the data; for observations with x >= 1 and quit = 0, set quit = 1 with
   probability q chosen so the right-side quit rate rises by 4.5 pp in expectation
   (q = 0.045 / (1 - right-side quit rate)); seed 12345. Re-estimate. Expected: estimate = true
   jump + 4.5 pp within the CI. This shows the power to see the FICS effect.
5. **Positive control: round numbers.** Sample rules 1-3, 5-7 (no PB filter). Running variable
   `d = ((r + 50) mod 100) - 50`; treatment `d >= 0` (ratings ending 00-49 vs 50-99 below the next
   hundred); same estimator, h = 15. A&G report +3.5 pp on FICS; Bobev (2026, retracted) reports a
   round-number effect on Lichess. This tests if the method can see a known reference point.

## 7. Robustness and secondary (reported, not part of the decision)

- Quit threshold 24 h instead of 60 min.
- Quit defined as next start more than 90 min after this start (no D_t).
- Bandwidths h = 10 and h = 25.
- Exclude tournament games (Event contains "tournament") from observations.
- Add the rating gain of game t as a linear covariate.
- Same primary test for Bullet and Classical.
- Simple difference of quit rates at x = 0 vs x = 1 (adjacent bins), as a model-free view.

## 8. Checks run before this protocol

- Header format of 2013-01, 2014-06, 2015-06, 2015-12 files (RatingDiff is present in most rows).
- Per-speed rating chains: in sampled 2013-2014 months, 92-96% of consecutive same-speed games
  satisfy `pre_{t+1} = pre_t + diff_t`, against 80-85% when speeds are pooled. So Lichess kept
  separate ratings per speed in this period.
- First Blitz game rating of new players in 2013: the mode is 1500 every month.

## 9. What would change the protocol

Nothing after outcomes are seen, except a dated addendum that says what was seen first.

## Addendum A (2026-11-25, 03:15 CET): second period after the "Highest rating" display

Written after the primary analysis of 2013-2015 was run. Seen before this addendum: all numbers
in `data/results.json` for 2013-2015 (primary jump +0.51 pp, 95% CI [-0.38, +1.39] pp, decision
"Null, smaller than FICS"; all controls). No 2016 data was downloaded or seen.

Fact found after the main protocol: the lila commit `5e9fde4a` (2015-12-26, "complete user perf
stats UI") adds the panel `ratingAt('Highest rating', d.stat.highest)` to the per-speed stats
page. Commit `4dacb459` (2016-01-10, "demonstrate perf stats") links it from the user page.
The deployment date is not confirmed; we assume it is before 2016-02-01.

This addendum is a secondary test. It does not change the decision on the primary test.

- Data: as section 2, plus the 12 monthly files of 2016 (accessed 2026-11-25).
- Period B observations: player-games that start from 2016-02-01 00:00 to 2016-12-30 23:59 UTC.
  Histories (PB, game index, filters) use all games from 2013-01 onward. Rule 7 changes its end
  date to 2016-12-30 23:59.
- Period A is re-estimated from the same extended build (observations 2013-01-01 to
  2015-12-30 23:59). Expected: identical to the primary result, except that `quit` for games at
  the end of 2015 now sees 2016 games (rule 7 already drops the last day, so the change is small).
- Test B: the primary estimator (section 5) on Blitz, period B. Decision words as in section 5.
- Difference test: jump_B - jump_A, SE = sqrt(SE_A^2 + SE_B^2) (treats the periods as
  independent; players overlap, so this is an approximation). If the display of the PB raises
  quitting at the PB, the prediction is jump_B > jump_A. Support for the salience prediction:
  95% CI of the difference above 0.
- Controls for period B: round-number control (section 6.5) and the injected jump (6.4).

## Addendum B (2026-11-25, 04:05 CET): self-play games

Written after the primary result (2013-2015) was seen; no 2016 outcome was seen.
The header data has rated games in which White and Black are the same account (for example
`lichess.org/tjdvfpx2`, 2013-12-27). The first build kept two rows for such a game, with the same
player, game and start time. The second build, which processes players in buckets to limit disk
use, found 917 such duplicate rows in 2013-2015. A self-play game is not a game between two
players. Rule added: games with White = Black are excluded from all histories and observations.
The primary result is recomputed with this rule. Both the first and the recomputed primary numbers
are reported. The decision uses the recomputed numbers; RESULT.md states if the decision differs.
