# Ecology integrated path/state v0.9 — final production handoff receipt

## 2026-10-16 — final island-scale framing and cover letter v0.6 (editorial only)

**No scientific unfreeze.** To avoid claiming an island colonization mechanism that was not measured, the canonical cover letter was revised to `submission/COVER_LETTER_SPATIAL_RECOVERY_ECOLOGY_V0_6.md` (older v0.5 is retained as provenance). The 1999, 2001 and 2002 Ross data confirm **all six breeding components stayed occupied throughout**, so the focal result concerns unequal compositional recovery of existing local breeding units, **not extinction and recolonization**, or identified inter-island movement. The cover letter keeps the frozen numerical result (96.97% aggregate loss restored, 90.59% six-unit path fidelity, 2.4% six-unit state restoration, corresponding 93.27%/28.3% at three-colony grain), and explains that Palmer, Signy and Beaufort are complementary nonreplicated processes. The old statement of reduced "export" from Beaufort was replaced with the defensible fact of changes in published band resightings.

**Scholarly novelty boundary:** The differentiation of population total, spatial trajectory and relative state is already ecological prior art. The current contribution is a particular quantified natural experiment, not proof of a new MacArthur–Wilson island mechanism or of inherited colony occupancy memory. Strong colony fidelity and available-but-unoccupied breeding habitat were modeled by Matthiopoulos et al. (2005, DOI `10.1111/j.1365-2656.2005.00970.x`), and Antarctic penguin colony geography was already assessed by Santora et al. (2020, DOI `10.1111/geb.13144`). The causal hypothesis involving exogenous nesting-space release, individual breeding pause and former-site reoccupation remains outside this initial submission.

**Reviewer/ethics gate:** the new cover letter contains **visible placeholders** for the corresponding author and an overlap/all-author approval statement, because these are NOT independently confirmed. It must never be sent with placeholders. `submission/SPATIAL_RECOVERY_ECOLOGY_SUBMISSION_MANIFEST_V1.md` now points to the updated letter and clarifies that an actual archival DOI is **not required at initial Article submission**, although DOI-backed data/code archiving is required by acceptance. The public preflight validates numerical consistency with the original Ross result records and keeps the submission blocked pending author-approved final documents.

---


## 2026-10-15 — ESA-compliant code-review scope and corrected publication archive

The first compact review capsule was intentionally limited to frozen Ross reproduction and manuscript figures, but the original 2026-10-07 `spatial-recovery-publication-archive` workflow was **stale**: it referenced v0.2 figure captions and the superseded SI Word builder and did not include the actual Palmer/Signy statistical model source-module dependency tree. ESA's published [Open Research Policy](https://esa.org/publications/data-policy/) requires novel source code for peer review in an external repository and sufficiently complete source/data archives for final publication.

