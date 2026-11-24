---
title: A 17-instruction Tierra genome fills the soup, but only by social replication
date: 2026-11-17
tags: code-golf, emulation, optimization
status: Audited
summary: The 17-instruction genome r17a fills the Tierra 6.02 soup on 13 of 13 seeds, but under 5 of about 18,500 births per run come from its own cell.
---

Tierra is an artificial-life system by Tom Ray. Small programs copy themselves in a shared memory called the soup. A common question is the size of the smallest program that can copy itself. Nehaniv (2002) designed `0018cln`, with 18 instructions, and called it the smallest known independently self-replicating Tierran. Askenazi's `0021aaa` has 21 instructions.

We built stock Tierra 6.02, turned mutations off and froze a test before any search. A genome passes if three generations of byte-exact copies occur within 3 million instructions on three seeds. We also wrote a fast simulator that matches stock Tierra birth for birth, and we searched near known genomes.

We found three small genomes. `r17a` has 17 instructions and fills the soup with about 1,900 cells on 13 of 13 seeds. But the mother's CPU finishes each birth by running the daughter's code. Only 0 to 4 of about 18,500 births per run come from a CPU in its own cell. This is social replication, as in `0021aaa`, and Nehaniv excludes it for `0018cln`. `c16a` has 16 instructions, but each cell makes only one daughter. Its lineage died out in 14 of 20 runs of 10 million instructions. `b20a` has 20 instructions and uses only its own templates, but it is also one-shot.

An independent audit rebuilt Tierra 6.02 from the same source archive and reproduced these numbers. It confirmed that the trace patch only prints and that the test cannot pass a non-replicator. It also gave the framing above. None of the three genomes is a like-for-like smaller replicator than `0018cln`.

We then added a stricter test that matches Nehaniv's claim, non-social and persistent. `0018cln` passes it. A search of 1,590,329,415 candidates at 16 and 17 instructions (6.9 CPU hours) found none that passed.

The searches cover only neighbourhoods of known genomes, in our simulator, with a short time budget. A slow replicator can be missed. So this is not a proof that no independent 17-instruction replicator exists. The stricter search came after the audit and has no independent check.

*Code and data: available on request.*
