# Climate relationships and warming scenarios implementation plan

> Execute the already approved research direction without a new approval round.

**Goal:** Quantify penguin relationships with vegetation, sea ice and salinity, and establish a reproducible path to conditional warming projections.

**Architecture:** Preserve the PR206 source snapshot and all historical results. Add three self-contained analyses: same-cohort September settlement relationships/forward prediction; vegetation–breeding associations in the vegetation-map period; and actual historical/future CMIP6 driver extraction. These answer distinct stages of one research objective.

**Tech stack:** Python, pandas/numpy/scipy, matplotlib, xarray/fsspec/zarr; isolated runtime `/tmp/mina_climate_env`.

**Spec:** `research/climate-penguin/outputs/climate_penguin/RESEARCH_GOAL_V2.md`, plus the user's 2026-10-30 instruction retaining vegetation, sea ice, salinity and warming prediction.

## Constraints

- Source base: PR206 `0035a298f48534785cd2bf7cf76f35c5a66f8428`.
- New work is exploratory after prior results. Existing 216 comparisons and their correction remain unchanged.
- Association is not causal attribution; failed predictive improvement does not invalidate descriptive relationships.
- No missing observation becomes absence or zero. A composite vegetation map is not an annual time series.
- Retain settlement day-index/calendar limitations, camera-season appendix inconsistency, coast-grid support and source provenance.
- Climate projections are conditional on model/scenario; no calibrated biological future forecast until observational transfer has been evaluated.

## Task 1: Same-cohort settlement relationships and forward prediction

- [x] Tests: common-cohort inclusion, camera aggregation, exact within-site decomposition, chronological heldout folds and training-only scaling.
- [x] Create `work/relationship_response_v1/analyze.py` and `outputs/relationship_response_v1/` under `research/climate-penguin`.
- [x] Use September air temperature, nearshore sea-ice concentration, surface salinity and surface potential temperature. Freeze these inputs before new coefficient calculation. One mean per species × geographic code × nominal season; all-label primary and appendix-consistent sensitivity.
- [x] Quantify between-site and within-site relationships and site/year-adjusted coefficients on the identical cohort. Express slopes per 1°C, 10 ice percentage points and 0.1 salinity product unit. Include residual exposure support and clustered interval limitations.
- [x] Forward-test 2015–2020, training only on preceding years and previously seen sites. Compare common site/trend baseline, ice, ocean and combined groups with fixed ridge alpha=1; no coefficient-sign or p-value selection. Holdout errors do not gate association value.
- [x] Write reproducible tables, figure and Japanese interpretation, preserving all specified models and sample counts.

## Task 2: Vegetation and breeding use

- [x] Independent implementation in `work/vegetation_response_v1/`, outputs of the same name, and focused tests.
- [x] Match the 2017–2023 vegetation-map period to observed breeding counts; distinguish positive detected vegetation from nondetection.
- [x] Evaluate species-specific and within-region relationships on identical included observations, and matched site/season species contrasts where available. State spatial/habitat confounding.

## Task 3: CMIP6 actual future drivers

- [x] Independent implementation in `work/cmip6_projection_v1/`, outputs of the same name, and focused tests.
- [x] Freeze model selection by common variable/experiment availability before viewing changes: tas, sos, siconc; historical, SSP2-4.5, SSP5-8.5.
- [x] Extract fixed coordinates and model/member/grid identities; compare 1995–2014 with 2041–2060 and 2081–2100, August–November using each model's calendar.
- [x] Record masks, units, shared cells, coast distances, missing months and data URLs. Preserve actual numeric source extracts.

## Integration and verification

- [x] Independently review scientific assumptions and new code; repair concrete issues.
- [x] Run focused tests, repository baseline tests where dependencies permit, and reproduce output summaries from the saved tables.
- [x] Add one current-state report and update only the climate-lane entry point. Synchronize verified additions into existing PR206 with a fresh-head check; no merge or new ecological branch.

## Progress / rulings

- Public repository cloned into an isolated local branch; main and other research lanes untouched.
- Default shell network could not reach its proxy; approved public-source read succeeded through the normal escalation review.
- Existing source goals already match the user's current request; no new theme or formal outcome-blind claim is introduced.

- Completed all three real-data analyses; independent numeric review found no unresolved critical/important issue after cache provenance and hindcast reporting fixes.
- Final repository test run: 430 passed, 1 skipped (31.40 s); focused additions comprise 7 relationship + 6 vegetation + 20 CMIP6 tests. Initial missing pyreadr/pyshp dependencies were installed before this successful run.
- Relationship metadata and outputs were regenerated with the final code. CMIP6 was reread with final cache identity code; all three numerical result tables match the first fresh read within 1e-12.
