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


## 2026-10-30 follow-up: three-GCM sign concordance across matched nesting/vegetation sites

**Additional executed geographic-exposure audit**, using the original 58 matched species-site rows from the same ID + <=2 km coordinate crosswalk and **per-GCM** \`site_model_changes.csv\` rather than model-averaged sign. A sign is unanimous only if every ACCESS-CM2, BCC-CSM2-MR and CESM2 first-member value has that sign. This is not a statistical confidence interval, three independent ecological observations or a predictive risk classification.

| SSP5-8.5 2081–2100 | matched site×species | all 3 GCMs warming | all 3 GCMs sea-ice loss | sea-ice direction mixed | all 3 GCMs salinity lower | salinity direction mixed | ice-loss-unanimous AND nearby mapped vegetation detected |
|---|---:|---:|---:|---:|---:|---:|---:|
| Adélie | 31 | 31 | **17** | 14 | 27 | 4 | 17 |
| Chinstrap | 9 | 9 | **9** | 0 | 6 | 3 | 8 |
| Gentoo | 18 | 18 | **18** | 0 | 8 | 10 | 13 |

The same all-three-model sea-ice *decrease* counts (17/31, 9/9, 18/18) occur under both SSPs at both 2041–2060 and 2081–2100, **for this particular same-site cohort and these three GCMs**. None of the selected site×species rows shows unanimous sea-ice increase. In this analysis, a "mixed ice" location means at least one GCM predicts a non-negative change; it is NOT evidence of unchanged ice, safe habitat or a penguin refuge.

The species contrast is strongly conditioned on the observed distribution of sampling locations: Adélie matched sites include Victoria Land and Adélie Land, whereas the selected Chinstrap/Gentoo sites are concentrated around South Shetland/Antarctic Peninsula. Do **not** report different intrinsic penguin thermal sensitivity based on 17/31 versus 18/18. Marine model grids are coarser and shared by multiple sites. Sensitivity to equal-unique-model-grid weighting, already noted above, remains relevant.

For this exact SSP5-8.5 2081–2100 scope, salinity direction is particularly inconsistent in Gentoo (10/18 mixed) and Chinstrap (3/9). Mapped vegetation positive is a 2017–2023 composite detection within 2 km, not annual greening, habitat suitability, nest placement or plant use. None of these intersections is a climate-driven biological outcome.

## 2026-10-30 follow-up: held-out-year population-response gate FAILED

An independent forward-only 2015–2018 Adelie nest-change audit is now executable at \`work/scenario_support_v1/count_growth_forward_gate_v1.py\`, with a source-frozen numeric receipt, 4 time-leakage/solver/independent-result tests and an [executed report](outputs/count_growth_forward_gate_v1/REPORT_JA.md). On **33 same-site held-out one-year count intervals**, MAE of the no-change benchmark was **0.155125**, site+year ridge **0.198080** and site+year+start-year September sea-ice ridge **0.198695**. The 28 timing-supported test intervals give **0.165408 / 0.216319 / 0.214450**, respectively. The tiny all-cohort RMSE improvement of ice versus site+year (0.255176 to 0.251651) does not beat no-change RMSE 0.230585. It is a single exploratory benchmark family, not exhaustive model optimality or proof of no climate effect.

Only **28 of the original 76 annual intervals** have complete start-year September ice, salinity and potential-water-temperature; **13** also have recorded original count-month support; only **9** full-feature intervals have a training-history-matched test site during the four held-out years, with **4** timing-supported. **No validated joint 3-environment → future nest-count elasticity can be inferred** from this observational overlap. Do not silently multiply the existing settlement/arrival-index coefficients, vegetation correlations or retrospective Signy \`κ\` by the projected climate changes.

Source and reproducibility: \`outputs/climate_penguin/count_environment_annual_intervals.csv\` (Git blob \`bcee8af700c02b28050f39c02b20730961ded19d\`); \`outputs/count_growth_forward_gate_v1/expected_receipt.json\`; [GitHub Actions successful time-held-out validation](https://github.com/zuizui0223/mina/actions/runs/41046631619) (4 tests passed, output archive ID 12973075740). Frozen Paper 1, Paper 2 and previous 216 comparisons remain unchanged.


## 2026-10-30 additional genuine long-term time-forward falsification (v2/v3)

**Historical sample expanded; demographic climate-link predictive gate still FAILS.** Read source receipts, not only earlier 76-interval short-window notes.

**v2 [long-count forward gate](outputs/long_count_forward_gate_v2/REPORT_JA.md):** Frozen 1991–2020 monthly SIC and original source-matched Adelie counts yield **301 one-year intervals across 33 sites / 6 regions**. A rolling 2005–2018 test using *only prior years* and only previously seen sites retains **129 held-out site-year count changes across 22 sites / 4 regions**. The primary actual mean absolute **log nest-count growth error** is no-change 0.1540, ridge site+year 0.1606, plus start-year September near-ice 0.1614, offshore 0.1630, both 0.1614. In the 98 date-supported tests, no-change 0.1539 vs near-ice 0.1622. The end-year SIC and end-minus-start SIC comparisons use future-observed ice and are **conditional hindcasts**; neither outperforms no-change in the main 129. This is a *fixed exploratory ridge family*, not all possible ecological population models. Authentic self-contained CI [41052912318](https://github.com/zuizui0223/mina/actions/runs/41052912318) **SUCCESS**, 5 tests.

**v3 [antecedent 1-/3-year SIC](outputs/antecedent_ice_forward_gate_v3/REPORT_JA.md):** The independently source-preserved monthly dataset has **9,600 site×year×month×coastal-band values** at 40 sites. Fitting use of only Aug-Nov 0–100 km observations over **t−1** and **t−3..t−1** leaves **264 original count intervals** with full 3-year support; held-out same-site testing over 2005–2018 yields **126 site-years across 19 sites**. Actual MAE no-change **0.15283**, site+year 0.16182, prior-1-year sea ice 0.16252, antecedent 3-year sea ice 0.16452, prior-1-year within-site anomalies 0.16202, antecedent 3-year within-site anomalies 0.16918. Adding the 3-year between-year variability gives 0.17008. The 95 date-supported tests retain no-change as lowest-error comparator. Independent full workflow [41053536796](https://github.com/zuizui0223/mina/actions/runs/41053536796) **SUCCESS**, 5 tests. **No future count data or future climate values** were used in the prospective predictors; training-only means standardize anomalies.

Both v2 and v3 preserve distinct original cohorts and their decision scopes; 301 vs 264 and 129 vs 126 are NOT contradictory. v3 uses the additional complete t−3..t−1 history requirement; differences in absolute MAE should not be attributed only to predictors when cohorts differ. Neither can identify the krill/food chain, stage-specific chick production, individual dispersal, salinity response or vegetation-driven nesting mechanisms, and neither is a formal causal null test.

**Integrated future-decision now explicitly NO-GO for numerical climate-driven nest-population forecasts:** Regional GCM temperature/sea-ice/salinity trajectories and matched species-site environmental exposure remain usable. Conditional Signy \`N_eff\` response under *externally specified* abundance changes remains an illustrative what-if. Future climate-to-count elasticities, vegetation dynamics, species replacement probabilities, and geographic island-carrying-capacity changes remain **unidentified**. Future scientifically meaningful joint projections require at minimum an independently transferable species×region population/stage-response model, measured reproductive output and prey/foraging (or informative constraints), and time-resolved nest-level landscape/vegetation exposures, not a selected positive coefficient from repeated post-hoc model families.


## 2026-10-30 new reproductive-stage / diet / breeding-space evidence (linked Signy single island)

The next biologically independent *stage*, not an independent climate system, has now been observed using original British Antarctic Survey archives: 3 species, **392 ordered source pairs–pre-fledging counts**, **22 shared breeding seasons** and **19 consecutive annual changes**. Observed three-species changes covary (first-difference r +0.794 Adélie/Chinstrap, +0.703 Adélie/Gentoo, +0.738 Chinstrap/Gentoo); source colony median/aggregate grains differ. **Dunn et al. 2016 already reported chinstrap–gentoo annual breeding success correlation 0.73 and divergent population trends; no novel common-response mechanism is claimed.**

Original diet (1997–2020 for Adélie/Chinstrap; Gentoo only 1998–2010) yields **45 matched species-years**, with realized stomach krill mass fraction at site/season grain. Same-year diet-share vs recorded fledgling output has only exploratory correlations +0.150, +0.174, −0.165, and strict diet-before-all-stage-count chronology in only **2/6/4 seasons**. No valid prey-mediated causal transfer coefficient. At Signy 2012–2019, 8 years of stage vs fixed-roster spatial N_eff overlap; only 7 stage-to-next N_eff transitions (r +0.104 Adélie, +0.225 Chinstrap) and heterogeneous roster/grain. These do not validate future distribution predictions.

**Therefore the original NO-GO for numerical climate-driven nesting counts, N_eff and vegetation forecasts stays.** See [source receipt + full distinctions](SIGNY_PREY_STAGE_SPATIAL_SYNTHESIS_20261030.md) and successful first-party [diet↔stage run](https://github.com/zuizui0223/mina/actions/runs/41057594354). The new result is a concrete filled food/reproductive-stage observational layer and an explicit temporal identifiability gate; the next necessary original data are external sea-ice/salinity, krill abundance, and breeding-patch geometry aligned to those same years, not more regressions on existing 3-species gut-share.
