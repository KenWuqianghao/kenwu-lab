# Numbers in the paper and their sources

Paths without a prefix are in this folder. Paths that start with `project:` are in the factory project repository (`problems/roller-coaster-odd-sum`).

| Number in the paper | Value | Source |
|---|---|---|
| Witness w | 8, 14, 3, 15, 6, 10, 2, 17, 7, 12, 1, 16, 5, 11, 4, 13, 9 | Botler–Netto Table 1 (`project:sources/botler_netto_2021.txt` line 158); Netto thesis Table 2.1 (`project:work/src/netto/netto.txt` line 1414) |
| t(w) | 798783 | Lean `fact_i`; `checks/t_definition.py` (`t = 798783`); `checks/check_lists.py` |
| Mirror sums of w | 17, 27, 7, 26, 11, 26, 3, 29 | `checks/t_definition.py` (`pair sums`) |
| Max t over Odd Sum permutations of [17] | 798775 | `data/logs/n17_oddsum_run.txt` (4 SUMMARY lines); `data/logs/v2_n17_oddsum_run.txt`; `checks/run_n17.py` |
| Odd Sum permutations with t = 798775 | 96 with π_1 ≤ 9; 128 with complements | same; `checks/check_lists.py` |
| Node counts of `oddsum_bb`, fact (ii) | 893550028, 893260703, 910073485, 841092770 | `data/logs/n17_oddsum_run.txt`; `data/expected.json`; VERIFY check 8 (same counts on rerun) |
| Time per process, fact (ii) | 943 to 1030 s | `data/logs/n17_oddsum_run.txt` (`seconds=1013, 1004, 1030, 943`) |
| Nodes of `v2_bb`, fact (ii) | 8.7·10^9 (2407779364 + 6298244618) | `data/logs/v2_n17_oddsum_run.txt` |
| Validation sets | 36 (n = 5..10), 50 (n = 5..9) | `data/logs/validate_bb_output.txt`; `data/logs/v2_validate_output.txt`; rerun in the write stage (below) |
| Ahmed–Snevily bound for n = 17 | 798471; their permutation has the Odd Sum property | `project:sources/ahmed_snevily_2013.txt` lines 63, 304–308; `checks/check_lists.py` |
| tmax(17), \|RC(17)\| | 798783, 128 | `data/logs/n17_all_run.txt` (found 48+0+0+48, best 798783); `data/logs/v2_n17_all_run.txt`; `data/rc17.txt`; `checks/check_lists.py` |
| Nodes and time, unrestricted n = 17 | 3.96·10^10 nodes; 11957 to 12542 s per process | `data/logs/n17_all_run.txt` |
| Properties of RC(17) | even sums at j = 4, 6; alternating; \|π_1 − π_17\| = 1; 32 with π_1 = 8, π_17 = 9; RC(17) = maximisers in g(w), \|g(w)\| = 512 | `checks/check_lists.py` |
| 128 = 2^7 ≤ 2^9 | Conjecture 2.3 at n = 17 | arithmetic |
| tmax(n), \|RC(n)\|, n = 3..14 | Table 1 rows | `data/logs/rc_exact_n3_to_14.txt` via `checks/check_lists.py`; `data/expected.json` |
| tmax(15), \|RC(15)\| | 174954, 128; all Odd Sum | `checks/run_rc.py 15 174954` (write stage, both programs; below); `data/rc15.txt` |
| tmax(16), \|RC(16)\| | 374409, 4; all satisfy π_j + π_{17−j} = 17 | `checks/run_rc.py 16 374409` (write stage; below); `data/rc16.txt`; `data/logs/rc16_run.txt` |
| Botler–Netto rows that break the condition | n = 25, 33, 35, 37, 38, 39, 40 | write-stage script over `project:sources/botler_netto_2021.txt` Table 1, with `rc_lib.odd_sum` (the even case uses the sum n + 1) |
| Lean run | about 8 min, up to 6 GB | write-stage `lean-audit` run (below); `project:RESULT.md` (6 GB cap) |
| OPG posting | posted by T. Ahmed, October 14, 2013 | `project:work/src/p_roller_coaster_permutations.html` |
| Botler–Netto bibliographic data | ETC 2021, pp. 50–53, doi:10.5753/etc.2021.16378 | SBC page citation metadata, fetched in the write stage |
| Netto thesis | COPPE/UFRJ, March 2022; quote from Section 2.2.1 | `project:work/src/netto/netto.txt` lines 1422–1425 (PDF fetched in the write stage) |
| Adamczak v2 date | December 29, 2025 | `project:work/src/ad2.txt` line 10 |

