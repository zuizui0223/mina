# Ecology Article v0.9 — initial submission handoff and required confirmations

**As checked:** 2026-10-14. **Current disposition:** scientific package frozen; mock/placeholder production QA previously passed; submission **NOT SENT**; author-approved production not yet rendered.

## Exact canonical package (no new ecological analysis)
- Manuscript: `docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md`
- Scientific freeze: `docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_8.md` (frozen head `3e8882742ca2affc6717d373fd9b6d903b01f4c1`)
- Reference library: `docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib`
- Two main figure captions: `docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_3.md`
- Supplement: `submission/SUPPLEMENT_SPATIAL_RECOVERY_PATH_STATE_V1.md`
- Main Word builder: `scripts/build_spatial_recovery_ecology_docx.py`
- Review code + original result receipts: public `https://github.com/zuizui0223/mina/tree/analysis/ross-sea-expansion-intensification-support-v1`
- Cover letter: `submission/COVER_LETTER_SPATIAL_RECOVERY_ECOLOGY_V0_5.md` (signature is placeholder).
- Submission copy fields: `submission/ECOLOGY_SPATIAL_RECOVERY_COPY_FIELDS_V1.md`
- Reproducibility statement: `submission/OPEN_RESEARCH_STATEMENT_SPATIAL_RECOVERY_V1.md`

## Verified journal policy

**Ecological Society of America, Ecology Article:**
- Standard main-file limit **30 pages** including title page, body, references, figure captions and main figures; Supporting Information does not count. Articles from 31–50 pages need two numbered justifications in the cover letter. Abstract **≤350 words**. The existing production QA recorded a **30-page mock author-complete rendering** and **196-word abstract**; **real-author rendering must be repeated** after final names and AI disclosure.
- ESA Open Research: publicly available source-data DOIs should be cited. Novel analytical code must be available during peer review in an external repository, and a public GitHub repository is allowed for review. Public permanent archive on acceptance is required: **GitHub alone is not an immutable DOI archive**. If choosing GitHub→Zenodo, obtain a real Zenodo DOI before the final accepted publication; never invent it. Data need not be deposited at initial submission for a standard Article, but source data and derived products must be publishable and properly archived by acceptance; some original data may be linked rather than re-distributed depending on terms.
- ESA AI policy: analytical or writing AI assistance is disclosed in relevant manuscript section(s), plus Acknowledgments and ScholarOne declaration; AI is not an author.
- Authorship & ethics: each author must consent to the submitted version and order. Dual-publication/overlap and any previously published source-data reuse must be disclosed in ScholarOne appropriately.

**Official pages:**
- https://esajournals.onlinelibrary.wiley.com/hub/journal/19399170/author-guidelines
- https://esa.org/publications/data-policy/
- https://esa.org/publications/artificial-intelligence-ai-policy/
- https://esa.org/about/code-of-ethics/
- https://esa.org/publications/be-an-author/submit-a-manuscript/

## Source identifiers independently checked on 2026-10-14

- Ross Adélie aerial census: `10.7931/kf06-x745` — public Landcare Research DataStore; confirm raw source version/year and license before redistributing copies.
- Palmer Adélie LTER annual census: `10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e` — public Palmer LTER ERDDAP.
- Signy Adélie breeding success: `10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d` — original BAS record GB/NERC/BAS/PDC/01535 (Dunn et al. 2021).
- Beaufort change/movement: LaRue et al. 2013, DOI `10.1371/journal.pone.0060568` (published paper, not a substitute for specifying reused Ross census data).
- Any data derived for the reported Tables/Figures require archived provenance, correct citations and transparent permissions. Do not add unsupported raw data sets or reproduce third-party licensed imagery.

## What is genuinely done

- [x] Frozen science integrity checked for 8 critical blobs, unchanged since original head.
- [x] Historical 2-character SHA typo identified and documented separately: `submission/ECOLOGY_SPATIAL_RECOVERY_FREEZE_BLOB_VERIFICATION_20261014.md`.
- [x] Journal Article category and abstract length fit the frozen **mock** submission audit.
- [x] Published data-source DOIs above individually source-checked.
- [x] Existing figure arrangement: 2 main figures, 2 supporting figures.
- [x] Previous Word preview structural and visual QA recorded as pass, *only for placeholder author metadata*.
- [x] One canonical submission lane: path/state v0.9; separate Palmer/Ecosphere, standalone Ross and older integrated drafts remain provenance, **not concurrent submissions**.

## Still human-gated / must NOT be guessed

- [ ] all actual authors, agreed author order and precise affiliations (with ORCID as appropriate);
- [ ] corresponding author, verified email, authority to submit and documented approval of the final manuscript by all coauthors;
- [ ] funding identifiers, acknowledgments and CRediT roles;
- [ ] conflicts of interest, research/data rights, source-data licenses and appropriate credit;
- [ ] AI tool/model inventory, which methods and text tasks used which tools, Methods + Acknowledgments + ScholarOne disclosure consistency;
- [ ] Open Research code-for-review access with fixed version, data/derived-data storage plan naming intended permanent repository; archive DOI is **not mandatory for first Article submission**;
- [ ] dual-publication/preprint/overlap truthfully declared;
- [ ] final author-complete DOCX, appended disclosure, page limit and ScholarOne assembled-PDF visual QA.

**Safeguard:** This public branch contains an unfilled `ECOLOGY_INITIAL_SUBMISSION_METADATA_TEMPLATE_20261014.json` only. Save a filled copy PRIVATELY off-repository; run the audit tool below using its local path and never commit authors' private contact or author-approval records. No corresponding author details, grants, signatures, AI-model inventory or permanent DOI have been invented.

## Command handoff

```bash
python scripts/audit_ecology_submission_handoff_v1.py --out /tmp/ecology_preflight.json
python scripts/audit_ecology_submission_handoff_v1.py --metadata /PRIVATE/PATH/submission_metadata.json --out /tmp/ecology_author_preflight.json
# The 2nd call must remain blocked unless every author-controlled item and final Word/PDF QA is confirmed.
```

**Decision:** Submit ONE frozen scientific manuscript after human-controlled metadata and proofing; **no further ecological endpoints or causal mechanism searches** before initial submission.
