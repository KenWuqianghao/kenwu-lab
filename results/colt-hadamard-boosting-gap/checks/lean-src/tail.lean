
theorem cover_all : ∀ a b : Fin 16, a < b → ∀ c d e f : Fin 16, b < c → c < d → d < e → e < f →
    ∃ p, valid p = true ∧ covers p a b c d e f = true := by
  rintro ⟨a, ha⟩ ⟨b, hb⟩
  interval_cases a <;> interval_cases b
  -- CASES --

lemma valid_spec (p : ℕ) (h : valid p = true) :
    0 < ∑ i : Fin 15, |yOf (p / 65536) i| ∧ ∀ c : Fin 16, p.testBit c = true →
      3 * ∑ i : Fin 15, |yOf (p / 65536) i| ≤ 7 * ∑ i : Fin 15, yOf (p / 65536) i * Umat i c := by
  simp only [valid, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range,
    Bool.or_eq_true, Bool.not_eq_true'] at h
  obtain ⟨h1, h2⟩ := h
  have e1 : l1 (p / 65536) = ∑ i : Fin 15, |yOf (p / 65536) i| := list_sum_range _ 15
  refine ⟨e1 ▸ h1, fun c hc => ?_⟩
  have e2 : dotc (p / 65536) c = ∑ i : Fin 15, yOf (p / 65536) i * Umat i c := list_sum_range _ 15
  rcases h2 c c.isLt with h3 | h3
  · simp [hc] at h3
  · rw [← e1, ← e2]; exact h3

theorem cert (S : Finset (Fin 16)) (hS : S.card = 6) : ∃ y : Fin 15 → ℤ, 0 < ∑ i, |y i| ∧
    ∀ c ∈ S, 3 * ∑ i, |y i| ≤ 7 * ∑ i, y i * Umat i c := by
  set e := S.orderEmbOfFin hS
  have m : ∀ i j : Fin 6, i < j → e i < e j := fun i j h => e.strictMono h
  obtain ⟨p, hv, hc⟩ := cover_all (e 0) (e 1) (m 0 1 (by decide)) (e 2) (e 3) (e 4) (e 5)
    (m 1 2 (by decide)) (m 2 3 (by decide)) (m 3 4 (by decide)) (m 4 5 (by decide))
  obtain ⟨hpos, hcol⟩ := valid_spec p hv
  refine ⟨fun i => yOf (p / 65536) i, hpos, fun c hcS => hcol c ?_⟩
  have hr : c ∈ Set.range e := by rw [Finset.range_orderEmbOfFin]; exact hcS
  obtain ⟨i, rfl⟩ := hr
  simp only [covers, Bool.and_eq_true] at hc
  obtain ⟨⟨⟨⟨⟨h0, h1⟩, h2⟩, h3⟩, h4⟩, h5⟩ := hc
  fin_cases i <;> assumption

lemma Umat_pm : ∀ i j, Umat i j = 1 ∨ Umat i j = -1 := by
  intro i j; unfold Umat; split <;> simp

lemma Umat_rows : ∀ i : Fin 15, ∑ j, Umat i j = 0 := by decide +kernel

lemma valD_Umat : valD Umat = 0 := by
  have hu := unif_mem (ι := Fin 16) 16 (by simp) (by norm_num)
  apply le_antisymm
  · simpa using valD_le Umat 0 ⟨_, hu⟩ (fun w _ => ⟨0, abs_nonneg _⟩)
  · have := le_valD Umat 0 _ hu (fun i => by
      have h := congrArg (Int.cast : ℤ → ℝ) (Umat_rows i)
      push_cast at h
      simp only [av, ← Finset.sum_mul, h, zero_mul, abs_zero, le_refl])
    simpa using this

lemma U_bound (S : Finset (Fin 16)) (hS : S.card = 6) :
    valD (Umat.submatrix id (fun x : S => (x : Fin 16))) ≤ -(3 / 7) := by
  obtain ⟨y, hy0, hy⟩ := cert S hS
  apply valD_le _ _ ⟨_, unif_mem 6 (by simp [hS]) (by norm_num)⟩
  intro w hw
  set a := av (Umat.submatrix id (fun x : S => (x : Fin 16))) w
  obtain ⟨i0, -, hi0⟩ := Finset.exists_max_image Finset.univ (fun i => |a i|) Finset.univ_nonempty
  refine ⟨i0, ?_⟩
  set Y : ℝ := ∑ i, |(y i : ℝ)|
  have hY : 0 < Y := by
    have := (Int.cast_lt (R := ℝ)).mpr hy0; push_cast at this; simpa [Y] using this
  have h1 : ∑ i, (y i : ℝ) * a i ≤ Y * |a i0| := by
    rw [Finset.sum_mul]
    apply Finset.sum_le_sum; intro i _
    calc (y i : ℝ) * a i ≤ |(y i : ℝ) * a i| := le_abs_self _
      _ = |(y i : ℝ)| * |a i| := abs_mul _ _
      _ ≤ |(y i : ℝ)| * |a i0| := mul_le_mul_of_nonneg_left (hi0 i (Finset.mem_univ _)) (abs_nonneg _)
  have h2 : 3 / 7 * Y ≤ ∑ i, (y i : ℝ) * a i := by
    have e : ∑ i, (y i : ℝ) * a i = ∑ x : S, w x * ∑ i, (y i : ℝ) * (Umat i x : ℝ) := by
      simp only [a, av, Matrix.submatrix_apply, id, Finset.mul_sum]
      rw [Finset.sum_comm]
      exact Finset.sum_congr rfl (fun x _ => Finset.sum_congr rfl (fun i _ => by ring))
    rw [e]
    have hc : ∀ x : S, 3 / 7 * Y ≤ ∑ i, (y i : ℝ) * (Umat i x : ℝ) := by
      intro x
      have := (Int.cast_le (R := ℝ)).mpr (hy x x.2)
      push_cast at this
      simp only [Y]; linarith
    calc 3 / 7 * Y = ∑ x : S, w x * (3 / 7 * Y) := by rw [← Finset.sum_mul, hw.2, one_mul]
      _ ≤ _ := Finset.sum_le_sum fun x _ => mul_le_mul_of_nonneg_left (hc x) (hw.1 x)
  have : 3 / 7 * Y ≤ |a i0| * Y := by linarith
  exact le_of_mul_le_mul_right this hY

/-! ## The Sylvester side -/

def Hh : Matrix (Fin 15) (Fin 16) ℤ := hhat 4

def S0 : Finset (Fin 16) := {0, 1, 2, 4, 8, 15}

lemma S0_card : S0.card = 6 := by decide

lemma Hh_S0 : ∀ i : Fin 15, |∑ c ∈ S0, Hh i c| ≤ 2 := by decide +kernel

lemma H_bound : -(1 / 3 : ℝ) ≤ valD (Hh.submatrix id (fun x : S0 => (x : Fin 16))) := by
  apply le_valD _ _ _ (unif_mem 6 (by simp [S0_card]) (by norm_num))
  intro i
  have h := (Int.cast_le (R := ℝ)).mpr (Hh_S0 i)
  push_cast at h
  have e : av (Hh.submatrix id (fun x : S0 => (x : Fin 16))) (fun _ => (1 : ℝ) / (6 : ℕ)) i
      = (∑ c ∈ S0, (Hh i c : ℝ)) / 6 := by
    simp only [av, Matrix.submatrix_apply, id, ← Finset.sum_mul]
    rw [Finset.sum_coe_sort S0 (fun c => (Hh i c : ℝ))]
    push_cast; ring
  rw [e, abs_div, abs_of_pos (by norm_num : (0 : ℝ) < 6)]
  linarith

/-- **Main theorem.** Conjecture 2 of Nie, Warmuth, Vishwanathan and Zhang is false for
`n = 16` (`k = 4`), with `Ĥ` from the Sylvester Hadamard matrix. -/
theorem conjecture2_false : ¬ Conjecture2 4 := by
  intro h
  have hU : maxValD Hh 6 ≤ maxValD Umat 6 := h Umat Umat_pm valD_Umat 6 (by norm_num) (by norm_num)
  have h1 : -(1 / 3 : ℝ) ≤ maxValD Hh 6 := le_maxValD Hh 6 _ ⟨S0, S0_card⟩ H_bound
  have h2 : maxValD Umat 6 ≤ -(3 / 7) := by
    haveI : Nonempty {S : Finset (Fin 16) // S.card = 6} := ⟨⟨S0, S0_card⟩⟩
    exact maxValD_le _ _ _ (fun S => U_bound S.1 S.2)
  linarith

#print axioms conjecture2_false

end HadamardBoosting
