---
title: All 6573 Bad Apple!! frames, bit for bit at 64x48, in 91,047 bytes
date: 2026-11-23
tags: compression, code-golf, data
status: Audited
summary: A compressed C decoder plus its payload reproduce our 1-bit 64x48 frames exactly in 91,047 bytes (audited); a newer version needs 90,227.
---

"Bad Apple!!" is a shadow-art video that people port to almost every small device. We asked how few bytes it takes to reproduce every frame exactly.

## Target and score

We decoded the Niconico original (sm8628149) and took the luma plane. We averaged it down to 64x48 pixels and set each pixel to white at a mean of 128 or more. That gives 6573 frames of 2,524,032 bytes. The score is the payload plus the `xz -9e` size of the C decoder source, so data cannot hide in the decoder for free. For scale, `xz -9e` of the frames alone gives 234,952 bytes.

## What we found

The decoder is a context-mixing coder in the style of paq. It predicts each pixel from nearby pixels, from motion, and from a small neural network that learns while it decodes.

The audited version totals 91,047 bytes. That is 87,663 bytes of payload and 3,384 bytes of compressed C. It decodes in about 85 s on one Apple M1 core with about 200 MB of RAM.

A newer version totals 90,227 bytes (86,899 payload, 3,328 compressed C). It needs about 200 s of CPU and 216 MB, and it is not audited.

## How it was checked

An independent audit decoded the video again with its own script and got the same reference hash. It confirmed the total. It also found three ways to bypass the evaluator sandbox. The decoders do not use them, but only a reading of the code shows this. A fixed evaluator has not yet run on the final submission. The audit also found two sites of undefined behaviour in the decoder. They did not change the output in the part of the run that the audit tested.

## Limits

This is a lossless result for one 1-bit conversion, so it does not compare with lossy ports. cnlohr's badderapple fits a lossy, 3-level, perceptually tuned 64x48 version with sound and player into 64.5 kB of flash on a microcontroller with 8 KB of RAM. Our decoder needs 200 MB of RAM on a desktop. A random search on this video tuned the contexts, so this is not a general codec. On 23 November 2026 we found no smaller published bit-exact result, but the search did not cover pouet.net.

Music by ZUN, arranged by Alstroemeria Records (nomico). Shadow-art video by Anira.

*Code available on request. The data is third-party and is not redistributed.*
