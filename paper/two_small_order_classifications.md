# Two Small-Order Classification Theorems for Signed Difference Sets

Nicolas Masselot  
August 12, 2026

## Abstract

A signed difference set assigns coefficients in `{0,+1,-1}` to a finite
group so that every nonidentity periodic autocorrelation has the same value.
We settle two clusters of cases that were marked Open in the April 24, 2026
snapshot of the La Jolla Signed Difference Set Repository. First, a signed
`(32,20,4)` difference set exists in an abelian group of order 32 exactly when
the group is noncyclic. The six positive cases are represented by explicit
coefficient vectors checked by two structurally independent validators; the
cyclic case is excluded by a complete `C8 -> C16 -> C32` quotient refinement.
Second, no signed `(36,29,4)` difference set exists in any of the three
noncyclic abelian groups `C2 x C18`, `C3 x C12`, and `C6 x C6`. Two cases are
settled by transparent quotient enumeration. In the last case quotient
constraints reduce the problem to one normalized orbit, whose CNF encoding is
proved unsatisfiable by a checked DRAT certificate. Together with the cyclic
nonexistence already recorded in the frozen repository, this closes the
abelian order-36 parameter set. All statements are tied to executable
validators, exact hashes, and independently checkable artifacts.

**Keywords:** signed difference set; finite abelian group; autocorrelation;
quotient enumeration; SAT certificate; DRAT.

## Main statements

**Theorem 1.** Let `G` be an abelian group of order 32. A signed
`(32,20,4)` difference set exists in `G` if and only if `G` is noncyclic.

**Theorem 2.** No signed `(36,29,4)` difference set exists in any of
`C2 x C18`, `C3 x C12`, or `C6 x C6`.

**Corollary.** Combining Theorem 2 with the earlier cyclic `C36`
nonexistence recorded in the frozen repository, no abelian group of order 36
admits a signed `(36,29,4)` difference set.

The theorem statements are the focus of this note. The larger 68-entry census
from which they emerged is discussed only after their proofs and certificates.

<!-- pagebreak -->

## 1. Signed difference sets in elementary terms

Let `G` be a finite group of order `v`, written multiplicatively with identity
`e`. A signed subset is a group-ring element

```text
D = sum_{g in G} a_g g,             a_g in {0,+1,-1}.
```

Its support has size `k` when exactly `k` coefficients are nonzero. Following
Gordon [1], `D` is a signed `(v,k,lambda)` difference set when

```text
D D^(-1) = (k-lambda)e + lambda G.                 (1)
```

For a reader unfamiliar with group rings, equation (1) is simply a periodic
correlation condition. For each shift `h in G`, form

```text
C(h) = sum_{g in G} a_g a_(h^(-1)g).
```

Then `C(e)=k` automatically, and the defining demand is `C(h)=lambda` for
every `h != e`. One may picture a cyclic group as points on a wrap-around
circle and a direct product of cyclic groups as a wrap-around grid. The signs
are arranged so that the pattern has exactly the same correlation with each
of its nontrivial translates.

Two elementary consequences provide strong arithmetic filters. Applying the
trivial character to (1) gives

```text
(sum_g a_g)^2 = k + (v-1)lambda.                   (2)
```

For every nontrivial complex character `chi`, one obtains

```text
|sum_g a_g chi(g)|^2 = k-lambda.                  (3)
```

For `(32,20,4)`, equation (2) gives coefficient sum `+/-12`. After a global
sign change we take the sum to be 12, so every solution has 16 positive and 4
negative coefficients. For `(36,29,4)`, the corresponding sum is `+/-13`,
and the positive normalization has 21 positive and 8 negative coefficients.
The nontrivial character magnitudes are respectively 4 and 5.

The invariant-factor notation `[2,16]`, used by the source repository, means
`C2 x C16`. The group description is essential: groups having the same order
and the same numerical parameters can have different answers, as Theorem 1
shows.

