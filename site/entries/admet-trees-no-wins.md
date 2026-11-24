---
title: Gradient-boosted trees lead 0 of 22 TDC ADMET tasks on the measured test run
date: 2026-11-10
tags: ml, data, optimization
status: Checked
summary: A CPU-only tree pipeline leads no task of the 22-task TDC ADMET board on test. The nearest gaps are 0.003 to 0.010.
---
The TDC ADMET Benchmark Group has 22 drug-property prediction tasks with a public leaderboard. We asked if a classical, CPU-only pipeline can take a #1 row. The pipeline puts fingerprints and descriptors into gradient-boosted trees. It uses one configuration for all tasks, and we made every choice on the scaffold validation split.

First we ported MapLight, an existing board entry, to check the harness. It reproduced the published test row on 20 of 21 comparable tasks within 0.007. Two tasks differ. ppbr is 7.734 against 7.660, and clhepa is 0.478 against 0.466. That reproduction is the only test run in the project.

Then we added one change per iteration. An average of CatBoost, LightGBM and XGBoost gained +0.0108 on the 22-task validation mean. A rank-target variant and a Tanimoto-kernel member gained nothing (-0.0010 and -0.0023).

The result is negative. On the measured test run, no task beats its #1 row. The nearest gaps are vdss -0.003, bbb -0.004, ames -0.005, clmicro -0.005 and herg -0.010. We also shifted that test run by the validation gain of the ensemble. This projection puts four tasks (clmicro, vdss, herg, ames) just above their #1 value, each inside one to two projection standard errors. The ensemble itself has no test run, so these four leads are projections and not measured results.

The far tasks (CYP inhibition, lipophilicity, DILI) are 9 to 65 standard deviations behind. The rows that lead them use a second molecular representation or multi-task transfer, which this pipeline does not have.

All scores use the official TDC Evaluator. The board values come from a dated snapshot of the official leaderboard pages (2026-09-27). Label-permutation leak tests pass on each candidate, and a planted leak fails as it must. A rebuild on a second machine reproduced all 44 validation rows. Data and task definitions are from TDC (Huang et al., 2021).

*Code available on request. The data is third-party and is not redistributed.*
