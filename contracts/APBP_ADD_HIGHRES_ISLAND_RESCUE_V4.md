# V4 — High-resolution island recovery and coordinate-uncertainty audit

**Date 2026-10-19.** Post-*source coverage* remedial audit. APBP original census data have NOT been fitted to any environmental outcomes. V3 medium-scale ADD polygon source classifies 435 original site IDs as separate land island polygons, 78 as largest Antarctica/mainland polygon, 206 as **HOLD**; the 2026 generalized coastline deliberately drops disjoint features below 0.1 km². A medium-map nonmatch is **not** a surveyed missing island or biological zero.

**Source locked before V4 effects (no effect endpoints are computed):**

- SCAR ADD 2026 edition v7.12 **HIGH resolution** coastline polygons, DOI `10.5285/13c4d2f1-8903-4d7f-8977-592121975554`, CC BY 4.0, original zipped .SHP at `https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_12.shp.zip?entryid=synth%3A13c4d2f1-8903-4d7f-8977-592121975554%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N18xMi5zaHAuemlw`, ~72.9MB, EPSG3031 and `surface=land`, distinct from `ice shelf` etc.
- Original V3 medium ADD v7.12 DOI `10.5285/c9c6d671-ad19-4a78-96b2-7d47e9bac46a`, SHA256 `b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38`. APBP official v2.3 ZIP SHA256 `afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf`.
- The high resolution snapshot combines surveys from **1993–2026**, and is a modern cartographic aid, not the nesting land extent in 1980. Island size / coastline changes cannot be assigned annual variation from it.

## Frozen georeference support and diagnostics

1. Reopen official 719 original `locationID` coordinates, including all 4,055 Event records; max within-site source coordinate drift remains checked against 1 km.
2. Download authentic high-res coastline zip plus original medium coast. Verify official HTTPS host, file SHA256, original EPSG3031 `.prj`, original polygon `surface` field. Bound compressed download to 90MB and total decompressed geometry to 1.0GB; do not fetch a different version after output inspection.
3. Use Shapely R-tree to match each source location to one `surface=land` polygon. Exact land containment first, then **one unique nearest land polygon within 250m**, identical to V3. Exclude `ice shelf`, `ice tongue`, `rumple`. Overlapping high-res polygons are ambiguous STOP for that site; do not automatically choose smallest/closest.
4. Report **V3 unmatched 206 site IDs** partitioned into high-res exact land, unique near-land, still absent, or ambiguous. For already matched 513 sites report high/medium assignment agreement/disagreement and cross-version polygons that changed area/identity; such shifts are cartographic source sensitivity not environmental mechanisms.
5. **Crucial location uncertainty gate:** Original APBP `coordinateUncertaintyInMeters` is missing for some sites, and often larger than the prespecified 500m/2000m rock buffers. Report separate `precision_missing`, `precision_lt250m`, `precision_250_to_1000m`, `precision_over_1000m`, and `precision_over_2000m`. A point inside island polygon is labelled `ISLAND_GEOMETRY_ONLY` unless its complete original positional uncertainty circle is contained within that one land polygon and excludes competing land; near-land matches cannot be labelled geometrically robust.
6. No `rock=0` assignment on unresolved sites. V3 rock is a *spatial exposure proxy*, not observed nesting capacity or time-varying deglaciation. The high-res geometry cannot rescue unreliable source georeferencing. Keep a direct match table with exact original site IDs, medium/high source classifications, positional uncertainty, and all source fingerprints.
7. **No ecological effect, fitted slope, habitat vs abundance relation, p-value, or population level outcome at this stage.** The high-res rescue source may strengthen island sampling coverage; it does not establish island effects.

## Decision after original georeference audit

High-res match success alone does not open H1 analysis. Counts must have paired marine-foraging ice anomalies for the correct **survey breeding season** and genuinely comparable island/continental land habitat. If source positional uncertainties dominate coastal island widths, either use site-level island group as an uncertain group in a hierarchical measurement model or restrict to a well-georeferenced subset **based on source accuracy, not on favorable count trends**. Do not imply a continent-wide law from predominantly South Shetland samples.
