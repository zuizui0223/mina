# V20 — Independent 2019/20 UAV nest coordinate source gate

Date: 2026-10-14. **New independent source family; pre-2020-row gate**, while 2011/2016/2025 mapped outcomes are already exposed. Stand-alone exploratory validation, no adjustment to Ecology PR189.

## Directly verified original publisher data (before reading coordinate/observation rows)

Hart, Manthorpe, Clucas & Lynch (2022), *Structure-from-motion-generated imagery, nest location coordinates and counts for Adelie, chinstrap, gentoo and macaroni penguins on the South Sandwich Islands, 2019–2020*, DOI: [10.5285/28222725-c53d-40f4-9350-49c368899f0b](https://doi.org/10.5285/28222725-c53d-40f4-9350-49c368899f0b). Its live official RAMADDA listing:
- Root entry `28222725-c53d-40f4-9350-49c368899f0b`;
- `Zavodovski/coordinates` folder `synth:28222725-c53d-40f4-9350-49c368899f0b:L1phdm9kb3Zza2kvY29vcmRpbmF0ZXM=`;
- Source files `ZAVO_2020_Macaroni_coordinates.csv`, `ZAVO_2020_Mixed_species_coordinates.csv`, `ZAVO_2020_Unknown_pengiun_coordinates.csv`, **`ZAVO_2022_Chinstrap_coordinates.csv`**, plus colony-outlines CSVs.

Publisher states the 2022 partial Zavodovski flight was used to distinguish chinstrap nests and substitute an estimate for 2020; therefore **do not claim simultaneous species-specific 2020 nest points from the 2022 Chinstrap file**. 2019/20 survey was spatially incomplete/distorted. The 'mixed' category denotes uncertain individual species; do not allocate it to maca or chinstrap. Original 2020 macaroni coordinate source could independently *confirm maca presence* at independently mapped 2011 pure-chinstrap places, but **cannot establish maca absence** at any unsampled location, displacement, dispersal direction, or complete 2020 occupancy.

## Hard source-first read envelope

- Fetch exact publisher-file `ZAVO_2020_Macaroni_coordinates.csv` and optionally `ZAVO_2020_Mixed_species_coordinates.csv` only for **first actual CSV header**. Read up to 40 source comment/blank lines within 4096 bytes before that line; **zero biological or location rows**.
- Strictly report names of coordinate/CRS/date/site provenance columns, original CSV header SHA256 and size. No dynamic guessed columns treated as valid coordinates. Source schema may have naked Easting/Northing, Lon/Lat or other coordinate fields. Confirm units and EPSG before any post-source row-level spatial test.
- Inspect original metadata, orthomosaic/DEM **file listing only** for an independent 2020 Zavodovski coverage footprint. Avoid downloading huge imagery or treating it as publicly available complete coverage just because a file is listed.
- If coordinate frame or 2020-vs-2022 provenance cannot be resolved, STOP.

## Independent observation question once support permits

Define **positive-only external validation** of already-observed V18 T=9,938.36 m²: how many independently dated Jan–Feb 2020 **macaroni nest** coordinate records map inside 2011 consensus CHPE / 2016 novel M co-location site? Evaluate 0/1/2/5 m polygon margin sensitivity for the V18 T core, fixing core definitions **before 2020 point rows**. Declare support if at least one validated point falls in a 2011-consensus historic CHPE territory and later mapped 2016 maca space, with QC of duplicates/record semantics; do **not** infer site-level absence or compute a settlement rate. More robust observational positive prediction: 2020 nests in T with count and nearest-to-boundary distribution, compared with a 2016 **already-established maca** polygon positive control (`M2011∩M2016`), all within verified UAV surveyed footprint, if such footprint is available. Distinct counts of 2020 mixed and unknown sites are not species-verified maca.

This source could add genuinely independent observational timing to the 2011/2016 map association, but even successful confirmation wouldn't identify competition, island carrying capacity, historical site-quality effect or founder recruitment.

No 2020 nest biological coordinate rows opened or outcome fitted at freeze.
