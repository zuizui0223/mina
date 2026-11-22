# Independent emperor penguin × coastal-polynya validation (v1)

**State (2026-11-22):** outcome-blind protocol frozen; public LaRue source inspected; code and five synthetic tests validated locally; **no DEEP-AA-exposure linkage or empirical effect estimate yet**.

## What is frozen
- Species: *Aptenodytes forsteri* (not the current Adélie manuscript).
- Outcome: LaRue et al. (2024) published 50-colony × 2009–2018 annual abundance/attendance index `N_mean`; those are model-derived values rather than 500 independent direct counts. Source: https://github.com/davidiles/EMPE_Global/blob/main/analysis/output/model_results/3_Colony_Level/colony_summary.csv .
- Exposure: DEEP-AA v1.1.0-2023 author's recommended `SIC60_6.25km_20d.zip` from https://doi.org/10.5281/zenodo.13358042 . Use `LonLat.nc`: daily NetCDF `x,y` refer to indices, **not metric coordinates**.
- Primary season: April–August; region 100 km geodesic radius; fraction of coastal-polynya ID-mask pixel-days; source code classifies positive EVEN IDs as coastal.
- Missing: 2011 September through 2012 July. April–August 2011 need not be excluded; April–August 2012 must be excluded.
- Outcome test: two-way (colony, year) fixed effects; regional clustered and exhaustive sign-flip diagnostics; stringent region-year FE; one-region-out sensitivity; a priori expected sign positive and two-sided p.
- Stop rule: no result unless primary ZIP MD5, source blob SHA, `LonLat.nc`, 95% daily season completeness, and a minimum of 300 complete colony-years validate.

## Evidence and interpretation gates
- Raw LaRue source was audited: 669 satellite-image rows across 2002–2021, of which 599 were dated 2009–2018, spanning 54 raw site IDs and 536 raw site×years. These are **not** the same as 599 independent modeled observations.
- Frozen LaRue `colony_summary.csv` has 500 posterior-summary rows, 50 model colonies and 10 years.
- A positive result would be **screening association**, not causal foraging access, not a paper-ready effect, and not direct replication of the Adélie δ¹⁵N observation.
- A publication claim requires uncertainty propagation from LaRue's posterior output and a separately measured sea-ice-concentration covariate.

**Current blocker:** the official 248.4 MB DEEP-AA ZIP download failed in the present analysis runtime. The independently created local package `emperor_polynya_independent_v1.zip` (run script, 5 synthetic tests, full frozen contract, validation ledger) was supplied with the research conversation. Do not replace empirical data with simulated exposure.

Literature checks: LaRue et al. 2024, *Proc. R. Soc. B*; Lin et al. 2024, *Scientific Data*; Foster-Dyer et al. 2026, *Proc. R. Soc. B*; 2026 Sentinel-1 overwinter colony mobility study.
