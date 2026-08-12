#!/usr/bin/env python3
"""Proof-producing unique normalized quotient case for SDS(36,29,4,[6,6])."""

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

INSTANCE = parse_name("SDS(36,29,4,[6,6])")
REAL_PATTERN = (7, 2, 2, 2)
ORDER3_PATTERN = (-3, 2, 2, 2, 2, 2, 2, 2, 2)
CHECKER = ROOT / "tools" / "drat-trim-src" / "drat-trim"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_sum(encoded, cell, required, top):
    literals = [encoded.positive_variables[g] for g in cell]
    literals += [-encoded.negative_variables[g] for g in cell]
    constraint = CardEnc.equals(
        literals, required + len(cell), top_id=top, encoding=EncType.totalizer
    )
    encoded.cnf.extend(constraint.clauses)
    return constraint.nv


def main() -> None:
    encoded = encode(INSTANCE, "totalizer")
    clause = [encoded.negative_variables[0]]
    assert encoded.cnf.clauses.count(clause) == 1
    encoded.cnf.clauses.remove(clause)
    real_cells = [[] for _ in range(4)]
    order3_cells = [[] for _ in range(9)]
    for g in range(36):
        first, second = divmod(g, 6)
        real_cells[2 * (first % 2) + second % 2].append(g)
        order3_cells[3 * (first % 3) + second % 3].append(g)
    top = encoded.cnf.nv
    for cells, pattern in ((real_cells, REAL_PATTERN), (order3_cells, ORDER3_PATTERN)):
        for cell, required in zip(cells, pattern):
            top = add_sum(encoded, cell, required, top)

    directory = ROOT / "artifacts" / "sat" / "v36_29_4_c6x6"
    directory.mkdir(parents=True, exist_ok=True)
    formula = directory / "normalized.cnf"
    proof = directory / "normalized.drat"
    checker_output = directory / "normalized.check.txt"
    report = directory / "normalized.json"
    encoded.cnf.to_file(
        str(formula),
        comments=[
            f"c instance {INSTANCE.name}",
            f"c real pattern {REAL_PATTERN}",
            f"c full C3^2 pattern {ORDER3_PATTERN}",
            "c translation normalized independently through C2^2 and C3^2",
        ],
    )
    started = time.perf_counter()
    with Solver(name="glucose4", bootstrap_with=encoded.cnf.clauses, with_proof=True) as solver:
        answer = solver.solve()
        stats = solver.accum_stats()
        trace = None if answer else solver.get_proof()
    seconds = time.perf_counter() - started
    if answer:
        raise SystemExit("unexpected SAT")
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
        raise SystemExit("checker failed")
    document = {
        "schema": "v36-29-4-c6x6-normalized-proof-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": INSTANCE.name,
        "result": "UNSAT",
        "real_pattern": REAL_PATTERN,
        "order3_pattern": ORDER3_PATTERN,
        "translation_fixed_negative_identity": False,
        "solve_seconds": seconds,
        "solver_stats": stats,
        "formula": {"path": str(formula.relative_to(ROOT)), "sha256": sha256(formula), "variables": encoded.cnf.nv, "clauses": len(encoded.cnf.clauses)},
        "proof": {"path": str(proof.relative_to(ROOT)), "sha256": sha256(proof), "bytes": proof.stat().st_size},
        "checker": {
            "verified": verified,
            "source_commit": subprocess.check_output(["git", "-C", str(CHECKER.parent), "rev-parse", "HEAD"], text=True).strip(),
            "binary_sha256": sha256(CHECKER),
            "output_path": str(checker_output.relative_to(ROOT)),
            "output_sha256": sha256(checker_output),
        },
    }
    report.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"seconds": seconds, "proof_bytes": proof.stat().st_size, "verified": verified}, indent=2))


if __name__ == "__main__":
    main()
