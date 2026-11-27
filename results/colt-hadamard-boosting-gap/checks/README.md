# Checks

Run the commands from the result folder. `check.py`, `check_extra.py`, `draw.py` and
`make_lean.py` use only the Python standard library (Python 3.10 or later) and exact
integers or `fractions.Fraction`. `vcheck.py --lp` also needs NumPy and SciPy
([requirements.txt](requirements.txt)); its floating-point linear programs only make new
dual vectors, which it then checks exactly.

| Command | What it checks | Time |
|---|---|---|
| `python3 -I checks/check.py checks/certificate.json` | *U* is 15 × 16 with entries ±1 and row sums 0, so val_D(*U*) = 0. For each of the 8008 sets *S* of 6 columns, the certificate vector *y* has ‖*y*‖₁ ≤ 1 and (*U*_*S*ᵀ *y*)_*j* ≥ 3/7 for every *j* ∈ *S*. The Sylvester witness *S*₀ = {0,1,2,4,8,15} with uniform weights gives ‖Ĥ_*S*₀ *w*‖∞ = 1/3. | 3 s |
| `python3 -I checks/check_extra.py checks/certificate.json checks/had.16.3.txt` | `had.16.3.txt` is a Hadamard matrix with an all-ones row 0, and *U* is that matrix without row 0. The equality case *S* = {0,1,2,3,4,12}, *w* = (1,1,1,1,1,2)/7 gives ‖*U*_*S* *w*‖∞ = 3/7. The Sylvester row sums on *S*₀ follow the hand formula 1 + (4 − 2\|*r*\|) + (−1)^\|*r*\| = ±2. | < 1 s |
| `python3 -I checks/vcheck.py checks/certificate.json --lp` | Second checker, written from the source definitions without reading `check.py`. It repeats the exact checks, solves the 8008 linear programs min ‖*U*_*S* *w*‖∞ with HiGHS, rounds its own dual vectors to rationals and checks them exactly (0 failures), and finds the equality case. Item 8 is the floating-point value 0.333333 for Ĥ (information only). | 36 s |
| `python3 -I checks/make_lean.py checks/certificate.json checks/lean-src/head.lean OUT.lean` | Writes the Lean proof from the certificate. `OUT.lean` equals [../lean/Solution.lean](../lean/Solution.lean). | 5 s |
| `python3 -I checks/draw.py --check` | The figure files `paper/fig_matrices.tex` and `data/matrices.svg` equal a fresh drawing. | < 1 s |
| `bash checks/ci.sh` | All of the above. The outputs of `check.py` and `check_extra.py` must equal the files in [expected/](expected/), and the numbers in the paper must match the outputs. | about 1 min |

Times are for one core of a Steam Deck (AMD Zen 2).

## Files

- [certificate.json](certificate.json): `U` (15 strings of `+` and `-`), `t = 6`, and
  `subset_certificates`: for each 6-subset `S` (sorted column indices, 0-based), the vector
  `y` as 15 decimal fractions. The vectors came from HiGHS dual solutions, rounded to
  rationals (sprint stage, `checks/search/make_cert.py` in the problem folder).
- [had.16.3.txt](had.16.3.txt): the source of *U* (see [../THIRD_PARTY.md](../THIRD_PARTY.md)).
- `lean-src/head.lean`, `lean-src/mid.lean`, `lean-src/tail.lean`: the hand-written parts
  of the Lean proof. `make_lean.py` inserts the data between them.
- [expected/](expected/): the outputs of `check.py` and `check_extra.py`.

## Lean

[../lean/Challenge.lean](../lean/Challenge.lean) states the definitions and the theorem
`HadamardBoosting.conjecture2_false : ¬ Conjecture2 4`.
[../lean/Solution.lean](../lean/Solution.lean) repeats them word for word and proves the
theorem. Compile it from a Lean project with Mathlib v4.36.0:

```sh
lake env lean lean/Solution.lean
```

The last output line must be
`'HadamardBoosting.conjecture2_false' depends on axioms: [propext, Classical.choice, Quot.sound]`.

How the proof works:

- The general part proves, for real weights, that a nonzero integer vector *y* with
  7 (*U*ᵀ*y*)_*j* ≥ 3 ‖*y*‖₁ on every column of *S* gives val_D(*U*_*S*) ≤ −3/7
  (`U_bound`), and that uniform weights give val_D(Ĥ_*S*₀) ≥ −1/3 (`H_bound`).
- The data part encodes each scaled vector *y* (entries −2 to 2) in base 5, together with
  the bit mask of the columns where the inequality holds. For each pair *a* < *b* of the two
  smallest columns (66 pairs), `all_a_b` checks the inequality for each entry of the list
  `D_a_b`, and `any_a_b` checks that every 6-set {*a* < *b* < *c* < *d* < *e* < *f*} lies in
  the mask of some entry. Both use `decide +kernel` (evaluation in the Lean kernel, no extra
  axiom). The lists have 2222 entries in total.
- `cert` turns a `Finset` of size 6 into its sorted elements and finds its certificate;
  `conjecture2_false` combines the three parts.

The kernel evaluation takes about 20 minutes on one core of a Steam Deck and up to about 6 GB of memory
(most of it is Mathlib). A first version that checked all 8008 sets in one kernel evaluation
exceeded a 4 GB memory limit, which is why the data is split by the pair (*a*, *b*).
