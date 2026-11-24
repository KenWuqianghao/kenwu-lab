---
title: Job-shop schedules beat JSPLib's bounds file, but 0 of 10 beat an open issue
date: 2026-11-10
tags: optimization, data, tools
status: Checked
summary: Eleven tabu-search schedules beat JSPLib's bounds file by up to 640, but an open issue already held better values for all ten tai_100_100 instances.
---
The Taillard tai_100_100 job-shop instances have 100 jobs and 100 machines, so 10,000 operations each. JSPLib (ScheduleOpt/benchmarks) keeps a file of best known upper bounds, `bks.json`. For these instances the holder is the commercial solver OptalCP. We asked if a tabu search plus exact CP-SAT searches on time windows can lower these bounds on one CPU core. The tabu search follows published papers (Nowicki and Smutnicki 1996; Zhang, Li, Guan and Rao 2007; Balas and Vazacopoulos 1998; Giffler and Thompson 1960).

It can lower the file. Eleven schedules are below the bounds file of 2026-11-12, with gains of 17 to 640 units (0.02 to 0.83 %). An earlier batch of seven bounds was accepted by the maintainer into the repository history. The maintainer then ran OptalCP warm-started from those seven schedules and lowered all seven.

The rest of the result is negative, for three reasons.

First, the maintainer now asks submitters to run a CP engine check first. We built that check with the OptalCP preview edition (900 s, 4 workers). It lowered every one of our ten tai_100_100 schedules, by 6 to 273 units. None pass.

Second, our CP window search stalls. Windows of 500 to 900 operations solve to proven optimality in a fraction of a second. But several critical paths cross each window, so a shorter path does not move the makespan. Larger windows do not solve. At 1,600 operations with four workers we got no proof at all. On the same schedules, OptalCP runs 110 large-neighbourhood steps per second, against 0.3 for CP-SAT.

Third, we missed prior work. Every round compared only with the bounds file. An open issue on the same repository, from 2026-11-06, already held better values for all ten instances. They came from an N7 tabu search on a consumer GPU. We validated those ten schedules with our checker. All are valid, and all are 81 to 1,041 units below ours. Against the best public values, we are 0 for 10.

Every staged schedule passes three checks, one of them JSPLib's own `validate_solution` from a pinned commit. The eleven schedules are not yet submitted to the maintainers, and they do not pass the requested CP check.

*Code available on request. The data is third-party and is not redistributed.*
