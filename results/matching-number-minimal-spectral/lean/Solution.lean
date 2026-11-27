import Mathlib

open Finset

/-- The data of Construction 9 of Hou–Tan (arXiv:2607.11061v2) for parameters `n`, `k`:
a tree `T1` on the vertex set `X = Fin k` and nonnegative integers `f i` with
`2 * d_{T1}(x_i) + f_i ∈ {c, c + 1}`, where `c = ⌊(n + 2k - 3) / k⌋`. -/
def Construction9Data (n k : ℕ) (T1 : SimpleGraph (Fin k)) [DecidableRel T1.Adj]
    (f : Fin k → ℕ) : Prop :=
  T1.IsTree ∧ ∀ i, 2 * T1.degree i + f i = (n + 2 * k - 3) / k ∨
    2 * T1.degree i + f i = (n + 2 * k - 3) / k + 1

/-- The order of the tree that Construction 9 builds: the `k` vertices of `X`, one new
vertex for each edge of `T1` (step 1), and `f i` pendant leaves at each `x_i` (step 2). -/
def construction9Order (k : ℕ) (T1 : SimpleGraph (Fin k)) [DecidableRel T1.Adj]
    (f : Fin k → ℕ) : ℕ :=
  k + #T1.edgeFinset + ∑ i, f i

/-- For `k ≥ 3` and `n = 2k`, no choice of data in Construction 9 gives a tree of order `n`.
So `T'_{2k,k}` has no graph of order `2k`. -/
theorem construction9_no_tree_of_order_two_mul (k : ℕ) (hk : 3 ≤ k)
    (T1 : SimpleGraph (Fin k)) [DecidableRel T1.Adj] (f : Fin k → ℕ)
    (h : Construction9Data (2 * k) k T1 f) : construction9Order k T1 f ≠ 2 * k := by
  obtain ⟨htree, hf⟩ := h
  have hc : (2 * k + 2 * k - 3) / k = 3 := by
    apply Nat.div_eq_of_lt_le <;> omega
  rw [hc] at hf
  have hterm : ∀ i ∈ (univ : Finset (Fin k)), 2 ≤ f i + T1.degree i := by
    intro i _
    rcases hf i with h1 | h1 <;> omega
  have hsum : ∑ _i : Fin k, 2 ≤ ∑ i, (f i + T1.degree i) := Finset.sum_le_sum hterm
  rw [Finset.sum_add_distrib, T1.sum_degrees_eq_twice_card_edges] at hsum
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul] at hsum
  have hE := htree.card_edgeFinset
  rw [Fintype.card_fin] at hE
  unfold construction9Order
  omega

#print axioms construction9_no_tree_of_order_two_mul
