#!/usr/bin/env python3
"""Cross-check two CNF encodings and search the two order-24 targets."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402
from sds.sat_encoding import decode, encode  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402

BASELINE_CASES = (
    ("SDS(5,4,-1,[5])", "SAT"),
    ("SDS(9,8,-1,[3,3])", "SAT"),
    ("SDS(9,8,1,[9])", "UNSAT"),
    ("SDS(9,8,1,[3,3])", "UNSAT"),
)
V24_CASES = (
    ("SDS(24,18,2,[2,12])", None),
    ("SDS(24,18,2,[2,2,6])", None),
)
ENCODINGS = ("seqcounter", "totalizer")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug(name: str) -> str:
    return name.replace("SDS(", "sds_").replace(",", "_").replace("[", "").replace("]", "").replace(")", "")


def run_case(name: str, expected: str, encoding_name: str, formula_dir: Path) -> dict:
    instance = parse_name(name)
    started = time.perf_counter()
    encoded = encode(instance, encoding_name)
    formula_path = formula_dir / f"{slug(name)}_{encoding_name}.cnf"
    encoded.cnf.to_file(str(formula_path), comments=[
        f"c instance {name}",
        f"c cardinality encoding {encoding_name}",
        "c p_g/n_g are exclusive; exact counts fix support and nonnegative augmentation sign",
        "c negative coefficient at identity is fixed by translation symmetry",
        "c AND auxiliaries are encoded by three clauses each (full equivalence)",
        "c each nonidentity equation is sum(same)+sum(not cross)=lambda+2v",
    ])
    build_seconds = time.perf_counter() - started
    solve_started = time.perf_counter()
    with Solver(name="cadical195", bootstrap_with=encoded.cnf.clauses) as solver:
        satisfiable = solver.solve()
        model = solver.get_model() if satisfiable else None
        stats = solver.accum_stats()
    solve_seconds = time.perf_counter() - solve_started
    result = "SAT" if satisfiable else "UNSAT"
    if expected is not None and result != expected:
        raise AssertionError(f"{name} with {encoding_name}: expected {expected}, got {result}")
    validation = None
    if model is not None:
        vector = decode(encoded, model)
        validation = {
            "coefficient_vector": vector,
            "reference": validate_reference(instance, vector),
            "independent": validate_independent(instance, vector),
        }
        assert validation["reference"]["valid"] and validation["independent"]["valid"]
    return {
        "instance": name,
        "encoding": encoding_name,
        "expected_from_independent_baseline": expected,
        "solver": "cadical195 via python-sat 1.9.dev13",
        "result": result,
        "proof_status": "NOT_REQUESTED" if satisfiable else "UNSAT_UNCERTIFIED",
        "encoding_metadata": encoded.metadata,
        "formula_path": str(formula_path.relative_to(ROOT)),
        "formula_sha256": sha256(formula_path),
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "solver_stats": stats,
        "validation": validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "sat_campaign.json",
    )
    parser.add_argument("--scope", choices=("baseline", "v24", "all"), default="all")
    parser.add_argument("--encoding", choices=("seqcounter", "totalizer", "both"), default="both")
    args = parser.parse_args()
    formula_dir = ROOT / "artifacts" / "sat"
    formula_dir.mkdir(parents=True, exist_ok=True)
    selected_cases = BASELINE_CASES if args.scope == "baseline" else V24_CASES if args.scope == "v24" else BASELINE_CASES + V24_CASES
    selected_encodings = ENCODINGS if args.encoding == "both" else (args.encoding,)
    cases = []
    for name, expected in selected_cases:
        for encoding_name in selected_encodings:
            print(f"running {name} {encoding_name}", flush=True)
            cases.append(run_case(name, expected, encoding_name, formula_dir))
            print(f"finished {name} {encoding_name}: {cases[-1]['result']} in {cases[-1]['solve_seconds']:.3f}s", flush=True)
    report = {
        "schema": "signed-difference-set-sat-campaign-v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": f".venv/bin/python scripts/run_sat_campaign.py --scope {args.scope} --encoding {args.encoding} --output {args.output}",
        "encoding_correctness_argument": [
            "Exclusive p_g and n_g variables encode coefficients in {0,+1,-1}; exact p/n counts enforce support and the chosen augmentation sign.",
            "Each product auxiliary is equivalent to its two input literals by all three Tseitin clauses.",
            "For every nonidentity shift, the signed autocorrelation is same-sign products minus cross-sign products.",
            "With exactly 2v cross-product occurrences, equality to lambda is equivalent to the unweighted cardinality equality sum(same)+sum(not cross)=lambda+2v.",
            "The identity equation follows from coefficient exclusivity and exact support.",
            "Global sign selects nonnegative augmentation, and translation moves a negative coefficient to identity; both preserve the full defining equation."
        ],
        "cases": cases,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "warning": "An UNSAT result in this report is not accepted as nonexistence unless a separately preserved proof passes an independent checker."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
