import Mathlib

/-!
# Gao–Gu Conjecture 4.12 fails for `k = 2`

Source: Y. Gao, A. Gu, *Arithmetic of weighted Catalan numbers*, arXiv:1908.03914v1,
Conjecture 4.12. A Dyck path is a list of steps: `true` is an up step `(1,1)`, `false` is a
down step `(1,-1)`. An up step weighs `b` of the height of its start; a down step weighs 1.
-/

namespace GaoGu

/-- The height after the steps of `s`. -/
def height (s : List Bool) : ℤ := (s.map fun u => if u then (1 : ℤ) else -1).sum

/-- `s` is a Dyck path of semilength `n`: `2n` steps, never below the axis, ends on it. -/
def IsDyckPath (n : ℕ) (s : List Bool) : Prop :=
  s.length = 2 * n ∧ (∀ k ≤ s.length, 0 ≤ height (s.take k)) ∧ height s = 0

/-- The product, over the up steps of `s`, of `b` at the height where the step starts. -/
def weight (b : ℤ → ℤ) (s : List Bool) : ℤ :=
  ((List.range s.length).map fun k =>
    if s.getD k false then b (height (s.take k)) else 1).prod

open Classical in
/-- The weighted Catalan number `C^b_n`: the sum of the weights of all Dyck paths of
semilength `n`. -/
noncomputable def weightedCatalan (b : ℤ → ℤ) (n : ℕ) : ℤ :=
  ∑ f : Fin (2 * n) → Bool, if IsDyckPath n (List.ofFn f) then weight b (List.ofFn f) else 0

/-- `L^{(k)}_n`: the weight is `b(x) = (2x+1)^(2k)`. -/
noncomputable def L (k n : ℕ) : ℤ := weightedCatalan (fun x => (2 * x + 1) ^ (2 * k)) n

/-- The Catalan number `C_n`: the weight is `b ≡ 1`. -/
noncomputable def C (n : ℕ) : ℤ := weightedCatalan (fun _ => 1) n

/-- The sum of the binary digits of `n`. -/
def s2 (n : ℕ) : ℕ := (Nat.digits 2 n).sum

/-- Conjecture 4.12 for one `k`. `n - α ≠ 0` records that `ξ₂(n - α)` is finite. -/
def Conjecture412 (k : ℕ) : Prop :=
  ∃ α : ℤ_[2], ∃ c : ℕ, ∀ n : ℕ, 2 ≤ n →
    (n : ℤ_[2]) - α ≠ 0 ∧
      padicValInt 2 (L k n - C n) = s2 n + ((n : ℤ_[2]) - α).valuation + c

/-- Conjecture 4.12 of Gao–Gu is false for `k = 2`. -/
theorem conjecture_4_12_false_k2 : ¬ Conjecture412 2 := by
  sorry

/-- Conjecture 4.12 of Gao–Gu ("for every positive integer `k`") is false. -/
theorem conjecture_4_12_false : ¬ ∀ k : ℕ, 0 < k → Conjecture412 k := by
  sorry

end GaoGu
