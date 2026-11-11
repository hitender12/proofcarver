"""Spec language for proofcarver.

A Spec describes a function by its pre/postconditions, plus an ordered
library of candidate implementations (broken first, correct last).  The
checker tests a candidate against the spec with generated inputs; the
repair loop uses counterexamples to pick the next candidate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass
class Candidate:
    """One implementation of a spec, as source code.

    ``fixes`` names the failure classes this candidate is expected to
    repair, e.g. ("unsorted",).  The repair loop uses it to choose the
    next candidate from the counterexample's failure class.
    """

    label: str
    source: str
    fixes: tuple = ()


@dataclass
class Counterexample:
    args: tuple
    output: object
    error: Optional[str]
    failure_class: str


@dataclass
class CheckResult:
    passed: bool
    cases_run: int
    counterexamples: List[Counterexample]
    failure_classes: List[str]


@dataclass
class Spec:
    name: str
    description: str
    func_name: str
    # input_gen(rng) -> tuple of arguments for the function.
    input_gen: Callable
    # precondition(args) -> bool; generated inputs that fail it are skipped.
    precondition: Callable
    # postcondition(args, output) -> failure class string, or None if it holds.
    postcondition: Callable
    candidates: List[Candidate] = field(default_factory=list)
