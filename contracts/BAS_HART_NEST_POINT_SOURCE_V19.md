# V19 first-party source nest coordinate coverage — full seven-locality census

**Stage from official BAS Hart live archive V16, 2026-10-26.**
No original point coordinates or bird observation rows are used in V19.
After V18 original site-by-species count ledger, a new same-survey cross-sectional
spatial point-pattern test may be possible if separately named original species
point records coexist at true surveyed localities. The valid specimen is an
individual counted/annotated **nest point**, not a whole-island population estimate.

V16 current manifest has original 32 CSV files, 132 TIFF files, versus earlier
published metadata 31/127; its exact BAS source-ID paths are retained in the
full successful original GitHub artifact. Source metadata discrepancy must
remain visible. Of the 32 CSV files, one is the root total count ledger
\`SSI_count_results.csv\`, others may include coordinate points, polygon
outline vertex files or ancillary materials; **do not label every CSV a nest.**

## Frozen filename classification before any point response
- Include potential **nest point** datasets only when the literal source
  filename contains \`coordinates.csv\` but not \`outline\`, a known original
  species label (\`Adelie/Chinstrap/Gentoo/Macaroni\`) and 2019 or 2020
  observation-year marker. Source 2022 Zavodovski chinstrap remains a distinct
  *temporally noncontemporaneous* HOLD, not a 2020 field observation.
- Label \`Mixed\`, \`Unknown\` independently. They do not supply counted
  species-specific point patterns and cannot be assigned to either taxon.
- Exclude \`colony_outline_coordinates.csv\` from nest point data; it contains
  outline vertices, not a nest abundance series.
- \`SSI_count_results.csv\` is site count categories, not source nest points.
- Source site-locality folder alone does not prove actual separate island.
  Retain original locality ID, physical island candidate name, observation year
  and separate original file ID.
- Inspect first original CSV header only, bounded to 16 KB per file with
  publisher redirects verified. A \`nest_number,lat,lon\` header implies
  possible individual nest points only. Original row count and coordinate
  precision remain unknown until a later explicit point-data audit.

## Biology after genuine sample gate
For each true **same-season, same UAV survey-footprint** locality with 2+
direct source species-labelled individual nest coordinate files, derive
local spatial segregation at 5–20 m as a descriptive point pattern, using
a within-survey physical footprint rather than assuming available patch
locations outside the observed imagery. Do not interpret species absence if a
taxon lacked countable imagery (Candlemas), and exclude imputed/modelled
unnumbered points. Nested scale and site-level clustering mean pooled
hundreds of thousands of nests are NOT independent island replicates.

Potential cross-sectional archipelago n is ~5 named islands, only a subset
with simultaneous multi-species point data, and **does not** establish a
transferable pan-Antarctic competition or classic colonisation mechanism.
Additional seasons and independent archipelagos would be needed.
