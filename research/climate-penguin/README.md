# Climate, sea ice and penguin breeding: exploratory progress

Research checkpoint, 2026-10-29. This directory is a draft research lane. It does not replace the frozen Paper 1 / Paper 2 analyses or establish publication readiness.

## Start here

- [Current research objective](outputs/climate_penguin/RESEARCH_GOAL_V2.md): correlation-first work across climate, sea ice, drift, ocean conditions and vegetation; future scenarios remain a later objective.
- [Exploratory significance](outputs/climate_penguin/EXPLORATORY_SIGNIFICANCE_RESULTS_JA.md) and [wild-cluster sensitivity](outputs/climate_penguin/WILD_BOOTSTRAP_RESULTS_JA.md): 216 post-exploration comparisons. The initial approximate tests had 3 BY-adjusted candidates; none retained BH-adjusted significance in either one-way wild-cluster sensitivity. This is not evidence of no ecological relationship.
- [Year alignment](outputs/climate_penguin/ENVIRONMENT_YEAR_ALIGNMENT_JA.md): source October sea-ice covariates support the current season-start-year environmental join; individual camera dates and settlement calendar origin remain unresolved.
- [Offshore association analysis](outputs/climate_penguin/OFFSHORE_ASSOCIATION_RESULTS_JA.md) and [seasonal sea ice](outputs/climate_penguin/SEASONAL_ICE_RESULTS_JA.md).
- [NOAA tracking audit](outputs/climate_penguin/NOAA_TRACKING_AUDIT_JA.md): public raw tracks obtained, but winter coverage ends in August and cannot calibrate September–October return directions.
- [Satellite common support](outputs/climate_penguin/SATELLITE_MULTISCENE_RESULTS_JA.md): 106 coordinates screened; unequal observation opportunities and limited common clear land constrain vegetation comparisons.
- [Original-pixel reflectance validation](outputs/climate_penguin/REFLECTANCE_ORIGINAL_VALIDATION_JA.md): 28 sampled band comparisons resolve the offset convention for the selected 14 images. No vegetation trend has yet been estimated.
- [Matched-pixel NDVI comparison](outputs/climate_penguin/MATCHED_NDVI_RESULTS_JA.md): seven coordinates, identical clear-land pixels, dates matched within five days, and boundary-mask sensitivity. These are two-date spectral differences, not validated vegetation change or warming attribution.
- [Historical count support](outputs/climate_penguin/HISTORICAL_COUNT_SUPPORT_JA.md): the 1991–2020 scope has 301 eligible consecutive-year comparisons at 33 sites across six regions. Historical sea-ice acquisition is in progress; the incomplete live manifest is excluded from this checkpoint.
- [Historical observation timing](outputs/climate_penguin/HISTORICAL_COUNT_TIMING_JA.md): 203 of the 301 comparisons have both counts confirmed after September, with stronger regional imbalance. The monthly aggregation pipeline reproduces all 3,200 existing 2011–2020 macro-site monthly SIC values; historical acquisition is not yet complete.

## Scope and evidence limits

Settlement, nest counts, breeding success and migration behavior are distinct outcomes. Sea-ice concentration retreat is not necessarily physical melting. Directional drift near colonies is not an observed bird trajectory. Vegetation composites are not annual observations. All current environmental associations are exploratory; source-calendar uncertainties, small cluster counts and spatial/temporal dependence constrain inference. There is no validated future breeding-date projection in this checkpoint.

The broader goals remain open: migration-route calibration, full-period count analyses, vegetation and breeding-patch extraction, annual vegetation support, and climate-scenario transfer with uncertainty. No goal completion is claimed by this PR.

## Layout and reproducibility

The original workspace-relative layout is retained inside this directory:

- `work/`: analysis and acquisition scripts authored during this research.
- `outputs/`: reviewable reports, derived tables, source inventories, checks and compressed daily environmental extracts.
- `SNAPSHOT_MANIFEST.json`: byte sizes and SHA256 for synchronized files.

Python scripts usually resolve the analysis root from their file location. Run from this directory when a script uses relative paths. Requirements vary by task; used packages include Python 3.10, numpy, pandas, scipy, statsmodels, rasterio, pyproj, shapely, geopandas, xarray, netCDF4, zarr, fsspec, requests and Pillow. The inference checkpoint used statsmodels 0.14.6. Dependency locking and a single end-to-end runner are not yet provided.

Raw external caches are intentionally not copied: satellite rasters, large NetCDF downloads, downloaded source documents, and some upstream data. The reports/manifests identify sources, versions and hashes where collected. Acquisition scripts cover many, but not all, inputs; a fresh clone cannot yet reproduce every step without restoring or downloading those inputs. Do not interpret a successful syntax/hash check as end-to-end reproduction. Older reports preserve the chronology; the newest reports linked above supersede their earlier unresolved/negative status where explicitly noted. Some image links in archived reports refer to omitted local previews.

External data and derivatives retain their source-specific licenses and attribution requirements; the repository's code license does not relicense external data. See source inventories and cited data DOIs, including Zenodo settlement data, NOAA/NCEI, OSI SAF, Copernicus Marine and Plantarctica.

## Synchronization

This is the rolling progress PR. At meaningful milestones, update the existing branch, manifest and summary rather than opening a new PR for each analysis. Synchronization does not imply merge or publication. No automatic scheduled task or unattended push has been installed.

The original workspace's `work/climate_penguin/sync_progress_snapshot.py --checkout <checkout>` copies the scoped outputs and scripts into this directory without committing or pushing. It is an additive sync: deletions must be reviewed explicitly. Never run it with source and destination set to the same directory.
