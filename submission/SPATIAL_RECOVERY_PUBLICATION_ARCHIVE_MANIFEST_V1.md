# Spatial recovery publication archive manifest v1

**Date:** 2026-10-07  
**Status:** pre-deposit archive specification; DOI not yet minted.

## Scientific source and production derivative

Frozen scientific manuscript:

    docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_8.md

Initial-submission production manuscript:

    docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md

Scientific freeze:

    submission/SPATIAL_RECOVERY_ECOLOGY_SCIENTIFIC_FREEZE_V1.md

Production derivation:

    submission/SPATIAL_RECOVERY_ECOLOGY_PRODUCTION_DERIVATION_V1.md

## Required archive contents

### Manuscript and submission science

- docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_8.md
- docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md
- docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib
- docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_2.md
- submission/SUPPLEMENT_SPATIAL_RECOVERY_PATH_STATE_V1.md

### Focal result receipts and interpretation audits

- results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json
- docs/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.md
- results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json
- docs/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.md
- results/ROSS_INVERSE_PATH_MISMATCH_V1.json
- results/ROSS_INVERSE_PATH_MISMATCH_CONTEXT_V1.json
- results/ROSS_ICEBERG_SHOCK_REBOUND_AUDIT_V1.json
- docs/ROSS_LOCAL_RECOVERY_RATIO_DECOMPOSITION_V1.md

### Supporting process contrasts

- results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json
- results/SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json
- results/BEAUFORT_ISLAND_INTENSIFICATION_EXPANSION_RESULT_V1.json
- docs/BEAUFORT_ISLAND_MEDIATED_COMPETITION_SYNTHESIS_V1.md

### Claim and transparency controls

- results/SPATIAL_RECOVERY_CLAIM_EVIDENCE_LEDGER_V4.json
- docs/SPATIAL_RECOVERY_PATH_STATE_NOVELTY_BOUNDARY_V2.md
- docs/SPATIAL_RECOVERY_PATH_STATE_REVIEWER_STRESS_TEST_V2.md
- submission/SPATIAL_RECOVERY_PATH_STATE_READINESS_V2.md
- submission/SPATIAL_RECOVERY_ECOLOGY_SUBMISSION_MANIFEST_V1.md
- submission/SPATIAL_RECOVERY_ECOLOGY_PRODUCTION_DERIVATION_V1.md
- submission/SPATIAL_RECOVERY_ECOLOGY_PRODUCTION_QA_V2.json
- submission/SPATIAL_MEMORY_V0_4_REINTERPRETATION_HOLD_V1.md
- submission/PENGUIN_MANUSCRIPT_CONSOLIDATION_V1.md

### Reproducible code

- scripts/analyze_ross_aggregate_vs_spatial_restoration.py
- scripts/analyze_ross_inverse_path_mismatch.py
- scripts/analyze_ross_inverse_path_bounded_count_sensitivity.py
- scripts/analyze_ross_shock_rebound.py
- scripts/build_spatial_recovery_path_state_figures.py
- scripts/build_spatial_recovery_ecology_docx.py
- scripts/build_spatial_recovery_si_docx.py
- pyproject.toml

Include any direct dependencies imported by those scripts from src/mina if required for a standalone rerun.

### Frozen focal derived data

- external/ross_island_v2_frozen_counts.csv

Do not republish third-party raw datasets when their repository terms or provenance are better preserved through original source links. Cite those sources by DOI/checksum instead.

## Public source identifiers to preserve

- Ross Sea Adélie aerial census: DOI 10.7931/kf06-x745
- Palmer Station LTER Adélie census: DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e
- Signy Island Adélie monitoring: DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d
- Beaufort natural experiment: DOI 10.1371/journal.pone.0060568

## Archive metadata to supply at deposit time

Author-controlled:
- final title;
- final author list;
- ORCIDs if desired;
- description;
- keywords;
- license;
- related identifier for the eventual article DOI when available.

Recommended archive version label:

    spatial-recovery-ecology-initial-submission-v1

Do not call the archive “version of record” until the manuscript is accepted and final publication changes have been reconciled.

## Determinism

The release bundle should include:
- a sorted file manifest;
- SHA-256 for every archived file;
- a bundle-level SHA-256;
- repository commit SHA;
- creation date;
- explicit list of excluded third-party raw data.

## DOI boundary

A DOI must not be invented in manuscript or title-page files.

Once an immutable archive deposit has been made:
1. record the deposit DOI;
2. update the Open Research Statement;
3. update the title page / copy fields;
4. preserve the pre-DOI submission history.
