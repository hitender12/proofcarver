"""Demo: run the repair loop on every spec and show the Lean skeleton."""

from proofcarver import ALL_SPECS, run_loop
from proofcarver.lean_adapter import emit_lean_theorem


def main() -> None:
    print("proofcarver demo: counterexample-guided repair")
    print("=" * 60)
    for name in ("sort", "binary_search", "dedup"):
        spec = ALL_SPECS[name]()
        result = run_loop(spec, n_cases=200, seed=0)
        first = result.history[0]
        print(
            f"\n{name}: first attempt '{first.candidate_label}' "
            f"failed with {first.failure_classes}; "
            f"loop {'PASSED' if result.success else 'FAILED'} "
            f"after {result.iterations} iteration(s)."
        )
    print("\nUnfixable spec (no correct candidate exists):")
    result = run_loop(ALL_SPECS["unfixable"](), n_cases=100, seed=0)
    print(f"  success={result.success} | {result.reason}")
    print("\nLean 4 skeleton for the sort spec (next-step backend):")
    print("-" * 60)
    spec = ALL_SPECS["sort"]()
    print(emit_lean_theorem(spec, spec.candidates[-1].source))


if __name__ == "__main__":
    main()
