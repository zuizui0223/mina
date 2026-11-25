# V4 testable ecological association: independent mapped AEI habitat versus candidate-site density

**Status:** locked 2026-10-26 after original V1/V2 AADC biological outcomes were examined and while the V3 *independent habitat atlas* is executing. This study is EXPLORATORY and cannot establish new field replication, island movement or causation. It does NOT reinterpret the older V14 null or V2 permutation placebo as a validated species effect.

## Biological question

The AADC 2025 candidate-site count is a spatial sampling-frame predictor. Does independently mapped terrestrial habitat (non-animal-derived AEI ice-free area and Tier-2 habitat richness at the fixed 2km radius) carry region-held-out information for original breeding P/A beyond original geographic/survey covariates and administrative potential-site density?

Four fixed, non-tuned model layers:
- **M0**: source V1 controls (year, original latitude/longitude phase, source island/continent *site* class, site area, station-distance + missing indicator, two survey vantage flags, expert-validation flags, 2021-frame inclusion indicator, species indicators within flying programme);
- **M1**: M0 + original AADC 2025 other-potential-site centroid count within 10km, `log1p`, reproducing the existing V1 candidate-network effect exactly **on the NEW matched AEI cohort**;
- **M2**: M0 + independent 2km AEI non-animal-derived icefree area `log1p(ha)` + nonanimal Tier2 Habitat Complex richness (linear);
- **M3**: M1 + the two AEI habitat features jointly. No additional transforms, threshold search, radii, habitat categories or species group selections after original outcomes are opened.

**Interpretation:** M2−M0 is *independent mapped habitat information beyond original site area*; M3−M1 is *habitat information beyond administrative candidate-site network density*; M3−M2 is *candidate reference point density beyond mapped local physical habitat*. A more positive gain at one spatial grain is not evidence of the biological mechanism, and sign differences are not proof of flight-dependent ecology.

## Matched cohort and fixed sample/estimation gates

- Same original source program and strict V1 P/A/NR/duplicate/certainty group rules (original AADC five workbooks SHA pinned); ADP = original penguin programme, seven original flying bird codes = distinct flying programme. Do not claim same visit across programmes.
- Freeze predictor eligibility to AADC original sites with **at least one AEI non-animal-derived mapped ice-free ecosystem raster cell inside the 2km disk**. Missing mapped habitat is missing rather than 0; don't extend radii or impute missing ice-free area to rescue blocks.
- For each programme separately, predeclared source 250km grid blocks with >=5 independent original sites, at least 3 blocks and >=50 source P/A survey rows. If a programme fails, stop for that programme without changing geographic or stage filters.
- Hold out entire 250km geographic blocks for spatial CV; site/species history gets total weight 1 across repeated seasons within programme, as in V1; equal mean of block-specific weighted Brier is primary **exploratory** score. Fixed C=0.3 logistic; training-only median imputation/standardization; baseline and habitat models use the identical sample, folds, weights, original programme and source-count stage. Report block-by-block gains and overall M3−M1 and M2−M0.
- Even if mean improvement positive, require >=2/3 blocks positive to call an exploratory heldout predictor association. No p-value, no causal claim and no rescue from additional habitats/scale chosen post result. Record source era/terrestrial class composition, missingness and number of source sites with independent habitat.

## Explicit diagnostic limits

AEI v1.0 is a modern single-time habitat raster; original AADC breeding P/A seasons span 1980–2020. Source 2025 potential geographical site centroids are NOT nest coordinates. The physical site-area metric is not nested ADD island geometry. Only classes without name fragments 'penguin/seabird/bird/colony/rookery/guano/ornithogenic' enter AEI traits; this prevents the most obvious circularity but not all habitat/source design bias.

Previously opened original AADC P/A information makes the association exploratory by construction. No independent out-of-study confirmation is available. Treat flyer and Adélie results as two *different observation programmes*, not a direct causal species trait interaction.
