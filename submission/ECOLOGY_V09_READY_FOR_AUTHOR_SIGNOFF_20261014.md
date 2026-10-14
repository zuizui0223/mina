# Ecology integrated path/state v0.9 — final production handoff receipt

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
