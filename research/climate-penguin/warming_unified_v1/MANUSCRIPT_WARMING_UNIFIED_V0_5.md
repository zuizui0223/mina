# Unequal climate predictability of marine niches and breeding assemblages in Antarctic penguins

**Unified warming-first manuscript, v0.5 | 8 November 2026 | Working analysis; not submitted**

**Scope:** One empirical paper in zuizui0223/mina PR #206, with the nested source-verified long-term exploratory test on PR #207. This supersedes the v0.1/v0.2 warming *framing* without retracting their real results. No reclassification of historic associations as future climate causality. No BTO, no UK JNCC as climate replication, no modification of main/Paper1/Paper2.

## Central question and falsifiable predictions

**Does the same measured sea-ice change transfer into predictable shifts in Antarctic penguin marine-resource partitioning, co-breeding species composition and colony-scale breeding counts?**

We distinguish three hypotheses rather than pretending that niche change, a change in the fraction of breeding pairs and colony abundance are the same outcome:

- **H1: Within-season marine trophic reconfiguration.** Gentoo–Adélie fish-share separation is associated with seasonal sea ice at Signy. Evaluate exactly the matched nine observed seasons, not hundreds of stomachs as independent climate years. Short-origin conditional hindcasts require lower error than the history-only mean.
- **H2: Reciprocal co-breeding assemblage reconfiguration.** Actual Adélie nest counts decline while gentoo counts increase at the same strictly co-observed census sites, yielding a rising ratio that is not solely a mathematical denominator effect. The observed sea-ice window must be specified (full 1991–2020 versus actual census years); ratio change alone does not establish turnover due to immigration, displacement, or competition.
- **H3: Forecast transfer.** If the H1/H2 climate association truly gives a quantitative future breeding prediction, models trained on preceding periods should beat the no-change benchmark on later, unseen five-year changes. They must do so with climate information actually available at the prediction origin, *not the test-period realized sea ice*. Prediction of nesting patches additionally requires the spatial census unit to match the habitat driver.

H1 and H2 describe positive empirical ecological patterns. H3 is not automatically a consequence of them. It is a diagnostic proposition now tested and not supported.

- **H4 (additional post-result, scale-matched descriptive test):** Does 1979–1990 absolute sea ice better describe observed 2001–2020 decadal Adélie nest-count trends across sites than contemporaneous 2001–2020 ice? The 26-site, four-region cohort, controls, windows, geographic holdouts and decision criteria were fixed before these new slope×climate scores were opened. A prelisted secondary contrast also evaluates historical-to-contemporary SIC change. This design is outcome-aware exploratory work—not independent preregistration, a delayed demographic response test, or evidence of penguin non-movement.

## Abstract

Environmental change may alter penguin diets and breeding populations on different temporal scales, but observational climate associations are not automatically transferable forecasts. We combined source-identified Antarctic nesting surveys, nearshore satellite sea ice (1979–2020), Signy stomach contents and breeding phenology, and three CMIP6 models. At six same-site, same-method co-breeding series (67 site-years, two regions), Adélie nests decreased while gentoo nests increased, raising the median gentoo:Adélie count ratio 6.02-fold. Census-year September ice did not consistently reflect all six sites' full-period August–November declines. At Signy, gentoo-minus-Adélie fish-share separation covaried with observed sea ice over nine seasons (r=0.781); a four-year conditional hindcast improved on a historical-mean baseline (MAE 0.184 versus 0.321) but did not provide an operational climate forecast. In a separately frozen exploratory analysis of 26 Adélie sites with 257 same-method census counts during 2001–2020, long-term site growth corresponded to historical-to-contemporary sea-ice change across regions (r=0.648 across sites; r=0.165 after region adjustment). This secondary climate-change predictor improved spatial leave-site-out MAE from 0.310 (region-only) to 0.266. Yet historical 1979–1990 *absolute* ice did not predict those trends better than 2001–2020 ice (MAE 0.293 versus 0.288), and the two climatologies were almost collinear (r=0.997). Separately, regressions using realized sea ice failed to outperform a zero-change baseline for later five-year nest-count changes (MAE 0.415 versus 0.339 across 47 test transitions). Under SSP5-8.5 in 2081–2100, CMIP6 projects +4.35°C at six sites and −23.94 percentage points of marine sea-ice concentration at four source-supported sites, not validated future nest counts. These results show geographically structured and response-specific climate associations, but do not establish a long climate debt, constrained breeding dispersal, or a temporally transferable demographic forecast.

