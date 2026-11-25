# V10 — AADC actual repeated breeding-boundary polygons: frozen source support and descriptive estimator

**Created 2026-10-26 after original V9 AADC file-manifest enumeration, but BEFORE opening any GIS animal geometry.**
This is a genuine new vector-level *original field/aerial survey data* acquisition from
AADC DOI 10.4225/15/58f59b52edfef, not a literature effect-size synthesis or a
re-fit of the 2025 AADC P/A source sample. All original published source lineage
must be tracked. Historical source observations from published methods still
count as exploratory relative to known colony movements.

## Genuine outcome-blind sample gate (from ORIGINAL publisher file names only)

- Original source index: 33 published dataset object manifests, 167 `.shp`
  original colony boundary files, 138 site identifiers, 153 distinct exact
  `IS_<id> × season_start_year` pairs that can be read from fixed exact source
  file paths without opening biological polygon coordinates.
- **Only 13 repeated original IS site IDs** occur in >=2 original mapped seasons;
  **one site `74585` in four seasons: 2012,2013,2015,2016**.
- These repeated IDs fall in two author source survey groups `HBE` and `HBW`,
  principally 2013→2015. The method described by original source file paths is
  nominally `2mbuff`; this label does NOT independently establish identical
  field precision, complete visited polygons or actual nest GPS accuracy.
- Genuine survey polygon coordinate data for this new lane were **not** opened
  when the site/season selection was fixed. The 13 repeated IDs are a complete
  source-list cohort, not selected because they changed in an interesting way.
- **Result cannot be called Antarctic-wide macroecological replication**: just
  two adjacent AADC survey groups, exact physical island distinctness and
  independent regional forcing not yet proven.

## Original source download/access and measurement

From pinned `results/ANTARCTIC_SOURCE_BOUNDARY_MANIFEST_V9.json`,
identify precisely one year+site source path for each of the 13 repeated sites
and their recorded seasons. Do not select an `original`, `adj`, `corrected`,
`_2mbuff` variant within a site-year based on spatial outcome; if multiple
different polygon sources share the same site-year, mark ambiguous and exclude.
For each selected shape, use its own original AADC REST publisher dataset
UUID+file path; require `shp,shx,dbf,prj` actual member names in that dataset's
current official object manifest *before* downloading.

Source files must be bounded and SHA256-receipted. Read the original CRS WKT
and exact DBF field names. A layer is qualified only if projected coordinate
reference is valid, each row geometry is valid (or `make_valid` is explicitly
tagged), finite, polygonal, and transforms to EPSG3031 consistently.
Source area is projected EPSG3031 planar area, not exact ground-surface area.
To compare repeated maps, require source method stage / spatial coverage to
be explicitly documented. A mapped polygon absent in a source file is not an
explicitly searched empty breeding patch.

## Locked descriptive endpoints, conditional on source QA

Per original `IS site ID × acquisition season`: source file, original SHA256
per component, original shape count, nonempty union polygon area, constituent
connected components, source original CRS, source repair flag/area effect, and
parent AADC group. Store source polygons in a *short-lived runner only*: do not
Git-commit third-party raw geometries unnecessarily; write compact site-season
metrics and provenance for replication.

For each **same original site** observed in two successive available seasons
(`successive observation`, not necessarily consecutive calendar years):
- area ratio `A_later/A_earlier` and logged area change;
- spatial intersection/union Jaccard (J);
- earlier mapped colony polygon area retained within later mapped polygon `I/A_earlier`;
- later mapped colony polygon fraction outside earlier `(A_later-I)/A_later`;
- original temporal separation (years);
- whether binary polygon WKB is identical across years, indicating possible
  copied/unchanged delineation; this alone does not prove a true same-year map.
- Preserve empty/invalid polygons as outcome uncertainty HOLD, never mapped
  colony extinction. Stop when source extent/coverage changes cannot be
  distinguished from genuine spatial dynamics.

**NO control-site random redistribution, signed ecological hypothesis p-values,
area–fragmentation slopes or location-shift mechanism selection is authorized
by these two source groups.** The descriptive estimates are constrained by
differential source digitization and known buffer rules. Do not call polygon
gain first colonization, colony competition, new island, rescue or dispersal.

## Independent biological progress and future gate

If >1 original subregion passes, this V10 provides actual multi-island source
breeding polygons, stronger than prior AADC site-centre source fields.
A prospective cross-island test needs independent original landmass ID and
time-matched substrate maps/observation coverage, and >=3 independent
geographical regions, multiple independently validated site-year transitions
per region, before attempting a general island biogeographic law.

BAS South Sandwich 2019–20 original nest coordinates are a separate
cross-sectional sub-Antarctic comparator, **not** a repeated Antarctic field
observation programme. ZAVO original 2020 maca/mixed source nest records are
already present in historical PR #196 and must not be double-counted.
