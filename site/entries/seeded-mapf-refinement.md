---
title: Seeding MAPF-LNS2 with the tracker's best plans gives 2,478 unsubmitted better plans
date: 2026-10-20
tags: optimization, games, tools
status: Checked
summary: Local search started from the MAPF Tracker's best plans gave 2,478 strictly better plans, with a mean gain of 8.10 % in sum of costs. Not yet submitted.
---

In multi-agent path finding (MAPF), many agents must cross a shared grid with no collisions. The usual objective is the sum of their path lengths. The MAPF Tracker holds about 1.46 million instances. About 1.23 million of them are still open, and each has a best known solution.

We asked a cheap question. What happens if the local search starts from the tracker's own best plan instead of solving from scratch? That one change is the whole method. On a fixed set of 200 development instances, a 60-second run of MAPF-LNS2 seeded with the tracker's plan improved 186 instances at 73.3 improvements per CPU-hour. The same solver with its usual LaCAM2 start improved 63 instances at 27.2 per CPU-hour.

Ranking targets by the relative gap between the best known value and the lower bound also helped. It raised the hit rate from 86 % to 94 % and the mean gain from 0.92 % to 11.9 %.

The result is 2,478 improved plans. The mean gain is 8.10 %, the median gain is 2.50 %, and the total sum-of-costs reduction is 26,654,811.

Every plan passes our validator. That validator agrees with the tracker's own Rust checker on 60,000 random test cases and on 206 real best known plans, with no mismatch. Each plan was compared live with the tracker when it was found. After a three-week gap, a second live check found all 2,478 plans still strictly better than the current tracker best. The last re-validation on a rebuilt machine covered a spot check of 40 files only, and all 40 were valid.

This is not a new solver. 2,128 of the plans are refinements of a plan that another solver found first. Of these, MAPF-LNS2 made 1,759, LaCAM2 210, LaCAM 143 and LaCAM with LaCAM2 16. So the credit goes in large part to those solvers and to the tracker contributors who made the starting plans. The method uses LaCAM2, LaCAM3 and MAPF-LNS2 (Li et al.) with two small patches. Nothing has been submitted to the tracker yet, so none of these plans appears there. The best known values also change, and each batch must be re-checked just before an upload.

*Code and data: available on request.*
