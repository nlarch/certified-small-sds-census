#!/usr/bin/env python3
"""Exhaust quotient orbits and all refinements for the six remaining v=27 cases."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "runs" / "v27_remaining_quotient_exhaustion.json"
PARAMETERS = ((17, 4, 11), (22, 3, 10), (22, 9, 16))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quotient_correlation(vector, da, db):
    return sum(
        vector[3 * a + b] * vector[3 * ((a - da) % 3) + (b - db) % 3]
        for a in range(3)
        for b in range(3)
    )


def quotient_solutions(k, lam, augmentation):
    candidates = []
    target_norm = k + 2 * lam

    def recurse(prefix, total, norm):
        remaining = 9 - len(prefix)
        if remaining == 0:
            if total == augmentation and norm == target_norm:
                candidates.append(tuple(prefix))
            return
        if total - 3 * remaining > augmentation or total + 3 * remaining < augmentation:
            return
        if norm > target_norm:
            return
        for value in range(-3, 4):
            recurse(prefix + [value], total + value, norm + value * value)

    recurse([], 0, 0)
    solutions = [
        vector
        for vector in candidates
        if all(
            quotient_correlation(vector, a, b) == 3 * lam
            for a in range(3)
            for b in range(3)
            if (a, b) != (0, 0)
        )
    ]
    return candidates, solutions


def invertible_matrices():
    return tuple(
        matrix
        for matrix in itertools.product(range(3), repeat=4)
        if (matrix[0] * matrix[3] - matrix[1] * matrix[2]) % 3
    )


def affine_transform(vector, matrix, translation):
    aa, ab, ba, bb = matrix
    output = [0] * 9
    for a in range(3):
        for b in range(3):
            new_a = (aa * a + ab * b + translation[0]) % 3
            new_b = (ba * a + bb * b + translation[1]) % 3
            output[3 * new_a + new_b] = vector[3 * a + b]
    return tuple(output)


def orbit_representatives(solutions, matrices):
    unseen = set(solutions)
    representatives = []
    orbit_sizes = []
    while unseen:
        seed = min(unseen)
        orbit = {
            affine_transform(seed, matrix, translation)
            for matrix in matrices
            for translation in itertools.product(range(3), repeat=2)
        }
        assert orbit <= set(solutions)
        unseen -= orbit
        representatives.append(min(orbit))
        orbit_sizes.append(len(orbit))
    return representatives, orbit_sizes


def full_correlation(vector, group, shift):
    if group == "c3x3x3":
        da, db, dc = shift
        return sum(
            vector[9 * a + 3 * b + c]
            * vector[9 * ((a - da) % 3) + 3 * ((b - db) % 3) + (c - dc) % 3]
            for a in range(3)
            for b in range(3)
            for c in range(3)
        )
    da, db = shift
    return sum(
        vector[9 * a + b] * vector[9 * ((a - da) % 3) + (b - db) % 9]
        for a in range(3)
        for b in range(9)
    )


def refinements(pattern, group, k, lam):
    options = {
        total: tuple(
            fiber
            for fiber in itertools.product((-1, 0, 1), repeat=3)
            if sum(fiber) == total
        )
        for total in range(-3, 4)
    }
    checked = 1
    for total in pattern:
        checked *= len(options[total])
    solutions = 0
    for fibers in itertools.product(*(options[total] for total in pattern)):
        vector = [0] * 27
        if group == "c3x3x3":
            for a in range(3):
                for b in range(3):
                    fiber = fibers[3 * a + b]
                    for c in range(3):
                        vector[9 * a + 3 * b + c] = fiber[c]
            shifts = itertools.product(range(3), repeat=3)
            identity = (0, 0, 0)
        else:
            for a in range(3):
                for residue in range(3):
                    fiber = fibers[3 * a + residue]
                    for quotient in range(3):
                        vector[9 * a + residue + 3 * quotient] = fiber[quotient]
            shifts = itertools.product(range(3), range(9))
            identity = (0, 0)
        if sum(value != 0 for value in vector) != k:
            continue
        if all(
            full_correlation(vector, group, shift) == lam
            for shift in shifts
            if shift != identity
        ):
            solutions += 1
    return checked, solutions


def main() -> None:
    identity_matrix = ((1, 0, 0, 1),)
    full_matrices = invertible_matrices()
    results = []
    for k, lam, augmentation in PARAMETERS:
        candidates, solutions = quotient_solutions(k, lam, augmentation)
        for group_tag, group_factors, matrices, action in (
            ("c3x3x3", [3, 3, 3], full_matrices, "AGL(2,3), lifted on the first two factors"),
            ("c3x9", [3, 9], identity_matrix, "all C3^2 translations, lifted to C3 x C9"),
        ):
            representatives, orbit_sizes = orbit_representatives(solutions, matrices)
            refinement_counts = []
            full_solutions = 0
            for representative in representatives:
                checked, count = refinements(representative, group_tag, k, lam)
                refinement_counts.append(checked)
                full_solutions += count
            assert full_solutions == 0
            results.append(
                {
                    "instance": f"SDS(27,{k},{lam},[{','.join(map(str, group_factors))}])",
                    "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
                    "quotient": "C3^2",
                    "kernel_order": 3,
                    "cell_bound": [-3, 3],
                    "zero_shift_correlation": k + 2 * lam,
                    "nonzero_shift_correlation": 3 * lam,
                    "candidates_after_sum_and_norm": len(candidates),
                    "quotient_solutions": len(solutions),
                    "symmetry_action": action,
                    "quotient_orbit_count": len(representatives),
                    "quotient_orbit_sizes": orbit_sizes,
                    "quotient_representatives": representatives,
                    "refinement_counts": refinement_counts,
                    "total_refinements_checked": sum(refinement_counts),
                    "full_solutions": full_solutions,
                }
            )
    document = {
        "schema": "v27-remaining-quotient-exhaustion-v1",
        "completeness_argument": [
            "Projection through a kernel of order three gives identity quotient correlation k+2lambda and every nonidentity quotient correlation 3lambda.",
            "All bounded integral C3^2 quotient vectors with the required sum and norm are enumerated before exact quotient autocorrelation filtering.",
            "For C3^3, every AGL(2,3) quotient action lifts; for C3 x C9, only the complete translation action is used, and every translation lifts.",
            "Every ternary coefficient refinement of every orbit representative is checked against every full-group shift.",
        ],
        "results": results,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "resolved": len(results),
                "total_refinements": sum(result["total_refinements_checked"] for result in results),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