## Open issues of the last VERIFY.md and where they are fixed

| Issue (VERIFY round 2) | Fix |
|---|---|
| 1. Netto's thesis already states tmax(17) = 798783 with this witness; cite it, correct the "lower bound" sentence, say what is new; cite arXiv:1703.08735v2. | Paper: abstract ("Netto's 2022 thesis already reports…"), Section 1 "Earlier work" (quote of Section 2.2.1, "floating-point solver result without a certificate"), paragraph "What is new", Section 5 ("as Netto found with Gurobi… confirms his value exactly"), references [Netto] and [Ad2]. README "Credits". The paper does not call the witness or the value of tmax(17) new. `project:RESULT.md` is a record of the solve stage and is not changed; the paper and README replace its prior-art sentence. |
| 2. The Lean main theorem is conditional. | Abstract ("The bound itself is a computation outside Lean"); Section 3 (bold "Lean does not prove fact (ii)", the theorem statements in full); Section 7, item 1; README paragraph after the figure; tier "Computer-assisted" in `result.json`. |
| 3. Memory need of the Lean check. | Section 6 ("up to 6 GB of memory"); Section 3 (one kernel call did not finish within 6 GB); README "Check it"; `checks/README.md`. |
| 4. Describe the second program. | Section 4, paragraph "A second program" (same kind of bound and complement symmetry; written separately by a different AI model; a method error would affect both); `checks/README.md`; `checks/run_n17.py` runs both programs. |
| 5. `checks/__pycache__` is committed. | Removed from git (`git rm --cached`) and added to `.gitignore` in the write stage. |

## Write-stage runs

All runs on the Steam Deck of the factory, compiler `leanc -O2` (the machine has no `cc`).

- `bin/lean-compare release/lean` (under `run-heavy`, `HEAVY_MEM=6G`): `Lean default kernel accepts the solution`, `Your solution is okay!`. The proof file printed `'fact_i' depends on axioms: [propext, Classical.choice, Quot.sound]` and the same for `not_oddSumConjecture_17`. `release/lean/` is a copy of `project:lean/` with no change.
- `bin/lean-audit release/lean/Solution.lean` (`HEAVY_MEM=6G`): `PASS release/lean/Solution.lean: 93 declarations, no project axioms`, 331 s.
- `python3 -I checks/run_rc.py 15 174954 --write`: both programs give 96 maximisers with π_1 ≤ 8; `RESULT n=15 tmax=174954 |RC(n)|=128 odd_sum_members=128`; `run_rc: ALL PASS` (367 s). Log: `data/logs/rc15_run.txt`.
- `python3 -I checks/run_rc.py 16 374409 --write`: both programs give 2 maximisers with π_1 ≤ 8; `RESULT n=16 tmax=374409 |RC(n)|=4 odd_sum_members=4`; `run_rc: ALL PASS` (1649 s). Log: `data/logs/rc16_run.txt`. Before this run, `oddsum_bb 16 374409 0 <job> 4 2` alone gave the same result (found 0, 1, 0, 1; best 374409).
- Clean copy (`git archive` of the committed `release/`, renamed `roller-coaster-odd-sum`), new venv (Python 3.13.18, `uv venv`): `bash checks/ci.sh` under `run-heavy` with 4 threads ends with `ci.sh: all checks passed`, exit 0, 1595 s. It includes `t = 798783`, `34 of 34 generated blocks found`, `check_lists: ALL PASS`, `figures match a fresh drawing`, `ALL SAME` (36 sets), `50 sets; ALL EQUAL`, `run_n17: ALL PASS` (both programs list the 96 permutations; node counts of `oddsum_bb` 893550028, 893260703, 910073485, 841092770; total node count of `v2_bb` 8706023989), `run_rc: ALL PASS` for n = 15, and `paper numbers match data/expected.json`.
- `python3 lab-repo/tools/check_result.py <clean copy>`: `ok: 1 result(s)`.
- Negative control: with the row `16 & 374409 & 4` changed to `… & 5` in a copy of `paper.tex`, the paper-number check of `ci.sh` exits 1 (`missing in paper.tex`).
- Paper: built with Tectonic 0.15.0 (no `latexmk` on this machine), no overfull boxes, 8 pages.
- After the clean `ci.sh` run, only text changed: `README.md`, `checks/README.md` and this file (run times); `paper/paper.tex` and the scripts are the tested versions.

## Work outside the request

- The exact searches for n = 15 and n = 16 (and the claim "the conjecture holds for n ≤ 16", "n = 17 is the smallest counterexample") were added in the write stage. No verify stage has rerun them. The paper says this (Section 7, item 3).
