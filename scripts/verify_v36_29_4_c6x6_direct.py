#!/usr/bin/env python3
"""Solver-free exhaustive proof for SDS(36,29,4,C6 x C6).

The meet-in-the-middle strategy was proposed and first implemented by Fabian
Arevalo in his independent review of project version 1.0.  This local version
is adapted with attribution under his MIT-licensed code release.  It rebuilds
both complete marginal systems and examines all 36 marginal pairs without
symmetry reduction.  NumPy is used only for batched exact int64 correlations.
"""

from __future__ import annotations

import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "runs" / "v36_29_4_c6x6_direct_exhaustion.json"
MODULI = (2, 2, 3, 3)
REVIEW_COMMIT = "05f18c4f9db8d3cb073f78fb486dce7c033a6b69"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def elements(moduli: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(product(*(range(modulus) for modulus in moduli)))


def correlation(vector: tuple[int, ...], moduli: tuple[int, ...]) -> tuple[int, ...]:
    group = elements(moduli)
    index = {element: position for position, element in enumerate(group)}
    result = []
    for shift in group:
        result.append(
            sum(
                vector[position]
                * vector[
                    index[
                        tuple(
                            (coordinate - displacement) % modulus
                            for coordinate, displacement, modulus in zip(
                                point, shift, moduli
                            )
                        )
                    ]
                ]
                for position, point in enumerate(group)
            )
        )
    return tuple(result)


def enumerate_system(
    moduli: tuple[int, ...],
    bound: int,
    target_sum: int,
    peak: int,
    off_peak: int,
) -> tuple[int, tuple[tuple[int, ...], ...]]:
    """Complete bounded quotient enumeration with exact sum/norm pruning."""

    size = int(np.prod(moduli))
    vector = [0] * size
    sum_norm_candidates = 0
    solutions: list[tuple[int, ...]] = []

    def visit(position: int, remaining_sum: int, remaining_norm: int) -> None:
        nonlocal sum_norm_candidates
        if position == size:
            if remaining_sum == 0 and remaining_norm == 0:
                sum_norm_candidates += 1
                candidate = tuple(vector)
                if correlation(candidate, moduli) == (peak,) + (off_peak,) * (size - 1):
                    solutions.append(candidate)
            return

        remaining = size - position - 1
        for value in range(-bound, bound + 1):
            next_sum = remaining_sum - value
            next_norm = remaining_norm - value * value
            if next_norm < 0 or abs(next_sum) > bound * remaining:
                continue
            if next_norm > remaining * bound * bound:
                continue
            if remaining == 0:
                if next_sum != 0 or next_norm != 0:
                    continue
            elif next_sum * next_sum > next_norm * remaining:
                continue
            vector[position] = value
            visit(position + 1, next_sum, next_norm)
        vector[position] = 0

    visit(0, target_sum, peak)
    return sum_norm_candidates, tuple(solutions)


def full_index(a: int, b: int, x: int, y: int) -> int:
    return 18 * a + 9 * b + 3 * x + y


def shift_permutations() -> tuple[np.ndarray, ...]:
    group = elements(MODULI)
    index = {element: position for position, element in enumerate(group)}
    permutations = []
    for shift in group[1:]:
        permutations.append(
            np.array(
                [
                    index[
                        tuple(
                            (coordinate - displacement) % modulus
                            for coordinate, displacement, modulus in zip(
                                point, shift, MODULI
                            )
                        )
                    ]
                    for point in group
                ],
                dtype=np.int64,
            )
        )
    return tuple(permutations)


def search_full_group(
    c3x3_solutions: tuple[tuple[int, ...], ...],
    c2x2_solutions: tuple[tuple[int, ...], ...],
) -> tuple[int, int, list[dict[str, object]]]:
    patterns = {
        total: tuple(row for row in product((-1, 0, 1), repeat=4) if sum(row) == total)
        for total in range(-4, 5)
    }
    fiber_columns = tuple(
        tuple(full_index(z // 2, z % 2, j // 3, j % 3) for z in range(4))
        for j in range(9)
    )
    shifts = shift_permutations()
    total_candidates = 0
    total_survivors = 0
    pair_counts: list[dict[str, object]] = []

    for c3x3_index, c3x3 in enumerate(c3x3_solutions):
        for c2x2_index, c2x2 in enumerate(c2x2_solutions):

            def build(fibers: range) -> list[tuple[list[int], tuple[int, int, int, int]]]:
                rows: list[tuple[list[int], tuple[int, int, int, int]]] = [
                    ([0] * 36, (0, 0, 0, 0))
                ]
                for fiber in fibers:
                    next_rows = []
                    for vector, column_sums in rows:
                        for pattern in patterns[c3x3[fiber]]:
                            updated = list(vector)
                            for position in range(4):
                                updated[fiber_columns[fiber][position]] = pattern[position]
                            next_rows.append(
                                (
                                    updated,
                                    tuple(
                                        old + new
                                        for old, new in zip(column_sums, pattern)
                                    ),
                                )
                            )
                    rows = next_rows
                return rows

            first_half = build(range(0, 4))
            second_half = build(range(4, 9))
            buckets: dict[tuple[int, int, int, int], list[list[int]]] = {}
            for vector, column_sums in second_half:
                buckets.setdefault(column_sums, []).append(vector)

            candidates = []
            for vector, column_sums in first_half:
                required = tuple(
                    target - partial for target, partial in zip(c2x2, column_sums)
                )
                for second in buckets.get(required, ()):
                    candidates.append([left + right for left, right in zip(vector, second)])

            total_candidates += len(candidates)
            survivors = 0
            if candidates:
                matrix = np.asarray(candidates, dtype=np.int64)
                alive = np.ones(len(matrix), dtype=bool)
                for permutation in shifts:
                    if not alive.any():
                        break
                    active = matrix[alive]
                    correlations = np.einsum(
                        "ij,ij->i", active, active[:, permutation], optimize=True
                    )
                    keep = correlations == 4
                    active_indices = np.flatnonzero(alive)
                    alive[active_indices[~keep]] = False
                survivors = int(alive.sum())
                total_survivors += survivors

            pair_counts.append(
                {
                    "c3x3_index": c3x3_index,
                    "c2x2_index": c2x2_index,
                    "candidates": len(candidates),
                    "survivors": survivors,
                }
            )

    return total_candidates, total_survivors, pair_counts


def main() -> None:
    started = datetime.now(timezone.utc)
    timer = time.perf_counter()

    c3x3_sum_norm, c3x3_solutions = enumerate_system(
        moduli=(3, 3),
        bound=4,
        target_sum=13,
        peak=41,
        off_peak=16,
    )
    c2x2_sum_norm, c2x2_solutions = enumerate_system(
        moduli=(2, 2),
        bound=9,
        target_sum=13,
        peak=61,
        off_peak=36,
    )
    candidates, survivors, pair_counts = search_full_group(
        c3x3_solutions,
        c2x2_solutions,
    )

    assert c3x3_sum_norm == 106353
    assert len(c3x3_solutions) == 9
    assert len(c2x2_solutions) == 4
    assert {tuple(sorted(vector)) for vector in c3x3_solutions} == {
        (-3, 2, 2, 2, 2, 2, 2, 2, 2)
    }
    assert {tuple(sorted(vector)) for vector in c2x2_solutions} == {
        (2, 2, 2, 7)
    }
    assert candidates == 16_964_640
    assert survivors == 0

    document = {
        "schema": "v36-29-4-c6x6-direct-exhaustion-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": "SDS(36,29,4,[6,6])",
        "result": "NONEXISTENT_BY_EXHAUSTION",
        "method": "complete two-layer meet-in-the-middle search without symmetry reduction",
        "marginals": {
            "C3xC3_kernel_order_4": {
                "sum_norm_candidates": c3x3_sum_norm,
                "solutions": len(c3x3_solutions),
                "solution_vectors": c3x3_solutions,
            },
            "C2xC2_kernel_order_9": {
                "sum_norm_candidates": c2x2_sum_norm,
                "solutions": len(c2x2_solutions),
                "solution_vectors": c2x2_solutions,
            },
            "pairs": len(pair_counts),
        },
        "full_search": {
            "marginal_consistent_candidates": candidates,
            "nonidentity_correlations_checked_per_survivor": 35,
            "solutions": survivors,
            "pair_counts": pair_counts,
        },
        "completeness": [
            "All nine C3^2 quotient solutions and all four C2^2 quotient solutions are generated from bounded sum, norm, and full-correlation equations.",
            "For each of the 36 marginal pairs, every {-1,0,1} filling of each four-point C2^2 fiber with the required C3^2 cell sum is generated.",
            "Meet-in-the-middle joins the two fiber halves on the exact four C2^2 marginal sums; it is an indexing optimization, not a quotient by symmetry.",
            "Every joined vector is filtered by all 35 nonidentity correlations using exact int64 arithmetic; none survives.",
        ],
        "provenance": {
            "algorithm_and_initial_implementation": "Fabian Arevalo, independent review of project version 1.0 (MIT License).",
            "review_repository": "https://github.com/farev/Matematica/tree/main/conjectures/signed-difference-sets/masselot-review",
            "review_commit_checked": REVIEW_COMMIT,
            "local_implementation": "Adapted and independently integrated into this project; no SAT solver is used.",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "started_at_utc": started.isoformat(),
        "runtime_seconds": time.perf_counter() - timer,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "marginal_pairs": len(pair_counts),
                "candidates": candidates,
                "solutions": survivors,
                "runtime_seconds": document["runtime_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
