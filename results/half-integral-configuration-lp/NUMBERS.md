# Numbers in the paper and their sources

Check outputs are the files in `checks/expected/` (each equal to a fresh run by
`bash checks/ci.sh`). "Lean" names a theorem of `lean/Solution.lean`.

| Number in the paper | Source |
|---|---|
| 12 machines, 20 jobs, sizes 1 (12 point jobs) and 3 (8 fillers) | `checks/instance.json`; `vcheck_main.txt` ("n=20 m=12"); Lean `P0` |
| Each machine allows 5 jobs (3 points, 2 fillers); each job is allowed on 3 machines | `checks/instance.json` (`M`); `RESULT.md` |
| Total processing time 36 = 12 · 3 | `certificate.txt` steps 2 and 3; Lean `sum_p` |
| 36 ≤ 12T ≤ 24 for T ≤ 2, so LP(P*) = 3 | `certificate.txt` step 2 ("36 > m(T-1) = 24"); `vcheck_main.txt` ("CLP(P,T-1) feasible (exact simplex): False"); Lean `not_feasible_of_le_two`, `isLeast_three` |
| Value 1/3 on each configuration of load 3; 3 such configurations per machine | `checks/instance.json` (`x`, 36 entries of 1/3); `certificate.txt` step 1; Lean `card_full`, `cover_full`, `x0_mem` |
| 36 full configurations, each with 0 or 3 point jobs of copy 0 | `certificate.txt` step 4; Lean `full_mod3` |
| Σ w_j = 4, 2 · 4 = 8, not a multiple of 3 | `certificate.txt` step 5; Lean `sum_w0`, `no_half_integral` |
| 10 configurations per machine at T = 3 | `vcheck_main.txt` |
| 2227 search nodes for P*, no half-integral point; control at T = 4 finds one | `vcheck_main.txt` ("search nodes: 2227", "control T=4: True") |
| IP(P*) = 4, gap 4/3 | `ip.txt` (makespan 4); no integral point at T = 3 by the main theorem |
| 2/3 · 4c fillers, integer for c = 3, so 8 fillers | arithmetic (paper, Section 3.1) |
| Second instance: 5 machines, 14 jobs, LP(P) = 14, the list p and the sets ℳ_j | `checks/instance_small.json`; `vcheck_small.txt` ("n=14 m=5 T=14") |
| 68 > 5 · 13 = 65 | `vcheck_small.txt` ("volume=68", "volume > m(T-1): True"); `small.txt` step 2 |
| 12 nonzero entries, values 1/3 and 2/3 | `checks/instance_small.json` (`x`); `ci.sh` checks both |
| 9, 74, 105, 49, 70 configurations at T = 14 | `vcheck_small.txt` |
| 155269 search nodes, no half-integral point | `vcheck_small.txt`; `small.txt` step 3 (second search) |
| 68 < 70 = 5 · 14 (volume not tight) | arithmetic |
| 400 random instances per seed; 282 and 281 with a half-integral point | `control1.txt`, `control2.txt` |
| Gap between 3/2 and 11/6 (restricted assignment); 3/2 and 1.749 (graph balancing) | the source, `work/src/src.pdf`, pages 23:8 and 23:9 (statements of the source, with its references [1], [14], [15], [16], [27]) |
| Conjecture 10 on page 23:10; definitions on page 23:8; v1 of 17 Sep 2026 | the source PDF (`pdftotext -layout`, problem folder `work/src/src.txt`, lines 429-489 and 582-599) |
| Jansen-Rohwedder graph balancing preprint of 2 Nov 2018 | arXiv API record of 1811.00955 (published 2018-11-02) |
| Svensson, STOC 2011, pages 617-626 | Crossref record of doi:10.1145/1993636.1993718 |
| Lean: compiles in about 18 s; axioms propext, Classical.choice, Quot.sound | `lake env lean lean/Solution.lean` from the shared workspace (real 18.6 s; output line `'HalfIntegralCLP.not_conjecture10' depends on axioms: [propext, Classical.choice, Quot.sound]`) |
| README times: 0.4 s, 1.6 s, 3 s, 6 s; comparator about 90 s | measured runs on the Steam Deck (vcheck main 0.39 s, vcheck small 1.65 s, control 3.0 s, ci.sh 6.1 s, lean-compare 87 s) |

## Issues left open by VERIFY.md (round 1) and where they are fixed

| Issue | Fix |
|---|---|
| 1. Quote "not confirmed against the PDF" | The paper cites the PDF v1, page 23:10 (reference [1], the introduction and Section 2 cite pages 23:10 and 23:8). `STATEMENT.md` and `RESULT.md` now say that the PDF confirms the quote. |
| 2. Not formalized in Lean; must not say "proved in Lean" | Changed by this stage: `lean/Solution.lean` now proves `¬ Conjecture10` from the definitions (paper, Section 5.1). `lean-audit` and `lean-compare` pass. So the tier is "Proved in Lean". The paper gives the 4-step hand proof (Section 3.1) and says that the finite facts use `decide +kernel`. The second counterexample is marked as not in Lean (Section 4 and Limits). |
| 3. No third-party source names Conjecture 10 | Paper, end of Section 1 ("We know of no other work that discusses Conjecture 10") and Limits, bullet 4. |
| 4. `check_solver.py` needs numpy and scipy, not recorded | `check_solver.py` (floating-point HiGHS diagnostic) is not in the release. All checks in `checks/` use only the standard library (`checks/requirements.txt`, `checks/README.md`). |
| 5. Configurations have load at most T; sub-full configurations | Paper, Section 2 ("Its load is at most T, not necessarily equal to T") and Lemma 3 with the paragraph after it (configurations of load less than 3 exist and get weight 0 by tight volume). The paper does not use the sentence "its only fractional perfect matching uses weight 1/3". |
| 6. Only 2 counterexamples have exact checks | The paper claims exactly two counterexamples (Theorem 1 and Section 4). It does not mention the 7 HiGHS reports of the search. `checks/README.md` says that the other search counts are not used. |

VERIFY.md section 4 gives "half-integral point: False (414 nodes)" for the main instance.
The rerun shows 2227 nodes for T = 3; 414 nodes is the control at T = 4
(`vcheck_main.txt`). The paper uses 2227.
