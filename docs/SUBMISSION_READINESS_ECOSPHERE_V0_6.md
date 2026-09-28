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

## Required submission additions

### Title page

Use `docs/TITLE_PAGE_ECOSPHERE_V0_6_TEMPLATE.md` and prepend the completed title page to the Word Main Document. It must contain journal, manuscript type/track, exact title, all authors and affiliations, one corresponding author/email, Open Research Statement, and 6–12 key words.

### Backmatter

Before References, the submission document must contain:

**Acknowledgments.** Include Palmer Station Antarctica LTER / Palmer Station, Antarctica, relevant funding acknowledgments, and the AI-use disclosure below.

**Author Contributions.** Complete a CRediT-style paragraph only after every author has approved the role assignment.

**Conflict of Interest Statement.** Confirm the actual author status. Do not assume “none” until every author has confirmed it.

### Required AI disclosure

Because OpenAI ChatGPT was used beyond spelling/grammar, the submission must disclose its use both in the manuscript and in ScholarOne. A suitable minimum disclosure is:

> OpenAI ChatGPT (GPT-5.6 Sol) was used during analysis and manuscript development to assist with code drafting and review, statistical sensitivity-analysis scripting, literature searching, and editorial drafting. All analyses were executed from version-controlled code, numerical results were checked against frozen result receipts, cited literature was independently verified, and the authors remain responsible for all analyses, interpretations, and text.

Add an appropriately brief section-level disclosure in the Reproducibility/Methods text and repeat the disclosure in the Acknowledgments. If any additional AI tools were used, expand the statement before submission.

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
- Continuous line numbering beginning after the title page and continuing through References.
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
8. Confirm whether the public GitHub link remains the review code link or is replaced by a private-for-review repository.
9. At acceptance, mint a permanent DOI for the exact code/derived-output release.

The submission guard is intentionally fail-closed: it reports **not ready for ScholarOne** until these author-controlled fields are explicitly resolved.
