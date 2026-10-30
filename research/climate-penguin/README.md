# Climate, sea ice and penguin breeding: exploratory progress

Research checkpoint, 2026-10-30. This directory is a draft research lane. It does not replace the frozen Paper 1 / Paper 2 analyses or establish publication readiness.

## Start here

- **[Latest integrated findings: correlations and conditional scenarios](outputs/research_synthesis_v1/RESEARCH_STATUS_JA.md)**: updated inference, salinity, annual NDVI, mapped vegetation support, tracking limits and remaining work. Earlier reports below are dated checkpoints.
- [Full correlation atlas](outputs/correlation_atlas_v1/REPORT_JA.md), [salinity sensitivity](outputs/salinity_sensitivity_v1/REPORT_JA.md), and [conditional response decomposition](outputs/scenario_components_v1/REPORT_JA.md).
- [Salinity site-deletion sensitivity](outputs/salinity_site_influence_v1/REPORT_JA.md): 48 fixed specifications and 656 deletion fits. Adelie retains positive direction after each camera deletion; previous year-deletion sensitivity still crosses zero.
- [Matched-period salinity scenario component](outputs/salinity_scenario_component_v1/REPORT_JA.md): 144 conditional salt-only summaries, with coefficient deletion sensitivity and extrapolation flags. Not a complete future response and not additive to the previous two-variable prediction.
- [Surface-temperature projections and period alignment](outputs/surface_temperature_projection_v1/REPORT_JA.md): nine additional public stores, 30,528 September values, same three model members and salinity cells. Widespread future extrapolation and the tos/top-level potential-temperature definition difference remain explicit.
- [Four-environment conditional scenarios](outputs/four_environment_scenarios_v1/REPORT_JA.md): 288 joint air/ice/salinity/water scenarios, component decomposition, coefficient deletion sensitivity and four-dimensional observational support. Model specification can reverse the direction; these are not calibrated breeding-date forecasts.
- [Observed predictor separation and extrapolation scale](outputs/environment_identifiability_v1/REPORT_JA.md): Adelie water-temperature VIF is about 1.1, but future changes are 8–34 times its conditional observed residual SD. Large projected components do not establish strong observed future responses.
- [Annual NDVI/count comparison](outputs/vegetation_annual_ndvi_v1/REPORT_JA.md), [mapped vegetation overlap](outputs/ndvi_vegetation_overlay_v1/REPORT_JA.md), and [Landsat support](outputs/landsat_vegetation_support_v1/REPORT_JA.md). NDVI differences are not validated vegetation changes.
- [Completed historical count association analysis](outputs/long_count_seaice_v1/REPORT_JA.md) and [timing support](outputs/long_ice_timing_v1/REPORT_JA.md): 1991–2020 sea-ice acquisition and the 301-interval association analysis are now available, superseding the acquisition-in-progress statements in the earlier checkpoints below.

