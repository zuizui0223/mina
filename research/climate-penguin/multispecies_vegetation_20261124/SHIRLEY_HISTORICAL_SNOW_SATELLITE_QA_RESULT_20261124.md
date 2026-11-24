# Shirley Island historical snow/ice and satellite observation feasibility (2026-11-24)

Executed locally on the four pinned original source archives (colony EDS 1539, Plantarctica, Shirley DEM and contours/reliability); source SHA256 in preceding terrain receipt. DEM footprint 509084 m², 127271 cells. Historical snow/ice reliability mask from 2001 aerial images, 2005/06 colony labels, 2017–2023 optical plant map. Not contemporaneous observations.

| Spatial support | Mapped vegetation cover in historical snow/ice % | Outside mask % |
|---|---:|---:|
| Relic excluding extant, DEM-valid | 10.055106 | 1.008479 |
| Outside union of extant/relic/maximum polygons | 0.108995 | 0.706721 |
| Entire valid DEM footprint | 0.224194 | 0.678540 |

The outside-colony contrast remains negative or tied in all common-support 100m (16 blocks), 200m (17), 400m (8) blocks using native 20m fixed-grid area fractions. Many blocks have zero plant-map detection. Distance-band descriptive checks are in local package. Outside known polygons does not prove no historical animal occupation. Positive historical-ice × relic contrast is localized to one spatial group, does not identify an interaction, abandonment mechanism, nutrient source, or warming-driven change.

## Actual satellite source pilot

[Run 45355069761](https://github.com/zuizui0223/mina/actions/runs/45355069761), artifact 14901757362, SHA256 073388f3baf71fa43d72385bc2d595c3d22456c7f7e08e23f95732d6e13beaec. All 36 source native raster windows retrieved, 18 Sentinel-2 SCL and 18 Landsat8 QA_PIXEL. Fixed Jan/Feb 2018, 2021, 2023; up to three distinct days per month chosen from catalogue cloud metadata only. Original native grids, exact geometric intersection on DEM footprint; >=80% valid DEM footprint, >=80% pure historic status. Only one Sentinel-2 20m native pixel pure relic+historical ice, zero Landsat 30m. Require >=2 usable observations per month at same pixel; only 2018 has support. Do not estimate snow duration/thaw dates or vegetation trends.

On common usable area, SCL vs QA_PIXEL snow-class disagreement: 33.327% (2018-01-20), 53.642% (2018-01-27), zero (2021-01-19, common area only 6651.59 m²). Classifications are not ground truth.

## Same-day spectral diagnostic, targeted after discrepancy

[Run 45355520180](https://github.com/zuizui0223/mina/actions/runs/45355520180), artifact 14901618883, SHA256 6099fec524c7389091a88523ab81ec558f38fcea8cfe888469536e21ec3280de. Original four exact same item IDs with green/SWIR1 and Landsat QA_RADSAT retrieved. Sentinel B03 10m aggregated to B11 20m, N02.12 scale 1e-4. Landsat reflectance scale 0.0000275 offset -0.2. Exclude masked, saturated and negative values. Exact overlap native cells. Illustrative common spectral screen NDSI>=0.4 and green>=0.1, not calibrated snow detection.

| Day | Common spectral area m² | S2 QA snow % | L8 QA snow % | QA disagreement % | S2 screen % | L8 screen % | Screen disagreement % |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018-01-20 | 183826.8492 | 98.6944 | 64.9340 | 33.7604 | 41.3115 | 38.0830 | 19.4988 |
| 2018-01-27 | 213768.9462 | 100 | 46.3578 | 53.6422 | 30.4643 | 29.2543 | 11.8039 |

Acquisition times differ 23.887 and 7.379 minutes. Threshold .3/.5 sensitivities remain substantially lower discrepancy than QA. Common spectral threshold is diagnostic of method dependence, not truth or a validated time series. Stop retrospective thaw model until common acquisition and spatial support, reliable classification and biological validation.

Local delivered package shirley_snow_vegetation_20261124.zip SHA256 640b76e8e6057e04a029ff1c7cde103f375827e0e8e3df1e6a5ad8700e1f3b57. Contains four executed local analysis scripts, source receipts, native-cell/day observations, overlap tables, local sensitivity tables and independent numeric reaggregation validation. No original publisher archives redistributed. Acquisition scripts/workflows in branch. No change to main, frozen papers or original isotope results.
