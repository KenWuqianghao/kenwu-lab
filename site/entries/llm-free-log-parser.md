---
title: An LLM-free log parser ranks second to PIPLUP on all 14 Loghub-2.0 datasets
date: 2026-11-10
tags: tools, data, ml
status: Checked
summary: tally gets FGA 0.851 on all 14 Loghub-2.0 datasets against PIPLUP's 0.904. On the 9 datasets it was tuned on, it leads on FTA by 0.063.
---
Log parsing turns raw log lines into templates, for example "Connection from <*> closed". The Loghub-2.0 benchmark scores parsers on 14 systems. The strongest published parsers call a large language model (LLM) for each new template group. The best published LLM-free online parser is PIPLUP. We asked if a pure-Python parser with no LLM can match it.

We built `tally`. It is a Drain-style prefix tree with 22 generic token-shape masks and several merge rules. It uses the Python standard library only and one configuration for all datasets. It runs at 0.96 to 3.04 times the speed of Drain.

On all 14 datasets, `tally` gets FGA 0.851 and FTA 0.690. PIPLUP gets 0.904 and 0.697. That puts `tally` second on the published LLM-free table, and far below the LLM parsers (AdaParser with GPT-3.5 gets 0.965). These all-14 figures come from a second read of the held-out data. We label that read "not independent", because the last two rules were designed after the first read showed over-splitting.

On the 9 datasets where we chose every rule, `tally` gets FGA 0.903 and FTA 0.785, against PIPLUP's 0.899 and 0.722. The FTA lead of 0.063 holds on 8 of the 9 datasets. The FGA lead of 0.003 is small.

The gap on all 14 is not spread out. It is almost entirely Proxifier (0.323 against 1.000) and Apache (0.857 against 1.000), where our parser over-splits. Proxifier alone is 0.68 of the 0.74 summed FGA gap. Late candidates gave large gains on single datasets, but a pre-registered rule rejected each change that helped only one or two of nine datasets.

On Android and Windows, two systems that nobody here tuned on, `tally` gets FGA 0.941 and FTA 0.774. A tuned Drain gets 0.878 and 0.552.

All scores use the benchmark's own evaluation functions. Our Drain run matches the Loghub-2.0 paper within 0.001 on every dataset. The baseline numbers for PIPLUP and the LLM parsers come from their published tables.

*Code available on request. The data is third-party and is not redistributed.*
