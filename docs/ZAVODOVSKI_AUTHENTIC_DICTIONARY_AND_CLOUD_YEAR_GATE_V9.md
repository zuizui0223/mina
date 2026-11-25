# V9 — First original source dictionary read and year provenance (2026-10-13)

**Breakthrough: authentic BAS original `layer_descriptions.csv` was directly obtained**, not inferred from publisher abstract. The exact 28-row dictionary has been archived under `sources/bas_zavodovski_layer_descriptions_v1.csv` without opening any biological shape rows. Original file GET URL derived from the RAMADDA official `output=default.csv` listing: https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=7220dc6b-2f52-4160-a6c0-e57c50963308&output=default.csv .

## Independent acquisition dates and provenance

| Published folder | Authentically observed image | Main direct species layers | Cloud mask | Temporal qualifier |
| --- | --- | --- | --- | --- |
| 2011 | 2011-01-08, WorldView-2 35cm | chinstrap_colony_boundaries_2011; macaroni_colony_boundaries_2011 | cloud_cover_2011 | Separately published macaroni_colony_boundaries_under_cloud_2011 uses 2010-12-09 and 2011-03-04; exclude |
| 2016 | 2016-01-09, WorldView-2 50cm | chinstrap_colony_boundaries_2016; macaroni_colony_boundaries_2016 | cloud_cover_2016 | Both species have separate *_under_cloud_2016 layers derived from **2020-02-04**; exclude them absolutely |
| 2020–22 | 2020-02-04; 2022-01-21 and 2022-02-04 | two **composite 2020–22** species layers | cloud_cover_2020, cloud_cover_Jan_2022, cloud_cover_Feb_2022 | Do not treat as a 2020→2022 time series or claim per-feature acquisition dates |
| 2025 | 2025-01-12, Airbus Pleiades 30cm | chinstrap_colony_boundaries_2025; macaroni_colony_boundaries_2025 | cloud_cover_2025 | single-date imagery; exclude clouds; no documented replacement layer |

Additional source feature: 2023 drone boundaries are genuine **2023-12-14**; the file `chinstrap_outwith_drone_area_2025` is **2025**, not 2023, and the `area_outwith_drone_survey_2023` delineates the survey gap. Do not silently mix drone/2025 unsurveyed areas or treat 2023 as comparable without masking.

## Actually confirmed archive accessibility

Through RAMADDA `output=default.csv` on the parent and satellite folders, verified **explicit per-file** .shp, .shx, .dbf, .prj, .cpg entries for each 2011, 2016 and 2025 original-date species layer and cloud-cover layer. This resolves the previous belief that original archive download URLs were not discoverable. It does **not** yet mean that those binary files have been downloaded or that their geometry validity, CRS, coordinate alignment, or temporal support has passed.

## Revised admissible test

Use main `chinstrap_colony_boundaries_YEAR` and `macaroni_colony_boundaries_YEAR` for years 2011, 2016, 2025, after masking the union of both dates' **observed cloud-cover polygons** for each pair. Exclude all `*_under_cloud_*` and 2020–22 composite layers, even if including them produces a more exciting effect. Work in EPSG:32726, verify source SHA256, shapefile sidecars, polygon validity, and geographic congruence. Further survey-footprint gaps and spatial registration remain limitations. Report any detected exchange strictly as **apparent breeding-boundary overlay**, not dispersal, successful recruitment, or causal species displacement.

**Biological values exposed at V9: none.** The code and windows remain prospective relative to raw GIS features, but not relative to already published island-wide species trends.

Official source DOI: 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308. Original dataset carries Open Government Licence 3.0.
