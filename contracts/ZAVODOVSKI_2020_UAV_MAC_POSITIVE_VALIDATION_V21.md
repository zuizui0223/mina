# V21 — Independent 2019/20 macaroni nest-point positive validation (frozen before opening point rows)

Date 2026-10-14. **2020 original coordinate data outcomes unopened at this freeze.** V10–V18 2011/2016 mapped outcomes are already exposed, so the analysis is exploratory conditional on that selection and should never be described as a confirmatory test of a newly chosen site.

## Original public source and provenance (V20 source gate succeeded)

- Hart, Manthorpe, Clucas & Lynch (2022), original 2019/20 UAV survey, UK Polar Data Centre DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b.
- Authentic public RAMADDA `Zavodovski/coordinates` folder includes `ZAVO_2020_Macaroni_coordinates.csv`, `ZAVO_2020_Mixed_species_coordinates.csv`, `ZAVO_2020_Unknown_pengiun_coordinates.csv` and separately `ZAVO_2022_Chinstrap_coordinates.csv`.
- Original `ZAVO_2020_Macaroni_coordinates.csv` and `ZAVO_2020_Mixed_species_coordinates.csv` first headers are both exactly `nest_number,lat,lon`, 0 biological rows read. Declared CSV bytes 19,476 and 559,088 respectively. There is no point-level timestamp, so interpret source season as 2019/20; do not imply exact-day observations.
- **Provenance red flag:** the separate 2022 chinstrap file is not contemporaneous with 2020 maca files and was used partly as 2020 imputation in original processing. **Never read or treat it as actual 2020 chinstrap presence or absence.** Mixed species point records are not confirmed maca.
- Original 2011 historic baseline CHPE 442, MCPE 18, MIXED 46. V18 positive-only mapped-concordance T=9,938.357 m² was calculated and fixed before looking at 2020 point rows.

## Frozen eligibility and original-record QA

1. Only two official **2020** files (maca species-confirmed and separately mixed category) fetched from authenticated RAMADDA source manifest on HTTPS. Validate file identity and SHA256, exact source header, row count within bounded source size (Maca <= 2 MB, MIXED <= 3 MB), no missing/nonnumeric lat/lon, original `nest_number` retained as source label (not assumed independent breeding attempts).
2. Interpret publisher `lat/lon` as degrees from GNSS in **WGS84 (EPSG:4326) only provisionally**; verify all coordinates fall within hard Zavodovski geographic window latitude **-56.34 to -56.26**, longitude **-27.66 to -27.50** and transform `(lon,lat)` via always_xy to EPSG:32726. Print source ranges and spatial-grid spread, fail closed rather than silently swap coordinates or drop unexpected rows.
3. Validate WGS84 coordinate scale by comparing to **independently sourced** 2023 BAS coastline (DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308; `zavodovski_coastline_2023` file). The baseline is not dated 2020; use as a *coarse georeference plausibility gate*, not 2020 coastline/habitat/census or biological absence. Report % points inside island polygon or within 150 m of its land geometry. If less than 90% of confirmed maca points fall on/near that geometry, STOP and inspect source CRS/registration; do not optimize shift to improve the metric.
4. Exact record duplicate coordinates are reported; do NOT turn a row count into a number of independent breeders and do not infer unsurveyed absence.
5. **No full-island 2020 coverage assumed**. Positive point records alone cannot test absence or a colonization probability.

## Positive-only preread endpoints

The already frozen V18 T area, for 2011→2016, requires 2011 CHPE in **both** source interpretations, excludes both 2011 maca and historic MIXED or MCPE, and is inside observed 2016 M gain with 2016 chinstrap absence on the mapped polygons. Its interior margins are `0,1,2,5` metres exactly as defined in V18 (shrink C2011 CHPE M2016; expand C2016 M2011 MCPE MIXED clouds; intersect original common direct-image support).

- (n_{2020,MAC}(T_{0,1,2,5})): number of genuine 2019/20 Macau-source point rows with centres strictly **within** each Tδ. Report also number of exact distinct coordinates and number of 5m and 10m grid cells to avoid pseudoreplication, with Tδ surface m² from the same original source geometry.
- (n_{2020,MIXED}(T_{0,1,2,5})): independent separate ambiguous mixed-record counts, never added to MAC-confirmed count.
- Positive control: `Q=(M2011∩M2016) ∩ same cloud-free support` and count positive macaroni records in this historically persistent zone. A zero or positive control failure is an observation support warning, not biological falsification.
- Additional source QA: fraction of each class's original points strictly within overall 2016 macaroni polygons, within the 2023 coastline land geometry, and within 100 m of all 2011/2016/2025 mapped penguin polygons (geometry alignment check only).
- Report **zero** findings as *no confirmed point observed in THIS source and mapped T*, not no species occupancy. Report **positive** hits as external georeferenced *2020 nest-location corroboration* of site use, conditional on publication and original imagery interpretation, not direct tracking of any original 2011 bird, direct competition, immigration, reproductive success or priority effect.

No model p values; no attempt at matched ecological habitat/availability inference. If georeference CRS, coastal plausibility, source year, or mixed-class labels are unverifiable -> scientific HOLD. Do not modify Ecology PR189.

References: BAS source DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b; original GIS baseline DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308; V18 receipt results/ZAVODOVSKI_CONCORDANT_HISTORICAL_C_TO_M_V18.json.
