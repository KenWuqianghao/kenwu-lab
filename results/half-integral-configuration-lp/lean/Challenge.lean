import Mathlib

open Finset

namespace HalfIntegralCLP

/-- An instance of the restricted assignment problem with `n` jobs and `m` machines. Job `j`
has processing time `p j ∈ ℕ₊` on each machine in `M j` and `∞` on the other machines. -/
structure RAInstance (n m : ℕ) where
  p : Fin n → ℕ
  M : Fin n → Finset (Fin m)
  p_pos : ∀ j, 0 < p j

variable {n m : ℕ}

/-- The jobs with finite processing time on machine `i`. -/
def allowedJobs (P : RAInstance n m) (i : Fin m) : Finset (Fin n) :=
  univ.filter (fun j => i ∈ P.M j)

/-- The load `∑_{j ∈ C} p_j` of a set of jobs. -/
def load (P : RAInstance n m) (C : Finset (Fin n)) : ℕ :=
  ∑ j ∈ C, P.p j

/-- `𝒞_i(P,T)` (eq. 8 of the source): the sets `C ⊆ [n]` with `∑_{j∈C} p_{j,i} ≤ T`. A set with
a job that is not allowed on `i` has infinite load, so `C` is a subset of `allowedJobs P i`. -/
def configs (P : RAInstance n m) (i : Fin m) (T : ℤ) : Finset (Finset (Fin n)) :=
  (allowedJobs P i).powerset.filter (fun C => (load P C : ℤ) ≤ T)

/-- `x ∈ CLP(P,T)` (eqs. 9a-9c of the source). Only the entries `x i C` with `C ∈ 𝒞_i(P,T)`
are coordinates of the point; the other values of the function `x` are not used. -/
def InCLP (P : RAInstance n m) (T : ℤ) (x : Fin m → Finset (Fin n) → ℝ) : Prop :=
  (∀ i, ∑ C ∈ configs P i T, x i C = 1) ∧
  (∀ j, ∑ i, ∑ C ∈ (configs P i T).filter (fun C => j ∈ C), x i C = 1) ∧
  (∀ i, ∀ C ∈ configs P i T, 0 ≤ x i C)

/-- `CLP(P,T)` is feasible (nonempty). -/
def CLPFeasible (P : RAInstance n m) (T : ℤ) : Prop :=
  ∃ x, InCLP P T x

/-- Every entry `x_{i,C}` with `C ∈ 𝒞_i(P,T)` is `0`, `1/2` or `1`. -/
def IsHalfIntegral (P : RAInstance n m) (T : ℤ) (x : Fin m → Finset (Fin n) → ℝ) : Prop :=
  ∀ i, ∀ C ∈ configs P i T, x i C = 0 ∨ x i C = 1 / 2 ∨ x i C = 1

/-- Conjecture 10 of arXiv:2609.19967: for every instance `P`, if `T = LP(P)` is the smallest
integer with `CLP(P,T)` feasible, then `CLP(P,T)` has a half-integral point. -/
def Conjecture10 : Prop :=
  ∀ (n m : ℕ) (P : RAInstance n m) (T : ℤ), IsLeast {T : ℤ | CLPFeasible P T} T →
    ∃ x, InCLP P T x ∧ IsHalfIntegral P T x

/-- **Main theorem.** Conjecture 10 of arXiv:2609.19967 is false. -/
theorem not_conjecture10 : ¬ Conjecture10 := by
  sorry

end HalfIntegralCLP
