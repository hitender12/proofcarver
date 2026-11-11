# ARCHITECTURE.md — proofcarver

## Design

```
spec (pre/postconditions + candidate library)
        │
        ▼
┌──────────────┐    counterexample     ┌──────────────┐
│   checker    │ ── failure class ──▶ │  repair loop │
│ (property    │                       │ (pick next   │
│  testing)    │ ◀── next candidate ── │  candidate)  │
└──────────────┘                       └──────────────┘
        │                                      │
        ▼                                      ▼
   PASS: candidate                     FAIL: failure report
   accepted as "checked"               (library exhausted / cap hit)
```

The loop is deliberately generator-agnostic. Today the "generator" is
an ordered candidate library per spec. Tomorrow it can be an LLM that
proposes candidates, with the same checker and the same loop. The
contract between generator and loop is just: *candidates have labels
and a `fixes` tag naming the failure classes they address*.

## Modules

| Module | Responsibility |
|---|---|
| `spec.py` | `Spec`, `Candidate`, `CheckResult`, `Counterexample` data model. A spec is a function name, an input generator, a precondition, a postcondition returning a failure class (or `None`), and a candidate library. |
| `specs.py` | Demo specs: sort, binary search, dedup, unfixable. Each candidate library is ordered broken → partial → correct, with `fixes` tags. |
| `checker.py` | Compiles a candidate with `exec` in an isolated namespace, runs seeded random inputs, returns up to 5 counterexamples with failure classes. Exceptions in candidate code are counterexamples of class `exception`. |
| `repair.py` | `run_loop`: check → on failure, prefer an untried candidate whose `fixes` intersect the observed failure classes, else the next untried candidate. Caps iterations; reports exhaustion honestly. |
| `lean_adapter.py` | Emits Lean 4 theorem skeletons (`sorry` included, honestly). `verify_with_lean` raises `NotImplementedError`. |
| `__main__.py` | CLI: `--spec`, `--cases`, `--max-iter`, `--seed`. |

## Key decisions

- **Property testing, not proof, for the loop.** Counterexamples are
  cheap and give the repair loop something actionable. Formal proof
  is the production backend, kept behind a separate adapter so the
  loop never overclaims.
- **Failure classes as the repair signal.** A bare "it failed" is not
  enough to choose a repair. Labelling *how* it failed
  (`unsorted` vs `not-permutation`) is what makes the loop guided
  rather than random search.
- **Deterministic seeds.** Same seed → same inputs → same loop trace.
  Every reported result is reproducible.
- **No LLM dependency.** The core runs on the standard library so the
  mechanism can be tested and audited without an API key. An LLM
  generator is a drop-in replacement for the candidate library.

## Security note

Candidates are executed with `exec`. Candidates in this repo are local,
reviewed code. A future LLM-backed generator must sandbox execution
(subprocess, resource limits, no network) before running untrusted
generated code.

## Roadmap

1. LLM candidate generator behind the same `Candidate` contract.
2. Lean 4 backend: discharge `sorry` with the real toolchain; feed
   proof errors back as failure classes.
3. Richer spec language: dicts, strings, higher-order functions.
4. Counterexample minimisation (delta debugging) so repairs get the
   smallest failing input.
