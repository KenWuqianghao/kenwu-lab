import Mathlib

open Finset

namespace SPD

/-- An involution of a finite set has as many fixed points as elements, modulo 2. -/
lemma card_mod_two_eq_fixed {α : Type*} [DecidableEq α] (s : Finset α) (f : α → α)
    (h1 : ∀ x ∈ s, f x ∈ s) (h2 : ∀ x ∈ s, f (f x) = x) :
    s.card % 2 = (s.filter (fun x => f x = x)).card % 2 := by
  have key : ∑ x ∈ s.filter (fun x => ¬ f x = x), (1 : ZMod 2) = 0 := by
    refine Finset.sum_involution (fun x _ => f x) ?_ ?_ ?_ ?_
    · intro a _; decide
    · intro a ha _
      exact (mem_filter.1 ha).2
    · intro a ha
      obtain ⟨has, hne⟩ := mem_filter.1 ha
      refine mem_filter.2 ⟨h1 a has, ?_⟩
      rw [h2 a has]; exact fun h => hne h.symm
    · intro a ha
      exact h2 a (mem_filter.1 ha).1
  rw [sum_const, nsmul_eq_mul, mul_one, ZMod.natCast_eq_zero_iff] at key
  have := card_filter_add_card_filter_not (s := s) (fun x => f x = x)
  omega

/-- If an involution exchanges `P` and `¬ P`, then the set has twice as many elements
as its part where `P` holds. -/
lemma card_eq_two_mul {α : Type*} [DecidableEq α] (s : Finset α) (f : α → α)
    (P : α → Prop) [DecidablePred P]
    (h1 : ∀ x ∈ s, f x ∈ s) (h2 : ∀ x ∈ s, f (f x) = x) (h3 : ∀ x ∈ s, (P x ↔ ¬ P (f x))) :
    s.card = 2 * (s.filter P).card := by
  have := card_filter_add_card_filter_not (s := s) P
  have h : (s.filter (fun x => ¬ P x)).card = (s.filter P).card := by
    refine card_nbij' f f ?_ ?_ ?_ ?_
    · intro x hx
      simp only [coe_filter, Set.mem_ofPred_eq] at hx ⊢
      refine ⟨h1 x hx.1, ?_⟩
      have := h3 x hx.1; tauto
    · intro x hx
      simp only [coe_filter, Set.mem_ofPred_eq] at hx ⊢
      refine ⟨h1 x hx.1, ?_⟩
      have := h3 (f x) (h1 x hx.1); rw [h2 x hx.1] at this; tauto
    · intro x hx; simp only [coe_filter, Set.mem_ofPred_eq] at hx; exact h2 x hx.1
    · intro x hx; simp only [coe_filter, Set.mem_ofPred_eq] at hx; exact h2 x hx.1
  omega

lemma sq_mod_eight (w : ℕ) : w ^ 2 % 8 = 0 ∨ w ^ 2 % 8 = 1 ∨ w ^ 2 % 8 = 4 := by
  rw [Nat.pow_mod]
  have h := Nat.mod_lt w (show 8 > 0 by norm_num)
  interval_cases (w % 8) <;> simp

lemma sq_mod_eight_odd {w : ℕ} (hw : w % 2 = 1) : w ^ 2 % 8 = 1 := by
  rw [Nat.pow_mod]
  have h := Nat.mod_lt w (show 8 > 0 by norm_num)
  have h2 : w % 8 % 2 = 1 := by omega
  interval_cases hh : (w % 8) <;> simp_all

lemma sq_mod_four_even {w : ℕ} (hw : w % 2 = 0) : w ^ 2 % 4 = 0 := by
  rw [Nat.pow_mod]
  have h := Nat.mod_lt w (show 4 > 0 by norm_num)
  have h2 : w % 4 % 2 = 0 := by omega
  interval_cases hh : (w % 4) <;> simp_all

lemma mul_mod_four_one {a b : ℕ} (h : a * b % 4 = 1) : a % 4 = b % 4 := by
  rw [Nat.mul_mod] at h
  have ha := Nat.mod_lt a (show 4 > 0 by norm_num)
  have hb := Nat.mod_lt b (show 4 > 0 by norm_num)
  interval_cases (a % 4) <;> interval_cases (b % 4) <;> simp_all

