#!/usr/bin/env python3
"""Independent mixed-radix verification of the v=27 quotient artifact."""

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "runs" / "v27_remaining_quotient_exhaustion.json"


def digits(index, moduli):
    row = [0] * len(moduli)
    for position in range(len(moduli) - 1, -1, -1):
        row[position], index = index % moduli[position], index // moduli[position]
    return row


def rank(row, moduli):
    value = 0
    for digit, modulus in zip(row, moduli):
        value = value * modulus + digit
    return value


def autocorrelation(vector, moduli, shift):
    return sum(
        vector[index]
        * vector[
            rank(
                [(coordinate - delta) % modulus for coordinate, delta, modulus in zip(digits(index, moduli), shift, moduli)],
                moduli,
            )
        ]
        for index in range(len(vector))
    )


def quotient_vectors(k, lam, augmentation):
    output = []
    count_vectors = []

    def compositions(prefix, remaining, slots):
        if slots == 1:
            count_vectors.append(tuple(prefix + [remaining]))
            return
        for count in range(remaining + 1):
            compositions(prefix + [count], remaining - count, slots - 1)

    def distinct_permutations(counts, prefix):
        if len(prefix) == 9:
            yield tuple(prefix)
            return
        for offset, count in enumerate(counts):
            if not count:
                continue
            updated = list(counts)
            updated[offset] -= 1
            yield from distinct_permutations(tuple(updated), prefix + [offset - 3])

    compositions([], 9, 7)
    for counts in count_vectors:
        values = range(-3, 4)
        if sum(count * value for count, value in zip(counts, values)) != augmentation:
            continue
        if sum(count * value * value for count, value in zip(counts, values)) != k + 2 * lam:
            continue
        # Multiset recursion is deliberately different from the generator's
        # position-by-position bounded-sum recursion.
        for vector in distinct_permutations(counts, []):
            if all(
                autocorrelation(vector, (3, 3), shift) == 3 * lam
                for shift in itertools.product(range(3), repeat=2)
                if shift != (0, 0)
            ):
                output.append(vector)
    return set(output)


def quotient_actions(representative, instance):
    if instance.endswith("[3,3,3])"):
        matrices = [
            matrix
            for matrix in itertools.product(range(3), repeat=4)
            if (matrix[0] * matrix[3] - matrix[1] * matrix[2]) % 3
        ]
    else:
        matrices = [(1, 0, 0, 1)]
    output = set()
    for aa, ab, ba, bb in matrices:
        for ta, tb in itertools.product(range(3), repeat=2):
            transformed = [0] * 9
            for a, b in itertools.product(range(3), repeat=2):
                new = ((aa * a + ab * b + ta) % 3, (ba * a + bb * b + tb) % 3)
                transformed[3 * new[0] + new[1]] = representative[3 * a + b]
            output.add(tuple(transformed))
    return output


def refinement_count(representative, moduli, k, lam):
    options = {
        total: [fiber for fiber in itertools.product((-1, 0, 1), repeat=3) if sum(fiber) == total]
        for total in range(-3, 4)
    }
    checked = 0
    solutions = 0
    for fibers in itertools.product(*(options[total] for total in representative)):
        checked += 1
        vector = [0] * 27
        if moduli == (3, 3, 3):
            for a, b, c in itertools.product(range(3), repeat=3):
                vector[9 * a + 3 * b + c] = fibers[3 * a + b][c]
        else:
            for a, residue, quotient in itertools.product(range(3), repeat=3):
                vector[9 * a + residue + 3 * quotient] = fibers[3 * a + residue][quotient]
        if sum(value != 0 for value in vector) != k:
            continue
        if all(
            autocorrelation(vector, moduli, shift) == lam
            for shift in itertools.product(*(range(modulus) for modulus in moduli))
            if any(shift)
        ):
            solutions += 1
    return checked, solutions


def main() -> None:
    document = json.loads(ARTIFACT.read_text())
    cached_quotients = {}
    for result in document["results"]:
        parts = result["instance"].split(",")
        k, lam = int(parts[1]), int(parts[2])
        augmentation = {17: 11, 22: 10 if lam == 3 else 16}[k]
        key = (k, lam)
        if key not in cached_quotients:
            cached_quotients[key] = quotient_vectors(k, lam, augmentation)
        solutions = cached_quotients[key]
        assert len(solutions) == result["quotient_solutions"]
        covered = set()
        representatives = [tuple(rep) for rep in result["quotient_representatives"]]
        for representative in representatives:
            covered |= quotient_actions(representative, result["instance"])
        assert covered == solutions
        moduli = (3, 3, 3) if result["instance"].endswith("[3,3,3])") else (3, 9)
        counts = []
        full_solutions = 0
        for representative in representatives:
            checked, found = refinement_count(representative, moduli, k, lam)
            counts.append(checked)
            full_solutions += found
        assert counts == result["refinement_counts"]
        assert full_solutions == result["full_solutions"] == 0
        print(result["instance"], "PASS")
    print("independent v=27 mixed-radix verification: PASS")


if __name__ == "__main__":
    main()
