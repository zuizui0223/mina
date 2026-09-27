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

Effective colony number (`1 / sum(p_j^2)`) has a positive conditional
coefficient (**+0.1168**) after island, current abundance and time are
controlled. However, its small held-out MSE gain (**+0.00103**) is compatible
with synchronized year-block permutation noise (**p = 0.262**), so it is no
longer treated as a supported predictive result. The coefficient itself remains unusual under serial-structure-preserving
surrogates: 100,000 independent island-wise circular shifts produced no
coefficient as large as observed (p < 1e-5), and an exact shift preserving
cross-island N_eff covariance among the four persistent islands gave p = 1/416
= 0.00240. Repeating the fixed Poisson / 10% / 20% Gamma-Poisson count-error
coupling sensitivities on circularly shifted latent topology also retained the
association (largest coupled-null p = 0.00780). It is therefore retained as a
bounded conditional association, not a supported predictor or causal mechanism.

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

## Submission status after N_eff uncertainty diagnostics

**JAE submission remains paused.** The frozen 20,000-replicate year-block
permutation shows that the observed held-out MSE gain (+0.00103) is not unusual
(one-sided **p = 0.262**; observed percentile **73.8%**). The subsequent serial-structure correction shows that the +0.1168 coefficient
remains extreme under autocorrelation-preserving circular shifts and under the
same fixed count-error sensitivities rebuilt on that structured topology null.
This addresses the spurious-regression concern without restoring the failed
predictive claim.

The evidence therefore supports **association without robust out-of-year
prediction**. The manuscript has been reframed as v0.4 with **Ecosphere as the
recommended first shot** and **Ecology and Evolution as fallback**. Archived
JAE v0.3/v0.3.1 files remain provenance only.

## Development state

Core ecological endpoint development is **closed**. The repository terminal
rule forbids opening additional climate windows, precipitation months,
colony-size thresholds or topology indices for the core paper.

Current work is limited to:

- external validation / spatial crosswalk resolution;
- figure and reproducibility packaging;
- manuscript prose, citations and submission materials.

The current scientific draft is **Ecosphere-oriented v0.5**, reconciled after
the year-block predictive-gain test, autocorrelation-preserving circular-shift
coefficient tests, and circular-shift count-error diagnostics. PC1/synchrony is now explicitly
descriptive context within established scale-dependent synchrony theory;
Palmer Penguins is removed from the primary Introduction motivation; and N_eff
is described only as a conditional association.

See:

- `docs/MANUSCRIPT_ECOSPHERE_V0_5.md`
- `docs/JOURNAL_FIT_V3.md`
- `docs/JOURNAL_FIT_V2.md` (pre-circular-shift journal-fit record)
- `docs/FIGURE_CAPTIONS_V4.md`
- `docs/REFERENCES_V3.bib`
- `docs/MANUSCRIPT_SPINE_V4.md`
- `docs/MANUSCRIPT_JAE_V0_3.md`
- `docs/COVER_LETTER_JAE_V1.md`
- `docs/JOURNAL_FIT_V1.md`
- `docs/TITLE_PAGE_JAE_TEMPLATE.md`
- `docs/SUBMISSION_CHECKLIST_JAE_V1.md`
- `docs/MANUSCRIPT_V0_2.md`
- `docs/FIGURE_CAPTIONS_V2.md`
- `docs/REVIEWER_AUDIT_V0_1.md`
- `docs/MANUSCRIPT_V0_1.md` (archived first draft)
- `contracts/PALMER_ISLAND_ECOLOGY_SYNTHESIS_V4.json`
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
