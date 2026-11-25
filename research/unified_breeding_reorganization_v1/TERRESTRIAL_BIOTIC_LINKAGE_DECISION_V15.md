# V15 terrestrial interaction source audit — 26 November 2026

**Decision: new open source verified; not a longitudinal animal–plant panel.** Close this direct temporal gate rather than invent matching or fit another surrogate regression.

## Source
Klarenberg, Liu, Convey, Cornelissen & Bokhorst (2026), Ecography e08175, DOI [10.1002/ecog.08175](https://doi.org/10.1002/ecog.08175) (online publication December 2025); original data release [10.5281/zenodo.17112197](https://doi.org/10.5281/zenodo.17112197), v1.0.0, CC BY 4.0. This is a combined archive, including previously published observations and recent samples. Do not call it a fully independent replication of 2019 data. Original paper already tested plant N/moisture and microarthropod associations, so repeating that model would not by itself be original.

Initial source job 45716923668 stopped because the official archive key contained a directory prefix. Exact key and safe basename were corrected without changing the source, and [run 45716998307](https://github.com/zuizui0223/mina/actions/runs/45716998307) acquired the 196,929-byte ZIP. Original advertised MD5 verified, outer/inner ZIP SHA256 and CRC, and workbook SHA256 checked locally. [Source artifact](https://github.com/zuizui0223/mina/actions/runs/45716998307/artifacts/15070282499). No publisher workbook copied into Git.

## Executed support comparison
| Region | 2013–2017 rows | 2023–2024 rows | Early distinct coordinates | Recent distinct coordinates | Exact shared coordinates |
|---|---:|---:|---:|---:|---:|
| Byers Peninsula | 241 | 0 | 29 | 0 | 0 |
| Rothera | 465 | 90 | 57 | 11 | 0 |
| Signy | 297 | 230 | 29 | 222 | 0 |

1,323 rows; 629 moss, 640 lichen, 30 vascular plant, 24 algae. Tissue N available 1,280; moisture 1,026; WHC 307. Some unavailable cells are literal #N/A. The 1,323 rows are not 1,323 independent sites. Sample_name has only 1,302 distinct values; geography × year × sample name has 1,316 keys, 7 repeated keys, no full duplicate rows. Do not silently remove or concatenate these observations.

Seven region–host pairs occur in both eras. Exact coordinate overlap zero even before conditioning on host. Within 100 m of an earlier same-host sample only one distinct recent coordinate (Rothera Sanionia uncinata, five sampled rows), distance 22.53 m. At 250 m, 17 distinct region–host–coordinate combinations (not 17 independent geographical locations). Distance support is not proof of resampling. No explicit animal-influence level, transect ID, plot ID or sampling date beyond year in workbook. Signy 2023 has 230 rows vs 210 newly collected Signy samples described by article; provenance unresolved, no arbitrary dropping of 20. No plant cover time series. No biological model fit.

## Interpretation / action
The study offers a distinct potential terrestrial-food-web module (cryptogam N/moisture and associated arthropod communities) and independent recent sampling campaigns; it does not establish a temporal effect of penguin/seal abundance on plant cover. Original animal-impact transect IDs and dates would be required to align with independent animal exposure. Even then, biomass samples need not measure vegetation extent. Do not link counts to these samples by island average or use N content as a penguin-specific exposure. Do not open another trait-association regression simply to obtain a positive result.

Cape Hallett original GIS/approved imagery dependency stays closed. Future prioritization should require actual repeated plant-cover/occupancy observations with measured same-area animal use, or a replicated animal-disturbance/nutrient manipulation with direct botanical outcomes; do not call cross-sectional gradients or satellite greenness a longitudinal effect. Broader Antarctic v0.6 and earlier manuscripts remain frozen. No submission or merge.

## Reproduction
`python cryptogam_temporal_support_v15.py github-actions-artifact-15070282499.zip OUTPUT_DIR` (read-only artifact_tool workbook API). Exact executed script Git blob a6734fa7ba3bf19dbc1b86510bab0a691bb25e5f; script SHA256 0ef50b867640653d38010b11f57615b250e59fa322dbe94965250c7f33cd7df8; full local result SHA256 8c2d46adbd40fbce90e72d28b7dec0d2d7c3543d693a6b620c48516520fee7fb. Summary JSON is a compact representation; full local audit can be regenerated from pinned archive. No independent new ecological effect.
