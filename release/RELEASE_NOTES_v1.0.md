# Certified Census of Small Signed Difference Sets v1.0

Version 1.0 freezes the complete decision and verification package for every
entry of group order at most 36 marked `Open` in La Jolla repository commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e`.

## Main mathematical results

- A signed `(32,20,4)` difference set exists in an abelian group of order 32
  if and only if the group is noncyclic.
- No signed `(36,29,4)` difference set exists in `C2 x C18`, `C3 x C12`, or
  `C6 x C6`. Together with the earlier cyclic result, this closes all abelian
  groups of order 36 for those parameters.

## Complete census

- 68 of 68 frozen targets resolved;
- 16 explicit existence witnesses;
- 52 certified nonexistence decisions;
- 57 accepted CNF/DRAT proof pairs, all rechecked in a clean pinned Debian
  environment;
- three independently regenerating quotient-verification programs.

The 10-page English note, all witnesses, validators, compact quotient
artifacts, audit reports, licensing metadata, and the AI-use statement are in
the repository and lightweight release assets.

The 242.2 MB deterministic CNF/DRAT archive is published separately at Zenodo:
[doi:10.5281/zenodo.21901581](https://doi.org/10.5281/zenodo.21901581).

Trace archive SHA-256:
`d982b6b5c62b49588e772563ef53161084425ae89b1812672910bf05f1479231`.

OpenAI Codex was used extensively for computational research, implementation,
artifact organization, and drafting. No model output is accepted as
mathematical evidence; see `AI_USE.md` for the exact verification boundary.
