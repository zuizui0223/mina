# Original East Antarctic Adélie repeated-colony GIS: independent V9–V13 source and biological interpretation

**2026-10-26 | original publisher GIS, not a synthesis of published effect sizes.** New result lane inside Draft PR #199. Frozen Ecology Article PR #189 unaffected.

## 1. Source acquisition and independently selected cohort

From the original Australian Antarctic Data Centre publisher dataset `AAS_4088_Adelie_breeding_colony_boundaries` (DOI 10.4225/15/58f59b52edfef), retrieved **33** original source-programme manifests containing **167** original `.shp` colony-boundary files. Original file path names unambiguously specify **138** individual `IS_<id>` group identities with **153** original site-year combinations. Only **13** sites are independently mapped in ≥2 surveyed years. The **28** original GIS layers for these 13 site identifiers were *source-frozen before opening the polygon geometry* in `contracts/AADC_REPEATED_COLONY_POLYGON_V10.md` and selected from `results/ANTARCTIC_SOURCE_BOUNDARY_MANIFEST_V9.json`.

Source repeat regions were **HBE (6 site IDs)** and **HBW (7 site IDs)**, both in the East Antarctic AADC published survey group. 12 source IDs appear in two seasons; site **IS_74585** appears in four (2012/2013/2015/2016). These are author site labels, NOT automatically 13 independent physical islands or two independent regions.

The 28 exact original GIS components were authenticated and downloaded from publisher public object URLs, original WKT CRS verified (including geographic WGS84 sources), projected to EPSG:3031, and **46** original polygon feature records read, **0** needed `make_valid` repairs. Full original source SHA256 receipts and original compact site-year/paired CSVs are in the source CI artifact of [V10 successful original GIS analysis](https://github.com/zuizui0223/mina/actions/runs/40257955794), receipt `results/AADC_REPEATED_ADELIE_COLONY_GIS_V10.json`.

## 2. Actual independently observed polygon change (post-source exploratory)

Across the **15** successive *observation* pairs (not necessarily consecutive calendar seasons):
- **13/15** later observed mapped colony footprints had less area;
- median **later/earlier mapped area = 0.451520**, p10=0.321554, p90=0.942533;
- median mapped polygon intersection/union **Jaccard = 0.403364**;
- HBE, n=8 paired observations: area ratio median **0.439087**, Jaccard **0.375160**;
- HBW, n=7: area ratio median **0.477826**, Jaccard **0.427170**.

These are **GIS colony footprint areas**, not direct number of breeding pairs, actual nest establishment, extinction or demographic migration. Source maps share the filename `2mbuff`; the mask/buffer precision and imaging effort may vary in time.

## 3. NEW source-derived spatial geometric result after accounting for area arithmetic

Jaccard falls mechanically when the mapped colony footprint shrinks. From the actual two-year polygon areas `A,B` and intersection `I`, define:
- maximum expected overlap given **perfect nesting**, `J_max = min(A,B)/max(A,B)`;
- observed **smaller-year footprint inclusion** `I/min(A,B)`;
- residual cartographic spatial mismatch `1-I/min(A,B)`.

Actual post-V10 diagnostics on **all 15** actual GIS comparisons:
- median smaller-footprint inclusion **0.846214** (84.6%; p10 60.4%, p90 95.8%);
- residual mismatch beyond area inequality **0.153786** (15.4%; p10 4.17%, p90 39.60%);
- site-ID-equal-weight descriptive summary for **13** unique IDs retained the **84.6% median**; the four-year site did NOT become three independent islands.
- HBE residual mismatch median 13.28%; HBW residual mismatch median 15.38%.

**Supported spatial description:** historical-to-recent mapped colony polygons changed markedly in mapped area, but the smaller of the two source footprints was commonly embedded within the larger. Earlier low Jaccard did **not** mean equally large physical relocation. This is an original GIS spatial reassembly metric. It is not independently established *individual nest-site fidelity*; original photography, 2-m source buffer, georeferencing, real accessible substrate and survey effort can generate or obscure this overlap.

Frozen after V10 result was observed; not pre-outcome confirmatory. V11 source-receipted [successful CI and GIS pair/site CSV](https://github.com/zuizui0223/mina/actions/runs/40258729220), machine-readable `results/AADC_ADELIE_COLONY_AREA_CONDITIONAL_OVERLAP_V11.json`.

## 4. Strict source-landmass identity attempt failed (important inference boundary)

Original `IS_<id>` colony mapping IDs were compared with the original **2025 AADC 7,785-site `geog_site_id` registry**. Actual V12 source audit: **0/13** source IDs matched, proving these different AADC programmes use **different identifiers**. No nearest-name/number join is justified; no claim that the 13 IS sites were absent from Antarctica. [V12 original publisher check](https://github.com/zuizui0223/mina/actions/runs/40259154543), receipt `results/AADC_REPEATED_SITE_ID_NAMESPACE_V12.json`.

V13 therefore used **the original colony GIS polygon union's own EPSG:3031 spatial bounding rectangle**, not the AADC 2025 site registry, and matched to the unchanged source-hashed SCAR ADD v7.12 high-resolution land polygons. **0/28** bounding rectangles were *fully* contained within exactly one parent SCAR land feature; **20/28** had a centre-point-only potential match and **8/28** lacked even a single centre-parent match. **0/13** original IS sites achieved complete multi-year stable strict full-rectangle physical landmass identity.

That is a deliberately conservative **source-boundary match HOLD**, NOT evidence that the original colonies occurred in ocean, that all 13 sites are on one physical island, or that Antarctic island effects are false. Rectangular envelopes are stricter than actual convoluted polygon footprints, and 2m-buffered colony polygons may overlap source coastline geometry due survey digitization and edition differences. No tolerance was tuned to reclassify them. [V13 successful source QA](https://github.com/zuizui0223/mina/actions/runs/40259590992), `results/AADC_REPEATED_COLONY_LAND_SOURCE_BOUNDARY_V13.json`.

## 5. Island biogeographic consequence and next original source need

**This original AADC source supports within-source-site mapped footprint contraction-with-nesting, not an Antarctic-wide biological law of island-mediated colonisation, competition, ice-gap connectivity or movement.** HBE/HBW are not verified independent physical islands; repeated observation geography is restricted; no independent historical surveyed absence or complete equal-footprint survey masks have been demonstrated.

Do not fit an island-level predictor, an across-island source comparison, dispersal ABM or biodiversity regression to these 13 IDs by pretending these cartographic geometries are population counts or 13 independent islands. Any next confirmatory biology requires independently documented original physical-island IDs/nesting substrate and consistent full coverage with repeated field nest counts across multiple regions. Prefer a truly independent observation programme and original georeferenced survey polygons, not another post-hoc buffer around already-opened GIS endpoints.

Original data terms: public AADC sources are CC BY 4.0; before scientific publication respect the accompanying AAD Seabird Conservation Team data sharing and acknowledgement statement. No publication release has been asserted.
