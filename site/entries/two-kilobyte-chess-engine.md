---
title: A 1,949-byte chess engine lost to micro-Max 4.8 by 73.7 Elo
date: 2026-11-17
tags: chess, code-golf, games
status: Not audited
summary: A 1,949-byte UCI engine scored 584-1002-414 against micro-Max 4.8 in 2,000 games (-73.7 ± 13.7 Elo). The target was +150 Elo.
---
How strong a chess engine fits in 2 KB? We set four tracks, 2,048 and 1,024 bytes, each as raw C source or as a compressed self-extracting shell script in the style of the TCEC 4k contest. Each engine must play full chess rules, speak a small subset of UCI, and pass 41 perft positions. All bytes count.

We set a test before the start. A 2,048-byte build must beat micro-Max 4.8, a well-known small engine by H.G. Muller, by 150 Elo or more over at least 2,000 games. The test failed. The best 2,048-byte script (1,949 bytes) scored 584 wins, 1,002 losses and 414 draws against micro-Max, at 5 s + 0.05 s per game on a Steam Deck. That is -73.7 ± 13.7 Elo.

We also rated the engines in a pool with micro-Max pinned at 1853 and three node-limited Stockfish anchors. The 1,949-byte script rated 1791. The raw-C 2,048-byte engine rated 1732, the 1,024-byte script 1448, and the 1,024-byte raw-C engine 1029. The pool ratings do not agree well with the head-to-head result, so the head-to-head is the main number.

Changes were accepted only by a sequential probability ratio test (SPRT) in self-play. Two more changes passed after the head-to-head match, reverse futility pruning (+51 Elo) and use of the clock increment (+25 Elo). They were not tested against micro-Max, because the test machine was given back.

An independent audit checked the byte counts, the perft results, the SPRT setup and the pool arithmetic. It also found that matches which stopped early were saved as complete results. The harness was fixed and the affected matches were played again. The head-to-head result above comes from that new run, which the audit did not see. The audit also found that micro-Max does not use the 0.05 s increment, which gives it about 4 % less thinking time. This favours our engine, and we did not measure the effect on Elo. The Steam Deck was heavily loaded during the matches.

This is a clean negative result. Self-play gains of +25 to +70 Elo per change did not close the gap in the time available. We did not survey other size-limited engines, so we make no claim about strength per byte.

*Code and data: available on request.*
