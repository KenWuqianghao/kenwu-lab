---
title: Linux boots on an emulated Commodore 64 in 5.2x fewer cycles than the 2023 build
date: 2026-11-24
tags: emulation, optimization, code-golf
status: Checked
summary: The same Linux image reaches the login prompt in 24,619,127,030 6502 cycles, against the 127,396,453,645 published in 2023.
---

semu-c64 is a small RISC-V emulator, published on GitHub as onnokort/semu-c64. It is compiled for the 6502 with llvm-mos and boots Linux on a Commodore 64 with a 16 MB RAM Expansion Unit (REU). In 2023 the author published the boot time to the `buildroot login` prompt. It was 127,396,453,645 6502 cycles. The author wrote that a gain of about 10x might be realistic. We found no faster fork as of 17 November 2026.

## What we found

We kept the guest work fixed, with the same v0.0.2 kernel and root file system. The best build boots in 24,619,127,030 cycles. That is 5.175x fewer than the published number and 5.202x fewer than the v0.0.2 release binary in our harness (128,063,766,010).

Most of the gain came from a hand-written 6502 fast path for the common RISC-V instructions. A 64-entry TLB and 23 measured assembly changes gave the rest. Every attempt, kept or reverted, has a row in a decision log.

## How it was checked

Before any change we froze a harness. It is the author's cycle-counting `kernalemu`, plus 1 cycle per byte of REU DMA. A change passes only under these conditions:

- The console log is byte-identical.
- The guest runs the same 94,801,292 RISC-V instructions.
- The final 16 MB guest state has the same hash as a native reference build.
- A second kernel image that we did not tune on boots (v0.0.1, 35,590,639,418 cycles).
- 62 of 62 RISC-V tests pass.

An independent audit of the harness, before the optimisation, found four defects. We fixed them before the climb.

As a second check, the same binary ran in the VICE `x64sc` 3.10 emulator, which also counts video bad lines, interrupts and KERNAL time. It reached the login prompt at 26,431,944,230 clock cycles, 7.45 h at 985,248 Hz. The final guest state was the same.

## Limits

We did not run it on a real C64, so the times are for emulators only. The 2023 boot on real hardware took about 150 G cycles, more than the published emulated count. No audit covered the final build. The headline is for one kernel image. The code is MIT, as upstream. The kernel and root file system images are the upstream author's releases.

*Code and data: available on request.*
