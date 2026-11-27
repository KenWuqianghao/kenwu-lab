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

/-! ## Bounds on `valD` and `maxValD` -/

section General
variable {m ι : Type*} [Fintype m] [Fintype ι]

/-- Row `i` of `U w`. -/
def av (U : Matrix m ι ℤ) (w : ι → ℝ) (i : m) : ℝ := ∑ j, (U i j : ℝ) * w j

lemma game_inl (U : Matrix m ι ℤ) (w : ι → ℝ) (i : m) :
    ((Matrix.fromRows U (-U)).map (Int.cast : ℤ → ℝ)).mulVec w (Sum.inl i) = av U w i := by
  simp [Matrix.mulVec, dotProduct, av, Matrix.fromRows_apply_inl, Matrix.fromRows_apply_inr]

lemma game_inr (U : Matrix m ι ℤ) (w : ι → ℝ) (i : m) :
    ((Matrix.fromRows U (-U)).map (Int.cast : ℤ → ℝ)).mulVec w (Sum.inr i) = -av U w i := by
  simp [Matrix.mulVec, dotProduct, av, Matrix.fromRows_apply_inl, Matrix.fromRows_apply_inr]

lemma inf_le_neg_abs (U : Matrix m ι ℤ) (w : ι → ℝ) (i : m) :
    (⨅ r, ((Matrix.fromRows U (-U)).map (Int.cast : ℤ → ℝ)).mulVec w r) ≤ -|av U w i| := by
  have hb : BddBelow (Set.range fun r =>
      ((Matrix.fromRows U (-U)).map (Int.cast : ℤ → ℝ)).mulVec w r) := (Set.finite_range _).bddBelow
  rcases abs_cases (av U w i) with ⟨h, _⟩ | ⟨h, _⟩
  · rw [h]; exact (ciInf_le hb (Sum.inr i)).trans_eq (game_inr U w i)
  · rw [h, neg_neg]; exact (ciInf_le hb (Sum.inl i)).trans_eq (game_inl U w i)

lemma neg_le_inf [Nonempty m] (U : Matrix m ι ℤ) (w : ι → ℝ) (c : ℝ) (h : ∀ i, |av U w i| ≤ c) :
    -c ≤ ⨅ r, ((Matrix.fromRows U (-U)).map (Int.cast : ℤ → ℝ)).mulVec w r := by
  apply le_ciInf
  rintro (i | i)
  · rw [game_inl]; exact neg_le_of_abs_le (h i)
  · rw [game_inr]; exact neg_le_neg (le_of_abs_le (h i))

lemma valD_le (U : Matrix m ι ℤ) (c : ℝ) (hne : (simplex ι).Nonempty)
    (h : ∀ w ∈ simplex ι, ∃ i, c ≤ |av U w i|) : valD U ≤ -c := by
  unfold valD val
  apply csSup_le (hne.image _)
  rintro _ ⟨w, hw, rfl⟩
  obtain ⟨i, hi⟩ := h w hw
  exact (inf_le_neg_abs U w i).trans (neg_le_neg hi)

lemma le_valD [Nonempty m] (U : Matrix m ι ℤ) (c : ℝ) (w : ι → ℝ) (hw : w ∈ simplex ι)
    (h : ∀ i, |av U w i| ≤ c) : -c ≤ valD U := by
  unfold valD val
  have hb : BddAbove ((fun w : ι → ℝ =>
      ⨅ r, ((Matrix.fromRows U (-U)).map (Int.cast : ℤ → ℝ)).mulVec w r) '' simplex ι) := by
    refine ⟨0, ?_⟩
    rintro _ ⟨v, -, rfl⟩
    exact (inf_le_neg_abs U v (Classical.arbitrary m)).trans (neg_nonpos.mpr (abs_nonneg _))
  exact (neg_le_inf U w c h).trans (le_csSup hb ⟨w, hw, rfl⟩)

lemma unif_mem (k : ℕ) (hk : Fintype.card ι = k) (hk0 : 0 < k) :
    (fun _ : ι => (1 : ℝ) / k) ∈ simplex ι := by
  refine ⟨fun _ => by positivity, ?_⟩
  simp only [Finset.sum_const, Finset.card_univ, hk, nsmul_eq_mul]
  field_simp

end General

lemma maxValD_le {m n : ℕ} (U : Matrix (Fin m) (Fin n) ℤ) (t : ℕ) (c : ℝ)
    [Nonempty {S : Finset (Fin n) // S.card = t}]
    (h : ∀ S : {S : Finset (Fin n) // S.card = t},
      valD (U.submatrix id (fun x : S.val => (x : Fin n))) ≤ c) : maxValD U t ≤ c :=
  ciSup_le h

lemma le_maxValD {m n : ℕ} (U : Matrix (Fin m) (Fin n) ℤ) (t : ℕ) (c : ℝ)
    (S : {S : Finset (Fin n) // S.card = t})
    (h : c ≤ valD (U.submatrix id (fun x : S.val => (x : Fin n)))) : c ≤ maxValD U t :=
  le_ciSup_of_le (Set.finite_range _).bddAbove S h

lemma list_sum_range {M : Type*} [AddCommMonoid M] (f : ℕ → M) (n : ℕ) :
    ((List.range n).map f).sum = ∑ i : Fin n, f i := by
  rw [Fin.sum_univ_eq_sum_range]
  induction n with
  | zero => simp
  | succ n ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Finset.sum_range_succ]; simp

