# Penguin manuscript consolidation decision v1

**Date:** 2026-10-07  
**Status:** ACTIVE SINGLE-MANUSCRIPT SUBMISSION POLICY

## Decision

While the integrated spatial-structure manuscript is active, the penguin research program has **one canonical submission candidate**:

    docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md

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

## Scientific reinterpretation

The prior v0.4 spatial-memory framing was superseded after the Ross path-versus-state audit showed that high inverse-path fidelity did not restore baseline composition:

    results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json
    docs/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.md
    submission/SPATIAL_MEMORY_V0_4_REINTERPRETATION_HOLD_V1.md

## Canonical current package

- Manuscript: `docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md`
- Bibliography: `docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib`
- Process classification: `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`
- Claim ledger: `results/SPATIAL_RECOVERY_CLAIM_EVIDENCE_LEDGER_V4.json`
- Local recovery decomposition: `docs/ROSS_LOCAL_RECOVERY_RATIO_DECOMPOSITION_V1.md`
- Spatial-grain audit: `docs/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.md`
- Evidence table: `docs/TABLE1_SPATIAL_MEMORY_EVIDENCE_V0_1.md`
- Reviewer stress test: `docs/SPATIAL_RECOVERY_PATH_STATE_REVIEWER_STRESS_TEST_V2.md`
- Novelty boundary: `docs/SPATIAL_RECOVERY_PATH_STATE_NOVELTY_BOUNDARY_V2.md`
- Figure builder: `scripts/build_spatial_recovery_path_state_figures.py`
- Figure captions: `docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_2.md`
- Scientific readiness: `submission/SPATIAL_RECOVERY_PATH_STATE_READINESS_V2.md`
- Submission plan: `submission/SPATIAL_RECOVERY_ECOLOGY_ARTICLE_PLAN_V5.md`
- Editorial triage: `submission/SPATIAL_RECOVERY_ECOLOGY_EDITORIAL_TRIAGE_V3.md`
- Cover letter: `submission/COVER_LETTER_SPATIAL_RECOVERY_ECOLOGY_V0_5.md`

## Scientific freeze

The active integrated manuscript is frozen for initial-submission production at:

`submission/SPATIAL_RECOVERY_ECOLOGY_SCIENTIFIC_FREEZE_V1.md`

Scientific head:

`3e8882742ca2affc6717d373fd9b6d903b01f4c1`

## Paper-count consequence

For submission planning, the Palmer concentration, Ross spatial reversal, Signy replication, and Beaufort contrast are now treated as **components of one manuscript**, not four publishable units.

Their separate repository artifacts remain audit trails, not paper-count commitments.
