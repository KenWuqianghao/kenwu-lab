---
title: A mate in 5 that Stockfish 19 does not find in a billion nodes (1 thread, 16 MB hash)
date: 2026-11-24
tags: chess, games, optimization
status: Not audited
summary: With 1 thread and a 16 MB hash, Stockfish 19 reports no mate in 1,000,000,000 nodes; a mate in 3 needs 273,345,719 nodes.
image: assets/stockfish-blind-mates/m5.svg
---

Strong chess engines find most short mates almost at once. We looked for the opposite. We wanted legal positions with a proven forced mate in 3 to 6 moves that Stockfish 19 does not see for a long time. The score of a position is the number of search nodes until Stockfish first reports the correct mate.

We froze the rules before the search. Stockfish 19 ran with 1 thread and a 16 MB hash, in a fresh process for each position. Only exact mate scores count. All numbers below use these settings unless a different setting is given.

## What we found

![Chess diagram of the mate-in-5 position, White to move](assets/stockfish-blind-mates/m5.svg)

White mates in 5 with 1.Nc5. Stockfish 19 (1 thread, 16 MB hash) reports no mate in 1,000,000,000 nodes. After one billion nodes it plays 1.Nb8 at +6.06 (depth 42).

![Chess diagram of the mate-in-3 position, White to move](assets/stockfish-blind-mates/m3.svg)

White mates in 3 with 1.a5. Stockfish 19 (1 thread, 16 MB hash) reports the mate at 273,345,719 nodes.

At 3 million nodes Stockfish already plays the key move 1.a5, but it shows +3.72 and no mate.

All positions come from one family. The search started from line 40 of vondele's public `matetrack` suite, a mate in 3 that took 469,672 nodes. Small edits and two retracted move pairs gave the final positions.

## How it was checked

Two independent mate provers must agree on the mate length. They are Chest 3.19 and a solver written for this project. A proof game must reach each position from the start position with legal moves, and promoted pieces are not allowed. The proof games replay to the exact positions in 130 to 238 plies. With 1 thread, the scores were the same in two runs for 10 of 10 positions. Stockfish was not run again for this write-up, and no independent audit exists.

## Limits

The numbers hold for this engine build and these settings only. With a 1 GB hash, Stockfish finds the mate in 5 at 258,219,159 nodes. With 8 threads it finds it at 812,585,041 nodes (one run, not deterministic). The mate in 3 needs 273M to 936M nodes in all three settings. We did not test other engines. We did not search the literature for similar positions.

*Code and data: available on request.*