lemma mul_mod_four_two {a b : ℕ} (h : a * b % 4 = 2) : (b % 2 = 0 ↔ ¬ a % 2 = 0) := by
  rw [Nat.mul_mod] at h
  have ha := Nat.mod_lt a (show 4 > 0 by norm_num)
  have hb := Nat.mod_lt b (show 4 > 0 by norm_num)
  have ea : a % 2 = a % 4 % 2 := by omega
  have eb : b % 2 = b % 4 % 2 := by omega
  rw [ea, eb]
  interval_cases (a % 4) <;> interval_cases (b % 4) <;> simp_all


/-! ## The sets -/

/-- Triples `(k, a, b)` of positive integers with `k² + a b = N`. -/
def Xs (N : ℕ) : Finset (ℕ × ℕ × ℕ) :=
  (range (N + 1) ×ˢ range (N + 1) ×ˢ range (N + 1)).filter
    (fun t => 0 < t.1 ∧ 0 < t.2.1 ∧ 0 < t.2.2 ∧ t.1 ^ 2 + t.2.1 * t.2.2 = N)

lemma mem_Xs {N k a b : ℕ} :
    (k, a, b) ∈ Xs N ↔ 0 < k ∧ 0 < a ∧ 0 < b ∧ k ^ 2 + a * b = N := by
  simp only [Xs, mem_filter, mem_product, mem_range]
  constructor
  · tauto
  · rintro ⟨hk, ha, hb, h⟩
    refine ⟨⟨?_, ?_, ?_⟩, hk, ha, hb, h⟩ <;> nlinarith

/-- Quadruples `(k, x, y, z)` with `k` odd, `x, y, z ≥ 1` and `k² + x² + 4 y z = N`. -/
def Zs (N : ℕ) : Finset (ℕ × ℕ × ℕ × ℕ) :=
  (range (N + 1) ×ˢ range (N + 1) ×ˢ range (N + 1) ×ˢ range (N + 1)).filter
    (fun t => t.1 % 2 = 1 ∧ 0 < t.2.1 ∧ 0 < t.2.2.1 ∧ 0 < t.2.2.2 ∧
      t.1 ^ 2 + t.2.1 ^ 2 + 4 * t.2.2.1 * t.2.2.2 = N)

lemma mem_Zs {N k x y z : ℕ} :
    (k, x, y, z) ∈ Zs N ↔ k % 2 = 1 ∧ 0 < x ∧ 0 < y ∧ 0 < z ∧
      k ^ 2 + x ^ 2 + 4 * y * z = N := by
  simp only [Zs, mem_filter, mem_product, mem_range]
  constructor
  · tauto
  · rintro ⟨hk, hx, hy, hz, h⟩
    have : 0 < k := by omega
    refine ⟨⟨?_, ?_, ?_, ?_⟩, hk, hx, hy, hz, h⟩ <;> nlinarith

/-- Zagier's involution, acting on `(x, y, z)` and keeping `k`. -/
def zag (t : ℕ × ℕ × ℕ × ℕ) : ℕ × ℕ × ℕ × ℕ :=
  if t.2.1 + t.2.2.2 < t.2.2.1 then
    (t.1, t.2.1 + 2 * t.2.2.2, t.2.2.2, t.2.2.1 - t.2.1 - t.2.2.2)
  else if t.2.1 < 2 * t.2.2.1 then
    (t.1, 2 * t.2.2.1 - t.2.1, t.2.2.1, t.2.1 + t.2.2.2 - t.2.2.1)
  else
    (t.1, t.2.1 - 2 * t.2.2.1, t.2.1 - t.2.2.1 + t.2.2.2, t.2.2.1)

variable {N : ℕ}

lemma Zs_facts (hN : N % 8 = 6) {k x y z : ℕ} (h : (k, x, y, z) ∈ Zs N) :
    x % 2 = 1 ∧ x + z ≠ y := by
  rw [mem_Zs] at h
  obtain ⟨hk, hx, hy, hz, hE⟩ := h
  have hk8 := sq_mod_eight_odd hk
  constructor
  · by_contra hxe
    have hx4 := sq_mod_four_even (w := x) (by omega)
    have : 4 * y * z = 4 * (y * z) := by ring
    omega
  · intro hyz
    subst hyz
    have h2 : k ^ 2 + (x + 2 * z) ^ 2 = N := by rw [← hE]; ring
    have := sq_mod_eight (x + 2 * z)
    omega

