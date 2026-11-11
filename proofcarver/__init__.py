"""proofcarver: specs to verified code, with a repair loop."""

from .repair import LoopResult, LoopStep, run_loop
from .specs import ALL_SPECS, binary_search_spec, dedup_spec, sort_spec, unfixable_spec
from .spec import Candidate, CheckResult, Counterexample, Spec
from .checker import check

__all__ = [
    "ALL_SPECS",
    "Candidate",
    "CheckResult",
    "Counterexample",
    "LoopResult",
    "LoopStep",
    "Spec",
    "binary_search_spec",
    "check",
    "dedup_spec",
    "run_loop",
    "sort_spec",
    "unfixable_spec",
]

__version__ = "0.1.0"
