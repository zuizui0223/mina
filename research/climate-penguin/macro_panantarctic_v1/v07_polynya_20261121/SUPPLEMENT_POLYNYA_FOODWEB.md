# Supplementary methods and results

## S1. Source identity, observation support and measurement provenance

The manuscript reuses frozen derived data; it does not treat a new calculation on the same pixels as an independent ecological replication. The original optical source is Youngflesh et al. (2026), Zenodo record 17409948. The downloaded original archive contains 256,425,816 bytes, with MD5 e29a2f68c84e3a515044d554540def2f. The released Landsat 4/5/7 reflectance RDS has SHA256 f86ba97f98bca33c1ff57a1ca1b6783f92c29d952710ce7a4256f0109323b50b. The broader 860-record panel covers 1996 and 1999–2012 (15 season-start years), 88 source sites, 82 distinct GLORYS wet cells and 13 reporting regions. The 439-record polynya panel is limited to 2004–2010; it is not a 15-year polynya series.

Source pixels satisfy guano_bin = 1 and bad = 0; the original minimum support is an average of at least two pixels per colony image. The seasonal reconstruction averages actual image-day values equally, rather than allowing an image with more selected pixels to dominate. The response is an optical δ¹⁵N reconstruction from the source calibration data, not a laboratory measurement for each colony-season. The final Youngflesh article's accepted-image table is not identical to the released pixel archive: nine HOPE image dates (361 L7 rows) in the latter were not found in the former. The reason was not established. No post-result removal from the frozen ecological sample was made on that basis. This difference remains a source-selection limitation and prevents claiming exact reproduction of the published full diet analysis.

DEEP-AA version 1.1.0-2023 is cited separately from its source paper (Lin et al. 2024). The recommended SIC60_6.25km_20d.zip has MD5 f3f958389cc5e67ac1c4e3a6ee164318 and SHA256 b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9. Extraction used 4,077 daily native files and the original geographic coordinates. The publication describes satellite-derived classifications; the resulting exposure is not a direct observation of prey density, winter foraging or a random environmental intervention. Daily valid zeros remain zeros. Product outages and insufficient monthly coverage remain missing.

The 100-km winter polynya measure, approximately 150-km summer sea-ice concentration and nearest-wet-cell GLORYS variables have deliberately documented, different spatial supports. They should not be represented as co-located direct field measurements. Their different seasons also prevent interpreting summer-ice adjustment as a test of winter spatial structure at fixed total ice extent.

## S2. Models, informative regions and numerical reproduction

Every main comparison shares the same 439 rows. M0 includes colony and region-by-season fixed effects, mean centred image day and mean squared centred image day (the square is taken before seasonal averaging), November–February sea-ice concentration and seawater temperature. M_S adds summer practical salinity, M_P adds winter coastal-polynya fraction, and M_SP adds both. Original coefficients use the single-fit optical response. The author-method sensitivity replaces only that response with the mean of 1,000 source-calibration fits.

Fixed effects were reproduced with an independent explicit dummy-matrix QR projection. No function from the original fitting implementation was imported. Cluster covariance follows the archived CR1 convention: the sandwich covariance is multiplied by G/(G−1) × (n−1)/(n−k), where G is the number of retained region clusters, n is the retained row count and k is the number of retained slope terms after absorption. This convention does not count absorbed fixed-effect parameters in k. It is documented to make the finite-sample approximation reproducible; it is not a guarantee of exact coverage with few clusters.

Three single-colony regions provide no residual exposure information after colony and region-by-season effects: Adelie Land (5 main-panel rows), Palmer Land (6) and Queen Mary Land (3). Excluding these 14 rows leaves 425 observations, 82 sites and eight informative regions. All slopes and residual sums of squares remain numerically unchanged. The 21 November 2026 support sensitivity recalculates only the cluster correction and t reference on this support. The corresponding matched temporal support is 347 of 358 rows in the same eight regions. This selection is determined by exposure information after the fixed effects, not by isotope values.

### Source-locked audit of the reporting increment and identifying exposure scale (22 November 2026)

The primary slope was originally reported per **10 percentage points** of polynya area fraction, which remains the coefficient and uncertainty unit in the frozen main results. This is a scaling convention, not evidence that the model frequently observes independent changes of 10 percentage points after adjustment. An additional **descriptive** audit recomputed the variance of the polynya covariate using the exact original 439 rows, independently absorbing the source colony and region-by-season dummies with a pivoted QR, then projecting against the same M0 summer covariates (and additionally salinity for M_SP). No ecological outcome or fitted exposure window was selected or changed.

| Frozen exposure/design | Original/raw SD (pp) | Exposure SD after all model controls (pp) | Same frozen coefficient per 10 pp (‰) | Coefficient per 1 residual-exposure SD (‰) |
|---|---:|---:|---:|---:|
| All 439 polynya values | 6.3115 | — | — | — |
| M_P: 439 original records | — | **1.6011** | **−1.0031** | **−0.1606** |
| M_SP: same 439, including salinity | — | **1.5879** | **−0.9216** | **−0.1463** |
| M_P: 425 informative records | — | 1.6273 | −1.0031 | −0.1632 |
| M_SP: 425 informative records | — | 1.6139 | −0.9216 | −0.1487 |

