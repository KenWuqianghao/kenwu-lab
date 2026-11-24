---
title: A 1,084-byte learned decision tree solves king and pawn against king exactly
date: 2026-11-23
tags: chess, code-golf, ml
status: Audited
summary: A 1,084-byte C program (a learned tree plus a one-ply look-ahead) and a 489-byte retrograde solver both make 0 errors on 331,352 KPK positions.
---
King and pawn against king (KPK) is the simplest chess ending that is not trivial. Engines store it as a table of a few kilobytes or build one at start-up. We asked how short a C program can be that gets every position right, as a win or a draw, with either side to move.

The test set is 331,352 positions, under the standard engine convention (pawn on ranks 2 to 7, kings not adjacent, side not to move not in check). 776 of these cannot occur in a game. A retrograde generator gives the answer for each position, and it agrees with the Syzygy KPvK tablebase on all of them.

Textbook rules are far from exact. The rule of the square alone is wrong in 51,854 positions (15.65 %). Our hand-written rules with exceptions still made 18,254 errors.

The best program under an instruction budget that forbids building a table at start-up is `rules/t16.c`, 1,084 bytes. It is a machine-learned decision tree over 16 chess features. They include the rule of the square, king races to the stop square and the queening square, opposition parity, and offsets of each king from the pawn. The tree was learned from the complete solved table for White to move. For Black to move, the program tries each black king move and asks the tree, a one-ply look-ahead. It makes 0 errors.

With no restriction, `any/a08.c` is 489 bytes. It solves the ending by retrograde analysis at start-up. It treats a promotion as a win unless the black king captures the new piece at once. That shortcut ignores stalemate and underpromotion, and it is still exact for KPK.

Learned exact trees for KPK are not new. Shapiro and Niblett (1982), "Automatic Induction of Classification Rules for a Chess Endgame", Advances in Computer Chess 3, already induced exact KPK trees. Our contribution is the byte count and the exhaustive check. For scale, the tree is about 7 times smaller than the 7,824-byte Syzygy KPvK file.

An independent audit re-ran the evaluator. It got 1,084 bytes and 0 errors for the tree, 489 bytes and 0 errors for the solver, and 0 mismatches between our reference and Syzygy. The instruction budget was measured on one Apple M1 machine. The size limit on static data does not prove that no table hides in code constants.

*Code and data: available on request.*
