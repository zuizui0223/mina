# Ecology Article cross-scale submission readiness v0.1

## Scientific status

**Scientific analysis is closed. Packaging QA is temporarily reopened for the publication-sized figures, current-head Main Document, and Appendix S1 PDF. No new ecological endpoint may be added.**

The active manuscript is now organized as an Ecology **Article**, not a Report. The change is editorial rather than scientific: the cross-scale extension adds a distinct regional inferential component, while the results and claim boundaries remain those already frozen.

## Ecology format checks

- Article page limit: 30 pages.
- Article abstract limit: 350 words.
- Current abstract: 259 words.
- Ecology title limit: 120 characters.
- Current title: 83 characters.
- Keywords: 8, within the required 6–12 range and alphabetized.
- Main-document body will be double-spaced, 12-point Times New Roman, Letter size with 1-inch margins.
- Line numbering begins after the title page and continues through References.
- Open Research Statement is on the title page.
- Figure captions are grouped in the Main Document; figures are also retained as separate high-quality files.
- Supporting Information is a separate file.

## Policy and disclosure checks

- AI-use disclosure is present in the applicable Methods section.
- AI-use disclosure is repeated in Acknowledgments.
- Submission-form AI disclosure copy is prepared.
- Long-term data providers are acknowledged in the generated Main Document.
- Open Research Statement is present on the title page.
- Figure captions contain no equations.

## Scientific checks

- Palmer remains explicitly the discovery system, with inference limited to three fixed sample-colony monitoring networks; summed monitored-component abundance is not described as exhaustive island-population abundance.
- Signy Adélie remains the independent geographic replication.
- Signy chinstrap remains the prospective cross-species replication.
- MAPPPD remains a scale-transfer test rather than an additional independent geography.
- Local and regional statistics are not pooled.
- Regional 4/4 sign concordance among declining panels is descriptive.
- The two regional p<0.05 panel calls are not presented as a family-wide generality test.
- All three increasing regional panels ending with lower E are treated as a major interpretive boundary, not as a preregistered ratchet test.
- The manuscript no longer claims that regional concentration is decline-specific.
- Universal kappa, trend-independent concentration, hysteresis and mechanism claims remain prohibited.

## Remaining blockers

Current packaging blockers are: (1) corrected Main Document regeneration and visual/page-count QA after the Palmer source-provenance correction, (2) corrected Appendix S1 build/QA, and (3) author-controlled metadata. Main-figure numerical content is unchanged. Permanent archiving can be completed later and is not required to open the initial submission.

## Canonical freeze

See `contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json`.


## Word Main Document QA

The previously rendered placeholder Ecology Article Main Document passed QA before the Palmer source-provenance wording correction and is now superseded for upload. Ecology counts separately uploaded figure pages toward the page limit, so the 24-page Main Document plus three one-page main figures gives an expected 27-page generated manuscript.

- rendered Main Document pages: **24**
- separately uploaded main-figure pages: **3**
- expected generated manuscript pages: **27**
- Ecology Article limit: **30 pages**
- all 24 pages visually inspected
- title page correctly labeled **Article**
- line numbering starts after the title page and continues through References and figure captions
- display and inline manuscript equations render correctly
- References render without clipping
- only Figures 1–3 are captioned in the Main Document
- Figure S1 caption is held outside the Main Document with the Supporting Information
- no clipping, overlap or missing glyphs detected

Provenance is frozen in `submission/ECOLOGY_ARTICLE_CROSS_SCALE_DOCX_QA_RECEIPT_V0_1.json`.

This prior QA remains provenance only. A corrected placeholder preview must first pass a fresh render check; once private author metadata are confirmed, the author-complete DOCX must be regenerated through the same builder and checked again before upload.


## Superseded pre-correction Word artifact

- workflow run: `37117211288`
- artifact: `11271907803`
- digest: `sha256:310d1eb394dda79cb4d3d0552edd40f70f68f97a4598fbd41ffae6552833364b`
- rendered Main Document: **24 pages**
- expected generated manuscript with three separate main-figure pages: **27/30 pages**


## Packaging QA reopened

The earlier 24-page Main Document and figure artifacts remain valid provenance, but they are no longer the final upload artifacts because subsequent compliance work added Appendix S1 references and changed figure dimensions to the Ecology publication-size limit. Final-gate status is therefore temporarily PENDING until the replacement DOCX, figures and Appendix S1 PDF pass QA.