The full-panel SD uses the observed 439 rows; 14 single-colony-region rows have effectively zero identifying exposure after the fixed effects. Across the full 439 panel, the residualised M_P polynya regressor has a 10th–90th percentile span of approximately **−1.55 to +1.75 percentage points**; only 7 of 439 absolute residuals reach 5 points, and only one reaches 10. The reported 10-point increment is approximately **6.25 residual-exposure SDs** (6.30 after salinity adjustment). These residuals are mathematical deviations after adjustment, not observed interventions, a counterfactual treatment distribution or the raw between-year differences of individual colonies. The slopes, CV3 intervals, model comparisons, source counts and calibration sensitivity are unchanged.

The independent frozen-input script is `audit_polynya_estimand_scale_20261122.py`, with `source_inputs/polynya_estimand_scale_audit_20261122.json` as its concise descriptive receipt. It verifies the frozen four ZIP hashes and original 860→439 site-season join before using Frisch–Waugh–Lovell algebra to reproduce the existing M_P/M_SP coefficients. This post-result scaling audit does not provide a new p value, confirm a biological mechanism, or solve selection and small-region uncertainty.

### Table S1. Frozen estimates and informative-region uncertainty

All entries are in ‰ per 10-percentage-point increase in winter polynya fraction. The P0−P1 contrast uses the full covariance of the simultaneous coefficients. Both archived CR1 conventions remain here for traceability; the manuscript also prominently displays the additional cluster-jackknife intervals in Table S2. The 425-row main CR1 sensitivities are support audits dated 21 November 2026. The 347-row temporal CR1 sensitivities were already present in the frozen temporal analyses.

| Response and model | Estimate | Nominal 11-region 95% interval | Informative 8-region 95% interval |
|---|---:|---:|---:|
| Original response, M_P | −1.0031 | [−1.4668, −0.5395] | [−1.5047, −0.5015] |
| Original response, M_SP | −0.9216 | [−1.3493, −0.4939] | [−1.3843, −0.4589] |
| Author R1,000 mean, M_P | −1.0233 | [−1.4982, −0.5485] | [−1.5371, −0.5096] |
| Author R1,000 mean, M_SP | −0.9411 | [−1.3789, −0.5033] | [−1.4148, −0.4675] |
| Original response, P0−P1 | −0.6877 | [−1.2962, −0.0792] | [−1.3461, −0.0293] |
| Author R1,000 mean, P0−P1 | −0.6933 | [−1.3093, −0.0773] | [−1.3598, −0.0267] |

In the 358-row original simultaneous model, P0 is −1.3790 [−2.2705, −0.4876] and P1 is −0.6913 [−1.4393, +0.0566] under the archived nominal-11-region intervals. Separate P0-only and P1-only regressions are not the basis for the temporal contrast. The raw P0–P1 correlation is +0.796; after the full adjustment it is −0.390. Their adjusted standard deviations are approximately 1.238 and 1.336 percentage points. Reporting per 10 percentage points therefore scales a local conditional slope; it does not demonstrate a typical within-colony change of that magnitude.

### Additional uncertainty audit: unequal regional information

Eight nonzero-information regions do not provide equal identifying information. After all M_P covariates and fixed effects are removed, Victoria Land contributes 55.0263% of the residual polynya sum of squares and Wilkes Land 19.0106%. The inverse sum of squared regional information shares is 2.8439 for M_P and 2.8793 for M_SP. These concentration indices describe the design; they are not inferential degrees of freedom or new counts of independent regions.

This concentration motivated one bounded uncertainty diagnostic, selected before calculating its intervals: the cluster-jackknife CV3 of MacKinnon et al. (2023, their Eq. 18). With G = 8, its covariance is (G−1)/G times the sum, over omitted regions, of the outer product of each leave-region-out coefficient vector minus the full coefficient vector. The centre is the full estimate, not the mean leave-out estimate. Each fit reconstructs and absorbs the same colony and region-by-season fixed effects. Every retained slope design has full rank. A t(7) reference gives the intervals below; a temporal contrast uses its complete coefficient covariance. This is an additional 21 November 2026 diagnostic on the frozen design, not a prespecified confirmation of the ecological hypothesis.

### Table S2. Cluster-jackknife uncertainty on the fixed informative support

Units are ‰ per 10 percentage points. M_P and M_SP use 425 informative rows from the unchanged 439-row cohort; the temporal contrast uses 347 informative rows from the unchanged 358-row cohort. Both supports contain eight regions and 82 sites.

| Response and model | Estimate | CV3 with t(7), 95% interval |
|---|---:|---:|
| Original response, M_P | −1.0031 | [−1.6753, −0.3309] |
| Original response, M_SP | −0.9216 | [−1.5151, −0.3281] |
| Author R1,000 mean, M_P | −1.0233 | [−1.7072, −0.3395] |
| Author R1,000 mean, M_SP | −0.9411 | [−1.5418, −0.3404] |
| Original response, P0−P1 | −0.6877 | [−1.4703, +0.0949] |
| Author R1,000 mean, P0−P1 | −0.6933 | [−1.4763, +0.0898] |