## Introduction

Sea ice, terrestrial nesting substrate, food accessibility and seasonal timing are connected through distinct processes. A change in accessible pelagic resources can occur within a breeding season, whereas recruitment, colony fidelity, dispersal, snow-free nesting area and interspecific shifts may accumulate over multiple generations. It is therefore a testable claim—not an assumption—that a climate indicator which describes diet within one island also predicts five-year changes in nests across Antarctic sites.

The purpose here is to confront that transfer rather than to present independently observed warming, redistribution and breeding-space contraction as proof of a common climatic cause. We use observed breeding and dietary outcomes as primary evidence, climate projections as potential future drivers, and chronological hindcasts as a stringent criterion for quantitative biological forecasts. We do not identify salinity, warming of nesting land or greening as direct causes without their same-year response support.

This study is not the first to identify scale-dependent sea-ice associations or limited transfer of penguin demographic models. Iles et al. (2020; DOI 10.1111/gcb.15085) established a multidecadal-versus-annual contrast in Adélie sea-ice responses; Şen et al. (2023; DOI 10.1016/j.ecolind.2023.110239) assessed environmental-model temporal and geographic transfer at 24 Adélie colonies; and Youngflesh et al. (2026; DOI 10.1016/j.cub.2026.06.028) linked sea ice, Adélie diet and longer-term population trends at continental scale. The narrower contribution here is to put source-locked, same-method co-breeding assemblage histories, a *signed interspecific* dietary contrast and origin-time five-year nest-change validation into one auditable, explicitly conditional forecast hierarchy. These endpoints differ in species pairs, geography, time resolution and available predictors: the tests cannot establish that dietary processes are intrinsically more predictable than demographic processes.

## Methods

### Source support and study grains

The strict common-site co-breeding cohort consists of ARDL, BISC, LION, LLAN, PCHA and PETE, in two ecological regions. Both focal species had positive nest counts in all matched observed years; one source method was required for each within-site series. The earlier broader macro archive contains 54 qualifying site-by-species long-series (Adélie 39, chinstrap 7, gentoo 8), but these do not represent 54 independent sites or climate units. We preserve source site and calendar-year identity, and never treat a missing count as absence.

Nearshore observed sea ice is derived from original satellite SIC, distinguishing mean August–November 1991–2020 from September values in actual census years. For the same six sites, CMIP6 projections include three source models, two SSP pathways, and 2041–2060/2081–2100 horizons relative to 1995–2014. All six have air-temperature support, while only four have source-confirmed marine cells within 50 km. These four sites reuse two marine model cells.

At Signy, the common-year stomach contrast is *signed* mean fish/(fish+crustaceans) for gentoo minus Adélie, with 349 and 73 original stomachs across nine seasons (2001–2009). This is not the older independently analyzed three-species/772-stomach distance statistic. The same-year hatching contrast is chinstrap minus Adélie, not the same species pair as diet. There are nine common climate years, not 422 independent years. Annual hatching-series method and colony switches are audited in the source contract.

### Prediction criterion and withheld data

For marine resource use, the pre-existing Signy rolling-origin diagnostic learns from at least five prior seasons and evaluates 2006–2009. It uses **realized target-year SIC** (conditionally observed environment), so is a small retrospective nowcast, not an operational climate forecast.

