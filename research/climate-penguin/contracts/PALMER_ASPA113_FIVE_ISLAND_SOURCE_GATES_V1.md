# Palmer five-island original source comparison: island mechanism gate

Context: Litchfield original ASPA 113 source (22 original breeding seasons 1991–2012) recovered six explicit zero seasons and the missing positive 2006 count; source months remain unresolved.

**Previously committed data:** `outputs/comparison_audit/palmer_five_island_counts.csv` is an independently retrieved **dataset product** from Rutgers/Palmer LTER ERDDAP, but it may share the W.R. Fraser original *field observations* with the 2014 ASPA 113 plan, so it is NOT an independent biological validation sample.

This source has all five island colony component count summaries in each of 27 years 1991–2017 (135 rows), including LIT zero for 2007–2017. Full four neighboring colony groups remain positive through 2017. These are aggregate monitored breeding groups, not explicit original survey effort or verified land polygons.

**Important count disagreement:** 1998 official LIT count 338 vs Palmer 325; 1999 official 322 vs Palmer 301. All other 20 official 1991–2012 annual values coincide. Both series remain immutable; the difference may reflect group-aggregation extent / census source version / methodology. Do not silently choose the more convenient count for a model.

**Original spatial association:** Source-known site code pairs CHR→CHIS, COR→CORM, HUM→HUMB, LIT→LITC, TOR→TORG; no fuzzy join. Site coordinate distances are center-point approximations, not the distances between island coastlines. The previously derived Plantarctica spatial point-buffer counts at 500m and 2km are explicitly NOT physical-island-unique habitat area, and at least the 500m Litchfield/Humble and Litchfield/Torgersen buffers overlap. No independent island vegetation covariates can be inferred from these overlapping centroids. Other temperature grids cannot be assumed independent over 0.7–6km.

**What remains unidentified:** local island *physical* rock availability change, snow cover dynamics, source-corrected annual observed vegetation cover, actual seal trampling history, full 1991–2007 local nearshore sea ice, exact Palmer census month, and prey. The 2014 ASPA plan documents Litchfield vegetation already present and its damage/recovery related to seals. This is a strong alternative pathway to a simplistic "abandoned penguin site greens" interpretation. The paper should treat this as a competing animal-driven habitat pathway, not retrospective causality or a new independently replicated experiment.

**Frozen outcome:** only original source-reconciliation, the five-island same-region comparison *opportunity*, and spatial/data gate fail. No post-hoc permutation p or ecological effect claimed. Keep Ecology Paper 1 (#189), Paper 2 geometry/mammal (#199) separate and unchanged. Code: `work/climate_penguin/audit_palmer_aspa113_island_context_v1.py`. 
