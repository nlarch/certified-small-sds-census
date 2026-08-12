#!/usr/bin/env python3
"""Independent direct-product verifier for the combined quotient artifact."""

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "runs" / "v36_29_4_combined_quotient_exhaustion.json"


def autocorrelation(vector, moduli, shift):
    def digits(index):
        result = [0] * len(moduli)
        for j in range(len(moduli) - 1, -1, -1):
            result[j], index = index % moduli[j], index // moduli[j]
        return result

    def rank(row):
        value = 0
        for digit, modulus in zip(row, moduli):
            value = value * modulus + digit
        return value

    rows = [digits(index) for index in range(len(vector))]
    return sum(
        vector[index]
        * vector[
            rank([(row[j] - shift[j]) % moduli[j] for j in range(len(moduli))])
        ]
        for index, row in enumerate(rows)
    )


def verify_c2x18(expected):
    options = {
        total: tuple(row for row in itertools.product(range(-3, 4), repeat=3) if sum(row) == total)
        for total in (7, 2)
    }
    candidates = 0
    solutions = 0
    for rows in itertools.product(options[7], options[2], options[2], options[2]):
        vector = tuple(value for row in rows for value in row)
        if tuple(sum(rows[r][c] for r in range(4)) for c in range(3)) != (1, 6, 6):
            continue
        if sum(value * value for value in vector) != 37:
            continue
        candidates += 1
        if all(
            autocorrelation(vector, (2, 2, 3), shift) == 12
            for shift in itertools.product(range(2), range(2), range(3))
            if shift != (0, 0, 0)
        ):
            solutions += 1
    assert candidates == expected["candidates_after_marginals_and_norm"] == 144
    assert solutions == expected["full_quotient_solutions"] == 0


def verify_c3x12(expected):
    pair_options = {
        total: tuple(pair for pair in itertools.product(range(-2, 3), repeat=2) if sum(pair) == total)
        for total in (-3, 2)
    }
    candidates = 0
    solutions = 0
    for columns in itertools.product(pair_options[-3], *([pair_options[2]] * 8)):
        vector = tuple(columns[column][row] for row in range(2) for column in range(9))
        if (sum(vector[:9]), sum(vector[9:])) != (4, 9):
            continue
        if sum(value * value for value in vector) != 33:
            continue
        candidates += 1
        if all(
            autocorrelation(vector, (2, 3, 3), shift) == 8
            for shift in itertools.product(range(2), range(3), range(3))
            if shift != (0, 0, 0)
        ):
            solutions += 1
    assert candidates == expected["candidates_after_marginals_and_norm"] == 420
    assert solutions == expected["full_quotient_solutions"] == 0


def main() -> None:
    document = json.loads(ARTIFACT.read_text())
    by_instance = {result["instance"]: result for result in document["results"]}
    verify_c2x18(by_instance["SDS(36,29,4,[2,18])"])
    verify_c3x12(by_instance["SDS(36,29,4,[3,12])"])
    print("independent combined-quotient verification: PASS")


if __name__ == "__main__":
    main()
