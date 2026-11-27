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

/-- Weighted double counting: for a point `x` of CLP(P,T) and job weights `w`,
`∑_i ∑_C x_{i,C} · w(C) = ∑_j w_j`. -/
theorem weighted_count (P : RAInstance n m) (T : ℤ) (x : Fin m → Finset (Fin n) → ℝ)
    (hx : InCLP P T x) (w : Fin n → ℝ) :
    ∑ i, ∑ C ∈ configs P i T, x i C * ∑ j ∈ C, w j = ∑ j, w j := by
  have h1 : ∀ i, ∑ C ∈ configs P i T, x i C * ∑ j ∈ C, w j
      = ∑ j, w j * ∑ C ∈ (configs P i T).filter (fun C => j ∈ C), x i C := by
    intro i
    calc ∑ C ∈ configs P i T, x i C * ∑ j ∈ C, w j
        = ∑ C ∈ configs P i T, ∑ j, (if j ∈ C then w j * x i C else 0) := by
          refine Finset.sum_congr rfl (fun C _ => ?_)
          rw [Finset.mul_sum, ← Finset.sum_filter]
          refine Finset.sum_congr (by ext j; simp) (fun j _ => by ring)
      _ = ∑ j, ∑ C ∈ configs P i T, (if j ∈ C then w j * x i C else 0) := Finset.sum_comm
      _ = ∑ j, w j * ∑ C ∈ (configs P i T).filter (fun C => j ∈ C), x i C := by
          refine Finset.sum_congr rfl (fun j _ => ?_)
          rw [Finset.sum_filter, Finset.mul_sum]
          refine Finset.sum_congr rfl (fun C _ => ?_)
          split_ifs <;> simp
  rw [Finset.sum_congr rfl (fun i _ => h1 i), Finset.sum_comm]
  refine Finset.sum_congr rfl (fun j _ => ?_)
  rw [← Finset.mul_sum, hx.2.1 j, mul_one]

/-- Volume bound: `∑_i ∑_C x_{i,C} · p(C) ≤ m · T`. -/
theorem volume_le (P : RAInstance n m) (T : ℤ) (x : Fin m → Finset (Fin n) → ℝ)
    (hx : InCLP P T x) :
    ∑ i, ∑ C ∈ configs P i T, x i C * ((load P C : ℕ) : ℝ) ≤ m * (T : ℝ) := by
  have : ∀ i, ∑ C ∈ configs P i T, x i C * ((load P C : ℕ) : ℝ) ≤ (T : ℝ) := by
    intro i
    calc ∑ C ∈ configs P i T, x i C * ((load P C : ℕ) : ℝ)
        ≤ ∑ C ∈ configs P i T, x i C * (T : ℝ) := by
          refine Finset.sum_le_sum (fun C hC => ?_)
          refine mul_le_mul_of_nonneg_left ?_ (hx.2.2 i C hC)
          have h := (Finset.mem_filter.1 hC).2
          exact_mod_cast h
      _ = (T : ℝ) := by rw [← Finset.sum_mul, hx.1 i, one_mul]
  calc _ ≤ ∑ _i : Fin m, (T : ℝ) := Finset.sum_le_sum (fun i _ => this i)
    _ = m * (T : ℝ) := by simp

theorem volume_eq (P : RAInstance n m) (T : ℤ) (x : Fin m → Finset (Fin n) → ℝ)
    (hx : InCLP P T x) :
    ∑ i, ∑ C ∈ configs P i T, x i C * ((load P C : ℕ) : ℝ) = ∑ j, (P.p j : ℝ) := by
  rw [← weighted_count P T x hx (fun j => (P.p j : ℝ))]
  simp [load]


/-! ## The counterexample: 12 machines, 20 jobs, `LP(P) = 3`

Machine `4c + t` is machine `(c,t)`, `c ∈ {0,1,2}`, `t ∈ {0,1,2,3}`. Job `4c + k` (`k < 4`) is
the point job `P(c,k)` of size 1, allowed on the machines `(c,t)` with `t ≠ k`. Job `12 + f`
(`f < 8`) is the filler `F(f)` of size 3, allowed on the machines `i` with `f / 2 = i mod 4`. -/

/-- Job `j` is allowed on machine `i`. -/
def allowed (i : Fin 12) (j : Fin 20) : Prop :=
  if j.val < 12 then i.val / 4 = j.val / 4 ∧ i.val % 4 ≠ j.val % 4
  else (j.val - 12) / 2 = i.val % 4

