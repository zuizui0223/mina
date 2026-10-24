# NOAA/NSIDC G02202 v6 — pre-result marine environment join V5

**2026-10-19.** This is a marine *covariate construction* contract, not an ecological effect model. APBP v2.3 source census and SCAR ADD medium/high coast and rock QA were opened before this contract; **original G02202 v6 monthly sea-ice values and their associations with breeding nest counts have not been examined** before committing these ocean exposure choices.

## Exact original source

- `NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6`, DOI **10.7265/b18j-z797**, Antarctic stereographic raster EPSG:3412 at **25 km**.
- Public HTTPS monthly aggregated original NetCDF file `https://noaadata.apps.nsidc.org/NOAA/G02202_V6/south/aggregate/sic_pss25_197811-202609_v06r00.nc`, official publisher index reports **117,472,635 bytes** (verified 2026-10-19). Download this exact file once, record original bytes and SHA256. Do not mix versions, hemispheres, variable types, daily/weekly or satellite algorithms.
- Schema expected: `cdr_seaice_conc_monthly`, `time`, projected `x` and `y` or legacy `xgrid`/`ygrid` with spacing ~25km, `projection` CF mapping; original CF units **fraction (0–1)** after packed netCDF automatic scale and fill handling. Land-masked and missing ocean pixels cannot be interpreted as zero open water.

## Exposure selection frozen before inspection

For every original APBP `locationID` (719), project original WGS84 Event source site coordinates to EPSG:3412; original `coordinateUncertaintyInMeters` and year/site representation retained, not silently deemed precise nesting patch location.

- Marine (offshore) annulus near: grid centers **25–75 km** from site source point; far/foraging sensitivity annulus **75–150 km**. Neither is species-specific empirically measured foraging habitat, and offshore sea-ice concentration is not sea-ice surface at the nest.
- Exposure months for southern summer breeding start-year `t`: **October and November of t** (both must be present). `SIC(i,t)` is the mean of two monthly **means of original valid ocean CDR cells** in the annulus. Require at least **four valid ocean pixels in each month**; otherwise emit missing/HOLD, never zero.
- Site-specific 1981–2010 climatology mean across available complete Oct–Nov seasons (at least **20 separate years**) is used to form anomaly `SIC(i,t) - baseline(i)`. Also preserve the raw SIC and the number of valid offshore pixels. Baseline not tuned to results.
- Use a descriptive availability ratio: number of matched APBP sites / site-season rows with near/far valid anomalies, and describe how many sites/seasons are always open water (all Oct–Nov SIC=0) or always high ice. This reveals predictor identifiability **without touching nest count effects**.
- The output `site_id × breeding_start_year × mean_SIC_near/far × anomaly × cell_count` is a *climate predictor candidate*, not reproductive effort, foraging success, migration, or coastal fast ice. Original marine values can fluctuate within same 25km coastal pixels across multiple neighboring colonies: clustered site/region dependence later necessary.

## Observation dates and temporal exclusion

For a future APBP nest-count matchup, `Event.eventDate` with an exact YYYY-MM-DD or YYYY-MM is required. December surveys `year t`; Jan–Feb surveys `year t+1` refer to Oct–Nov climate in t. November surveys could include after-survey days in November and are **not eligible for the primary temporally antecedent design** (pre-existing site-year data still retained; future Sep–Oct sensitivity requires a new frozen temporal plan). Source `YYYY` only cannot unambiguously locate the breeding season and is **HOLD_YEAR_ONLY**, not forced to Jan or Dec. Surveys outside Dec/Jan/Feb excluded from primary temporal match without claiming those were biologically irrelevant.

## No statistical overclaim

This stage uses **all original 719 locationIDs independent of counts**. It generates NO climate→abundance correlation, beta, p-value, habitat interaction or claim that offshore SIC is causal krill abundance. Monthly 25km SIC cannot resolve landfast ice or immediate colony access; emperor penguin breeding failures and coastal fast ice need a different higher-resolution environmental indicator.

If G02202 aggregates are unavailable, payload too large, temporal coordinate/CF mapping invalid, fields contain unhandled coastal flags, or non-unit 0–1 data are returned, **STOP** and do not substitute a convenient year or a different ice product after seeing APBP counts. The source variable is frozen. Final model remains prospective until this climate-matching QA and island habitat/classification limitations are resolved.

## 2026-10-19 provenance-only correction before marine values were read

The originally archived directory listing named `197811-202606` (116,765,633 bytes), but direct original NOAA download returned **HTTP 404**. A new *live* official NOAA HTTPS index was inspected; its single current monthly aggregate is `sic_pss25_197811-202609_v06r00.nc` (117,472,635 bytes). Only the upstream **end-of-aggregate filename/month and corresponding byte-size provenance** changed; the predeclared analysis interval remains 1979–2022, exposure months Oct–Nov, near/far annuli, climatology 1981–2010 and all exclusion rules unchanged. No sea ice concentration values or penguin effects had been read before this correction. Do not silently adopt later monthly aggregate files or change source-version family after outcomes become available.
