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

lemma ξ3_prim : IsPrimitiveRoot ξ3 3 := by
  have h := Complex.isPrimitiveRoot_exp 3 (by norm_num)
  simpa [ξ3] using h

lemma ξ3_cube : ξ3 ^ 3 = 1 := ξ3_prim.pow_eq_one

lemma ξ3_sum : 1 + ξ3 + ξ3 ^ 2 = 0 := by
  have h := ξ3_prim.geom_sum_eq_zero (by norm_num)
  simpa [Finset.sum_range_succ] using h

lemma ξ3_pow_mod (n : ℕ) : ξ3 ^ n = ξ3 ^ (n % 3) := by
  conv_lhs => rw [← Nat.div_add_mod n 3]
  rw [pow_add, pow_mul, ξ3_cube, one_pow, one_mul]

lemma ξ3_conj : (starRingEnd ℂ) ξ3 = ξ3 ^ 2 := by
  have hn : ‖ξ3‖ = 1 := ξ3_prim.norm'_eq_one (by norm_num)
  rw [← Complex.inv_eq_conj hn]
  exact inv_eq_of_mul_eq_one_right (by linear_combination ξ3_cube)

/-! ## Exponent words -/

/-- The sequence `j ↦ ξ₃^{e j}` given by an exponent word `e`. -/
def seqOf {ℓ : ℕ} (e : Fin ℓ → Fin 3) : Fin ℓ → ℂ := fun j => ξ3 ^ (e j).val

lemma seqOf_mem {ℓ : ℕ} (e : Fin ℓ → Fin 3) (j : Fin ℓ) :
    seqOf e j ∈ ({1, ξ3, ξ3 ^ 2} : Set ℂ) := by
  simp only [seqOf, Set.mem_insert_iff, Set.mem_singleton_iff]
  generalize e j = x
  fin_cases x <;> simp

/-- The exponent of `a_j · conj(a_{j+s})`, reduced mod 3. -/
def qexp {ℓ : ℕ} [NeZero ℓ] (e : Fin ℓ → Fin 3) (s j : Fin ℓ) : ℕ :=
  ((e j).val + 2 * (e (j + s)).val) % 3

/-- `M_r(s)` for one sequence: the number of `j` with `a_j · conj(a_{j+s}) = ξ₃^r`. -/
def cnt {ℓ : ℕ} [NeZero ℓ] (e : Fin ℓ → Fin 3) (s : Fin ℓ) (r : ℕ) : ℕ :=
  (univ.filter (fun j => qexp e s j = r)).card

lemma term_eq {ℓ : ℕ} [NeZero ℓ] (e : Fin ℓ → Fin 3) (s j : Fin ℓ) :
    seqOf e j * (starRingEnd ℂ) (seqOf e (j + s)) = ξ3 ^ qexp e s j := by
  simp only [seqOf, qexp, map_pow, ξ3_conj, ← pow_mul, ← pow_add]
  rw [ξ3_pow_mod]

lemma PAF_seqOf {ℓ : ℕ} [NeZero ℓ] (e : Fin ℓ → Fin 3) (s : Fin ℓ) :
    PAF (seqOf e) s = (cnt e s 0 : ℂ) + (cnt e s 1 : ℂ) * ξ3 + (cnt e s 2 : ℂ) * ξ3 ^ 2 := by
  unfold PAF
  simp_rw [term_eq]
  have hmaps : ∀ j ∈ (univ : Finset (Fin ℓ)), qexp e s j ∈ range 3 := by
    intro j _
    simp only [mem_range, qexp]
    exact Nat.mod_lt _ (by norm_num)
  rw [← Finset.sum_fiberwise_of_maps_to hmaps]
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add]
  have hfib : ∀ r : ℕ, (∑ j ∈ univ.filter (fun j => qexp e s j = r), ξ3 ^ qexp e s j)
      = (cnt e s r : ℂ) * ξ3 ^ r := by
    intro r
    rw [Finset.sum_congr rfl (fun j hj => by rw [(Finset.mem_filter.mp hj).2])]
    simp [cnt]
  rw [hfib 0, hfib 1, hfib 2]
  simp

/-! ## The certificate -/

/-- Exponent word of `A`: `02021220020100021222201110110121211`. -/
def eA : Fin 35 → Fin 3 :=
  ![0,2,0,2,1,2,2,0,0,2,0,1,0,0,0,2,1,2,2,2,2,0,1,1,1,0,1,1,0,1,2,1,2,1,1]

/-- Exponent word of `B`: `01222010111021021121200221100200122`. -/
def eB : Fin 35 → Fin 3 :=
  ![0,1,2,2,2,0,1,0,1,1,1,0,2,1,0,2,1,1,2,1,2,0,0,2,2,1,1,0,0,2,0,0,1,2,2]

/-- Combined counts `(M₀, M₁, M₂)(s) = (22, 24, 24)` for every nonzero lag `s`. -/
lemma counts_ok : ∀ s : Fin 35, s ≠ 0 →
    cnt eA s 0 + cnt eB s 0 = 22 ∧ cnt eA s 1 + cnt eB s 1 = 24 ∧
    cnt eA s 2 + cnt eB s 2 = 24 := by
  decide

/-- **Main theorem.** A ternary Legendre pair of length 35 exists. -/
theorem exists_ternary_legendre_pair_35 :
    ∃ A B : Fin 35 → ℂ, IsTernaryLegendrePair 35 A B := by
  refine ⟨seqOf eA, seqOf eB, seqOf_mem eA, seqOf_mem eB, ?_⟩
  intro s hs1 hs2
  have hs0 : s ≠ 0 := by
    intro h
    subst h
    simp at hs1
  obtain ⟨h0, h1, h2⟩ := counts_ok _ hs0
  rw [PAF_seqOf, PAF_seqOf]
  have e0 : (cnt eA s 0 : ℂ) + cnt eB s 0 = 22 := by exact_mod_cast h0
  have e1 : (cnt eA s 1 : ℂ) + cnt eB s 1 = 24 := by exact_mod_cast h1
  have e2 : (cnt eA s 2 : ℂ) + cnt eB s 2 = 24 := by exact_mod_cast h2
  linear_combination e0 + ξ3 * e1 + ξ3 ^ 2 * e2 + 24 * ξ3_sum

end

#print axioms exists_ternary_legendre_pair_35
