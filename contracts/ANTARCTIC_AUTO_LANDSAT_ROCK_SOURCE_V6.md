# V6 — Independent Landsat-derived Antarctic rock geography, no animal outcomes

**2026-10-26, source-first extension after V5 closed original AADC ecological-effects lane.**
This is a *different independent mapped-rock input*, not a permitted rescue of the failed
SCAR v7.11 strict site→rock→same parent-land cohort (6 Adélie/11 flying sites),
and not new prospective confirmation of already viewed AADC P/A outcomes.

## New original remotely sensed Antarctic substrate source

BAS/SCAR ADD **automatically extracted Antarctic rock-outcrop Landsat 8**
v7.3 (2020), DOI **10.5285/178ec50d-1ffb-42a4-a4a3-1145419da2bb**,
CC BY 4.0. Official zipped shapefile, ~41 MB:

https://ramadda.data.bas.ac.uk/repository/entry/get/add_rockoutcrop_landsat_v7.3.zip?entryid=synth%3A178ec50d-1ffb-42a4-a4a3-1145419da2bb%3AL2FkZF9yb2Nrb3V0Y3JvcF9sYW5kc2F0X3Y3LjMuemlw

This original raster-derived vector is **not** identical to the prior ADD
high-resolution manually compiled rock v7.11 polygons (31,480 original features,
source largely 1993, updated to 2025). The original v7.3 source was in places
adjusted to an older coastline; its 2020 vintage and mapping resolution must not
be treated as historical nesting substrate in every 1980–2020 AADC season.

## Source reference frame

7,785 original AADC 2025 potential geographic site IDs, all validated coordinates
and unique exact lat/lon. The 4,862 original sites shared with the 2021 publisher
reference are identified *without looking at animal observations*.

Old comparison: source-hashed **31,480-rock** v7.11 AADC×SCAR spatial diagnostic
CSV from original CI run 40163525892 with known
SHA256 c011eddbf2936d627dd22ff7cf5d0dc6992366f047806bf35f63a60bb1e51100.
Old strict 1,638 sites are a separate *parent-land* validity requirement; do not
equate with point-inside-any-rock.

## Fixed geography-only estimands

For every original AADC site reference coordinate (WGS84→EPSG:3031), compare
independent rock datasets at the *same point*, never using species or P/A/NR:
- Source rock polygon **contains** site-centre point (one, multiple, or none);
- non-containing site centre within **<=250 m**, **>250m to <=2,000m**, or
  **>2,000m** from every source polygon, using exactly mapped geometry rather
  than nearest centroid or snapped aliases;
- v7.3 site counts by original publisher island/continent site label and 2021
  source-frame ID membership;
- direct old-vs-new **5-category disagreement** contingency, aggregate coverage,
  and exact source reference/payload hash receipts.

The 250 and 2,000m distances are **preexisting QA diagnostics**, not
post-result ecological radius optimizations. These thresholds were used by
previous geographic QC and will NOT select a new biology cohort.

The source v7.3 shapefile should be iterated with a spatial index of the
**original 7,785 site coordinates**, rather than loading every high-resolution
Landsat rock feature into memory. Spatial bounding-box candidate selection is
only a fast superset; the exact polygon overlap/distance is computed
before classifying any site. Missing or invalid candidate polygons become
HOLD for relevant sites, never falsely converted to absent rock.

## Outcome interpretation and terminal constraints

A boost in 2020 Landsat map coverage shows *map-source disagreement* and may
improve a future independent spatial atlas; it is **not a biological population
or island effect**. Animal-derived 2025 AEI 'penguin colonies' raster classes
are still prohibited as independent predictors. This V6 must not reopen the
V14/V4 ecological model, the strict source site polygon failure, or tune
the original P/A sample selection after seeing which source seems better.

If official ZIP/CRS/format is unavailable, record a source STOP and retain
old conclusions. If geographic crosswalk can be audited, open a *separate*
new biological dataset/independent survey programme only after exact source
lineage and precision gates; do not reuse known AADC P/A outcomes as
pre-registered independent replication.

Source authority: BAS/SCAR catalogue item
https://data.bas.ac.uk/items/178ec50d-1ffb-42a4-a4a3-1145419da2bb/
