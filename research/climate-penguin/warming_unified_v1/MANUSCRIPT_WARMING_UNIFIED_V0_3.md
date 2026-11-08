# Unequal climate predictability of marine niches and breeding assemblages in Antarctic penguins

**Unified warming-first manuscript, v0.3 | 8 November 2026 | Working analysis; not submitted**

**Scope:** One empirical paper in zuizui0223/mina PR #206. This supersedes the v0.1/v0.2 warming *framing* without retracting their real results. No reclassification of historic associations as future climate causality. No BTO, no UK JNCC as climate replication, no modification of main/Paper1/Paper2.

## Central question and falsifiable predictions

**Does the same measured sea-ice change transfer into predictable shifts in Antarctic penguin marine-resource partitioning, co-breeding species composition and colony-scale breeding counts?**

We distinguish three hypotheses rather than pretending that niche change, a change in the fraction of breeding pairs and colony abundance are the same outcome:

- **H1: Within-season marine trophic reconfiguration.** Gentoo–Adélie fish-share separation is associated with seasonal sea ice at Signy. Evaluate exactly the matched nine observed seasons, not hundreds of stomachs as independent climate years. Short-origin conditional hindcasts require lower error than the history-only mean.
- **H2: Long-term assemblage reconfiguration.** The relative abundance of gentoo and Adélie nests changes consistently in co-monitored sites, independently of census-method switches. The observed sea-ice window must be specified (full 1991–2020 versus actual census years).
- **H3: Forecast transfer.** If the H1/H2 climate association truly gives a quantitative future breeding prediction, models trained on preceding periods should beat the no-change benchmark on later, unseen five-year changes. They must do so with climate information actually available at the prediction origin, *not the test-period realized sea ice*. Prediction of nesting patches additionally requires the spatial census unit to match the habitat driver.

H1 and H2 describe positive empirical ecological patterns. H3 is not automatically a consequence of them. It is a diagnostic proposition now tested and not supported.

## Abstract

Antarctic warming changes the climatic environment of penguin colonies, yet measured resource use and breeding populations may respond at different spatial and temporal grains. We combined original multi-season MAPPPD nesting records with matched observational sea-ice series, a Signy Island stomach-content series, independently archived breeding phenology, and three CMIP6 projections. In six same-site, same-method co-breeding series across two regions, Adélie nest counts declined and gentoo counts increased; meanwhile, full-period August–November nearshore sea ice declined at all six sites, whereas September sea ice sampled only in census years increased at four. At Signy, nine common seasons (2001–2009) comprising 422 Adélie and gentoo stomachs gave a positive association between ice and the signed gentoo–Adélie fish-share difference (r = 0.781); the differently paired chinstrap–Adélie hatching-day gap had little association with that same ice series (r = −0.066). A four-year climate-conditioned rolling hindcast of fish-share difference improved MAE over a past-mean baseline (0.184 versus 0.321), but used realized seasonal ice and provides no distant-future skill validation. We then reconstructed 87 adjacent five-year census transitions and evaluated 47 later transitions from 20 sites under chronological training. The unchanged-count benchmark (MAE 0.339 in five-year mean-log-nest-change units) outperformed both an observed-future-ice regression (0.415) and regressions using only origin-available historic ice estimates (MAE 0.412–0.431). Future physical exposure can nevertheless be quantified: for SSP5-8.5 in 2081–2100, three CMIP6 models gave an average +4.35°C surface-air change at six co-breeding sites and −23.94 percentage points in sea-ice concentration at four marine-supported sites (two distinct ocean model cells), relative to 1995–2014. Thus, demonstrable assemblage and marine niche changes do not themselves constitute transferable forecasts of breeding abundance. Because the dietary and breeding evaluations use different islands, horizons and information sets, their error scores do not estimate a universal difference in intrinsic predictability between ecological processes. Predictions of future colony numbers, occupation or nesting-space concentration remain unsupported by the present climate-response model.

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

## Results

