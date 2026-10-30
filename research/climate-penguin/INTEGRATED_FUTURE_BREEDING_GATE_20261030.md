# Climate × sea ice × salinity × vegetation × breeding space: integrated future scenario gate (2026-10-30)

**Status: measured joint climate exposure + conditional breeding-space sensitivity. NOT a calibrated penguin abundance or vegetation forecast.** This note is an exploratory extension in draft PR #206. It does not change frozen Paper 1 PR #189, Antarctic GIS Paper 2 PR #199, the previous 216 comparisons, or any existing model outcomes.

## Main question

Under a changing external marine resource environment and changing terrestrial nesting substrate, when does warming produce (i) breeding decline with disproportionate concentration, (ii) terrestrial patch redistribution without demographic recovery, or (iii) persistence/expansion with new ice-free nesting opportunities? Keep successful breeding, nest abundance, breeding component composition and post-colony vegetation distinct.

## Completed source-level join

- **Input:** `outputs/vegetation_response_v1/site_species_cohort.csv`: 246 site × species records (2017–2023 recorded nests and static 2017–2023 Pl antarctica composite vegetation detections in 2-km site buffers). This is *not annual change* and not nest-level vegetation use.
- **Climate:** `outputs/cmip6_projection_v1/site_model_changes.csv`: 3 GCMs (ACCESS-CM2, BCC-CSM2-MR, CESM2) × 2 SSPs × 2 20-year periods × 3 physical variables × 106 source coordinates (3,816 model-location-variable scenario records). Future exposure differences use **1995–2014 8–11 month climatology**. Each source native grid cell is carried through the scenarios; nearest coastal ocean cells are not a penguin nest microclimate.
- **Match rule:** same original `site_id` AND geodesic source-location separation <= 2 km; nearest climate location selected with no response-based tuning. Unmatched records are excluded only from the exposure-join view, NOT recoded as ecological zeros.
- **Output of this join:** **58 site × species** at **48 distinct source site IDs**, breakdown Adélie 31, Chinstrap 9, Gentoo 18. Of 58, **47 have positive mapped 2-km vegetation detection**, **50 have 2+ recorded nesting seasons**. Largest matched coordinate separation 1.09 km. This is not 58 independent climate grid cells, 58 patch surveys, or an unbiased Antarctic population sample.
- **Important time mismatch:** observed nest/vegetation anchors (2017–2023) do not share the CMIP6 baseline (1995–2014). These source changes are environmental exposures *at matched geographical coordinates*, NOT changes relative to the actual census-date nest conditions. No future nest count is computed from them.

## Matched-place future forcing

Each cell below is the **unweighted mean across matched species-sites and then the three available models**. `siconc` change is *percentage points*, `sos` uses model sea-surface salinity's numeric (approximately 0.001) scale. These are not independent species responses.

| SSP / period | species | matched site×species | Δ air °C | Δ sea ice pp | Δ salinity |
|---|---|---:|---:|---:|---:|
| SSP2-4.5 / 2041–2060 | Adélie | 31 | +1.31 | -3.58 | -0.042 |
| SSP2-4.5 / 2041–2060 | Chinstrap | 9 | +1.57 | -13.86 | -0.006 |
| SSP2-4.5 / 2041–2060 | Gentoo | 18 | +1.75 | -15.46 | -0.043 |
| SSP2-4.5 / 2081–2100 | Adélie | 31 | +2.23 | -7.63 | -0.158 |
| SSP2-4.5 / 2081–2100 | Chinstrap | 9 | +2.32 | -25.58 | -0.098 |
| SSP2-4.5 / 2081–2100 | Gentoo | 18 | +2.53 | -34.08 | -0.169 |
| SSP5-8.5 / 2041–2060 | Adélie | 31 | +1.57 | -4.54 | -0.074 |
| SSP5-8.5 / 2041–2060 | Chinstrap | 9 | +1.83 | -17.84 | -0.021 |
| SSP5-8.5 / 2041–2060 | Gentoo | 18 | +1.98 | -18.96 | -0.074 |
| SSP5-8.5 / 2081–2100 | Adélie | 31 | +3.91 | -10.54 | -0.229 |
| SSP5-8.5 / 2081–2100 | Chinstrap | 9 | +4.07 | -28.47 | -0.184 |
| SSP5-8.5 / 2081–2100 | Gentoo | 18 | +4.64 | -44.51 | -0.324 |

**Non-independent climate cells:** At SSP5-8.5 / 2081–2100, mean Δice under each GCM is Adélie [-9.39,-5.63,-16.61], Chinstrap [-18.75,-10.49,-56.17], Gentoo [-38.49,-23.56,-71.48] pp (ACCESS, BCC, CESM). Their independently computed equal-native-marine-grid-cell mean over the same species' locations is respectively **-7.14, -30.03, -31.37 pp** after equal averaging of the three model-specific unique-cell means, compared with site-weighted -10.54, -28.47, -44.51 pp. Changing site versus marine cell weights can materially affect apparent between-species exposure contrast, especially Gentoo. This is spatial sampling composition, not measured susceptibility.

**Salinity model disagreement:** For 2081–2100 SSP5-8.5 Gentoo matched sites, GCM-specific means are ACCESS -0.644, BCC +0.026, CESM -0.355. Do not equate salinity with a direct effect on nests or call the ensemble mean a robust local freshwater trend. Salinity/stratification can influence plankton and krill through a lagged trophic pathway, whose coefficient is not identified here.

