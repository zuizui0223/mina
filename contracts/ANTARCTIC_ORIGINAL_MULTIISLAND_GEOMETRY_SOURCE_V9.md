# Independent colony-polygon macro source campaign V9 (2026-10-26)

## Main ecological advance — independently reconstructed colony spatial changes

**Question**: when Antarctic breeding populations contract or expand, does the occupancy and location of *observed breeding patches* respond to connected breeding-substrate topology within physical landmasses, beyond local colony abundance? Compare multiple independent physical islands / mainland rock exposures before attempting any species/flight-ability interaction.

This is an independent original *polygon/point observation database* effort, NOT a re-analysis of published effect-size tables, nor another fit of AADC 2025 P/A site-centre records. Earlier `mina` PR #199 V1–V8 original physical geography and its source-georeference mismatch must be respected. Frozen Ecology PR #189 untouched.

### Priority A — East Antarctic multi-season Adélie colony outlines
- Publisher: Australian Antarctic Data Centre (AADC), Southwell & Emmerson.
- Original primary metadata ID: `AAS_4088_Adelie_breeding_colony_boundaries`.
- DOI: **10.4225/15/58f59b52edfef**.
- Source-declared region approximately **65–70° S, 60–140° E**; temporal coverage **1981–2017**.
- Published **many separate group-season child records**, including Vestfold 2009/2011/2012, Rookery 2013/2014/2015, Robinson 2006/2013, etc. Those descriptions are NOT proof of source-compatible same-site time series.
- A distinct original island/site ID is expected in directory names (source example `IS_72276`), with source-group and observation season. Original boundary method ranges from ground/GPS to orthorectified aerial photography; original spatial errors must be retained by stratum. A mapped absence cannot be inferred from a missing boundary file; a non-photographed site cannot be treated as vacant.
- AADC metadata: https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_breeding_colony_boundaries . Original source reuse under CC BY 4.0, plus published Seabird Conservation Team Data Sharing Policy / acknowledgement conditions. Do not bypass access restrictions if actual file objects require permission.

### Priority B — South Sandwich multi-island 2019–2020 UAV individual nests
- Publisher: NERC/UK Polar Data Centre / BAS, Hart et al. (2022).
- DOI **10.5285/28222725-c53d-40f4-9350-49c368899f0b**.
- At least **31 publisher CSV objects** and **127 TIFFs**, across documented South Sandwich sites; published site names include Zavodovski, Ashen Hills, Herd/Hewison, Beach Point, Bellingshausen and Candlemas. Group by *verified physical island*, not by original survey-location name.
- Species source labels reported include Adélie, chinstrap, gentoo, macaroni; MIXED and UNKNOWN are *not* arbitrarily assigned to single species.
- **Important source exception:** the original *2022 resurvey* used to estimate some 2020 Zavodovski chinstrap nests is NOT independent 2020 contemporaneous observation. Keep such original nest CSV data in an imputation/quarantined lineage tier. Estimates from distorted orthomosaics are not GPS-observed nest locations.
- Multiple islands in one austral season are a **cross-sectional community geometry** test, NOT a spatial turnover time series. South Sandwich Islands lie mostly *north of 60° S*, thus they are a **sub-Antarctic island analogue** and may not be counted among Antarctic Treaty-area geographic replicates.
- Public source with no access constraints, Open Government Licence v3: https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01556 .
- Prior PR #196 accessed 2020 ZAVO macaroni and mixed coordinates, but NOT the full six-locality source roster. These ZAVO points must not be double-counted as another independent publication or species sample.

### Stage 1: primary-publisher file inventory only (this PR)
- Retrieve original AADC public dataset registry through the verified `/eds/api/dataset?size=10000` endpoint and find `metadata_entry_id` matches `AAS_4088_...`, and original object manifests when present.
- Independently enumerate the official BAS RAMADDA directory/file manifest recursively from the DOI UUID, following **publisher-host-only** links and bounded document manifests (no UAV TIFF payloads).
- Receipt contains actual official original source paths, extension/type, sizes/edition/DOIs, counts by source region/year when possible. **Zero penguin records or polygon geometry rows opened**.
- A registry or API that does not expose source objects is ACCESS_HOLD, not 0 colonies.
- Do NOT replace verified absent API registry entries with invented `eds_id`, anonymous mirror download URLs, or paper summary tables.

### Stage 2: source data eligibility
- Parse only public original lightweight GIS polygon sidecars / census CSV after retaining the original file path, publisher SHA256, original source year/date, source spatial group and island/site lineage.
- Confirm geometrical coordinate reference, original survey type, scanned/photo footprint, age of image, count stage, extant colony boundary versus surveyed unoccupied polygon, and any masked/substituted/cloud region.
- Repeated *same physical island* polygon overlap is eligible only where **same true site** and **repeated independent observed acquisition dates** and comparable coverage have been verified.
- Species/time/island counts must show enough independent site-year transitions and physical island groups *before opening the spatial displacement estimands*. Otherwise STOP and preserve raw sources.

### Macro model only after sample gate
- Within-land breeding patch persistence/rescue and across-land recolonisation compete as two mechanisms; model within-island restructuring conditional on environmental rock/icefree surface and proper survey controls, with distinct geographical island IDs.
- Only support a transferable Antarctic island-ecology law if several truly independent islands/regions and source methods corroborate it. A single Zavodovski polygon series, 2019–20 cross-sectional map, or already-published colony boundary change cannot establish new Antarctic generality.

## Strict receipt status at creation
BAS and AADC dataset *metadata existence* verified. **Actual original 1981–2017 multi-season polygon manifest, and multi-island 31 original CSV object list are NOT YET VERIFIED**. Do not print sampled biological results until the original inventory runs.
