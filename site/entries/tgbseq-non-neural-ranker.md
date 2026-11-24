---
title: A non-neural ranker scores above the TGB-Seq board on two datasets, not yet submitted
date: 2026-11-10
tags: ml, data
status: Checked
summary: A CPU-only ranker gets test MRR 0.6458 on GoogleLocal and 0.6833 on YouTube, against board leaders at 0.5413 and 0.5887. Not yet submitted.
---
TGB-Seq is a temporal link prediction benchmark (ICLR 2025). Given the history of a user up to time t, the task is to rank the next item for that user against 100 negatives. The benchmark removes repeated edges by design, so a memory of past pairs does not help. Its leaderboard lists eight temporal graph neural networks.

We built a ranker with no neural network. It uses signals that are standard in recommender systems. They are popularity with time decay, item co-occurrence, sequential transitions, two-hop neighbours and low-rank SVD similarity. Some features use the fact that the benchmark removed repeated edges. A conditional-logit model fitted on the end of the training period combines the signals, in minutes on one CPU core.

The candidate was fixed on validation and scored on test once, with three seeds. On GoogleLocal, the test MRR is 0.6458 ± 0.0010, against 0.5413 ± 0.0197 for TGN, the board leader. On YouTube, it is 0.6833 ± 0.0005, against 0.5887 ± 0.0012 for GraphMixer. That is a lead of about 0.10 MRR on both datasets.

These numbers use a per-timestamp view, where each query sees every event strictly before its own timestamp. The view matters. If the model sees updates only in batches of 200 events, GoogleLocal falls to 0.6044. That is still above TGN but below SGNN-HN (0.6288), a model reported only in the paper. In the batch-20 view, the score is 0.6161.

The scores come from the official TGB-Seq evaluator code, run as published, with the official test negatives. Our data cache matches the official loader element by element. A leak audit replaces every event at or after a cut time with fake events. The scores before the cut must stay bit-identical, and planted leaks must fail the audit. Every kept candidate passes.

The board has not changed since October 2024, and we did not search the later literature. The results are not yet submitted to the maintainers.

*Code available on request. The data is third-party and is not redistributed.*
