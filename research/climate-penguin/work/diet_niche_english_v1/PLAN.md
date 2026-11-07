# English manuscript implementation plan

> **For agentic workers:** Primary execution with isolated parallel drafting and a final independent scientific review. The user has opted for autonomous continuation; no approval handoff is required.

**Goal:** Deliver complete editable English main and supplementary manuscripts with the existing scientific results and six figures.

**Architecture:** Pin source files, draft two Markdown manuscripts, build Word documents with Python and native math, verify content, render every page and publish the same checked files.

**Tech Stack:** Bundled primary-runtime Python, python-docx, lxml, Pandoc for Markdown parsing/native math, packaged document renderer.

**Spec:** [DESIGN.md](DESIGN.md).

## Global constraints

Preserve all estimands, numerical results and scientific qualifications in the design. Existing analysis code, Japanese scientific text and source figures are immutable inputs. Do not fill author-specific declarations or submit to a journal. Work on the existing clean draft branch, not main or frozen Paper1/Paper2.

## Review focus

1. The difference between counts of stomachs, seasons and sites must survive English editing.
2. The three diet denominators and the non-product of fitted curves must be explicit.
3. Absolute future values, changes, coefficient intervals and unsupported conditions must stay distinct.
4. Table and figure numbering, native equations and all manuscript content must survive conversion to Word.
5. Bibliographic details must match verified records; declarations cannot become invented author assertions.

## Tasks

- [x] **1. Pin and draft.** Save `SOURCE_MANIFEST.json`; create `MANUSCRIPT_EN.md` and `SUPPLEMENT_EN.md`; retain exact numerical tables and all six figure links. Review the text and abstract length.
- [x] **2. Build and inspect.** Implement `work/diet_niche_english_v1/build_documents.py`; create two DOCX files; render using the packaged `render_docx.py`; inspect every page and correct layout issues.
- [x] **3. Verify scientific fidelity.** Independently check claims, saved numerical sources, definitions, references, figure identity and complete text transfer. Save `VALIDATION.json` and a scoped review record.
- [ ] **4. Integrate and deliver.** Add README/current-status links, commit once, update the existing PR206 by expected-head lease, and verify exact remote/local tree equality.

## Progress ledger

- Base commit: `a0b678bad6b8bd57d1f73e687aa6c415416aebb3`; clean branch `codex/climate-penguin-progress`; remote PR206 open and draft at the same commit.
- Scoping: independent manuscript review found English text and Word packaging to be the concrete missing deliverable. Timing review found no unused Gentoo overlap supporting a new simultaneous three-axis model.
- Pre-flight: both drafts consume pinned results and figure files; the builder consumes Markdown links and native math; final checks consume the built documents and unchanged source values.
- Ruling: preserve the current isolated draft branch and use exclusive file ownership instead of creating another checkout. The work is document generation on an already authorized branch.
- Ruling: use document/source checks and full-page visual review rather than new unit tests that would mirror the formatter. Scientific analyses remain unchanged.

## Completion evidence before publication

- English main and Supplement S1–S9 are complete; the abstract is 233 words. Original scientific text, numeric inputs and figure files remain unchanged. Nine official CMIP6 experiment citations are now mapped to the analysed members and source versions.
- The independent numerical review matched 71/71 displayed table rows and manually checked the other key values and scientific qualifications. `REVIEW.json` has no unresolved blockers.
- The final document checks passed 95/95, including ordered full-text transfer, 30 pinned inputs, six unchanged embedded figures, 150 native equations, 14 physical tables and local links.
- All 15 main and 14 supplement pages were visually inspected. Short-table splitting, an isolated Figures heading, references below Figure 4, an empty break page and an isolated final dataset citation were corrected before the final render.
- Formatter diagnoses: trim boundary newlines before passing display math to Pandoc; disable implicit-figure AST nodes because captions are explicit; resolve the Palmer provenance path under work/sources; attach page breaks to content instead of an empty paragraph. These were conversion/layout fixes, not scientific revisions.
- README and synthesis entry points are updated. Step 4 is prepared at this snapshot: publication must occur after the containing commit, with expected parent `a0b678bad6b8bd57d1f73e687aa6c415416aebb3` and exact-tree verification. The current head of Draft PR206 and the final delivery response record that post-commit outcome.
