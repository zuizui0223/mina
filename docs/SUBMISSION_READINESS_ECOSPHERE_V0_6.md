# Ecosphere v0.6 submission-readiness audit

## Current status

**Scientific content: READY. Submission metadata: BLOCKED pending author confirmation.**

The frozen scientific manuscript remains `docs/MANUSCRIPT_ECOSPHERE_V0_6.md`. This submission layer must not change endpoints, statistics, null families, thresholds, climate windows, or the interpretation boundary.

## Requirements already satisfied

- Title length: **102 characters**, below the Ecosphere 120-character limit.
- Abstract length: **323 words**, below the 350-word limit.
- Keywords: **8**, within the required 6–12 range.
- Article structure contains Abstract, Introduction, Methods, Results, Discussion, Conclusion, Data availability, and references pointer.
- Five-figure package and grouped captions are frozen in the v0.6 figure workflow.
- Hierarchical-variability, component-count, N_eff momentum, structured-null, and manuscript-number guards pass.
- The code repository is publicly accessible for peer review.
- Primary external data sources already have permanent identifiers.
- The reproducible Word preview has been generated and visually inspected across all **31 pages**: title-page separation, body line numbering, page numbering, equations, materialized citations/references, AI disclosure, and Figure 1–5 captions all render correctly.
- The public metadata template is `submission/ECOSPHERE_METADATA_TEMPLATE.json`; completed author/contact metadata should normally be kept in an untracked local copy rather than committed to the public repository.

## Required submission additions

### Title page

The Word builder already creates the title-page section. Copy `submission/ECOSPHERE_METADATA_TEMPLATE.json` to an untracked local JSON file and complete it; then pass that file to `scripts/build_ecosphere_submission_docx.py --metadata ... --require-complete-metadata`. The builder fills all authors and affiliations, one corresponding author/email, the Open Research Statement, and the frozen 8 keywords.

### Backmatter

Before References, the submission document must contain:

**Acknowledgments.** Include Palmer Station Antarctica LTER / Palmer Station, Antarctica, relevant funding acknowledgments, and the AI-use disclosure below.

**Author Contributions.** Complete a CRediT-style paragraph only after every author has approved the role assignment.

**Conflict of Interest Statement.** Confirm the actual author status. Do not assume “none” until every author has confirmed it.

### Required AI disclosure

Because OpenAI ChatGPT was used beyond spelling/grammar, the submission must disclose its use both in the manuscript and in ScholarOne. A suitable minimum disclosure is:

> OpenAI ChatGPT (GPT-5.6 Sol) was used during analysis and manuscript development to assist with code drafting and review, statistical sensitivity-analysis scripting, literature searching, and editorial drafting. All analyses were executed from version-controlled code, numerical results were checked against frozen result receipts, cited literature was independently verified, and the authors remain responsible for all analyses, interpretations, and text.

The Word builder already inserts an appropriately brief disclosure in the Reproducibility/Methods text and the full disclosure in the Acknowledgments. Before final generation, confirm the complete AI-tool inventory; any additional tools entered in the metadata JSON are appended to both disclosures.

### Open Research

For review, the public GitHub repository is acceptable as the external code location. Data are already publicly archived under the DOIs listed on the title-page template. Upon acceptance, archive the exact code and derived-output release in a permanent repository (planned: Zenodo) and update the Open Research Statement with the DOI.

## Formatting gate for the Word Main Document

Before upload:

- Letter page size, portrait.
- 1-inch margins.
- Times New Roman, 12 pt (tables may use 10 pt if necessary).
- Double-spaced manuscript text, references, figure captions, and table captions/notes.
- Left aligned, not fully justified.
- Page numbering from the title page.

The detailed general-formatting subsection also describes numbering as starting after the title page; because the initial-submission checklist explicitly requires continuous line numbering on all pages, this package follows the stricter all-pages rule.
- Continuous line numbering on **all manuscript pages**, including the title page, following the stricter initial-submission requirement in the September 2026 Ecosphere guidelines.
- Abstract begins on a new page.
- Tables, if any, begin on new pages in the Main Document.
- Figure captions are grouped once in their own section.
- Figures are either each on their own page in the Main Document or uploaded separately at sufficient quality.

## Human-only blockers before ScholarOne upload

1. Confirm final author order.
2. Confirm all affiliations/present addresses.
3. Confirm one corresponding author and email.
4. Confirm author contributions.
5. Confirm funding text and identifiers.
6. Confirm conflict-of-interest statement.
7. Confirm the complete AI-tool inventory.
8. Confirm the dual-publication/overlap statement used in ScholarOne and the cover letter.
9. Confirm whether the public GitHub link remains the review code link or is replaced by another accessible review repository.
10. Generate the **author-complete** Word Main Document and visually inspect that final rendered file.

The submission guard is intentionally fail-closed: metadata completeness alone is insufficient; `ready_for_scholarone=true` requires both complete metadata and confirmed visual QA of the author-complete Word file.

## Post-acceptance tasks (not initial-submission blockers)

- Archive the exact code and derived-output version of record in a permanent repository.
- Mint the permanent archive DOI (planned: Zenodo).
- Update the final Open Research Statement with that DOI.
