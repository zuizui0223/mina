# A冬季表層塩分 vs B成層：同一693元site×seasonでの探索的生態関連のモデル比較契約

**2026-11-19 JST | mina PR #214 exploratory only | 結果を閲覧・計算する前にコミット。** The starting observation (full-860 salinity+optical δ15N beta 0.834, region sign heterogeneity) is already known. This contract cannot turn further reanalysis into independent confirmatory evidence.

## Data, same-support cohort

1. Same original [Youngflesh et al. 2026](https://doi.org/10.1016/j.cub.2026.06.028)-derived original 860 Adelie optical δ15N site×season source, artifact **14328755565**, original derived ZIP SHA256 `dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`.
2. Fixed independently extracted source-only [GLORYS winter salt + TEOS-10 density physical gate](MECHANISM_AB_PHYSICAL_SOURCE_RESULT_20261119_JA.md), Actions **44539876656**, artifact **14537926313**, GitHub Actions artifact digest **sha256:a300e588c85256c060ffffa14717378fc9198a75a0ef583669e6e94e2236255f**. Original 82 grid cells ×15 seasons source-derived; join only on **exact site_id+season**, never nearest-neighbor rematch.
3. The denominator is **all source site×season with all original Nov–Feb surface salt, June–Oct winter surface salt, and Nov–Feb 0m/47.37m density difference** (expected **693/860** in physical-only source). No outcome-based row selection, no imputation of 167 depth-missing site-seasons; report actual source sites, native wetcells, reporting regions and train/heldout split.
4. Original [time split](FROZEN_TEMPORAL_TRANSFER_AND_TWO_AXIS_TEST_20261118_JA.md): train seasons <=2004, heldout seasons >=2005 and <=2012, *only* original sites observed in training. Don't use target-year region×season FE in prediction. Keep 2004 cutoff regardless of result.

## Predictor definitions

- Base controls always unchanged: source image mean DOY centered, DOY²; original Nov–Feb NSIDC 150km SIC; original Nov–Feb GLORYS near-surface temperature; original site effect; region×breeding-season fixed effects **for in-sample conditional association only**.
- **S**: Nov–Feb GLORYS `so` at near-surface (existing M1).
- **A**: preceding June–October GLORYS near-surface `so` same source grid and season-start year (candidate winter polynya/brine proxy **not** direct polynya).
- **B**: Nov–Feb `sigma0(47.37m)-sigma0(0.494m)` (TEOS-10 stratification **not** a direct meltwater fraction).
- Separate one-extra-df candidates from the *same* M0 on **identical 693 rows**: `M0`, `M_S=M0+S`, `M_A=M0+A`, `M_B=M0+B`. Descriptive joint conditions `M_SA=M0+S+A`, `M_SB=M0+S+B`, `M_AB=M0+A+B`, `M_SAB=M0+S+A+B`; no nonlinear exploration/tuned lags/thresholds/cells.
- For in-sample, iterative same-source two-way site FE and source reporting region×season FE, with no separate intercept, ordinary OLS on FWL-transformed columns. Validate FWL zero group means and matrix rank. Report original-unit β, one train/full sample standard deviation β, partial residual R², Akaike IC on FWL space (same sample), and two-way? **Cluster by unique original GLORYS wetcell**, with conservative **reporting-region t(G-1)** CI and leave-one-region-out coefficient sensitivity. Clusters are not repeated source months or Landsat pixels.

## Separate temporal transfer: **main falsification**

- Fit on the subset of <=2004 rows only. Site intercepts from training only; numerical covariates standardized by *training* mean/SD. Study same identical heldout known-site source rows across `M0, M_S, M_A, M_B, M_AB, M_SAB`. All must use complete observed physics from that year; no target-year Y or region×season FE.
- Evaluate site-equal heldout RMSE and site-equal MSE loss for all models on **exactly same heldout rows**, compared as paired losses. Report uncertainty from **2000 source-reporting-region resamples**, seed 20261119; each reported region sampled with replacement then all its sites, sites weighted equally within sampled region, and difference MSE to M0 and M_S. Intervals are sample-region sensitivity, not population-wide hypothesis test.
- An A or B explanatory contender is provisionally preferred **only if** its heldout site-equal RMSE is lower than M0, M_S, and the other candidate **and** 95% source-region resampled paired MSE difference CI upper end is <0 for all three. Even if met, **ecological mechanism unproven** without direct independent polynya or freshwater/CDW and isotope baseline observations.
- If neither satisfies that joint criterion, verdict **NO_GO_AB_MECHANISM_WINNER**, while original 860 observation remains unchanged. Any favorable subset or in-sample coefficient is described exploratory, not promoted as verified mechanism.
- A+B (two df) is reported exploratory only to test complementarity, never evidence that A and B are mutually exclusive or causal.
- Response is **Landsat spectral PLSR-reconstructed optical δ15N proxy**, not observed fish fraction, not identical to original hierarchical diet posterior. Youngflesh isotope preprocessing uncertainty and local POM baseline unaccounted; direct diet source only a handful of localities. No future 2050/2100 demographic or fish/krill projection.

## Reproducibility / valid error rules

- Independently hash-check isotope source ZIP and assert A/B physical artifact names, 860 site-seasons, 693 complete B, 82 wetcells, 68 B-wetcells, 13 regions, exact site+season one-to-one and original summer source salinity agreement <=1e-4.
- Report full sample equal-support and heldout source cohort. The expected time counts on the 693 subset are **not assumed**, rather measured from original fixed season split.
- If training sample rank or heldout known-site support is too sparse, record **MODEL_SUPPORT_NO_GO**, not invented coefficient/zero-filled outputs. Missing Zarr or ZIP is retrieval failure not negative ecological result.
- Save derived CSV/JSON model coefficients, paired losses, region sensitivity and source receipts. Do not re-archive author raw images or old biological source ZIP.
