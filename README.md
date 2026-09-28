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

The nested variability analysis identifies an **observed scale hierarchy**,
but its biological interpretation is now explicitly measurement-error
bounded. In the three islands with unchanged colony-code rosters (Cormorant,
Humble and Litchfield), raw Wang–Loreau beta variability is **1.0737** from
colony-code components to islands but only **1.0112** from islands to the
archipelago; **86.4%** of the observed additive log-beta transition occurs at
the within-island step. Under a complete-synchrony error null, this raw contrast
is extreme under independent Poisson and Gamma–Poisson CV10% error
(**p < 0.00001** for both) but is ordinary under the frozen CV20% sensitivity
(**p = 0.448**). Detrended and annual-growth versions are compatible with
error-only nulls even at lower error, so they are not treated as stronger
evidence for biological buffering. The public census lacks record-level error
calibration, so the hierarchy is retained as count-error-sensitive descriptive
evidence rather than a demonstrated buffering mechanism.

Finite prospective tests did **not** support simple positive annual sea-ice
duration, 3/5/7-year sea-ice-duration rescue, or October snowfall × static
snow-prone-habitat formulations.

Effective colony number (`1 / sum(p_j^2)`) remains a secondary,
bounded result. Its standardized conditional coefficient is **+0.1168** after
island, current abundance and time are controlled. Conditioning on the
preceding two annual growth intervals leaves a coefficient of **+0.1126**
(**96.4%** of the original), and the same full-series structured null remains
unusual (100,000 independent circular shifts: **p = 0.00102**; exact
covariance-preserving shifts: **5/416 = 0.0120**). In contrast, the
two-lag held-out MSE gain is only **+0.000444**, and the original held-out gain
(**+0.00103**) is compatible with synchronized year-block permutation noise
(**p = 0.262**). Fixed circular-shift count-error sensitivities also retain the
association (largest coupled-null p = 0.00780). N_eff is therefore retained as
a weak but structured-null- and momentum-robust conditional association, not a
supported predictor, causal mechanism or early-warning indicator.

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

## Submission status after hierarchy and N_eff robustness diagnostics

**JAE submission remains paused.** The frozen 20,000-replicate year-block
permutation shows that the observed held-out MSE gain (+0.00103) is not unusual
(one-sided **p = 0.262**; observed percentile **73.8%**). The subsequent serial-structure correction shows that the +0.1168 coefficient
remains extreme under autocorrelation-preserving circular shifts and under the
same fixed count-error sensitivities rebuilt on that structured topology null.
This addresses the spurious-regression concern without restoring the failed
predictive claim.

The current positive evidence is deliberately split. The raw census shows a
nested variability contrast that survives low-to-moderate stylized count error
but not the frozen 20% sensitivity; this is **not** promoted as a
measurement-error-robust buffering result. Separately, N_eff remains a weak but
structured-null-, momentum- and count-error-robust conditional association
without robust out-of-year prediction. The current manuscript is **v0.7**,
with **Ecosphere as the recommended first shot** and **Ecology and Evolution as
fallback**. v0.6, v0.5 and the archived JAE v0.3/v0.3.1 files remain
provenance only.

## Development state

Core same-census endpoint development is **closed at v0.7**. The repository
terminal rule forbids opening additional hierarchy metrics, beta definitions,
colony-roster reconciliations, climate windows, precipitation months,
colony-size thresholds or topology indices for the core paper.

Current work is limited to:

- external validation / spatial crosswalk resolution;
- figure and reproducibility packaging;
- manuscript prose, citations and submission materials.

The current scientific draft is **Ecosphere-oriented v0.7**. PC1/synchrony
remains descriptive context within established scale-dependent synchrony
theory. The nested subcolony–island–archipelago variability result is retained
with an explicit count-error boundary, and the detrended/growth hierarchy is
not used as independent support. N_eff remains a separate conditional
association with frozen one- and two-year demographic-momentum and count-error
sensitivities.

See:

- `docs/MANUSCRIPT_ECOSPHERE_V0_7.md`
- `docs/MANUSCRIPT_SPINE_V6.md`
- `docs/FIGURE_CAPTIONS_V6.md`
- `docs/REFERENCES_V4.bib`
- `docs/HIERARCHICAL_VARIABILITY_EXTENSION_V1.md`
- `results/PALMER_HIERARCHICAL_VARIABILITY_RESULT_V1.json`
- `results/PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json`
- `results/PALMER_NEFF_DEMOGRAPHIC_MOMENTUM_RESULT_V1.json`
- `docs/MANUSCRIPT_ECOSPHERE_V0_6.md` (provenance)
- `docs/MANUSCRIPT_ECOSPHERE_V0_5.md` (provenance)
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
mina-hierarchical-variability --census build/adelie_census.csv --out build/hierarchy.json
mina-neff-momentum --census build/adelie_census.csv --out build/neff_momentum.json
```

The manuscript figure workflow additionally exports pinned APBP/MAPPPD site
metadata and regenerates Figure 1–5 data before rendering PNG and PDF outputs.

## Provenance

The project began as a biological follow-up to the frozen ODSP Palmer Penguins
audit. ODSP remains the methodological provenance source; all current biological
development and manuscript work belongs in `mina`.
