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

## Literature cited

Lin Y, Nakayama Y, Liang K, Huang Y, Chen D, Yang Q (2024) A dataset of the daily edge of each polynya in the Antarctic. Scientific Data 11:1006. https://doi.org/10.1038/s41597-024-03848-2

MacKinnon JG, Nielsen MØ, Webb MD (2023) Fast and reliable jackknife and bootstrap methods for cluster-robust inference. Journal of Applied Econometrics 38:671–694. https://doi.org/10.1002/jae.2969

Youngflesh C, Che-Castaldo C, Schwaller MR, Polito MJ, Serbin SP, Lynch HJ (2026) Space-based monitoring of penguin diet links sea ice, food webs, and population change. Current Biology 36:3707–3714.e5. https://doi.org/10.1016/j.cub.2026.06.028
