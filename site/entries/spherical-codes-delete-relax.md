---
title: Delete-and-relax gives two unsubmitted improvements to Cohn's spherical code table
date: 2026-11-10
tags: maths, optimization
status: Not audited
summary: Two spherical codes, (16, 199) and (3, 838), have a smaller maximal cosine than the table of 2026-11-10, by 2.765e-6 and 6.638e-6. Not yet submitted.
---
A spherical code is a set of N points on the unit sphere in d dimensions. The points are spread out so that the smallest angle between any two points is as large as possible. Henry Cohn keeps a public table of the best known codes for d from 3 to 32 and N up to 1,024. It has about 15,000 entries.

Polishing the published codes gave nothing. Every flagged entry we tried was already stationary. Random restarts were 1e-3 to 1e-2 worse. The method that worked is "delete and relax". Take the table's code for N+1 points and remove one point. Then let the rest spread out under a smooth approximation of the maximum (log-sum-exp) with L-BFGS. Finish with a linear-programming polish. The choice of point matters. For (16, 199), deleting point 77 worked, and three other choices did not.

Two codes beat the table as of 2026-11-10. In 16 dimensions with 199 points, the largest cosine falls from 0.249583186098 to 0.249580421227. In 3 dimensions with 838 points, it falls from 0.991793296667 to 0.991786658783. Our validator computes both values exactly from rational coordinates, not in floating point. Both gains are above the table's display precision.

Both codes start from codes in the table. The (3, 838) code comes from Antoine Jay's (3, 839) code. The (16, 199) code comes from the table's (16, 200) code. The two table entries that we beat are also Antoine Jay's. The gains are small, about 3e-6 and 7e-6.

No independent review has checked the codes. The validator is our own, with its own tests. The table is very active. In three weeks, 6,171 entries improved, and our first (16, 199) code was overtaken before we counted it. These results can be overtaken at any time. The codes are not yet submitted to the maintainer of the table.

*Code and data: available on request.*
