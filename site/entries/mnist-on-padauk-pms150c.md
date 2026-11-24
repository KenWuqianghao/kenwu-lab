---
title: A 2-bit network on a Padauk PMS150C classifies 94.68 % of MNIST digits in simulation
date: 2026-11-17
tags: ml, code-golf, optimization
status: Not audited
summary: A hand-written assembly engine fits a 64-32-16-10 network in 907 ROM words and scores 94.68 % on 8x8 MNIST in the ucsim_pdk simulator.
---
The Padauk PMS150C is a very small 8-bit microcontroller. It has 1014 usable words of program memory, 64 bytes of RAM and no multiply instruction. In 2024, cpldcpu published BitNetPDK, a digit classifier for this chip, based on the BitNetMCU project. Its README states 90.1 % test accuracy on MNIST images scaled to 8x8 pixels. We asked how much accuracy fits in the same limits.

We built a test harness in the ucsim_pdk 0.9.9 simulator. It runs a program on all 10,000 MNIST test images and checks the ROM size, the RAM use and the allowed instructions. It uses the BitNetPDK 8x8 preprocessing without change.

We wrote an assembly engine and trained a 64-32-16-10 network with 2-bit weights from the set {-2, -1, 1, 2}. Training uses the exact integer arithmetic of the chip. The final program uses 907 of 1014 ROM words and 58 of 64 bytes of RAM, including 8 stack bytes. It needs 93,024 cycles per image on average. It classifies 9,468 of 10,000 test images correctly (94.68 %).

The simulator and a bit-exact Python model agree on all 10,000 predictions. We used the test set once, after we chose the model on a separate validation split. About 50 other configurations that fit the ROM gave 93.8 % to 95.0 % on validation. Seed noise is about 0.4 points, so we stopped.

All results come from the simulator. We did not run the program on a real chip. Some tricks in the engine depend on hardware details that the simulator does not model, such as the high byte of `idxm` and a return-address trick with `pushaf`. The RAM count of 58 bytes is from the design. The harness checks the engine's RAM only through a guard fill above address 0x3F. No independent review was done.

*Code and data: available on request.*
