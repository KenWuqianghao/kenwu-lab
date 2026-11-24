---
title: An emulated Pentium 66 reaches 2700 on Carlini's chess scale, as a point estimate
date: 2026-11-18
tags: chess, emulation, games
status: Not audited
summary: Cfish on an emulated Pentium 66 scored 2745 on Carlini's scale at 10 s per move over 200 games. The 95 % interval is 2592 to 3004.
---
In November 2026 Nicholas Carlini showed that a tuned Stockfish port on a real Pentium Pro 200 plays at 2846 Elo at 1 s per move and 3109 at 10 s. We asked what is the slowest PC on which a chess engine reaches 2700, the figure often given for Deep Blue. We use Carlini's own engine-against-engine scale, so "2700" here means 2700 on his scale only.

The engine is Cfish, a C port of Stockfish with the classical evaluation. It runs as a 32-bit DJGPP program under FreeDOS inside the 86Box emulator, with its default settings and one thread. Emulated time moves only when the harness steps the emulator, so host load does not change the engine's clock. 86Box runs some CPUs faster than real hardware. Each machine therefore gets a time factor k from chess code, and the engine gets 10 s / k of guest time. For the Pentium 60, 66 and 75, k = 1.46 comes from a family rule, not from a measurement on each machine. The opponents are Stockfish 17.1 anchors on the host (one thread, Hash 16 MB, fixed depth). Each opening from `8moves_v3` is played twice with colours swapped. We mapped our pool Elo to Carlini's scale with three Crafty 11.13 points that he published.

At 10 s per move, an emulated Pentium 66 (1993) scored 2745 over 200 games (59 wins, 76 draws, 65 losses). A Pentium 75 scored 2767. The next slower machines scored below 2700. The 486DX4-100 got 2680 (200 games) and the Pentium 60 got 2666 (40 games). At 1 s per move no emulated machine reached 2700. The fastest, a Pentium II 450, scored 2630. Cfish is not Carlini's tuned port. On an emulated Pentium Pro 200 at 1 s it scored 2556, against his 2846 on real hardware.

An independent audit reviewed the Elo method before the claim runs and found serious problems, which the project fixed. No audit covered the final numbers.

The joint 95 % interval for the Pentium 66 is 2592 to 3004, so 2700 is reached as a point estimate only. The order of the Pentium 66, Pentium 75, 486DX4-100 and Pentium 60 is inside the noise. A direct match against Crafty gave a value about 200 higher. All machines are emulated, and the host-load check has no recorded result.

*Code and data: available on request.*
