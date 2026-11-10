# Original OSI SAF sea-ice expansion from 40 to 595 Antarctic breeding sites

**2026-11-09 | A scale-fix source experiment, not a new positive p-value search.**

After [Pan-Antarctic MAPPPD macro inventory](outputs/macro_original_coverage.json) succeeds, the biological denominator remains **595 observed sites in 18 source regions**. Prior native 30-year site-month SIC exists at only **40/595 sites**. **Do not reduce the macro question to those 40 or to 25 local satellite points.** The next operation is extraction of original gridded monthly SIC at all 595 site coordinates.

## Fixed source pilot (source QA before longitudinal models)

- Publisher **EUMETSAT OSI SAF OSI-450-a1 v3.1**, native 25km Southern EASE2 monthly NetCDF, via original THREDDS `thredds.met.no`. This is measured/monthly reprocessed SIC, *not* a future climate forecast and not the same estimator as prior daily-derived original 40-site SIC.
- Fixed 3 source years **1993, 2008 and 2018** × August–November = **12 original monthly source scenes**. They were selected to span the historical source period, not based on colony response. **This is an acquisition/geometry pilot only**, not a two/three-date ecological trend or years chosen for statistical significance.
- All 595 sites from source-pinned original file `macro_panantarctic_v1/outputs/panantarctic_595_site_inventory.csv`. Verify unique original site codes, polar coordinates and original static source file SHA.
- Use 1993-09 as **fixed native ocean mask reference**. Native `status_flag` marine when `(flag & 3)==0` and `ice_conc` physically valid. For each original site, choose **all source-ocean cells whose original EASE2 lat/lon center is within 100 km WGS84 geodesic** of the observed colony point; keep those same reference cells in every month. If fewer than 3 reference ocean cells are available, mark original site support inadequate, do not relocate/shift a site to find favorable climate.
- Later monthly `ice_conc` included only for **the same frozen native reference ocean pixel IDs** when their original source status/physical values remain valid. Monthly value accepted if ≥80% of those reference ocean cells have valid original SIC; otherwise **MISSING_SIC_SOURCE_COVERAGE**, not ice=0. Months with 0 SIC on all valid ocean cells are valid observations.
- Record original source URL and SHA256 for all 12 NetCDFs, 595 site IDs, exact native ocean-source grid hash, pixel count, nearest ocean cell distance, per-month supported pixel fraction, and original SI mean SIC. Independently compare the 40 overlapping original site codes to the earlier original daily-derived monthly values in **1993/2008/2018**. Since source products and aggregation differ, do not demand exact numerical equality; a large systematic disagreement is a scale/sampling warning to resolve before computing environmental niches.

## Interpretation + exit

A successful marine source expansion across the full observed colony site set is a **real scale upgrade**, but the 12 monthly snapshots are not a robust long-term climatic trend. If original publisher download/coordinate/coverage fails, record `SOURCE_HOLD` and do not assert no sea ice.

On success, the same **595-site fixed native marine pixel memberships** can then be evaluated across the full 1991–2020 Aug–Nov period, while preserving varying monthly masks, spatial dependence and region blocks. Land vegetation remains the independently mapped 222-site **static** environment, not annual green-up.

No MaxEnt pseudoabsence, GAM k/β selection, climate effect p or warming-caused future penguin nest forecast is produced by this pilot.
