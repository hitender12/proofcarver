"""Demo specs: sorting, binary search, list dedup, plus an unfixable one.

Each spec ships an ordered candidate library: a deliberately broken first
attempt, one or two partially-fixed attempts, and a correct one.  The
repair loop must walk the library using counterexample failure classes.
"""

from __future__ import annotations

import random

from .spec import Candidate, Spec


# ---------------------------------------------------------------- sorting
def _sort_inputs(rng: random.Random):
    n = rng.randrange(0, 13)
    return ([rng.randrange(-20, 21) for _ in range(n)],)


def _sort_post(args, out):
    xs, = args
    if not isinstance(out, list):
        return "not-a-list"
    if out != sorted(out):
        return "unsorted"
    if sorted(out) != sorted(xs):
        return "not-permutation"
    return None


def sort_spec() -> Spec:
    return Spec(
        name="sort",
        description="Sort a list of ints ascending, preserving all elements.",
        func_name="sort_list",
        input_gen=_sort_inputs,
        precondition=lambda args: True,
        postcondition=_sort_post,
        candidates=[
            Candidate(
                label="identity (broken)",
                source="def sort_list(xs):\n    return list(xs)\n",
                fixes=(),
            ),
            Candidate(
                label="one-pass bubble (partial)",
                source=(
                    "def sort_list(xs):\n"
                    "    xs = list(xs)\n"
                    "    for i in range(len(xs) - 1):\n"
                    "        if xs[i] > xs[i + 1]:\n"
                    "            xs[i], xs[i + 1] = xs[i + 1], xs[i]\n"
                    "    return xs\n"
                ),
                fixes=("unsorted",),
            ),
            Candidate(
                label="correct",
                source="def sort_list(xs):\n    return sorted(xs)\n",
                fixes=("unsorted", "not-permutation"),
            ),
        ],
    )


# ----------------------------------------------------------- binary search
def _bs_inputs(rng: random.Random):
    xs = sorted(rng.sample(range(0, 51), rng.randrange(0, 16)))
    # Half the time search for a present element, half for an absent one.
    if xs and rng.random() < 0.5:
        x = rng.choice(xs)
    else:
        x = rng.randrange(0, 51)
    return (xs, x)


def _bs_post(args, out):
    xs, x = args
    if not isinstance(out, int):
        return "not-an-int"
    if x in xs:
        if out != xs.index(x):
            return "wrong-index"
    else:
        if out != -1:
            return "wrong-absent"
    return None


def binary_search_spec() -> Spec:
    return Spec(
        name="binary_search",
        description="Return the index of x in a sorted unique list, or -1.",
        func_name="binary_search",
        input_gen=_bs_inputs,
        precondition=lambda args: True,
        postcondition=_bs_post,
        candidates=[
            Candidate(
                label="off-by-one linear scan (broken)",
                source=(
                    "def binary_search(xs, x):\n"
                    "    for i, v in enumerate(xs):\n"
                    "        if v == x:\n"
                    "            return i + 1\n"
                    "    return -1\n"
                ),
                fixes=(),
            ),
            Candidate(
                label="binary search, returns insertion point (partial)",
                source=(
                    "def binary_search(xs, x):\n"
                    "    lo, hi = 0, len(xs) - 1\n"
                    "    while lo <= hi:\n"
                    "        mid = (lo + hi) // 2\n"
                    "        if xs[mid] == x:\n"
                    "            return mid\n"
                    "        elif xs[mid] < x:\n"
                    "            lo = mid + 1\n"
                    "        else:\n"
                    "            hi = mid - 1\n"
                    "    return lo\n"
                ),
                fixes=("wrong-index",),
            ),
            Candidate(
                label="correct",
                source=(
                    "def binary_search(xs, x):\n"
                    "    lo, hi = 0, len(xs) - 1\n"
                    "    while lo <= hi:\n"
                    "        mid = (lo + hi) // 2\n"
                    "        if xs[mid] == x:\n"
                    "            return mid\n"
                    "        elif xs[mid] < x:\n"
                    "            lo = mid + 1\n"
                    "        else:\n"
                    "            hi = mid - 1\n"
                    "    return -1\n"
                ),
                fixes=("wrong-index", "wrong-absent"),
            ),
        ],
    )


# ------------------------------------------------------------------- dedup
def _dedup_inputs(rng: random.Random):
    n = rng.randrange(0, 13)
    return ([rng.randrange(0, 6) for _ in range(n)],)


def _dedup_post(args, out):
    xs, = args
    if not isinstance(out, list):
        return "not-a-list"
    seen = []
    for v in xs:
        if v not in seen:
            seen.append(v)
    if out != seen:
        if len(out) != len(set(out)):
            return "duplicates-remain"
        if set(out) != set(xs):
            return "missing-elements"
        return "order-changed"
    return None


def dedup_spec() -> Spec:
    return Spec(
        name="dedup",
        description="Remove duplicates, keeping the first occurrence order.",
        func_name="dedup",
        input_gen=_dedup_inputs,
        precondition=lambda args: True,
        postcondition=_dedup_post,
        candidates=[
            Candidate(
                label="identity (broken)",
                source="def dedup(xs):\n    return list(xs)\n",
                fixes=(),
            ),
            Candidate(
                label="dedups but drops first element (partial)",
                source=(
                    "def dedup(xs):\n"
                    "    out = []\n"
                    "    for v in xs:\n"
                    "        if v not in out:\n"
                    "            out.append(v)\n"
                    "    return out[1:] if out else out\n"
                ),
                fixes=("duplicates-remain",),
            ),
            Candidate(
                label="correct",
                source=(
                    "def dedup(xs):\n"
                    "    out = []\n"
                    "    for v in xs:\n"
                    "        if v not in out:\n"
                    "            out.append(v)\n"
                    "    return out\n"
                ),
                fixes=("duplicates-remain", "missing-elements", "order-changed"),
            ),
        ],
    )


# --------------------------------------------------------------- unfixable
def _unfixable_inputs(rng: random.Random):
    return ([rng.randrange(0, 5) for _ in range(rng.randrange(0, 6))],)


def unfixable_spec() -> Spec:
    """A spec whose candidate library contains no correct implementation.

    Used to test that the loop reports failure cleanly instead of looping
    forever or crashing.  The spec asks for a sorted list of *distinct*
    elements, but the only candidate returns the input unchanged.
    """
    return Spec(
        name="unfixable",
        description="Sort and dedup (no correct candidate exists).",
        func_name="sort_dedup",
        input_gen=_unfixable_inputs,
        precondition=lambda args: True,
        postcondition=lambda args, out: (
            None
            if isinstance(out, list)
            and out == sorted(out)
            and len(out) == len(set(out))
            and sorted(out) == sorted(set(args[0]))
            else "not-sorted-distinct"
        ),
        candidates=[
            Candidate(
                label="identity (broken, only candidate)",
                source="def sort_dedup(xs):\n    return list(xs)\n",
                fixes=(),
            ),
        ],
    )


ALL_SPECS = {
    "sort": sort_spec,
    "binary_search": binary_search_spec,
    "dedup": dedup_spec,
    "unfixable": unfixable_spec,
}