For actual nest-count prediction, we use frozen original MAPPPD known-method census series, original 1991–2020 August–November SIC and the 54-site-species source cohort, verified at exact Git blob identifiers. For each eligible species/site, mean log(1+nests) is taken within nonoverlapping five-year bins with at least two original counts. Changes between consecutive bins form the response. This gives 87 response transitions in 20 geographical site codes and 29 site×species units. Training always ends before held-out periods ending 2010, 2015 or 2020, with 47 total held-out transitions. Tests repeat site IDs and adjacent transitions share census blocks, so they are not 47 independent experiments.

The first source-locked audit (v3) evaluated species, site, year and sea-ice predictors with **realized held-out-period SIC**. The follow-on audit (v4) independently reproduced all 94 v3 model predictions containing ice terms and evaluated six combinations of two ridge-response models with three SIC inputs known at forecast origin: (i) no change, (ii) last observed same-site SIC change, (iii) mean earlier SIC change across distinct site×period climate units in the same region. The target-period SIC is used only to score climate predictions and reproduce v3 controls, never in a v4 biological forecast input. Ridge penalties and target definition were inherited from exploratory v3 and must not be described as new preregistration.

We use mean absolute error and RMSE to compare models with a **zero-change five-year nest benchmark**. A climate term is not a forecast simply because a regression can return a coefficient. A numerical 2050/2100 nest forecast is only defensible if an origin-time hindcast demonstrates transferable skill over that benchmark, with sufficient regional as well as time support; this is stricter than the evidence here.

**Separate climatic-legacy diagnostic (post-hypothesis-generation):** After seeing the earlier annual and five-year prediction failures, we froze a narrower comparison *before calculating any 11–20-year exposure scores*: at the same Adélie site, could August–November SIC averaged over years t−20 to t−11 predict next-year log nest-count change better than SIC from t−10 to t−1? We extended the original OSI SAF OSI-450-a1 v3.1 product to 1979 using official monthly fields, with a 120-site-month source-bridge check against the established daily-derived product. The fixed 301 positive-to-positive same-method count intervals yielded 208 eligible full-window observations; 111 site-known 2006–2018 intervals were scored with chronological training, site+calendar trend, fixed ridge penalties, and zero-growth baseline. The primary contrast was fixed in advance of the new lag test, but the overall idea and its data source were selected after observing prior results, so this is not an independent confirmatory preregistration.

### Long-term Adélie site-trend test (post-result scale-matched addition)

To avoid treating a one-year nest-count fluctuation as a multidecadal outcome, a separate exploratory design was committed before evaluating the new site slope × historical SIC contrasts. We selected the already fixed 39-site Adélie source cohort, retained only the original site method and unambiguous 2001–2020 census counts, and required at least four distinct seasons over ten or more years. This yielded 26 sites (17 Victoria Land, five central-west Antarctic Peninsula, three South Shetland Islands, one Adélie Land) and 257 site-year counts. The response was the actual-year least-squares slope of log(1+nest count), converted to log1p nests per decade, not annual residual change. True recorded zeros were not imputed to missing years.

We rebuilt official OSI SAF OSI-450-a1 v3.1 1979–1990 August–November monthly nearshore fields at 40 source coordinates and verified the overlap with the original daily-derived 1991–2020 series (120 matched site-months, median absolute difference 0.081 SIC percentage points). Primary predictors were historic 1979–1990 (12y) versus contemporaneous 2001–2020 (20y) annual mean SIC; prespecified secondary variables were an equally long recent 2009–2020 (12y) climatology and the change between 1979–1990 and 2001–2020 SIC. For each site, we required complete four-month and annual source support and used the same 0–100km ocean mask and month-day weights.

All comparisons included an unchanged-decadal-count baseline, a training-site average, a ridge-shrunk region-only baseline, and identical ridge climate penalties. Twenty-six leave-one-site-out folds tested spatial generalization; four leave-one-region-out folds exposed geographic dependence. Test-site responses were never used to standardize climate predictors or tune models. The primary hypothesis was *historical absolute SIC outperforms contemporary absolute SIC*; the change-predictor analysis was fixed as secondary. No temporal forecast or movement mechanism can be inferred from these spatial holdouts.

