# Ecology Article cross-scale submission manifest v0.1

## Canonical submission

**Journal:** Ecology  
**Article type:** Article  
**Title:** Breeding-component concentration recurs across spatial scales in Antarctic penguins

This package supersedes the earlier Ecology Report submission line for initial submission. Older Report, Ecosphere, JBI and integrated manuscript files remain only as provenance.

## Main scientific files

- main manuscript: `submission/MANUSCRIPT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- supporting information: `submission/SUPPLEMENT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- main figure captions: `submission/FIGURE_CAPTIONS_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- supplementary figure caption: `submission/SUPPLEMENTARY_FIGURE_CAPTION_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md`
- references: `docs/REFERENCES_V6.bib`

Approximate manuscript metrics:

- title: 83 characters including spaces
- abstract: 259 words
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

- Palmer discovery in fixed sample-colony monitoring networks: `results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`
- Palmer source-provenance correction: `docs/PALMER_SAMPLE_COLONY_PROVENANCE_AUDIT_V1.md`
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

Scientific endpoints are closed. On 2026-10-06 a source-provenance audit corrected the Palmer observational scope from exhaustive island population totals to summed counts in fixed sample-colony monitoring networks; no endpoint, roster, null family, p-value or effect size changed. These metadata blockers do not authorize new ecological analyses.


## Word and visual QA status

The prior one-paper Main Document and Appendix passed visual QA before the Palmer source-provenance wording correction. Those artifacts are now provenance-only. A corrected Main Document and Appendix must be regenerated and visually checked before upload; page counts below remain historical until that rebuild is complete.

With the three main figures counted as one page each, the complete Ecology Article is **32 pages**. This is two pages above the standard 30-page Article length. The cover letter now contains the two numbered justifications required by Ecology for an Article above 30 pages and below 50 pages: broad ecological contribution and the value/necessity of the additional length.

The preview artifacts still contain author placeholders and therefore must not be uploaded as the final submission files.

## Canonical target resolution

Initial submission is **Ecology — Article**. The compact Ecology Report package is retained as an alternate only and must not be uploaded in parallel. See `contracts/ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json`.


## Artifact provenance

Superseded pre-correction artifacts:

- DOCX workflow run: `37391673031`
- DOCX artifact: `11381845511`
- DOCX digest: `sha256:5a679d1fbc69d3cb81f226d2b84e1d10834f64e7e40a706f2b403bebb549dd42`
- rendered Main Document: **29 pages**
- figure workflow run: `37391673074`
- figure artifact: `11381685529`
- figure digest: `sha256:d0801b4a25440a782f8f04101a4707f6976653f2bc62635f238450206cb42451`
- Appendix S1 workflow run: `37391672322`
- Appendix artifact: `11381457683`
- Appendix digest: `sha256:6451ec8aaa0590a37cbc281cf06438e7f3e279ab4f7634db981fab64890596ca`
- rendered Appendix S1: **9 pages**

Older DOCX, figure and Appendix artifacts remain provenance only.

## AI disclosure status

OpenAI ChatGPT use is disclosed in the applicable Methods section, in Acknowledgments, and in the prepared submission-form copy field. The current placeholder Word artifact includes the Methods and Acknowledgments disclosures.

## Initial-upload blocker

Scientific endpoints are closed, but the corrected Palmer sampling-unit wording requires regeneration and visual/page-count QA. **Current blockers are corrected-package QA plus author-controlled metadata**, followed by regeneration of the author-complete Main Document and Appendix S1 and inspection of the ScholarOne proof.

SMP PR #177 and guillemot PR #178 are independent follow-up projects and are not conditions for this submission.