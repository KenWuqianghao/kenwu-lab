# Checking guide

Run every command from the result folder. `checks/verify.py` and `checks/draw_figure.py` use only the Python standard library. The other scripts need the pinned packages in [requirements.txt](requirements.txt) (NetworkX and NumPy).

| Command | What it checks | Time (one Steam Deck core) |
|---|---|---|
| `python3 -I checks/verify.py 8` | The exact checker (below) for k = 3..8 | < 1 s |
| `python3 -I checks/verifier_check.py 7 6` | The independent checker (below): explicit graphs for k = 3..7, membership for k = 3..6 | about 11 s |
| `python3 -I checks/search.py 20 OUT.json` | The search of Section 4 of the paper over all trees of order ≤ 20 | about 2.5 min |
| `python3 -I checks/compare_search.py OUT.json` | The new search output against `data/search20.json` and `data/expected.json` | < 1 s |
| `python3 -I checks/draw_figure.py --check` | `data/figure.svg` is the drawing that the script makes | < 1 s |
| `bash checks/ci.sh` | All of the above, and the numbers in `paper/paper.tex` | about 3 min |
| `lake env lean lean/Solution.lean` (from a Lean project on Mathlib v4.36.0) | The Lean theorem and its axioms | about 15 s after Mathlib is built |

## The exact checker (`verify.py`)

It was written by the solver. It uses exact integers only.

1. For each k, it takes the degree sequence of every labelled tree on k vertices, from all Prüfer codes. Only the degree sequence of T1 matters for the condition of Construction 9 and for the order of the built tree.
2. With n = 2k and c = ⌊(n + 2k − 3)/k⌋ (integer division), it tries every f with f_i = c − 2d_i or c + 1 − 2d_i and f_i ≥ 0. It counts the choices whose order k + (k − 1) + Σ f_i equals n. The count must be 0.
3. It computes the matching number of P_{2k} by brute force over all sets of edges. It must be k.
4. Control: for n = 2k + 1 the count must be positive, so the checker finds members when they exist.

## The independent checker (`verifier_check.py`)

It was written by the verifier before reading `verify.py`.

- Part A builds every graph of Construction 9 as an explicit NetworkX graph, from every labelled tree T1 and every admissible f, for n = 2k and k = 3..7. It reports the smallest order built (2k + 1) and checks that no order equals 2k. It repeats this with c read as a ceiling. Control: n = 2k + 1 gives members.
- Part B takes every tree of order 2k with matching number k, for k = 3..6, and searches each tree for a vertex set X that shows it as a member of T'_{2k,k}. It finds none. The tree of minimum spectral radius (floating point) is the path. Controls: for n = 2k + 1 the unique minimiser is a member, and P_4 is a member of T'_{4,2}.
- It also checks that the matching number of P_{2k} is k for k = 3..10.

## The search (`search.py`, `compare_search.py`)

`search.py` takes every non-isomorphic tree of order n ≤ 20 (NetworkX). It computes the matching number exactly (greedy leaf matching, which is optimal on trees) and the spectral radius with `numpy.linalg.eigvalsh`. For each k it keeps the trees within 10⁻⁹ of the minimum. It builds T'_{n,k} from every non-isomorphic T1 and every admissible f of order n, and it tests membership with a canonical string of the tree. Spectrally minimal graphs of G_{n,k} are trees (Liu, Lou and Trevisan), so the search covers all of G_{n,k}.

`compare_search.py` compares a new output with `data/search20.json`: spectral radii to within 10⁻⁹, all other fields exactly. It then checks the facts that the paper states: 100 pairs (n, k); a minimiser outside T'_{n,k} exactly for (2k, k), k = 3..10; there, T'_{n,k} has no tree of order n, and the unique minimiser is the path, with spectral radius 2 cos(π/(n + 1)); every minimiser is in T'_{n,k} for the 90 pairs with n ≥ 2k + 1; and the four pairs with tied minimisers.

The search is a floating-point diagnostic. It is evidence for the open question for n ≥ 2k + 1. It is not a proof, and the main theorem does not use it.

## Lean

`lean/Solution.lean` imports only Mathlib. It defines `Construction9Data` (the condition of Construction 9 on T1 and f) and `construction9Order` (the order of the built tree: k + number of edges of T1 + Σ f_i). It proves `construction9_no_tree_of_order_two_mul`: for k ≥ 3 and n = 2k, the order is never 2k. The proof computes c = 3, shows f_i + d_i ≥ 2 for each i, and uses the handshake lemma and the edge count k − 1 of a tree. `lean/Challenge.lean` repeats the definitions and the statement with `sorry`; `lake comparator` with `lean/comparator.json` checks that the proof file proves exactly this statement with the axioms `propext`, `Quot.sound` and `Classical.choice`.

Lean does not define the matching number, the spectral radius or the family G_{n,k}. The fact that P_{2k} is in G_{2k,k} is proved by hand in the paper and checked by the Python checkers for small k.
