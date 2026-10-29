# South-polar functional island geography — original Landsat vs mapped rock V6–V8 result

**Analysis date 2026-10-26. Source-only, no animal outcomes opened.**

## Ecological purpose

We aim to test an Antarctic island-biogeography mechanism, not to merge results
from others' penguin papers. A nominal 'physical island' and a patch of
accessible rock/fast-ice substrate are different geographical units.
Do not treat author-defined potential-site centres as nest GPS or a rock-vector
polygon feature as a stable breeding population.

## Full original satellite-mapping input

- **BAS/SCAR automatically extracted rock v7.3 (2020)**, DOI
  10.5285/178ec50d-1ffb-42a4-a4a3-1145419da2bb,
  40,955,252 zipped bytes, SHA256
  `7eb0cae84016b758c98a61977c90d0a8c2c6450c4bf82433e08d03ef2e5a4a5a`.
  All **366,106** source polygon records were inspected; original GRIDCODE
  identifies **359,880** Landsat-derived features and **6,226** manual-source
  fill-ins. This is **partially reused underlying source**, not an independent
  second field survey.
- Earlier BAS/SCAR manually compiled rock v7.11: **31,480** source polygons,
  original publisher ZIP SHA256
  `4d93119052d3c6bf51d20dab218447686e2273e7489e1b63351b69e4bc3d7d8b`.
- **AADC 2025 potential site frame**: 7,785 unique original author site IDs
  and coordinates, independent of animal observations.
- The two published rock maps differ in vintage, feature delineation,
  survey coverage and original manual fallback; neither provides historic
  surveyed nest-suitable substrate for all breeding seasons.

## Geometry quality and correction

A first intentionally conservative V6 search marked **4,940** candidate sites
HOLD if a source-invalid polygon's *bounding envelope* came within 2km;
the initial **694** unvetoed exact hits are ONLY a conservative QA lower bound,
and should not be compared to the old map as a genuine 694-site habitat census.

The source-only v7 shapefile contained **1,344 original invalid rock features**
within an AADC search-bbox envelope. Shapely `make_valid` recovered polygonal
geometry for all 1,344, preserving separate counts for native-valid and repaired
features; no source-boundary snapping or buffer choice based on bird outcomes.

- New native-valid exact site-centre containment: **2,159**.
- New including tagged make-valid repairs: **2,700**, an additional **541**.
- Previous v7.11 source-centre containment: **2,523**.

This provides two new auditable source-geographical estimates, not proof that
one source correctly identifies every ice-free location.

## Strongest new quantitative finding: map-source discordance

| Same fixed 7,785 AADC source reference points | Original-site count |
|---|---:|
| Site centre in BOTH independent-publisher versions of mapped rock | 721 |
| Site centre within OLD v7.11 rock only | 1,802 |
| Site centre within NEW v7.3 rock only | 1,979 |
| Site centre in neither mapped rock | 3,283 |
| Union of site centres with mapped rock by either map | 4,502 |
| Exact rock-site-set Jaccard overlap | **0.16015** |

With a common diagnostic of *within 250m* of either original mapped rock
polygon, counts are old-positive 3,035 vs new-positive 5,769;
intersection 2,094; union 6,710; Jaccard overlap **0.31207**.
The within-250m diagnostic is NOT an approved ecological locality correction
or a substitute for actual nest GPS precision.

All cells are **source cross-classifications**, not independent animal
replications; even the new map includes 6,226 fallback manual polygons.
Site point-in-rock disagreement may reflect map accuracy, nominal site
coordinates, actual winter/summer exposure, raster source era or feature
segmentation. No time series of rock surface change is estimated, so do NOT
label this as ice retreat, island ecological turnover or bird relocations.

## Biological decision and next independent analysis unit

**STOP interpreting single-point rock polygon membership as a fixed predictor
of penguin habitat capacity or island boundary.** Existing AADC strict
observation support failed at six Adélie and eleven flying-bird source sites
under the original verified parent-land gate. Retuning old GIS buffers or
picking the map that gives a positive biological model would not establish
Antarctic island causality. The positive 2025 potential-reference-site density
observation is separate and does not rescue physical habitat identification.

Use an external actual **season × georeferenced breeding patch** with explicit
P/A versus unsearched and a *locally validated polygonal nest substrate*.
The new Antarctic test should compare physical coast continuity, exposed
ice-free habitat connectivity and dated fast-ice availability separately.
The ordinary physical island comparison from `zuizui0223/island` (GSHHG 2.3.7
operational 8,264 island units) is a reference geometry, **not** an
assumed comparable population-scale response. See
`contracts/ANTARCTIC_EXCEPTIONAL_INSULARITY_MACRO_V2.md`.

## Durable evidence / repro

- V6 original source-only QA:
  `results/SCAR_LANDSAT_ROCK_V6_SOURCE_GEOGRAPHY_QA.json`
  [source CI](https://github.com/zuizui0223/mina/actions/runs/40254221274).
- V7 native/repair/source origin:
  `results/SCAR_LANDSAT_V7_SOURCE_TOPOLOGY.json`
  [source CI](https://github.com/zuizui0223/mina/actions/runs/40254680093).
- V8 exact 2×2 and 250m source overlap:
  `results/SCAR_ROCK_TWO_SOURCE_SITE_OVERLAP_V8.json`
  (computed deterministically from the pinned V7 cross-tabulation; no
  new bird or ecological model).
- Separate pre-existing original SCAR/AEI/AADC provenance, prior negative
  biological gates and original paper freeze remain in PR #199 / PR #189.

**Current result is original-data macro *geography* and a quantitative
measurement limit. It is NOT yet a novel penguin/island biological causal law.**
