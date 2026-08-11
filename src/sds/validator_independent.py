"""Independent mixed-radix/index-table validator.

This implementation does not import or reuse the reference validator's
element construction, tuple arithmetic, or element-to-coefficient map.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

from .model import Instance


def _digits(index: int, moduli: Sequence[int]) -> List[int]:
    result = [0] * len(moduli)
    for coordinate in range(len(moduli) - 1, -1, -1):
        result[coordinate] = index % moduli[coordinate]
        index //= moduli[coordinate]
    return result


def _rank(digits: Sequence[int], moduli: Sequence[int]) -> int:
    result = 0
    for digit, modulus in zip(digits, moduli):
        result = result * modulus + digit
    return result


def validate(instance: Instance, coefficients: Sequence[int]) -> Dict[str, object]:
    errors = []
    if len(coefficients) != instance.v:
        return {"valid": False, "errors": ["coefficient vector length mismatch"]}
    if any(value not in (-1, 0, 1) for value in coefficients):
        errors.append("coefficient outside {0,+1,-1}")
    support = instance.v - list(coefficients).count(0)
    if support != instance.k:
        errors.append(f"support is {support}, expected {instance.k}")

    digit_table = [_digits(i, instance.group) for i in range(instance.v)]
    correlations = []
    for shift_index in range(instance.v):
        shift = digit_table[shift_index]
        total = 0
        for left_index in range(instance.v):
            left = digit_table[left_index]
            right = [
                (left[j] - shift[j]) % instance.group[j]
                for j in range(len(instance.group))
            ]
            total += coefficients[left_index] * coefficients[_rank(right, instance.group)]
        correlations.append(total)

    mismatches = {
        str(i): value
        for i, value in enumerate(correlations)
        if value != (instance.k if i == 0 else instance.lam)
    }
    if mismatches:
        errors.append(f"autocorrelation mismatch at {len(mismatches)} shifts")
    return {
        "valid": not errors,
        "validator": "independent_mixed_radix_v1",
        "support": support,
        "coefficient_sum": sum(coefficients),
        "autocorrelation": correlations,
        "mismatches": mismatches,
        "errors": errors,
    }

