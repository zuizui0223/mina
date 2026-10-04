# Remote-sensing method audit v1 — dynamic Antarctic breeding opportunity

**Status:** method rationale frozen before habitat-change outputs and before new demographic outcomes.

## 1. What the optical pipeline is allowed to measure

The dynamic-land program needs a repeatable measure of changing terrestrial breeding opportunity around fixed penguin breeding-site nodes.

The first optical target is deliberately narrower than "true nestable habitat":

> **summer exposure of independently mapped ice-free / rock substrate within the frozen 2 km site support.**

This can later be combined with topographic accessibility. It must not be relabeled as occupied nesting area.

## 2. Why scene availability is no longer the limiting issue

The outcome-blind STAC audit queried the public Microsoft Planetary Computer Landsat Collection 2 Level-2 archive around the frozen 107 Pygoscelis site × species units.

The catalog gate passed for 106/107 units (99.1%). The sole catalog failure was CHPE|HANN, where the early window had six <=80%-cloud scenes but only one distinct year, below the frozen two-year requirement.

After intersecting with the pre-existing 2 km Antarctic Ecosystem Inventory support, the next-stage roster contains 103 site × species units at 84 physical sites.

Thus the active uncertainty is local measurement validity, not gross archive coverage.

## 3. Landsat products

Primary archive: Landsat Collection 2 Level-2 (landsat-c2-l2) on Microsoft Planetary Computer.

Relevant common-name assets:

- green
- nir08
- swir16
- swir22
- qa_pixel

Collection 2 Level-2 is available from 1982 onward and the Planetary Computer stores imagery as cloud-optimized GeoTIFFs.

Surface-reflectance values are not assumed to be equally reliable at every Antarctic latitude. USGS cautions about high-latitude surface-reflectance use and low solar zenith constraints. Therefore Level-2 support is an initial route, not evidence that Level-1/TOA imagery is biologically unusable where Level-2 support fails.

## 4. Pixel quality mask

The observation-support gate uses QA_PIXEL, carried from Landsat Level-1 into the Level-2 product.

The primary valid-observation mask explicitly removes:

- fill (bit 0);
- dilated cloud (bit 1);
- high-confidence cloud (bit 3);
- high-confidence cloud shadow (bit 4).

Snow/ice (bit 5) and water (bit 7) are recorded diagnostically at this stage.

The pipeline does **not** rely on the QA_PIXEL "clear" bit alone. USGS documents a Collection 2 clear-bit discrepancy for Landsat 4–7 and recommends direct use of the cloud/dilated-cloud conditions.

## 5. Why NDSI is not the sole classifier

NDSI is physically relevant because snow is bright in the visible and dark in SWIR, whereas rock generally differs in that spectral contrast.

However, Antarctic-specific evaluations show that NDSI alone is unreliable for a continental automated rock mask because:

- shaded rock can be confused with snow;
- illuminated rock can be confused with cloud;
- the optimal NDSI threshold can vary substantially among scenes.

Burton-Johnson et al. (2016, *The Cryosphere* 10:1665–1677) therefore used a multispectral/thermal workflow rather than a single fixed NDSI threshold.

Consequence for mina:

> **NDSI may be a feature or sensitivity diagnostic, but a fixed NDSI threshold cannot be chosen as the primary dynamic-land classifier merely because it reproduces a desired ecological result.**

## 6. Fixed spatial support

The initial local QA uses the Antarctic Ecosystem Inventory v1.0 ice-free raster already frozen in the static breeding-options atlas.

That inventory was constructed from the union of independent Antarctic rock-outcrop layers and masked to a high-resolution SCAR Antarctic coastline.

Advantages:

- independent of penguin count outcomes;
- fixed before the dynamic-land question;
- already audited at the same 2 km site radius;
- limits cloud/visibility QA to places independently mapped as potential exposed ground.

Limitation:

The mask cannot discover deglaciated ground outside the union of mapped rock-outcrop support. Therefore the first dynamic quantity is **change in exposure of mapped potential rock**, not total new land created by glacier retreat everywhere.

A later total-deglaciation extension would require a separate coastline/grounded-land support and its own frozen validation.

## 7. External controls

### Beaufort Island

LaRue et al. (2013, PLoS ONE, doi:10.1371/journal.pone.0060568) documented increased nesting opportunity as ice and snow retreated at Beaufort Island using aerial photographs and high-resolution satellite imagery.

Because their source imagery was far finer than Landsat, the validation target is **direction**, not recovery of the exact published percentage change.

Before multi-site Landsat-derived habitat-change outputs are accepted:

- Beaufort must pass both local-pixel observation epochs;
- the final classifier must recover a positive direction of terrestrial opportunity change over the closest comparable historical-to-2010 window.

The published penguin abundance change at Beaufort is not used to tune the classifier.

### Antarctic Peninsula glacier retreat

Where candidate sites overlap independent mapped glacier-front change, retreat direction can be used as a second spatial QA. This remains auxiliary because coverage is not uniform across all sites.

## 8. Staged validation

1. **Catalog gate** — scene existence and temporal replication. PASSED.
2. **Local pixel gate** — clear observation of independently mapped potential rock. ACTIVE.
3. **Classifier gate** — rock/snow/ice classification validated without penguin demographic outcomes.
4. **Full 84-site extraction** — only after the pilot succeeds.
5. **Dynamic ecological model** — only after the habitat metric, roster and marine-support choice are frozen.

## 9. Current claim boundary

No current result says that ice-free breeding opportunity increased or decreased at any site.

No current result links terrestrial change to penguin population change.

The only present positive result is methodological: the long Landsat archive appears broad enough to make the dynamic-island hypothesis testable at the scene-catalog level.
