-- Example of what the production Lean 4 backend would emit for the sort spec.
-- STATUS: illustrative skeleton only. Every theorem ends in `sorry` and
-- must be discharged with the Lean 4 toolchain before this counts as a
-- verified artifact. See proofcarver/lean_adapter.py.

-- Reference implementation (Python):
--   def sort_list(xs):
--       return sorted(xs)

def sortListImpl : List Int → List Int := sorry

theorem sort_list_sorted (xs : List Int) : (sortListImpl xs).Sorted (· ≤ ·) := by
  sorry

theorem sort_list_perm (xs : List Int) : (sortListImpl xs) ~ xs := by
  sorry
