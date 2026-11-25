# V52 source-first — BAS/SCAR 2020 Sub-Antarctic coastline original source island exact match

**2026-10-28, frozen BEFORE seeing any original V52 shapefile geometry or bird coast-distance effect.** Only reason to move beyond V51: the globally generalized GSHHG 2.3.7 L1 original full polygons lacked exact containment at TWO of THREE original BAS 2019–20 penguin island sites (Saunders 1, Bellingshausen 0, Thule 0), so V51 biological effect was NEVER calculated. Do not tune island buffer, shoreline nearest-snap, bird guild or geographic threshold to rescue it.

## New publisher-specified original source

BAS/SCAR ADD Supplement original GIS **Vector polygons of the Sub-Antarctic coastline**, Gerrish (2020), edition 1.0, DOI **10.5285/c1d83502-8799-4e3c-bdca-21db6a4405d4** (CC BY 4.0), original catalog https://data.bas.ac.uk/items/c1d83502-8799-4e3c-bdca-21db6a4405d4/ . **Explicit geographic scope 50°–60°S** and **South Sandwich Islands coastlines from official South Georgia GIS**; other 50–60S land from Natural Earth. Source catalogue records projection EPSG:3031, original publisher ZIP shapefile ~1.3 MB. Direct original first-party file:
https://ramadda.data.bas.ac.uk/repository/entry/get/sub_antarctic_coastline_high_res_polygon_v1.0.zip?entryid=synth%3Ac1d83502-8799-4e3c-bdca-21db6a4405d4%3AL3N1Yl9hbnRhcmN0aWNfY29hc3RsaW5lX2hpZ2hfcmVzX3BvbHlnb25fdjEuMC56aXA%3D

Access only original BAS HTTPS and its previously verified first-party 194.66.5.50 redirect, total <=8 MB; validate ZIP magic, safe paths, exactly 1 SHP+SHX+DBF+PRJ geometry family, original shp shape polygon, original PRJ via pyproj CRS (preferred EPSG:3031; STOP if unexpected non-transformable or geodetic CRS source) and record **true SHA256 of ZIP before ANY biological access**. Never write publisher raw geometries/animal coordinates to Git. Subsequent effect-bearing run must PIN this original SHA: first run is explicitly source-only.

## Same independent 3 BAS penguin islands, no new animal data

Source V26 frozen artifact run 40279185790, source NPZ SHA256 1566f4fef4ac5370f40f6482e9f76f7b252e32ade8915a190cf0d2fc946883ec, 122,139 2019–20 original nest records, four source localities. Source candidate islands Ashen Hills=Saunders, Bellingshausen=Bellingshausen, Beach Point+Hewison Point=Thule. EPSG:32726 original nest XY, taxon IDs never used to choose an island polygon. Exclude exactly coincident original source coordinates per existing V27 collision rule.

**Source-only gate:**
1. Transform each candidate island's source-species-blind pooled median nesting coordinate into the original BAS shapefile native CRS, strict point-in-polygons (no nearest point/snap, no arbitrary radius).
2. EXACTLY one original geometry per named candidate; all 3 source candidates resolve to **3 distinct original polygons**; area in UTM 32726 between 0.02 and 1000 km2.
3. >=95% of **all collision-excluded original nest XY** on EACH island must be strictly inside its original BAS/SCAR coast polygon; Beach and Hewison must share the identical Thule original feature. Record each site's raw count, unique count, strictly inside and offshore counts, original shape ID (when source id is nonpersonal) and land area, preserving source exact labels only for candidate site names already public.
4. On pass ONLY save original ZIP SHA256, georeference source CRS, data license/provenance, source row/polygon counts and site-nesting containment fractions. Biological nest concentration/species differences, coast distances, logistic tests, actual shore-to-nest routes, mammalian/refuge/flight interaction still CLOSED in this original unpinned-source run.
5. If source gate fails, report precise failure and close alternative geographical source, NOT nearest-snap or lower 95%. This is a source result, not a biological negative.

On scientific support gate pass, freeze original ZIP SHA in a SECOND source-dependent outcome script run. Reuse V51 otherwise unchanged original Adélie/Chinstrap island-held-out B1=local DEM elevation+slope versus B2=DEM plus original coastline distance, C=0.3, train-only median/IQR, 3 physically held-out islands, equal island-balanced Brier. Prediction requires >=2/3 positive gains AND equal-island mean >=0.005. This is explicitly post V27 exploratory, not an estimate of penguin pathway movements nor mammalian predator effects. Distinguish original full coastline from true 2019–20 season's passable landing coast and surveyed empty nesting habitat.

**Broader hypothesis remains:** Island asymmetric access (predator terrestrial access versus marine-breeder ocean-to-nest access) across mammal exposure and flight. The 3 original islands have only penguin nests and do not identify flying-versus-flightless or mammal effects. No changes to frozen Ecology Paper1 PR189 or paused Zavodovski PR196.