The frozen baseline is commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e` of [2], dated April 24, 2026.
The target of this note is not a moving web page but the exact named entries
in that snapshot.

<!-- pagebreak -->

## 2. What counts as a computational proof

The distinction between search and proof is central. A heuristic that fails
to find a vector says nothing about nonexistence, and a SAT solver printing
`UNSAT` is not by itself a durable mathematical certificate. We therefore use
different acceptance boundaries for positive and negative results.

For an existence result, the artifact is the full coefficient vector in the
repository's lexicographic direct-product coordinate order. A deliberately
simple reference validator constructs all group elements as tuples, performs
componentwise addition, and recomputes every correlation. A separate
validator represents elements by mixed-radix integers and uses different
indexing and group-operation code. Both verify the coefficient domain,
support, coefficient sum, and all `v` correlations in unsymmetrized
coordinates. A witness is accepted only when both validators agree.

For a nonexistence result, we use one of two routes. A quotient enumeration is
acceptable when its finite search space, arithmetic constraints, symmetry
normalizations, and final refinements can be reconstructed by a short
independent program. A solver-based result must preserve the exact DIMACS
formula, the variable mapping implicit in the generator, the DRAT proof, the
checker source commit, the checker output, and cryptographic hashes. The proof
is accepted only if an independently compiled checker reports `s VERIFIED`.

The certificate chain is therefore:

```text
mathematical instance
  -> exact reduction or encoding
  -> finite enumeration or CNF formula
  -> explicit witness or DRAT proof
  -> independent full-coordinate validator or proof checker.
