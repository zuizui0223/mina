# Ardley monitoring map: independent shoreline registration gate (2026-11-24)

Executed locally after the public-source workflow commit 54cff033d228a360d53aa707c7c46f013fdbeecf. No plant overlap, animal-use transition area or climate effect fitted. Main and previous research results unchanged.

## Exact source evidence
- UBA TEXTE 63/2025, Braun, Grämer & Peter, DOI 10.60810/openumwelt-7664, figure 6, printed p.62. Original verified figure artifact 14919110826, run 45390508988, SHA256 81e03fddcbe2f9d16df37d9f3f226b0a58946498d5ccd56aa119bd91b87813e5.
- SCAR ADD v7.13, DOI 10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb, high-resolution polygon feature-service official bbox subset -59.00,-62.24,-58.88,-62.18; 53 features, EPSG:32721, no geometry simplification; source run 45394326684, artifact 14920057284, SHA256 6a5a23efd984d96cd62b5566760fee79e5f98eac7d386e26b87719d7a8a507f6; GeoJSON SHA256 2b1e3d8ea0bd4c1b6bbab3c84d06d2487a565261b298ce020ec3845ee4f9a191. Ardley FID 13516 valid land polygon (1,191,879.56 m2).
- Fit similarity transform only to visible shoreline traces (north 165 points, east 142, south 129, west-north 122). Fixed nominal scale 250/189 m/pixel; offset start [399130,3101024] UTM21S; robust least squares, translation ±90m, rotation ±5°, relative scale ±3%. Four leave-one-shoreline-segment-out fits, plus all-shoreline diagnostic. No plant symbols or breeding group symbols used in fit. These are nearest coastline distances, not surveyed point-coordinate errors.

| Held-out segment | Median m | P90 m | RMSE m |
|---|---:|---:|---:|
| east | 5.35 |22.73|11.67|
| north |16.81|28.37|18.68|
| south |25.75|34.86|26.31|
| west_north |11.99|19.23|13.17|

All-coast fit dx=12.5432639m, dy=6.9391008m, rotation=-1.0252982°, scale fraction=-0.0244459. Primary acceptance requires EVERY held-out median <=20m and P90 <=40m. **FAIL**, southern median 25.7527176m. One leave-segment-out fit hits lower scale constraint. Coast definition, geometry generalization, differing survey dates or map distortion may explain residuals. Not grounds to relax gate or infer exact location of historical polygons.

## Post-fit uncertainty diagnostic
At each image pixel inside seven disjoint zone interiors, compute maximum pairwise coordinate separation across all five fitted transforms. Median of that separation (m): zones 1–7 respectively 22.38,18.97,24.09,21.01,24.42,28.14,27.11. Zone 7 P90 31.09m, maximum 33.05m; zone 4 P90 23.51m. This is model disagreement, not a positional uncertainty confidence bound. Calculation reproduced against the original output CSV. Not an alternate acceptance gate. No plant data opened in this analysis.

## Source retrieval decision
2013–18 open drone vector archive 10.5281/zenodo.14503437 does not include 2023/24. Original monitoring report attributes current aerial imagery to Uruguayan scientists; public Instituto Antártico Uruguayo environmental monitoring programme (https://iau.gub.uy/monitoreo-ambiental/) and CCAMLR CEMP site catalogue (https://www.ccamlr.org/en/science/cemp-sites) identify Uruguay and University of Jena collaboration for Ardley monitoring. Request original 2017/18 and 2023/24 georeferenced occupied breeding-group polygons, survey coverage and date, CRS, active/AON definitions, species and repeated vegetation observations. No contact has been sent and no new source permission presumed. Do not substitute raster colors, approximate georeference or older partial coverage for measured transition areas.

Local reproduction bundle ardley_coast_registration_audit_20261124.zip, SHA256 b3cc17af077107eb01f34305e2dcc50fc119590450691b9536015bca800db7f2, includes executed registration and zone-disagreement scripts, numeric outputs and provenance. Source PDF and original imagery not redistributed. Registration script SHA256 05bd7f488e70759f12f53324149a09c8140e00fb9cb330a029cb4c306cec194f. Source artifacts remain linked to original GitHub Actions runs. No main merge.
