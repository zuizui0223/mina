# Locked long-term climatic-legacy test v2 — slope outcome, not annual fluctuations

**Freeze timestamp:** 2026-11-08 JST; created after the annual-lag experiment in PR #207 and after the historical whole-period spatial r=+0.622 had been observed. **This is an exploratory, outcome-aware additional analysis; it is not an independent preregistration and not a second confirmatory test of the same hypothesis.** New 2001–2020 site-specific slope × 1979–1990 SIC fits and scores must not be read before this design is committed.

## Why one more test is justified

Previous annual log(nests) changes and five-year bins did not exceed simple no-change baselines, including an 11–20-year antecedent-SIC lag. Those responses are not equivalent to the decadal *site trend* in the hypothesis "breeding distributions reflect past climate". This contract tests **a different response grain**, with exact windows and models frozen *once*; it is not a post-result search for preferred lag length.

## Source records and independent outcome-support audit

- Original site×species×year source CSV: `research/climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv`, Git blob `fc134e364cf38699fa7611d7dee5fbbbcb370c0a`.
- Site-method cohort: `research/climate-penguin/outputs/warming_species_breeding_v1/historical_species_site_trends.csv`, Git blob `2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b`. Filter species ADPE and the **39 specific original site IDs**; require exact same original site-specific method, unambiguous n_methods=1, valid source record (n_counts>0), and 2001≤season≤2020. No changing count method within a site, no filling unobserved years, no treating a missing count as zero.
- Primary annual count response uses source count (including genuine recorded zero), `log1p(count)`. For each site, OLS slope of log1p(count) on actual calendar year, multiplied by 10 for **log1p count trend per decade**. Minimum **4 distinct census seasons spanning at least 10 calendar years**.
- Data-support-only gate (the outcome values were not inspected): 39 historical site-method series → **26 supported sites**, 257 site-year counts, four regions: Victoria Land 17; South Shetland Islands 3; Central-west Antarctic Peninsula 5; Adélie Land 1. Exactly one site in Adélie Land and no Mac. Robertson Land site meet the threshold.
- Neither 39 nor 26 are independent ice-grid replicates, and the outcome is a *within-site trend* while the regressors are *between-site climatologies*. This cannot establish time-lagged demographics, recruitment or philopatry.

## Predetermined sea-ice windows, same target and geography

Product is official EUMETSAT OSI SAF **OSI-450-a1 v3.1**, the same original 0–100 km nearshore extraction geometry and 40 original macro site coordinates; source blobs:
- `research/climate-penguin/outputs/sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv` `5a211a0eaa63b6a5d3516353dd9431428618dbd3`.
- Existing source-complete Aug–Nov 1991–2020 daily-derived monthly table `research/climate-penguin/outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv`, blob `4fcea71c2d8b1069b6ad143f6522061ed434daf5`.
- Historical 1979–1990 source monthly fields are downloaded under `research/climate-penguin/climatic_legacy/extract_legacy_monthly.py`, with the previously successful 120 site×month monthly-to-daily quality bridge and all individual source SHA256 recorded.

For each site first compute 8–11 monthly SIC season mean weighted by month days. The *across-year* mean weights calendar years equally. All 4 months in each year and all years in each window must be supported; missing is NA, never zero.

- **H_79_90:** 1979–1990 mean SIC (12 annual values), historical.
- **C_01_20:** 2001–2020 mean SIC (20 annual values), contemporaneous with slope outcome.
- **C_09_20:** 2009–2020 mean SIC (12 values), prespecified *equal-duration* sensitivity; no replacement of the primary 2001–2020 contrast.
- **Delta_C_minus_H:** C_01_20 – H_79_90, an ancillary change metric, not a searched alternative lag.

No month, nearshore buffer, decade, start/end year, trend horizon, source eligibility, or nonlinear functional form may be selected after opening the response/climate comparisons.

## Frozen predictive models, training/testing

A **site-out spatial** comparison, not a validation of future climate-to-growth temporal transfer:
- Mzero: assume no site trend (slope=0).
- Mglobal: training sites' mean trend.
- Mregion: intercept + ridge-shrunk one-hot region offsets (penalty λ=4 per region, intercept unpenalized).
- Mrecent: Mregion + one globally train-standardized C_01_20, ridge λ=8.
- Mhistory: Mregion + one globally train-standardized H_79_90, same penalty λ=8.
- Mboth: Mregion + globally train-standardized C_01_20 and H_79_90, same λ=8 each.
- Mequalwindow (secondary): Mregion + train-standardized C_09_20, same λ=8.
- Mdelta (secondary): Mregion + train-standardized Delta_C_minus_H, same λ=8.
All predictors standardize on the training sites only. All models use identical site test folds. Always include all four predefined region columns (site metadata), with ridge shrinkage to zero when an entire region is unseen in training. No penalty tuning or spatial grid interpolation by test outcome.

**LOSO (leave-one-site-out) is the PRIMARY prediction validation:** 26 site folds. Compare **site-equal MAE**, primary paired Δ = MAE(Mrecent) − MAE(Mhistory) (positive favors history); report RMSE and all baselines. Keep exact site, region, n_years, count span, count slope, all sea-ice means, each fitted out-of-site prediction and residual in the archived artifact.
**LORO (leave-one-region-out)** is a prespecified conservative transport check (four folds, one singleton region), with held-out-region intercept returning to the estimated global mean. No formal significance attached to four independent folds.
**Descriptive correlations**: historical versus recent SIC raw Pearson r and after removing region offsets; correlation of site slope versus each SIC (raw and region-residualized), plus leave-one-region influence. Such correlation does not replace LOSO prediction.
**Clustering & uncertainties:** 2,000 resamples of four geographic regions with replacement (seed 20261108), each site appearing when its region is drawn; report paired MAE difference interval *as a dependence sensitivity, not independent spatial-unit CI*. Equal-region weighting and Victoria Land removal are mandatory. If within-region residual H/C correlation |r|≥0.95, distinct time windows are deemed **non-identifiable** regardless of apparent score difference.

## Prespecified verdict

- **Stronger historical-predictive association (bounded, exploratory)** only if Mhistory LOSO MAE is smaller than Mrecent, Mregion, Mglobal and Mzero; sign persists for C_09_20 instead of C_01_20, under Victoria Land removal, and every leave-one-region-out test with ≥2 sites; 2,000-region-resampling Δ interval wholly positive; the region-adjusted historical/current SIC correlation magnitude is below 0.95. Even then, do not conclude a long demographic delay or dispersal constraint.
- **Weak or inconclusive** if the historical model beats recent only on one score, one region, unequal windows, or if historical/current climate is too collinear to distinguish the eras, or uncertainty crosses zero.
- **Not supported** if adequate data exist and Mhistory does not improve on Mrecent, with benchmark comparisons reported.
- **Not testable** if source consistency or the pre-fixed quality gate (≥25 sites and ≥3 regions, ≥3 sites in each of at least 3 regions) fails. Because Adélie Land has one site, treat LORO for it as highly unstable rather than suppressing it.

**Important:** The original 39-site whole-1991–2020 r=+0.622 is not the result of this test. Its response/count years and SIC years differ; it must not be presented as a replication. The present spatial cross-validation cannot tell us whether individual penguins dispersed, died, skipped breeding or recruited, nor does it test movement; "climate debt" requires an independently defined equilibrium distribution and lag of actual redistribution. Future CMIP6 breeding numbers remain NO-GO without temporal transfer.
