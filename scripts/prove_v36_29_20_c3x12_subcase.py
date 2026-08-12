#!/usr/bin/env python3
"""Proof-producing normalized quotient subcase for SDS(36,29,20,[3,12])."""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sds.model import parse_name  # noqa: E402
from sds.sat_encoding import encode  # noqa: E402

INSTANCE = parse_name("SDS(36,29,20,[3,12])")
REAL_PATTERN = (12, 15)
ORDER3_PATTERNS = ((7, 10, 10), (8, 8, 11))
CHECKER = ROOT / "tools" / "drat-trim-src" / "drat-trim"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_signed_sum(encoded, cell, required_sum, top):
    literals = [encoded.positive_variables[g] for g in cell]
    literals += [-encoded.negative_variables[g] for g in cell]
    constraint = CardEnc.equals(
        literals,
        required_sum + len(cell),
        top_id=top,
        encoding=EncType.totalizer,
    )
    encoded.cnf.extend(constraint.clauses)
    return constraint.nv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orbit-index", type=int, choices=range(2), required=True)
    args = parser.parse_args()
    order3_pattern = ORDER3_PATTERNS[args.orbit_index]

    encoded = encode(INSTANCE, "totalizer")
    # The quotient patterns themselves normalize all translations: retaining
    # negative(identity) would discard valid members of a normalized orbit.
    translation_clause = [encoded.negative_variables[0]]
    assert encoded.cnf.clauses.count(translation_clause) == 1
    encoded.cnf.clauses.remove(translation_clause)

    parity_cells = [[], []]
    order3_cells = [[], [], []]
    for g in range(INSTANCE.v):
        first, second = divmod(g, 12)
        parity_cells[second % 2].append(g)
        order3_cells[first].append(g)

    top = encoded.cnf.nv
    for cells, pattern in ((parity_cells, REAL_PATTERN), (order3_cells, order3_pattern)):
        for cell, required_sum in zip(cells, pattern):
            top = add_signed_sum(encoded, cell, required_sum, top)

    directory = ROOT / "artifacts" / "sat" / "v36_29_20_c3x12_subcases"
    directory.mkdir(parents=True, exist_ok=True)
    stem = directory / f"orbit_{args.orbit_index}"
    formula = stem.with_suffix(".cnf")
    proof = stem.with_suffix(".drat")
    checker_output = stem.with_suffix(".check.txt")
    report = stem.with_suffix(".json")
    encoded.cnf.to_file(
        str(formula),
        comments=[
            f"c instance {INSTANCE.name}",
            "c translation normalized by independent C2 and C3 quotient patterns",
            f"c parity pattern {REAL_PATTERN}",
            f"c order-three pattern {order3_pattern}",
            "c exact totalizer full-autocorrelation encoding",
        ],
    )

    started = time.perf_counter()
    with Solver(name="glucose4", bootstrap_with=encoded.cnf.clauses, with_proof=True) as solver:
        answer = solver.solve()
        stats = solver.accum_stats()
        trace = None if answer else solver.get_proof()
    solve_seconds = time.perf_counter() - started
    if answer:
        raise SystemExit("unexpected SAT result")
    proof.write_text("\n".join(trace) + "\n")

    checked = subprocess.run(
        [str(CHECKER), str(formula), str(proof), "-f"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    checker_output.write_text(checked.stdout)
    verified = checked.returncode == 0 and "s VERIFIED" in checked.stdout
    if not verified:
        raise SystemExit("independent DRAT check failed")

    document = {
        "schema": "v36-29-20-c3x12-subcase-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": INSTANCE.name,
        "orbit_index": args.orbit_index,
        "real_pattern": REAL_PATTERN,
        "order3_pattern": order3_pattern,
        "all_order3_orbit_representatives": ORDER3_PATTERNS,
        "translation_fixed_negative_identity": False,
        "translation_normalized_by_quotient_patterns": True,
        "result": "UNSAT",
        "solve_seconds": solve_seconds,
        "solver_stats": stats,
        "formula": {
            "path": str(formula.relative_to(ROOT)),
            "sha256": sha256(formula),
            "variables": encoded.cnf.nv,
            "clauses": len(encoded.cnf.clauses),
        },
        "proof": {
            "path": str(proof.relative_to(ROOT)),
            "sha256": sha256(proof),
            "bytes": proof.stat().st_size,
        },
        "checker": {
            "verified": verified,
            "source_commit": subprocess.check_output(
                ["git", "-C", str(CHECKER.parent), "rev-parse", "HEAD"], text=True
            ).strip(),
            "binary_sha256": sha256(CHECKER),
            "output_path": str(checker_output.relative_to(ROOT)),
            "output_sha256": sha256(checker_output),
        },
    }
    report.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "orbit": args.orbit_index,
                "seconds": solve_seconds,
                "proof_bytes": proof.stat().st_size,
                "verified": verified,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
