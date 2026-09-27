# Palmer colony crosswalk retrieval queue v1

Date: 2026-09-27

Purpose: retrieve independent spatial identity evidence before any
distance-conditioned demographic re-analysis. No demographic trajectory
similarity may be used to resolve aliases.

| Priority | Source / asset | What is already established | Required next evidence | Status |
| --- | --- | --- | --- | --- |
| P0 | Bird et al. 2020 Duke archive, DOI 10.7924/r4cv4jq6j | 2017 all-Torgersen UAS survey; final colony polygons; per-colony abundance/density; public archive | file manifest; polygon/shapefile/GDB fields; colony IDs; coordinate reference system | archive identified, file manifest not yet exposed through current web interface |
| P0 | USGS OFR 99-402 companion GIS | 1998/99 Palmer target-island mapping used GIS/GPS control; Torgersen TOR1 survey control documented | downloadable GIS layers / orthobases / colony perimeter attributes | report public; companion spatial assets not yet recovered |
| P0 | Cimino et al. 2025 supplement | 1998/99 historic Torgersen perimeters georeferenced/digitized; 2020 orthomosaic; 2022 GPS perimeter data | S3/S13 and any polygon identifier or centroid table | supplement known, identifier content not yet recovered |
| P1 | Sanchez & Fraser 2001 orthobases | Litchfield 6-cm orthobase + DTM is explicitly cited with ±2 m accuracy | locate Torgersen/Christine/Cormorant/Humble counterparts or archive inventory | existence partly documented |
| P1 | Patterson 2001/2003 historical maps | 23 historical Torgersen physical colonies; numbered sampling subset; aerial-photo colony map | explicit number-to-polygon key or source field map | partial mapping evidence recovered |
| P1 | Palmer LTER historical census maps/protocols | raw LTER colony_code is nominal and island-specific | source map or protocol linking nominal codes to physical colony footprints | not yet recovered |
| P2 | 2020 Palmer drone products | high-resolution Torgersen/Humble orthomosaic + DSM and GPS ground control documented | public data location and polygon identifiers | product existence documented |

## Stop rule

Do not run a distance-conditioned `same_island` model until the source-based
crosswalk gives:

1. at least two independently identified physical units on at least two islands;
2. coordinates or polygons sufficient for pairwise distance;
3. explicit coverage and unresolved-code summaries;
4. overlapping within-island and between-island distance ranges sufficient to
   separate distance from island membership.

If condition 4 fails, report that coastline/island membership is not separately
identifiable from distance in Palmer rather than fitting an extrapolative model.
