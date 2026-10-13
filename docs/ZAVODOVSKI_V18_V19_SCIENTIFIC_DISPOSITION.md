# Zavodovski V18–V19 scientific disposition — 2026-10-13

This is an exploratory source-backed assessment on PR #196, separate from frozen Ecology PR #189.

## What passed
- V18 original GIS Actions #38409990975: successful. Historic 2011 C/macaroni/MIXED codes and the revised 2011/2016 maps were read only after the V18 exclusive-partition and buffer contract was committed.
- Baseline overlay X (mapped 2011 revised chinstrap loss × newly mapped 2016 macaroni gain): 27,511.990m².
- Joint 2011 revised/historic *pure chinstrap* label, absent from both revised/historic historic macaroni/mixed labels: T=9,938.357m², i.e. 36.124% of X, 24.189% of revised mapped macaroni gain, 2.881% of revised mapped chinstrap loss.
- Remaining X: MIXED=5,169.202m² (18.789%), historical MCPE outside MIXED=3,908.725m² (14.207%), unmapped by historic map=8,495.706m² (30.880%). The first two are explicitly not proof of maca absence in 2011; the last is NOT a surveyed zero.
- Concordant interior after 1/2/5-m geometric shrink and competing-class expansion: 7,003.755 / 4,753.571 / 1,216.517m². Arbitrary sensitivity distances, not actual mapping error estimates.
- V19 original BAS 2011 field colony-density CSV DOI 10.5285/96febb5d-1821-4f49-9b5f-32e489ae3839: source-format stage read only publisher's 25-line comment preamble plus first CSV header. Stage PASS, scientific georeference gate HOLD. Exact header names: `number_occupied_nests`, `sub-colony_area (m2)`, `density (nests/m2)`; no independent coordinate or joinable polygon/subcolony ID. The field nest count is independent observational evidence of chinstrap at visited sites, but the calculated density itself uses satellite-digitized area. Without spatial join keys, source cannot validate whether a specific V18 polygon was ground-visited.
- CSV V19 Github Action #38412197168 completed successfully as a source audit, and source read exactly ZERO original nest count or density values.

## Biological statement allowed

'At a single island and mapped times, 2011-to-2016 penguin polygon changes co-locate on some land. Only 36.1% of the initial 2011→2016 co-location area is concordantly labelled pure chinstrap in two interpretations of the *same* Jan 2011 satellite image. An independently published 2011 ground tally CSV cannot be joined to local map polygons because public header lacks site IDs/coordinates.'

**NOT established**: actual site-by-site maca colonization, competitive takeover, recruitment, species priority effects, guano legacy, local carrying capacity, historical site abandonment, true absence from any mapped/undrawn place, or a causal island-biogeography mechanism. The 2016 eruption happened after the Jan 2016 snapshot; temporal ordering alone disqualifies attributing 2011→Jan2016 GIS change to that eruption.

## Independent-source route

- Ask original source custodians for georeferenced 2011 nest-plot or subcolony boundary crosswalk; only proceed to a real same-site validation if available and independently dated. Do not join using approximate polygon area ranks.
- DARWIN DPLUS186 final report (2025) describes TerraSAR-X/PAZ collection every 4–7 days in 2023/24–2024/25 and later approximate 11-day supply, with SAR colony footprints not species-specific historical 2011–2016 events. No original SAR series publicly verified; don't claim it supplies a 2011→2016 settlement test.
- Until a spatially and temporally independent source exists, PR #196 is a cartographic robustness/data-quality follow-up, NOT a stand-alone causal ecological paper. Keep historic measurement source original and report both positive co-location and cautionary disagreement.

Relevant receipts: `results/ZAVODOVSKI_CONCORDANT_HISTORICAL_C_TO_M_V18.json`, `results/ZAVODOVSKI_GROUND2011_NEST_COUNT_COORDINATE_GATE_V19.json`.
