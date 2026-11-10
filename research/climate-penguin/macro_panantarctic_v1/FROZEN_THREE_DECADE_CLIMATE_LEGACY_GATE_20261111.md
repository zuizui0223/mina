# Frozen three-decade climate legacy and nesting mismatch gate — 2026-11-11 JST

Continuation of mina Draft PR #214 based on the 595-site Antarctic original source panel. Outcome-aware from prior reported 1990s/2010s summaries; not independent preregistration. No upstream paper/main merge.

## Scientific question
Within original colony locations actually monitored in all three 1991–2000, 2001–2010, 2011–2020 decades, is the **relative** later breeding-count change (2000s→2010s) more aligned with **earlier** change in that colony's Aug–Nov nearshore sea-ice concentration (1990s→2000s) than with climate change over 2000s→2010s? Does any time-directed alignment survive region and spatial-block conditioning? This is a bounded "legacy signature" rather than a biophysical climatic debt estimate.

## Time and source contract
- Original MAPPPD fixed most-frequent-method valid nest counts: 2,456 genuine observed site×species×season records from 595 original site codes; 18 reported source regions. Use existing SHA-pinned macro_panantarctic_v1/build.py, not imported count datasets.
- Original 1991–2020 EUMETSAT OSI SAF v3.1 25km marine ice: 120 original monthly source files previously verified at 595 sites. Use source SHA-validated previous artifact (run 42612067836, ID 13671496095) at fixed 0–100 km native ocean pixel IDs. SIC decade means require all ten originally source-valid Aug–Nov yearly means each decade. Do not invent 1980s source.
- Same colony IDs in **all three** decades for each species, with **>=2 genuinely observed nest-count years in each decade** and complete SIC; within each fixed species×site×decade take median of all originally recorded nest counts. True original zero preserved, unrecorded species, sites and years omitted (never zero).
- Adélie, chinstrap, gentoo run with identical rules. No case or predictor selected for nominal significance.
- Normalize all relative biological changes to within-source-region, not across species: response Y_i = log1p(N_i,2010s) - log1p(N_i,2000s), demeaned within regional categories with >=2 independent site IDs. Climate predictors X_earlier = SIC_i,2000s - SIC_i,1990s, X_concurrent = SIC_i,2010s - SIC_i,2000s, each demeaned within the same regions, on the same site roster.
- Compare region-demeaned Pearson r(Y,X_earlier) vs r(Y,X_concurrent) on **identical sites and source regions**, preserving both signs; descriptive absolute difference |r_earlier|-|r_concurrent| as score only. The predictors are spatially and temporally autocorrelated; this is **not a fitted 10-year response timescale**, nor a causal climate coefficient. If fewer than 5 native EPSG3031 250km blocks or fewer than 2 eligible source regions, mark underpowered.
- **Negative-time control:** response Y_past_i = log1p(N_i,2000s)-log1p(N_i,1990s) vs **future** climate X_concurrent = SIC_i,2010s - SIC_i,2000s. This cannot be a biological response to climate that had not yet occurred. A spurious association flags geographic sorting/shared trends.
- Report leave-one-native-250km-block and leave-one-original-region **signed correlation ranges**, each with the site and eligible-region counts. These are diagnostic ranges, not 95% intervals or species-independent tests. If deletion yields <5 data points or zero residual variance, mark that deletion unavailable; never treat undefined r as 0.
- Also re-run fixed three-decade **same roster** nest-weighted latitude (southward-positive km per 10-year step), within-decadal physical ice-change components and count-reweighting components. The two transition shifts can be added **only on the same triple-observed roster**, unlike previously separate pair-specific rosters. No true range edge or individual movement.
- Optionally descriptively join each same site to original 60% offshore full-grid meridional contour 10° longitude-sector changes (source run 42791019321). If <5 independent 10° sectors and >=3 original regions, suppress any temporal lead-lag correlation as insufficient sector support; do not count same-sector colonies as independent fronts. Show coverage and direction only.
- No threshold retuning (60% remains descriptive) and no new lag search. Existing 2026 emperor penguin 5-year lag result is external prior art for **another species and different abundance index**, not transferable as coefficient or evidence for three Pygoscelis.

## Interpretation
A larger prior-period absolute correlation alone is **insufficient** to name historical climatic debt. Temporal dependence, unbalanced original surveys, potential ecological nonlinearity and geographical confounding remain. Require independently repeated source regions, biologically calibrated sea-ice preference, consistent true occupancy/absence/survey effort and prospective data to claim species climate tracking lag; none are acquired by this three-bin descriptive reanalysis. Report a negative/underpowered gate rather than optimizing lags after inspection.

## Exact outputs
1. 3-decade matched original site roster with original median nest counts, source observation counts, sector IDs and decade SIC.
2. One row per species for signed synchronous, earlier and forbidden-future control correlations plus source-region and block support; signed ranges for leave-one-block/region.
3. Fixed-roster decade transitions with observed nesting latitude, symmetric SIC exposure physical+reweighting decomposition and evidence boundary.
4. Machine-readable verdict with explicit candidate/rejected lag classification.