```

Symmetry is used only to make a search smaller. Translation, global sign,
inversion, and selected automorphisms do not replace the final defining
equation. Every positive answer is checked after all normalizations have been
forgotten. Every negative symmetry quotient is accompanied by an argument
that the action lifts through the next refinement stage.

All accepted files are addressed by SHA-256. The canonical census itself has
hash
`11cd6bed9b7dcc1c23c66257f0765f2827c8aaefaf944ae4977bf6073cf08d9f`.
This makes accidental or selective modification detectable, but hashing is
not a substitute for semantic checking: the supplied programs also recompute
the mathematics.

<!-- pagebreak -->

## 3. The quotient projection lemma

The main reduction used in both theorems is elementary. Let `K` be a normal
subgroup of `G`, let `Q=G/K`, and project `D` to

```text
B = sum_{q in Q} b_q q,       b_q = sum_{g in q} a_g.
```

If `|K|=m`, summing equation (1) over the shifts in each fiber gives

```text
coefficient of e_Q in B B^(-1) = k + (m-1)lambda,
coefficient of q != e_Q        = m lambda.          (4)
```

Each `b_q` is an integer between `-m` and `m`, with parity and support
restrictions determined by its fiber. Thus a large ternary search is replaced
by a much smaller search over bounded integer cell sums. Surviving quotient
vectors can then be refined to a quotient with smaller kernel, ending at
individual coefficients.

Equation (4) is a necessary condition because projection is a group-ring
homomorphism. Completeness requires more: every bounded cell vector compatible
with the exact fiber data must be enumerated, and every possible refinement
of every survivor must be checked. The independent verification programs do
exactly this. They do not trust saved candidate counts; they regenerate the
options, correlations, and refinement trees.

Translations act on quotient vectors and lift to translations of the full
group. In cyclic quotients, multiplication by a unit also lifts through the
cyclic ladder used below. This permits orbit representatives without losing a
possible full solution. In product quotients we use only translations unless
an additional affine action is explicitly justified.

At order 36, real characters and order-three characters give complementary
marginals. For groups with a `C6` factor, the Chinese remainder decomposition
`C6 = C2 x C3` makes the corresponding translation normalizations
independent: the real exceptional fiber and the order-three exceptional fiber
can be moved to their chosen origins simultaneously. This observation reduces
the final `C6 x C6` instance to one normalized joint pattern.

The quotient approach has two advantages. It exposes the mathematical reason
that the search collapses, and it produces small intermediate data that can be
checked without the original solver. Only the last normalized `C6 x C6`
refinement remains large enough to justify a proof-producing SAT encoding.

<!-- pagebreak -->

## 4. The six constructions at order 32

There are seven abelian groups of order 32. The six noncyclic groups all admit
signed `(32,20,4)` difference sets. The table identifies one standalone
witness for each group; the final column is the SHA-256 of the JSON witness.

| Group | Positive/negative | Witness SHA-256 |
|---|---:|---|
| `C2 x C16` | 16 / 4 | `4ac02b48513f14385bffd574a2b531d46223375baf7cdc3e398be7f70a433eff` |
| `C4 x C8` | 16 / 4 | `d22db64868c4632dde42cf06c2f8ad4f36378cec7a8b62f77fa39f022f362540` |
| `C2 x C2 x C8` | 16 / 4 | `7b6c903b5b6c7c788615ec9a3ea2b67eb8ff41e538e23085c97b842219144799` |
| `C2 x C4 x C4` | 16 / 4 | `b6b9de3b1bd7f821e1d79ffcd03fc92e9931f245429825d1f01e53342e896dc1` |
| `C2 x C2 x C2 x C4` | 16 / 4 | `d099f73f04a3233d8802183e714edfa3cbdc396c252f02dd3dc45dba99910334` |
| `C2^5` | 16 / 4 | `7b4fdd2a34ca1e61376a53169e7475bccecd69aa909d967b5d44011e4eabd101` |

Each file contains more than a bare vector. It records the group invariant
factors, coordinate convention, positive and negative point sets, coefficient
sum, complete autocorrelation vector, discovery provenance, and outputs from
both validators. The expected correlation vector is

```text
(20,4,4,...,4), with 31 occurrences of 4.
```

The existence proof is short once a vector is known: substitute it into (1).
The value of retaining two implementations is defensive rather than
theoretical. A shared indexing error can make many vectors appear valid, so
the mixed-radix checker deliberately avoids the tuple operation used by the
reference checker. Unit tests also compare the implementations on good and
mutated vectors.

No classification up to equivalence is claimed. A single verified vector is
sufficient for existence in each named group, and the files may represent
only one of many translation, sign, inversion, or automorphism orbits. The
theorem classifies groups by existence, not the number of inequivalent signed
difference sets.

The coefficient composition also gives a convenient human check. Every row
has `16+4=20` nonzero positions and coefficient sum `16-4=12`, consistent
with equation (2). This is necessary but not sufficient; the validators still
check all 31 nonidentity shifts.

<!-- pagebreak -->

## 5. Excluding the cyclic group of order 32

For `G=C32`, projection along the subgroup of order 4 first gives a vector on
`C8`. The independent exhaustive verifier enumerates 9,528 bounded integral
vectors after the total-sum and zero-shift norm constraints. Exactly 56 solve
the full quotient autocorrelation equations. The affine action generated by
cyclic translation and multiplication by units reduces them to five orbits,
of sizes 8, 16, 8, 16, and 8.

Each orbit representative is refined through `C16`. Across the normalized
parents, 12 distinct `C16` solutions survive. The verifier then enumerates
every ternary refinement to `C32`. There are 20,736 refinements for each of the
12 parents, hence 248,832 final coefficient vectors in total. None satisfies
the full `C32` autocorrelation equations.

| Stage | Complete count | Survivors |
|---|---:|---:|
| Bounded vectors on `C8` after sum and norm | 9,528 | 56 |
| Affine orbits on `C8` | 5 | 5 representatives |
| Distinct normalized solutions on `C16` | all refinements | 12 |
| Ternary refinements on `C32` | 248,832 | 0 |

The completeness argument has three parts. First, the cell bounds and parity
conditions enumerate every possible sum of four coefficients over a `C8`
fiber. Second, equation (4) is checked at every quotient shift, not merely at
selected characters. Third, every `C16` fiber is split in all compatible
ways, and every surviving two-cell fiber is finally split into its two
individual coefficients. The cyclic affine actions used at the first stages
lift to `C16` and `C32`, so orbit reduction does not discard a possible
solution.

The full result is independently regenerated by
`scripts/verify_v32_remaining_quotients.py`. The canonical aggregate artifact
has SHA-256
`2870150476387abadaf39792d254455a85cd2321a85011c6b2719a756001b1ab`.
Because all six noncyclic groups have witnesses and the only cyclic group is
excluded, Theorem 1 follows.

<!-- pagebreak -->

## 6. Two transparent exclusions at order 36

For `(36,29,4)`, the normalized coefficient sum is 13 and equation (4)
combines effectively with real and order-three character marginals.

For `C2 x C18`, use a quotient `C2^2 x C3` with kernel order 3. Its zero-shift
correlation must be `29+2*4=37`, and every nonzero quotient shift must have
correlation `3*4=12`. After normalizing the order-three marginal to
`(1,6,6)` and the real marginal to `(7,2,2,2)`, the bounded cells lie in
`[-3,3]`. There are 144 candidates satisfying the marginals and norm. Direct
calculation of every quotient correlation leaves no solution.

For `C3 x C12`, a quotient `C2 x C3^2` with kernel order 2 has zero-shift
correlation `29+4=33` and nonzero-shift correlation 8. The normalized real
marginal is `(4,9)`, and the order-three marginal is
`(-3,2,2,2,2,2,2,2,2)`. The cells lie in `[-2,2]`. Exactly 420 candidates
satisfy the marginals and norm, and none satisfies every quotient
autocorrelation.

| Group | Quotient | Candidates after marginals and norm | Full solutions |
|---|---|---:|---:|
| `C2 x C18` | `C2^2 x C3` | 144 | 0 |
| `C3 x C12` | `C2 x C3^2` | 420 | 0 |

These are exclusions already at a quotient level: a full signed difference
set would necessarily project to a listed quotient solution, but there are no
such solutions. No SAT solver is used for either decision.

The regenerating checker is
`scripts/verify_v36_29_4_combined_quotients.py`. It rebuilds the bounded row
and column options, derives the normalized marginals, and checks every shift.
The shared aggregate artifact has SHA-256
`416ca62582a54b9d3b398436b36ccfbd239db1c48b113ed385329110c98b99e5`.
This compact file and checker are included in the lightweight package, so
these two parts of Theorem 2 can be audited without the gigabyte-scale proof
archive.

<!-- pagebreak -->

## 7. The certified `C6 x C6` exclusion

The same character analysis for `C6 x C6` first considers its `C3^2`
projection. Exhaustive bounded enumeration produces 106,353 candidates after
the sum and norm tests and only nine full projection solutions. Those nine
are one affine orbit, represented by

```text
(-3,2,2,2,2,2,2,2,2).
```

The real quotient likewise has one orbit, represented by `(7,2,2,2)`.
Through `C6=C2 x C3`, translations can normalize the exceptional cells in
both patterns independently. Therefore a single exact full-autocorrelation
CNF instance covers every remaining candidate.

The normalized formula has 79,680 variables and 814,764 clauses. The
proof-producing solver returned `UNSAT` and emitted a 23,359,321-byte DRAT
trace. The formula and proof hashes are respectively

```text
CNF:  3b67af8cc63ea9377220816334fdf26cb1c2c22e5c4dac637f2c9a6f4d3158ff
DRAT: f8a427135933a5033aa33e69554f269c41b3b3544ae00cf2cf18d92b007bb4c4
```

The certificate is checked in forward mode by `drat-trim` at source commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`. The checker validates each
admissible proof addition and derives the empty clause; it does not rerun or
trust the original solver. A clean-environment audit recompiles that exact
checker source in a fresh pinned Debian container, verifies every CNF and DRAT
hash, and reruns this proof together with the other accepted proof subcases.
The complete machine-readable report and unabridged journal are stored under
`artifacts/audit/`.