The main polynya intervals remain below zero, but both temporal-contrast intervals include zero. The difference between winters is therefore sensitive to the uncertainty method and remains uncertain. CV3 does not guarantee exact coverage with eight heterogeneous clusters and does not correct exploratory selection, common calibration bias or correlation of errors across regions. The reproducible diagnostic stores all 48 leave-out fits, complete covariance matrices and information shares. Its 34 numerical checks confirm unchanged full/informative coefficients, agreement with archived original-response regional omissions, and agreement between direct scalar and matrix contrast calculations. The R1,000 response is assessed symmetrically with the original response.

### Table S3. Salinity and same-sample variance comparisons

| Quantity | Result | Sample and interpretation |
|---|---:|---|
| Joint-model salinity coefficient | +0.6462‰ per salinity unit | M_SP on the same 439 rows |
| Joint-model salinity CV3 interval | [−0.1960, +1.4884]‰ | 425 informative rows, 8 regions; t(7) |
| Joint-model salinity CR1 interval | [+0.1537, +1.1387]‰ | Same informative support; archived correction |
| Broader-panel salinity coefficient | +0.8341‰ per salinity unit | Separate 860-row panel; 88 sites, 13 regions |
| Salinity 13-region interval | [−0.0159, +1.6842]‰ | Includes zero; t(12) |
| Salinity 82-wet-cell interval | [+0.3886, +1.2797]‰ | Different clustering and normal-reference convention |
| Polynya–salinity adjusted correlation | −0.0804293 | Same 439; colony + region-by-season effects only |
| M0→M_S residual SSE reduction | 2.1429% | Same 439, original response |
| M0→M_P residual SSE reduction | 3.7939% | Same 439, original response |
| M0→M_SP residual SSE reduction | 5.2928% | Same 439, original response |
| M_S→M_SP residual SSE reduction | 3.2188% | Same 439; not out-of-sample gain |

The broader salinity coefficient is not a second coefficient estimated on the same 439 polynya panel, nor was it re-estimated in the author R1,000 sensitivity. Reduced correlation after fixed effects is not causal independence.

The numerical verifier checks the four source ZIP SHA256 digests and CRCs, exact matched temporal CSV bytes, unique keys, sample support, original and ensemble-response coefficients, covariance contrasts, SSE reductions and informative-region calculations. The machine-readable receipt contains 58 successful numerical/source checks and the source hash of the verifier itself. The comparison tolerance is explicit. This verification reproduces frozen derived results; it does not rerun the original laboratory calibration, retrieve new satellite scenes or test later ecological observations.

## S3. Calibration, time transfer and period heterogeneity

The author-method sensitivity used R pls::plsr, method oscorespls, scale = FALSE, fitting six components and predicting with five. It drew 1,000 stratified 65% training splits of the original 103 laboratory observations, using five isotope quantiles and seed 1. Median held-out laboratory RMSE was 1.729‰ for Landsat 4, 1.730‰ for Landsat 5 and 1.739‰ for Landsat 7, compared with 2.326‰ for a laboratory-mean reference. These errors describe laboratory calibration, not verified error of every remotely sensed colony-season.

The original and ensemble-mean 860 reconstructed responses correlated at 0.999880, with difference RMSE 0.05993‰. On the fixed439 panel, 1,000 calibration-specific slopes were all negative; their 2.5–97.5% ranges were [−1.2544, −0.8556]‰ for M_P and [−1.1629, −0.7843]‰ for M_SP. The temporal-contrast range was [−0.8747, −0.5291]‰. These are calibration-split sensitivities, not ecological confidence intervals or independent observations.

### Table S4. Frozen forward prediction and descriptive period refits

| Comparison | Support | Result |
|---|---|---|
| Training | 2004–2006; 132 rows, 79 sites, 10 regions | Source-fixed training interval |
| Testing | 2007–2010; 291 rows, 79 previously seen sites, 10 regions | 16 new-site rows excluded |
| Site-equal test RMSE, M0 / M_P | Same 291 | 1.83954 / 1.84893‰ |
| Site-equal test RMSE, M_S / M_SP | Same 291 | 1.80090 / 1.81221‰ |
| Paired MSE difference, M_P−M0 | Region-bootstrap, 2,000 draws |  +0.03466 [−0.13760, +0.22534]‰² |
| Paired MSE difference, M_SP−M_S | Region-bootstrap, 2,000 draws | +0.04084 [−0.17040, +0.29469]‰² |
| Early M_SP slope | 2004–2006; 132 rows | −1.6830 [−2.6152,−0.7508]‰/10pp |
| Late M_SP slope, all sites | 2007–2010; 307 rows, 85 sites | −0.3622 [−0.8784,+0.1540]‰/10pp |
| Late M_SP slope, known sites | 2007–2010; 291 rows, 79 sites | −0.5636 [−1.3459,+0.2186]‰/10pp |

Prediction models were refitted using site intercepts and numeric covariates, with region-by-season effects omitted from both training and prediction. No future intercept was inferred using the held-out response. These prediction scores were not rerun under the R1,000 response. The period refits are post-result descriptions with their archived nominal-region intervals, not a preregistered change-point test or proof of a significant difference between slopes.

