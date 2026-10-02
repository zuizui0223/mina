# Ecology Report submission manifest v1

## Canonical submission

**Journal:** Ecology  
**Article type:** Report  
**Title:** Breeding-space contraction recurs across declining Adélie and chinstrap penguins

Only the files listed in this manifest are canonical for the initial submission.
Older Ecosphere, JBI, integrated, v0.4 and earlier submission documents remain
for provenance and must not be uploaded as parallel manuscripts.

## Scientific manuscript

- `submission/MANUSCRIPT_ECOLOGY_REPORT_V0_5.md`
- approximate pre-reference word count: **2,445**
- abstract: **155 words**
- main figures: **2**
- supplementary figures: **1**
- tables: **0**

## Submission prose

- cover letter: `submission/COVER_LETTER_ECOLOGY_REPORT_V3.md`
- submission copy fields: `submission/ECOLOGY_SUBMISSION_COPY_FIELDS_V2.md`
- title-page template: `submission/TITLE_PAGE_ECOLOGY_REPORT_TEMPLATE.md`
- private-metadata template: `submission/ECOLOGY_METADATA_TEMPLATE.json`

## Figures

Main:
1. `figure1_replicated_trajectories.pdf`
2. `figure2_cross_population_summary.pdf`

Supplement:
- `figureS1_nominal_dominance_routes.pdf`

Caption sources:
- `submission/FIGURE_CAPTIONS_ECOLOGY_REPORT_V0_4.md`
- `submission/SUPPLEMENT_ECOLOGY_REPORT_V0_4.md`

Reproducible builders:
- `scripts/build_replicated_concentration_figure_data.py`
- `scripts/plot_replicated_concentration_figures.py`
- `.github/workflows/replicated-concentration-figures.yml`

## Word main-document builder

- builder: `scripts/build_ecology_submission_docx.py`
- QA workflow: `.github/workflows/ecology-report-docx-preview.yml`

The builder creates:
- a placeholder review preview from public repository information;
- an author-complete file only when a private metadata JSON passes the complete
  metadata gate.

Formatting enforced by the builder:
- Letter page size;
- 1-inch margins;
- Times New Roman 12 pt;
- title page separated from the line-numbered body;
- double-spaced body;
- page numbers;
- black headings.

## Primary evidence

### Palmer Adélie discovery

Receipt:
- `results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`

Role:
- exploratory discovery system;
- three stable-roster island populations;
- Palmer colony codes treated as monitored census units, not verified fixed GIS
  polygons.

### Signy Adélie confirmatory replication

Contract:
- `contracts/SIGNY_BREEDING_PATCH_CONCENTRATION_V1.json`

Receipt:
- `results/SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`

Role:
- prospectively frozen independent-system replication.

### Signy chinstrap confirmatory replication

Contract:
- `contracts/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_V1.json`

Receipt:
- `results/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`

Role:
- separately prospectively frozen cross-species replication.

## Interpretation audits

- literature positioning:
  `docs/LITERATURE_POSITIONING_REPLICATED_CONCENTRATION_V2.md`
- Palmer colony-code continuity audit:
  `docs/PALMER_COLONY_CODE_CONTINUITY_AUDIT_V1.md`
- reviewer stress test:
  `submission/PRE_SUBMISSION_REVIEWER_STRESS_TEST_ECOLOGY_V1.md`
- provider inquiry draft:
  `submission/PALMER_COLONY_CODE_CONTINUITY_INQUIRY_DRAFT.md`

## Scientific freeze

Canonical freeze:
- `contracts/ECOLOGY_REPORT_SUBMISSION_V3.json`

No new ecological endpoint, concentration metric, threshold, tuned time window,
error model, mechanism endpoint, or post-result rescue species may be added
before initial submission.

## Human-controlled blockers

The public repository intentionally does not guess or publish unconfirmed
author metadata. Initial submission still requires private confirmation of:

- author list and order;
- affiliations and present addresses;
- corresponding author and email;
- funding/grant statement;
- acknowledgments;
- CRediT roles;
- conflict-of-interest statement;
- full AI-tool inventory;
- overlap/dual-publication statement;
- ORCIDs if requested.

Once those are supplied in a private copy of
`submission/ECOLOGY_METADATA_TEMPLATE.json`, run the Word builder with
`--require-complete-metadata`.
