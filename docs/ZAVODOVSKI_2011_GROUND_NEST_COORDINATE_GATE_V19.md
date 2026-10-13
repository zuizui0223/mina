# V19 — Independent Jan 2011 ground-nest validation: public-source ID/coordinate feasibility gate

Frozen 2026-10-13 *before reading the row schema/any count data* for UK PDC source DOI 10.5285/96febb5d-1821-4f49-9b5f-32e489ae3839.

## Ecological reason, not another map interpretation

The two published 2011 digitizers agree only moderately on colony boundaries (Jaccard chinstrap 0.541; macaroni 0.512) and V18 concordantly classified only 9,938m² of 27,512m² direct 2011–2016 apparent C-loss-to-M-gain map overlap as pure chinstrap in Jan 2011. The historic GIS DBF has only `species` and `area`, so merely knowing 2011 survey totals **cannot** link a specific counted ground subcolony to the 2011 mapped polygon.

An independent ground-observed nest point/subcolony location **would** help validate true chinstrap presence at a specific baseline site, but would still NOT show macaroni absence at other sites, 2016 settlement, pair genealogy, interaction, or causality.

## Publisher metadata (no biological rows opened)

BAS archive GB/NERC/BAS/PDC/02263, Ratcliffe, Lynch, Black, White & Hart 2026: `Chinstrap penguin nesting density on Zavodovski Island, South Sandwich Islands, January 2011`. Counts of apparently occupied chinstrap nests made in **49 sub-colonies from 10–13 January 2011**, using direct shore-side tallies; mapped area was derived from a WorldView-2 image on 8 January 2011. Census quality ranked N1 (within ~5% per published ordinal method). The public dataset advertises **1 CSV ~5KB**, child file `zavodovski_chinstrap_density_2011.csv` at official RAMADDA record https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=96febb5d-1821-4f49-9b5f-32e489ae3839&output=default.csv.

**Stage 1 schema-only gate:** inspect **only the first CSV row** for column names, and source HTTP headers/file size/version. Never read or print any subsequent counts, densities or outcomes at Stage 1. Determine whether there are independently provided latitude/longitude, projected XY, or stable local site IDs which can be mapped to the historic 2011 polygons. Only if spatial coordinates are present is a literal polygon-containing-point validation possible. A bare `subcolony_id` cannot be matched to the historic 2011 DBF (which has no ID field) without an independently documented crosswalk; **never area-match or rank-match rows post-outcome**.

**Stop:** no independent spatial key -> HOLD site-level validation. In either case, 2011 density = field count / satellite-derived area is **not independent evidence of mapped polygon area**; independent evidence would be verified count + independently dated/located nest site. The 49 sampled colonies do not amount to island-wide ground confirmation or all-site absence.

## Alternative high-frequency source (prior art / limited)

Darwin Plus DPLUS186 project final report (https://darwinplus.org.uk/documents/DPLUS186/27933/DPLUS186%20FR%20-%20edited.pdf, p.4–6) reports independent TerraSAR-X/PAZ imaging every 4–7 days in 2023/24 and 2024/25, later continued near 11-day intervals (Richter et al. EGU 2024 DOI 10.5194/egusphere-egu24-22189). This is *not* a published 2011–2016 site-level species-coded tracking series and currently cannot identify within-interval order for the frozen map comparison. Do not imply the original SAR images are publicly downloadable; no public original site/season product link confirmed here.

Scientific status: independent ground-source **feasibility audit**, not a new biological effect, and independent from Ecology PR189.
