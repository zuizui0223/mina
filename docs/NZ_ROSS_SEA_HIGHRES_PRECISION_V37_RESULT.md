# V37 — Higher-resolution Antarctic coastline does not resolve the original Ross Sea colony position uncertainty

**Executed 2026-10-24.** Frozen geography-only post-V36 audit, no original penguin count magnitudes opened. Original high-resolution SCAR Antarctic Digital Database (ADD) coastline polygons 2026 edition 7.12, DOI [10.5285/13c4d2f1-8903-4d7f-8977-592121975554](https://doi.org/10.5285/13c4d2f1-8903-4d7f-8977-592121975554), were downloaded from the official BAS original Shapefile ZIP, **72,864,027 bytes, SHA256 `66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4`**. Source shape coordinate system EPSG:3031 validated, original source `surface=land` polygon count **17,269**, source geography invalid polygons zero. Source original data and V35 source reference hashes all match. [Original GIS CI #40076084073](https://github.com/zuizui0223/mina/actions/runs/40076084073) PASSED after two coding/fixture fixes (1. synthetic test falsely placed land polygons within 2 km, 2. original archived column name used `original_colony`).

## New real positional-geography result

The original 2026 NZ Ross Sea Adélie location workbook reports coordinates only to the nearest minute. Adding more precise coastline polygons DOES NOT make the original penguin location observations more precise. Thirty-three exact matched original site names were reconsidered. The high-resolution coastline returned **9** points exactly inside one mapped land polygon, **13** unique near-land assignments within the unchanged 2 km V35 threshold, **6** too far from any mapped land, and **5** with multiple candidate near-land polygons. The latter 24 are not precisely certified source island points.

For the **same four fixed** original V35 source island groups and identical original source observation-presence roster, the three predeclared positional scenarios yield:

| Geographic evidence requirement | Named island groups with >=5 original annual observation windows | Shared years with >=2 islands | Frozen >=3 islands + >=8 years pass? |
|---|---:|---:|---|
| High-res exact SOURCE LOCATION CENTER inside land polygon | **2** | **5** | NO |
| Exact center AND whole latitude/longitude ±0.5 arcminute rectangle inside same polygon | **1** | **0** | NO |
| Exact center AND whole conservative ±1 arcminute rectangle inside same polygon | **1** | **0** | NO |

The only location that remains source-positional-envelope stable under the conservative scenario is **Cape Royds on Ross Island**, yielding 34 annual same-colony pair windows at the original author observation level. Beaufort's original point is not exactly on the new mapped land polygon; Coulman is split between source exact and approximate points with too little qualifying independent yearly support; Inexpressible's georeference center is inside land but its whole 1′ source-position envelope crosses the land polygon boundary. None of these failures implies the birds never nested on the named island—the geometry audit concerns the *rounded original point's inferential precision*, not known penguin presence or site reality.

The high-res source has 17,269 mapped `land` polygons; this should not be mistaken for 17,269 independently observed breeding islands. Its 2026 shoreline is not historical 1980s nesting substrate or annual rock exposure.

## Scientific decision

**HOLD_COARSE_COLONY_GEOREFERENCE_NOT_FULL_ISLAND_ROBUST.** V36 remains a real exploratory result of observed mixed annual breeding changes among four **source-named candidate landmasses**; high-resolution GIS alone cannot elevate it into a geographically robust island-level synchrony law. No V36 animal response was recomputed, and the V35/V36 2-km selection threshold and 13-year roster were not modified.

The next source that can change the inference is an independently acquired original higher-precision colony location/uncertainty dataset, matched on IDENTICAL source colony identities and localities, checked against original GIS and independently recorded survey methods. The earlier APBP v2.3 original Darwin Core Event archive is a prospective **georeferencing source** only, not a source of new independent nesting outcomes when it republishes the same colony-year census. No post-result fuzzy-matching alias, named-feature rescue or hand-positioned GPS is permitted.

- [Frozen original V37 geometry/position-error protocol](../contracts/NZ_ROSS_SEA_HIGHRES_SOURCE_UNCERTAINTY_V37.md)
- [Actual source result JSON and all 33 point-by-point geometry categories](../results/NZ_ROSS_SEA_HIGHRES_PRECISION_V37.json)
- [BAS SCAR high-resolution original publisher source](https://data.bas.ac.uk/items/13c4d2f1-8903-4d7f-8977-592121975554/)
