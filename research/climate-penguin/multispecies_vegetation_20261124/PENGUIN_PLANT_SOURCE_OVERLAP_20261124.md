# Current mapped terrestrial vegetation near observed breeding-nest changes (2026-11-24)

Executed locally, original Plantarctica ZIP DOI 10.6084/m9.figshare.24745956 SHA256 7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236 (87,391 features, 2017–2023 composite). Fixed source panel from CROSS_SPECIES_SOURCE_OFFSET_RESULT_20261124.json blob 141cb5a18b2a59dff2dd12bc3ccec0e8a5401a76 (30 site-species rows, 21 sites, 1991–2000 vs 2011–2020 medians), archived census coordinates blob fc134e364cf38699fa7611d7dee5fbbbcb370c0a. Compact copied source roster verified length 1352 bytes and FNV1a 58e1594a, local text SHA256 70a26a46164dc6c4ca7782c5ac920ec0d63e03f17d66eca4215e7b8dac3bc9b9. No unobserved species zero-filled. No restricted AADC data used.

Primary 1 km geodesic disks, 360 vertices, EPSG:6932 equal-area. Union mapped vegetation and lichen, snow algae separate. Partition overlapping disks into disjoint zones and classify by sum of observed nest changes across covering sites. No land-area denominator, no validated deposition footprint. Equal-nest weights primary, GEPE 0.5/2 as illustrative sensitivity only. No vegetation change, marine subsidy amount, or causal effect estimated.

| Region | sites | observed nest net change | mapped vegetation+lichen union ha | mapped area near net decline ha | decline-side % |
|---|---:|---:|---:|---:|---:|
| South Shetland |10|-11507|176.5090|84.1190|47.657088|
| Central-west Antarctic Peninsula |11|6118|15.6046|0.4376|2.804366|
| Combined |21|-5389|192.1136|84.5567|44.013878|

Equal weights 0.5km 43.137425%, 2km 57.061748%. At 1km GEPE weight 0.5/1/2 gives 53.654268/44.013878/44.013878%. Leave-one-site-out 34.318256–71.510203%, not confidence interval. At 1km equal weights separate classes vegetation 43.364713% and lichen 46.397402%. Absolute decline-side fraction is driven by observation roster and mapped-area distribution; regional contrasts descriptive. No proof of botanical absence where map unmarked.

## Post-result magnitude and coverage audit
At >=25% decline in observed weighted sum, 58.494953 ha (30.448101% of mapped union) at 1km, all three tested species weights yield same area; 10 and 50% thresholds happen to give same equal-weight result. At 1km, 14 sites have only one observed species, 5 two species, 2 three species. Restricting to >=2 observed species leaves 7 sites: equal-weight decline-side 6.478779% of 105.4434 ha, only SHIR. Restricting to three observed species leaves 2 sites, both increase under equal weight (GEPE weight 0.5: one declines). These subsets change geographic denominator; the full 44% cannot be called a whole-community decline rate. Even paired decadal medians are not necessarily same-year counts.

## Stricter three-species observation grain
Reopened strict_original_pair_1993_2020_matched_siteyears.csv (blob 7e86b2eb5f5a4e012f128101ebec02d51cbfe41c on PR214 branch), reconstructed 34 common site-years at 3 sites from all paired rows; duplicate species count identities checked, original archived coordinates exact. Same site/calendar year/shared citation and counting method, not necessarily same census day or effort. Each site's first and last common years used, not identical time windows. Geodesic disks of these three sites do not overlap.

| Site | years | first→last three-species sum | change % | mapped vegetation+lichen within 1 km ha |
|---|---|---|---:|---:|
| ARDL |1993–2018|4927→6783|+37.669982|73.869444|
| LION |1994–2018|9771→7304|-25.248183|8.562753|
| PCHA |2000–2019|1230→1571|+27.723577|0.344955|

LION declines under GEPE weights 0.5, 1, 2 (-35.98%, -25.25%, -10.63%); other two increase. At equal weights LION accounts for 10.344344% of the 82.777152 ha mapped union in this three-site panel (0.5km 8.127322%, 2km 8.278308%). Not comparable denominator to 21 sites, and only one declining site, two regions; no population inference or independent replication. This is a priority site for local matched field/guano source and repeated vegetation records, not evidence for declining vegetation.

## Reproducibility
Local archive penguin_plant_source_overlap_20261124.zip SHA256 5e83e446919188322f78a91b50b09cd4b376133aa202cd46c812e89fd57fd077 contains executed scripts, source roster and source-derived endpoint CSV, area tables, all weight/radius/threshold/roster sensitivities and README. Exact area conservation checked against disjoint atomic-zone sum and independent loss/gain/both/neither partition. No publisher archives redistributed. Only this interpretation record committed publicly; local code package remains attached in conversation. No merge, no main or frozen manuscript changes. Stop extrapolating across partially observed species; next test matched source-specific nutrient/exposure data or repeated vegetation field measurements rather than more arbitrary buffer tuning.
