#!/usr/bin/env python3
"""Exhaust the C18 quotient system for signed (36,29,4) difference sets.

Fabian Arevalo observed during his independent review of version 1.0 that
this quotient system is empty.  The implementation here is local and uses
only the Python standard library.  It enumerates the complete C9 and C2
marginal systems and then every compatible refinement to C18, without any
orbit or symmetry reduction.

An empty C18 quotient excludes a signed (36,29,4) difference set in every
abelian group of order 36 admitting such a quotient, in particular C36 and
C2 x C18.
"""

from __future__ import annotations

import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "runs" / "v36_29_4_c18_quotient_exhaustion.json"
PARAMETERS = {"v": 36, "k": 29, "lambda": 4, "coefficient_sum": 13}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cyclic_correlation(vector: tuple[int, ...]) -> tuple[int, ...]:
    """Return every periodic autocorrelation using exact integer arithmetic."""

    n = len(vector)
    return tuple(
        sum(vector[index] * vector[(index - shift) % n] for index in range(n))
        for shift in range(n)
    )


def enumerate_cyclic_system(
    order: int,
    cell_bound: int,
    target_sum: int,
    peak: int,
    off_peak: int,
) -> tuple[int, list[tuple[int, ...]]]:
    """Enumerate a complete bounded cyclic quotient system.

    The depth-first search applies only necessary sum and norm bounds.  Every
    terminal vector with the requested sum and norm is checked against every
    cyclic shift.
    """

    vector = [0] * order
    sum_norm_candidates = 0
    solutions: list[tuple[int, ...]] = []

    def visit(index: int, remaining_sum: int, remaining_norm: int) -> None:
        nonlocal sum_norm_candidates
        if index == order:
            if remaining_sum == 0 and remaining_norm == 0:
                sum_norm_candidates += 1
                candidate = tuple(vector)
                if cyclic_correlation(candidate) == (peak,) + (off_peak,) * (order - 1):
                    solutions.append(candidate)
            return

        remaining_cells = order - index - 1
        for value in range(-cell_bound, cell_bound + 1):
            next_sum = remaining_sum - value
            next_norm = remaining_norm - value * value
            if next_norm < 0:
                continue
            if abs(next_sum) > remaining_cells * cell_bound:
                continue
            if next_norm > remaining_cells * cell_bound * cell_bound:
                continue
            if remaining_cells == 0:
                if next_sum != 0 or next_norm != 0:
                    continue
            elif next_sum * next_sum > next_norm * remaining_cells:
                continue
            vector[index] = value
            visit(index + 1, next_sum, next_norm)

        vector[index] = 0

    visit(0, target_sum, peak)
    return sum_norm_candidates, solutions


def refine_to_c18(
    c9_solutions: list[tuple[int, ...]],
    c2_solutions: list[tuple[int, ...]],
) -> tuple[int, int, list[tuple[int, ...]]]:
    """Enumerate all C18 vectors having the supplied C9 and C2 marginals."""

    splits = {
        total: tuple(
            pair
            for pair in product(range(-2, 3), repeat=2)
            if sum(pair) == total
        )
        for total in range(-4, 5)
    }
    marginal_refinements = 0
    sum_norm_candidates = 0
    solutions: list[tuple[int, ...]] = []

    for c9 in c9_solutions:
        for c2 in c2_solutions:
            chosen: list[tuple[int, int]] = []

            def visit(index: int, parity_sums: tuple[int, int], norm: int) -> None:
                nonlocal marginal_refinements, sum_norm_candidates
                if index == 9:
                    if parity_sums != c2:
                        return
                    marginal_refinements += 1
                    if norm != 33:
                        return
                    sum_norm_candidates += 1
                    candidate = tuple(pair[0] for pair in chosen) + tuple(
                        pair[1] for pair in chosen
                    )
                    if cyclic_correlation(candidate) == (33,) + (8,) * 17:
                        solutions.append(candidate)
                    return

                remaining = 9 - index - 1
                for first, second in splits[c9[index]]:
                    next_sums = list(parity_sums)
                    next_sums[index % 2] += first
                    next_sums[(index + 9) % 2] += second
                    if any(
                        abs(c2[parity] - next_sums[parity]) > 2 * remaining
                        for parity in range(2)
                    ):
                        continue
                    next_norm = norm + first * first + second * second
                    if next_norm > 33:
                        continue
                    chosen.append((first, second))
                    visit(index + 1, (next_sums[0], next_sums[1]), next_norm)
                    chosen.pop()

            visit(0, (0, 0), 0)

    return marginal_refinements, sum_norm_candidates, solutions


