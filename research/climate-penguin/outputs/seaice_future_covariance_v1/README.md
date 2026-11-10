# Future sea-ice covariance at fixed Adélie source breeding sites (physical model only)

**Question:** Does within-model future annual August–November marine SIC cofluctuation change relative to 1995–2014, when annual absolute mean SIC, native model grid-cell duplication and original noncontemporaneous census-count weights are tracked independently?

**Source:** all 9 original committed monthly CMIP6 SIC CSV.gz files, representing 3 model/member pairs each at historical/SSP2-4.5/SSP5-8.5. Calendar-day annual SIC means are recomputed and checked against **all 585 original model×period×39 site historical/future climatology means AND their 20-year annual SDs**. Exact Git blobs pinned. Satellite 1995–2014 SIC is a physically different 0–100 km nearshore observational target; it is only a diagnostic context.

**Model treatment:** For each model/experiment, compare 20 historical years (1995–2014) to two separate future windows 2041–2060 and 2081–2100. Site eligibility is paired within model across each historical/future period (annual SIC sample SD ≥ 0.1, 0.5 or 1.0 percentage points both periods). If a site becomes nearly constant, we do NOT divide by its near-zero SD and fabricate extreme normalized anomalies; excluded census weight is reported. Pairwise time series have identical source-site support, with model native-cell effective number and distinct-cell coverage audited.

**Measures:**
- standard deviation in pp of a fixed-weight *raw* mean SIC across the 20 years;
- standard deviation of a fixed-weight mean of **within-period site-standardized** SIC (unitless shared model anomalies), separately with/without linear detrending;
- equal source-site, latest recorded MAPPPD count, same long-term survey method, within-region equal weights preserving region total count mass, Cape Crozier-exclusion and distinct-model-marine-cell equal weights;
- future minus historical change **within the same model**, not a 3-model likelihood distribution.

**Inference:** No prediction of survival, recruitment, nesting counts, spatial insurance, colony persistence or future animal response. Single-member CMIP6 covariance can be sensitive to internal variability over just 20 years; the model-native marine grid is coarse and many source site codes share cells. An observed historical increase in standardized common anomalies does not prove a future increase. Raw model SIC historical values have 10pp-level local discrepancies with satellite nearshore SIC; no unvalidated model-to-satellite covariance transfer is assumed.

**Reproduction:** \`python research/climate-penguin/work/seaice_future_covariance_v1/build.py --check-receipt\` (Python 3.11, no third-party packages). All historical/future source model-year matrices, site support, annual portfolio series and audits saved to GitHub Actions artifact.
