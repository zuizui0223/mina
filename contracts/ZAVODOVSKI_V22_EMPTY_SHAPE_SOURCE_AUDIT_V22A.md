# V22a source-format amendment after first V22 source/geometry HOLD (before opening 2023 bird point records)

On 2026-10-14, source-backed Actions #38422852481 passed synthetic tests, downloaded the authentic BAS 2023 GIS components, but **stopped before opening any 2023 point records** with `ShapefileException: Shape: Polygon or shape type: POLYGON requires non-empty points or non-empty lines`. Its original-status receipt expressly reported `original_2023_nest_point_rows_opened=0`. It is not a biological null result.

Before changing the original strict V22 reading logic, audit the **source geometry file structural metadata only** for each 2023 drone layer: file identity/SHA, shapefile type, record count, geometry-type frequency, count of genuinely empty-point records and shape records with nonempty vertices. Do not print or fit 2023 bird nest points or any 2023 ecological effects.

**Permissible narrowly-scoped repair, if needed:** only original source records with genuinely zero coordinates / no line vertices (and no biological geometry) may be skipped during polygon union; count and report skipped records. Any nonempty but invalid polygon, unexpected shape type, CRS mismatch, or transformed-geometry repair is still a hard HOLD. Do not reinterpret the empty record as a colony or a surveyed zero. Keep the original source file unchanged, and do not patch until source audit identifies exact affected filename(s). 

The 2023 same-species point-to-boundary ≥90% QA and coast plausibility ≥90%, prior V18 T surface reproduction, survey mask subtraction and original hypotheses remain **unchanged**. No post-outcome optimization or threshold change.
