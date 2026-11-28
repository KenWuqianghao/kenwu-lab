# Checking guide

Run every command from the result folder. The Python scripts use only the standard library, except `validate_bb.py`, which needs NumPy (pinned in [requirements.txt](requirements.txt)). The search programs are plain C with no headers; any C compiler works (`cc`, `gcc`, `clang`, or `leanc` from a Lean toolchain). The scripts take the compiler from `$CC`, or else the first of these that exists.

All times are for one core of a Steam Deck (AMD Zen 2, 2.4 to 3.5 GHz), unless the table says otherwise.

| Command | What it checks | Time |
|---|---|---|
| `python3 -I checks/t_definition.py` | Fact (i): t(w) = 798783 from the definition (all 2^17 subsequences); the source's examples t(2143) = 11, t(1234) = 5 | < 1 s |
| `python3 -I checks/check_lists.py` | The data lists (below) | 2 s |
| `python3 -I checks/gen_lean_split.py --check` | The 32 part values in `lean/Solution.lean` equal a fresh computation and add up to 798783 | < 1 s |
| `python3 -I checks/draw_witness.py --check` | `data/witness.svg` and `paper/fig_witness.tex` equal a fresh drawing | < 1 s |
| `python3 -I checks/validate_bb.py <oddsum_bb binary>` | The first program against brute force, n = 5..10, both modes, 4 thresholds each: 36 sets, `ALL SAME` | 30 s |
| `python3 -I checks/independent/v2_validate.py <v2_bb binary>` | The second program against brute force, n = 5..9, both modes, 5 thresholds each: 50 sets, `ALL EQUAL` | 8 s |
| `python3 -I checks/run_n17.py` | Fact (ii) with both programs (below) | about 1000 s per process for the first program (4 processes); 4084 s in total for the 9 processes of the second program, with 8 processes on 4 cores |
| `python3 -I checks/run_rc.py 15 174954` | RC(15) with both programs | 367 s with 2 processes at a time |
| `python3 -I checks/run_rc.py 16 374409` | RC(16) with both programs; not in `ci.sh` | 1649 s with 4 processes at a time |
| `bash checks/ci.sh` | All of the above except RC(16), and the numbers in `paper/paper.tex` | 1595 s on 4 cores |
| `lake env lean lean/Solution.lean` (from a Lean project on Mathlib v4.36.0) | The Lean theorems and their axioms | about 6 to 8 min, up to 6 GB |

## The value t and the turn identity

`t_definition.py` evaluates t from the definition of Ahmed and Snevily: for each subsequence with at least 3 entries, it counts the maximal runs of equal direction. Everything else uses the turn identity (Lemma 1 of the paper):

t(π) = Σ_{m=3}^{n} C(n, m) + Σ_{a<b<c, (a,b,c) a turn} 2^{a−1} 2^{n−c},

where (a, b, c) is a turn if π_b is larger than both π_a and π_c or smaller than both. `validate_bb.py` compares the identity with the definition on 100 random permutations (n = 4..8). `v2_validate.py` compares it on all permutations with n ≤ 7. `check_lists.py` compares the two on the witness and on one element of RC(17).

## The two search programs

`oddsum_bb.c` (written in the solve stage) and `independent/v2_bb.c` (written in the verify stage, by a different AI model, before its author read `oddsum_bb.c`) list every permutation with t ≥ T. Both place values from left to right and cut a branch only if an integer lower bound on the loss of the completion shows t < T for every completion. The comment at the top of each file gives the bound and the proof of each part. Both use the complement symmetry (π ↦ 18 − π keeps t and the Odd Sum property) and search only π_1 ≤ ⌈n/2⌉.

- `oddsum_bb n T mode [job K depth]`: mode 0 = all permutations, mode 1 = Odd Sum permutations (n odd). With `job K depth` it searches the subtrees at depth `depth` whose index is `job` mod `K`. Output: lines `t=<t> <π>` after the line `BEGIN n=<n> …`, then a `SUMMARY` line.
- `v2_bb n T mode lo hi`: the same question for lo ≤ π_1 ≤ hi. Output: lines `PERM t=<t> : <π>` and a `SUMMARY` line.

## `run_n17.py` (fact (ii))

It compiles both programs and runs `oddsum_bb 17 798775 1 <job> 4 2` (job = 0..3) and `v2_bb 17 798775 1 <v> <v>` (v = 1..9), as many at a time as there are CPUs (`--workers`). It checks:

