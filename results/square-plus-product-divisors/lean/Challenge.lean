import Mathlib

open Finset

/-- General form: for every natural number `N` with `N ≡ 6 (mod 8)`,
`∑_{1 ≤ k < √N} σ₀(N - k²) ≡ 0 (mod 4)`. -/
theorem sum_card_divisors_mod_four (N : ℕ) (hN : N % 8 = 6) :
    (∑ k ∈ (range N).filter (fun k : ℕ => 1 ≤ k ∧ (k : ℝ) < Real.sqrt (N : ℝ)),
      (N - k ^ 2).divisors.card) ≡ 0 [MOD 4] := by
  sorry

/-- Conjecture 7 of arXiv:2604.25394: for `N = 16n + 6`,
`∑_{1 ≤ k < √N} σ₀(N - k²) ≡ 0 (mod 4)`. -/
theorem conjecture_7 (n : ℕ) :
    (∑ k ∈ (range (16 * n + 6)).filter
        (fun k : ℕ => 1 ≤ k ∧ (k : ℝ) < Real.sqrt ((16 * n + 6 : ℕ) : ℝ)),
      (16 * n + 6 - k ^ 2).divisors.card) ≡ 0 [MOD 4] := by
  sorry