instance (i : Fin 12) (j : Fin 20) : Decidable (allowed i j) := by
  unfold allowed; infer_instance

/-- The counterexample instance. -/
def P0 : RAInstance 20 12 where
  p j := if j.val < 12 then 1 else 3
  M j := univ.filter (fun i => allowed i j)
  p_pos j := by by_cases h : j.val < 12 <;> simp [h]

/-- Indicator of the point jobs of copy 0. -/
def w0 (j : Fin 20) : ℕ := if j.val < 4 then 1 else 0

/-- Number of point jobs of copy 0 in `C`. -/
def W (C : Finset (Fin 20)) : ℕ := ∑ j ∈ C, w0 j

/-! Finite facts, checked by kernel evaluation (`decide +kernel`, no extra axioms). -/

theorem sum_p : ∑ j, P0.p j = 36 := by decide +kernel

theorem full_mod3 (i : Fin 12) :
    ((configs P0 i 3).filter (fun C => load P0 C = 3 ∧ W C ≠ 0 ∧ W C ≠ 3)).card = 0 := by
  fin_cases i <;> decide +kernel

theorem card_full (i : Fin 12) : ((configs P0 i 3).filter (fun C => load P0 C = 3)).card = 3 := by
  fin_cases i <;> decide +kernel

theorem cover_full (j : Fin 20) :
    ∑ i : Fin 12, (((configs P0 i 3).filter (fun C => j ∈ C)).filter
      (fun C => load P0 C = 3)).card = 3 := by
  fin_cases j <;> decide +kernel

theorem sum_w0 : ∑ j, w0 j = 4 := by decide +kernel

theorem sum_p_real : ∑ j, (P0.p j : ℝ) = 36 := by
  exact_mod_cast sum_p

/-- `CLP(P0,T)` is empty for `T ≤ 2` (volume `36 > 12 · 2`). -/
theorem not_feasible_of_le_two (T : ℤ) (hT : T ≤ 2) : ¬ CLPFeasible P0 T := by
  rintro ⟨x, hx⟩
  have h1 := volume_le P0 T x hx
  rw [volume_eq P0 T x hx, sum_p_real] at h1
  have h2 : (T : ℝ) ≤ 2 := by exact_mod_cast hT
  norm_num at h1
  linarith

/-- The point with value `1/3` on each configuration of load 3. -/
noncomputable def x0 (_i : Fin 12) (C : Finset (Fin 20)) : ℝ :=
  if load P0 C = 3 then 1 / 3 else 0

theorem x0_mem : InCLP P0 3 x0 := by
  refine ⟨fun i => ?_, fun j => ?_, fun i C _ => ?_⟩
  · unfold x0
    rw [← Finset.sum_filter, Finset.sum_const, card_full i]
    norm_num
  · unfold x0
    simp_rw [← Finset.sum_filter, Finset.sum_const, nsmul_eq_mul]
    rw [← Finset.sum_mul, ← Nat.cast_sum, cover_full j]
    norm_num
  · unfold x0
    split_ifs <;> norm_num

theorem isLeast_three : IsLeast {T : ℤ | CLPFeasible P0 T} 3 := by
  refine ⟨⟨x0, x0_mem⟩, fun T hT => ?_⟩
  by_contra h
  exact not_feasible_of_le_two T (by omega) hT