## S4. Mechanistic checks and independent data compatibility

### Frozen site-mean versus within-site scale diagnostic (22 November 2026)

Before examining the new between-site coefficient, the same-source scale comparison and positive-inversion adoption criteria were frozen in `FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md`. The sample was the unchanged 439 optical colony-seasons at 85 source sites in 11 nominal reporting regions from 2004–2010. The original within-colony coefficient (−1.0031‰ per 10 percentage points, CV3 [−1.6753,−0.3309]) was already known. The new analysis used one equal-weight row per colony, averaging the Y proxy, June–October 100-km polynya fraction and measured summer and observation-date covariates over *actually observed* site-seasons. Three colonies had two observed winters, three had three, seven had four, 44 had five, 20 had six and eight had seven; no missing year was filled. A separate original colony-latitude variable and each site's mean observed year were added only to the pre-frozen primary between-site adjustment.

| Original optical response, between-site model | Colonies | Slope (‰ / 10 pp polynya fraction) | Eight-informative-region jackknife 95% interval, where estimated |
|---|---:|---:|---|
| Raw site means; equal weight per site | 85 | −0.3187 | Not a primary inferential model |
| Site means + reporting-region fixed effects | 85 | −0.7948 | Not a primary inferential model |
| **B1: region, original summer/timing covariates, mean observed year, latitude** | **85** | **−1.2947** | **[−4.9650, +2.3755]** |
| B1 using the same source R1,000 optical-calibration mean | 85 | −1.3102 | [−5.0147, +2.3942] |
| B1 restricted to at least three actually observed winters | 82 | −1.2556 | [−4.7063, +2.1951] |
| B2: region×season-centred observations before site averaging, same controls | 85 | −1.2629 | [−5.1964, +2.6706] |

B1's between-colony covariate support identified eight informative reporting regions after full adjustment. All region omissions were retained in the reproducible source-locked output. The adjusted between-site slope was negative under seven of eight omitted-region refits, but became approximately **+0.16‰** when Wilkes Land was removed. The directly pre-frozen positive inversion criteria therefore **failed**: the raw and adjusted between-site point estimates were not positive; B1's CV3 interval included zero and its region-omission sign was not stable. The other original-source calibration and calendar-support checks remained negative in point estimates, but were imprecise. This result is *not* a zero-effect demonstration and does not identify whether historical site-level prey composition differs from temporal responses. The between-site and site-FE within-site slopes condition on different site baselines. Neither is directly exchangeable with Reaves et al. (2025), who analyzed spatial/historical chick-bone material and a different polynya setting. We did not conduct an additional post-result search of favourable colony groups, season windows, spatial radii, isotope response variants or covariates.

