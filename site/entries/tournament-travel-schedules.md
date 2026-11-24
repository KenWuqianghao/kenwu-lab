---
title: 64 unsubmitted schedules improve or add upper bounds for RobinX travel instances
date: 2026-11-10
tags: sports, optimization
status: Checked
summary: 64 unsubmitted schedules: 46 are below the RobinX bar and 18 had no bar. LINE34_Mirrored drops from 25,632 to 14,166 (-44.7 %).
---
The Traveling Tournament Problem asks for a double round-robin schedule that minimises total team travel. Each team can play at most three home or away games in a row, and no pair can meet in two consecutive rounds. The RobinX repository at Ghent University lists hundreds of instances with the best known lower and upper bounds. The "mirrored" variants need the second half of the season to repeat the first half with venues swapped.

We wrote a simulated annealing solver with the standard TTP moves. A large-neighbourhood search then re-solves a window of rounds or a subset of teams exactly with CP-SAT. Some runs started from a schedule in the repository, and each such file names its source schedule.

On the mirrored families, 44 instances got a strictly better schedule than the bar. The bar is the smaller of the repository's best upper bound and the literature column. Another 18 mirrored instances had no schedule in the table, and now they have one. Some gains are large. LINE34_Mirrored drops from 25,632 to 14,166, which is 44.7 % less travel. Gains of this size mostly show that few people had worked on these instances. On the classic, well-studied instances, the published schedules are local optima even for windows of 5 to 8 rounds. Only two small improvements came out. LINE32 goes from 8,932 to 8,928, and BRA24 from 499,804 to 499,793.

Every schedule passes the official RobinX validator, built from its GitHub source. It also passes an independent re-implementation with a strict textbook check. The two checkers agree on all 436 published solutions and on 3,487 corrupted copies. We re-read 62 files with large gains. All 64 values were counted against the site on 2026-10-19, and they are still below the bars in a snapshot of 2026-11-10.

The schedules are not yet submitted to the maintainers. The online validator has not been run. We did not check the literature beyond the repository table, so a better schedule can exist in a paper that the table does not list.

*Code and data: available on request.*
