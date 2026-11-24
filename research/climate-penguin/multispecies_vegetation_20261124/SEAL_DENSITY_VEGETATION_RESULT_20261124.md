# Seal local use density and mapped terrestrial vegetation (2026-11-24)

**Executed original-source exploratory spatial comparison. Broad intermediate-density optimum prediction not supported.** No causal vegetation response, annual greening, or marine-to-land trophic pathway inferred. Prior isotope manuscript and frozen papers unchanged.

## Design (specified before tile outputs)
Same ten local positive-detection sites and 3,684 eligible source detections as the prior point analysis. Original Dryad ZIP SHA256 `7a5f991864d9a433cb9667626d27cc6f05cd43368097a8b57fd02340a9bc17af`; original Plantarctica ZIP SHA256 `7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236`. All native 2m eligible terrain cells, not the previous plotting subsample. Fixed UTM20S 20m primary tiles, >=50% eligible area. Count detections per 100m2 per recorded survey day; reference site mask assumed constant because per-date polygons unavailable. This is detected use, not true density or absence. Split positive tiles at within-site median into low and high (ties low); common elevation (5,10,20m), slope (5,15,30deg), exposed-edge distance (10,30,60m) strata require >=3 tiles in every group. Area-weight cover in each group, then use common minimum group area stratum weight and equal site weight. No p-value; tiles autocorrelated and sites within one region. Static 2017–2023 map overlaps 2020 survey period; no botanical truth or temporal direction.

## Main result
2,508 eligible 20m tiles at 10 sites; common support 9 sites, 34 strata, 1,199 tiles (708 non-detection, 258 low, 233 high). ER fails common support.

| Mapped class | Non-detection % | Low % | High % | High−low pp |
|---|---:|---:|---:|---:|
| Vegetation+lichen | 6.828424 | 8.884026 | 11.295359 | +2.411333 |
| Vegetation | 2.948775 | 4.943521 | 7.983973 | +3.040452 |
| Lichen | 3.879649 | 3.940505 | 3.311386 | −0.629120 |

Vegetation high−low 7 positive, 2 tied, 0 negative sites; LOO mean +1.5073 to +3.4205 pp. Combined high−low LOO +0.7996 to +3.3170 pp. Broad hump (low > zero and high < low) occurs in 1/9 combined cover sites and 0/9 vegetation sites. Lichen contrast negative at only 3/9 sites; no confirmed differential biological mechanism.

| Sensitivity | Sites | Matched tiles | Combined high−low pp | Vegetation high−low pp |
|---|---:|---:|---:|---:|
| 10m | 10 | 5008 | +0.5541 | +0.7942 |
| 20m primary | 9 | 1199 | +2.4113 | +3.0405 |
| 40m | 7 | 205 | +2.3216 | +3.5761 |
| 20m detected-day fraction | 9 | 999 | +1.2000 | +1.8692 |
| 20m peak observed count date | 9 | 822 | +2.7928 | +3.4110 |

Sensitivity supports differ, no claim of invariant per-site slope. 40m low vs undetected vegetation difference is negative; do not assert monotonicity universally.

## Separate post-result upper-tail diagnostic
Same 20m grid, >90th percentile of within-site positive density versus remaining positive, common terrain support (>=3 in all three groups). Six sites, 252 matched tiles. Vegetation upper minus remaining positive −1.4251 pp, driven entirely by Humb (five other sites exactly zero). Excluding Humb: 0. Combined −1.3985 pp, without Humb +0.1821 pp. Not a replicated threshold or evidence of vegetation damage. Extreme strata have little informative plant cover.

## Reproduction/validation
Local artifact `palmer_seal_density_vegetation_20261124.zip` delivered in conversation: SHA256 `6ed568c9ae50acc84a675156dfdf565d9eb7dbdfac0ba61f8cd769d6eba38ffb`. Includes executed scripts, prior source-pinned reproducer, native-tile aggregates, matching strata, per-site contrasts, summaries and independent validation receipt. Main script SHA256 `72177dab54366fd06c54edb426a9a98edeb6b7b65cfd60ecfb6fa9b50570b917`. Upper-tail script SHA256 `86aa3906f535890aa6f1b3325539acbb4ee77dc9d3ff2579a27873c70b4bc44f`. All 3,684 detections matched original row IDs, coordinates, site/date; allocation to one tile per scale; area/density identities and common-stratum weights verified; primary numbers independently reaggregated. No original archives republished. Local results only; no Actions execution claimed for this extension.