## Results

### 1. Observed breeding assemblage reconfiguration is not a uniform annual-ice response

Adélie counts declined and gentoo counts increased at all six focal co-breeding sites between each site's first and last shared census, giving rising gentoo/Adélie breeding-count ratios across all six series. These six sites comprise **67 site-years**, but only **two regions**, with overlapping climatic grid cells; neither 67 records nor six sites are independent regional experiments. The **median across six site-level first-to-last ratio fold changes is 6.02**; the leave-one-site medians range 5.84–6.21, while BISC's extreme 245-fold change starts from only 45 gentoo nests. These differences are real observed census contrasts, not standardized rates over a common calendar interval.

| Site (shared years) | Adélie nests, first → last | Gentoo nests, first → last | Gentoo:Adélie ratio fold | Observed-census-year September SIC trend (pp/decade) |
|---|---:|---:|---:|---:|
| ARDL (21) | 1,205 → 339 | 3,678 → 6,428 | 6.21× | −2.184 |
| BISC (8) | 1,801 → 522 | 45 → 3,197 | 245.12× | +5.229 |
| LION (7) | 7,113 → 3,473 | 2,642 → 3,789 | 2.94× | −11.799 |
| LLAN (16) | 5,612 → 3,246 | 1,498 → 6,123 | 7.07× | +8.473 |
| PCHA (7) | 18 → 4 | 1,200 → 1,556 | 5.84× | +8.667 |
| PETE (8) | 553 → 174 | 2,145 → 3,498 | 5.18× | +2.575 |

August–November SIC declined over the full **1991–2020** observational period at all six sites; however, its **census-year-restricted** trend increased at 2/6 sites for August–November and 4/6 for September. This is an explicit mismatch of sampling windows and season definitions: it does not show that sea ice increased across the full 30 years or that its effect on penguin breeding was absent. Neither time window is evidence for a monotonic year-by-year causal shift from sea ice to one species or the other. The site-wise table is descriptive, reconstructed with immutable original count and trend source hashes and independently audited in the six-site CI artifact.

The broader historical study independently observed gentoo/Adélie ratio increases at seven of seven same-site comparisons and chinstrap/Adélie increases at six of six. These comparisons overlap geographic sites and are not 13 independent experimental islands. They support an assemblage shift, not a temperature-response coefficient.

### 2. Marine and timing niches are differently associated with the same observed ice series

For matched nine-year Signy observations, the signed gentoo–Adélie fish-share contrast correlated with SIC (r = +0.7814), retaining r = +0.7649 after removing linear calendar-year trends. The chi​nstrap–Adélie hatching gap correlated weakly (r = −0.0661); a null effect or temporal-niche invariance does not follow from nine years. The joint diet-versus-timing correlation is similarly weak, but the two niche measures use **different species pairs**. A previous three-species diet comparison (772 stomachs) had r = +0.7839 and a three-statistic permutation-adjusted p = 0.0342, not an independent climate replicate or inferential correction for all prior exploratory comparisons.

The four held-out Signy conditional diet years yielded MAE 0.184 for seasonal SIC regression versus 0.321 for historical mean. This positive short-horizon result remains limited to one island, four evaluation years and realized climate input. A prior external-island attempt using a related but *different absolute* diet measure did not beat its own mean baseline, so we make no transferable marine-response claim beyond this local series.

### 3. The five-year breeding response fails real forecast transfer

| Predictor in five-year nest-change models | Pooled MAE |
|---|---:|
| No change in nest count | **0.338736** |
| Regression given realized future SIC (v3 oracle) | 0.415112 |
| Regression given zero future SIC change at origin | 0.412491 |
| Regression given last observed site SIC change | 0.431069 |
| Regression given past regional SIC mean change | 0.418280 |
| Species-interaction variants using origin-available SIC | 0.411280–0.425857 |

