# Palmer P0 original catalogue support — 2026-10-29

**SOURCE AVAILABILITY PASSES; LOCAL PIXEL / HISTORIC COLONY GEOMETRY REMAIN UNVERIFIED.**

The [source-only Actions run](https://github.com/zuizui0223/mina/actions/runs/40858156062) completed **52/52** fixed February–March, source×year STAC requests without errors and passed five deterministic contract tests. Original artifact **12889064493** contains scene IDs, acquisition dates and page SHA-256 receipts. Its complete ZIP SHA-256 is **89d7ccc08c1c44ff10822b26f6d8f1e1fdbad3c0788a324d8ee6f162990a8d6f**.

The queries cover one fixed pooled Palmer bounding box (Litchfield, Humble, Torgersen), not colony polygons. Landsat Collection 2 Level 2 (Planetary Computer) searched 1986–2026; Sentinel-2 L2A (Element84 Earth Search) searched 2016–2026. An image in February–March calendar year Y belongs to the penguin breeding season starting Y−1.

- **Landsat 406 scene records**, present in 32 of 41 queried calendar years; **Sentinel-2 152 records**, present in eight of 11 years. In the chosen Sentinel source, February–March 2016–2018 returned no scenes; this is a catalogue-specific absence, not an assertion that all satellite imagery was absent.
- **Litchfield historical monitoring:** 2006 breeding-season count was positive (four pairs), with first observed zero in 2007. This corresponds to **2007 imagery as last post-season positive** and **2008 imagery as first post-zero**. Across 1986–2007, Landsat has 96 candidate scenes across 13 positive catalogue-years; 2008–2026 has 310 across all 19 years. This passes a **scene-only** ≥3-year screening, nothing stronger.
- **2008 (critical first post-zero summer): one scene, reported whole-scene cloud 94%.** From 2008–2011, 19 scenes total and **none** with reported whole-scene cloud <20%; local clear-pixel support is untested and could differ.
- **Geographic gate:** Cimino et al. (2025, https://doi.org/10.1007/s10980-025-02088-y) published 23 historic Torgersen subcolony locations, 18 extinct and five remaining in 2022. Extinct polygons span 212–3433 m²: only ~0.24–3.81 nominal 30 m Landsat pixel *areas*, not necessarily uncontaminated pixels; 10 m Sentinel-2 areas span 2.12–34.33 nominal pixel areas. Historic polygon GIS and census-code crosswalk have not been retrieved and authenticated within mina; a figure or a 2 km buffer cannot substitute.
- **Prior local-pixel constraint remains:** at Litchfield the fixed January 2019/2024 Sentinel comparison had *zero shared clear-land pixels*. The newly discovered Feb–Mar scene records cannot overturn that without reading QA and reflectance on the same plots.

The raw per-year source counts are committed in the accompanying \`catalog_years.csv\`; detailed item IDs and source response SHA-256 hashes remain in the Actions artifact. No vegetation change, penguin-driven ecological effect, or front migration is estimated.

**NEXT gate:** verify GPS-georeferenced historic nesting patches, independent never-occupied ground, and raster QA-clear (non-water/non-snow) pixels on matching plots before measuring any vegetation. Require three reliably imaged years before and after documented local abandonment (not merely three catalogue years), test pre-event trends, and match elevation, aspect, snow persistence and observation support. On failure, record *not identifiable* rather than use selected positive NDVI images.
