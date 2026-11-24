---
title: A sperm whale coda table rebuilt byte for byte from 62,717 bytes
date: 2026-11-23
tags: compression, data
status: Audited
summary: A small C decoder and its payload rebuild the 747,518-byte coda table of Sharma et al. 2024 from 62,717 bytes, against 134,336 for xz -9e.
---

Sharma et al. (2024) published a table of 8,719 sperm whale codas recorded off Dominica. A coda is a short pattern of clicks. Each row of the 747,518-byte CSV gives the date, the whale, a coda type label and the time between consecutive clicks.

We asked how small a self-contained C program can be that prints this file again, byte for byte. The score is the payload size plus the `xz -9e` size of the decoder source. The decoder reads the table as typed columns and codes each field with an adaptive arithmetic coder. It predicts each click interval from recent codas with the same rhythm.

An independent audit rebuilt the decoder and the payload and got 62,717 bytes in total. `xz -9e` needs 134,336 bytes. A second file of the same study, with whale dialogues, came to 49,824 bytes. A later run of the same method reached 59,453 bytes for the coda table and 47,293 bytes for the dialogues (against 95,416 for `xz -9e`). Nobody has reproduced the later run independently.

Most of the gain comes from the file format. In the later run, typed columns alone save 138,433 of the 172,642 bytes saved. Of the remaining bytes, 90 % are click timing, 53,332 bytes. Of these, 23,793 bytes are digits below one millisecond. No model that we tried made those digits cheaper than the file prints them.

Control analyses shuffled rows, whale labels or the intervals inside each coda. After these controls, only one result is about the animals. Codas with the same number of clicks share a pattern of intervals, which is the known coda rhythm. Other gains depend on row order or on how the annotators assigned labels, and this data cannot separate those causes. The same method also beats `xz -9e` on humpback song, Bengalese finch song, fruit bat calls and English text. The costs per unit do not compare across species, because each corpus has its own units and labels.

The audit also found two holes in the evaluator. The current result does not use them, and a later change closes them. The model was selected on the same file that it is scored on. The baseline is weak, and we did not run a context-mixing compressor such as `paq8px` or `cmix`.

*Code available on request. The data is third-party and is not redistributed.*
