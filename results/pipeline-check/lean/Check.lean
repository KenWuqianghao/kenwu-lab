import Mathlib

theorem primes_below_100 : (Finset.filter Nat.Prime (Finset.range 100)).card = 25 := by
  decide

#print axioms primes_below_100
