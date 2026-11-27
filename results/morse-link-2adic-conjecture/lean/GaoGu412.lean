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

/-! ## From the path definition to a recursion -/

def st (u : Bool) : ℤ := if u then 1 else -1

lemma height_nil : height [] = 0 := rfl

lemma height_cons (u : Bool) (l : List Bool) : height (u :: l) = st u + height l := by
  simp [height, st]

/-- Validity from start height `h`, step by step. -/
def okR (h : ℤ) : List Bool → Prop
  | [] => h = 0
  | u :: l => 0 ≤ h ∧ okR (h + st u) l

/-- Weight from start height `h`, step by step. -/
def wR (b : ℤ → ℤ) (h : ℤ) : List Bool → ℤ
  | [] => 1
  | u :: l => (if u then b h else 1) * wR b (h + st u) l

lemma ok_iff (l : List Bool) : ∀ h : ℤ,
    ((∀ k ≤ l.length, 0 ≤ h + height (l.take k)) ∧ h + height l = 0) ↔ okR h l := by
  induction l with
  | nil => intro h; simp [okR, height_nil]; omega
  | cons u l ih =>
    intro h
    rw [okR, ← ih (h + st u)]
    constructor
    · rintro ⟨h1, h2⟩
      refine ⟨by simpa [height_nil] using h1 0 (Nat.zero_le _), fun k hk => ?_, ?_⟩
      · have := h1 (k + 1) (by simpa using hk)
        simpa [List.take_succ_cons, height_cons, add_assoc] using this
      · simpa [height_cons, add_assoc] using h2
    · rintro ⟨h0, h1, h2⟩
      refine ⟨fun k hk => ?_, by simpa [height_cons, add_assoc] using h2⟩
      cases k with
      | zero => simpa [height_nil] using h0
      | succ k =>
        have := h1 k (by simpa using hk)
        simpa [List.take_succ_cons, height_cons, add_assoc] using this

lemma weight_eq (b : ℤ → ℤ) (l : List Bool) : ∀ h : ℤ,
    ((List.range l.length).map fun k =>
      if l.getD k false then b (h + height (l.take k)) else 1).prod = wR b h l := by
  induction l with
  | nil => intro h; simp [wR]
  | cons u l ih =>
    intro h
    rw [wR, ← ih (h + st u), List.length_cons, List.range_succ_eq_map]
    simp [List.map_cons, List.prod_cons, List.map_map, Function.comp_def, height_cons,
      height_nil, add_assoc]

/-- The weighted sum over all step sequences of length `m` from height `h`. -/
noncomputable def S (b : ℤ → ℤ) (m : ℕ) (h : ℤ) : ℤ := by
  classical exact ∑ f : Fin m → Bool, if okR h (List.ofFn f) then wR b h (List.ofFn f) else 0

lemma weightedCatalan_eq (b : ℤ → ℤ) (n : ℕ) : weightedCatalan b n = S b (2 * n) 0 := by
  classical
  unfold weightedCatalan S
  refine Finset.sum_congr rfl fun f _ => ?_
  have h1 : IsDyckPath n (List.ofFn f) ↔ okR 0 (List.ofFn f) := by
    rw [← ok_iff]; simp [IsDyckPath]
  have h2 : weight b (List.ofFn f) = wR b 0 (List.ofFn f) := by
    rw [← weight_eq]; simp [weight]
  rw [h2]; exact if_congr h1 rfl rfl

lemma S_zero (b : ℤ → ℤ) (h : ℤ) : S b 0 h = if h = 0 then 1 else 0 := by
  classical
  unfold S
  simp [okR, wR]

lemma S_succ (b : ℤ → ℤ) (m : ℕ) (h : ℤ) :
    S b (m + 1) h = if 0 ≤ h then b h * S b m (h + 1) + S b m (h + -1) else 0 := by
  classical
  unfold S
  rw [← (Fin.consEquiv fun _ => Bool).sum_comp, Fintype.sum_prod_type, Fintype.sum_bool]
  simp only [Fin.consEquiv, Equiv.coe_fn_mk, List.ofFn_succ, Fin.cons_zero, Fin.cons_succ,
    okR, wR, st, ite_true, Bool.false_eq_true, ite_false, one_mul]
  split_ifs with h0
  · simp only [h0, true_and, Finset.mul_sum, mul_ite, mul_zero]
  · simp [h0]

lemma S_neg (b : ℤ → ℤ) (m : ℕ) (h : ℤ) (hh : h < 0) : S b m h = 0 := by
  cases m with
  | zero => rw [S_zero]; simp [hh.ne]
  | succ m => rw [S_succ]; simp [not_le.2 hh]

lemma S_high (b : ℤ → ℤ) (m : ℕ) : ∀ h : ℤ, (m : ℤ) < h → S b m h = 0 := by
  induction m with
  | zero => intro h hh; rw [S_zero]; simp [(show h ≠ 0 by omega)]
  | succ m ih =>
    intro h hh
    rw [S_succ, ih _ (by push_cast at hh; omega), ih _ (by push_cast at hh; omega)]
    simp

/-! ## A fast evaluation of `S` by rows of heights -/

def W : ℕ := 40

def row0 : List ℤ := (List.range W).map fun h => if h = 0 then 1 else 0

def rowStep (b : ℤ → ℤ) (l : List ℤ) : List ℤ :=
  (List.range W).map fun h : ℕ =>
    b (h : ℤ) * l.getD (h + 1) 0 + (if h = 0 then 0 else l.getD (h - 1) 0)

def rows (b : ℤ → ℤ) : ℕ → List ℤ
  | 0 => row0
  | m + 1 => rowStep b (rows b m)