The mathematical and propositional layers are kept distinct. The quotient
enumeration proves that one normalized orbit is complete. The encoding tests
compare SAT solutions and direct autocorrelation on smaller instances and
known positive cases. The DRAT checker proves that the final CNF has no model.
Together these statements exclude a signed difference set in `C6 x C6` and
complete Theorem 2.

The corollary uses one prior datum rather than presenting it as new: the
frozen La Jolla snapshot marks `SDS(36,29,4,[36])` as `No` with comment
`Orbit Exhaust`. The new computations settle precisely the other three
abelian groups of order 36.

<!-- pagebreak -->

## 8. Reproducibility package and audit protocol

The lightweight package is designed to separate ordinary verification from
archival storage. It contains this note, all 16 positive witnesses from the
broader census, both validators, unit tests, the final quotient artifacts and
their regenerating checkers, the census manifest, licensing information, and
a SHA-256 manifest. It intentionally omits the 1.1 GB of CNF and DRAT files.
Those large traces are to be archived separately with stable hashes and a DOI;
the package manifest provides the link once the archival record exists.

A minimal positive audit uses only the Python standard library:

```text
python3 -m unittest discover -s tests -v
python3 scripts/audit_final_census.py
```

The three compact final quotient audits are:

```text
python3 scripts/verify_v27_remaining_quotients.py
python3 scripts/verify_v32_remaining_quotients.py
python3 scripts/verify_v36_29_4_combined_quotients.py
```

