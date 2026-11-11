"""Counterexample-guided repair loop.

Flow: check the current candidate -> if it passes, done; otherwise take
the failure classes from the counterexamples and pick the next untried
candidate whose ``fixes`` cover one of them.  If no candidate matches,
fall back to the next untried candidate in order.  The loop stops with a
clear failure report when the candidate library is exhausted or the
iteration cap is hit, so a contradictory spec can never hang the loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .checker import check
from .spec import Candidate, CheckResult, Spec


@dataclass
class LoopStep:
    iteration: int
    candidate_label: str
    passed: bool
    failure_classes: list
    n_counterexamples: int
    first_counterexample: object = None


@dataclass
class LoopResult:
    success: bool
    candidate: Candidate | None
    iterations: int
    history: list = field(default_factory=list)
    reason: str = ""


def run_loop(spec: Spec, max_iter: int = 10, n_cases: int = 200, seed: int = 0) -> LoopResult:
    history: list[LoopStep] = []
    tried: set[int] = set()
    idx = 0
    for iteration in range(1, max_iter + 1):
        candidate = spec.candidates[idx]
        tried.add(idx)
        result: CheckResult = check(spec, candidate, n_cases=n_cases, seed=seed)
        history.append(
            LoopStep(
                iteration=iteration,
                candidate_label=candidate.label,
                passed=result.passed,
                failure_classes=result.failure_classes,
                n_counterexamples=len(result.counterexamples),
                first_counterexample=result.counterexamples[0] if result.counterexamples else None,
            )
        )
        if result.passed:
            return LoopResult(
                success=True,
                candidate=candidate,
                iterations=iteration,
                history=history,
                reason=f"all {result.cases_run} property checks passed",
            )
        # Prefer a candidate whose fixes cover an observed failure class.
        failed = set(result.failure_classes)
        nxt = None
        for j, cand in enumerate(spec.candidates):
            if j not in tried and set(cand.fixes) & failed:
                nxt = j
                break
        if nxt is None:
            for j, cand in enumerate(spec.candidates):
                if j not in tried:
                    nxt = j
                    break
        if nxt is None:
            return LoopResult(
                success=False,
                candidate=candidate,
                iterations=iteration,
                history=history,
                reason=(
                    "candidate library exhausted; remaining failures: "
                    + ", ".join(result.failure_classes)
                    + ". The spec may be contradictory or the repair "
                    "library may be missing a fix."
                ),
            )
        idx = nxt
    return LoopResult(
        success=False,
        candidate=spec.candidates[idx],
        iterations=max_iter,
        history=history,
        reason=f"max iterations ({max_iter}) reached without a passing candidate",
    )