The origin-available SIC approximations themselves have MAE 9.36, 13.83 and 11.00 SIC percentage points respectively across 47 test records (zero, last, region). The climate regressions do not beat the unchanged-nest baseline even when retrospectively given the correct held-out ice. This is a failure of **these models and these predictor/data grains**, not evidence that ice or warming has zero ecological effects. The models are exploratory and no inferential p-values are attached to selecting their minimum score.

The previously reported 39-site spatial historical association (Adélie long-term count trend versus SIC, r = +0.622) is retained, but historical two-window/23-site time transfer did not reproduce the average trend change. Spatial covariance and future temporal transfer are different estimands.

**A newly executed 10–20-year lag test does not rescue annual prediction.** In 111 time-ordered Adélie annual transitions from 17 sites, pooled MAE was 0.1517 for no nest-count change, 0.1799 for the preceding 1–10-year SIC mean, 0.1751 for the 11–20-year mean, 0.1810 for both means and 0.1785 for a prespecified 3–7-year recruitment-period SIC mean (all errors in annual log nest-change units, not directly comparable to the five-year MAE above). Thus the long-historical window was slightly preferable to the recent window by transition-weighted MAE (0.0048), but not to the no-change benchmark. On equal-site averaging, the new-versus-recent window preference reversed; a site/year resampling approximation gave a paired improvement interval spanning zero (95% −0.0053 to +0.0177). These observations give no empirical support for a 10–20-year climatic legacy as a predictive explanation of immobile breeding distribution.

### 3b. Matching the decadal breeding trend reveals regional covariance, not an absolute climatic legacy

In the separately frozen decadal-scale cohort, 26 sites supplied 257 same-method Adélie observations for 2001–2020. Mean observed SIC from 1979–1990 and 2001–2020 was highly similar across sites (r=+0.997, and r=+0.960 after residualizing four region means), above the fixed |r|≥0.95 non-identifiability threshold. The site-growth correlation with historical absolute SIC was r=+0.554 (region-residual r=+0.036); for contemporary absolute SIC it was r=+0.578 (region-residual r=+0.080). The historical-to-contemporary SIC difference correlated more strongly with site trends (r=+0.648), but region adjustment reduced it to r=+0.165. Thus the observed climate-change signal mostly contrasts regions with different directions of sea-ice change and Adélie abundance trends.

| Fixed decadal site-growth predictor | Leave-site-out MAE | Leave-region-out MAE |
|---|---:|---:|
| No long-term change | 0.4260 | 0.4260 |
| Region only | 0.3097 | 0.5791 |
| Region + historical 1979–1990 mean SIC | 0.2933 | 0.4919 |
| Region + contemporary 2001–2020 mean SIC | 0.2884 | 0.4790 |
| Region + contemporary 2009–2020 mean SIC (equal-length sensitivity) | 0.2873 | 0.4810 |
| Region + mean SIC change (secondary) | **0.2664** | **0.3910** |

The *primary historical versus contemporary* test did not support a long-lag advantage; contemporary mean SIC slightly outperformed earlier SIC by leave-site and leave-region MAE, and the two time periods were nearly collinear. The exploratory *change* variable was the lowest-error predictor under this fixed regression procedure. It improved region-out retrospective spatial prediction relative to the zero-growth baseline, but these holdouts contain only four unequally represented regions (one a singleton), and within-region climate–demography covariance was weak. **These scores describe regional spatial association, not a response delay, measured breeding dispersal, or future site-count forecast.** In contrast, the annual and five-year tests hold out future biological periods and remain unsuccessful; performance cannot be numerically compared across targets that use different response grains and site selections.

### 4. The physical warming scenarios are quantitative; the future breeding response remains unidentified

