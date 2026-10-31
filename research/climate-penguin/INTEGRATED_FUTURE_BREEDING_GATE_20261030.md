# Climate × sea ice × salinity × vegetation × breeding space: integrated future scenario gate (2026-10-30)

> **2026-10-31 最新の確定エビデンス入口:** [肯定結果・未達ゲートの統合台帳](POSITIVE_EVIDENCE_MERGED_20261031.md) を参照。Palmer・Signyの繁殖構成単位の縮退と地域同期は元結果JSONに照合済み。Rossの再配置・回復は著者確認待ちPR189の固定コミットを参照するだけで、こちらのDraft PRへ論文全体を混ぜない。新しいGPS/TDRの位置・圧力対応は技術的に前進したが、**2050/2100年の繁殖数・N_eff・植生の確定予測は未許可**。

**2026-10-30 critical source correction:** IMR 2024 Table2 and Skaret 2023 original Table3 disagree on annual krill labels (8 of the 10 year alignments). Prior \`imr_south_orkney_krill_v1\` numerical food→fledgling results are superseded. Skaret 2023's 2013 combined value is missing (not zero), and 2014 combined is 76.5 g/m². On the corrected 8-year source, Pearson r to source Signy fledgling stage is Adélie +0.0573, Chinstrap −0.2118, Gentoo −0.4134, not the old 9-year figures. [Source conflict audit](outputs/south_orkney_source_reconciliation_v2/REPORT_JA.md) and [dedicated successful checks](https://github.com/zuizui0223/mina/actions/runs/41069153393). Source-implied NO-GO for climate-driven future nesting forecasts remains.

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


## 2026-10-30 South Orkney external krill biomass bridge: DONE, no robust stage transfer

A genuinely **independent-from-penguins** external marine prey survey series now exists in the research pipeline, but the annual biomass data were **published by IMR**; mina did not collect or independently process raw acoustic transects. [IMR 2024 survey Report, Table 2](https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14) reports ten estimates for the *overall ~60,000km² South Orkney regional stratum* during 2011–2020, spanning 23.2–128.8 g/m². Original Skaret et al. 2023 [ICES J Mar Sci DOI 10.1093/icesjms/fsad076](https://doi.org/10.1093/icesjms/fsad076) describes the acoustic surveys, variable 38/120kHz instruments and severe **2013 and 2015 ice-constrained transect coverage**; raw data are available on reasonable request (NOT downloaded here).

The first-party BAS **three-species source-native** fledgling-stage dates (Jan-Feb T+1) have been matched separately to two *calendar-defined* marine exposure specifications:
- Primary **preceding seasonal opportunity**: Jan-Feb acoustic survey in year T, before Oct T nesting and T+1 fledgling counts.
- Secondary **concurrent/chick-season index**: survey Jan-Feb T+1, which can overlap or follow the native fledgling counts, so is *not usable as a prospective predictor without exact acoustic dates*.

Primary all nine breeding seasons T=2011–2019, shared yearly acoustic exposure across all 3 species, return native-stage Pearson r = **−0.212 Adélie / −0.559 chinstrap / −0.546 gentoo**. Two incompletely surveyed acoustic calendar years 2013/2015 excluded leaves seven season opportunities: **−0.359 / −0.794 / −0.663**. Sensitivity additionally removing **2012** (postresult influential high-krill, low-stage year) yields only six years and **+0.044 / +0.011 / +0.214**. Rank correlations for these 7 full-coverage years are only −0.036 / −0.286 / −0.036; result does not support a robust region-aggregated krill→fledgling slope. The concurrent-window all-nine correlation is **+0.212 / +0.099 / +0.363** and its sign cannot rescue the earlier null because it uses a different timing estimand. Do NOT select the most favorable lag, choose an R², or treat 3 species as independent regional ocean observations.

The conclusion strengthens the prior **NO-GO for quantitative 2050/2100 climate-driven nesting-pair, breeding N_eff or vegetation forecast**: actual external prey biomass can be measured and joined, but available **regional** abundance does not identify the actual within-commuting-range prey availability of nesting adults or subsequent recruitment. The ecological next information is smaller-scale acoustics/NASC and verified foraging area/time, multiple independent islands/regions, and date-matched salinity/stratification, not more specification search over nine surveys.

Durable source data, executed method and caveats: [IMR biomass × BAS fledgling stage source report](outputs/imr_south_orkney_krill_v1/REPORT_JA.md) and [successful first-party BAS source CI / numeric receipt](https://github.com/zuizui0223/mina/actions/runs/41065644242), 5 tests PASS. Freeze-replay source \`inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv\` is explicitly a manual transcription of published estimates, not new original krill measurements. Paper 1/PR189, Paper 2/PR199 and the 216-test environmental family remain untouched.


## 2026-10-30 BAS 2011–2020 original annual spatial krill predictions: executed proximity sensitivity

Signy native BAS source colony GPS reference points (14), plus 2011–2020 original first-party Freer et al 2025 modelled krill raster source [DOI](https://doi.org/10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32), have now been genuinely spatially joined. **This source is already GAM-modelled** using raw acoustic data, ice, salinity and oceanography. It is not independently measured near-colony krill or a second independent validation of environmental effects.

BAS 0.083333° GeoTIFF original grid, original 30 TIFF combined content hash \`f4fffbc2b0cbe2dffc5a5728c81f1b46ba9ff99988c6589bb3515d38d2a2fead\`. Original Signy GPS bbox center lat **−60.704025**, lon **−45.6275835**. Fixed 0–50/50–100/100–150 km rings yielded **90 published-model annual×product×band measurements**, with all native noData and output mask preserved. Stage response is the original 3-species 2011–2019 pre-fledging count per pair; there are **nine years of shared island model exposure** (not 27 independent climate replicates).

Probability-weighted predicted krill field r with recorded fledgling output in **all 9** years by ring 0–50 / 50–100 / 100–150 km:
- Adélie **+0.226 / +0.167 / +0.012**
- Chinstrap **−0.115 / −0.112 / −0.326**
- Gentoo **−0.239 / −0.259 / −0.387**

Restricting to original acoustic coverage-complete years (n=7) shifts values; additionally excluding influential 2012 (n=6, posthoc only) produces markedly different positive values. Thus *neither the regional IMR observational mean nor source-GAM-modelled Signy-proximate density gives a stable, transferable food-to-fledgling coefficient* on these data. Since the year-specific raster is already fitted with ice-edge, salinity and other environmental predictors, its correlation with climate cannot be advertised as an independent mechanism test. Original GPS reference points are not measured feeding routes; source raster mask has not been independently verified as a coastline/ocean mask. Do not call fixed rings actual foraging areas.

[Full executed spatial source outcome](outputs/bas_spatial_krill_signy_v2/REPORT_JA.md) · [GitHub Actions source/data verification](https://github.com/zuizui0223/mina/actions/runs/41067871772) SUCCESS (5 tests). The user-directed climate, sea-ice, salinity, breeding-space and vegetation future scenario remains **conditional/exploratory**; no scientific validation of 2050/2100 pair count or patch N_eff forecasts.


## 2026-10-30 source GPS track × GAM krill conditional spatial accessibility: executed

**First-party BAS animal movement tracks are now spatially matched to original 2011–2020 Freer modelled krill:** 173 source GPS CSV members (41 Adélie, 121 chinstrap, 11 gentoo), one identical duplicated chinstrap deployment and four empty chinstrap CSVs; **168 unique nonempty source deployments, 174,127 GPS positions**; 8 duplicate timestamps and 119 isolated >12m/s middle-fix spikes audited rather than counted as independent environmental observations. Canonical source-member SHA256: \`e65a884341346a95ebb4a25de492d350716fde5f5cb77a669d66846811f6800a\`. The ten original Freer combined GeoTIFF member SHA256 are all pinned, WGS84 native 0.083333°.

Geographic analytical restriction is a source Signy 14-original-colony reference-point bbox midpoint with fixed **5/10/20 km** lower exclusions, fixed 150 km upper source-coverage restriction, only original median-time fix per hour, **at least 10 hourly positions per deployment**; primary chooses 10–150 km and removes **only isolated speed-spike fixes**, a sensitivity keeps them. Equal unique GAM cells **within each deployment**, then equal-weight deployments within each species-year, avoids treating every GPS point as an independent climate opportunity. **152 / 168** qualified in primary (35 Adélie / 109 chinstrap / 8 gentoo). 3-species overlap in only **2013/14 and 2015/16**, with just **one Gentoo 2015 deployment**. The GPS is measured movement but *not dive/foraging/capture behavior*, and the geographic window lacks an independently applied land/ocean mask.

2013/14 *tracked locations* in the primary: Adélie **22 deployment units**, median distance **50.1 km**, Jan-Feb 2013 (preseason) GAM krill estimate **4.08 g/m²**, Jan-Feb 2014 (same summer, NOT an operational input) **9.24 g/m²**; chinstrap **20**, **95.6 km**, **3.16 / 8.65 g/m²**; gentoo **7**, **20.6 km**, **6.64 / 10.87 g/m²**. The **gentoo > Adélie > chinstrap** ordering of the same published GAM's predicted krill field at GPS-reached locations is unchanged by 5/10/20 km exclusion, speed spike sensitivity and leave-one-deployment-out ranges (preseason LOO means gentoo **6.460–6.799**, Adélie **3.586–4.188**, chinstrap **2.894–3.249**; those are NOT confidence intervals). The same-summer 2014 GAM values show the same order. By 2015, Adélie vs chinstrap pre-season ranking switches (~2.877 vs ~2.962 g/m²) and gentoo has n=1. **Do not generalize a 2013 field pattern as a species trait or causal food limitation.**

Comparison to original BAS same-season fledgling output (2013 stage: Adélie 1.163, chinstrap 0.586, gentoo 0.691 recorded fledglings per native pair source unit) is a **three-species within-one-island descriptive comparison**, not a 2013 food-effect regression. The species with greatest measured pre-fledgling output is NOT the species with greatest GAM krill value. Tag length, natal origin, sea/land ambiguity, within-year source model, original coastal krill surveys and fecundity may confound.

**Science gate:** An actual tagged-animal spatial-location layer is now available to study connectivity between terrestrial colony configuration and modelled marine resources, but the same published Freer model is already fitted to IMR acoustic data and sea-ice/salinity covariates. Source GPS does not identify actual prey capture, temporal transfer to 2050/2100, new ice/salinity mechanism, or future \`N_eff\`/vegetation feedback. Therefore the numerical climate-driven future penguin breeding count/space model **remains NO-GO**, conditional exposure indices only.

Reproduction: [executed source-GPS movement × model krill result](outputs/signy_gps_krill_access_v1/REPORT_JA.md) and [GitHub Actions source/timeline/numeric validation](https://github.com/zuizui0223/mina/actions/runs/41074276918) **SUCCESS** (5 tests); source model rasters sha-pinned and all data rebuilt from publisher ZIP in CI. Original raw GPS positions are not republished in git; source DOI and result-level support remain linked.


## 2026-10-30 same-species / same-year South Orkney multiple-island comparison (GPS source analysis)

The island-geography component of the original future scenario research now has a genuine first-party GPS observation bridge: [BAS Chinstrap GPS Version 2](https://doi.org/10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92), 313 original publisher CSV GPS members, a sha-verified canonical member digest \`f56dc817aefefda41e509541d24a184f68644d12c0a1c28af8071717275101c9\`, 4 empty and 1 identical duplicate, **308 unique nonempty deployments / 215,615 GPS position rows**. Other island colonies occur in single matched years: Laurie 2011, Powell 2013, Monroe 2015; Signy has these same years plus 2018. **Within each matched year, the *species is always Chinstrap***, reducing but not eliminating ecological confounding. They are **three within-year island pairs, not three independent island×year replications per island**.

Source geographic anchor for each island×year is the median of original first GPS fix per deployment, computed *without* looking at krill or reproductive outcomes, not an independently surveyed nest or penguin landing route. Source spot clustering is tight at Powell and Monroe (90th percentiles <1 km) but more diffuse at Laurie (~6 km). Same conservative isolated-spike filtering, one actual GPS fix per hour, ≥10 hours, 10–150 km from that source-derived anchor, native Freer-model cell means, then equal-deployment island-year mean; 5/10/20 km source origin sensitivity and a no-spike-filter sensitivity are retained. No independent coastline/land-only mask or dive state was verified.

**Published GAM-predicted krill at actually tracked geographic cells** in Jan–Feb year T (ahead of subsequent Dec–Feb breeding season) for *matched Chinstrap years*:

| breeding season / same species | other island qualified tags / Signy tags | other-island mean / Signy mean GAM g m^-2 | ratio |
|---|---:|---:|---:|
| 2011/12 Laurie vs Signy | 48 / 4 | 18.498 / 7.581 | **2.440** |
| 2013/14 Powell vs Signy | 56 / 19 | 17.742 / 2.810 | **6.314** |
| 2015/16 Monroe vs Signy | 46 / 26 | 8.132 / 2.959 | **2.748** |

This is an observational **animal-location × published-model-output geographic contrast**. The GPS positions are measured but prey density is not independently observed at those positions. Freer GAM fitted original IMR acoustic surveys and salinity/sea ice, so using it to confirm those climate links would be **circular**. The Skaret 2023 Combined acoustic estimate for 2013 is *missing*, making 2013 extrapolation particularly sensitive to published GAM assumptions and survey coverage. The above-ratio directions persist across 5/10/20 km geographic cutoff, but the 2011 Signy comparison becomes n=1 at 20 km. No separate Laurie/Powell/Monroe native fledgling success source is joined; thus this is **not an island effect on reproduction or persistence**.

**Ecological hypothesis now sharpened:** Antarctic island placement and the movement constraints of flightless breeding birds may jointly determine which parts of the marine resource landscape are reachable, even for the same species and climate year. We can measure this as source-GPS geographic co-location; to conclude *actual prey availability/accessibility* still requires matched tagged diving/foraging behavior and independent acoustic/trawl krill estimates within reachable marine space. The published BAS TDR sources are [Adélie](https://doi.org/10.5285/bf62d713-93e5-487f-acba-1ec2da35c7e1), [Chinstrap v2](https://doi.org/10.5285/da13e049-be2b-4345-bbdd-ab960cb24731) and [Gentoo](https://doi.org/10.5285/ff0cbcb7-bdad-4d03-bdf2-a54c54d67d9f); official source metadata supports cross-instrument deployment IDs, but actual TDR original overlap/dive calibration is **not yet audited**. Position is not catch; dive is not automatically krill consumption.

[Source-coded original multi-island results](outputs/south_orkney_island_gps_krill_v1/REPORT_JA.md), [original source and all matched-year sensitivity run](https://github.com/zuizui0223/mina/actions/runs/41075715761) **SUCCESS with five tests**. Old Paper1 and Paper2 frozen. **Future 2050/2100 breeding abundance, patch N_eff, species replacement and vegetation change remain NOT calibrated.** This improves the mechanistic research design but not the numerical predictive authorization.


## 2026-10-31: original BAS TDR×GPS source linkage with pressure-event pilot

A new [original-data source-gated island-access note](ORIGINAL_GPS_TDR_ISLAND_ACCESS_GATE_20261031.md) documents **300 exactly matched original BAS Chinstrap v2 GPS/TDR nonempty deployments** across four islands (Signy108/Laurie60/Powell68/Monroe64), against **317 original TDR files (314 with actual timestamped raw pressure, three header-only)**. The publisher GPS/TDR Powell native ID discrepancy PI### / PIC### is explicitly mapped only by the numeric suffix; raw filenames remain preserved.

The 4 source-ID-prefixed pressure pilot successfully reads 1-second TDR and detects source pressure-defined candidate dive events with provisional moving hourly lower-quantile ZOC, 5dbar and ≥10s; GPS time bracket eligibility is only ~44–64% of these candidates in the 4-tag sample despite >96% temporal overlap of sensor recordings. Monroe's within-hour lower-quantile surface offset varies by **7.75dbar** while the other three range only 0.3–0.6dbar. Consequently **no inter-island diving-rate or ecological prey-access mechanism can yet be inferred**; a pressure-ZOC method sensitivity and dive/GPS/land/ocean validation remain necessary. Previous BAS original dive-distance/pelagic patch-quality relationships were already studied in Movement Ecology 2021 (doi:10.1186/s40462-021-00261-x) and are not claimed as a novel first observation.

Source verification: [GPS×TDR original overlap](https://github.com/zuizui0223/mina/actions/runs/41164341816), [GPS bracket opportunity](https://github.com/zuizui0223/mina/actions/runs/41164271535), [4-tag pressure pilot](https://github.com/zuizui0223/mina/actions/runs/41164838622), all completed SUCCESS. The 2011–2020 krill source raster remains an existing model already trained on acoustic/ice/salinity (NOT independent observed prey availability), and the 2050/2100 demographic/patch/vegetation forecast remains NO-GO.


**2026-10-31 TDR pressure quality sensitivity finalized:** [48 fixed original-tag zero-offset×pressure-cutoff tests](outputs/chinstrap_tdr_zoc_sensitivity_v2/REPORT_JA.md), [dedicated successful CI](https://github.com/zuizui0223/mina/actions/runs/41165153690) with 4 tests. Among four original pilot tags, 5dbar candidate-event counts across calibration methods vary Laurie1476–1481, Powell4771–4825, Monroe**1254–1456**, Signy51–52; GPS-bracketed event counts Laurie897–901, Powell2113–2132, Monroe**846–1012**, Signy24. The large Monroe sensor drift (~7.75dbar) forces sensor-specific offset QA before original 300 source units can be interpreted as comparable diving ecology. No independent acoustic/krill capture or environmental causal response has been established.

## 2026-10-31: 4 native TDR dive-candidate GPS cells joined to original krill GAM

原BAS TDR×GPSと既存Freerオキアミモデルの固定4タグ接続が実行済み。圧力5dbar・10秒以上（暫定q1/60min ZOC）、前後実GPS600秒以内＋最近実GPS300秒以内という候補段階で、原GPS時間対応はLaurie901、Powell2117、Monroe876、Signy24。地理10〜150km条件の後にモデル値を得られたのはLaurie901/27固有セル、Powell543/28、Monroe802/13、Signy0/0。先行夏の候補GAM平均は8.813、11.902、6.485 g/m²（Signyは推定不能）；タグ内全GPSセル基準の比は0.985、0.928、0.982。原4タグ・48条件すべて保存し、[元CI](https://github.com/zuizui0223/mina/actions/runs/41168213176)はSUCCESS。

したがって『潜水が起きている場所ほどモデル上のオキアミ密度が高い』とは支持できない。なお潜水候補は実捕食・海上潜水ではなく、GAM自体は音響観測と海氷・塩分の入力を使用済み。Monroeのセンサゼロ点漂移7.75dbar、各島1タグ、年が異なる問題を保持。陽性結果は**原GPS・原TDR・GAM格子の技術的接続に成功したこと**であり、2050/2100年の生態学的予測ゲートは通過しない。
## 2026-10-31 source-fixed 16-tag actual sensor QA (run complete)


## 2026-10-31 pressure sensor quality 16-tag source extension

[Original BAS 16-tag × four ZOC method workflow](https://github.com/zuizui0223/mina/actions/runs/41176761764) **SUCCESS**: all 16 original frozen GPS/TDR matched tags were opened, and 64 source-offset 5dbar candidate profiles reconstructed. Source choice fixed to first four original matched tags per island, not based on outcome values. Provisional 1% 60-minute zero-offset range >2 dbar in **3 of 16** tags: Powell PI004 2.50 dbar, Monroe MIC001 7.7525 dbar, Monroe MIC002 11.4975 dbar. MIC002 had 3,246 candidate events, only 108 strict original-GPS time-bracketed (3.33%), with 20.5% maximum–minimum candidate count range across four correction algorithms. Signy/Laurie 0/4 tags above 2 dbar in this **nonrepresentative** subset; other three source series (LIC003, MIC004, SIC010) had 0 provisional 5dbar events despite usable pressure, which is *not* absence of biological diving. The original 4-tag pilot receipts and 16×4 source/QA breadth are reproduced.

Instrument-level positive endpoint = source processing and detection of candidate-instrument heterogeneity, **not a new ecological divergence or prey capture**. Original 300 matched tags cannot be interpreted uniformly without sensor/clock/land-activity QA, and the number flagged (3/16) is not a population failure frequency. The 2050/2100 breeding-pairs/N_eff/vegetation quantitative forecast remains NO-GO.


## 2026-10-31 external Paper2 terrestrial coast-source evidence linked, no ecological cross-system transfer

[Independent South Sandwich nesting coastline study PR199 V55 fixed source](https://github.com/zuizui0223/mina/blob/348e741dc046eaaf632ebd70c2b1f0d7ea36c794/results/PAPER2_V55_BAS_COAST_MAP_STRICT_LAND_AND_30M_CELL_SOURCE_RESULT.json) measured heldout Adélie–Chinstrap nest-species discrimination beyond original DEM slope/elevation using *independently published 2020 coastline distance*: strictly on-source-land 3 true heldout island balanced Brier improvement **+0.051197**, 3/3 positive. This is **exploratory heldout source model information**, not validated shore-to-nest walkability, accessible breeding area, penguin climate response, or an independent 122k nest-level island replication. The strict 30m occupied-cell weighted independent falsification was **unavailable** because Chinstrap cells on Bellingshausen n=16 and Thule Beach Point n=12, under preread n>=20 each locality/taxon, so **cell-dependence robust effect NOT established**. Draft PR199 remains on source-cell gate HOLD.

This provides a terrestrial-side geographic signal to articulate the **dual island access** question next to South Orkney original Chinstrap GPS×published-GAM marine co-location. The two data systems concern DIFFERENT islands, sites, years, observation grain and outcome variables and cannot be jointly fitted as a causal sea-to-land corridor / penguin breeding response without new aligned observations. It is not an approved cross-paper code merge, publication submission, or 2050/2100 N_eff/vegetation forecast.