lemma zag_mem (hN : N % 8 = 6) : ∀ t ∈ Zs N, zag t ∈ Zs N := by
  rintro ⟨k, x, y, z⟩ h
  obtain ⟨hxo, hne⟩ := Zs_facts hN h
  rw [mem_Zs] at h
  obtain ⟨hk, hx, hy, hz, hE⟩ := h
  have hE' : (k : ℤ) ^ 2 + (x : ℤ) ^ 2 + 4 * y * z = N := by exact_mod_cast hE
  unfold zag
  dsimp only
  split_ifs with h1 h2
  · rw [mem_Zs]
    refine ⟨hk, by omega, hz, by omega, ?_⟩
    have e : ((y - x - z : ℕ) : ℤ) = y - x - z := by omega
    have : ((k ^ 2 + (x + 2 * z) ^ 2 + 4 * z * (y - x - z) : ℕ) : ℤ) = N := by
      push_cast [e]; linear_combination hE'
    exact_mod_cast this
  · rw [mem_Zs]
    refine ⟨hk, by omega, hy, by omega, ?_⟩
    have e1 : ((2 * y - x : ℕ) : ℤ) = 2 * y - x := by omega
    have e2 : ((x + z - y : ℕ) : ℤ) = x + z - y := by omega
    have : ((k ^ 2 + (2 * y - x) ^ 2 + 4 * y * (x + z - y) : ℕ) : ℤ) = N := by
      push_cast [e1, e2]; linear_combination hE'
    exact_mod_cast this
  · rw [mem_Zs]
    refine ⟨hk, by omega, by omega, hy, ?_⟩
    have e1 : ((x - 2 * y : ℕ) : ℤ) = x - 2 * y := by omega
    have e2 : ((x - y + z : ℕ) : ℤ) = x - y + z := by omega
    have : ((k ^ 2 + (x - 2 * y) ^ 2 + 4 * (x - y + z) * y : ℕ) : ℤ) = N := by
      push_cast [e1, e2]; linear_combination hE'
    exact_mod_cast this

lemma zag_eq (k x y z : ℕ) : zag (k, x, y, z) =
    if x + z < y then (k, x + 2 * z, z, y - x - z)
    else if x < 2 * y then (k, 2 * y - x, y, x + z - y)
    else (k, x - 2 * y, x - y + z, y) := rfl

lemma zag_zag (hN : N % 8 = 6) : ∀ t ∈ Zs N, zag (zag t) = t := by
  rintro ⟨k, x, y, z⟩ h
  obtain ⟨hxo, hne⟩ := Zs_facts hN h
  rw [mem_Zs] at h
  obtain ⟨hk, hx, hy, hz, hE⟩ := h
  rw [zag_eq k x y z]
  split_ifs with h1 h2
  · rw [zag_eq, if_neg (by omega), if_neg (by omega)]
    simp only [Prod.mk.injEq, and_true, true_and]; omega
  · rw [zag_eq, if_neg (by omega), if_pos (by omega)]
    simp only [Prod.mk.injEq, and_true, true_and]; omega
  · rw [zag_eq, if_pos (by omega)]
    simp only [Prod.mk.injEq, and_true, true_and]; omega

lemma zag_fixed (hN : N % 8 = 6) :
    (Zs N).filter (fun t => zag t = t) = (Zs N).filter (fun t => t.2.1 = t.2.2.1) := by
  refine filter_congr ?_
  rintro ⟨k, x, y, z⟩ h
  obtain ⟨hxo, hne⟩ := Zs_facts hN h
  rw [mem_Zs] at h
  obtain ⟨hk, hx, hy, hz, hE⟩ := h
  rw [zag_eq k x y z]
  split_ifs <;> simp only [Prod.mk.injEq, and_true, true_and] <;> omega

/-! ## Odd `k`: from `X₁` to the Zagier set -/

/-- Swap of the last two coordinates of a triple. -/
def sw3 (t : ℕ × ℕ × ℕ) : ℕ × ℕ × ℕ := (t.1, t.2.2, t.2.1)

lemma sw3_mem : ∀ t ∈ Xs N, sw3 t ∈ Xs N := by
  rintro ⟨k, a, b⟩ h
  rw [mem_Xs] at h
  show (k, b, a) ∈ Xs N
  obtain ⟨hk, ha, hb, hE⟩ := h
  rw [mem_Xs]
  exact ⟨hk, hb, ha, by rw [mul_comm]; exact hE⟩

