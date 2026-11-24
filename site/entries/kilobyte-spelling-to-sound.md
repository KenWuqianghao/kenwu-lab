---
title: A 1,024-byte C program converts English spelling to phonemes at 15.3 % error
date: 2026-11-24
tags: code-golf, ml, data
status: Checked
summary: A 1 KB C program gets 15.260 % phoneme error on validation words, against 21.020 % for the 1976 NRL rules scored with a Python port.
image: assets/kilobyte-spelling-to-sound/frontier.svg
---
English spelling is a poor guide to sound. We asked how much of it a very small program can learn. Each program is one C file of at most 512, 1,024, 2,048 or 4,096 bytes. It reads a word and prints its phonemes in the code of the CMU Pronouncing Dictionary (CMUdict).

The 1 KB program is a 507-byte interpreter and a 517-byte string of about 190 rules. Each rule matches some letters with a left and right context and gives the sound. A greedy search wrote the rules. At each step it proposed rules from the remaining errors, ranked them by errors fixed minus errors caused per byte, and kept the best one.

On a sealed test of 11,663 words that the search never saw, the 1 KB program has a phoneme error rate (PER) of 15.338 %. It gets 41.224 % of words exactly right. On the validation split it gets 15.260 %. The 1976 Navy (NRL) rules of Elovitz et al., with about 2,288 bytes of rule data, get 21.020 % on the same validation split. More bytes help less and less. Sealed PER is 22.876 % at 512 bytes, 12.941 % at 2 KB and 11.582 % at 4 KB. Large learned models reach about 5 % with megabytes of parameters, on other splits.

![Line chart of validation phoneme error rate against program size from 512 to 4,096 bytes, with the NRL rules and a one-letter-one-phoneme baseline marked](assets/kilobyte-spelling-to-sound/frontier.svg)

Validation error rate for each size limit, with two baselines for scale.

The most useful rules per byte are consonant pairs (`ng`, `sh`, `ch`, `th`), double letters, and final `s` as Z. The search made `e` and `h` silent by default and added rules to say them. Common words are harder than rare ones. Weighted by word frequency, the error rate is 29.195 % on validation. Words such as "one", "two" and "the" keep old spellings that no short rule covers.

The test set was read once per size, after the last kept change. We re-ran the evaluator on the validation split and got the same 15.260 %.

The NRL baseline was scored with a Python port, not a built C program, and its byte count is an estimate. We did not search for earlier size-limited programs of this kind. The dictionary is CMUdict (BSD licence, Carnegie Mellon University).

*Code and data: available on request.*
