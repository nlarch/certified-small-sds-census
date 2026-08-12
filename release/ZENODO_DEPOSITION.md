# Zenodo deposition checklist for v1.0 proof traces

No upload has been performed by this file or by the release-preparation
scripts. Complete these steps only after the final local audit has passed and
the author has approved the public metadata.

## File to deposit

Build with:

```sh
python3 scripts/build_trace_archive.py
```

Upload `dist/certified-small-sds-drat-traces-v1.0.tar.gz`. Copy the exact size
and SHA-256 from `dist/certified-small-sds-drat-traces-v1.0.tar.gz.json` into
the deposition description. The archive contains all 241 files under
`artifacts/sat/`, including 70 CNF formulas, 57 DRAT proofs, 57 proof metadata
records, and 57 checker-output files. Exactly 57 formula/proof pairs are
accepted by the final census; the remaining formulas are retained for complete
research provenance.

## Proposed metadata

- Upload type: Dataset
- Title: Certified Small Signed Difference Sets: CNF and DRAT Proof Archive
- Version: 1.0
- Publication date: use the actual deposition date
- Creator: Nicolas Masselot
- Description: Exact DIMACS formulas, DRAT certificates, proof metadata, and
  checker outputs supporting the nonexistence results in the Certified Census
  of Small Signed Difference Sets, frozen against the April 24, 2026 La Jolla
  repository snapshot.
- License: CC BY 4.0 for project-authored data; retain and describe the
  original licenses for bundled third-party metadata if any.
- Related identifier: the GitHub v1.0 release URL, relation `is supplement to`
- Keywords: signed difference sets; combinatorial designs; SAT; DRAT;
  computer-assisted proof

## After Zenodo reserves a DOI

Before publishing the deposition:

1. Insert the reserved DOI and record URL in `CITATION.cff`, the paper's data
   availability section, and the lightweight package README.
2. Re-render and visually inspect the PDF.
3. Rebuild both archives so their manifests cover the DOI-bearing files.
4. Re-run `python3 verify_package.py` in an unpacked lightweight archive.
5. Verify the uploaded archive size and SHA-256 against the local record.
6. Publish the Zenodo record only after that comparison passes.

Do not claim the DOI before Zenodo has actually reserved it, and do not reuse
a sandbox DOI in production metadata.
