# Publication checklist

This checklist preserves the intended order of operations. Items involving a
public service or a third party require an explicit final approval immediately
before execution.

## Local preparation

- [x] Put the two classification theorems before the 68-case census in the
  README.
- [x] Draft and render the English 8-12 page note.
- [x] Finish and retain the clean-environment audit of all 57 DRAT proofs.
- [x] Build and verify the lightweight article/witness/validator/quotient
  package.
- [x] Build the separate trace archive and record its file-level and archive
  hashes.
- [x] Add `LICENSE`, `CITATION.cff`, and a precise AI-use statement.
- [x] Prepare Zenodo metadata and post-deposition update steps.
- [x] Create the local `main` branch for the publication-preparation commit.

## Archival and repository release

- [x] Reserve Zenodo DOI `10.5281/zenodo.21901581` for the trace dataset.
- [x] Add the reserved DOI and record URL to the paper, `CITATION.cff`, and
  package README; rebuild and re-verify both archives.
- [x] Upload the trace archive, compare its size and SHA-256, then publish the
  Zenodo record.
- [ ] Commit the final DOI-bearing release state on a `main` branch.
- [ ] Create and push tag `v1.0` and publish a GitHub release with the
  lightweight package as an asset.
- [ ] Make the repository public, or grant explicit access to named reviewers,
  and verify the link from a signed-out browser.

## Review and publication

- [ ] Send the prepared private-review message to Arévalo and Gordon only
  after they can access the materials.
- [ ] Record corrections and reviewer feedback; issue a maintenance release if
  any artifact or statement changes.
- [ ] Submit the revised manuscript to arXiv with primary category `math.CO`.
- [ ] Submit to an appropriate peer-reviewed combinatorics/design-theory
  journal after the external review pass.
