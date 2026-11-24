---
title: A 184-character NBA player rating beats PER and ties BPM on a retrodiction test
date: 2026-11-23
tags: sports, ml, code-golf
status: Audited
summary: On 90 sealed team-seasons, a 184-character box-score formula has RMSE 3.258, against 3.668 for PER, 3.713 for WS/48 and 3.297 for BPM (a tie).
---
Advanced basketball metrics such as BPM use long regressions. PER is a famous formula, but it is long and not very accurate. We asked how good a player rating can be if the whole formula must fit in a tweet.

The test comes from Taylor Snarr (2020). Take each player's rating from last season. Weight it by the minutes he plays this season. Sum it for each team, and compare the sum with the team's adjusted net rating. A better rating gives a lower error. We built the data from game logs from 2003-04 to 2025-26. We computed PER, WS/48 and BPM 2.0 locally with the same harness.

We searched formulas on 510 development team-seasons and chose between candidates on 60 validation team-seasons. Then we scored the last 90 team-seasons (2023-24 to 2025-26) one time. The 184-character formula uses per-100-possession box-score rates and minutes per game. Its error on the sealed seasons is 3.258 points per 100 possessions. PER gives 3.668 and WS/48 gives 3.713. The formula beats PER by 0.41, with a 90 % interval of 0.21 to 0.62. BPM gives 3.297. The difference from BPM is -0.04, with an interval of -0.24 to +0.16, so it is a tie. A 94-character version gives 3.317.

A second, longer formula (267 characters) did better on validation and worse on the sealed set (3.392). We report it as a failure.

An independent audit reproduced the sealed numbers and found no leakage that favours the formula. It also found that a better replacement level lowers every score by 0.1 to 0.2, and the order of the metrics does not change. The audit could not confirm from git history that the rules came before the search. So this is not a pre-registered result. Our harness reproduces the numbers of Snarr's test closely for BPM, WS/48 and PER.

PER is a weak baseline. The best public metrics (EPM, DARKO, LEBRON) were not in the test, because their data is not open. We did not check for earlier short player ratings.

*Code available on request. The data is third-party and is not redistributed.*
