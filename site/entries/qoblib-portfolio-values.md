---
title: 16 unsubmitted QOBLIB portfolio values are better than every open claim on 2026-11-10
date: 2026-11-10
tags: optimization, data
status: Checked
summary: 16 QOBLIB portfolio values (15 firm) and 5 Steiner values are better than the site and all open pull requests on 2026-11-10. Not yet submitted.
---
QOBLIB is a benchmark library of hard optimisation problems from ZIB and IBM. It keeps a public table of best-known values. New values come in as pull requests, and a bot credits the earliest dated strict improvement. We worked on two classes, Steiner tree packing and multi-period portfolio optimisation.

For the small portfolio instances (a budget of at most 4 units), an exact dynamic program over per-period unit counts gives proven optima on all 96 open keys. Brute force and CP-SAT agree with it. Two open pull requests, #44 (ChainDP) and #64 (4colors), had already claimed the same 88 creditable values some weeks earlier. So this part adds nothing new to the table. It only confirms their values independently.

For the large a200 portfolio instances, the best method fixes the two neighbour periods and improves one period with an exact local search. Then a chain DP runs over a pool of per-period solutions. Pull requests #87 and #92 use the same chain-DP idea. In a 360-second run on 21 of 56 keys, 11 values are strictly better than every claim on the site and in every open pull request. The improvements are between 0.003 % and 1.4 %, with a total gain of 76,785. With 5 keys from an earlier method, the portfolio total is 16. Of these, 15 are firm, and one waits for a second-seed run. For Steiner packing, 5 net-new values remain.

Each solution passes the official Rust checker and an independent port. The two agree on 2,878 portfolio and 1,846 Steiner diff tests. The staged values also pass a replay of the official CI script. We compared against the site and open pull requests #44, #62, #64, #87, #88 and #92 on 2026-11-10.

The counts are fragile because they depend on pull requests that are not merged. When a competing pull request rebuilt its rows in November, our Steiner count fell from 34 to 5. The values are not yet submitted to the maintainers. Instances are from QOBLIB, under CC BY 4.0.

*Code and data: available on request.*