- each program lists exactly the 96 permutations of `data/oddsum17_t798775.txt`;
- all of them have the Odd Sum property, π_1 ≤ 9 and t = 798775 (evaluated again in Python), so no Odd Sum permutation has t ≥ 798776;
- the node counts of `oddsum_bb` are 893550028, 893260703, 910073485 and 841092770 (`data/expected.json`); the total node count of `v2_bb` is 8706023989.

## `run_rc.py n T` (RC(n) for n = 15, 16)

It runs `oddsum_bb n T 0 <job> 4 2` and `v2_bb n T 0 <v> <v>`, checks that both programs give the same maximisers and evaluates them again, adds the complements, and compares RC(n) with `data/rc<n>.txt`. T is the lower bound of Ahmed and Snevily; because a permutation reaches it, the largest listed value is tmax(n). The script prints `RESULT n=… tmax=… |RC(n)|=… odd_sum_members=…`.

## `check_lists.py` (data lists)

- `data/rc17.txt`: RC(17), 128 permutations. The script checks that each has t = 798783, none has the Odd Sum property, each has even mirror sums exactly at j = 4 and 6, the set is closed under reversal and complement, it contains the witness, every element is alternating, |π_1 − π_17| = 1, 32 elements have π_1 = 8 and π_17 = 9, and RC(17) is the set of maximisers of t over g(w), the 512 permutations of Ahmed and Snevily's construction.
- `data/oddsum17_t798775.txt`: the 96 Odd Sum permutations with t = 798775 and π_1 ≤ 9 (128 with complements).
- `data/logs/rc_exact_n3_to_14.txt`: the output of `checks/rc4.c` (an earlier exact search of this project, with a weaker bound) for n = 3..14. The script evaluates every listed permutation again, gives |RC(n)| and tmax(n), and checks Conjecture 2.4 for each n. For n = 14 the log lists the permutations with π_1 ≤ 7; the script adds the complements.
- The literature permutations that the paper quotes: their t and whether they have the Odd Sum property.

## Logs of the long runs (`data/logs/`)

These runs are too long for CI. Their outputs are committed; `check_lists.py` checks the lists that they produced.

| File | Command | Result | Time |
|---|---|---|---|
| `n17_oddsum_run.txt` | `oddsum_bb 17 798775 1 <job> 4 2`, job = 0..3 | 96 permutations, best 798775 (fact (ii)) | 943 to 1030 s per job |
| `n17_all_run.txt` | `oddsum_bb 17 798783 0 <job> 4 2`, job = 0..3 | 96 permutations, best 798783 (RC(17)) | 11957 to 12542 s per job |
| `v2_n17_oddsum_run.txt` | `v2_bb 17 798775 1 1 5` and `… 6 9` | 0 and 96 permutations, best 798775 | about 29 min (verify stage) |
| `v2_n17_all_run.txt` | `v2_bb 17 798783 0 v v`, v = 1..9 | 96 permutations, best 798783 | 1640 to 2591 s for v = 5, 6, 7 |
| `rc16_run.txt` | `run_rc.py 16 374409` | tmax(16) = 374409, \|RC(16)\| = 4, all four satisfy Conjecture 2.4; the two programs agree | 1649 s |
| `validate_bb_output.txt`, `v2_validate_output.txt` | the two validations | 36 and 50 equal sets | |
| `rc_exact_n3_to_14.txt` | `rc4 n T`, n = 3..14, with T the value of Ahmed and Snevily | RC(n), n ≤ 14 | |

## Lean

`lean/Solution.lean` imports only Mathlib. It proves `fact_i` (the witness is a permutation of [17], t = 798783, π_4 + π_14 = 26) and `not_oddSumConjecture_17` (if every Odd Sum permutation of [17] has t < 798783, then the conjecture fails for n = 17). The hypothesis of the second theorem is fact (ii); Lean does not prove it. `lean/Challenge.lean` repeats the definitions and both statements with `sorry`; `lake comparator` with `lean/comparator.json` checks that the proof file proves exactly these statements with the axioms `propext`, `Quot.sound` and `Classical.choice`. The value t(w) is computed by `decide +kernel` in 32 parts (`gen_lean_split.py`); one kernel call on the whole definition did not finish within 6 GB. No `native_decide` is used.
