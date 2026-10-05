# Ecology Article cross-scale submission manifest v0.1

## Canonical submission

**Journal:** Ecology  
**Article type:** Article  
**Title:** Breeding-space concentration recurs across spatial scales in Antarctic penguins

This package supersedes the earlier Ecology Report submission line for initial submission. Older Report, Ecosphere, JBI and integrated manuscript files remain only as provenance.

## Main scientific files

- main manuscript: `submission/MANUSCRIPT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- supporting information: `submission/SUPPLEMENT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- main figure captions: `submission/FIGURE_CAPTIONS_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- supplementary figure caption: `submission/SUPPLEMENTARY_FIGURE_CAPTION_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- references: `docs/REFERENCES_V6.bib`

Approximate manuscript metrics:

- title: 79 characters including spaces
- abstract: 257 words
- main text before full reference list: ~4,600 words
- main figures: 3
- supplementary figures: 1
- main tables: 0

## Submission prose and metadata

- cover letter: `submission/COVER_LETTER_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- copy fields: `submission/ECOLOGY_ARTICLE_CROSS_SCALE_COPY_FIELDS_V0_1.md`
- title-page template: `submission/TITLE_PAGE_ECOLOGY_ARTICLE_CROSS_SCALE_TEMPLATE.md`
- private metadata template: `submission/ECOLOGY_METADATA_TEMPLATE.json`
- Word-layout QA receipt: `submission/ECOLOGY_ARTICLE_CROSS_SCALE_DOCX_QA_RECEIPT_V0_1.json`

## Main figures

1. `figure1_replicated_trajectories.pdf`
2. `figure2_cross_scale_transfer.pdf`
3. `figure3_regional_endpoint_context.pdf`

Supplement:
- `figureS1_nominal_dominance_routes.pdf`

Reproducible figure workflow:
- `.github/workflows/cross-scale-concentration-figures.yml`

## Scientific provenance

- Palmer discovery: `results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`
- Signy Adélie prospective replication: `results/SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`
- Signy chinstrap prospective replication: `results/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`
- regional scale transfer: `results/MAPPPD_REGIONAL_CONCENTRATION_RECEIPT_V2.json`
- closed local scaling description: `results/CONTRACTION_SCALING_LAW_SYNTHESIS_V1.json`
- reviewer audit: `docs/CROSS_SCALE_CONCENTRATION_REVIEWER_AUDIT_V0_1.md`

## Human-controlled blockers

Initial submission still requires private confirmation of:

- author list/order
- affiliations and present addresses
- one corresponding author and email
- funding/grant text
- acknowledgments
- CRediT roles
- conflict-of-interest statement
- complete AI-tool inventory
- overlap/dual-publication statement
- ORCID IDs if requested

Scientific endpoints are closed, but the manuscript interpretation was revised on 2026-10-05 to promote the increasing MAPPPD networks as a main boundary condition. These metadata blockers do not authorize new ecological analyses.


## Word preview status

The revised one-paper DOCX has been rebuilt successfully and passed structural Word audit. The revised main figures have passed the Ecology dimension audit, and Appendix S1 has been rebuilt successfully.

Final human visual QA and the rendered page-count check remain pending. These artifacts must not be uploaded until that QA is recorded.

## Canonical target resolution

Initial submission is **Ecology — Article**. The compact Ecology Report package is retained as an alternate only and must not be uploaded in parallel. See `contracts/ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json`.


## Artifact provenance

Current revised artifacts:

- DOCX workflow run: `37271645516`
- DOCX artifact: `11328750641`
- DOCX digest: `sha256:261b32a8ed3c7aa199ab47861e970bb6165256056ba5acb576390c5236e857d6`
- figure workflow run: `37271645669`
- figure artifact: `11328134584`
- figure digest: `sha256:b11e37a4a1ffc7a209abcc9ea201785546184b93a9a90dae5537c2ca33f6fd8f`
- Appendix S1 workflow run: `37271645474`
- Appendix artifact: `11327474999`
- Appendix digest: `sha256:5c0152464b1475a1e4060058d7a6226f2052e189d1861f049263c61512866eb0`

The older 24-page DOCX and pre-revision figures remain provenance only.

## AI disclosure status

OpenAI ChatGPT use is disclosed in the applicable Methods section, in Acknowledgments, and in the prepared submission-form copy field. The current placeholder Word artifact includes the Methods and Acknowledgments disclosures.

## Initial-upload blocker

Scientific endpoints are closed and the revised package has been regenerated. **Initial upload is blocked by final human visual QA / page-count verification and author-controlled metadata.**