/-- Every configuration in the support of a point of `CLP(P0,3)` has load exactly 3. -/
theorem support_full (x : Fin 12 → Finset (Fin 20) → ℝ) (hx : InCLP P0 3 x)
    (i : Fin 12) (C : Finset (Fin 20)) (hC : C ∈ configs P0 i 3) (h0 : x i C ≠ 0) :
    load P0 C = 3 := by
  have hle : ∀ i, ∀ C ∈ configs P0 i 3, ((load P0 C : ℕ) : ℝ) ≤ 3 := by
    intro i C hC
    have h := (Finset.mem_filter.1 hC).2
    exact_mod_cast h
  have hsum : ∑ i, ∑ C ∈ configs P0 i 3, x i C * (3 - ((load P0 C : ℕ) : ℝ)) = 0 := by
    have e : ∀ i, ∑ C ∈ configs P0 i 3, x i C * (3 - ((load P0 C : ℕ) : ℝ))
        = 3 - ∑ C ∈ configs P0 i 3, x i C * ((load P0 C : ℕ) : ℝ) := by
      intro i
      simp_rw [mul_sub]
      rw [Finset.sum_sub_distrib, ← Finset.sum_mul, hx.1 i, one_mul]
    rw [Finset.sum_congr rfl (fun i _ => e i), Finset.sum_sub_distrib, volume_eq P0 3 x hx,
      sum_p_real]
    simp
    norm_num
  have hnn : ∀ i ∈ (univ : Finset (Fin 12)),
      0 ≤ ∑ C ∈ configs P0 i 3, x i C * (3 - ((load P0 C : ℕ) : ℝ)) := by
    intro i _
    exact Finset.sum_nonneg (fun C hC => mul_nonneg (hx.2.2 i C hC) (by linarith [hle i C hC]))
  have hi := (Finset.sum_eq_zero_iff_of_nonneg hnn).1 hsum i (Finset.mem_univ i)
  have hC' := (Finset.sum_eq_zero_iff_of_nonneg
    (fun C hC => mul_nonneg (hx.2.2 i C hC) (by linarith [hle i C hC]))).1 hi C hC
  rcases mul_eq_zero.1 hC' with h | h
  · exact absurd h h0
  · have : ((load P0 C : ℕ) : ℝ) = 3 := by linarith
    exact_mod_cast this

/-- `CLP(P0,3)` has no half-integral point. -/
theorem no_half_integral (x : Fin 12 → Finset (Fin 20) → ℝ) (hx : InCLP P0 3 x)
    (hh : IsHalfIntegral P0 3 x) : False := by
  classical
  let y : Fin 12 → Finset (Fin 20) → ℕ := fun i C =>
    if x i C = 1 / 2 then 1 else if x i C = 1 then 2 else 0
  have hterm : ∀ i, ∀ C ∈ configs P0 i 3,
      x i C * ∑ j ∈ C, ((w0 j : ℕ) : ℝ) = ((y i C * W C : ℕ) : ℝ) / 2 := by
    intro i C hC
    have hW : ∑ j ∈ C, ((w0 j : ℕ) : ℝ) = ((W C : ℕ) : ℝ) := by
      simp [W]
    rw [hW]
    rcases hh i C hC with h | h | h
    · simp [y, h]
    · simp [y, h]
      ring
    · simp [y, h]
  have hdiv : ∀ i, ∀ C ∈ configs P0 i 3, 3 ∣ y i C * W C := by
    intro i C hC
    by_cases h0 : x i C = 0
    · simp [y, h0]
    · have hl := support_full x hx i C hC h0
      have hbad := Finset.card_eq_zero.1 (full_mod3 i)
      have hW : W C = 0 ∨ W C = 3 := by
        by_contra hne
        simp only [not_or] at hne
        have : C ∈ (configs P0 i 3).filter (fun C => load P0 C = 3 ∧ W C ≠ 0 ∧ W C ≠ 3) :=
          Finset.mem_filter.2 ⟨hC, hl, hne.1, hne.2⟩
        rw [hbad] at this
        simp at this
      rcases hW with h | h <;> simp [h]
  have hcount := weighted_count P0 3 x hx (fun j => ((w0 j : ℕ) : ℝ))
  have hw : ∑ j, ((w0 j : ℕ) : ℝ) = 4 := by exact_mod_cast sum_w0
  rw [hw] at hcount
  rw [Finset.sum_congr rfl (fun i _ => Finset.sum_congr rfl (hterm i))] at hcount
  simp_rw [← Finset.sum_div] at hcount
  have hN : (∑ i, ∑ C ∈ configs P0 i 3, y i C * W C : ℕ) = 8 := by
    have : ((∑ i, ∑ C ∈ configs P0 i 3, y i C * W C : ℕ) : ℝ) = 8 := by
      push_cast at hcount ⊢
      linarith
    exact_mod_cast this
  have h3 : 3 ∣ (∑ i, ∑ C ∈ configs P0 i 3, y i C * W C : ℕ) :=
    Finset.dvd_sum (fun i _ => Finset.dvd_sum (fun C hC => hdiv i C hC))
  rw [hN] at h3
  omega

/-- **Main theorem.** Conjecture 10 of arXiv:2609.19967 is false. -/
theorem not_conjecture10 : ¬ Conjecture10 := by
  intro h
  obtain ⟨x, hx, hh⟩ := h 20 12 P0 3 isLeast_three
  exact no_half_integral x hx hh

end HalfIntegralCLP

#print axioms HalfIntegralCLP.not_conjecture10
