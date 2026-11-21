# Actual co-census × marine PCA geographic selection / period sensitivity, 2026-11-11

This is a **post-result diagnostic**, not new confirmatory species-level hypothesis or P-value fishing. Earlier source-verified 34-site/6-region/2011–2020 dataset yielded an apparent ADPE-to-GEPE within-colony observed nest-ratio correlation with marine PC1 of +0.523, but expanded source-verified 588-site/18-region/1993–2020 dataset yielded −0.008. Both the **physical PCA calibration**, **site cohort** and **year window** changed; attributing all variation to one dimension would be an error.

Fixed actual original archive: GitHub Actions #42959103493 complete 588 site×28yr marine joint physical site-years, exact true two-species co-census source site×year rows, all from original 595-site source atlas, plus original 40-site ocean geolocation support. The source old34 2011–2020 PCA explanation 0.7094310203120341 and old ADPE/GEPE within-site correlation +0.5231858620924323 are original benchmark checks.

Compute PCA transforms without looking at species counts:
1. Physical reference A: re-fit original 34 true coastal sites, 2011–2020 3-variable pooled SIC / GLORYS salinity / GLORYS thetao PCA, warm-oriented first loading.
2. Physical reference B: pooled equal-region-year (18 original reporting regions × 1993–2020 annual means), warm-oriented PC1.
3. Hold either reference's loadings/means/scales fixed, project the original real marine physical site-years. No re-fitting based on the ecological endpoint or choosing better climate axis.
4. Compare exactly (a) old34 site IDs, real 2011–2020 two-species same-site same-year count pairs; (b) all newly eligible 588 source site IDs, real 2011–2020 pairs; (c) all original 588 site IDs, real 1993–2020 pairs. Within-site demeaned and raw Pearson r reported ONLY as exploratory ecological association with actual observed two-species count ratios. Provide number sites, years, regions, 250km blocks for each.
5. Reproduce old baseline 34 ADPE/GEPE (r raw −0.50795008628; within +0.52318586209) and 588 1993–2020 full18 PC1 (r raw −0.10135101338; within −0.00836584141) exactly, else fail before biological interpretation.
6. Do not create any spurious species absence, "new" climate debt, greening time series, climatic niche preference, p-values, or future population projections. The 34-site PCA applied to continental sites may be environmentally out-of-domain, and even all-588 co-census are uneven geographically.

Output a fixed 2 PCA fit × 3 geography/period cohort table of genuine ADPE/GEPE, CHPE/GEPE and ADPE/CHPE observables. Interpret fragility of small-cohort species–physical-axis link, not a causal source mechanism.
