#!/usr/bin/env python3
"""Assemble the v1.0 lightweight verification package and archives."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_NAME = "certified-small-sds-v1.0-lightweight"
PACKAGE = DIST / PACKAGE_NAME

FILES = [
    "LICENSE",
    "CITATION.cff",
    "AI_USE.md",
    "paper/two_small_order_classifications.md",
    "output/pdf/two_small_order_classifications.pdf",
    "artifacts/census/current_census.json",
    "artifacts/audit/final_audit.json",
    "artifacts/audit/drat_clean_environment_2026-08-12.json",
    "artifacts/audit/drat_clean_environment_2026-08-12.log",
    "artifacts/manifests/trace_archive_manifest_v1.0.json",
    "artifacts/manifests/trace_archive_v1.0.json",
    "artifacts/runs/v27_remaining_quotient_exhaustion.json",
    "artifacts/runs/v32_remaining_quotient_exhaustion.json",
    "artifacts/runs/v36_29_4_combined_quotient_exhaustion.json",
    "artifacts/runs/v36_29_4_c6x6_certified_sat.json",
    "scripts/verify_v27_remaining_quotients.py",
    "scripts/verify_v32_remaining_quotients.py",
    "scripts/verify_v36_29_4_combined_quotients.py",
    "src/sds/__init__.py",
    "src/sds/model.py",
    "src/sds/validator_reference.py",
    "src/sds/validator_independent.py",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    DIST.mkdir(exist_ok=True)
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir()

    for relative in FILES:
        source = ROOT / relative
        if not source.is_file():
            raise RuntimeError(f"missing release input: {relative}")
        destination = (
            PACKAGE / "paper" / source.name
            if relative == "output/pdf/two_small_order_classifications.pdf"
            else PACKAGE / relative
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    for source in sorted((ROOT / "artifacts/witnesses").glob("*.json")):
        destination = PACKAGE / "artifacts" / "witnesses" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    shutil.copy2(ROOT / "release/README_lightweight.md", PACKAGE / "README.md")
    shutil.copy2(ROOT / "release/verify_package.py", PACKAGE / "verify_package.py")

    payload = sorted(path for path in PACKAGE.rglob("*") if path.is_file())
    sums = "".join(f"{digest(path)}  {path.relative_to(PACKAGE)}\n" for path in payload)
    (PACKAGE / "SHA256SUMS").write_text(sums)

    tar_path = DIST / f"{PACKAGE_NAME}.tar.gz"
    zip_path = DIST / f"{PACKAGE_NAME}.zip"
    for path in (tar_path, zip_path):
        if path.exists():
            path.unlink()
    with tarfile.open(tar_path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        archive.add(PACKAGE, arcname=PACKAGE_NAME)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, Path(PACKAGE_NAME) / path.relative_to(PACKAGE))

    archive_sums = DIST / f"{PACKAGE_NAME}.SHA256SUMS"
    archive_sums.write_text(
        f"{digest(tar_path)}  {tar_path.name}\n{digest(zip_path)}  {zip_path.name}\n"
    )
    release_record = {
        "schema": "certified-small-sds-lightweight-release-manifest-v1",
        "version": "1.0",
        "payload_file_count": len(payload),
        "tar_gz": {
            "path": tar_path.name,
            "bytes": tar_path.stat().st_size,
            "sha256": digest(tar_path),
        },
        "zip": {
            "path": zip_path.name,
            "bytes": zip_path.stat().st_size,
            "sha256": digest(zip_path),
        },
    }
    release_manifest = ROOT / "artifacts/manifests/lightweight_release_manifest_v1.0.json"
    release_manifest.parent.mkdir(parents=True, exist_ok=True)
    release_manifest.write_text(json.dumps(release_record, indent=2, sort_keys=True) + "\n")
    print(PACKAGE)
    print(tar_path, digest(tar_path))
    print(zip_path, digest(zip_path))


if __name__ == "__main__":
    main()
