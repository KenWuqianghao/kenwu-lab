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
    (h : Construction9Data (2 * k) k T1 f) : construction9Order k T1 f ≠ 2 * k := by sorry