/-- Triples of `Xs N` with `k` odd. -/
def X1 (N : ℕ) : Finset (ℕ × ℕ × ℕ) := (Xs N).filter (fun t => t.1 % 2 = 1)

/-- Triples of `Xs N` with `k` even. -/
def X0 (N : ℕ) : Finset (ℕ × ℕ × ℕ) := (Xs N).filter (fun t => ¬ t.1 % 2 = 1)

lemma card_split : (Xs N).card = (X1 N).card + (X0 N).card :=
  (card_filter_add_card_filter_not _).symm

lemma odd_facts (hN : N % 8 = 6) {k a b : ℕ} (h : (k, a, b) ∈ Xs N) (hk : k % 2 = 1) :
    a % 4 = b % 4 ∧ a ≠ b := by
  rw [mem_Xs] at h
  obtain ⟨_, ha, hb, hE⟩ := h
  have hk8 := sq_mod_eight_odd hk
  have hab : a * b % 8 = 5 := by omega
  refine ⟨mul_mod_four_one (by omega), ?_⟩
  rintro rfl
  have := sq_mod_eight a
  rw [sq] at this
  omega

lemma card_X1 (hN : N % 8 = 6) :
    (X1 N).card = 2 * ((X1 N).filter (fun t => t.2.1 < t.2.2)).card := by
  refine card_eq_two_mul _ sw3 _ ?_ ?_ ?_
  · rintro ⟨k, a, b⟩ h
    simp only [X1, mem_filter] at h ⊢
    exact ⟨sw3_mem _ h.1, h.2⟩
  · rintro ⟨k, a, b⟩ _; rfl
  · rintro ⟨k, a, b⟩ h
    simp only [X1, mem_filter] at h
    have := (odd_facts hN h.1 h.2).2
    show a < b ↔ ¬ b < a
    omega