The full certificate audit is intentionally heavier:

```text
scripts/run_clean_drat_audit.sh
```

That script pulls a minimal Debian image, records its resolved image digest,
installs a compiler and Git inside the disposable container, clones
`drat-trim`, checks out the frozen commit, compiles it, and invokes the
57-certificate audit. For each pair the journal records paths, expected and
observed SHA-256 values, the exact command, complete checker output, return
code, elapsed time, and final verification status. The repository is mounted
read-only; the report is copied from a temporary output mount afterward.

Reproducibility has limits worth stating. A DRAT certificate certifies the CNF,
not an informal description of the combinatorial problem. Confidence in the
translation rests on readable generators, structural tests, agreement with
small exhaustive cases, and the quotient completeness argument. Likewise,
the dated literature and repository search supports a novelty assessment but
cannot logically prove that no earlier result exists.

<!-- pagebreak -->

## 9. Relation to the 68-entry census, availability, and disclosure

The two theorems are the principal mathematical contribution. They arose in a
larger audit of all 68 entries of group order at most 36 marked Open in the
frozen snapshot. That census closes every named entry: 16 are existential and
52 are nonexistential. The accepted evidence consists of 16 explicit
constructions, 13 decisions by checked SAT/DRAT proofs, 4 direct exhaustive
enumerations, 9 exhaustive character obstructions, 14 exhaustive
quotient/character reductions, and 12 real-character square obstructions.

A dated prior-art screen found an exact independent predecessor for 58 of the
68 decisions in the public `farev/Matematica` project, with no disagreements.
Those 58 decisions are described as independent replications. The seven
order-32 and three noncyclic order-36 entries treated in this note are only
called novelty-supported: searches through the named repositories,
alternate notation, exact parameters, related papers, and citations found no
earlier exact resolution as of August 12, 2026. Search evidence is not a proof
of novelty, and specialist review remains desirable before journal submission.

All computations reported here used local CPU resources; paid-compute cost was
zero. The frozen input data are CC BY 4.0. The project software is released
under the MIT License, while the note and project-authored data are released
under CC BY 4.0. Exact third-party provenance remains attached to imported
material.

**AI-use disclosure.** OpenAI Codex was used extensively as a computational
research and software-engineering assistant: to propose search and quotient
strategies, write and revise code and documentation, execute local
experiments, organize artifacts, and draft this note. No model output was
accepted as mathematical evidence. Every positive claim is backed by an
explicit vector checked by two independent deterministic validators; every
negative claim is backed by a reconstructible exhaustive calculation or an
exact CNF/DRAT certificate checked by independently compiled software. The
human author selected the research objective, authorized the work, and remains
responsible for the claims, framing, and release.

## References

[1] D. M. Gordon, "Signed Difference Sets," Designs, Codes and
Cryptography 91 (2023), 2107-2115. DOI: 10.1007/s10623-022-01171-8.

[2] D. M. Gordon, La Jolla Signed Difference Set Repository,
`https://github.com/dmgordo/signed-difference-sets`, frozen commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e`.

[3] Y. He, H. Chen, and G. Ge, "New constructions of signed difference
sets," Designs, Codes and Cryptography 92 (2024), 2323-2340.
DOI: 10.1007/s10623-024-01389-8.

[4] N. Wetzler, M. J. H. Heule, and W. A. Hunt Jr., "DRAT-trim: Efficient
Checking and Trimming Using Expressive Clausal Proofs," SAT 2014, 422-429.
DOI: 10.1007/978-3-319-09284-3_31.

[5] Certified Census of Small Signed Difference Sets, machine-readable
census, witnesses, quotient artifacts, and audit logs, version 1.0.