- **[Earlier checkpoint: vegetation, sea ice, salinity and warming scenarios, 2026-10-30](CLIMATE_RELATIONSHIPS_AND_SCENARIOS_20261030.md):** same-cohort relationships on 169 species/site/seasons; vegetation associations on 246 site/species units; actual 3-model CMIP6 extraction at 106 coordinates. Future environmental changes are quantified; biological future responses remain uncalibrated.
- [Current research objective](outputs/climate_penguin/RESEARCH_GOAL_V2.md): correlation-first work across climate, sea ice, drift, ocean conditions and vegetation, leading to conditional future scenarios. Predictive performance and descriptive relationships are distinct questions.
- [September relationships and conditional historical prediction](outputs/relationship_response_v1/REPORT_JA.md): identical complete cases, between/within-site comparisons, and chronological evaluation using realized heldout-year environments at previously observed sites.
- [Vegetation and observed breeding counts](outputs/vegetation_response_v1/VEGETATION_RELATIONSHIPS_RESULTS_JA.md): 2017–2023 map/count period alignment, regional contrasts, detection sensitivity and species comparisons on common observed site/seasons.
- [CMIP6 future environments](outputs/cmip6_projection_v1/REPORT_JA.md): 27 actual store reads, 381,600 monthly point values, 1995–2014 baseline and two future periods under SSP2-4.5/SSP5-8.5. Three models, one member each; native-grid, uncorrected environmental projections.
- [Exploratory significance](outputs/climate_penguin/EXPLORATORY_SIGNIFICANCE_RESULTS_JA.md) and [wild-cluster sensitivity](outputs/climate_penguin/WILD_BOOTSTRAP_RESULTS_JA.md): 216 post-exploration comparisons. The initial approximate tests had 3 BY-adjusted candidates; none retained BH-adjusted significance in either one-way wild-cluster sensitivity. This is not evidence of no ecological relationship.
- [Year alignment](outputs/climate_penguin/ENVIRONMENT_YEAR_ALIGNMENT_JA.md): source October sea-ice covariates support the current season-start-year environmental join; individual camera dates and settlement calendar origin remain unresolved.
- [Offshore association analysis](outputs/climate_penguin/OFFSHORE_ASSOCIATION_RESULTS_JA.md) and [seasonal sea ice](outputs/climate_penguin/SEASONAL_ICE_RESULTS_JA.md).
- [NOAA tracking audit](outputs/climate_penguin/NOAA_TRACKING_AUDIT_JA.md): public raw tracks obtained, but winter coverage ends in August and cannot calibrate September–October return directions.
- [Satellite common support](outputs/climate_penguin/SATELLITE_MULTISCENE_RESULTS_JA.md): 106 coordinates screened; unequal observation opportunities and limited common clear land constrain vegetation comparisons.
- [Original-pixel reflectance validation](outputs/climate_penguin/REFLECTANCE_ORIGINAL_VALIDATION_JA.md): 28 sampled band comparisons resolve the offset convention for the selected 14 images. No vegetation trend has yet been estimated.
- [Matched-pixel NDVI comparison](outputs/climate_penguin/MATCHED_NDVI_RESULTS_JA.md): seven coordinates, identical clear-land pixels, dates matched within five days, and boundary-mask sensitivity. These are two-date spectral differences, not validated vegetation change or warming attribution.
- [Historical count support](outputs/climate_penguin/HISTORICAL_COUNT_SUPPORT_JA.md): the 1991–2020 scope has 301 eligible consecutive-year comparisons at 33 sites across six regions. The historical sea-ice series and count association analysis are now complete within the specified scope; see the updated links above.
- [Historical observation timing](outputs/climate_penguin/HISTORICAL_COUNT_TIMING_JA.md): 203 of the 301 comparisons have both counts confirmed after September, with stronger regional imbalance. The monthly aggregation pipeline reproduces all 3,200 existing 2011–2020 macro-site monthly SIC values; historical acquisition is now complete; see the updated timing and count analyses above.

## Scope and evidence limits

Settlement, nest counts, breeding success and migration behavior are distinct outcomes. Sea-ice concentration retreat is not necessarily physical melting. Directional drift near colonies is not an observed bird trajectory. Vegetation composites are not annual observations. All current environmental associations are exploratory; source-calendar uncertainties, small cluster counts and spatial/temporal dependence constrain inference. There is no validated future breeding-date projection in this checkpoint.

The broader goals remain open: migration-route identification, validated vegetation and breeding-patch measurements, and climate-scenario calibration; full-period count associations and conditional index scenarios have been delivered. No goal completion is claimed by this PR.

## Layout and reproducibility

The original workspace-relative layout is retained inside this directory:

- `work/`: analysis and acquisition scripts authored during this research.
- `outputs/`: reviewable reports, derived tables, source inventories, checks and compressed daily environmental extracts.
- `SNAPSHOT_MANIFEST.json`: the earlier synchronization snapshot, not a manifest of later additions. The latest synthesis inputs are listed in `outputs/research_synthesis_v1/current_evidence_manifest.csv`.

Python scripts usually resolve the analysis root from their file location. Run from this directory when a script uses relative paths. Requirements vary by task; used packages include Python 3.10, numpy, pandas, scipy, statsmodels, rasterio, pyproj, shapely, geopandas, xarray, netCDF4, zarr, fsspec, requests and Pillow. The inference checkpoint used statsmodels 0.14.6. Dependency locking and a single end-to-end runner are not yet provided.

Raw external caches are intentionally not copied: satellite rasters, large NetCDF downloads, downloaded source documents, and some upstream data. The reports/manifests identify sources, versions and hashes where collected. Acquisition scripts cover many, but not all, inputs; a fresh clone cannot yet reproduce every step without restoring or downloading those inputs. Do not interpret a successful syntax/hash check as end-to-end reproduction. Older reports preserve the chronology; the newest reports linked above supersede their earlier unresolved/negative status where explicitly noted. Some image links in archived reports refer to omitted local previews.

External data and derivatives retain their source-specific licenses and attribution requirements; the repository's code license does not relicense external data. See source inventories and cited data DOIs, including Zenodo settlement data, NOAA/NCEI, OSI SAF, Copernicus Marine and Plantarctica.

## Synchronization

This is the rolling progress PR. At meaningful milestones, update the existing branch, manifest and summary rather than opening a new PR for each analysis. Synchronization does not imply merge or publication. No automatic scheduled task or unattended push has been installed.

The original workspace's `work/climate_penguin/sync_progress_snapshot.py --checkout <checkout>` copies the scoped outputs and scripts into this directory without committing or pushing. It is an additive sync: deletions must be reviewed explicitly. Never run it with source and destination set to the same directory.
