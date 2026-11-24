---
title: A swap tabu search finds an unsubmitted better feasible point for QPLIB_3347
date: 2026-11-10
tags: optimization, data
status: Not audited
summary: On QPLIB_3347 a tabu search reaches objective 3,817,948 against the library's best 3,818,879, a gain of 931 (0.024 %). Not yet submitted.
---
MINLPLib and QPLIB are reference libraries of nonlinear and quadratic optimisation problems. Each instance page lists the best feasible objective value that anyone has found. The maintainer adds a better point by hand and credits the contributor.

We built a checker in pure Python. It reads the instance files and evaluates a candidate point with the official tolerances. Before any search, the checker had to reproduce the libraries' own best points. It does, except for 10 documented cases. We did not confirm the cause of those cases with the maintainers.

The search was short. It used SCIP warm starts and simple tabu searches on binary quadratic instances. Almost every run tied the library value. One run found a better point. On QPLIB_3347, a minimisation problem, a swap tabu search reached 3,817,948 against the published 3,818,879. That is a gain of 931, or 0.024 %. The search started from the library's own best point. After the search, 37 of the 45 nonzero entries differ from that point. A run from scratch also beat the bound, at 3,818,577.

Two evaluators agree on the new point. The first is our checker. The second reads the GAMS file directly. Both give 3,817,948 and zero constraint violation. The comparison uses the QPLIB table fetched on 2026-11-10.

This is one instance and a small gain. The best point started from the library's own solution. No independent review has checked the point. The point is not yet submitted to the maintainers.

*Code and data: available on request.*
