"""Tests for proofcarver: the loop must fix deliberately broken first attempts."""

import unittest

from proofcarver import ALL_SPECS, check, run_loop
from proofcarver.lean_adapter import emit_lean_theorem, verify_with_lean


class TestRepairLoop(unittest.TestCase):
    def test_sort_loop_fixes_broken_first_attempt(self):
        spec = ALL_SPECS["sort"]()
        result = run_loop(spec, n_cases=200, seed=0)
        self.assertFalse(result.history[0].passed, "first attempt should fail")
        self.assertIn("unsorted", result.history[0].failure_classes)
        self.assertTrue(result.success, result.reason)
        self.assertGreaterEqual(result.iterations, 2)
        self.assertEqual(result.candidate.label, "correct")

    def test_binary_search_loop_fixes_broken_first_attempt(self):
        spec = ALL_SPECS["binary_search"]()
        result = run_loop(spec, n_cases=300, seed=1)
        self.assertFalse(result.history[0].passed)
        self.assertIn("wrong-index", result.history[0].failure_classes)
        self.assertTrue(result.success, result.reason)
        self.assertGreaterEqual(result.iterations, 2)
        self.assertEqual(result.candidate.label, "correct")

    def test_dedup_loop_fixes_broken_first_attempt(self):
        spec = ALL_SPECS["dedup"]()
        result = run_loop(spec, n_cases=200, seed=2)
        self.assertFalse(result.history[0].passed)
        self.assertIn("duplicates-remain", result.history[0].failure_classes)
        self.assertTrue(result.success, result.reason)
        self.assertGreaterEqual(result.iterations, 2)
        self.assertEqual(result.candidate.label, "correct")

    def test_checker_finds_counterexample(self):
        spec = ALL_SPECS["sort"]()
        broken = spec.candidates[0]
        result = check(spec, broken, n_cases=200, seed=0)
        self.assertFalse(result.passed)
        self.assertIn("unsorted", result.failure_classes)
        self.assertTrue(result.counterexamples)
        ce = result.counterexamples[0]
        self.assertNotEqual(ce.args[0], sorted(ce.args[0]))

    def test_checker_passes_correct_candidate(self):
        for name in ("sort", "binary_search", "dedup"):
            spec = ALL_SPECS[name]()
            result = check(spec, spec.candidates[-1], n_cases=300, seed=3)
            self.assertTrue(result.passed, f"{name} correct candidate should pass")

    def test_unfixable_spec_reports_failure_cleanly(self):
        spec = ALL_SPECS["unfixable"]()
        result = run_loop(spec, n_cases=100, seed=0)
        self.assertFalse(result.success)
        self.assertIn("exhausted", result.reason)
        self.assertTrue(result.history)

    def test_max_iter_cap_is_respected(self):
        spec = ALL_SPECS["unfixable"]()
        result = run_loop(spec, max_iter=1, n_cases=50, seed=0)
        self.assertFalse(result.success)
        self.assertEqual(result.iterations, 1)


class TestLeanAdapter(unittest.TestCase):
    def test_emit_lean_skeleton_contains_theorems_and_sorry(self):
        spec = ALL_SPECS["sort"]()
        out = emit_lean_theorem(spec, spec.candidates[-1].source)
        self.assertIn("theorem sort_list_sorted", out)
        self.assertIn("theorem sort_list_perm", out)
        self.assertIn("sorry", out, "skeleton must not pretend to be a proof")

    def test_verify_with_lean_refuses_to_pretend(self):
        spec = ALL_SPECS["sort"]()
        with self.assertRaises(NotImplementedError):
            verify_with_lean(spec, spec.candidates[-1].source)


if __name__ == "__main__":
    unittest.main()
