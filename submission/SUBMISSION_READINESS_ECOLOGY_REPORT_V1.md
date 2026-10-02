# Ecology Report submission readiness v1

Checked against the official *Ecology* author guidelines revised September 2026.

## Submission type

**Report**

Rationale: the manuscript makes one concise scientific statement—declining colonial penguin populations lose effective breeding-component number faster than proportional thinning predicts—and tests it through a discovery system, an external replication and a cross-species replication.

Official limit:
- 20 manuscript pages including title page, text, references, captions and figures
- abstract ≤200 words
- keywords required

Current package:
- title: **Breeding-space contraction recurs across declining Adélie and chinstrap penguins**
- title length: 80 characters
- manuscript rough word count: ~2,100 before full references
- abstract: 173 words
- keywords: 8
- main figures: 3
- tables: 0

## Scientific package

### Primary discovery
results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json

### Prospective external replication
contracts/SIGNY_BREEDING_PATCH_CONCENTRATION_V1.json
results/SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json

### Prospective cross-species replication
contracts/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_V1.json
results/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json

### Post-hoc descriptive mechanism boundary
contracts/CONCENTRATION_DOMINANCE_DESCRIPTIVE_V1.json
results/CONCENTRATION_DOMINANCE_DESCRIPTIVE_SUMMARY_V1.json

### Figure reproducibility
scripts/build_replicated_concentration_figure_data.py
scripts/plot_replicated_concentration_figures.py
.github/workflows/replicated-concentration-figures.yml

The figure-data builder re-downloads the frozen public Palmer and Signy sources and asserts that recomputed N_eff endpoints and slopes match the frozen result receipts before rendering figures.

## Figure files

The submission workflow generates each figure as:
- PDF — preferred Ecology submission format
- PNG — review/preview copy
- SVG — editable vector archive

Required files:
1. figure1_replicated_trajectories.pdf
2. figure2_cross_population_summary.pdf
3. figure3_dominance_routes.pdf

Captions:
docs/FIGURE_CAPTIONS_REPLICATED_CONCENTRATION_V0_2.md

## Main document order required by Ecology

The final Word main document should contain, in order:

1. Title page
   - journal name: Ecology
   - manuscript type: Report
   - title
   - author list
   - affiliations
   - corresponding author + email
   - Open Research Statement
   - keywords
2. Abstract on a new page
3. Main text
4. Acknowledgments
5. Author Contributions
6. Conflict of Interest Statement
7. References
8. Figure captions, grouped together
9. Figures, if embedded rather than uploaded separately

Formatting for final submission:
- Word (.doc/.docx) preferred
- 12-point Times New Roman
- double-spaced
- continuous line numbers after title page
- page numbers
- Letter page size
- 1-inch margins
- left aligned

## Items still requiring author-supplied metadata

These cannot be inferred safely from the repository and must be filled before submission:

- final author list and order
- affiliations
- corresponding author email
- acknowledgments/funding statement
- CRediT/author-contribution statement
- conflict-of-interest statement
- Open Research Statement wording and final repository/archive URL
- whether a preprint has been or will be posted

## Submission text files

- manuscript: submission/MANUSCRIPT_ECOLOGY_REPORT_V0_3.md
- cover letter: submission/COVER_LETTER_ECOLOGY_REPORT_V1.md
- references: docs/REFERENCES_V6.bib
- figure captions: docs/FIGURE_CAPTIONS_REPLICATED_CONCENTRATION_V0_2.md
- literature positioning: docs/LITERATURE_POSITIONING_REPLICATED_CONCENTRATION_V1.md

## Claim boundary before submission

Do not add new ecological endpoints.

Main claim:
> Declining breeding populations in two Pygoscelis species and two Antarctic monitoring systems lost effective breeding-component number faster than expected under proportional thinning plus the frozen count-error family.

Secondary descriptive claim:
> Palmer populations reached that endpoint through dominance turnover, whereas both Signy populations showed dominant-core retention.

Do not claim:
- universal large-colony resilience
- individual dispersal or public-information mechanism
- early-warning prediction
- physical occupied area from N_eff
- applicability to all penguins
- first observation of colony/subcolony extinction

## Journal routing

Primary submission: **Ecology — Report**

If rejected for editorial fit rather than a fatal scientific issue:
1. **Journal of Animal Ecology — Research Article**, reframing the general contribution as a principle of spatial animal-population decline and converting the abstract to the journal's required numbered-statement format.
2. **Ecosphere** or **Ecology and Evolution** as broader-scope fallback without changing the scientific claim.
