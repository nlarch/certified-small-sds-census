#!/usr/bin/env python3
"""Independent orbit-coverage and full-refinement verification for v=32."""

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "runs" / "v32_remaining_quotient_exhaustion.json"


def mixed_correlation(vector, moduli, shift):
    rows = []
    for raw in range(len(vector)):
        value = raw
        row = [0] * len(moduli)
        for j in range(len(moduli) - 1, -1, -1):
            row[j], value = value % moduli[j], value // moduli[j]
        rows.append(row)

    def rank(row):
        value = 0
        for coordinate, modulus in zip(row, moduli):
            value = value * modulus + coordinate
        return value

    return sum(
        vector[index]
        * vector[
            rank(
                [(rows[index][j] - shift[j]) % moduli[j] for j in range(len(moduli))]
            )
        ]
        for index in range(len(vector))
    )


def count_compositions(total, slots):
    if slots == 1:
        yield (total,)
        return
    for head in range(total + 1):
        for tail in count_compositions(total - head, slots - 1):
            yield (head,) + tail


def multiset_permutations(counts, values, prefix=()):
    if len(prefix) == sum(counts) + len(prefix):
        yield prefix
        return
    if not any(counts):
        yield prefix
        return
    for index, count in enumerate(counts):
        if not count:
            continue
        updated = list(counts)
        updated[index] -= 1
        yield from multiset_permutations(tuple(updated), values, prefix + (values[index],))


def quotient_solutions(length, bound, total, norm, moduli, off_correlation):
    values = tuple(range(-bound, bound + 1))
    solutions = set()
    candidates = 0
    for counts in count_compositions(length, len(values)):
        if sum(count * value for count, value in zip(counts, values)) != total:
            continue
        if sum(count * value * value for count, value in zip(counts, values)) != norm:
            continue
        for vector in multiset_permutations(counts, values):
            candidates += 1
            if all(
                mixed_correlation(vector, moduli, shift) == off_correlation
                for shift in itertools.product(*(range(modulus) for modulus in moduli))
                if any(shift)
            ):
                solutions.add(vector)
    return candidates, solutions


def cyclic_affine_cover(representatives, modulus):
    cover = set()
    for representative in representatives:
        for unit in range(1, modulus, 2):
            for translation in range(modulus):
                output = [0] * modulus
                for index in range(modulus):
                    output[(unit * index + translation) % modulus] = representative[index]
                cover.add(tuple(output))
    return cover


def product_translation_cover(representatives, modulus):
    cover = set()
    for representative in representatives:
        for ta in range(2):
            for tb in range(modulus):
                output = [0] * (2 * modulus)
                for a in range(2):
                    for b in range(modulus):
                        output[modulus * ((a + ta) % 2) + (b + tb) % modulus] = representative[modulus * a + b]
                cover.add(tuple(output))
    return cover


def split_to_next(pattern, target_moduli, target_norm, target_off):
    bound = 2
    choices = [
        tuple((left, total - left) for left in range(-bound, bound + 1) if -bound <= total - left <= bound)
        for total in pattern
    ]
    checked = 1
    for choice in choices:
        checked *= len(choice)
    solutions = []
    for pairs in itertools.product(*choices):
        if target_moduli == (16,):
            vector = tuple(pair[0] for pair in pairs) + tuple(pair[1] for pair in pairs)
        else:
            old_modulus = target_moduli[1] // 2
            vector = [0] * (2 * target_moduli[1])
            for a in range(2):
                for b in range(old_modulus):
                    pair = pairs[old_modulus * a + b]
                    vector[target_moduli[1] * a + b] = pair[0]
                    vector[target_moduli[1] * a + b + old_modulus] = pair[1]
            vector = tuple(vector)
        if sum(value * value for value in vector) != target_norm:
            continue
        if all(
            mixed_correlation(vector, target_moduli, shift) == target_off
            for shift in itertools.product(*(range(modulus) for modulus in target_moduli))
            if any(shift)
        ):
            solutions.append(vector)
    return checked, solutions


def full_refine(pattern, moduli, k, lam):
    options = {
        total: tuple(pair for pair in itertools.product((-1, 0, 1), repeat=2) if sum(pair) == total)
        for total in range(-2, 3)
    }
    checked = 1
    for total in pattern:
        checked *= len(options[total])
    found = 0
    for pairs in itertools.product(*(options[total] for total in pattern)):
        if moduli == (32,):
            vector = tuple(pair[0] for pair in pairs) + tuple(pair[1] for pair in pairs)
        else:
            vector = [0] * 32
            for a in range(2):
                for b in range(8):
                    pair = pairs[8 * a + b]
                    vector[16 * a + b], vector[16 * a + b + 8] = pair
        if sum(value != 0 for value in vector) != k:
            continue
        if all(
            mixed_correlation(vector, moduli, shift) == lam
            for shift in itertools.product(*(range(modulus) for modulus in moduli))
            if any(shift)
        ):
            found += 1
    return checked, found