def main() -> None:
    started = datetime.now(timezone.utc)
    timer = time.perf_counter()

    c9_sum_norm, c9_solutions = enumerate_cyclic_system(
        order=9,
        cell_bound=4,
        target_sum=13,
        peak=41,
        off_peak=16,
    )
    c2_sum_norm, c2_solutions = enumerate_cyclic_system(
        order=2,
        cell_bound=18,
        target_sum=13,
        peak=97,
        off_peak=72,
    )
    refinements, c18_sum_norm, c18_solutions = refine_to_c18(
        c9_solutions,
        c2_solutions,
    )

    assert len(c9_solutions) == 9
    assert set(c2_solutions) == {(4, 9), (9, 4)}
    assert not c18_solutions

    document = {
        "schema": "v36-29-4-c18-quotient-exhaustion-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": PARAMETERS,
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
        "instances": [
            {
                "instance": "SDS(36,29,4,[36])",
                "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
                "reason": "The necessary C18 quotient system is empty.",
            },
            {
                "instance": "SDS(36,29,4,[2,18])",
                "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
                "reason": "The necessary C18 quotient system is empty.",
            },
        ],
        "systems": {
            "C9_kernel_order_4": {
                "cell_bound": 4,
                "sum": 13,
                "peak": 41,
                "off_peak": 16,
                "sum_norm_candidates": c9_sum_norm,
                "solutions": len(c9_solutions),
                "solution_vectors": c9_solutions,
            },
            "C2_kernel_order_18": {
                "cell_bound": 18,
                "sum": 13,
                "peak": 97,
                "off_peak": 72,
                "sum_norm_candidates": c2_sum_norm,
                "solutions": len(c2_solutions),
                "solution_vectors": c2_solutions,
            },
            "C18_kernel_order_2": {
                "cell_bound": 2,
                "sum": 13,
                "peak": 33,
                "off_peak": 8,
                "marginal_compatible_refinements": refinements,
                "sum_norm_candidates": c18_sum_norm,
                "solutions": len(c18_solutions),
            },
        },
        "mathematical_argument": [
            "Projection through a kernel of order m sends an SDS to bounded quotient cell sums with peak k+(m-1)lambda and off-peak m lambda.",
            "Every bounded C9 quotient vector and every C2 quotient vector satisfying the exact sum, norm, and full correlation equations is enumerated without symmetry reduction.",
            "Every pair splitting in [-2,2]^2 compatible with both marginals is enumerated, then every resulting C18 vector of norm 33 is checked at all 18 cyclic shifts.",
            "The C18 quotient system has no solution, excluding both C36 and C2 x C18.",
        ],
        "provenance": {
            "observation": "Suggested by Fabian Arevalo in his independent review of project version 1.0.",
            "review_repository": "https://github.com/farev/Matematica/tree/main/conjectures/signed-difference-sets/masselot-review",
            "review_commit_checked": "05f18c4f9db8d3cb073f78fb486dce7c033a6b69",
            "implementation": "Independent local standard-library implementation; no external review code imported.",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "runtime_seconds": time.perf_counter() - timer,
        "started_at_utc": started.isoformat(),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "c9_solutions": len(c9_solutions),
                "c18_sum_norm_candidates": c18_sum_norm,
                "c18_solutions": len(c18_solutions),
                "runtime_seconds": document["runtime_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
