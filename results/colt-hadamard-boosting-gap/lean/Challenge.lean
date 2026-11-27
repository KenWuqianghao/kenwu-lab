import Mathlib

open Matrix Finset

namespace HadamardBoosting

/-- The number of bit positions `i < k` at which both `r` and `c` have a 1. -/
def commonBits (k r c : ℕ) : ℕ :=
  ((Finset.range k).filter (fun i => r.testBit i = true ∧ c.testBit i = true)).card

/-- The Sylvester Hadamard matrix of order `2 ^ k`: entry `(r, c)` is `(-1) ^ ⟨r, c⟩`, where
`⟨r, c⟩` is the number of common 1 bits of `r` and `c`. -/
def sylvester (k : ℕ) : Matrix (Fin (2 ^ k)) (Fin (2 ^ k)) ℤ :=
  fun r c => (-1) ^ commonBits k r.val c.val

/-- `Ĥ`: the Sylvester matrix with its first row removed. Row `i` of `Ĥ` is row `i + 1` of `H`. -/
def hhat (k : ℕ) : Matrix (Fin (2 ^ k - 1)) (Fin (2 ^ k)) ℤ :=
  fun i c => sylvester k ⟨i.val + 1, by have := i.isLt; have : 0 < 2 ^ k := (by positivity); omega⟩ c

/-- The probability simplex `S^t` on the index type `ι`. -/
def simplex (ι : Type*) [Fintype ι] : Set (ι → ℝ) := {w | (∀ i, 0 ≤ w i) ∧ ∑ i, w i = 1}

/-- Equation (1) of the source: `val(G) = max_{w ∈ S^t} min_r [G w]_r`. -/
noncomputable def val {ρ ι : Type*} [Fintype ι] (G : Matrix ρ ι ℤ) : ℝ :=
  sSup ((fun w : ι → ℝ => ⨅ r, (G.map (Int.cast : ℤ → ℝ)).mulVec w r) '' simplex ι)

/-- `val_D(U) = val([U; -U])`. -/
noncomputable def valD {m ι : Type*} [Fintype ι] (U : Matrix m ι ℤ) : ℝ :=
  val (Matrix.fromRows U (-U))

/-- `max_{U_t} val_D(U_t)`, over the sub-matrices of `U` with `t` distinct columns. -/
noncomputable def maxValD {m n : ℕ} (U : Matrix (Fin m) (Fin n) ℤ) (t : ℕ) : ℝ :=
  ⨆ S : {S : Finset (Fin n) // S.card = t}, valD (U.submatrix id (fun c : S.val => (c : Fin n)))

/-- Conjecture 2 of Nie, Warmuth, Vishwanathan and Zhang (COLT 2013), for `n = 2 ^ k`. -/
def Conjecture2 (k : ℕ) : Prop :=
  ∀ U : Matrix (Fin (2 ^ k - 1)) (Fin (2 ^ k)) ℤ, (∀ i j, U i j = 1 ∨ U i j = -1) → valD U = 0 →
    ∀ t, 1 ≤ t → t ≤ 2 ^ k → maxValD (hhat k) t ≤ maxValD U t

/-- **Main theorem.** Conjecture 2 of Nie, Warmuth, Vishwanathan and Zhang is false for
`n = 16` (`k = 4`), with `Ĥ` from the Sylvester Hadamard matrix. -/
theorem conjecture2_false : ¬ Conjecture2 4 := by sorry

end HadamardBoosting
