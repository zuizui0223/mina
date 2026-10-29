# Independent Antarctic candidate-site network: actual AADC ecological V1–V2 results

**Date: 2026-10-26 — exploratory only.** These are original public AADC P/A survey observation analyses, not a meta-analysis of author-published effect sizes. The authors already published a 2025 seabird occupancy study, and this project's earlier V14 model opened the same animal data; this is not an independent confirmatory replication.

## Observational units and V1 results

Candidate-network geography is derived first from **7,785 source-defined potential geographic sites**, with 10-km counts of *other candidate site centroids* (not physical nesting patches, island polygons, animal movement distances, colonies or confirmed accessible sites). AADC survey observations remain source site × species × season; only original explicit P/A, exact source certainty and nonduplicated original groups are analyzed; NR is never zero. Sites are held out by 250-km geographic block; same-site seasons are history-weighted.

| V1 | Adélie original source programme | Seven flying seabird source species |
|:--|--:|--:|
| Original source site IDs scored | 1,031 | 368 |
| Original survey P/A rows scored | 3,618 | 6,956 |
| 250km geographic holdout blocks | 12 | 8 |
| Equal-block Brier source geography/area/effort B0 | 0.277253 | 0.358390 |
| B1 B0 plus 10km local source candidate-site density | 0.266550 | 0.312243 |
| B0−B1 | **+0.010703** | **+0.046148** |
| Blocks with positive improvement | 8/12 | 8/8 |

The V1 original calculation and 10km choice are recorded in `contracts/AADC_POTENTIAL_SITE_NETWORK_P_A_EXPLORATORY_V1.md` and `results/AADC_POTENTIAL_SITE_P_A_EXPLORATORY_V1.json`. Real reproducible CI: https://github.com/zuizui0223/mina/actions/runs/40209072157 .

## V2 prespecified *post-V1-outcome* falsifications

V2 is locked **after** seeing the positive V1 associations. The diagnostics are therefore adversarial, not a confirmatory external study. Full original V1 model and input population reproduced numerically before every falsification.

| V2 | Adélie | Flying seabirds |
|:--|--:|--:|
| Exact V1 frozen model replay | PASS | PASS |
| Same V1 cohort, remove outcome-adjacent expert-validation predictors: Brier gain | +0.008886 (8/12 regions) | +0.047003 (6/8 regions) |
| 2021 original potential-geography frame 10km network: Brier gain | +0.017864 (1,031 shared sites) | +0.062081 (357 shared sites) |
| Same historical-site cohort, 2025 geography density Brier gain | +0.010703 | +0.047297 |
| Frozen 31 within-250km × source-class × old-frame stratified site-level shuffled density placebo: median gain | +0.027805 | +0.005635 |
| Original observed gain vs all placebo gains | **30/31 placebos ≥ actual** | **0/31 placebos ≥ actual** |
| Median unique sites with actually altered density (placebo) | 94.7% | 89.9% |

Original data CI and signed result: `results/AADC_SITE_OPTION_V2_FALSIFICATION.json`; https://github.com/zuizui0223/mina/actions/runs/40209742219 .

### Interpretable evidence hierarchy

**Adélie:** Site-density association is *positive in the raw cross-regional predictive model* and persists without expert terms and in 2021 frame, but the original precise within-source-region locations are **not** distinguished from within-region shuffled placements. An observed B0→B1 Brier improvement is therefore not support for an individual Adélie local habitat-option network mechanism. Source programme geography and mapped density distributions are enough to produce similar or greater gains under the placebo. No null of biological reality is established.

**Flying seabirds:** The source candidate-site covariate improves out-of-block predictions, remains positive under the historical source frame and lean expert-free controls, and exceeds all 31 site-level within-region source-class/source-frame shuffles. That supplies nontrivial **original-database local geographic information** not reducible only to its *per-block distribution in these fixed comparisons*. However, no statistical prospective p value or physical land/ice/water causality is identified by the 31 *post-result* placebos. Local mapping effort, species-specific detectability and imperfect regional capture can still generate the association.

**No species-wide causal claim:** Different original source programmes, sampled site IDs, breeding dates, detection and number of regions mean the apparent contrast between flightless Adélie and flying seabirds is **not itself evidence that flight ability causes a change in island connectivity**. An explicitly matched and independently observed dispersal/occupancy dataset is needed. Do not conflate 2021/2025 map editions with ecological time series; the 2025 reference map is not historical breeding habitat in all past survey years.

## Novel ecological question the current data make testable

Does **independent mapped habitat availability and fragmentation**, rather than the administrative density of potential-site reference points, determine local breeding occupancy conditional on observation effort? This is still a *hypothesis*, not a result; the V3 habitat atlas extracts 100m AEI terrestrial cells for **all original 7,785 geographic reference sites**, excluding author classes with bird/penguin/guano-derived labels to avoid direct predictor circularity. AEI extraction is independent of new animal outcome fitting, but later AADC V3 biological models on already-seen P/A rows remain exploratory.

The paper-ready novelty requires further site lineage, historical habitat area, alternative sampling-frame controls and independent P/A programmes. Even the strongest current V2 flyers result should not be written as proven Antarctic insularity mechanism.
