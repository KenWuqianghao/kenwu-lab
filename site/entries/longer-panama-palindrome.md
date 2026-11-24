---
title: A 27,794-word "a man, a plan" palindrome, 1.5% below a proven phrase bound
date: 2026-11-24
tags: optimization, maths, games
status: Audited
summary: 27,794 words and 21,729 phrases under Norvig's rules, against his 21,012 words; no such palindrome can have more than 22,050 phrases.
---

In 2002 Peter Norvig started a search for the longest palindrome that begins "a man, a plan" and ends "a canal, Panama". His 2016 version has 21,012 words and 16,111 phrases. Each phrase comes from his list `npdict.txt`, and no phrase can occur twice. A later GitHub project by EricSpencer00 (September 2026) got 21,088 words and 16,168 phrases under the same rules, plus one stricter rule. That result passed Norvig's length before ours.

## What we found

With the same list and the same rules, we got 27,794 words and 21,729 phrases (122,679 letters).

The method is a change of view. We build the palindrome from both ends. The state is the unmatched text in the middle, and each phrase is an edge between two states. A palindrome is then a walk that uses each phrase at most once. This is an integer program on a graph of 135,443 states and 426,584 edges.

The linear relaxation of this program has the optimum 22,046.41 edges. With the 4 fixed frame phrases, no palindrome under these rules can have more than 22,050 phrases. Our result is 321 phrases (1.5 %) below this bound. We found it with integer programs restricted to the edges that LP solutions use (HiGHS 1.16.0, one thread). The gains got smaller at each step (+89, +39, +7, +2 phrases).

## How it was checked

An independent audit wrote a new checker from Norvig's `pal3.py`, not from our checker. It got the same counts for our file, for Norvig's text and for the September 2026 text. It also built the graph again from zero and got the same size and the same LP optimum. An exact dual certificate proves the bound. Anyone can check the palindrome with `python3 -I verify.py results/best.txt`.

## Limits

The bound is for phrases only. We have no bound on words. The bound holds only for the frozen rules, for example letters-only keys, distinct keys and the fixed 4-phrase frame. Each integer program stops at a time limit, so a rerun on another machine can give a different palindrome. The phrase list is Norvig's.

*Code and data: available on request.*
