/-- The 15 × 16 matrix `U` (Sloane's Hadamard matrix Had.16.3 without its all-ones row 0). -/
def Umat : Matrix (Fin 15) (Fin 16) ℤ := fun i j => if (Urows.getD i 0).testBit j then 1 else -1

/-- Entry `i` of the dual vector with code `code`: base-5 digit `i`, minus 2. -/
def yOf (code i : ℕ) : ℤ := ((code / 5 ^ i % 5 : ℕ) : ℤ) - 2

def l1 (code : ℕ) : ℤ := ((List.range 15).map fun i => |yOf code i|).sum

def dotc (code c : ℕ) : ℤ :=
  ((List.range 15).map fun i => yOf code i * (if (Urows.getD i 0).testBit c then 1 else -1)).sum

/-- `p = mask + 2^16 * code`. The dual vector `y` of `code` is nonzero, and
`7 (Uᵀ y)_c ≥ 3 ‖y‖₁` for every column `c` in `mask`. -/
def valid (p : ℕ) : Bool :=
  decide (0 < l1 (p / 65536)) && (List.range 16).all fun c =>
    !p.testBit c || decide (3 * l1 (p / 65536) ≤ 7 * dotc (p / 65536) c)

def covers (p a b c d e f : ℕ) : Bool :=
  p.testBit a && p.testBit b && p.testBit c && p.testBit d && p.testBit e && p.testBit f

lemma cover_of {l : List ℕ} {Q : ℕ → Bool} (h1 : l.all valid = true) (h2 : l.any Q = true) :
    ∃ p, valid p = true ∧ Q p = true := by
  rw [List.all_eq_true] at h1
  obtain ⟨p, hp, hq⟩ := List.any_eq_true.mp h2
  exact ⟨p, h1 p hp, hq⟩

