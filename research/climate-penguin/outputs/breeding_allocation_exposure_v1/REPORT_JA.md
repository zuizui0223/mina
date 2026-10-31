# Climate exposure and current breeding allocation: source-backed spatial crosswalk (2026-10-31)

**Science target:** Are larger extant **recorded site-code breeding allocations** concentrated where CMIP6 seasonal physical changes are high or low? Do *not* assume a decline in sea ice means demographic harm. This is the direct observational allocation × conditional environment overlay, with no causal coefficient.

## Main source and sample

2017–2023 MAPPPD-matched site×species records supply the **median of each site's actually observed nest counts** (different census seasons and techniques). Previously frozen climate–biological GIS crosswalk supplies **58 species×site_code units across 48 unique codes**, repeated for the same four conditions SSP245/585 × 2041–2060 / 2081–2100. Independently source-verified AEI ice-free land and REMA relief are available at **46/48 site codes** in original 122-site data; only **two codes BAIL/HERO** are outside the frozen candidate atlas. The 2km AEI circle is neither colony nesting area nor a possible future ice-free area.

The primary exposure indicator is SIC decrease ≥10 **percentage points** in **all three separate CMIP6 models** from 1995–2014 to a 20-year future 8–11 month period. Descriptive benchmark: share of matched sites satisfying the physical criterion, versus share of the sum of observed within-site median nest counts assigned to those sites. These denominators are not synchronized surveys and cannot be reported as global abundance or a percentage of remaining world penguins. All 3-model air-temperature, sea-ice and salinity *continuous* changes are also retained; strong sea ice loss is not necessarily a detrimental exposure.

## SSP5-8.5, 2081–2100

| Species | Sampled species-site units | ≥10pp SIC loss site share | Observed nest-median weighted share in those sites | Physical exposure-weighted SIC mean (pp) | Equal-site SIC mean (pp) |
|---|---:|---:|---:|---:|---:|
| ADPE | 31 | 12.90% | 0.20% | -2.54 | -10.54 |
| CHPE | 9 | 22.22% | 0.36% | -20.08 | -28.47 |
| GEPE | 18 | 77.78% | 64.89% | -40.19 | -44.51 |

**Important ecological/statistical interpretation:**
- ADPE sampled observed nest medians are very concentrated in eastern/Victoria Land (sampled-site effective count = 4.52 across 31 codes; top single site ADAR contributes 39.7%). ADPE's 4 strong SIC-loss codes are all Central-west Antarctic Peninsula, but the historical allocation is largely Victoria Land. Thus its low high-ice-change weighted share is *mostly a regional composition phenomenon*, not evidence that local declining colonies moved toward safe sites.
- CHPE 9 sampled codes have one dominant **single-season UAV** site (BAIL, 87.0% of the sum of site medians). Its weighted share can shift dramatically when that one site is removed. Do not infer species-wide refuge patterns.
- GEPE high-SIC-loss sites include 14/18 site codes but account for 64.9% of sampled nest medians. After **holding observed regional nest-median allocation fixed and reallocating equally among site codes within each region**, the expected high-loss share is 62.18% versus observed 64.89% (difference **+2.71 percentage points**). The apparent raw lower mass share than site share (64.9 vs 77.8%) is mainly regional selection, not within-region avoidance.
- Across all species the sites share coarse marine-grid fingerprints and regions; we report descriptive contrasts and sensitivity, **not** p-values from site-count pseudo-replicates.

## Site exposure vs region-conditioned comparison

The region-conditioned reference is defined by: keeping the **observed fraction of site-median nest counts in each region**, but assigning the region's weights equally across its matched site codes. Thus it removes *between-region* composition as an explanation while retaining all source region labels. It is **not** a counterfactual colony redistribution model and does not infer habitat selection.

| Species | Original high-loss mass share | Region-conditioned equal-code share | Within-region allocation contrast |
|---|---:|---:|---:|
| ADPE | 0.20% | 0.20% | 0.00 pp |
| CHPE | 0.36% | 0.86% | -0.50 pp |
| GEPE | 64.89% | 62.18% | 2.71 pp |

## Physical land and sensitivity

The original AEI ice-free and REMA terrain site traits are now pinned to this analysis as a separate source table, but remain **current local physical context**, not a direct measure of actual nesting options available to individual penguins or of future change. `species_scenario_summary.csv` includes unchanged population-median weights with five additional fixed sensitivity cohorts: ≥3 observed seasons; all three ocean-model cell centres within 50km; ground-only source; AEI/REMA site overlap; ≥3 seasons with 50km cell restriction. The "weighted share in high retreat" can change sharply as coverage changes, especially GEPE when restricting to ocean-model grid distance.

## Critical distinction from the original Palmer/Signy N_eff result

The newly calculated `effective_number_of_sampled_site_codes_W2_over_sumw2` is **cross-sectional across incompletely sampled MAPPPD site codes**, not the 1991–2017 within-island repeated-colony Hill N_eff endpoint and not GIS breeding-area. Neither Palmer LTER colony codes nor Signy monitored components have verified polygon geometry synchronized to CMIP6. Moreover, 25–100km native CMIP6 cells cannot distinguish subcolonies on a single small island. This means the exact proposed test, *retained within-island patches versus lost patches and their local future exposure*, is **NOT IDENTIFIABLE** from the current spatial/temporal supports. The present cross-site allocation analysis is a genuinely executed **scale-appropriate proxy** with this boundary.

All future breeding abundance/N_eff/species replacement/greening projections remain uncalibrated. Positive outcome here: a quantified region/source allocation of current observed breeding mass across physical climate fields, without fitting a suspect biological climate-response coefficient.

## Reproducibility

Inputs: `../land_marine_colocation_v1/matched_site_species_scenarios.csv`, `../vegetation_response_v1/site_species_cohort.csv`, `../cmip6_projection_v1/site_model_changes.csv`, derived`frozen_AEI_REMA_46site_traits.csv`. Source Git blob hashes and two GitHub Actions ZIP/source CSV SHA-256 recorded in `summary.json`.

Output: `site_allocation_exposure.csv` 232 records, `species_scenario_summary.csv` 72 records (3 species ×4 scenarios ×6 prespecified descriptive cohorts), `region_scenario_summary.csv`, and WGS84 `site_allocation_exposure.geojson`. Model-specific values are preserved for the three actual CMIP6 models. Derived code `../../work/breeding_allocation_exposure_v1/build.mjs` uses Node.js built-ins. This is source-arithmetic reproducibility, **not** a prospective validation of biological response.
