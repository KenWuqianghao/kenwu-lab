import Mathlib

/-!
# A ternary Legendre pair of length 35

Source: I. S. Kotsireas, H. Liu, A. Winterhof, *k-ary Legendre pairs*,
arXiv:2611.31067 (2026). The source calls length 35 the smallest open case of
its Conjecture 10. See `STATEMENT.md` for the line-by-line match.
-/

open Complex Finset

noncomputable section

/-- `ξ₃ = e^{2πi/3}`, a primitive complex cube root of unity. -/
def ξ3 : ℂ := Complex.exp (2 * Real.pi * Complex.I / 3)

/-- Periodic autocorrelation `PAF(A, s) = ∑_{j=0}^{ℓ-1} a_j · conj(a_{j+s})`,
indices taken mod `ℓ` (addition in `Fin ℓ` wraps around). -/
def PAF {ℓ : ℕ} [NeZero ℓ] (a : Fin ℓ → ℂ) (s : Fin ℓ) : ℂ :=
  ∑ j : Fin ℓ, a j * (starRingEnd ℂ) (a (j + s))

/-- `(A, B)` is a ternary Legendre pair of length `ℓ`: all entries are in
`{1, ξ₃, ξ₃²}` and `PAF(A,s) + PAF(B,s) = -2` for `s = 1, …, ⌊ℓ/2⌋`. -/
def IsTernaryLegendrePair (ℓ : ℕ) [NeZero ℓ] (A B : Fin ℓ → ℂ) : Prop :=
  (∀ j, A j ∈ ({1, ξ3, ξ3 ^ 2} : Set ℂ)) ∧
  (∀ j, B j ∈ ({1, ξ3, ξ3 ^ 2} : Set ℂ)) ∧
  ∀ s : Fin ℓ, 1 ≤ s.val → s.val ≤ ℓ / 2 → PAF A s + PAF B s = -2

/-! ## Facts about `ξ₃` -/

/-- **Main theorem.** A ternary Legendre pair of length 35 exists. -/
theorem exists_ternary_legendre_pair_35 :
    ∃ A B : Fin 35 → ℂ, IsTernaryLegendrePair 35 A B := by
  sorry

end
