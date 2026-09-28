# Ecosphere v0.7 submission-readiness audit

## Current status

**Scientific content: READY at v0.7. Word preview: QA PASSED. Submission metadata: BLOCKED pending author confirmation.**

The scientific manuscript is `docs/MANUSCRIPT_ECOSPHERE_V0_7.md`. The previous v0.6 submission package is provenance only.

## Frozen scientific boundary

- Five-island long-term decline/state results are retained.
- The observed raw hierarchy is `beta_within = 1.0737`, `beta_among = 1.0112`.
- The hierarchy exceeds Poisson and inherited CV10% count-error expectations, but is compatible with the uncalibrated CV20% sensitivity (`p = 0.924` for beta-within; `p = 0.448` for the log-beta contrast).
- Detrended and annual-growth hierarchy statistics are not rescue endpoints.
- N_eff remains a separate weak conditional association; it is not a supported predictor or causal buffering metric.

## Structural requirements already satisfied

- Title: **113/120 characters**.
- Abstract: **329/350 words**.
- Keywords: **8**, within the required 6–12 range.
- Main figures: 5; Figure 3 now includes the count-error identification boundary.
- Public source data have permanent identifiers.
- Public code/reproducibility repository is available for peer review.

## Word Main Document

The v0.7 preview has been rendered and visually inspected across all **35 pages**. Continuous line numbering runs **1–737**. Equations, count-error Methods/Results, references, AI disclosure, and Figure 1–5 captions render correctly. The source defects found during the first render (plain alpha/gamma/phi tokens and duplicated headings) were fixed and the document was re-rendered.


The Word builder is version-agnostic and takes the manuscript title from the supplied H1. For v0.7 use:

`docs/MANUSCRIPT_ECOSPHERE_V0_7.md`  
`docs/REFERENCES_V5.bib`  
`docs/FIGURE_CAPTIONS_V6.md`

Final formatting gate:

- Letter portrait, 1-inch margins.
- Times New Roman 12 pt.
- Double-spaced manuscript body, references and captions.
- Page numbers from the title page.
- Continuous line numbering on all manuscript pages.
- Abstract starts on a new page.
- Figure captions grouped once after References.
- No control-character or math-rendering defects.

## Required AI disclosure

OpenAI ChatGPT (GPT-5.6 Sol) was used during analysis and manuscript development to assist with code drafting and review, statistical sensitivity-analysis scripting, literature searching, and editorial drafting. All analyses were executed from version-controlled code, numerical results were checked against frozen result receipts, cited literature was independently verified, and the authors remain responsible for all analyses, interpretations, and text.

The builder inserts the Methods/Reproducibility disclosure and the full Acknowledgments disclosure. Confirm the complete AI-tool inventory before final generation.

## Human-only blockers

1. Final author list/order.
2. Affiliations and present addresses.
3. Exactly one corresponding author and email.
4. Funding and grant identifiers.
5. Author Contributions.
6. Conflict of Interest Statement.
7. Complete AI-tool inventory.
8. Dual-publication/overlap statement.
9. Generate and visually inspect the author-complete v0.7 Word file.

## Post-acceptance only

- Archive the exact code and derived-output version of record.
- Mint the permanent DOI.
- Update the Open Research Statement with the archive DOI.
