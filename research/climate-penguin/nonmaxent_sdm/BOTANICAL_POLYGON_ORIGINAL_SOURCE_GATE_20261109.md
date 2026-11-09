# Botanical map overlap after original Landsat8 fixed-site yearly QA (2026-11-09)

**Post-spectral-result source qualification, NOT preregistration, and no tuning to reproduce positive NDVI.** The Landsat 8 original 50 breeding-site years, 150 site-scene reads (64 unique satellite scenes), 11,550 source sample pixels and 983 QA-valid red/NIR observations have been source-validated in CI. Three Dec–Feb seasonal NDVI pairs at two Victoria Land sites passed 6 fixed points and 2 dates/year; strict both-December QA retained only **Inexpressible Island 2018–2019, 13 fixed positions** (mean NDVI changed sign from +0.00184 to −0.02969 after matching month).

## One question

Do the **exact preselected original Landsat fixed geographic sample locations** that support one or more year-to-year comparisons lie **within** independently published mapped source polygons classified as `Vegetation` or `Lichen`, rather than only unclassified rock/snow/guano? This is an *image-source-class concordance* check, not an independent field survey, and a 2024 vegetation composite does **not** establish botanical state in 2017–2020.

## Original first-party vector source frozen

Reuse the already validated original Figshare **Plantarctica** publisher file, DOI **10.6084/m9.figshare.24745956**, `PlantarcticaVegetationMap.zip`, **SHA256 `7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236`**, **EPSG:3031**, expected **87,391 source polygons** (class codes `Vegetation` 58,740, `Lichen` 24,876, `Snow Algae` 3,775). Reuse `research/climate-penguin/work/climate_penguin/audit_palmer_plants_original_land_clip_v1.py` for official-source authentication/download/unpacking, not an unrelated mapping service.

- Two sites only: `CRZW` Cape Crozier west, `INEX` Inexpressible Island. Source centroids in `nonmaxent_sdm/outputs/contemporary_vegetation_site_species_197.csv` pinned against original Git SHA, not reselected after NDVI changes.
- Coordinates for every original site fixed Landsat sample point: EPSG:3031 center + the unchanged **77 EPSG:3031 offsets** from `acquire_original_landsat8_seasonal_spectra.py`. Read 150 scene QA artifact from successful [Action #42608609143](https://github.com/zuizui0223/mina/actions/runs/42608609143) (ID 13669078857). Recompute from original QA exactly: 3 summer-wide year pairs CRZW2017–18(6), CRZW2018–19(6), INEX2018–19(30); December-only INEX2018–19(13). If any count changes, do not interpret mapped-class overlap.
- Use point-in-source-polygon `covers`, no buffer, no nearest-positive-source or manual pixel shifting. Class code from original field `Vegetation`. Multiple overlapping class polygons can be separately recorded. `Snow Algae` is counted separately, **not as vascular plant/moss/lichen cover**.
- Report 2×77 fixed points by class, and mapped botanical match counts for the original 3 summer and 1 December source-support sets. Do **not** falsely multiply source botanical observations by years or species.
- Even if a point is classified as vegetation/lichen in the source **2024-era composite**, its botanical status in 2017–2020 is *not* independently measured. No point-in-polygon does **not** mean true vegetation absence; 400m fixed sample spacing can miss small patches, and Landsat 30m native pixels can overlap a polygon even when sample point does not.
- No added ecological p-values, MaxEnt refit, map interpolation, historical source imputation, or individual penguin migration inference. Do not merge into warming v0.6.

**Decision:** If fewer than six already strict month-matched points INEX are classified `Vegetation` or `Lichen` by the original static polygon, `BOTANICAL_SOURCE_SUPPORT_TOO_WEAK`. If six or more: `STATIC_PLANTARCTICA_CLASS_SUPPORT_ONLY` — still *not* verified temporal greening. Protect the original source with SHA verification and record full class counts and original projected geometries.
