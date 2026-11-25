# Checking guide

Run every command from the result folder. All arithmetic is exact (integers); no step depends on floating point.

| Command | What it checks | Time (one M1 Pro core) |
|---|---|---|
| `python3 -I checks/check.py` | The quick checks below | < 1 s |
| `python3 -I checks/draw_pair.py --check` | `data/pair.svg` and `paper/fig_pair.tex` equal a fresh drawing of `data/lp35.txt` | < 1 s |
| `python3 -I checks/search.py [g ...]` | The search of Table 1 of the paper; the counts must equal `data/expected.json` | about 7 min for all 7 groups |
| `lake env lean lean/TernaryLP35.lean` (from a Lean project on Mathlib v4.36.0) | The Lean theorem and its axioms | about 1 to 3 min |
| `bash checks/ci.sh` | All Python checks, the full search, and the numbers in `paper/paper.tex` | about 7 min |

## Quick checks (`check.py`)

1. The words in `data/lp35.txt` equal the words `eA` and `eB` in `lean/TernaryLP35.lean`.
2. Both words have composition (11, 12, 12). Both are invariant under j ↦ 6j (mod 35). Neither is invariant under j ↦ −j.
3. The combined counts (M₀, M₁, M₂)(s) are (22, 24, 24) for every lag s = 1, …, 34. So PAF(A, s) + PAF(B, s) = 22 + 24ξ + 24ξ² = −2.
4. Two separate checkers accept the pair. `check_pair.py` counts M_r(s) and also sums in Z[ω]. `check_pair_zw.py` was written by the verifier from the source definition before it read `check_pair.py`; it multiplies in Z[ω] = Z[x]/(x² + x + 1) and gives a floating-point cross-check.
5. Positive controls: both checkers accept the 8 pairs printed in arXiv:2611.31067 (lengths 5, 11, 14, 17, 20, 23, 29, 32).
6. Negative controls: both checkers reject each of the 140 pairs that differ from the certificate in one entry.
7. Z₃₅* has 15 subgroups other than {1}. Each contains ⟨34⟩, ⟨6⟩, ⟨29⟩ or ⟨11⟩. Only ⟨6⟩ contains none of ⟨34⟩, ⟨29⟩, ⟨11⟩. With the zero counts of the search for those three groups, this gives Proposition 3 of the paper.

Each checker also runs alone: `python3 checks/check_pair.py <A> <B>` and `python3 checks/check_pair_zw.py <A> <B>`, with the two exponent words.

## Search (`search.py`, `search/mitm.c`, `search/orbits.py`)

For a multiplier g, `orbits.py 35 g` prints the orbits of ⟨g⟩ on Z/35Z. `mitm.c` lists every word that is constant on these orbits and has composition (11, 12, 12). It stores a hash of the exact PAF vector of each word for lags 1 to 17, and looks up the hash of −2 − PAF for each word. Each hash hit is checked exactly in integers. It prints the first 20 pairs and the counts. `search.py` compiles `mitm.c` with `cc -O2`, runs each group, and compares the counts with `data/expected.json`. For g = 6 it also checks that the certificate is one of the printed pairs.

| g | words | ordered pairs | time | peak memory |
|---|---|---|---|---|
| 34 | 5 717 712 | 0 | 14 s | |
| 6 | 42 042 000 | 2400 | 85 to 96 s | 0.7 GB |
| 29 | 130 162 032 | 0 | 286 s | 2.1 GB |
| 11, 8, 13, 3 | 87 150; 14 840; 1 400; 2 | 0 | < 1 s each | |

The C program is not formally verified. Only the existence of the pair is proved in Lean.

## Lean

`lean/TernaryLP35.lean` imports only Mathlib. It defines ξ₃, PAF and `IsTernaryLegendrePair` from the source and proves `exists_ternary_legendre_pair_35 : ∃ A B : Fin 35 → ℂ, IsTernaryLegendrePair 35 A B`. The lemma `counts_ok` is proved by kernel `decide`; the proof does not use `native_decide`. The file ends with `#print axioms`, which prints `[propext, Classical.choice, Quot.sound]`. Measured run times on an M1 Pro: 151 s, 60 s and 56 s.

## The case ℓ = 38

The paper reports 27 runs in structured families at ℓ = 38, all with no pair. Their programs and logs are in the project records and are not part of this folder, because 7 of the runs need about 3.6 GB of memory each. These are negative results inside the listed families only. They say nothing about whether a pair of length 38 exists.
