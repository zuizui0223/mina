# Palmer historical-footprint source recovery and pixel-resolution gate

2026-10-29. **Executed cartographic geometry diagnostic; no vegetation effect estimated.** Existing climate, Paper 1, Paper 2 and seabird analyses are unchanged. This is a continuation of the registered-point/old-colony mismatch, not a new biological endpoint.

## 1. New original sources recovered

Original-source Actions run **40876949180**, artifact **12898506622**, archive SHA256 `8b9acb397bc158178b0befcab0dcc8c0ce2dedb14003072840696a6dde9f6167`. All three requested responses were retrieved successfully, with the four existing source-payload tests passing.

- **2004 ASPA113 management plan**, https://documents.ats.aq/recatt/att210_e.pdf ; PDF SHA256 `362ab29c53493834af3db497ea5eefe3dcf8b07e566813c5a4141c75504c8e35`. The final map (PDF p21) predates the monitored 2007 disappearance and places small penguin-colony patches on eastern Litchfield. It is not an independent survey of the 2009-map shapes; shared source lineage is likely. Map year is not an exact per-polygon survey date.
- **Sanchez 1999 USGS Open-File Report 99-402**, https://pubs.usgs.gov/of/1999/0402/report.pdf ; SHA256 `f28ccde28f06bc6a90d4ea549ecdce49dc5bf5f2759bf971996708f5eef85db3`. Its original habitat-GIS description (PDF pp5-6) includes species/type, **active/original/extinct status, colony number, date collected, area and perimeter**. These are the right fields to connect counts to historical footprints, but the actual GIS layer was not downloaded. December 1998 aerial imagery and January 1999 ground controls are described (PDF pp4-6). The LIT1 appendix identifies ITRF96/GRS80 and the original monument coordinates (PDF pp14/22); no epoch-specific datum transformation for map-derived polygons is established here.
- **Duke dataset DataCite metadata**, https://api.datacite.org/dois/10.7924/r4sf2xs2w ; SHA256 `f9e40c5cb96ec98e7a770916fcf1d1ff6ce01c04a55e8a6558dbced3828130ab`. The record describes 2019/2020 imagery with 1.5-3 cm ground sampling and RGB without spectral calibration. Raw orthomosaics remain **not acquired** and Litchfield coverage is not certified by this metadata.

**Specific newly identified high-resolution historical target:** the 2004 plan's bibliography (PDF p19) cites **Sanchez & Fraser (2001), Litchfield Island Orthobase**, a **6 cm-pixel** digital orthophotograph, horizontal/vertical base-map accuracy stated as **±2 m**, delivered on **CD-ROM** with USGS99-402. This identifies a concrete pre-abandonment source rather than a generic request for better imagery. The embedded low-resolution management-plan raster is NOT this original orthobase. Pixel size is not positioning accuracy; ±2 m is not a verified accuracy bound on every derived nesting outline. The original CD-ROM imagery/GIS is still missing.

The downloaded PDFs were rendered and their relevant maps/tables visually inspected; no OCR was used. Remote web PDF screenshot access failed, so the SHA-pinned original PDFs retrieved through Actions were inspected locally.

## 2. Executed map-geometry exclusion

Source maps: 2009-02-06 Litchfield ERA map (SHA `4df88154c34fbb41b278e6d0543b37caad7c2dcaa080c57392aa9d4ce1a256a2`) and 2008-12-11 Torgersen ERA map (SHA `89e2af9b2708e8eba05d0a5a46fcb34b6ca1ec763d57883cae91d40fb75aef6f`). Closed perimeter strokes were visually identified against the penguin-colony legend; hatch strokes, contours, shorelines and symbols were excluded. The original Litchfield 10 candidates were preserved. Torgersen supplied 28 cartographic polygons and 16 graticule intersections. Its internal fit RMSE is 0.0697 m, **not field georeferencing accuracy**.

A full square pixel of side s necessarily contains an inscribed disk of radius s/2. If the polygon cannot contain that disk, no square of that size can fit wholly inside it at any rotation or grid phase. Maximum inscribed circles were computed with Shapely 2.1.2 at 0.001 m numerical tolerance. **Passing this necessary condition does not prove a fitting square, an actual clear native pixel, or an unmixed sensor response.**

| Source map | Drawn polygons | Excluded for a full 10 m square | Excluded for a full 30 m square | Largest inscribed-disk diameter |
|---|---:|---:|---:|---:|
| Litchfield | 10 | **10/10** | **10/10** | 8.325 m |
| Torgersen | 28 | **23/28** | **28/28** | 18.958 m |

Mapped areas are approximately 9.68-114.97 m² in Litchfield and 15.80-910.07 m² in Torgersen. Area alone would be misleading: a narrow polygon larger than a pixel area can still exclude every full square pixel. Source drawing indices **43,151,281,306,379** are the five Torgersen shapes *not excluded* for 10 m; these are provisional candidates only.

**Important non-equivalences:** 28 Torgersen drawing objects are not automatically the 23 historical census subcolonies in Cimino et al.2025. The five remaining geometry candidates are NOT identified as the five colonies active in 2022. These maps do not supply each patch's abandonment year or a census-code crosswalk. They also do not establish that the drawn outlines capture all historical occupancy.

## 3. What changes in the research

- Correcting the sampling position alone cannot make ordinary 30 m Landsat pixels isolate these mapped nesting patches from the surrounding ground. The conditional geometry excludes all 38 candidate shapes. The ten Litchfield shapes also fail at 10 m.
- Do not re-run the old positive/negative NDVI contrast at a new centroid and call it a historical-colony vegetation response. An enlarged buffer would estimate the colony *neighborhood*, including new substrates and disturbance, rather than the old nesting patch.
- Retain the five Torgersen map shapes as unresolved 10 m geometry candidates, but do not choose them based on greenness. Verify exact census IDs, survey dates, footprint generalization, image registration and native-grid support first.
- The direct route to the original question is now explicit: **1998-era imagery/2001 Orthobase plus the original dated colony GIS**, linked to later high-resolution imagery and matched never-occupied controls. Availability of the document or metadata is not acquisition of the underlying imagery. Seal disturbance and snow history remain competing explanations.
- A subpixel/aggregate model would be a different estimand requiring calibration; the current geometry diagnostic does not claim that all remote-sensing approaches are impossible.

## 4. Reproducibility and honest verification scope

New code: `work/abandonment/palmer_map_resolution.py`; six dedicated tests: `tests/test_palmer_map_resolution.py`. Tests were written first (six expected missing-implementation failures) and then all six passed locally. A fresh local replay from both SHA-pinned source PDFs reproduced the entire geometry result JSON exactly. Local versions: PyMuPDF1.26.7, numpy2.3.5, pyproj3.7.2, Shapely2.1.2. Numerical geometry tolerances are not ecological or map-position uncertainty.

A dedicated workflow `.github/workflows/palmer-map-pixel-resolution.yml` installs the optional geospatial dependencies, runs the full repository pytest suite, fetches the two original maps, reconstructs both geometries and verifies counts/areas against the stored local result. **Its actual run conclusion must be checked separately; this document does not pre-claim CI success.** Core numpy-only CI can skip the optional geometry tests and is not their verification.

Generated outputs: `resolution_gate_result.json`, `map_pixel_resolution.csv` (76 polygon×pixel-size rows), `torgersen_map_candidates.geojson`, `torgersen_map_controls.csv`; compact pinned result `MAP_PIXEL_RESOLUTION_RESULT_20261029.json`. No annual vegetation series, event-time treatment effect, guano-source measurement, or macroecological replication has been produced by this step.
