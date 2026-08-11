"""Deliberately simple tuple/dictionary reference validator."""

from __future__ import annotations

from typing import Dict, Sequence, Tuple

from .model import Instance, elements


def validate(instance: Instance, coefficients: Sequence[int]) -> Dict[str, object]:
    elts = elements(instance.group)
    errors = []
    if len(coefficients) != instance.v:
        return {"valid": False, "errors": ["coefficient vector length mismatch"]}
    if any(value not in (-1, 0, 1) for value in coefficients):
        errors.append("coefficient outside {0,+1,-1}")
    support = sum(value != 0 for value in coefficients)
    if support != instance.k:
        errors.append(f"support is {support}, expected {instance.k}")

    by_element = dict(zip(elts, coefficients))
    autocorrelation: Dict[Tuple[int, ...], int] = {}
    for shift in elts:
        total = 0
        for group_element in elts:
            shifted = tuple(
                (coordinate - displacement) % modulus
                for coordinate, displacement, modulus in zip(
                    group_element, shift, instance.group
                )
            )
            total += by_element[group_element] * by_element[shifted]
        autocorrelation[shift] = total

    identity = (0,) * len(instance.group)
    bad = {
        str(shift): value
        for shift, value in autocorrelation.items()
        if value != (instance.k if shift == identity else instance.lam)
    }
    if bad:
        errors.append(f"autocorrelation mismatch at {len(bad)} shifts")
    return {
        "valid": not errors,
        "validator": "reference_tuple_dictionary_v1",
        "support": support,
        "coefficient_sum": sum(coefficients),
        "autocorrelation": [autocorrelation[element] for element in elts],
        "mismatches": bad,
        "errors": errors,
    }

