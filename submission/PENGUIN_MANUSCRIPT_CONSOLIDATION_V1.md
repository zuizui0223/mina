# Penguin manuscript consolidation decision v1

**Date:** 2026-10-07  
**Status:** ACTIVE SINGLE-MANUSCRIPT SUBMISSION POLICY

## Decision

While the integrated spatial-structure manuscript is active, the penguin research program has **one canonical submission candidate**:

    docs/MANUSCRIPT_SPATIAL_MEMORY_INTEGRATED_V0_4.md

The following previously complete packages remain frozen scientific provenance but are **not independent active submission lanes**:

1. Palmer Paper 1 / Ecosphere v0.8
   - scientific provenance: `docs/PAPER1_V1.md`
   - manuscript: `docs/MANUSCRIPT_ECOSPHERE_V0_8.md`
   - submission package: `contracts/PALMER_ECOSPHERE_SUBMISSION_PACKAGE_V0_8.json`

2. Ross spatial-reversal Ecology Report / PR189 standalone package
   - scientific provenance retained;
   - standalone submission hold: `submission/SUBMISSION_READINESS_SPATIAL_REVERSAL_V6.md`

## Why consolidation is necessary

The integrated manuscript already contains the primary Palmer concentration result that anchors Paper 1 and the Ross disturbance/rebound result that anchors the standalone PR189 Report.

Submitting either source manuscript independently while the integrated manuscript is active would create substantial scientific overlap and would defeat the explicit program decision not to split one evidence chain into multiple papers.

This consolidation changes **submission architecture only**.

It does not:
- alter any frozen endpoint;
- retroactively reclassify confirmatory/post-result status;
- delete the Paper 1 v1 manuscript or package;
- change the Ross mechanism-search stop rule;
- convert the integrated synthesis into a preregistered analysis.

## Canonical evidence inheritance

The integrated manuscript inherits, without reopening:

### From Palmer Paper 1
- regional decline context;
- the three stable-roster within-island concentration endpoints;
- fixed-composition proportional-thinning nulls;
- independent count-error sensitivities;
- the original physical-code and mechanism boundaries.

It does **not** need to inherit every secondary Paper 1 result. In particular, weak forecasting, beta-hierarchy, and other non-core branches should remain outside the integrated main text unless required as a boundary.

### From PR189
- Ross 1999→2001→2002 inverse-path effect sizes;
- measurement boundary: breeding abundance, not total adult abundance;
- mismatch calibration against other Ross down→up triplets;
- the failed original 2001→2012 prediction and its transparent post-result status;
- the closed mechanism-search record.

### Additional integrated evidence
- Signy independent concentration replication;
- Beaufort capacity-release case;
- Bird / Emperor prospective anti-sign-locking boundaries;
- Heard literature triangulation.

## Single-submission rule

Do not submit:
- Palmer Ecosphere v0.8;
- standalone Ross Ecology Report;
- integrated spatial-memory manuscript

as simultaneous or overlapping manuscripts.

The integrated manuscript is currently preferred.

If it is later abandoned, reopening either narrower package requires an explicit new submission-decision record that:
1. states why integration failed;
2. maps scientific overlap;
3. restores exactly one narrower active lane;
4. leaves the other lane on hold.

## Canonical current package

- Manuscript: `docs/MANUSCRIPT_SPATIAL_MEMORY_INTEGRATED_V0_4.md`
- Bibliography: `docs/REFERENCES_SPATIAL_MEMORY_INTEGRATED_V0_4.bib`
- Process classification: `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`
- Claim ledger: `results/SPATIAL_MEMORY_CLAIM_EVIDENCE_LEDGER_V2.json`
- Evidence table: `docs/TABLE1_SPATIAL_MEMORY_EVIDENCE_V0_1.md`
- Reviewer stress test: `docs/SPATIAL_MEMORY_INTEGRATED_REVIEWER_STRESS_TEST_V1.md`
- Novelty boundary: `docs/SPATIAL_MEMORY_NOVELTY_BOUNDARY_V1.md`
- Figure builder: `scripts/build_spatial_memory_integrated_figures.py`
- Figure captions: `docs/FIGURE_CAPTIONS_SPATIAL_MEMORY_INTEGRATED_V0_1.md`
- Scientific readiness: `submission/SPATIAL_MEMORY_INTEGRATED_READINESS_V1.md`

## Paper-count consequence

For submission planning, the Palmer concentration, Ross spatial reversal, Signy replication, and Beaufort contrast are now treated as **components of one manuscript**, not four publishable units.

Their separate repository artifacts remain audit trails, not paper-count commitments.