| Scenario | Period | Mean Δair temperature (6 sites) | Mean ΔSIC (4 supported sites) |
|---|---|---:|---:|
| SSP2-4.5 | 2041–2060 | +1.66 °C | −11.27 pp |
| SSP2-4.5 | 2081–2100 | +2.51 °C | −19.96 pp |
| SSP5-8.5 | 2041–2060 | +1.92 °C | −13.96 pp |
| SSP5-8.5 | 2081–2100 | +4.35 °C | −23.94 pp |

Four sea-ice sites represent two model marine grid-cell fingerprints, not four independent future ice trajectories. Reweighting the two distinct cells equally gives −35.74 pp rather than −23.94 pp for SSP5-8.5 late-century; neither is an empirical breeding response. The three GCMs comprise one member each, rather than a climate uncertainty ensemble sufficient to claim site-level calibrated odds. Historical CMIP6 coastal SIC biases are strong in this source and in the Antarctic sea-ice literature (Schroeter et al. 2025, DOI 10.1080/07055900.2025.2507880). In the existing Signy *conditional* fish-share scenario, eight of twelve future model combinations pass a 50 km grid-distance gate; extrapolative means are not a validated future biological forecast.

### 5. Breeding-space contraction remains positive but cannot be assigned to warming

The independently replicated decrease in fixed census-patch effective breeding number at Palmer/Signy (observed reductions around 19%–83% across distinct panels) is a valid breeding-structure result. The annual colony/patch-level matching to future model ocean grids and time-varying snow, vegetation and nesting polygon boundaries has not been demonstrated. Accordingly, this paper treats spatial concentration as a **biological downstream hypothesis under warming**, not an estimated quantitative response to SIC, salinity or vegetation. Neither salinity change nor mapped land vegetation is entered as a coefficient for nests or occupancy without outcome-matched data.

## Discussion: what the single paper establishes

The positive biological evidence includes **reciprocal absolute nesting trajectories**, not merely a compositional ratio rise: Adélie decreases and gentoo increases at each of six repeatedly sampled breeding sites. A separate 26-site decadal growth comparison shows that climate-era *change* corresponds to regional differences in trends, while long-lag *absolute* SIC is not superior to contemporary SIC and their individual effects are non-identifiable. Multiple measured aspects of penguin ecology *do not supply an interchangeable climate-response scale*. A same-island marine dietary contrast co-varies with seasonal SIC; an unlike-paired hatching-gap contrast does not show that same correlation in nine matched years; and a broad five-year nest-count model fails time-origin prediction even when given realized sea ice. The last failure helps prevent an unwarranted 2050/2100 colony-number forecast, but does not by itself prove which mechanism causes decoupling.

A concrete ecological interpretation to test—not yet an inference—is that short-lag food accessibility responds to ocean conditions, whereas colony fidelity, density dependence, recruitment, terrestrial site suitability and larger-scale demographic forcing gate how marine changes reach breeding numbers and space. Neither the prior 11–20-year annual-prediction comparison nor the new long-term site-trend comparison established the specific climatic-legacy or philopatry explanation. The secondary sea-ice-*change* indicator deserves to be retained only as exploratory regional covariance, not interpreted as a direct temperature- or SIC-response coefficient. Differences in timing, spatial grain and site selection continue to preclude a direct climate-debt estimate. To demonstrate this interpretation would require non-overlapping biological cohorts across regions, true pre-breeding forcing plus survival/recruitment or independent juvenile return records, and year-specific spatial nesting counts with matched land and marine exposures.

The study should not be framed as a causal demonstration that retreating ice replaces Adélie by gentoo, that vegetation expands on abandoned nesting ground, or that changing diet is evidence of direct interspecific competition. Nor does falling abundance at these six selected co-breeding sites demonstrate that individual penguins fail to move: in the broader 39-site Adélie long-series archive, 25 site slopes were positive and 14 were negative, and without identity-marked movements, nonbreeding states and colonization sites, individual redistribution is not identifiable. The smallest biological climate replicate is nine seasons on one island; the breeding forecast has 47 dependent records at 20 sites from source-selected known-method series. Those bounds govern novelty and journal scope.

