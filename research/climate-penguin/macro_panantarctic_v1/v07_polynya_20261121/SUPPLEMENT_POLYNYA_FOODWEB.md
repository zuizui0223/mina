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

### Table S1. Frozen estimates and informative-region uncertainty

All entries are in ‰ per 10-percentage-point increase in winter polynya fraction. The P0−P1 contrast uses the full covariance of the simultaneous coefficients. The original 11-region intervals remain archived; the manuscript emphasises the informative-eight-region intervals. The 425-row main sensitivities are new support audits dated 21 November 2026. The 347-row temporal sensitivities were already present in the frozen temporal analyses.

| Response and model | Estimate | Nominal 11-region 95% interval | Informative 8-region 95% interval |
|---|---:|---:|---:|
| Original response, M_P | −1.0031 | [−1.4668, −0.5395] | [−1.5047, −0.5015] |
| Original response, M_SP | −0.9216 | [−1.3493, −0.4939] | [−1.3843, −0.4589] |
| Author R1,000 mean, M_P | −1.0233 | [−1.4982, −0.5485] | [−1.5371, −0.5096] |
| Author R1,000 mean, M_SP | −0.9411 | [−1.3789, −0.5033] | [−1.4148, −0.4675] |
| Original response, P0−P1 | −0.6877 | [−1.2962, −0.0792] | [−1.3461, −0.0293] |
| Author R1,000 mean, P0−P1 | −0.6933 | [−1.3093, −0.0773] | [−1.3598, −0.0267] |

In the 358-row original simultaneous model, P0 is −1.3790 [−2.2705, −0.4876] and P1 is −0.6913 [−1.4393, +0.0566] under the archived nominal-11-region intervals. Separate P0-only and P1-only regressions are not the basis for the temporal contrast. The raw P0–P1 correlation is +0.796; after the full adjustment it is −0.390. Their adjusted standard deviations are approximately 1.238 and 1.336 percentage points. Reporting per 10 percentage points therefore scales a local conditional slope; it does not demonstrate a typical within-colony change of that magnitude.

### Table S2. Salinity and same-sample variance comparisons

| Quantity | Result | Sample and interpretation |
|---|---:|---|
| Salinity coefficient | +0.8341‰ per salinity unit | Separate 860-row panel; 88 sites, 13 regions |
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

### Table S3. Frozen forward prediction and descriptive period refits

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

The offline package includes source-derived inputs, fixed numerical outputs, manuscript source, plotting and verification scripts, and checksums. It reproduces the frozen 439/358 analyses and all five figures. Large original satellite/calibration archives are linked by DOI and identity rather than silently replaced by simulated data. Publishing a final DOI, resolving any redistribution conditions, confirming author contributions and completing the target journal's current administrative requirements remain author-level publication steps.
