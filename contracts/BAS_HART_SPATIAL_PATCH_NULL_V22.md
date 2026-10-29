# V22 — conditional geographic patch test of original South Sandwich nest taxon clustering

**Status: post-V21 source geometry observation, 2026-10-26.** The initial four-locality exchangeable-label test found near-zero heterospecific closest nest within 10m despite four species at Ashen and two species each in three other localities (V21). That null destroys entire species-specific patch structure and is too permissive to identify interspecific competition or fine-scale species exclusion.

We now attempt to **falsify the incorrect reading of V21 as a direct fine-scale competition mechanism**.

## Fixed, post-V21 geographically stratified null

Read only V20 successful source-receipted compressed original UTM EPSG:32726 nest points, and V21 original exact observed 10m nearest-heterospecific rates. Freeze four site files, original ten taxa × site CSV SHA receipts, and all V20 coordinate source-completeness gates; never add source mixed/unknown or 2022 Zavodovski chinstrap nests.

- Primary spatial stratum **100 m × 100 m UTM square**, indexed by `floor(x/100),floor(y/100)`, with absolute UTM grid origin (0,0).
- Secondary spatial strata **25 m** and **500 m** UTM squares; these are diagnostics chosen post-V21, not alternate significance tests.
- Fixed primary grid phase sensitivity at 100m: `(0,0)`, `(50,0)`, `(0,50)`, `(50,50)` m shifts. A species effect dependent on arbitrary grid origin is not reliable.
- In each site separately, maintain **all fixed original nest positions and the exact number of nest labels of each species in each spatial cell**. Permute species labels only within each cell that actually contains at least two species and two nest coordinates. Monospecific spatial cells remain unchanged.
- Repeat **99** within-cell label permutations per site × scale/grid-phase with frozen RNG seed `20261026 + site-index*10000 + scale-index*100 + phase-index`. The observable response is the **exact same V21 10m nearest-neighbour heterospecific probability**, with no model fitting or selected species contrasts.
- Report `delta = median(null_{within_grid}) − observed_original`, not an inferential p-value. Also report the fraction of V21 source points in mixed-species cells and percentage of permutation-eligible nearest-neighbor points.
- **Predefined interpretation testability:** If <**5%** of original eligible nearest-neighbour source positions occur within cells actually containing multiple labelled species, the test has low power to measure *within-cell* mixing; return a **GEOGRAPHIC_MIXED_PATCH_SUPPORT_HOLD**, even if species segregate very strongly overall. Do not label the resulting near-zero delta as proof of no fine-scale competition.

## Inference

If original nearest heterospecific rates are below the 100m within-cell label-permutation distribution in a well-mixed cell-supported source sample, evidence exists of nest-scale *within-patch* species assortativity beyond coarse 100m species sorting. This could arise from fine habitat, colonial group nesting, social settlement, methodological drawing or genuine interspecific interactions. It is NOT direct evidence of competition, territorial exclusion, island dispersal, original habitat capacity, or a transferable Antarctic island law.

If 100m cell-local null is close to observed or has very few mixed cells, the larger V21 result is mostly explained by source distribution into separate patches rather than within-patch neighbor avoidance. Species-specific local breeding patch occupancy becomes the proper ecological unit; independent patch geology, area, weather, elevation, survey/orthomosaic common footprints and actual ecological species interaction must be measured to test mechanism.

**Unit of geographical replication:** four surveyed localities (Ashen, Bellingshausen, Beach, Hewison) nested within three **gazetteer candidate** parent islands (Saunders, Bellingshausen, Thule). Nests are NOT four independent island population replicates and the data are one campaign, not a demographic time series. No standardized visited-empty habitat or shoreline-distance comparisons are available. V21 original already-published observational patterns cannot be promoted as prospectively novel causes.
