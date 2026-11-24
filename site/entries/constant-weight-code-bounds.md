---
title: Lengthening plus clique search gives 26 unsubmitted bounds for constant weight codes
date: 2026-11-10
tags: maths, optimization, data
status: Checked
summary: One lengthening step plus a maximum clique search gives A(43,8,8) >= 5,830 against the table's 5,418, one of 26 unsubmitted lower bounds.
---

A binary constant weight code is a set of 0/1 words of length n, each with exactly w ones, where any two words differ in at least d positions. A(n,d,w) is the largest possible size of such a set. Andries Brouwer's table "Bounds for binary constant weight codes" has held the best known values for decades. 760 of its 1,437 entries are still open, and in 2026 several contributors ran automated searches on them.

We used one simple method. Take the best known code for length n-1 and add a zero coordinate. Then add as many words as possible that use the new coordinate. This second step is a maximum clique problem on the graph of compatible words. Branch and bound solves it first, then tabu search. Each gain is chained into the next length.

37 codes are staged. At the count on 2026-11-10, 26 of them were still strictly above the table's lower bound, by 2,119 codewords in total. The largest gain is A(43,8,8) >= 5,830 against the table's 5,418, which is 7.6 %. Other gains include A(50,6,6) >= 11,123 against 10,825, A(51,6,6) >= 11,819 against 11,354 and A(52,6,6) >= 12,619 against 12,220. The productive families are A(n,8,7), A(n,8,8), A(n,10,8) and A(n,6,6).

Many chains start from table entries found by other contributors, among them W. Echols, J. Boisclair and C. Lysenstoen. Our step only extends their codes. Plain bit-swap tabu search is the method of the 2026 searches by Echols and by C. D. Rosin, so we chose lengthening instead.

Two independent checkers test each file for length, weight, duplicate words and minimum distance, and they must agree. A third checker in C++ re-read the two largest gains. For this page we also re-checked the A(43,8,8) file with a separate short script. It has 5,830 distinct words of weight 8 with minimum distance 8.

Nothing has been sent to the table maintainer, so none of these codes is in the table. The target also moves. Between 2026-09-29 and 2026-11-10 other contributors overtook 11 of the 37 entries, often by one word. Each number is valid only against the page snapshot of its count date. The method fails where the code at n-1 comes from an algebraic construction instead of a search.

*Code and data: available on request.*
