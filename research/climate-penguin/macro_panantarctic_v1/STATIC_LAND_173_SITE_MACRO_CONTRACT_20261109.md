# Fixed pan-Antarctic 3-axis cross-sectional macro niche test (2026-11-09)

This is an outcome-aware **descriptive multi-region** support test after prior Gaussian and NB GAM findings. It is NOT an independent preregistration and is not a rescue of a failed p-value. Biological source denominator remains **595 original observed penguin colony sites**, marine 30-year SIC exists for all **595** (120 months each), static positive Plantarctica mapped land exists for **197 site×species at 173 sites** in **8 regions** and **14 original EPSG3031 250km geographic blocks**. This is not the prior 25-site 2017–2020 annual intersection.

## Fixed response and environmental predictors

- Actual current season-aggregated nest count median `count_median` for one source site×species, 2017–2023 era; *never* treat unrecorded species at a site or mapped plant absence as a true ecological zero. Log1p count median (positive or measured original 0) is the conditional observed-colony **abundance response**.
- Original **2017–2023 mapped plant/lichen 2km positive polygon area**: one static measured area per site even if repeated across species. This is **not an annual NDVI trend, directly measured botanical percent cover, or a causal warming-induced greening effect**.
- Original **1991–2020 August–November mean OSI SAF 25km site-coastal SIC** (full 120 native months, fixed original ocean cells at 1993 baseline), a historic long-term environmental context; not automatically the exposure in 2017–2023 when count median was observed.

## Exactly two fixed descriptive exercises

1. With one entry per each of the **173 distinct terrestrial positive-map sites**, compute the *unadjusted* Pearson correlation of `mean 1991-2020 SIC` vs `log1p mapped plant polygon area`, plus a **source-region-demeaned** correlation. Predefine a 250km block-bootstrap 95% interval with 2000 replicates, seeded 20261109. Do not report naive independent-site p. Geographic source region/neighboring 25km ocean pixels can be dependent across many colony codes.
2. With all **197 original site×species** positive mapped plant count medians, fit **one fixed linear model on source observed log counts**: `log1p(count_median) ~ species + source_region + log1p(observed_seasons) + mean_30yr_SIC + log1p(mapped_plant_area)`. Do not change terms after coefficients. Report vegetation and SIC coefficients in interpretable *conditional descriptive* units, and 250km block-bootstrap coefficient percentile intervals. With 14 blocks, these intervals are uncertain and are **not** full project-wise FDR, random site or detectability-calibrated causal effects. Condition on species and region; no zero-inflated/presence-only pseudoabsence.
3. If underdetermined or singular in ≥25% of block resamples, state **REGIONAL_INFERENCE_UNSTABLE**, not an artificial p value. Report exact n sample, site count, region count and 250km blocks. Do not add a new region/β/season/land threshold after seeing outcomes. A descriptive positive SIC–land correlation alone is not evidence of warming→vegetation mediation.

## Source files

- `outputs/vegetation_response_v1/site_species_cohort.csv` original published Git blob `23fea5988889303ecdc16f4b5309073cf38e366a` (246 site×species original, 197 positive mapped).
- `macro_panantarctic_v1/outputs/panantarctic_595_site_inventory.csv` generated from published original MAPPPD source Git blob `fc134e364cf38699fa7611d7dee5fbbbcb370c0a`.
- Reuse actual completed [1991–2020 595-site original OSI monthly 120-file QA artifact](https://github.com/zuizui0223/mina/actions/runs/42612067836) (no repetitive source downloads); original 40-site crosswalk 4800 pairs r=0.99996.

## Why this is macro, but not yet a dynamic niche-change model

It is an 8-region spatial comparison of **marine climate environment, terrestrial environmental niche, and three penguin species' recorded breeding abundance** on the full source-supported modern sites. It does not supply annual vegetation changes, random background absences, ecological occupancy, colony recruitment or future abundance change. Longitudinal macro biology is independently tested on [100 site×species trends at 77 sites, 7 regions](THREE_SPECIES_100_TREND_TEST_CONTRACT_20261109.md).

Do not collapse these independent temporal and spatial analyses into a single causal chain or select the nicer p value. `main`, frozen Paper1/2 and old v0.6 manuscript are unchanged.
