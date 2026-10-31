# Antarctic Palmer island natural contrast — original-data crosswalk and inference ceiling

2026-10-29. Draft mina PR #206, observational island-ecology discovery; frozen Ecology Article PR #189 and Antarctic predator/access Paper2 PR #199 are unchanged.

## One-sentence source finding

**Five genuinely different physical Palmer islands contain five monitored Adélie breeding groups whose 1991–2017 trajectories diverge despite all five mapped site coordinates receiving exactly the same regional ERA5 air-temperature grid; Litchfield, the largest mapped landmass but initially the smallest monitored colony, records breeding-pair zero beginning in 2007, whereas all four other island groups remain positive in 2017.** The post-abandonment-era Plantarctica published composite maps 11.54 ha of vegetation plus lichen within Litchfield's independently verified physical island boundary. **None of these observations identifies a warming-, abandonment- or animal-driven vegetation-change mechanism.**

## Original-data sources and sample grain

1. 2014 Antarctic Treaty ASPA 113 official Litchfield Table 1: 22 annual breeding seasons 1991–2012, four breeding pairs in 2006 and six original zeros 2007–2012. No row-level census month; **do not impute** date. Original MAPPPD frozen source overlaps 17/17 counts but misses five 2006/2009–2012 records.
2. Palmer LTER independent dataset product: five named monitored island-group histories × 27 annual seasons 1991–2017 = 135 rows. **Not independent biological replication** of the ASPA primary source; the 1998 and 1999 Litchfield source counts differ (ASPA 338,322 versus Palmer 325,301).
3. SCAR high-res v7.12 2026 cartography: all five preserved site coordinates lie inside five **different** original `surface=land` source polygon IDs. Physical mapped land areas: Litchfield **0.353379 km²**; Christine 0.205425; Cormorant 0.084518; Humble 0.083013; Torgersen 0.083975. 2026 area is not documented historical nesting availability. The available 2026 medium-res SCAR rock map finds 0 exactly assigned recorded source rock polygons in each; no biological absence follows.
4. Plantarctica 2024-published original map (Figshare DOI 10.6084/m9.figshare.24745956; 87,391 original polygon features; source SHA256 `7e304e7a...`). Union/clip vegetation, lichen and algae to the **actual unique mapped land polygon** instead of overlapping point buffers. Litchfield: 85,558 m² Vegetation + 29,819 m² Lichen = **115,377 m² (32.65% of mapped source land)**. Humble 23,026 m² (27.74%); Christine 4,700 (2.29%); Cormorant 1,872 (2.21%); Torgersen 1,161 (1.38%). This is a **static classification composite**, not a map of vegetation that newly colonized after a 2007 colony collapse. Published original ASPA ecology describes moss vegetation and seal trampling/recovery as independent pathways.
5. Original Open-Meteo ERA5 2 m 1991–2020 grid source (explicit ERA5; no elevation downscaling; verified **10,958 daily observations**): all five exact site coordinate queries resolve to **one source grid [-64.75,-64.0]**, with **identical** 30-year daily temperature values; source SHA256 of 5-site query `3ecdee19edcebd44837d137734634b622a2c005d3e3d1757646c221cb9448596`. The shared ERA5 source is not a field-observed shared island microclimate. Local coastal snow/sea ice, seal disturbance, food supply, nesting capacity and survey effort could still differ considerably.

## Five-island inspectable crosswalk

Source-joined sample: `outputs/climate_penguin/palmer_five_island_observed_counts_static_maps_source_crosswalk_v1.csv`. Site keys CHIS/CHR, CORM/COR, HUMB/HUM, LITC/LIT, TORG/TOR are explicitly fixed. Litchfield's 1991 monitored count was **497 (smallest of five)**, although its mapped land area **0.353 km² (largest of five)**; the others' 1991 counts were 1410/681/1085/3016. Hence apparent failure of a naive island-area survivorship ranking is confounded with **initial social-colony size**, and cannot refute probabilistic island-biogeography theory.

Selected yearly original monitored counts (Palmer source):
- 2006: CHR 229, COR 134, HUM 188, LIT 4, TOR 362.
- 2007: CHR 329, COR 94, HUM 178, LIT 0, TOR 246.
- 2017: CHR 27, COR 23, HUM 68, LIT 0, TOR 22.

## Testable general island-ecology contrast vs invalid conclusion

- **Supported descriptive contrast:** common *coarse atmospheric forcing*, different monitored colony histories; one original physical island shows sustained zero in monitored breeding pairs while four others retain positive populations. Static physical land area does not equal original monitored colony size.
- **Not yet identified:** whether land substrate capacity, recurrent social aggregation (Allee/conspecific attraction), population density, fur seal occupancy, nearshore seasonal ice, sea access or prey availability caused the observed differential decline; and whether penguin abandonment accelerated vegetation establishment.
- **No inferential comparison** of 5 sites with only 1 independent regional temperature grid; no climate effect p-value, no causal warming association, no before/after vegetation outcome, no extrapolation to Antarctica. The already explored 216 climate screens have no wild-cluster BH-corrected confirmations; do not post-hoc reduce their adjustment family to manufacture significance.

## Priority next real measurements

1. **Temporal vegetation:** co-registered satellite images with independent seasonal/snow/cloud masks on true island polygons before and after 2007, plus near-contemporaneous four island controls. A published post-event static map cannot serve as pre-event baseline.
2. **Independent climate/microhabitat:** original 1991–2007 local nearshore sea-ice and snow/ice-free rock/nest access time series at island scale, not cloned ERA5 grid exposures.
3. **Observation process:** obtain dated source census months and comparable effort in all five original colony series; don't treat unspecified source months as precise September/post-November counts.
4. **Competing mechanisms:** original time-varying local fur seal trampling/abundance, guano, shore access and initial colony size/social occupancy. One local loss cannot identify a multi-mechanism island-size effect.

All original-data wrappers are held in PR206 source-specific JSONs; see `ORIGINAL_LITCHFIELD_PALMER_EVENT_RECEIPTS_20261029.json`, `ORIGINAL_PALMER_5ISLAND_PLANTARCTICA_LAND_CLIPPED_RESULT_20261029.json`, `ORIGINAL_PALMER_FIVE_ISLAND_ERA5_GRID_RECEIPT_20261029.json`, and source crosswalk CSV. Real original GIS and temperature source GitHub Actions runs: #40861973884, #40862837021, #40863372786. Generic CI checks do not imply scientific inference; all attribution remains HOLD.
