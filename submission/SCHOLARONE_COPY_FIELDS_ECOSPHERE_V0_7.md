# Ecosphere v0.7 — ScholarOne copy fields

**Status:** Frozen non-author submission fields for `docs/MANUSCRIPT_ECOSPHERE_V0_7.md`.

## Journal / submission type

- **Journal:** Ecosphere
- **Manuscript type:** Article
- **Subject Track:** Animal Ecology

## Manuscript title

Hierarchical demography of Antarctic penguin breeding islands: divergent fate and measurement-sensitive buffering

**Character count including spaces:** 113

## Abstract

Seabird breeding islands separate a marine trophic environment from discrete terrestrial reproductive patches, providing a tractable system for asking whether demographic state and temporal compensation occur at the same spatial scale. We analysed a complete 1991–2017 annual census of five neighbouring Adélie penguin (Pygoscelis adeliae) islands near Palmer Station, West Antarctic Peninsula, together with broader breeding-site records and independent spatial reconstruction from Torgersen Island. The five populations shared a strong long-term decline (PC1 of standardized log abundance = 96.4%) while annual growth was only moderately synchronized (median pairwise r = 0.373). Among the three islands with unchanged colony-code rosters, observed raw-abundance beta variability was 1.0737 from colony-code components to islands but 1.0112 from islands to the aggregate; 86.4% of the total log-beta transition occurred within islands. A fully synchronous-subcolony observation-error null changed the interpretation. The raw separation exceeded independent Poisson and inherited Gamma–Poisson 10% multiplicative-CV sensitivities (0/100,000 exceedances for both primary statistics), but was compatible with the uncalibrated 20% sensitivity (within-island beta p = 0.924; hierarchy-contrast p = 0.448). Detrended and annual-growth separations were also compatible with error-only nulls and therefore were not used as rescue evidence. Historical Palmer procedures used repeated independent colony counts with explicit agreement targets, but replicate-count errors are unavailable in the public analysis table, so biological buffering cannot be identified from beta variability alone. Effective colony number retained a small positive conditional association with next-year growth (+0.1168), remaining +0.1126 after two lagged growth terms and unusual under structured nulls, while its held-out MSE gain fell to +0.000444 and was not predictively supported. Prospectively bounded sea-ice-duration and snowfall × habitat formulations were unsupported, whereas independent Torgersen mapping documented habitat-structured subcolony attrition. The strongest inference is therefore scale-explicit but bounded: islands retain distinct demographic states and endpoints, observed sub-island variability is greater than low-to-moderate count-error expectations but remains sensitive to a high uncalibrated error scenario, and colony organization carries a separate weak but robust conditional signal.

**Word count:** 329

## Key words/phrases

Adélie penguin; breeding patches; hierarchical variability; island ecology; long-term monitoring; population dynamics; spatial synchrony; temporal compensation

**Keyword count:** 8

## Open Research Statement

The primary Palmer Station Antarctica Long Term Ecological Research Adélie penguin census is publicly available at DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e. The sea-ice and Palmer Station weather data used in the bounded mechanism tests are publicly available at DOI 10.6073/pasta/4207e529832840db2282498d9f4f4f05 and DOI 10.6073/pasta/3eefb45dbfb784c3cabe3690ea46fe9e, respectively; broader APBP/MAPPPD data are publicly available as cited in the manuscript. Novel analysis code, frozen endpoint contracts, and result receipts used for this submission are publicly accessible for peer review at https://github.com/zuizui0223/mina. If the manuscript is accepted, the exact version of record of the analysis code and derived outputs will be archived in a permanent repository with a DOI, and the final Open Research Statement will be updated with that identifier.

## AI-use disclosure for the submission form

OpenAI ChatGPT (GPT-5.6 Sol) was used during analysis and manuscript development to assist with code drafting and review, statistical sensitivity-analysis scripting, literature searching, and editorial drafting. All analyses were executed from version-controlled code, numerical results were checked against frozen result receipts, cited literature was independently verified, and the authors remain responsible for all analyses, interpretations, and text.

The Word builder inserts the corresponding disclosure in the Reproducibility/Methods text and Acknowledgments. If any additional AI tools were used, add them through the final private metadata file.

## Dual Publication / overlap field

**AUTHOR CONFIRMATION REQUIRED.** Do not infer this from repository history.

If—and only if—all authors confirm there is no relevant overlap, use:

> No overlapping manuscript is published, in press, submitted, or under review elsewhere, and no other manuscript using substantially overlapping data, text, or figures is currently planned for submission.

Otherwise provide a factual overlap statement and identify the related manuscript(s) in the cover letter.

## Author-controlled fields

Complete only from the final author-approved private metadata JSON:

- author names and order;
- affiliations and present addresses;
- one corresponding author and email;
- funding acknowledgments and grant identifiers;
- Author Contributions;
- Conflict of Interest Statement;
- complete AI-tool inventory;
- Dual Publication / overlap statement.

Public template: `submission/ECOSPHERE_METADATA_TEMPLATE.json`

## Main-document / cover-letter sources

- Main manuscript: `docs/MANUSCRIPT_ECOSPHERE_V0_7.md`
- Figure captions: `docs/FIGURE_CAPTIONS_V6.md`
- References: `docs/REFERENCES_V5.bib`
- Scientific contract: `contracts/PALMER_ECOSPHERE_MANUSCRIPT_V0_7.json`
- Count-error receipt: `results/PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json`
- Word builder: `scripts/build_ecosphere_submission_docx.py`
- Cover letter: `docs/COVER_LETTER_ECOSPHERE_V0_7.md`

## Claim boundary reminder

Do not describe the observed nested beta hierarchy as measurement-error robust or as proof of biological spatial insurance. The full frozen count-error family includes an uncalibrated CV20% scenario compatible with the observed hierarchy. Detrended and annual-growth hierarchy statistics are not rescue endpoints.

## Formatting note

The current Word builder uses continuous line numbering on all manuscript pages. A fresh v0.7 render must be visually checked before ScholarOne upload.
