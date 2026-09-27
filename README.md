# mina

Development and manuscript repository for the **Palmer Archipelago penguin
island-ecology** study.

## Current ecological claim

Five neighboring Adélie penguin island populations share an exceptionally
strong long-term decline, but their annual dynamics and extinction endpoints
are not interchangeable.

Across the complete 1991–2017 five-island Palmer LTER panel:

- PC1 explains **96.4%** of standardized log-abundance variation;
- median pairwise annual-growth correlation is only **0.373**;
- year uniquely accounts for **53.5%** of total log-abundance variance;
- island identity accounts for **33.0%**;
- Litchfield reaches local extinction while four neighboring islands persist at
  low abundance through 2017.

Finite prospective tests did **not** support simple positive annual sea-ice
duration, 3/5/7-year sea-ice-duration rescue, or October snowfall × static
snow-prone-habitat formulations.

The one positive local-state result is narrow: **effective colony number**
(`1 / sum(p_j^2)`) has a positive conditional coefficient (**+0.1168**) and
slightly improves held-out-year next-year growth prediction beyond island,
current abundance and secular time. Active-colony count does not transfer, and
an externally fixed >50-pair threshold improves prediction only with the
opposite coefficient direction to its historical hypothesis.

Independent Torgersen spatial reconstruction shows real breeding-footprint
contraction (23 historic active subcolonies -> five active in 2022) and
topographically non-random attrition. This is **phenomenon-level spatial
convergence**, not colony-ID-level validation: the public LTER `colony_code`
values have not been crosswalked one-to-one to the independent GIS polygons.

## Ecological framing

mina treats penguin breeding islands as **externally subsidized breeding
patches**. Food resources are primarily marine; breeding surfaces are discrete
and terrestrial. Regional marine processes can therefore impose a shared
demographic direction while local snow, geomorphology, colony history and
remaining nest-space organization shape vulnerability.

Direct biotic interactions are not assumed absent. They are treated as
localized and testable rather than as the default explanation for whole-island
trajectories.

## Development state

Core ecological endpoint development is **closed**. The repository terminal
rule forbids opening additional climate windows, precipitation months,
colony-size thresholds or topology indices for the core paper.

Current work is limited to:

- external validation / spatial crosswalk resolution;
- figure and reproducibility packaging;
- manuscript prose, citations and submission materials.

The current reviewer-facing scientific draft is **v0.2**. A journal-targeted **JAE submission draft v0.3** adds a numbered abstract, eight keywords, Materials and Methods naming, a Data Availability statement, an anonymous cover letter and automated Journal of Animal Ecology format checks without changing ecological endpoints.

See:

- `docs/MANUSCRIPT_SPINE_V2.md`
- `docs/MANUSCRIPT_JAE_V0_3.md`
- `docs/COVER_LETTER_JAE_V1.md`
- `docs/JOURNAL_FIT_V1.md`
- `docs/TITLE_PAGE_JAE_TEMPLATE.md`
- `docs/SUBMISSION_CHECKLIST_JAE_V1.md`
- `docs/MANUSCRIPT_V0_2.md`
- `docs/FIGURE_CAPTIONS_V2.md`
- `docs/REVIEWER_AUDIT_V0_1.md`
- `docs/MANUSCRIPT_V0_1.md` (archived first draft)
- `contracts/PALMER_ISLAND_ECOLOGY_SYNTHESIS_V2.json`
- `results/PALMER_MANUSCRIPT_FIGURE_PACKAGE_RESULT_V1.json`

## Reproduce

Install:

```bash
python -m pip install -e ".[dev,figures]"
```

Fetch the frozen census:

```bash
python scripts/fetch_lter_census.py build/adelie_census.csv
```

Primary analyses:

```bash
mina-lter --census build/adelie_census.csv --out build/lter.json
mina-colony-network --census build/adelie_census.csv --out build/colony.json
```

The manuscript figure workflow additionally exports pinned APBP/MAPPPD site
metadata and regenerates Figure 1–4 data before rendering PNG and PDF outputs.

## Provenance

The project began as a biological follow-up to the frozen ODSP Palmer Penguins
audit. ODSP remains the methodological provenance source; all current biological
development and manuscript work belongs in `mina`.
