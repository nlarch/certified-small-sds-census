#!/usr/bin/env python3
"""Exhaust the normalized combined quotients for two SDS(36,29,4) groups."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "runs" / "v36_29_4_combined_quotient_exhaustion.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cyclic_correlation_2x2x3(vector, shift):
    dr, dc = shift
    return sum(
        vector[3 * row + col] * vector[3 * (row ^ dr) + (col - dc) % 3]
        for row in range(4)
        for col in range(3)
    )


def exhaust_c2x18():
    values = range(-3, 4)
    row_options = {
        total: [row for row in itertools.product(values, repeat=3) if sum(row) == total]
        for total in (7, 2)
    }
    candidates = []
    for row0 in row_options[7]:
        for row1 in row_options[2]:
            for row2 in row_options[2]:
                partial = [sum(values) for values in zip(row0, row1, row2)]
                row3 = tuple(target - partial[i] for i, target in enumerate((1, 6, 6)))
                if row3 not in row_options[2]:
                    continue
                vector = row0 + row1 + row2 + row3
                if sum(value * value for value in vector) == 37:
                    candidates.append(vector)
    solutions = [
        vector
        for vector in candidates
        if all(
            cyclic_correlation_2x2x3(vector, (row, col)) == 12
            for row in range(4)
            for col in range(3)
            if (row, col) != (0, 0)
        )
    ]
    return {
        "instance": "SDS(36,29,4,[2,18])",
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
        "quotient": "C2^2 x C3",
        "kernel_order": 3,
        "cell_bound": [-3, 3],
        "normalized_real_marginal": [7, 2, 2, 2],
        "normalized_order3_marginal": [1, 6, 6],
        "zero_shift_correlation": 37,
        "nonzero_shift_correlation": 12,
        "row_option_counts": {str(key): len(value) for key, value in row_options.items()},
        "candidates_after_marginals_and_norm": len(candidates),
        "full_quotient_solutions": len(solutions),
    }


def correlation_3x3(vector, da, db):
    return sum(
        vector[3 * a + b] * vector[3 * ((a - da) % 3) + (b - db) % 3]
        for a in range(3)
        for b in range(3)
    )


def enumerate_c3x3_projection():
    candidates = []

    def recurse(prefix, total, square_total):
        remaining = 9 - len(prefix)
        if not remaining:
            if total == 13 and square_total == 41:
                candidates.append(tuple(prefix))
            return
        if total - 4 * remaining > 13 or total + 4 * remaining < 13:
            return
        if square_total > 41:
            return
        for value in range(-4, 5):
            recurse(prefix + [value], total + value, square_total + value * value)

    recurse([], 0, 0)
    solutions = [
        vector
        for vector in candidates
        if all(
            correlation_3x3(vector, da, db) == 16
            for da in range(3)
            for db in range(3)
            if (da, db) != (0, 0)
        )
    ]
    return len(candidates), solutions


def cyclic_correlation_2x3x3(vector, shift):
    de, da, db = shift
    return sum(
        vector[9 * e + 3 * a + b]
        * vector[9 * (e ^ de) + 3 * ((a - da) % 3) + (b - db) % 3]
        for e in range(2)
        for a in range(3)
        for b in range(3)
    )


def exhaust_c3x12():
    projection_candidates, projection_solutions = enumerate_c3x3_projection()
    expected = tuple([-3] + [2] * 8)
    assert len(projection_solutions) == 9
    assert {tuple(sorted(vector)) for vector in projection_solutions} == {
        tuple(sorted(expected))
    }

    column_options = {
        total: [pair for pair in itertools.product(range(-2, 3), repeat=2) if sum(pair) == total]
        for total in (-3, 2)
    }
    candidates = []
    for columns in itertools.product(column_options[-3], *([column_options[2]] * 8)):
        rows = tuple(tuple(column[row] for column in columns) for row in range(2))
        if tuple(map(sum, rows)) != (4, 9):
            continue
        vector = rows[0] + rows[1]
        if sum(value * value for value in vector) == 33:
            candidates.append(vector)
    solutions = [
        vector
        for vector in candidates
        if all(
            cyclic_correlation_2x3x3(vector, (e, a, b)) == 8
            for e in range(2)
            for a in range(3)
            for b in range(3)
            if (e, a, b) != (0, 0, 0)
        )
    ]
    return {
        "instance": "SDS(36,29,4,[3,12])",
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
        "quotient": "C2 x C3^2",
        "kernel_order": 2,
        "cell_bound": [-2, 2],
        "normalized_real_marginal": [4, 9],
        "normalized_c3x3_marginal": list(expected),
        "c3x3_projection_candidates_after_sum_and_norm": projection_candidates,
        "c3x3_projection_solutions": len(projection_solutions),
        "c3x3_projection_affine_orbits": 1,
        "zero_shift_correlation": 33,
        "nonzero_shift_correlation": 8,
        "column_option_counts": {str(key): len(value) for key, value in column_options.items()},
        "candidates_after_marginals_and_norm": len(candidates),
        "full_quotient_solutions": len(solutions),
    }


def main() -> None:
    results = [exhaust_c2x18(), exhaust_c3x12()]
    assert all(result["full_quotient_solutions"] == 0 for result in results)
    document = {
        "schema": "v36-29-4-combined-quotient-exhaustion-v1",
        "result_derivation": [
            "Projection to a quotient with kernel K turns the identity correlation into k+(|K|-1)lambda and every nonidentity quotient correlation into |K|lambda.",
            "Translations normalize the unique real and order-three exceptional fibers independently by the C6 = C2 x C3 Chinese-remainder decomposition.",
            "Every bounded integral quotient vector satisfying the normalized marginals and zero-shift norm is enumerated, then every remaining quotient autocorrelation is checked.",
        ],
        "results": results,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "results": [
                    [result["instance"], result["full_quotient_solutions"]]
                    for result in results
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
