#!/usr/bin/env python3
"""Create the separately depositable CNF/DRAT archive and file manifest."""

from __future__ import annotations

import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "sat"
DIST = ROOT / "dist"
ARCHIVE_NAME = "certified-small-sds-drat-traces-v1.0.tar.gz"
MANIFEST_PATH = ROOT / "artifacts" / "manifests" / "trace_archive_manifest_v1.0.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    files = sorted(path for path in SOURCE.rglob("*") if path.is_file())
    records = [
        {
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    manifest = {
        "schema": "certified-small-sds-trace-archive-manifest-v1",
        "version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_directory": "artifacts/sat",
        "file_count": len(records),
        "total_uncompressed_bytes": sum(item["bytes"] for item in records),
        "accepted_drat_proof_pairs": 57,
        "files": records,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    DIST.mkdir(exist_ok=True)
    archive = DIST / ARCHIVE_NAME
    if archive.exists():
        archive.unlink()
    with tarfile.open(archive, "w:gz", compresslevel=6, format=tarfile.PAX_FORMAT) as output:
        output.add(SOURCE, arcname="artifacts/sat")
        output.add(MANIFEST_PATH, arcname=str(MANIFEST_PATH.relative_to(ROOT)))
    archive_record = {
        "archive": archive.name,
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256(archive),
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "manifest_sha256": sha256(MANIFEST_PATH),
    }
    record_text = json.dumps(archive_record, indent=2, sort_keys=True) + "\n"
    (DIST / f"{ARCHIVE_NAME}.json").write_text(record_text)
    (MANIFEST_PATH.parent / "trace_archive_v1.0.json").write_text(record_text)
    print(json.dumps(archive_record, indent=2))


if __name__ == "__main__":
    main()
