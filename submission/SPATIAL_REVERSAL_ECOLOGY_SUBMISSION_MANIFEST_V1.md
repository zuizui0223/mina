# PR189 spatial-reversal Ecology submission manifest v1

## Canonical submission package

**Journal:** Ecology  
**Article type:** Report  
**Title:** Breeding rebound largely retraces spatial loss after a mega-iceberg disturbance

This manifest applies **only** to PR189 spatial reversibility.

Do **not** upload the separate `MANUSCRIPT_ECOLOGY_REPORT_*` breeding-space-contraction package as part of this submission.

## Main manuscript

- `submission/MANUSCRIPT_SPATIAL_REVERSAL_ECOLOGY_V0_3.md`

## Cover letter

- `submission/COVER_LETTER_SPATIAL_REVERSAL_ECOLOGY_V0_2.md`

## References

- `submission/REFERENCES_SPATIAL_REVERSAL_V2.bib`

## Figure captions

- `submission/FIGURE_CAPTIONS_SPATIAL_REVERSAL_V0_2.md`

## Main figures

Built by:

- `scripts/build_spatial_reversal_figures.py`
- workflow: `.github/workflows/spatial-reversal-figures.yml`

Expected files:

1. `figure1_ross_disturbance_rebound.pdf`
2. `figure2_inverse_path_rebound.pdf`
3. `figure3_external_sign_tests.pdf`

PNG review copies are generated with the same stems.

## Scientific audit files

- preferred analysis spine: `docs/MANUSCRIPT_RECOVERY_REDUNDANCY_V0_12.md`
- mechanism closure: `docs/PR189_MECHANISM_CLOSURE_V1.md`
- inverse-path effect: `docs/ROSS_INVERSE_PATH_MISMATCH_V1.md`
- count uncertainty: `docs/ROSS_COUNT_UNCERTAINTY_AUDIT_V1.md`
- bounded-count sensitivity: `docs/ROSS_INVERSE_PATH_BOUNDED_COUNT_SENSITIVITY_V1.md`
- mismatch context: `docs/ROSS_INVERSE_PATH_MISMATCH_CONTEXT_V1.md`
- dominance reviewer audit: `docs/ROSS_SPATIAL_REVERSIBILITY_DOMINANCE_AUDIT_V1.md`
- reviewer stress test: `submission/PRE_SUBMISSION_REVIEWER_STRESS_TEST_SPATIAL_REVERSAL_V2.md`
- readiness: `submission/SUBMISSION_READINESS_SPATIAL_REVERSAL_V3.md`

## Primary result receipts

- Ross inverse path: `results/ROSS_INVERSE_PATH_MISMATCH_V1.json`
- Bird Island sign test: `results/BIRD_ISLAND_GENTOO_SIX_UNIT_RECOVERY_ALLOCATION_V1.json`
- Bird temporal audit: `results/BIRD_ISLAND_GENTOO_SIX_UNIT_TEMPORAL_AUDIT_V1.json`
- Emperor global decline: `results/EMPEROR_GLOBAL_DECLINE_SPATIAL_REDUNDANCY_V1.json`

## Human-controlled blockers before upload

- final author list/order;
- affiliations;
- corresponding author/email;
- funding and acknowledgments;
- CRediT roles;
- conflict-of-interest statement;
- ORCIDs if requested;
- final AI disclosure;
- permanent archive DOI / Open Research Statement;
- final dual-publication confirmation.

## Scientific freeze

No new ecological endpoint, species, lag, mechanism covariate, concentration metric or tuned Ross anchor should be added before initial submission.

Allowed:
- copyediting;
- formatting;
- final reference verification;
- figure QA;
- archive packaging;
- author metadata.