def verify_cyclic(result, k, lam, augmentation):
    candidate_count, q8 = quotient_solutions(8, 4, augmentation, k + 3 * lam, (8,), 4 * lam)
    assert candidate_count == result["q8_candidates_after_sum_and_norm"]
    assert len(q8) == result["q8_solutions"]
    q8_reps = [tuple(vector) for vector in result["q8_representatives"]]
    assert cyclic_affine_cover(q8_reps, 8) == q8
    q16 = set()
    counts, solution_counts = [], []
    for representative in q8_reps:
        checked, found = split_to_next(representative, (16,), k + lam, 2 * lam)
        counts.append(checked)
        solution_counts.append(len(found))
        q16.update(found)
    assert counts == result["q16_refinement_counts"]
    assert solution_counts == result["q16_solution_counts"]
    assert q16 == {tuple(vector) for vector in result["q16_representatives"]}
    full_counts = []
    solutions = 0
    for representative in sorted(q16):
        checked, found = full_refine(representative, (32,), k, lam)
        full_counts.append(checked)
        solutions += found
    assert full_counts == result["full_refinement_counts"]
    assert solutions == result["full_solutions"] == 0


def verify_product(result):
    k, lam, augmentation = 28, 12, 20
    candidate_count, q8 = quotient_solutions(8, 4, augmentation, k + 3 * lam, (2, 4), 4 * lam)
    assert candidate_count == result["q8_candidates_after_sum_and_norm"]
    assert len(q8) == result["q8_solutions"]
    q8_reps = [tuple(vector) for vector in result["q8_representatives"]]
    assert product_translation_cover(q8_reps, 4) == q8
    q16 = set()
    counts, solution_counts = [], []
    for representative in q8_reps:
        checked, found = split_to_next(representative, (2, 8), k + lam, 2 * lam)
        counts.append(checked)
        solution_counts.append(len(found))
        q16.update(found)
    assert counts == result["q16_refinement_counts"]
    assert solution_counts == result["q16_solution_counts"]
    assert q16 == {tuple(vector) for vector in result["q16_representatives"]}
    full_counts = []
    solutions = 0
    for representative in sorted(q16):
        checked, found = full_refine(representative, (2, 16), k, lam)
        full_counts.append(checked)
        solutions += found
    assert full_counts == result["full_refinement_counts"]
    assert solutions == result["full_solutions"] == 0


def verify_elementary(result):
    representatives = {
        label: tuple(points) for label, points in result["zero_support_representatives"].items()
    }

    def character(character, point):
        return -1 if bin(character & point).count("1") % 2 else 1

    for label, zero_set in representatives.items():
        available = tuple(point for point in range(32) if point not in zero_set)
        checked = 0
        found = 0
        for negative_set in itertools.combinations(available, 4):
            checked += 1
            vector = [1] * 32
            for point in zero_set:
                vector[point] = 0
            for point in negative_set:
                vector[point] = -1
            if all(
                mixed_correlation(vector, (2, 2, 2, 2, 2), shift) == 12
                for shift in itertools.product(range(2), repeat=5)
                if any(shift)
            ):
                found += 1
        assert {"negative_supports_checked": checked, "solutions": found} == result["type_counts"][label]
    # Classification: translating one point to zero leaves three distinct
    # nonzero differences.  Their F2 rank is either two (then they are exactly
    # u,v,u+v, an affine plane) or three (affinely independent); GL(5,2) is
    # transitive on ordered independent tuples of either rank.
    ranks = set()
    for subset in itertools.combinations(range(32), 4):
        base = subset[0]
        differences = [point ^ base for point in subset[1:]]
        basis = []
        for value in differences:
            reduced = value
            for pivot in basis:
                reduced = min(reduced, reduced ^ pivot)
            if reduced:
                basis.append(reduced)
                basis.sort(reverse=True)
        ranks.add(len(basis))
    assert ranks == {2, 3}


def main() -> None:
    document = json.loads(ARTIFACT.read_text())
    by_instance = {result["instance"]: result for result in document["results"]}
    verify_cyclic(by_instance["SDS(32,20,4,[32])"], 20, 4, 12)
    print("SDS(32,20,4,[32]) PASS")
    verify_cyclic(by_instance["SDS(32,28,12,[32])"], 28, 12, 20)
    print("SDS(32,28,12,[32]) PASS")
    verify_product(by_instance["SDS(32,28,12,[2,16])"])
    print("SDS(32,28,12,[2,16]) PASS")
    verify_elementary(by_instance["SDS(32,28,12,[2,2,2,2,2])"])
    print("SDS(32,28,12,[2,2,2,2,2]) PASS")
    print("independent v=32 quotient verification: PASS")


if __name__ == "__main__":
    main()