The publication-archive workflow is now `spatial-recovery-publication-archive-v2-staging` (same workflow filename, new internal publication contract). Successful [run #38741761900](https://github.com/zuizui0223/mina/actions/runs/38741761900) generated **58 allowlisted source/code records plus a NOT-FOR-SUBMISSION README and archive manifest** (60 tar entries). It checks all **8 immutable scientific source Git blob SHA-1 values**, includes the correct `FIGURE_CAPTIONS..._V0_3.md` and `build_spatial_recovery_supplement_docx.py`, the bibliography addendum and OpenAI disclosure modules, and recursively bundles the local Python import closure for **original Palmer concentration and Signy replication null models**. An independent extraction successfully imported those historical model modules and regenerated **all 4 main/SI figure PNG+PDF pairs**, rather than merely checking ZIP content.

**Authenticated staging archive SHA256:** `0d581ca5bb6ddce2c9cb0c581168a60267d5699d3993d4c1a8604e27442e4728`, name `Ecology_v09_CODE_RESULTS_REVIEW_STAGING_NOT_DEPOSITED.tar.gz`; [temporary Actions ZIP artifact #11976203413](https://github.com/zuizui0223/mina/actions/runs/38741761900/artifacts/11976203413). Historic Palmer/Signy 100,000-draw null models were **not rerun from externally hosted original raw records** in this staging validation. The *source code* is archived; final original/derived data provenance and licensing still require author-approved archiving decisions. This is not a Dryad/Zenodo deposit, an immutable DOI, a publisher version of record, or an approved submission.

Do NOT mark complete before actual author names/order, author-wide approval, corresponding-author authority, AI tool inventory/Methods/Acknowledgments/ScholarOne disclosure agreement, source license, selection of the permanent repository, final real-author Word/PDF and upload checks. The frozen manuscript v0.8/v0.9 scientific claims were not edited in this production-only change.

---


## 2026-10-15: reduced science-only review capsule independently executed

[Original-data-to-figures workflow #38703651530](https://github.com/zuizui0223/mina/actions/runs/38703651530) completed SUCCESS. The `scripts/build_ecology_v09_reviewer_capsule_v1.py` fixed allowlist isolated 23 publication-relevant scientific files (26 ZIP members including README, requirement pins and SHA manifest) from a much larger historical repository without any real author metadata or other island PRs. All eight scientific frozen Git blob SHA-1 values were verified before packaging. The complete inner reviewer capsule ZIP is 63,192 bytes, SHA256 `0f4fcf96d41961c51ba607ef706b123b2e1386704577a668cdc1cce0834383e7`.

**Independent extraction test**: Within a new directory extracted from the built ZIP, the original Ross scripts recomputed **aggregate restoration 0.969675 and inverse path mismatch 0.094054** to numerical tolerance. The original figure builder generated all four main/SI figure PNGs and four corresponding PDFs from the frozen counts and results receipts. Four figures regenerated, no new ecological effect fitted. See [Actions reviewer-only capsule artifact #11956828405](https://github.com/zuizui0223/mina/actions/runs/38703651530/artifacts/11956828405).

**Crucial scope boundary**: This is a *compact reviewer entry point*, **not** an accepted permanent archiving DOI or a full standalone re-execution of Palmer/Signy 100,000-draw source-data-to-p-value Monte Carlo. For final ESA acceptance, the separately documented full analysis code and legally distributable source/derived data must be made reproducible in a permanent repository. A temporary GitHub Actions artifact can expire and is not an immutable archive; the publicly inspectable original code is in the frozen `mina` branch. Do not overstate completion or cite the capsule as the definitive code/data version of record.

Human author metadata, all-coauthor signoff, actual final Word/PDF proof, AI inventory, licences and external permanent repository remain pending. No journal manuscript sent.

---


## 2026-10-14 follow-up: direct file-level visual QA and tighter Supporting Information layout

After the original 30-page Word mock render, the authenticated GitHub Actions Word artifact was downloaded and rendered to page PNGs/PDF outside CI. The manuscript was visually checked across its 30 pages: no obvious clipping, missing figures, unrendered equation glyphs or truncated references were observed; the original two 300-dpi figure assets were present. Main Figures 1 and 2 remain separate on pages 29 and 30. The figure-caption continuation occupies part of page 28, so the 30-page **real-author** page budget remains tight.

A small **production-only** change to `scripts/build_spatial_recovery_supplement_docx.py` removed an unnecessary forced page break before the two-sentence "Inferential boundary" paragraph. **No scientific claim, caption wording or figure changed.** The paragraph now appears immediately after Figure S2 on page 2. Authenticated [SI/Word preview rerun #38563299801](https://github.com/zuizui0223/mina/actions/runs/38563299801) **SUCCESS**; the actual PDFs (LibreOffice/PDFInfo) measured **30 pages main and 2 pages Supporting Information**, including synthetic author-stress main (30 pages). Base [CI #38563299905](https://github.com/zuizui0223/mina/actions/runs/38563299905) and [publication freeze/preflight #38563299716](https://github.com/zuizui0223/mina/actions/runs/38563299716) also **SUCCESS**.

Final author-submitted Word/PDF has NOT been created or approved. The current text, figure labels, and page counts describe synthetic author metadata only. Before actual submission, regenerate from private, approved real author information and visually check every final page and ScholarOne combined proof. This note supersedes the prior *SI three pages* count; it does not supersede any scientific freeze or author-consent requirements.

---


**Date:** 2026-10-14 (Asia/Tokyo).  
**Disposition:** **READY FOR HUMAN AUTHOR INFORMATION / CONSENT, NOT SUBMITTED.**  
**Target:** *Ecology* (Ecological Society of America), Article.  
**Canonical code/manuscript branch:** `analysis/ross-sea-expansion-intensification-support-v1`.  
**Original scientific freeze:** `3e8882742ca2affc6717d373fd9b6d903b01f4c1`.  
**Frozen research/biological endpoints:** UNCHANGED; source v0.8 and production v0.9 preserved.

## Executed QA with real GitHub Actions provenance

| Check | CI run | Result |
| --- | --- | --- |
| Complete standard `ci` (`pytest`) | [#38506791383](https://github.com/zuizui0223/mina/actions/runs/38506791383) | SUCCESS |
| Original freeze SHA / author metadata & disclosure preflight | [#38506791501](https://github.com/zuizui0223/mina/actions/runs/38506791501) | SUCCESS; submission result `BLOCKED_BEFORE_REAL_SUBMISSION` (expected) |
| Production DOCX + synthetic named and stress samples, SI + PDF-render pagination | [#38506791586](https://github.com/zuizui0223/mina/actions/runs/38506791586) | SUCCESS |

**Page counts measured by new headless LibreOffice PDFInfo check, not inferred:**

- `Spatial_Recovery_Ecology_v0_9_SYNTHETIC_COMPLETE.docx` -> **30 PDF pages**.
- `Spatial_Recovery_Ecology_v0_9_METADATA_STRESS.docx` (eight fictitious authors, four fictitious affiliations, long funding and CRediT text) -> **30 PDF pages**.
- Both are **fictional author metadata**, NOT the final author's manuscript. Neither page count licenses final submission. The actual author-approved text (including grants and AI disclosure) must be rendered anew and both final DOCX and ScholarOne PDF inspected.

[Preview DOCX bundle and check receipts](https://github.com/zuizui0223/mina/actions/runs/38506791586/artifacts/11868495773).

## Publication-only improvements, with frozen science intact

- Original scientific sources verified byte-identical at the 8 frozen Git blob SHAs. See `submission/ECOLOGY_SPATIAL_RECOVERY_FREEZE_BLOB_VERIFICATION_20261014.md`, including original freeze log's 2-character typo correction for the spatial grain JSON.
- Source dataset bibliography citations for Ross `10.7931/kf06-x745`, Palmer `10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e` and Signy `10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d` added **only** to author-named publication derivative from `submission/ECOLOGY_SOURCE_DATASET_BIB_ADDENDUM_20261014.bib`. Original frozen bibliography not changed. Authors must verify exact dataset versions/credit prior to submission.
- `src/mina/ecology_ai_submission_disclosure.py` supports author-reviewed AI Methods and Acknowledgments text, rather than assuming the prior mock fixed `GPT-5.6 Sol` was a complete inventory. `src/mina/ecology_submission_source_citations.py` adds dataset citations to corresponding production Methods. Both only insert if named author metadata file is explicitly passed.
- `scripts/build_spatial_recovery_ecology_docx.py` renders these production-only disclosures and Bib addendum, while enforcing source/AI inventory and intended archive input when `--require-complete-metadata`. Methodological results unchanged.
- Public `submission/ECOLOGY_INITIAL_SUBMISSION_METADATA_TEMPLATE_20261014.json` contains **no private identifying information**. Filled copy must remain private. `scripts/audit_ecology_submission_handoff_v1.py` verifies freeze, bibliographic and production dependencies, then blocks until actual author signoffs are true.

## Honest current outstanding AUTHOR-ONLY items

- [ ] Agree all actual author identities/order, affiliations, corresponding author and email, present addresses / ORCIDs.
- [ ] Agree funding/grants, acknowledgments, CRediT, potential conflict-of-interest text.
- [ ] Confirm **full** AI tool/model inventory and actual activity; approve Methods and Acknowledgments; use matching ScholarOne disclosure form.
- [ ] Confirm dual-publication/preprint/overlap, all-author approval of final submission, associated source licenses and acknowledgments.
- [ ] Select intended permanent repository and publicly reviewed branch/version; **permanent DOI is not required at initial Article submission** but an appropriate immutable deposit/identifier is needed by acceptance per ESA open research policy.
- [ ] Render final **real-author** Word, inspect figures/equations/lines/references; recheck actual page count and ScholarOne proof. A 30-page fictional proof is not sufficient.
- [ ] Corresponding author submits the accepted final files in the authorised ScholarOne account. Nothing has been submitted by this research automation.

## Official policies to re-check at actual submission

- [ESA Author Instructions](https://esajournals.onlinelibrary.wiley.com/hub/journal/19399170/author-guidelines).
- [ESA Open Research Policy](https://esa.org/publications/data-policy/).
- [ESA AI Policy](https://esa.org/publications/artificial-intelligence-ai-policy/).
- [ESA Ethics](https://esa.org/about/code-of-ethics/).

**Stop:** no new Ross / Palmer / Signy / Beaufort / Zavodovski / Béchervaise endpoints, code tuning or new null searches before initial submission. PR #173 is superseded; PR #196 is explicitly paused; no Béchervaise email sent (user chose to skip). Keep PR #189 as the ONE active manuscript production lane.
