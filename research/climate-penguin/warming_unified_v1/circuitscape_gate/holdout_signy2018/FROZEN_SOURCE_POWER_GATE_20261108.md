# Frozen independent-season extension gate: BAS Chinstrap Signy 2018/19

**Date:** 2026-11-08 JST. **Status:** source-support and physical-SIC gate defined *before viewing 2018/19 source-GPS ocean-use scores*. The earlier 2011/2013/2015 GPS and ice diagnostics are known, so this is a **post-hoc held-out season extension**, not an independent preregistration or a new independent island.

## Biological/evidentiary purpose
In the current PR #211, nominal 270 same-day Circuitscape runs on 2011/13/15 had only one source-year with substantial seasonal SIC spatial variation, and neither β=+2 nor β=−2 consistently beat β=0 on six island-year mean GPS current-rank scores. Before adding GPS outcomes, determine whether source BAS Chinstrap **Signy 2018/19**, which did not enter those 45 old matched-island dates, can provide an **out-of-year test in an original previously withheld GPS season**.

## Frozen source and support
- Original BAS V2 Chinstrap GPS DOI `10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92`, same original archive, SHA-confirmed 313 files / 308 nonempty tracks and 253 QC-qualified overall. Only `site=SI`, `season_start=2018`.
- Predefine entire breeding summer calendar **2018-11-01 through 2019-02-28** inclusive; do **not** choose dates based on SIC gradients or model score. Original source track has timestamp, latitude, longitude, unique deployment. Source island center from original median *first* GPS fix across all 58 deployed Signy 2018 tracks, not a subsequently chosen marine endpoint.
- Apply exact existing source qualification per track: 10–150 km geodesic from original first-fix-median center, remove isolated GPS spikes, choose one fix per hour from retained positions, ≥10 hourly fixes in a track; original ocean-use GPS cells are deduplicated within each day and never treated as independent individuals.
- All unique GPS days with ≥1 qualified source fix within the frozen date range are **required**. Before inspecting SIC, archive their exact roster and n deployment/fix effort. No day discarded because its SIC looks boring. Fetch only matching source-date OSI SAF OSI-450-a1 v3.1 daily 25km EASE2 originals with publisher file hashes, 2018/19 months; the source is available through 2020. If fewer than 8 GPS days qualify or required NetCDF unavailable, record SOURCE_HOLD without changing source cohort.

## Environmental *power-to-identify* gate, no outcomes scored
- For each GPS day, original 25-km source-valid (flags bits 1/2 clear) sea pixels within 210 km of source first-fix-median center. Make the 8-neighbor component of the nearest source-valid marine pixel within 35 km. If no source within 35 km, record unresolvable (not missing=zero).
- Restrict GPS ranking background to source-connected marine pixels 10–160 km from center. For all calendar days compute original SIC physical grid variance: 10th–90th quantile width (pp), min–max, fraction with SIC≥1%, 15%, 30%, coverage of valid connected ocean, and count of offshore ground pixels 175–210 km, independent of GPS ocean-use result.
- **Frozen GO for new Circuitscape GPS test** only if at least **10 distinct GPS days** have usable original SIC, **at least 5 distinct days** have 10–160 km SIC p90−p10≥1 percentage point and **≥8** connected offshore ground pixels on each included date; otherwise NO-GO for a useful new season test. These are *power/source gates*, not a biological negative finding. Avoid β optimization.
- Report how many days have a perfectly constant entire circuit SIC (≤1e−8 pp), perfectly constant ranking-area SIC, and weak rank-area contrast (<1 pp) separately. Even when spatial SIC ranges exist, model signal vs GPS compatibility remains untested until a valid new test is executed.

## Locked out-of-year validation if physical support GO
- Use same GPS-to-original-source-valid-ocean pixel max **20km** and 10–160km ranking bins of width 25km, dedup within original day.
- Same three frozen 8-neighbor Circuitscape advanced models: `R=exp(β×SIC/100)` for β0=0, β+=+2, β−=−2; same original nearest ocean source (within 35km), 210km outer domain, 175–210km ground belt, and 1A source. No grid resampling, no alternative sinks after seeing fit.
- Compare observed GPS-cell current-rank percentiles in matched 25-km source-distance bins against uniform sea-only β0; report per-day gain, then **one** out-of-year island-season mean, not a new independent island replicate or a p-value based on GPS cells. Do not use withheld 2018/19 GPS locations to choose β or to define source/grounds.
- Independently reproduce at least one actual Julia Circuitscape current map with SciPy Laplacian. If not numerically validated, do not report ecological skill. **Keep true availability vs GPS unobserved ocean distinct**.

## Biological scope and stop
This is a **within-season marine-use** check and cannot infer individual breeding dispersal (requires years of band/resight site/status), ice navigation cost, direct consumption, actual prey density, or future penguin nest numbers. If SOURCE_HOLD or low-SIC-spatial-contrast NO-GO, report it as source/power limitation and **do not** expand to a new series of β or select only ice-rich GPS days post-hoc. Existing positive penguin assemblage turnover and original Circuitscape calculations remain unchanged.

Output: original day roster, original GPS source SHA, per-day SIC spatial support and choice-free decision, and if GO independently verified fixed models and scores. Branch/PR: `codex/penguin-circuitscape-feasibility-20261108`, Draft PR #211. Do not modify `codex/climate-penguin-progress` manuscript v0.6 or `main`/Paper1/2.
