---
title: A rule-based web extractor finishes just below the WCXB leader on the test split
date: 2026-10-20
tags: tools, data
status: Checked
summary: marrow scores word-level F1 0.8963 on the WCXB test split, below the published 0.903 for rs-trafilatura. Its lead in one harness is not significant.
---
Web main-content extraction takes a web page and keeps the article, forum posts or product description. It drops menus, footers and ads. WCXB is a 2026 benchmark of 2,008 human-reviewed pages of seven types. It scores an extractor by word-level F1 against the reference text. The leader is rs-trafilatura, a hybrid of rules and machine learning by the benchmark's author.

We asked if a rule-based extractor with no model can take the top. marrow is written in Python with one dependency, selectolax. It detects the page type and uses rules for each type, such as forum threads, product pages, card grids and article tails. We kept each of thirteen rule changes only if it improved a part of the dev split. The 511-page test split was used only for reports.

It did not take the top. On the held-out test split, marrow scores 0.8963. The paper gives 0.903 for rs-trafilatura, and its README gives 0.893. When we run rs-trafilatura 0.1.1 in the same harness, it scores 0.8905. So marrow leads in our harness by 0.0058, with a standard error of 0.0081. That lead is not significant. rs-trafilatura also wins on more single pages (315 against 146). marrow's mean comes from large wins on listings and collections.

On the dev split (1,497 pages), marrow scores 0.8657 against the published 0.859. That number is weaker evidence, because we chose every rule on most of these pages.

All scores come from the benchmark's own evaluate.py. Our run of rs-trafilatura gave byte-identical predictions on a repeat run. The test split was read twice, and no rule was chosen on it. A later learned model that drops lines gained 0.0073 out of fold. But 32 % of that gain came from three empty pages on one site, so our pre-registered rule rejected it.

The fair summary is close to the leader, faster, and with no model. marrow takes 21 to 30 ms per page, against a published 44 ms for rs-trafilatura. The WCXB data is under CC BY 4.0.

*Code and data: available on request.*
