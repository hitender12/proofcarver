"""Property-based checker: runs a candidate against a spec on generated inputs.

A candidate passes only if the postcondition holds on every generated
input.  Failures are returned as counterexamples with a failure class the
repair loop can act on.  This is a *testing* check, not a formal proof:
see lean_adapter.py for the production proof backend (next step).
"""

from __future__ import annotations

import random

from .spec import Candidate, CheckResult, Counterexample, Spec

MAX_COUNTEREXAMPLES = 5


def load_candidate(candidate: Candidate, func_name: str):
    """Compile a candidate's source and return the named function."""
    namespace: dict = {}
    exec(candidate.source, namespace)  # noqa: S102 - candidates are local, reviewed code
    return namespace[func_name]


def check(spec: Spec, candidate: Candidate, n_cases: int = 200, seed: int = 0) -> CheckResult:
    rng = random.Random(seed)
    fn = load_candidate(candidate, spec.func_name)
    counterexamples: list[Counterexample] = []
    failure_classes: list[str] = []
    cases_run = 0
    for _ in range(n_cases):
        args = spec.input_gen(rng)
        if not spec.precondition(args):
            continue
        cases_run += 1
        try:
            out = fn(*args)
            error = None
        except Exception as exc:  # noqa: BLE001 - any candidate crash is a counterexample
            out, error = None, f"{type(exc).__name__}: {exc}"
        if error is not None:
            failure_class = "exception"
        else:
            failure_class = spec.postcondition(args, out)
        if failure_class is not None:
            counterexamples.append(
                Counterexample(args=args, output=out, error=error, failure_class=failure_class)
            )
            if failure_class not in failure_classes:
                failure_classes.append(failure_class)
            if len(counterexamples) >= MAX_COUNTEREXAMPLES:
                break
    return CheckResult(
        passed=not counterexamples,
        cases_run=cases_run,
        counterexamples=counterexamples,
        failure_classes=failure_classes,
    )
