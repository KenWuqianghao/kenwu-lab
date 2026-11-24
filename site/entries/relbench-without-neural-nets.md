---
title: A CPU-only LightGBM model scores 0.7742 on RelBench, above the reference GNN
date: 2026-11-10
tags: ml, data
status: Checked
summary: Time-cut relational features plus LightGBM score a 12-task mean test AUROC of 0.7742 on RelBench, against 0.7283 for the reference GNN.
---
RelBench is a benchmark for prediction on relational databases. One example task asks if a driver finishes a Formula 1 race. Another asks if a user churns on an e-commerce site. Its public leaderboard ranks systems by the mean test AUROC over 12 classification tasks. The reference model is a graph neural network (GNN) at 0.7283. All rows above it use neural networks or language models.

We asked if a model with no neural part can pass the GNN. Our system, reldfs, builds features automatically from the database schema. For each label row, it aggregates over foreign-key paths. It uses only rows dated strictly before the prediction time of that row. Then LightGBM fits the features on a CPU.

A leak check rebuilds the features from a database truncated at each prediction time and requires identical values. A deliberately planted leak fails this check.

All choices were made on the validation split. The filed version scores 0.7742 on test. The maintainers' CI gave the same number on RelBench issue #406. That is 0.046 above the GNN and 0.035 above the GNN+LightGBM row (0.7389). The official LightGBM row is 0.631. On the board of 2026-11-10, our row is 10th of the listed systems. The top row is 0.8119.

A later version scored 0.7785 on one local test run with the official evaluation code. It is not filed. That version, and the later rounds, were built after we saw the test scores of the filed version. So they are weaker evidence than the 0.7742.

We did not search the literature beyond the leaderboard. The board is well above us at the top, and every row above us uses a neural part.

*Code available on request. The data is third-party and is not redistributed.*
