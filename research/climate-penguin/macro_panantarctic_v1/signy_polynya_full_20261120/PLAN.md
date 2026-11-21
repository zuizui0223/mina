# Signy independent diet implementation plan

**Goal:** Audit the full BAS Adélie stomach series and test the within-Signy polynya association with measured diet, without selecting windows on its result.
**Architecture:** Reuse the verified native DEEP-AA geography and category decoder; extract environment separately before joining stomach seasons. Export sample exclusions, annual support, model estimates and a Japanese verdict.
**Tech Stack:** Python/pandas/numpy/netCDF4/pyproj/scipy/statsmodels.
**Spec:** User-approved Signy-first independent diet validation in this chat; preceding feasibility audit.

## Fixed analysis contract (before environment extraction/join)
- Source: BAS DOI 10.5285/eb421e6d-b93b-4174-904b-9a7b0b401403, full summary table; no restriction to gentoo-overlap years.
- Exposure: native DEEP-AA SIC60_6.25km_20d, coastal polygon IDs, source marine mask. Main radius100 km, June–October in season start year; secondary radius25 km only. This replaces the feasibility memo's provisional50 km suggestion to match the already measured satellite exposure, not because of observed diet correlations.
- Coordinates: BAS Signy/Gourlay locality; record exact source and coordinate limitations. Daily area-weighted fraction, monthly means then equal mean of5 months; each month >=80% calendar days. Missing maps/coverage are not zeros.
- Response: mean per-stomach E.superba / (fish+crustacean+cephalopod+otherfood) mass. Fish fraction secondary, not independent confirmation. Keep mass ratio-of-sums as sensitivity. Missing components are not zero. Duplicated DATE/RECORD_ID excluded; negatives, nonpositive food, component>total tolerance5%+0.05g excluded. Krill cannot exceed crustacean with same tolerance; ratios outside0..1 excluded.
- Season: Nov–Apr; Jan–Apr belongs to previous start year. Use actual dates; adjust sampling date by mean days since Nov1. Minimum5 valid stomachs/season.
- Main coefficient: annual krill fraction ~ coastal_polynya_fraction + mean_sampling_day + linear_year; equal season weights; two-sided95% HAC lag1 interval and p value. Directional prediction positive, significance threshold0.05. Report n, exposure range, effective years. No environmental variance => not estimable; do not fit or try alternative windows for significance. At least8 complete seasons and full-rank design required to fit; this is a feasibility rule, not a power guarantee.
- Secondary unadjusted association,25 km, fish, ratio-of-sums and leave-one-season-out only if supported; mark as sensitivity. Salinity deferred until main test has exposure support; no extra variable search to rescue absent variation.
- Other sites: inventory whether same exposure is measured and variable at Palmer/Hope/Stranger, but current22 records do not authorize pooling incompatible published statistics. Report potential transfer separately.
- Future: no absolute prey supply or population forecast. Scenario interpretation requires exposure overlap and out-of-time skill; absent support means no climate translation.

## Tasks and checks
- [x] Verify BAS source hash, actual years, dates, samples and mass consistency.
- [x] Verify DEEP-AA hash, source grid, valid marine pixels and temporal coverage at fixed coordinates/radii.
- [x] Join by season; execute fixed test or explicit nonidentifiability verdict, preserving all exclusions.
- [x] Check annual counts against raw rows and boundary-year mapping; inspect output and synchronize PR214.

## Execution ledger
- BAS description1997–2020 but actual summary table639 records dates2002-01-03 to2020-01-18,19 breeding seasons2001/02–2019/20. One food-mass inconsistency excluded;638 retained. No invented1997–2001 rows.
- Signy coordinate is Gourlay A39 (-60.731183,-45.586850), BAS GPS attachment DOI10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d. Diet summary identifies Signy only: this is a locality proxy, not individually matched nests or measured foraging positions.

- Completed fixed main fit and prespecified sensitivity checks. Main14 seasons p0.647;25 km and one-season deletion change slope direction. Salinity effect deferred; future projection unsupported. Other-site exposure overlap16 site-seasons, no pooled effect fitted.