### 1. Observed breeding assemblage reconfiguration is not a uniform annual-ice response

Adélie counts declined and gentoo counts increased at all six focal co-breeding sites, giving rising gentoo/Adélie breeding-count ratios. August–November SIC declined over the full 1991–2020 observational period at all six sites, but the sampled-year September series increased at four sites. These are different time windows and sometimes different monthly means: neither is evidence for a monotonic year-by-year causal shift from sea ice to one species or the other.

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

The positive empirical advance is that multiple measured aspects of penguin ecology *do not supply an interchangeable climate-response scale*. Repeated co-breeding sites show reciprocal absolute nesting trajectories; a same-island marine dietary contrast co-varies with seasonal SIC; an unlike-paired hatching-gap contrast does not show that same correlation in nine matched years; and a broad five-year nest-count model fails time-origin prediction even when given realized sea ice. The last failure helps prevent an unwarranted 2050/2100 colony-number forecast, but does not by itself prove which mechanism causes decoupling.

A concrete ecological interpretation to test—not yet an inference—is that short-lag food accessibility responds to ocean conditions, whereas colony fidelity, density dependence, recruitment, terrestrial site suitability and larger-scale demographic forcing gate how marine changes reach breeding numbers and space. To demonstrate this interpretation would require non-overlapping biological cohorts across regions, true pre-breeding forcing plus survival/recruitment or independent juvenile return records, and year-specific spatial nesting counts with matched land and marine exposures.

The study should not be framed as a causal demonstration that retreating ice replaces Adélie by gentoo, that vegetation expands on abandoned nesting ground, or that changing diet is evidence of direct interspecific competition. The smallest biological climate replicate is nine seasons on one island; the breeding forecast has 47 dependent records at 20 sites from source-selected known-method series. Those bounds govern novelty and journal scope.

**Prior-work boundary:** Iles et al. (2020) already separated multidecadal sea-ice association from weak annual demographic predictability, while Şen et al. (2023) directly tested spatiotemporal forecast transfer for Adélie abundance. Youngflesh et al. (2026) established a continent-scale sea-ice–diet–abundance connection. Our results do not replicate these studies independently or overturn their findings. The specific additional evidence is reciprocal absolute counts in six strict sympatric census series, Signy *between-species signed fish-share* variation, and a transparent perfect-forcing-versus-origin-time comparison for later five-year nest changes. Publication claims should be proportionate to this narrower, partly exploratory integration.

**Concluding statement:** Antarctic penguin breeding-community reorganization and seasonal dietary niche shifts are empirically detectable under changing sea-ice conditions, but the climate relation that locally explains or nowcasts one niche axis does not yet yield a validated future prediction of colony nest counts, site occupancy or spatial concentration. The future climate forcing is quantitatively scenario-dependent; future breeding demography is an open prediction problem.

## Reproducibility and provenance

- Main activity branch: [Draft PR #206](https://github.com/zuizui0223/mina/pull/206).
- Original nine-year and six-site cohort: warming_unified_v1/ANALYSIS_CONTRACT_20261107.md, source-verified outputs and figures.
- Original 2010/2015/2020 five-year forecast test: warming_unified_v1/forecast_gate_v3/build.mjs, [successful Actions run 42379420066](https://github.com/zuizui0223/mina/actions/runs/42379420066).
- Real origin-time comparison and four projected physical scenarios: warming_unified_v1/forecast_gate_v4/build.mjs, [successful Actions run 42430582918](https://github.com/zuizui0223/mina/actions/runs/42430582918), artifact penguin-origin-time-forecast-audit-v4 (metrics, predictions, future physical table, Japanese numeric report).
- Source-pinned Signy conditional fish contrast hindcast: warming_unified_v1/forecast_gate_v2/build.mjs.
- No source census/sea-ice file was modified; Paper1, Paper2 and main remain untouched.

**Editorial gate:** This is an evidence-preserving integrated working manuscript, not a definitive future-demography forecast or a submitted article.