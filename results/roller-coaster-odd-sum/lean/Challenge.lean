import Mathlib

/-!
# The Odd Sum conjecture (Ahmed–Snevily, Conjecture 2.4) at n = 17

Definitions follow T. Ahmed, H. Snevily, *Some properties of Roller Coaster permutations* (2013).
A permutation of `[n] = {1, …, n}` is a list in one-line notation that is a permutation of
`[1, 2, …, n]`. The main theorem proves that the conjecture fails, under one hypothesis: every
Odd Sum permutation of `[17]` has `t < 798783`. That hypothesis is the computed fact (ii) of
`STATEMENT.md`; it is checked by the exact search `checks/oddsum_bb.c`, not by Lean.
-/

/-- `id τ = i τ + d τ`: the number of maximal increasing runs plus the number of maximal decreasing
runs of `τ` (a run has at least two entries). A maximal increasing (decreasing) run is a maximal
block of consecutive adjacent comparisons that are all `<` (all `>`). -/
def idv (τ : List ℕ) : ℕ :=
  ((List.zipWith (fun a b => decide (a < b)) τ τ.tail).splitBy (· == ·)).length

/-- `t π = Σ_{τ ∈ X(π)} id τ`, where `X(π)` is the set of subsequences of `π` with at least
3 entries. `List.sublists` lists the subsequences by positions. -/
def tval (π : List ℕ) : ℕ :=
  ((π.sublists.filter (fun τ => 3 ≤ τ.length)).map idv).sum

/-- `π ∈ RC(n)`: `π` is a permutation of `[n]` and `t π = max_{σ ∈ S_n} t σ`. -/
def IsRC (n : ℕ) (π : List ℕ) : Prop :=
  π.Perm (List.range' 1 n) ∧ ∀ σ : List ℕ, σ.Perm (List.range' 1 n) → tval σ ≤ tval π

/-- Conjecture 2.4 (The Odd Sum conjecture), for one `n`. `π.getD (j-1) 0` is `π_j`. -/
def OddSumConjecture (n : ℕ) : Prop :=
  ∀ π : List ℕ, IsRC n π →
    (n % 2 = 1 → ∀ j, 1 ≤ j → j ≤ n / 2 → Odd (π.getD (j - 1) 0 + π.getD (n - j) 0)) ∧
    (n % 2 = 0 → ∀ j, 1 ≤ j → j ≤ n / 2 → π.getD (j - 1) 0 + π.getD (n - j) 0 = n + 1)

/-- The Odd Sum property for `n = 17`: `π_j + π_{18-j}` is odd for `1 ≤ j ≤ 8`. -/
def OddSum17 (π : List ℕ) : Prop :=
  ∀ j, 1 ≤ j → j ≤ 8 → Odd (π.getD (j - 1) 0 + π.getD (17 - j) 0)

/-- The witness of Botler–Netto, Table 1. -/
def witness : List ℕ := [8, 14, 3, 15, 6, 10, 2, 17, 7, 12, 1, 16, 5, 11, 4, 13, 9]

/-- Fact (i) in one statement: the witness is a permutation of `[17]`, `t = 798783`, and
`π_4 + π_14 = 26`. -/
theorem fact_i : witness.Perm (List.range' 1 17) ∧ tval witness = 798783 ∧
    witness.getD 3 0 + witness.getD 13 0 = 26 := by sorry

/-- The main theorem: if every Odd Sum permutation of `[17]` has `t < 798783` (fact (ii), checked by
the exact search outside Lean), then Conjecture 2.4 fails for `n = 17`. -/
theorem not_oddSumConjecture_17
    (h : ∀ σ : List ℕ, σ.Perm (List.range' 1 17) → OddSum17 σ → tval σ < 798783) :
    ¬ OddSumConjecture 17 := by sorry