**Prior-work boundary:** Iles et al. (2020) already separated multidecadal sea-ice association from weak annual demographic predictability, while Şen et al. (2023) directly tested spatiotemporal forecast transfer for Adélie abundance. Youngflesh et al. (2026) established a continent-scale sea-ice–diet–abundance connection. Our results do not replicate these studies independently or overturn their findings. The specific additional evidence is reciprocal absolute counts in six strict sympatric census series, Signy *between-species signed fish-share* variation, a source-verified 1979–2020 climate-era exposure comparison against 26 site-specific decadal growth slopes with explicit region holdout, and a transparent perfect-forcing-versus-origin-time comparison for later five-year nest changes. The association between sea ice and multidecadal Adélie growth, and the annual-scale weakness, were already shown by Iles et al. (2020); neither the scale contrast nor the climate–diet–abundance linkage alone constitutes a new mechanism. Publication claims should be proportionate to this narrower, partly exploratory integration.

**Concluding statement:** Antarctic penguin breeding-community reorganization and seasonal dietary variation are empirically detectable under changing sea-ice conditions, and historic-to-contemporary sea-ice change covaries with geographically structured decadal breeding trends. Yet the absolute historic climate did not outperform contemporary ice, and neither these spatial associations nor a local diet nowcast yields a validated *time-forward* prediction of colony nest counts, site occupancy or spatial concentration. The future climate forcing is quantitatively scenario-dependent; future breeding demography is an open prediction problem.

## Reproducibility and provenance

- Main activity branch: [Draft PR #206](https://github.com/zuizui0223/mina/pull/206).
- Original nine-year and six-site cohort: warming_unified_v1/ANALYSIS_CONTRACT_20261107.md, source-verified outputs and figures.
- Original 2010/2015/2020 five-year forecast test: warming_unified_v1/forecast_gate_v3/build.mjs, [successful Actions run 42379420066](https://github.com/zuizui0223/mina/actions/runs/42379420066).
- Real origin-time comparison and four projected physical scenarios: warming_unified_v1/forecast_gate_v4/build.mjs, [successful Actions run 42430582918](https://github.com/zuizui0223/mina/actions/runs/42430582918), artifact penguin-origin-time-forecast-audit-v4 (metrics, predictions, future physical table, Japanese numeric report).
- Source-pinned Signy conditional fish contrast hindcast: warming_unified_v1/forecast_gate_v2/build.mjs.
- [Post-hypothesis-generation frozen 11–20y SIC diagnostic PR #207](https://github.com/zuizui0223/mina/pull/207), [run #42439297053](https://github.com/zuizui0223/mina/actions/runs/42439297053), artifact penguin-legacy-ice-and-chronological-prediction-v1; complete [Japanese result report](../climatic_legacy/RESULT_JA_20261108.md).
- [Pinned original-count six-site effect-size audit (successful CI run #42440280519)](https://github.com/zuizui0223/mina/actions/runs/42440280519): script [audit_six_site_effects.mjs](audit_six_site_effects.mjs), artifact penguin-reciprocal-six-site-effects-v1 (ID 13601322352), with six site-wise rows and summary JSON.
- [Frozen decadal site-slope climate-era test](../climatic_legacy/FROZEN_LONGTERM_SLOPE_V2_20261108.md), [successful GitHub Actions #42440306026](https://github.com/zuizui0223/mina/actions/runs/42440306026), artifact penguin-climatic-legacy-longterm-slope-v2 (ID 13601222672), full [Japanese interpretation](../climatic_legacy/RESULT_LONGTERM_SLOPE_V2_JA_20261108.md).
- No source census/sea-ice file was modified; Paper1, Paper2 and main remain untouched.

**Editorial gate:** This is an evidence-preserving integrated working manuscript, not a definitive future-demography forecast or a submitted article.