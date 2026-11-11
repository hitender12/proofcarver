# proofcarver

**Specs to verified code, with a repair loop.**

LLM codegen is fast but untrustworthy; formal verification is trustworthy
but slow. proofcarver closes the gap with a counterexample-guided loop:
generate code from a spec, check it against the spec, and feed failures
back as targeted repairs until the check passes — or the spec is shown
contradictory.

## The novel idea

Most "verified codegen" either trusts the generator or demands a human
written proof. proofcarver treats verification as a *search problem*:
the checker produces counterexamples, each labelled with a failure
class, and the repair loop selects the next candidate whose repair
addresses exactly that failure class. The loop is the mechanism, not the
model — it works with template candidates today and with an LLM
generator or a Lean 4 prover tomorrow, without changing the loop.

## What works today (honest status)

- A small spec language: pre/postconditions over list/int functions.
- A property-based checker: seeded random testing that returns labelled
  counterexamples (e.g. `unsorted`, `wrong-index`, `duplicates-remain`).
- A repair loop that walks a candidate library using failure classes,
  with an iteration cap and a clean failure report when no candidate
  can satisfy the spec.
- Demo specs: **sorting**, **binary search**, **list dedup** — each
  starts from a deliberately broken first attempt and is repaired to
  passing. Plus an **unfixable** spec that demonstrates graceful
  failure reporting.
- A Lean 4 adapter that emits theorem skeletons. **This is a next
  step, not implemented**: the skeletons end in `sorry`, and
  `verify_with_lean()` raises `NotImplementedError` rather than
  pretending to prove anything.

What this is *not*: a formal proof. The checker is property-based
testing. It finds bugs fast; it does not prove absence of bugs. The
Lean backend is the path to real proofs (see `ARCHITECTURE.md`).

## Quickstart

Requires Python 3.10+ and nothing else (standard library only).

```bash
# Run the repair loop on every spec
python -m proofcarver --spec all

# Just sorting, with more test cases
python -m proofcarver --spec sort --cases 500

# Runnable demo (loops + Lean skeleton)
python demo.py

# Tests
python -m unittest discover -s tests -v
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md). Core modules:

- `proofcarver/spec.py` — Spec and Candidate data model.
- `proofcarver/specs.py` — demo specs and their candidate libraries.
- `proofcarver/checker.py` — property-based checker, returns
  counterexamples with failure classes.
- `proofcarver/repair.py` — the counterexample-guided repair loop.
- `proofcarver/lean_adapter.py` — Lean 4 skeleton emitter (next step).

## Evaluation plan

1. **Repair rate**: fraction of specs the loop repairs, and iterations
   needed (target: every fixable demo spec in ≤ 3 iterations).
2. **Checker power**: mutation testing — the checker must catch
   seeded bugs (off-by-one, dropped elements, wrong return) with
   high probability at 200 cases.
3. **Proof backend** (future): Lean success rate on the same specs,
   and repair iterations saved by using proof failures instead of
   test counterexamples.
