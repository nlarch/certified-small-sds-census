"""Parsing and witness conversion for the frozen La Jolla data format."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from itertools import chain, product
from typing import Iterable, Sequence, Tuple


NAME_RE = re.compile(
    r"^SDS\((?P<v>-?\d+),(?P<k>-?\d+),(?P<lam>-?\d+),"
    r"\[(?P<group>\d+(?:,\d+)*)\]\)$"
)


@dataclass(frozen=True)
class Instance:
    name: str
    v: int
    k: int
    lam: int
    group: Tuple[int, ...]


def parse_name(name: str) -> Instance:
    match = NAME_RE.fullmatch(name)
    if match is None:
        raise ValueError(f"unrecognized SDS name: {name!r}")
    group = tuple(int(x) for x in match.group("group").split(","))
    instance = Instance(
        name=name,
        v=int(match.group("v")),
        k=int(match.group("k")),
        lam=int(match.group("lam")),
        group=group,
    )
    if math.prod(group) != instance.v:
        raise ValueError(f"group order mismatch in {name}")
    return instance


def elements(group: Sequence[int]) -> Tuple[Tuple[int, ...], ...]:
    """Lexicographic elements of the direct product of cyclic factors."""
    return tuple(product(*(range(modulus) for modulus in group)))


def witness_from_record(
    instance: Instance, positive: Iterable[object], negative: Iterable[object]
) -> Tuple[int, ...]:
    """Convert the repository's P/N representation to a coefficient vector."""
    elts = elements(instance.group)
    index = {element: i for i, element in enumerate(elts)}
    coeffs = [0] * instance.v

    def normalize(value: object) -> Tuple[int, ...]:
        if len(instance.group) == 1:
            if not isinstance(value, int):
                raise ValueError(f"expected an integer cyclic-group element: {value!r}")
            return (value % instance.group[0],)
        if not isinstance(value, list) or len(value) != len(instance.group):
            raise ValueError(f"expected {len(instance.group)} coordinates: {value!r}")
        return tuple(int(x) % modulus for x, modulus in zip(value, instance.group))

    signed_elements = chain(((x, 1) for x in positive), ((x, -1) for x in negative))
    for value, coefficient in signed_elements:
        element = normalize(value)
        position = index[element]
        if coeffs[position] != 0:
            raise ValueError(f"duplicate repository element {value!r}")
        coeffs[position] = coefficient
    return tuple(coeffs)
