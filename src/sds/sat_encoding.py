"""Auditable CNF encoding of signed difference sets using PySAT."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

from .model import Instance


ENCODINGS = {
    "seqcounter": EncType.seqcounter,
    "totalizer": EncType.totalizer,
}


def _digits(index: int, moduli: Sequence[int]) -> List[int]:
    result = [0] * len(moduli)
    for j in range(len(moduli) - 1, -1, -1):
        result[j] = index % moduli[j]
        index //= moduli[j]
    return result


def _rank(row: Sequence[int], moduli: Sequence[int]) -> int:
    value = 0
    for digit, modulus in zip(row, moduli):
        value = value * modulus + digit
    return value


def subtraction_table(instance: Instance) -> List[List[int]]:
    rows = [_digits(i, instance.group) for i in range(instance.v)]
    return [
        [
            _rank(
                [(rows[left][j] - rows[shift][j]) % instance.group[j] for j in range(len(instance.group))],
                instance.group,
            )
            for left in range(instance.v)
        ]
        for shift in range(instance.v)
    ]


@dataclass
class EncodedInstance:
    cnf: CNF
    positive_variables: Tuple[int, ...]
    negative_variables: Tuple[int, ...]
    positive_count: int
    negative_count: int
    metadata: Dict[str, object]


def encode(instance: Instance, encoding_name: str = "seqcounter") -> EncodedInstance:
    if encoding_name not in ENCODINGS:
        raise ValueError(f"unknown cardinality encoding {encoding_name!r}")
    augmentation_square = instance.k + instance.lam * (instance.v - 1)
    augmentation = int(augmentation_square**0.5)
    if augmentation * augmentation != augmentation_square:
        raise ValueError("trivial-character square is not a square")
    if (instance.k + augmentation) % 2:
        raise ValueError("support and augmentation parities disagree")
    positive_count = (instance.k + augmentation) // 2
    negative_count = (instance.k - augmentation) // 2
    if negative_count <= 0:
        raise ValueError("translation fixing requires at least one negative coefficient")

    vpool = IDPool()
    positive = tuple(vpool.id(("positive", g)) for g in range(instance.v))
    negative = tuple(vpool.id(("negative", g)) for g in range(instance.v))
    cnf = CNF()

    # Coefficient domain: at most one of positive and negative at each element.
    for g in range(instance.v):
        cnf.append([-positive[g], -negative[g]])
    card_encoding = ENCODINGS[encoding_name]
    cnf.extend(CardEnc.equals(positive, positive_count, vpool=vpool, encoding=card_encoding).clauses)
    cnf.extend(CardEnc.equals(negative, negative_count, vpool=vpool, encoding=card_encoding).clauses)

    # Translation symmetry: every candidate has a negative element; translate
    # one such element to the identity. D D^-1 is translation invariant.
    cnf.append([negative[0]])

    subtraction = subtraction_table(instance)
    product_variables = 0

    def conjunction(left: int, right: int) -> int:
        nonlocal product_variables
        output = vpool.id()
        product_variables += 1
        # output iff (left and right), not merely output => conjunction.
        cnf.append([-output, left])
        cnf.append([-output, right])
        cnf.append([output, -left, -right])
        return output

    for shift in range(1, instance.v):
        same_sign = []
        cross_sign = []
        for g in range(instance.v):
            right = subtraction[shift][g]
            same_sign.append(conjunction(positive[g], positive[right]))
            same_sign.append(conjunction(negative[g], negative[right]))
            cross_sign.append(conjunction(positive[g], negative[right]))
            cross_sign.append(conjunction(negative[g], positive[right]))
        # sum(same)-sum(cross)=lambda iff
        # sum(same)+sum(not cross)=lambda+len(cross).
        literals = same_sign + [-variable for variable in cross_sign]
        bound = instance.lam + len(cross_sign)
        cnf.extend(CardEnc.equals(literals, bound, vpool=vpool, encoding=card_encoding).clauses)

    return EncodedInstance(
        cnf=cnf,
        positive_variables=positive,
        negative_variables=negative,
        positive_count=positive_count,
        negative_count=negative_count,
        metadata={
            "encoding": encoding_name,
            "variables": vpool.top,
            "clauses": len(cnf.clauses),
            "product_variables": product_variables,
            "translation_fixed_negative_identity": True,
            "augmentation_sign_normalized_nonnegative": True,
        },
    )


def decode(encoded: EncodedInstance, model: Sequence[int]) -> Tuple[int, ...]:
    true_variables = {literal for literal in model if literal > 0}
    return tuple(
        1 if encoded.positive_variables[g] in true_variables else -1 if encoded.negative_variables[g] in true_variables else 0
        for g in range(len(encoded.positive_variables))
    )

