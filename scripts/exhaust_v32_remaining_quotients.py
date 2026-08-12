#!/usr/bin/env python3
"""Certified quotient ladders for the four remaining negative v=32 cases."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "runs" / "v32_remaining_quotient_exhaustion.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cyclic_correlation(vector, shift):
    return sum(vector[index] * vector[(index - shift) % len(vector)] for index in range(len(vector)))


def bounded_vectors(length, bound, target_sum, target_norm):
    output = []

    def recurse(prefix, total, norm):
        remaining = length - len(prefix)
        if remaining == 0:
            if total == target_sum and norm == target_norm:
                output.append(tuple(prefix))
            return
        if total - bound * remaining > target_sum or total + bound * remaining < target_sum:
            return
        if norm > target_norm:
            return
        for value in range(-bound, bound + 1):
            recurse(prefix + [value], total + value, norm + value * value)

    recurse([], 0, 0)
    return output


def cyclic_affine_orbits(solutions, modulus):
    units = tuple(value for value in range(modulus) if value % 2)

    def transform(vector, unit, translation):
        output = [0] * modulus
        for index in range(modulus):
            output[(unit * index + translation) % modulus] = vector[index]
        return tuple(output)

    unseen = set(solutions)
    representatives = []
    orbit_sizes = []
    while unseen:
        seed = min(unseen)
        orbit = {
            transform(seed, unit, translation)
            for unit in units
            for translation in range(modulus)
        }
        assert seed in orbit
        unseen -= orbit
        representatives.append(min(orbit))
        orbit_sizes.append(len(orbit))
    return sorted(representatives), orbit_sizes


def split_integer_pattern(pattern, bound):
    choices = [
        tuple((left, total - left) for left in range(-bound, bound + 1) if -bound <= total - left <= bound)
        for total in pattern
    ]
    candidate_count = 1
    for choice in choices:
        candidate_count *= len(choice)
    for pairs in itertools.product(*choices):
        yield tuple(pair[0] for pair in pairs) + tuple(pair[1] for pair in pairs)
    return candidate_count


def cyclic_case(k, lam, augmentation):
    q8_candidates = bounded_vectors(8, 4, augmentation, k + 3 * lam)
    q8_solutions = [
        vector
        for vector in q8_candidates
        if all(cyclic_correlation(vector, shift) == 4 * lam for shift in range(1, 8))
    ]
    q8_representatives, q8_orbit_sizes = cyclic_affine_orbits(q8_solutions, 8)

    q16_solutions = set()
    q16_refinement_counts = []
    q16_solution_counts = []
    for pattern in q8_representatives:
        choices = [
            tuple((left, total - left) for left in range(-2, 3) if -2 <= total - left <= 2)
            for total in pattern
        ]
        checked = 1
        for choice in choices:
            checked *= len(choice)
        found = 0
        for pairs in itertools.product(*choices):
            vector = tuple(pair[0] for pair in pairs) + tuple(pair[1] for pair in pairs)
            if sum(value * value for value in vector) != k + lam:
                continue
            if all(cyclic_correlation(vector, shift) == 2 * lam for shift in range(1, 16)):
                found += 1
                q16_solutions.add(vector)
        q16_refinement_counts.append(checked)
        q16_solution_counts.append(found)
    # These are normalized relative to a representative at the C8 stage.  Do
    # not quotient them again: the full C16 affine orbit need not remain inside
    # this normalized-parent slice.  Refining every survivor is the transparent
    # complete cover.
    q16_representatives = sorted(q16_solutions)

    coefficient_options = {
        total: tuple(
            pair for pair in itertools.product((-1, 0, 1), repeat=2) if sum(pair) == total
        )
        for total in range(-2, 3)
    }
    full_refinement_counts = []
    full_solutions = 0
    for pattern in q16_representatives:
        checked = 1
        for total in pattern:
            checked *= len(coefficient_options[total])
        full_refinement_counts.append(checked)
        for pairs in itertools.product(*(coefficient_options[total] for total in pattern)):
            vector = tuple(pair[0] for pair in pairs) + tuple(pair[1] for pair in pairs)
            if sum(value != 0 for value in vector) != k:
                continue
            if all(cyclic_correlation(vector, shift) == lam for shift in range(1, 32)):
                full_solutions += 1
    assert full_solutions == 0
    return {
        "instance": f"SDS(32,{k},{lam},[32])",
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
        "ladder": ["C8 (kernel 4)", "C16 (kernel 2)", "C32 (kernel 1)"],
        "q8_candidates_after_sum_and_norm": len(q8_candidates),
        "q8_solutions": len(q8_solutions),
        "q8_affine_orbit_count": len(q8_representatives),
        "q8_orbit_sizes": q8_orbit_sizes,
        "q8_representatives": q8_representatives,
        "q16_refinement_counts": q16_refinement_counts,
        "q16_solution_counts": q16_solution_counts,
        "q16_unique_solutions_in_normalized_parents": len(q16_solutions),
        "q16_normalized_parent_survivor_count": len(q16_representatives),
        "q16_representatives": q16_representatives,
        "full_refinement_counts": full_refinement_counts,
        "total_full_refinements": sum(full_refinement_counts),
        "full_solutions": full_solutions,
    }


def product_correlation(vector, modulus, da, db):
    return sum(
        vector[modulus * a + b]
        * vector[modulus * ((a - da) % 2) + (b - db) % modulus]
        for a in range(2)
        for b in range(modulus)
    )


def product_translation_orbits(solutions, modulus):
    def translate(vector, ta, tb):
        output = [0] * (2 * modulus)
        for a in range(2):
            for b in range(modulus):
                output[modulus * ((a + ta) % 2) + (b + tb) % modulus] = vector[modulus * a + b]
        return tuple(output)

    unseen = set(solutions)
    representatives = []
    orbit_sizes = []
    while unseen:
        seed = min(unseen)
        orbit = {translate(seed, a, b) for a in range(2) for b in range(modulus)}
        assert orbit <= set(solutions)
        unseen -= orbit
        representatives.append(min(orbit))
        orbit_sizes.append(len(orbit))
    return sorted(representatives), orbit_sizes


def c2x16_dense_case():
    k, lam, augmentation = 28, 12, 20
    q8_candidates = bounded_vectors(8, 4, augmentation, k + 3 * lam)
    q8_solutions = [
        vector
        for vector in q8_candidates
        if all(
            product_correlation(vector, 4, a, b) == 4 * lam
            for a in range(2)
            for b in range(4)
            if (a, b) != (0, 0)
        )
    ]
    q8_representatives, q8_orbit_sizes = product_translation_orbits(q8_solutions, 4)
    q16_solutions = set()
    q16_refinement_counts = []
    q16_solution_counts = []
    for pattern in q8_representatives:
        choices = [
            tuple((left, total - left) for left in range(-2, 3) if -2 <= total - left <= 2)
            for total in pattern
        ]
        checked = 1
        for choice in choices:
            checked *= len(choice)
        found = 0
        for pairs in itertools.product(*choices):
            vector = [0] * 16
            for a in range(2):
                for b in range(4):
                    pair = pairs[4 * a + b]
                    vector[8 * a + b], vector[8 * a + b + 4] = pair
            vector = tuple(vector)
            if sum(value * value for value in vector) != k + lam:
                continue
            if all(
                product_correlation(vector, 8, a, b) == 2 * lam
                for a in range(2)
                for b in range(8)
                if (a, b) != (0, 0)
            ):
                found += 1
                q16_solutions.add(vector)
        q16_refinement_counts.append(checked)
        q16_solution_counts.append(found)
    # As in the cyclic ladder, retain every survivor in the normalized-parent
    # slice instead of imposing a second, unjustified symmetry quotient.
    q16_representatives = sorted(q16_solutions)

    options = {
        total: tuple(pair for pair in itertools.product((-1, 0, 1), repeat=2) if sum(pair) == total)
        for total in range(-2, 3)
    }
    full_refinement_counts = []
    full_solutions = 0
    for pattern in q16_representatives:
        checked = 1
        for total in pattern:
            checked *= len(options[total])
        full_refinement_counts.append(checked)
        for pairs in itertools.product(*(options[total] for total in pattern)):
            vector = [0] * 32
            for a in range(2):
                for b in range(8):
                    pair = pairs[8 * a + b]
                    vector[16 * a + b], vector[16 * a + b + 8] = pair
            if sum(value != 0 for value in vector) != k:
                continue
            if all(
                product_correlation(vector, 16, a, b) == lam
                for a in range(2)
                for b in range(16)
                if (a, b) != (0, 0)
            ):
                full_solutions += 1
    assert full_solutions == 0
    return {
        "instance": "SDS(32,28,12,[2,16])",
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
        "ladder": ["C2 x C4 (kernel 4)", "C2 x C8 (kernel 2)", "C2 x C16 (kernel 1)"],
        "symmetry": "translations only at both quotient stages",
        "q8_candidates_after_sum_and_norm": len(q8_candidates),
        "q8_solutions": len(q8_solutions),
        "q8_translation_orbit_count": len(q8_representatives),
        "q8_orbit_sizes": q8_orbit_sizes,
        "q8_representatives": q8_representatives,
        "q16_refinement_counts": q16_refinement_counts,
        "q16_solution_counts": q16_solution_counts,
        "q16_unique_solutions_in_normalized_parents": len(q16_solutions),
        "q16_normalized_parent_survivor_count": len(q16_representatives),
        "q16_representatives": q16_representatives,
        "full_refinement_counts": full_refinement_counts,
        "total_full_refinements": sum(full_refinement_counts),
        "full_solutions": full_solutions,
    }


def elementary_dense_case():
    zero_types = {
        "affine_plane": (0, 1, 2, 3),
        "affinely_independent": (0, 1, 2, 4),
    }

    def character_sign(character, point):
        return -1 if bin(character & point).count("1") % 2 else 1

    type_counts = {}
    solutions = 0
    for label, zero_set in zero_types.items():
        available = tuple(point for point in range(32) if point not in zero_set)
        checked = 0
        found = 0
        for negative_set in itertools.combinations(available, 4):
            checked += 1
            valid = True
            for character in range(1, 32):
                value = -sum(character_sign(character, point) for point in zero_set)
                value -= 2 * sum(character_sign(character, point) for point in negative_set)
                if abs(value) != 4:
                    valid = False
                    break
            if valid:
                found += 1
        type_counts[label] = {"negative_supports_checked": checked, "solutions": found}
        solutions += found
    assert solutions == 0
    return {
        "instance": "SDS(32,28,12,[2,2,2,2,2])",
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
        "representation": "f = 1 - 1_Z - 2*1_N with |Z|=|N|=4",
        "symmetry": "AGL(5,2) has exactly two four-point-set types: an affine plane and an affinely independent set",
        "zero_support_representatives": zero_types,
        "type_counts": type_counts,
        "total_negative_supports_checked": sum(item["negative_supports_checked"] for item in type_counts.values()),
        "full_solutions": solutions,
    }


def main() -> None:
    results = [
        cyclic_case(20, 4, 12),
        cyclic_case(28, 12, 20),
        c2x16_dense_case(),
        elementary_dense_case(),
    ]
    document = {
        "schema": "v32-remaining-quotient-exhaustion-v1",
        "completeness_argument": [
            "Each cyclic or product quotient ladder enumerates all bounded integral cell sums, then all exact two-cell refinements, ending with every {-1,0,1} coefficient refinement.",
            "All affine actions used for cyclic quotients and all translations used for product quotients lift to the next group in the ladder.",
            "For C2^5, any four-point zero support is affine-equivalent either to the complete affine plane or to four affinely independent points; every disjoint four-point negative support is checked.",
        ],
        "results": results,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "sha256": sha256(OUTPUT), "resolved": len(results)}, indent=2))


if __name__ == "__main__":
    main()