## Breeding-space component: a STRICTLY conditional calculation

Use the previously frozen `results/SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` and `results/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`. The actual long-interval source endpoints are:

- Signy Adélie N: 2342 -> 1217; inverse-Simpson component number: 3.080744686 -> 1.936162759. Descriptive long-interval elasticity `κ = log(1.936162759/3.080744686)/log(1217/2342) = 0.70952`.
- Signy Chinstrap N: 1642 -> 581; inverse-Simpson component number 4.437881666 -> 2.191029760; `κ = 0.67936`.

A **what-if**, NOT a climate forecast: *if* a comparable declining, fixed-roster system's nest abundance becomes 0.5 × its baseline, *and if* this observed two-system long-interval κ is imposed as a counterfactual mapping, `N_eff_future / N_eff_base = 0.5^κ = 0.612–0.624`. That is a **37.6–38.8% reduction in effective monitored component number** conditional on a hypothetical 50% abundance decline. There is no proof of a universal κ, none calibrated for Gentoo, no causal attribution of κ to climate or salinity, no future nest-number response coefficient, and no equivalence to geographic breeding area or local extirpation. The concentration results were confirmed under count-error nulls; this does NOT validate transfer of κ to 2100.

## Coherent joint model, not a sum of unrelated correlations

1. **Marine resource state:** `F_{i,t} = f(ice_concentration, ice_duration, air/sea temperature, salinity, stratification, timing, prey)`. Treat SST, ice and salinity as jointly generated model fields, not independent experiments. Food/krill is currently missing.
2. **Breeding stage process:** nest pairs, egg/chick outputs, fledging, immature survival and return/immigration are separate terms with appropriate lags and observation error. Previous V9–V11 show that recorded chick/nest ratios do not automatically predict later species-composition change. Do not convert the 169 camera settlement-index rows to nest-number change or use their coefficients as demographic elasticities.
3. **Breeding option/capacity:** local nest-level bare, snow-free, accessible land, habitat heterogeneity and slope, with ocean access. Existing Atlas provides static 2 km ice-free habitat in 118/122 candidate sites, but is **not mapped occupied nesting polygons** and its time-varying change is not calibrated.
4. **Spatial allocation:** conditional on predicted population and fixed patch IDs, define `p_{s,i,k,t}=N_{s,i,k,t}/sum_k N_{s,i,k,t}` and `N_eff=1/sum_k p^2`. Forecast both total nests and `N_eff`; neither directly implies the other. Local persistence, vacant patch creation and new colonization need patch-level monitoring data.
5. **Vegetation feedback:** do not assume more green = more nest suitability. Model vegetation as *potential response and potential local modifier* to temperature/snow, guano-driven nutrient deposition, penguin trampling and abandonment, with direction-specific lags. Existing 2-km static vegetation detection shows only co-location, NOT birds using plants or vegetation expansion. Snow algae are not included in the static vegetation union.

## Non-negotiable predictive gates

| Gate | Status | Why |
|---|---|---|
| Climate / nest / vegetation joint geographic exposure | **DONE (58 matched rows)** | Model location and source site geometry audited |
| Independent model and effective coastal grid support | **PARTIAL** | 3 GCMs, 1 member each; coarse ocean grid, repeats |
| Date-aligned future exposure vs baseline nests | **OPEN** | 1995–2014 climate baseline vs 2017–23 nests |
| Sea ice, warming and salinity -> future nest abundance | **UNIDENTIFIED** | Timing-robust annual growth effects do not survive correction; salinity year-grid dependence |
| Species-specific prey and fledging -> future recruitment | **UNIDENTIFIED** | Different stages/lag cohorts and field food data lacking |
| Change in usable nesting-patch geometry and vegetation | **UNIDENTIFIED** | Static 2-km polygons are not annual patch maps or nest pixels |
| Climate-conditioned future N_eff and occupancy | **UNIDENTIFIED** | Current κ is a descriptive conditional stress test, not a fitted climate or recolonization response |
| Hindcast validation in held-out regions and years | **NOT PASSED** | The current camera hindcast includes test-year observed weather and unstable gains |

**Scientific decision:** report actual projected `T/ice/salinity` exposures and the conditional abundance-to-N_eff stress test, but **do not report a numerical 2050/2100 breeding-pair population forecast or greening percentage**. The next result must estimate and validate at least one species-and-region-specific lagged demographic response with observation process accounted for, or retain multiple explicit externally supplied abundance trajectories as non-probabilistic what-ifs.

## Reproduction / source paths

- `research/climate-penguin/outputs/cmip6_projection_v1/site_model_changes.csv`: for each `location_id` × `source_id` × SSP × period × variable; verified 3,816 rows.
- `research/climate-penguin/outputs/vegetation_response_v1/site_species_cohort.csv`: 246 source site×species rows, including source coordinates, 2-km static vegetation presence, nest observation support.
- Match exact `site_id`; choose the nearest climate `location_id` within great-circle 2 km; all eligible units must carry `tas,siconc,sos` and all 3 GCMs for all 4 futures.
- Mean 3 model-specific site changes per matched species-site; mean equally by species site. Independent sensitivity: within each GCM, first collapse repeated `siconc.grid_cell_id` to one mean and then equal-average its unique cells; only then equal-average GCM means.
- `results/SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`; `results/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` for κ; never substitute `N_eff` for actual occupied breeding polygons.

This note adds exploratory cross-layer analysis only; it is not a publication-grade end-to-end prediction or a replacement for the frozen manuscript.