lemma card_X1_lt (hN : N % 8 = 6) :
    ((X1 N).filter (fun t => t.2.1 < t.2.2)).card =
      ((Zs N).filter (fun t => t.2.1 = t.2.2.1)).card := by
  refine card_nbij' (fun t => (t.1, t.2.1, t.2.1, (t.2.2 - t.2.1) / 4))
    (fun t => (t.1, t.2.1, t.2.1 + 4 * t.2.2.2)) ?_ ?_ ?_ ?_
  · rintro ⟨k, a, b⟩ h
    simp only [X1, mem_coe, mem_filter] at h
    obtain ⟨⟨hX, hk⟩, hlt⟩ := h
    obtain ⟨h4, -⟩ := odd_facts hN hX hk
    rw [mem_Xs] at hX
    obtain ⟨-, ha, hb, hE⟩ := hX
    simp only [mem_coe, mem_filter, mem_Zs]
    have hb' : b = a + 4 * ((b - a) / 4) := by omega
    refine ⟨⟨hk, ha, ha, by omega, ?_⟩, trivial⟩
    have e : k ^ 2 + a ^ 2 + 4 * a * ((b - a) / 4) = k ^ 2 + a * b := by
      conv_rhs => rw [hb']
      ring
    rw [e, hE]
  · rintro ⟨k, x, y, z⟩ h
    simp only [mem_coe, mem_filter, mem_Zs] at h
    obtain ⟨⟨hk, hx, hy, hz, hE⟩, rfl⟩ := h
    simp only [X1, mem_coe, mem_filter, mem_Xs]
    refine ⟨⟨⟨by omega, hx, by omega, ?_⟩, hk⟩, by omega⟩
    rw [← hE]; ring
  · rintro ⟨k, a, b⟩ h
    simp only [X1, mem_coe, mem_filter] at h
    obtain ⟨⟨hX, hk⟩, hlt⟩ := h
    obtain ⟨h4, -⟩ := odd_facts hN hX hk
    dsimp only at hlt ⊢
    simp only [Prod.mk.injEq, true_and]
    omega
  · rintro ⟨k, x, y, z⟩ h
    simp only [mem_coe, mem_filter] at h
    obtain ⟨-, hxy⟩ := h
    dsimp only at hxy ⊢
    simp only [Prod.mk.injEq, true_and]
    omega

/-! ## Two swaps on the Zagier set -/

/-- Swap of `y` and `z`. -/
def swyz (t : ℕ × ℕ × ℕ × ℕ) : ℕ × ℕ × ℕ × ℕ := (t.1, t.2.1, t.2.2.2, t.2.2.1)

/-- Swap of `k` and `x`. -/
def swkx (t : ℕ × ℕ × ℕ × ℕ) : ℕ × ℕ × ℕ × ℕ := (t.2.1, t.1, t.2.2.1, t.2.2.2)

lemma swyz_fix (k x y z : ℕ) : swyz (k, x, y, z) = (k, x, y, z) ↔ y = z := by
  simp only [swyz, Prod.mk.injEq, true_and]
  omega

lemma swkx_fix (k x y z : ℕ) : swkx (k, x, y, z) = (k, x, y, z) ↔ k = x := by
  simp only [swkx, Prod.mk.injEq, and_true]
  omega

/-- Points of the Zagier set with `y = z`. -/
def Zyz (N : ℕ) : Finset (ℕ × ℕ × ℕ × ℕ) := (Zs N).filter (fun t => swyz t = t)

lemma Zs_parity_yz : (Zs N).card % 2 = (Zyz N).card % 2 := by
  refine card_mod_two_eq_fixed _ swyz ?_ ?_
  · rintro ⟨k, x, y, z⟩ h
    rw [mem_Zs] at h
    obtain ⟨hk, hx, hy, hz, hE⟩ := h
    show (k, x, z, y) ∈ Zs N
    rw [mem_Zs]
    exact ⟨hk, hx, hz, hy, by rw [← hE]; ring⟩
  · rintro ⟨k, x, y, z⟩ _; rfl

lemma Zyz_parity_kx (hN : N % 8 = 6) :
    (Zyz N).card % 2 = ((Zyz N).filter (fun t => swkx t = t)).card % 2 := by
  refine card_mod_two_eq_fixed _ swkx ?_ ?_
  · rintro ⟨k, x, y, z⟩ h
    simp only [Zyz, mem_filter, swyz_fix] at h
    obtain ⟨hZ, hyz⟩ := h
    have hxo := (Zs_facts hN hZ).1
    rw [mem_Zs] at hZ
    obtain ⟨hk, hx, hy, hz, hE⟩ := hZ
    show (x, k, y, z) ∈ Zyz N
    simp only [Zyz, mem_filter, swyz_fix, mem_Zs]
    exact ⟨⟨hxo, by omega, hy, hz, by rw [← hE]; ring⟩, hyz⟩
  · rintro ⟨k, x, y, z⟩ _; rfl

/-! ## Even `k` -/

lemma even_facts (hN : N % 8 = 6) {k a b : ℕ} (h : (k, a, b) ∈ Xs N) (hk : ¬ k % 2 = 1) :
    (b % 2 = 0 ↔ ¬ a % 2 = 0) := by
  rw [mem_Xs] at h
  obtain ⟨_, ha, hb, hE⟩ := h
  have hk4 := sq_mod_four_even (w := k) (by omega)
  exact mul_mod_four_two (by omega)

lemma card_X0 (hN : N % 8 = 6) :
    (X0 N).card = 2 * ((X0 N).filter (fun t => t.2.2 % 2 = 0)).card := by
  refine card_eq_two_mul _ sw3 _ ?_ ?_ ?_
  · rintro ⟨k, a, b⟩ h
    simp only [X0, mem_filter] at h ⊢
    exact ⟨sw3_mem _ h.1, h.2⟩
  · rintro ⟨k, a, b⟩ _; rfl
  · rintro ⟨k, a, b⟩ h
    simp only [X0, mem_filter] at h
    exact even_facts hN h.1 h.2

/-- Triples of `X0 N` with `b` even. -/
def Xb (N : ℕ) : Finset (ℕ × ℕ × ℕ) := (X0 N).filter (fun t => t.2.2 % 2 = 0)

/-- The involution `(k, a, b) ↦ (k, b / 2, 2 a)`. -/
def gm (t : ℕ × ℕ × ℕ) : ℕ × ℕ × ℕ := (t.1, t.2.2 / 2, 2 * t.2.1)

lemma Xb_parity : (Xb N).card % 2 = ((Xb N).filter (fun t => gm t = t)).card % 2 := by
  refine card_mod_two_eq_fixed _ gm ?_ ?_
  · rintro ⟨k, a, b⟩ h
    simp only [Xb, X0, mem_filter, mem_Xs] at h
    obtain ⟨⟨⟨hk, ha, hb, hE⟩, hko⟩, hbe⟩ := h
    show (k, b / 2, 2 * a) ∈ Xb N
    simp only [Xb, X0, mem_filter, mem_Xs]
    have hb2 : b = 2 * (b / 2) := by omega
    refine ⟨⟨⟨hk, by omega, by omega, ?_⟩, hko⟩, by omega⟩
    have e : k ^ 2 + b / 2 * (2 * a) = k ^ 2 + a * b := by
      conv_rhs => rw [hb2]
      ring
    rw [e, hE]
  · rintro ⟨k, a, b⟩ h
    simp only [Xb, mem_filter] at h
    obtain ⟨-, hbe⟩ := h
    show (k, 2 * a / 2, 2 * (b / 2)) = (k, a, b)
    simp only [Prod.mk.injEq, true_and]
    omega

lemma card_final (hN : N % 8 = 6) :
    ((Zyz N).filter (fun t => swkx t = t)).card = ((Xb N).filter (fun t => gm t = t)).card := by
  refine card_nbij' (fun t => (2 * t.2.2.1, t.1, 2 * t.1))
    (fun t => (t.2.1, t.2.1, t.1 / 2, t.1 / 2)) ?_ ?_ ?_ ?_
  · rintro ⟨k, x, y, z⟩ h
    simp only [Zyz, mem_coe, mem_filter, swyz_fix, swkx_fix, mem_Zs] at h
    obtain ⟨⟨⟨hk, hx, hy, hz, hE⟩, rfl⟩, rfl⟩ := h
    simp only [Xb, X0, mem_coe, mem_filter, mem_Xs]
    refine ⟨⟨⟨⟨by omega, by omega, by omega, ?_⟩, by omega⟩, by omega⟩, ?_⟩
    · rw [← hE]; ring
    · show (2 * y, 2 * k / 2, 2 * k) = (2 * y, k, 2 * k)
      simp only [Prod.mk.injEq, true_and, and_true]
      omega
  · rintro ⟨k, a, b⟩ h
    simp only [Xb, X0, mem_coe, mem_filter] at h
    obtain ⟨⟨⟨hX, hko⟩, hbe⟩, hfix⟩ := h
    have hao := (even_facts hN hX hko).1 hbe
    rw [mem_Xs] at hX
    obtain ⟨hk, ha, hb, hE⟩ := hX
    have hfix' : b / 2 = a ∧ 2 * a = b := by
      simpa only [gm, Prod.mk.injEq, true_and] using hfix
    dsimp only
    simp only [Zyz, mem_coe, mem_filter, swyz_fix, swkx_fix, mem_Zs]
    have hk2 : k = 2 * (k / 2) := by omega
    refine ⟨⟨⟨by omega, ha, by omega, by omega, ?_⟩, trivial⟩, trivial⟩
    have e : a ^ 2 + a ^ 2 + 4 * (k / 2) * (k / 2) = k ^ 2 + a * b := by
      rw [← hfix'.2]
      conv_rhs => rw [hk2]
      ring
    rw [e, hE]
  · rintro ⟨k, x, y, z⟩ h
    simp only [Zyz, mem_coe, mem_filter, swyz_fix, swkx_fix] at h
    obtain ⟨⟨-, rfl⟩, rfl⟩ := h
    show (k, k, 2 * y / 2, 2 * y / 2) = (k, k, y, y)
    simp only [Prod.mk.injEq, true_and]
    omega
  · rintro ⟨k, a, b⟩ h
    simp only [Xb, X0, mem_coe, mem_filter] at h
    obtain ⟨⟨⟨-, hko⟩, hbe⟩, hfix⟩ := h
    have hfix' : b / 2 = a ∧ 2 * a = b := by
      simpa only [gm, Prod.mk.injEq, true_and] using hfix
    show (2 * (k / 2), a, 2 * a) = (k, a, b)
    simp only [Prod.mk.injEq, true_and]
    omega

/-! ## Counting -/

lemma card_Xs_mod (hN : N % 8 = 6) : (Xs N).card % 4 = 0 := by
  have e1 := card_split (N := N)
  have h1 := card_X1 hN
  have h2 := card_X1_lt hN
  have h3 := card_mod_two_eq_fixed (Zs N) zag (zag_mem hN) (zag_zag hN)
  rw [zag_fixed hN] at h3
  have h4 := Zs_parity_yz (N := N)
  have h5 := Zyz_parity_kx hN
  have h6 := card_X0 hN
  have h7 := Xb_parity (N := N)
  have h8 := card_final hN
  change (X0 N).card = 2 * (Xb N).card at h6
  omega

lemma card_Xs_eq (N : ℕ) : (Xs N).card =
    ∑ k ∈ (range N).filter (fun k => 1 ≤ k ∧ k ^ 2 < N), (N - k ^ 2).divisors.card := by
  rw [card_eq_sum_card_fiberwise (f := fun t => t.1)
    (t := (range N).filter (fun k => 1 ≤ k ∧ k ^ 2 < N))]
  · refine sum_congr rfl ?_
    intro k hk
    simp only [mem_filter, mem_range] at hk
    refine card_nbij' (fun t => t.2.1) (fun a => (k, a, (N - k ^ 2) / a)) ?_ ?_ ?_ ?_
    · rintro ⟨k', a, b⟩ h
      simp only [mem_coe, mem_filter, mem_Xs] at h
      obtain ⟨⟨_, ha, hb, hE⟩, rfl⟩ := h
      simp only [mem_coe, Nat.mem_divisors]
      exact ⟨⟨b, by omega⟩, by omega⟩
    · intro a h
      simp only [mem_coe, Nat.mem_divisors] at h
      obtain ⟨hd, hne⟩ := h
      have ha : 0 < a := Nat.pos_of_dvd_of_pos hd (by omega)
      have hmul := Nat.mul_div_cancel' hd
      simp only [mem_coe, mem_filter, mem_Xs]
      refine ⟨⟨by omega, ha, ?_, by omega⟩, trivial⟩
      exact Nat.div_pos (Nat.le_of_dvd (by omega) hd) ha
    · rintro ⟨k', a, b⟩ h
      simp only [mem_coe, mem_filter, mem_Xs] at h
      obtain ⟨⟨_, ha, hb, hE⟩, rfl⟩ := h
      have e : N - k' ^ 2 = a * b := by omega
      show (k', a, (N - k' ^ 2) / a) = (k', a, b)
      rw [e, Nat.mul_div_cancel_left b ha]
    · intro a _; rfl
  · rintro ⟨k, a, b⟩ h
    simp only [mem_coe, mem_Xs] at h
    simp only [mem_coe, mem_filter, mem_range]
    obtain ⟨hk, ha, hb, hE⟩ := h
    have : 0 < a * b := Nat.mul_pos ha hb
    have : k ≤ k ^ 2 := by nlinarith
    omega

end SPD

/-- General form: for every natural number `N` with `N ≡ 6 (mod 8)`,
`∑_{1 ≤ k < √N} σ₀(N - k²) ≡ 0 (mod 4)`. -/
theorem sum_card_divisors_mod_four (N : ℕ) (hN : N % 8 = 6) :
    (∑ k ∈ (range N).filter (fun k : ℕ => 1 ≤ k ∧ (k : ℝ) < Real.sqrt (N : ℝ)),
      (N - k ^ 2).divisors.card) ≡ 0 [MOD 4] := by
  have hfil : (range N).filter (fun k : ℕ => 1 ≤ k ∧ (k : ℝ) < Real.sqrt (N : ℝ)) =
      (range N).filter (fun k => 1 ≤ k ∧ k ^ 2 < N) := by
    refine filter_congr (fun k _ => ?_)
    rw [Real.lt_sqrt (Nat.cast_nonneg k)]
    norm_cast
  rw [hfil, ← SPD.card_Xs_eq]
  exact SPD.card_Xs_mod hN

/-- Conjecture 7 of arXiv:2604.25394: for `N = 16n + 6`,
`∑_{1 ≤ k < √N} σ₀(N - k²) ≡ 0 (mod 4)`. -/
theorem conjecture_7 (n : ℕ) :
    (∑ k ∈ (range (16 * n + 6)).filter
        (fun k : ℕ => 1 ≤ k ∧ (k : ℝ) < Real.sqrt ((16 * n + 6 : ℕ) : ℝ)),
      (16 * n + 6 - k ^ 2).divisors.card) ≡ 0 [MOD 4] :=
  sum_card_divisors_mod_four (16 * n + 6) (by omega)

#print axioms sum_card_divisors_mod_four
#print axioms conjecture_7
