# English manuscript and supplement

Editable English paper based on the frozen Signy dietary analyses, the Palmer comparison and conditional sea-ice scenarios. The scientific and numerical scope matches the Japanese manuscript; this package adds English text, native Word equations and embedded original figures and tables.

## Deliverables

- [Signy_diet_manuscript.docx](Signy_diet_manuscript.docx): complete main manuscript, main Tables 1–3 and Figures 1–4.
- [Signy_diet_supplement.docx](Signy_diet_supplement.docx): supplementary methods and results S1–S9, Tables S1–S8 and Figures S1–S2.
- [MANUSCRIPT_EN.md](MANUSCRIPT_EN.md) and [SUPPLEMENT_EN.md](SUPPLEMENT_EN.md): editable source text for the two Word documents.

The supplement includes **nine formal CMIP6 experiment-collection dataset references**, covering historical, SSP2-4.5 and SSP5-8.5 inputs for ACCESS-CM2, BCC-CSM2-MR and CESM2. [CMIP6_CITATIONS.csv](CMIP6_CITATIONS.csv) and the [citation audit](CMIP6_CITATION_AUDIT.md) map those references to the actual analysed members and source versions. The existing nine observational-data and research references remain in the main manuscript.

## Reproduce the documents

From the repository root, with Pandoc available and the primary Python runtime containing python-docx, lxml and Pillow:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" research/climate-penguin/work/diet_niche_english_v1/build_documents.py
"$CODEX_PRIMARY_RUNTIME_PYTHON" research/climate-penguin/work/diet_niche_english_v1/verify_documents.py
```

The builder writes both DOCX files and [BUILD_MANIFEST.json](BUILD_MANIFEST.json). The verifier reads the existing files and prints a JSON report; it checks all 30 pinned inputs, source and Word hashes, complete visible-text order after whitespace normalization, embedded figure bytes, native equation and table counts, local links and abstract length. Equations and images use placeholders in the text comparison and receive separate structural and image-byte checks. It does not rerun ecological analyses or replace visual inspection of rendered pages. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) records the frozen inputs; [REVIEW.json](REVIEW.json) records the independent scientific-fidelity review. Original analysis reproduction commands remain in the [Japanese manuscript README](../diet_niche_manuscript_v1/README.md).

## Validation

The main document renders to 15 pages and the supplement to 14. All 29 pages were visually inspected after pagination corrections. The read-only document checks passed 95/95; the independent scientific review matched all 71 automatically compared table rows and checked the remaining reported values. See [VALIDATION.json](VALIDATION.json), [main visual review](VISUAL_QA_MAIN.json) and [supplement visual review](VISUAL_QA_SUPPLEMENT.json). No ecological model was refitted.

## Author inputs still required before submission

Supply and confirm author names, affiliations, corresponding-author details, author contributions, funding, competing interests, acknowledgments and the required ethics/permit/data-use statements. Select the target journal and apply its submission format. Assign a permanent code-and-results release identifier. These items are deliberately unfilled; no submission or invented author declaration is implied.
