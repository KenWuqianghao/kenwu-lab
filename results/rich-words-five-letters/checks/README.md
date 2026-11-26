# The checks

Run everything from the result folder. Python 3.13 with the pinned packages in
[requirements.txt](requirements.txt) (SymPy 1.14.0, mpmath 1.3.0, NumPy 2.5.5) and a C
compiler are sufficient. `bash checks/ci.sh` installs the packages, runs every program
below and compares each output with the saved output in `checks/expected/`. It ignores
only the lines that give a run time.

Letters are the characters `0`–`8` for u₉ and `0`–`4` for z = π(u₉). The three
morphisms A, B and C are written in each program. A is the morphism of the paper.

## `verify.py [A|B|C]` — the proof

It does the proof of Sections 3 and 4 of the paper for one morphism:

- π is of class P_ret with marker 0, and the characteristic polynomial of the incidence
  matrix M is P5·Q4 with P5 = t⁵ − 2t⁴ − 1 and Q4 = t⁴ − t³ − t² − t − 1 (exact).
- The length vector h is orthogonal to the eigenvectors of the roots of Q4 (exact
  remainder modulo Q4).
- The prefix φ²¹(0) (2 310 194 letters) contains every factor of u₉ of length ≤ 4153,
  because all 17 two-letter factors occur in φ⁹(0).
- The tree of bispecial factors of u₉: 7 multi nodes and 16 seeds. The tree agrees with
  the 36 bispecial factors of length ≤ 40 found directly.
- The return words of each seed are certified from the prefix: the longest window of the
  prefix without an occurrence of the seed is short enough that every return word occurs
  in the prefix. Each seed has 9 return words.
- The 51 bispecial factors of z from multi nodes and the 15 nonempty bispecial factors
  without 0: shortest return word, and |v|/|r| < q in exact arithmetic
  (a/b < q ⇔ P5(3 − b/a) < 0).
- The 16 chains: exact check for n ≤ 60, then the closed form and the tail bound. The test
  κ_Λ = 0 is exact in Q[t]/(P5). Only κ_μ (μ ≠ Λ), ε and ρ use mpmath with 60 digits.
- The bilateral-order condition for richness on every bispecial factor type.

It writes `checks/out/predicted_<name>.json` (the predicted bispecial factors of length
≤ 6000 and their shortest return words) and ends with `RESULT: ALL CHECKS PASSED`.

## `crosscheck.py A` — brute force, no theory

It reads `checks/out/predicted_A.json`, so run it after `verify.py A`. It builds prefixes
of z that contain every factor of a given length. It finds all 64 bispecial factors of z
of length ≤ 60 and their shortest return words by brute force and compares them with the
prediction. It confirms that each of the 149 predicted factors of length ≤ 3000 is
bispecial in z with the predicted shortest return word.

## `independent_check.py [A|B|C]` — a second implementation

It was written in the verification stage from the definitions and the proof plan, before
its author read `verify.py`. It finds by brute force the 75 bispecial factors of u₉ of
length ≤ 300 and the 146 bispecial factors of z of length ≤ 2000. It checks the richness
condition on all of them and |v|/|r| < q on the 125 with a certified shortest return word.
It rebuilds the tree, certifies the return words of the seeds, checks the chains exactly
for n ≤ 1000, and has its own closed form and tail bound.

## `prefix_check.c` — definitions only

`prefix_check <π(0)> … <π(8)> <N>` builds N letters of u₉ and their image under π. An
eertree counts the distinct palindromes of the prefix (rich if the count equals the
length). Then it finds the largest exponent of a repetition inside the prefix, for every
period, and the best exponent in each band of periods [2^k, 2^(k+1)). For A and
N = 3 000 000 the prefix has 9 727 357 letters, it is rich, and the largest exponent is
3684955/1789434 ≈ 2.0592852265 < E*(u₉). The figure `data/exponents.svg` is drawn from
this output by `draw_figure.py` (not part of the proof).

## `search/` — how the morphisms were found

`dfs.cpp` is a depth-first search over morphisms of class P_ret with marker 0. It extends
the images letter by letter, keeps the image of a prefix of u₉ rich (eertree with undo) and
rejects repetitions of exponent ≥ 2.059285449. `sweep.sh` loops over the lengths h0, …,
h4 and sets h5, …, h8 by the length condition h5 = h0 + h4, h6 = h1 − h4 + 2h5,
h7 = h2 − h4 + 2h6, h8 = h3 − h4 + 2h7. The search is not part of the proof.