The frozen pre-results specification, reproducible script and numerical verdict are in `FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md`, `test_between_within_source439_20261122.py` and `RESULT_BETWEEN_WITHIN_POLYNYA_NO_GO_20261122_JA.md`. Original-source fitting and leave-region outputs are fully reproduced by [GitHub Actions #45011139260](https://github.com/zuizui0223/mina/actions/runs/45011139260). These are historical same-source sensitivity tests, not independent biological studies.

### Event-level falsification: the February 2010 Mertz Glacier Tongue calving

An externally observed B-09B iceberg collision and Mertz Glacier Tongue calving on 12–13 February 2010 disrupted the George V coastal polynya system (Kusahara et al. 2011; Tamura et al. 2012). The event date, 100-km winter-exposure definition, geographical groups, and positive optical-response sign gate were fixed before viewing the isotope outcomes; however, the analysis reuses the previously selected 439 records. It is not independent ecological validation or a randomized study. The case comprises 10 colonies at 139–146°E, 65–70°S and 18 other complete-year East Antarctic colonies at 100–135 or 150–180°E, 65–73°S. Every site has genuine optical response and polynya fraction measurements for all five 2006–2010 winters (28 sites × 5 = 140 source records). Missing winters were not imputed. Each colony receives equal weight. The comparison subtracts each group's mean over 2006–2009 from its 2010 mean; the difference of those two changes is a descriptive difference-in-differences.

| Response (units) | Mertz-area sites: pre → 2010 | Distant controls: pre → 2010 | 2010 difference-in-differences |
|---|---|---|---:|
| June–October coastal polynya fraction | 10.285% → 4.161% | 9.797% → 9.224% | **−5.551 percentage points** |
| Summer original optical δ¹⁵N (‰) | 26.976 → 25.996 | 24.779 → 24.354 | **−0.555‰** |
| Same-source author R1,000 calibration mean δ¹⁵N (‰) | 26.941 → 25.966 | 24.722 → 24.292 | **−0.545‰** |
| November–February sea-ice concentration | 0.230 → 0.303 | 0.489 → 0.352 | **+0.211 fraction (~21.09 pp)** |
| November–February potential temperature (°C) | −1.060 → −1.060 | −1.066 → −0.692 | **−0.373°C** |

The observed physical contrast was more extreme than any of the four 2006–2009 physical placebo-year differences; by contrast, the 2010 optical δ¹⁵N deviation (−0.555‰) was *smaller* in absolute magnitude than placebo deviations in 2006 (−1.877‰) and 2007 (+1.693‰). For treated sites in Victoria Land (five) versus their same-reporting-region controls (nine), the winter polynya difference was −11.020 pp and the optical δ¹⁵N difference was **+0.494‰**. For treated sites in Wilkes Land (four) versus their controls (nine), the respective differences were −0.378 pp and **−1.390‰**. The tenth treated site, PGEO, lies in Adelie Land without a matched same-source-region control. Both fixed distant control longitude bands yielded negative pooled optical δ¹⁵N differences (−0.875‰ with western controls; −0.234‰ with eastern controls). Multiple geographically close colonies share ocean grid cells.

In the balanced 140-record panel, a site-and-season fixed-effect treated×2010 coefficient reproduced the unadjusted optical difference of −0.555‰. Adjustment for the original measured *summer* ice, temperature and observation-date variables produced +0.099‰, and additional summer salinity adjustment +0.023‰. These later-observed physical covariates might be pathways altered by the glacier event rather than pre-event causes; therefore, positive adjusted point estimates cannot be interpreted as polynya-specific causal effects. Between 2006–2009 and 2010, treated versus control observation support also shifted (−2.783 image days and −139.9 selected guano-positive pixels in differences-in-differences). Consequently, both ecological and optical observation changes remain possible.

The frozen sign gate required a negative physical shock alongside **positive** optical δ¹⁵N responses in both the original and author calibration, positive responses in each region-matched comparison, and a 2010 optical shift more extreme than all pre-event placebos. Only the physical conditions were met. **NO_GO_EVENT_BIOLOGICAL_RESPONSE**: this local shock did not validate the direction predicted by transporting the broad observational winter-polynya coefficient. **NO_GO_CAUSAL_MEDIATION** regardless of sign: the iceberg changed several ocean/ice processes at once, the controls are distant, the post-event period is a single winter and the 140 site-years do not represent independent randomizations.

Full source-linked 140 site×year data, 2006–2010 group-year and pre-placebo contrasts, the two fixed control bands and both summer-adjusted checks are regenerated by `test_mertz_iceberg_event_source439_20261122.py` using the pre-outcome source-ID freeze `FROZEN_MERTZ_2010_ICEBERG_EVENT_BIOLOGICAL_GATE_20261122_JA.md`. The numerical record is `RESULT_MERTZ_2010_ICEBERG_EVENT_NOGO_20261122_JA.md`, with [GitHub Actions #45012884027](https://github.com/zuizui0223/mina/actions/runs/45012884027). An iceberg event does not isolate polynya area alone or independently measure fish versus krill consumption.

The chlorophyll pathway check retained only 112 of 358 temporal rows, at 55 sites in 10 nominal regions; only four regions supplied identifying variation. Retained observations had mean summer sea-ice concentration 22.91%, versus 46.07% among excluded records, and winter polynya fraction 10.54%, versus 5.73%. The same 112-row polynya estimate was already +0.5604‰/10pp before adding chlorophyll. Consequently, comparing its coefficient to the full 358 negative estimate cannot identify attenuation or mediation. The fitted indirect product was −1.5414 with interval [−7.1178,+4.5235] in the archived pathway parameterisation. The pathway remains unestablished and is not promoted to a mechanism.

The separate BAS Signy stomach-content source provided 639 samples dated 2002–2020. One internally inconsistent food-weight sample was excluded; 638 samples remained across 19 observed breeding seasons. The winter exposure gate allowed 14 seasons: 2004/05–2010/11 and 2013/14–2019/20. Climate replication is therefore 14 seasonal values, not 638 independent environmental observations. The adjusted association with krill weight fraction was +0.421 percentage points per one-percentage-point polynya increase, with HAC-lag1 t interval [−1.568,+2.410]. The 25-km estimate was negative, and omission of the last season reversed the 100-km estimate. This is inconclusive dietary corroboration at one different location, not proof of no biological effect. The source DOI is 10.5285/eb421e6d-b93b-4174-904b-9a7b0b401403; colony-location support uses 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d.

The independent bulk/amino-acid feather dataset USAP-DC 602094 was obtained and checksum-verified: 108 feathers form 55 site-by-collection-year combinations. The six combinations overlapping 2004–2010 were all at least 30.5 km from the original 88 optical sites; none met a 25-km geographic match. Feather formation dates were also unresolved. This dataset therefore supplies no directly matched trophic-position replication of the historical 439-row association. An earlier retrieval failure in the project history is superseded by actual acquisition; the remaining obstacle is matching, not absence of access.

The 21-component optical-band decomposition uses the same calibrated response. For example, the ensemble M_SP coefficient is the sum of opposing sensor-band contributions; a negative blue-band contribution and a positive green-band contribution do not chemically identify prey or nitrogen-cycle processes. Such algebraic attribution is useful for measurement scrutiny but cannot establish an ecological pathway.

## S5. Why the later-period extension stopped

A source-matched guano classifier was trained on publicly supported historical pixel-centre labels and evaluated without threshold retuning. On 2008–2012 observations at 45 sites in 8 regions, known-positive recovery was 64.8279%, with region-bootstrap interval 58.3349–74.6497%, below the 80% requirement. Accounting for images shared across regions yielded six blocks and interval 60.7051–77.4413%, also below the threshold. Candidate-background exclusion was 99.0282%; those selected candidate backgrounds are not a representative set of field-verified negative pixels.

The recovery metric gives image and site units their specified weights and is not a simple overall pixel-accuracy score. The historical source positive labels are themselves classification outputs; they do not establish field purity. The 2013–2021 ecological δ¹⁵N–polynya analysis was therefore not run. No later-period validation, replication or null effect is claimed.

## S6. Nest-weighted climate exposure retained as supplementary context

The earlier climate-exposure manuscript is retained as a historical source record, not a competing current manuscript. On the same 271 recently counted colony locations, selected three-model CMIP6 high-emissions late-century sea-ice changes were −28.6341 percentage points under equal-site weighting and −13.2762 under fixed observed-nest-median weighting. Their +15.3579-point difference decomposed into +15.6560 between source reporting regions and −0.2981 within regions. These are physical-exposure accounting identities for a documented census footprint, not evidence of dispersal, adaptation or demographic buffering. They are not linked to the polynya regression by a common causal model.

The future outputs do not provide a validated projection of the DEEP-AA coastal-polynya measure. Neither future diet nor future penguin abundance is calculated by extrapolating the isotope coefficients. The broader source atlas, historical census comparisons and their four-figure v0.6 presentation remain available in the repository as provenance. They are excluded from the five main figures of this polynya manuscript.

## S7. Research history and limits of the review package

The pre-result direct-polynya protocol specified a positive direction after previous environmental exploration; that directional hypothesis was not supported. The later focus on the negative association, the temporal comparison and this manuscript structure are retrospective. Publicly committed protocols document timing within this project but are not represented as an independent confirmatory preregistration. No radius, outcome, lag, classifier threshold or favourable subset was newly searched during the manuscript restructuring.

The offline package includes source-derived inputs, fixed numerical outputs, manuscript source, plotting and verification scripts, and checksums. It reproduces the frozen 439/358 analyses, the separately dated CV3 uncertainty diagnostic and all five figures. Large original satellite/calibration archives are linked by DOI and identity rather than silently replaced by simulated data. The source-reuse register records the two principal Zenodo datasets' CC BY 4.0 licences, Copernicus credit and product DOI, and the unresolved historical NSIDC v4 redistribution label. Publication of a final DOI, a licence decision for project-created code, human scientific review and author declarations remain outstanding.

## S8. Ecological scale and contemporary conservation geography (author-review addition, 23 November 2026)

This section is an **interpretive appendix only**. It is not an independent trophic measurement, a new polynya–diet model, an intervention or evidence of conservation benefits. All existing 439 source-matched colony-seasons, 85 sites, five main figures and original statistical estimates are unchanged.

### S8.1. Interpreting the optical δ¹⁵N scale using a deliberately simplified two-prey contrast

The original adjusted within-colony estimate was −1.0031‰ per ten percentage points (pp) of winter coastal-polynya area fraction (M_P; source-informative eight-region CV3 interval [−1.6753, −0.3309]‰). The exposure remaining after colony, region-by-season and summer covariate adjustment has SD **1.6011 pp**, so the same slope corresponds to **−0.1606‰ per one residual-exposure SD**. A +10-pp change is about 6.25 such SDs, and should not be described as typical year-to-year environmental variation.

For a heuristic unit comparison only, Hong et al. (2021, Table 1, doi:10.3390/ani11092681) report prey δ¹⁵N (‰): Antarctic krill *Euphausia superba* 3.65 ± 0.58; ice krill *E. crystallorophias* 6.12 ± 0.51; Antarctic silverfish *Pleuragramma antarctica* 10.30 ± 0.80. In a two-prey model with a constant nitrogen enrichment offset, the difference obeys Δδ¹⁵N = (δ¹⁵N of fish − δ¹⁵N of krill) × Δfish fraction. Accordingly, Δfish fraction = Δδ¹⁵N divided by (δ¹⁵N of fish − δ¹⁵N of krill). These values concern **whole-prey measurements in the Ross Sea** (krill sampled in 2019 and silverfish source records from 2002–03), not contemporaneous source values for the pan-Antarctic 2004–2010 optical guano records.

**Table S5. Hypothetical isotope-equivalent changes in the fish-derived contribution to assimilated dietary nitrogen (not measured fish mass, prey biomass or diet proportions).**

| Illustrative prey endmembers (fish − krill) | δ¹⁵N separation (‰) | M_P: +10-pp exposure, fish-N equivalent | M_P: +1.6011-pp SD, fish-N equivalent | M_SP: +1.5879-pp SD, fish-N equivalent |
|---|---:|---:|---:|---:|
| Antarctic silverfish − Antarctic krill | 6.65 | −15.1 percentage points | −2.4 percentage points | −2.2 percentage points |
| Antarctic silverfish − ice krill | 4.18 | −24.0 percentage points | −3.8 percentage points | −3.5 percentage points |

The salinity-adjusted M_SP slope is −0.9216‰ per +10 pp. Here, the mixing weight is **the fraction of assimilated dietary nitrogen contributed by fish**, not the percentage of fish in the stomach, diet by wet/dry mass, or prey biomass. Deriving a dietary mass fraction additionally requires nitrogen concentrations and assimilation efficiencies for each prey (Phillips and Koch 2002). Translating these *contrasts* is not a fitted diet-mixture posterior: prey endmembers can vary geographically and through time; prey nitrogen baselines, taxon-specific routing, guano–prey enrichment, macronutrient mixing, and the underlying reflectance-based isotope calibration can change. A constant enrichment factor cancels algebraically in a within-sample **difference**, but this does not establish that enrichment or prey baselines were constant across colony-seasons. Without matched prey isotopes or direct diet observations, even the **sign** of a fish-fraction change remains unidentified.

### S8.2. Exact source-cohort recovery and limits of geographic representation

The original Youngflesh RDS and source-author `Scripts/4-diet-est.R` pixel-support rule were independently reproduced: 179,346 qualified pixels at 119 source sites across all years. In 2004–2010 this yields 583 observed site-seasons at 113 original source sites. The frozen optical-isotope-plus-summer-marine source panel retains **439 site-seasons at 85 sites**, with *every available season at each retained site* preserved: the **144 excluded site-seasons are precisely the complete histories of 28 entirely omitted sites**. Those 28 sites are **all absent** from the pinned 88-site `colony_geography.csv` catalogue, while the 85 retained sites are present. The geographic catalogue has three other sites without qualifying original-source seasons in 2004–2010. This identifies a **site-inventory/coverage selection gate**. To locate its stages without examining the optical isotope response, we independently reproduced the original `extract_matched_novfeb_glorys.py` crosswalk on the archived Youngflesh 146-site projected centroids, the MAPPPD 595-site coordinates and the original 1997 marine-source inventory. The original gate accepts 102/146 sites when the nearest MAPPPD identifier matches at 2 km or less and the second-closest MAPPPD location lies beyond 2 km. Of those, 100 have a matching site in the frozen 1997 marine inventory, and 99 have at least one observed Landsat season during the pre-existing 1993–2013 source window (892 matched site-seasons). Exactly 85 of the original author-supported 113 sites observed during 2004–2010 pass this entire crosswalk. 

**Table S6. First failed data-linkage criterion among 28 original image-supported sites missing from the frozen 85-site cohort.** This is sequential bookkeeping of site matching, not biological absence or a decomposition of independent causes.

| First failed source-matching criterion | Excluded sites | Excluded observed colony-seasons (2004–2010) |
|---|---:|---:|
| Another MAPPPD site lies within 2 km (nonunique match) | 12 | 58 |
| The nearest MAPPPD identifier differs from the original image site ID | 8 | 42 |
| Nearest matching-ID site lies more than 2 km away | 6 | 33 |
| Site absent from frozen 1997 marine-source inventory | 2 | 11 |
| **Total** | **28** | **144** |

The excluded observations were spatially uneven: 36/73 source-colony seasons in Mac. Robertson Land, 28/70 in Princess Elizabeth Land and 38/136 in Victoria Land were excluded. Both original source sites in Central-west Antarctic Peninsula (8/8 colony-seasons) were absent from the final cohort. This does not invalidate the conditional model for its selected observations but limits extrapolation of the 439-site-season association to all Adélie colonies or regions. A first-failed condition is not necessarily the only issue at a site: identity conflicts, distances and marine-source coverage can overlap. Missing a frozen 1997 marine site is a source-roster condition, not proof that water was absent at that location.

The original frozen `matched_isotope860.csv` and `polynya_physical860.csv` join on unique `site_id,season` keys; selecting records with complete 100-km winter coastal-polynya exposure reproduces exactly 439/85/11, including 34 measured zeros, mean 7.0304% and SD 6.3187 pp. There is **no additional loss of eligible site-seasons at this winter-polynya gate**. The previously prepared 472/88 source-pool map is not interchangeable with this frozen site cohort. No missing year is treated as a measured zero.

A separate **source-only, outcome-unseen representativeness audit** compared all 583 author-supported site-seasons using the same independently re-extracted (approximate pixel-area) DEEP-AA exposure definition. Across the 439 site-seasons retained in the original analysis, mean winter-polynya fraction was **7.075%**, compared with **5.949%** across the 144 excluded source site-seasons, a descriptive difference of **1.127 percentage points**. The corresponding equal-weight average of site means was **7.054%** across 85 retained sites versus **5.830%** across 28 excluded sites. All **34 zero-exposure site-seasons** were in the retained group; none were observed among the 144 excluded records. This comparison uses the *same approximate source re-extraction* for both selected and excluded sites; these values are not substituted for the frozen original 439-row exposure file (mean 7.030%). The groups differ geographically and no coefficient direction, selection mechanism, or ecological effect follows from this descriptive contrast. The comparison was not used to change inclusion criteria, model covariates or the reported association.

### S8.3. Descriptive juxtaposition with present-day CCAMLR marine protected areas

For the 85 original frozen sites, annual 2004–2010 June–October polynya area fractions (100-km exposure definition) were summarized separately by site. Only **79 sites observed in at least four winters** were assigned a descriptive standard deviation; **six sites with two or three observed winters** remain visible but unranked. The median within-site SD among the 79 is **2.825 pp**. No colony-specific isotope response sensitivity is estimated by this dispersion measure.

The official CCAMLR designated MPA boundaries (source: `https://github.com/ccamlr/data/blob/main/geographical_data/mpa/CCAMLR_MPA.json`, EPSG:6932, six spatial subzones: five Ross Sea and one South Orkney southern shelf) were intersected with a **geodesic 100-km circle** around each original colony coordinate. **15 of 85** circles intersect current designated MPA boundaries, all within **Victoria Land / Ross Sea**; **13** of the 15 have ≥4 winters and therefore a colour-coded SD. Circles for the remaining 70 original colonies do not intersect these polygons. These circle intersections represent *potential proximity to a legally mapped marine area*, **not** actual documented foraging routes, the ocean-only denominator used for polynya exposure, area of protected prey habitat, or the fraction of any individual's feeding inside an MPA. A circle–polygon intersection may include non-ocean portions; polygon status is a current spatial descriptor.

The Ross Sea MPA was adopted by CCAMLR in 2016 and entered into force in **2017**, after the study's 2004–2010 winters; the South Orkney Islands southern-shelf MPA dates to 2009 and does not intersect any of these source-site 100-km discs. Therefore, no pre/post-policy effect, MPA-induced stability or conservation effectiveness can be inferred. The spatial clustering of these intersections in Victoria Land also precludes interpreting differences in winter polynya variability inside and outside current MPAs as a protected-area effect.

**Reproducibility and version boundary.** The source-locked cohort and CCAMLR geospatial intersections, 583→439 site-key crosswalk, region counts and Figure S1 preview are archived with GitHub Actions [frozen 439/85 audit](https://github.com/zuizui0223/mina/actions/runs/45082480478) and [28-site catalogue audit](https://github.com/zuizui0223/mina/actions/runs/45083270769). Analysis and frozen input hashes are documented in `analysis/adelie-polynya-conservation-source-20261122` (research-only branch). This is a **23 November 2026 post-result descriptive addition for author review**, not an additional hypothesis test or part of the independent pre-outcome sign gate.

## Literature cited

Phillips DL, Koch PL (2002) Incorporating concentration dependence in stable isotope mixing models. Oecologia 130:114–125. https://doi.org/10.1007/s004420100786

Hong S-Y, Gal J-K, Lee B-Y, Son W-J, Jung J-W, La H-S, Shin K-H, Kim J-H, Ha S-Y (2021) Regional differences in the diets of Adélie and Emperor penguins in the Ross Sea, Antarctica. Animals 11:2681. https://doi.org/10.3390/ani11092681

CCAMLR (2016; maintained current geography) Ross Sea region marine protected area, Conservation Measure 91-05, and marine protected area spatial GIS. https://cm.ccamlr.org/ ; https://github.com/ccamlr/data/tree/main/geographical_data/mpa

Lin Y, Nakayama Y, Liang K, Huang Y, Chen D, Yang Q (2024) A dataset of the daily edge of each polynya in the Antarctic. Scientific Data 11:1006. https://doi.org/10.1038/s41597-024-03848-2

MacKinnon JG, Nielsen MØ, Webb MD (2023) Fast and reliable jackknife and bootstrap methods for cluster-robust inference. Journal of Applied Econometrics 38:671–694. https://doi.org/10.1002/jae.2969

Kusahara K, Hasumi H, Williams GD (2011) Impact of the Mertz Glacier Tongue calving on dense water formation and export. Nature Communications 2:159. https://doi.org/10.1038/ncomms1156

Tamura T, Williams GD, Fraser AD, Ohshima KI (2012) Potential regime shift in decreased sea ice production after the Mertz Glacier calving. Nature Communications 3:826. https://doi.org/10.1038/ncomms1820

Youngflesh C, Che-Castaldo C, Schwaller MR, Polito MJ, Serbin SP, Lynch HJ (2026) Space-based monitoring of penguin diet links sea ice, food webs, and population change. Current Biology 36:3707–3714.e5. https://doi.org/10.1016/j.cub.2026.06.028

## Supplementary figure

**Figure S1.** Historical winter coastal-polynya exposure variability at the 85 *Adélie* colony sites in the frozen 439-season optical isotope-proxy panel, alongside *currently designated* CCAMLR MPAs. Point colour encodes within-site SD of winter June–October coastal-polynya fraction (percentage points) from 2004–2010 at 79 colonies with at least four observed winters. Grey crosses denote six colonies with fewer than four available winters, for which no SD category was assigned. Dark outlines denote six currently designated MPA subzones. The 100-km circle around 15 colonies intersects current mapped MPA boundaries; all are located in the Ross Sea region. This retrospective, descriptive geographic overlap must not be interpreted as penguin diet sensitivity, observed foraging inside protection, or any causal protection effect.
