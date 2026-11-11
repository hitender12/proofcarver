"""CLI: run the repair loop for one spec, or all of them.

Usage:
    python -m proofcarver --spec sort
    python -m proofcarver --spec all --cases 500
"""

from __future__ import annotations

import argparse

from .repair import run_loop
from .specs import ALL_SPECS


def _report(spec_name: str, result) -> None:
    status = "PASS" if result.success else "FAIL"
    print(f"\n[{spec_name}] {status} after {result.iterations} iteration(s): {result.reason}")
    for step in result.history:
        mark = "ok " if step.passed else "FAIL"
        detail = ""
        if not step.passed and step.first_counterexample is not None:
            ce = step.first_counterexample
            detail = f" | e.g. args={ce.args} -> {ce.output!r} ({ce.failure_class})"
        print(
            f"  iter {step.iteration}: {mark} {step.candidate_label} "
            f"failures={step.failure_classes} counterexamples={step.n_counterexamples}{detail}"
        )
    if result.success and result.candidate is not None:
        print("  final code:")
        for line in result.candidate.source.rstrip().splitlines():
            print(f"    {line}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="proofcarver")
    parser.add_argument("--spec", choices=list(ALL_SPECS) + ["all"], default="all")
    parser.add_argument("--cases", type=int, default=200)
    parser.add_argument("--max-iter", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    names = list(ALL_SPECS) if args.spec == "all" else [args.spec]
    overall = True
    for name in names:
        spec = ALL_SPECS[name]()
        result = run_loop(spec, max_iter=args.max_iter, n_cases=args.cases, seed=args.seed)
        _report(name, result)
        # The "unfixable" demo spec is *expected* to fail; it must not
        # flip the exit code when running --spec all.
        if name != "unfixable":
            overall = overall and result.success
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
