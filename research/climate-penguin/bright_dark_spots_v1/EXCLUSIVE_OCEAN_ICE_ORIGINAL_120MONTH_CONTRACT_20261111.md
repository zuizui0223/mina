# Original 120-month exclusive marine ocean-cell SIC source diagnostic — frozen before new result (2026-11-11 JST)

## Single ongoing question
Can surprisingly different observed changes in Antarctic penguin nest counts among already-monitored nearby colonies be compared to *distinct local source marine climate*, instead of to two averages partly constructed from the exact same ocean pixels?

This is a **post-discovery diagnostic** following original bright/dark PR #215. Do not interpret it as a preregistered causal finding, proof of biological refugia, a new individual movement path, or independent climatic niche calibration. No expansion into broad predictive model searches.

## Fixed source / immutable biological candidate universe
- Reuse **all 147** original site-pair rows established before this diagnostic in successful Actions #42919893846, each same species×source region×original fixed polar 250km block, >=5 genuinely **co-surveyed original nesting seasons** spanning >=10 years. Pair identities, survey-year lists, count method, colony coordinates and original paired nest slope are immutable.
- Reuse original 595-site native 25km ocean-cell membership frozen from 1993-09 original OSI SAF (previous successful #42612067836), and 595×30×4 original source monthly site means and 120 publisher SHA256 receipts from the **same completed source artifact**. Source must be genuine EUMETSAT OSI-450-a1 v3.1 corrected reprocessing, 1991–2020 Aug/Sep/Oct/Nov, 25km EASE2. All 120 full-grid publisher NetCDF files are SHA-256 compared to frozen original receipts; original native grid latitude/longitude fingerprint matches; any mismatch STOP, no partial result.
- The original 147 paired colony differences, all actual co-census years, and the full source 100km SIC means are recomputed only for QA and comparison on exactly the same years. Neither source census absences nor missing ice pixels are converted into zeros.

## Geometrically exclusive source cells — frozen math
For pair (i,j), freeze:
- Left whole original native ocean cells A, right whole original native ocean cells B.
- Shared ocean pixels C=A∩B.
- Left **exclusive** L=A\B, right **exclusive** R=B\A. These are mutually disjoint source grid cells (but still spatially autocorrelated and may be within the same passive-microwave antenna footprints).
- Require **>=3 original fixed marine native cells in each L and R** before evaluating a pair; if one side has fewer, flag SOURCE_EXCLUSIVE_GRID_SUPPORT_INSUFFICIENT rather than making a missing/zero/NaN mean or relaxing the threshold.
- For each source monthly image and each subset L/R, use the SAME original status_flag valid ocean criteria (status bitmask & 3 == 0, source SIC finite 0–100). A source-exclusive mean is supported only if at least 3 valid subset cells and >=80% of that frozen exclusive ocean cell subset are valid. Shared subset C uses same QA when reported, but its failure does not invalidate L/R.
- Annual (original 1991–2020) is the equal-weight mean of the **four Aug–Nov source monthly means** for L and R. A year is supported only when all four monthly exclusive means on both sides are source-valid. This is the same original SIC season as the previous pair study, not a new chosen niche.
- Restrict to the immutable original **actually co-surveyed census year list** in each pair, then require >=5 source-supported paired exclusive SIC annual years and >=10-year span. If not, mark **INSUFFICIENT_VALID_EXCLUSIVE_CLIMATE_YEARS**, do not report an artificial zero/no-effect. Record number and years dropped from the old paired count roster.

## Original source cross-validation and fair comparison
- For every unique site in all 147 pairs and all 120 months, recompute site full 100km mean from the frozen original native cell IDs; compare to previously verified original **source_25km_buffer_mean_SIC_pct** within 1e-8 percentage points and require exact monthly OK versus incomplete status. This must pass before interpreting any exclusive-vs-full metric.
- For pairs with adequate exclusive ice source support: **on precisely the same retained census years**, report (a) mean absolute original full buffer SIC difference, (b) mean absolute original non-overlapping L/R SIC difference, (c) original full and exclusive signed annual SIC trends and their differences per decade, (d) ratio of the two nonnegative differences only when the original full difference >1e-9 pp, and (e) shared-cell mean when supported. Report original count log1p nesting slope difference **as already fixed from all common counted years**, not refitted post-hoc on reduced exclusive-ice years; a separate field gives limited-year sensitivity if count survey years are reduced.
- Preserve site-specific original frozen ocean subset sizes, overlap Jaccard, mean distances, counts, months and SHA receipts. No new geographic classification, SIC threshold, lag optimization, multiple-comparison p-values, or coefficient searches.
- Summarize (without assuming pair independence) eligible pair support across all species, same species-region-250km blocks, median full/exclusive difference, number with exclusive difference >/< full on common years, number with missing sufficient marine subsets. Treat this as a **measurement-resolution** study, not environmental causation.
- Highlight *pre-existing* Cape Crozier West/Cape Royds Adélie 25 co-surveyed aerial seasons and *pre-existing* Biscoe Point/Port Lockroy gentoo and Barton Peninsula/Demay chinstrap cases **whether the new exclusive data support them or not**. Keep an honest negative/unidentifiable outcome for any.
- If exclusive climate differences are larger, **do not claim 'the cause of divergent penguin nests is sea-ice'**. Exclusive subsets can be biased toward different distances/directions from coast, do not measure individual foraging routes, and may inherit smoothing/regridding uncertainty. OSI SAF 25km grid spacing is NOT true 25km physical resolution.

## Final reproducibility
1. Original source monthly SHA256 + native geolocation + full-site original means **all matching**.
2. Exact all-147 pair source geometry and fixed common-census-year support with explicitly identified insufficient cases.
3. Full/exclusive 8–11 SIC differences on identical supported survey years, retaining nesting outcomes and raw evidence.
4. Do not modify main, frozen Paper 1/2, climate PR #206 or mismatch PR #214; stay inside exploratory PR #215.