lemma getD_map_range (f : ℕ → ℤ) (h : ℕ) :
    ((List.range W).map f).getD h 0 = if h < W then f h else 0 := by
  by_cases hh : h < W
  · simp [hh, List.getD_eq_getElem?_getD]
  · simp [hh, List.getD_eq_getElem?_getD, List.getElem?_range]

lemma rows_spec (b : ℤ → ℤ) : ∀ m : ℕ, m < W → ∀ h : ℕ, (rows b m).getD h 0 = S b m h := by
  intro m
  induction m with
  | zero =>
    intro _ h
    rw [rows, row0, getD_map_range, S_zero]
    split_ifs <;> simp_all [W] <;> omega
  | succ m ih =>
    intro hm h
    rw [rows, rowStep, getD_map_range, S_succ, if_pos (show (0 : ℤ) ≤ h by positivity)]
    by_cases hW : h < W
    · rw [if_pos hW, ih (by omega) (h + 1), Nat.cast_add, Nat.cast_one]
      by_cases h0 : h = 0
      · subst h0
        rw [if_pos rfl, S_neg b m (((0 : ℕ) : ℤ) + -1) (by norm_num)]
      · rw [if_neg h0, ih (by omega) (h - 1)]
        have e : ((h - 1 : ℕ) : ℤ) = (h : ℤ) + -1 := by omega
        rw [e]
    · rw [if_neg hW, S_high _ _ _ (by unfold W at *; push_cast; omega),
        S_high _ _ _ (by unfold W at *; push_cast; omega)]
      simp

lemma S_eval (b : ℤ → ℤ) (m : ℕ) (hm : m < W) : S b m 0 = (rows b m).getD 0 0 := by
  rw [rows_spec b m hm 0]; rfl

/-! ## The three values -/

lemma val_of (x : ℤ) (n : ℕ) (hx : x ≠ 0) (h1 : (2 : ℤ) ^ n ∣ x) (h2 : ¬ (2 : ℤ) ^ (n + 1) ∣ x) :
    padicValInt 2 x = n := by
  have a := (padicValInt_dvd_iff (p := 2) n x).1 (by exact_mod_cast h1)
  have b : ¬ (n + 1 ≤ padicValInt 2 x) := fun hb =>
    h2 (by exact_mod_cast (padicValInt_dvd_iff (p := 2) (n + 1) x).2 (Or.inr hb))
  omega

lemma LC_eq (n : ℕ) (hn : 2 * n < W) :
    L 2 n - C n = (rows (fun x => (2 * x + 1) ^ (2 * 2)) (2 * n)).getD 0 0 -
      (rows (fun _ => 1) (2 * n)).getD 0 0 := by
  rw [L, C, weightedCatalan_eq, weightedCatalan_eq, S_eval _ _ hn, S_eval _ _ hn]

lemma val2 : padicValInt 2 (L 2 2 - C 2) = 4 := by
  rw [LC_eq 2 (by decide)]
  apply val_of <;> decide +kernel

lemma val3 : padicValInt 2 (L 2 3 - C 3) = 13 := by
  rw [LC_eq 3 (by decide)]
  apply val_of <;> decide +kernel

lemma val19 : padicValInt 2 (L 2 19 - C 19) = 11 := by
  rw [LC_eq 19 (by decide)]
  apply val_of <;> decide +kernel

/-! ## The 2-adic argument -/

lemma dvd_of_le_val {x : ℤ_[2]} (hx : x ≠ 0) {j : ℕ} (hj : j ≤ x.valuation) :
    ((2 : ℕ) : ℤ_[2]) ^ j ∣ x := by
  have := (PadicInt.mem_span_pow_iff_le_valuation x hx j).2 hj
  rwa [Ideal.mem_span_singleton] at this

/-- Conjecture 4.12 of Gao–Gu is false for `k = 2`. -/
theorem conjecture_4_12_false_k2 : ¬ Conjecture412 2 := by
  rintro ⟨α, c, h⟩
  obtain ⟨-, h2⟩ := h 2 (by norm_num)
  obtain ⟨h3ne, h3⟩ := h 3 (by norm_num)
  obtain ⟨h19ne, h19⟩ := h 19 (by norm_num)
  rw [val2, show s2 2 = 1 by norm_num [s2]] at h2
  rw [val3, show s2 3 = 2 by norm_num [s2]] at h3
  rw [val19, show s2 19 = 3 by norm_num [s2]] at h19
  have d3 := dvd_of_le_val h3ne (j := 8 - c) (by omega)
  have d19 := dvd_of_le_val h19ne (j := 8 - c) (by omega)
  have d16 : ((2 : ℕ) : ℤ_[2]) ^ (8 - c) ∣ ((16 : ℤ) : ℤ_[2]) := by
    have := dvd_sub d19 d3
    convert this using 1
    push_cast; ring
  rw [PadicInt.pow_p_dvd_int_iff] at d16
  have : (2 : ℤ) ^ 5 ∣ 16 := (pow_dvd_pow 2 (by omega : 5 ≤ 8 - c)).trans (by exact_mod_cast d16)
  norm_num at this

/-- Conjecture 4.12 of Gao–Gu ("for every positive integer `k`") is false. -/
theorem conjecture_4_12_false : ¬ ∀ k : ℕ, 0 < k → Conjecture412 k :=
  fun h => conjecture_4_12_false_k2 (h 2 (by norm_num))

end GaoGu

#print axioms GaoGu.conjecture_4_12_false_k2
#print axioms GaoGu.conjecture_4_12_false
