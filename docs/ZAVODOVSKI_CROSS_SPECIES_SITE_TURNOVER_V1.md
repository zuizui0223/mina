# Zavodovski: does colony-space succession accompany cross-species population turnover?

Status: PROSPECTIVE SPATIAL-OUTCOME GATE / ECOLOGICAL RESULT **NOT RUN**. Drafted 2026-10-10 after reading published **island-wide** population trends, but **before looking at colony polygons**. This is *not* globally outcome-blind or a confirmatory test of climate impacts. This is separate from frozen Ecology PR189 and ongoing PR193.

## Why this is a distinct ecological question

Ratcliffe et al. (2026, *Current Biology*, doi:10.1016/j.cub.2026.09.010) already established that the chinstrap population fell dramatically while the macaroni population rose on the **same island**. The authors disfavor nesting-space competition as the chief explanation because total occupied colony area contracted and marine foraging niches differ. We **cannot** claim that anti-correlated species totals, a volcanic eruption, climate preference, sea-access effects, krill shortage or nesting competition are novel discoveries.

Unresolved, narrower spatial question: **Does newly occupied macaroni breeding space appear disproportionately on ground just vacated by chinstraps, or on ground not previously occupied by chinstraps?** A spatial transfer would be compatible with local facilitation / site legacy / competitive release, but it would not identify which, prove displacement, or explain the island-wide population changes. A zero-transfer result would be informative: shared-island species replacement may happen **without replacement of individual nest patches**.

## Frozen public source and timing

- Spatial archive: Ratcliffe, Dickens & Clucas (2026), UK Polar Data Centre doi:10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308; BAS record GB/NERC/BAS/PDC/02256.
- Published inventory: 28 shapefiles and associated files (~34 MB), `layer_descriptions.csv`, `validation.csv`; chinstrap and macaroni colony-boundary polygons available as satellite series 2011, 2016, 2020, 2022 and 2025, plus 2023 field drone polygons.
- Main comparison is **matched satellite-to-satellite transitions**, specifically 2011→2016, 2016→2020, 2020→2022, 2022→2025. Drone-derived 2023 boundaries are **not inserted as another annual point** because sensor and method differ.
- Source reports 30–50 cm satellite resolution, >90% survey coverage of occupied habitat, EPSG:32726, and imputation of cloudy gaps from **different years**. Thus map labels alone are **not enough** to establish genuine occupancy at a particular time.

## Causal and spatial validity gate (STOP unless every condition documented)

1. Obtain original archive and read `layer_descriptions.csv` before using any biological shapefile geometry. Confirm source version, all polygon names, species labels, dates and CRS. We have **not** downloaded or analyzed any original polygon here.
2. For every interval and species, confirm actual acquisition year for every mapped region. **Exclude** clouds, copied nearest-year boundaries, obstructed areas and unknown observation-year locations from a common valid-coverage spatial mask. If the archive does not supply georeferenced provenance masks (and they cannot be recreated from legitimate images or metadata), STOP; do **not** substitute a whole-island mask or treat imputed features as simultaneous observations.
3. Use a single documented projected 32726 CRS for all four layers and the common coverage mask; audit registration at fixed coast/terrain landmarks. Reject questionable registration rather than explain overlaps as animal movements. Validate that the same site was searched, and retain the survey/season date provenance.
4. Species polygon overlap must be permitted as an ambiguous or mixed habitat state. No forced exclusive classification, no claims of individual movement, and no ecological p values from raw overlap.
5. Do not copy restricted commercial satellite images. The publicly described colony polygons are governed by the source's data terms.

## Exact area partition (descriptive endpoint, not mechanistic identification)

For interval t→t+1 on common valid land support S let C_t be chinstrap colony area and M_t macaroni colony area, all intersected with S. Define L_C = C_t minus C_(t+1) (chinstrap-space loss) and G_M = M_(t+1) minus M_t (macaroni-space gain).

Primary spatial co-location quantity: **E = area(G_M∩L_C)/area(G_M)**. It is undefined when macaroni has no mapped gain. Secondary quantity: **F = area(G_M∩L_C)/area(L_C)**, undefined when no chinstrap loss. Show absolute m² alongside fractions.

Partition every m² of new macaroni habitat into (1) previously chinstrap / now chinstrap absent; (2) chinstrap still present in both maps; (3) no mapped chinstrap at the first date. This is a complete partition, *not* a zero-sum model. Also measure the reverse process, chinstrap gain where macaroni was lost.

Interpretation: E high means same-place succession *is possible*. It does **not** establish competitive release, colony-site modification, predecessor order within a multi-year gap, or reproductive success. E near zero means growth and loss occurred in separate mapped places, even when island-wide species totals diverged. Either outcome could be ecological insight, but first inspect historical maps and prior art for whether it was already reported.

## Further mechanism discrimination (not yet supported or fitted)

A stronger claim needs independent measurements of elevation, slope, access, volcanic disturbance, distance to existing colonies, and possibly nest-site substrate/guano state **before** turnover. A covariate-constrained null distribution of new macaroni area across eligible sites would then test whether former chinstrap patches are preferentially used beyond availability; a source-only overlay cannot do that. Guano legacy and competitive release may yield the same mapped outcome and cannot be distinguished without additional data.

## Source references

- https://doi.org/10.1016/j.cub.2026.09.010 — published whole-island population and community outcome (prior art)
- https://doi.org/10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308 — open spatial polygon dataset
- https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/02256 — methods, cloud gap replacement, 34 MB files, documentation

**Current conclusion: mapped-site succession is testable in principle; no real exchange fraction has been calculated, and the lack of verified actual-year coverage masks is presently an identification HOLD.**
