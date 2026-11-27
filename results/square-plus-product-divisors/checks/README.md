# Checking guide

Run every command from the result folder. All arithmetic is exact (Python integers or numpy int64 with values far below the limit). Times are for one core of a Steam Deck (AMD Zen 2).

| Command | What it checks | Time |
|---|---|---|
| `python3 -I checks/check_statement.py 3000` | The statement from the definitions, with σ0 by trial division: S(N) ≡ 0 (mod 4) for all 375 values N ≡ 6 (mod 8), N ≤ 3000. Also the values of Table 1, the control N ≡ 2 (mod 8), the residues of S(N) mod 4 for each class mod 16, σ1(N)/2 ≡ 0 (mod 4) for N ≡ 14 (mod 16), and the sets of the example N = 22. | about 10 s |
| `python3 -I checks/check_lean_route.py 4000` | Each step 1 to 8 of the proof (Section 3 of the paper), by brute-force counts of the sets X, X1, X1<, Z, the fixed points, X0 and Xb, for all 500 values N ≡ 6 (mod 8), N ≤ 4000. | about 9 s |
| `python3 -I checks/check_nu2.py 700` | ν2(N) ≡ −σ1(N)/2 (mod 4) for N ≡ 6 (mod 8), N ≤ 700, with ν2 counted directly (Section 4). | < 1 s |
| `python3 -I checks/sieve.py 3000000` | A divisor sieve: S(N) ≡ 0 (mod 4) for all N ≡ 6 (mod 8), N ≤ 3·10⁶. For N ≤ 3·10⁵ it lists the classes B mod A (A = 16, 32, 64) on which S(N) ≡ 0 (mod 4) always holds; these are the classes with B ≡ 6 (mod 8). Needs numpy. | about 25 s |
| `bash checks/ci.sh` | All of the above. Each output must equal the file in `checks/expected/`. Then it checks that every number of the paper that these checks give occurs in `paper/paper.tex`. | about 1 min |

`check_statement.py` uses no step of the proof. `check_lean_route.py` counts the sets of the proof one by one, so a wrong step would show as a failure for some N.

## Lean

`lean/Solution.lean` imports only Mathlib. Its helper definitions and lemmas are in `namespace SPD`. It proves

- `sum_card_divisors_mod_four (N : ℕ) (hN : N % 8 = 6)`: the sum of `(N - k ^ 2).divisors.card` over `1 ≤ k` with `(k : ℝ) < Real.sqrt N` is `≡ 0 [MOD 4]`;
- `conjecture_7 (n : ℕ)`: the same for `N = 16 * n + 6`, as a corollary.

The proof follows Section 3 of the paper. `card_mod_two_eq_fixed` and `card_eq_two_mul` are Lemma 3. `card_X1`, `card_X1_lt`, `zag_mem`, `zag_zag`, `zag_fixed`, `Zs_parity_yz` and `Zyz_parity_kx` are steps 1 to 5. `card_X0`, `Xb_parity` and `card_final` are steps 6 to 8. `card_Xs_eq` proves that the set X has S(N) elements, and `card_Xs_mod` is the conclusion. The proof uses no `native_decide`. The file ends with `#print axioms`, which prints `[propext, Classical.choice, Quot.sound]` for both theorems.

`lean/Challenge.lean` repeats the imports, the `open Finset` line and the two statements with `sorry`. The statements use only Mathlib definitions. `lake comparator` with `lean/comparator.json` checks that the proof file proves exactly these statements with only the three standard axioms. Section 5 of the paper explains, line by line, why these statements are the statement of the source.

The Python programs are not formally verified. The Lean proof does not depend on them.
