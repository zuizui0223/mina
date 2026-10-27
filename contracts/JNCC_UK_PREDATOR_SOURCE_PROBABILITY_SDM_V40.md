# V40 — Island predator probabilistic source-label SDM and GIS probability atlas

**Status: post-V34 predictive mapping extension. All outcomes concerning source-recorded mink, rats and mice in V34 are already known; this is not a new preregistered ecological test. Scientific target is a probability PRODUCT, not proof of predator absence or seabird impact.**
**Date:** 2026-10-27; base branch research/jncc-v32-mechanism-contract; historical seabird Ecology PR #189 and V30/V36–V39 frozen results unchanged.

## Model target and ecological interpretation

Compute \`P(Stanbury 2017 status is CONFIRMED or PROBABLE | measured 2014 RSPB island covariates, source label is 0/1/2)\` for four separate mammal species:
- American mink
- Brown rat
- House mouse
- Feral cat

This is a **probability of the published observation/assessment label conditional on predictors**, not \`P(actual species inhabits island)\` and not a risk of seabird nest predation. Source code 0 mixes **assumed and known absence**. Source code 3 means possible/incidental and is NOT a positive or a verified absence: exclude from training/evaluation but allow an out-of-fit, marked prediction. Presence-only NBN/GBIF records do not turn code 0 into verified negative.

## Frozen primary source and domain

- RSPB 2014 UK Islands layer 9,688 \`lowid\` original island POINT features. Original low-/high-water area, coordinates (EPSG27700 reprojected WGS84), ferry link and resident human population.
- Stanbury et al. 2017 first-party ESM5 original XLSX SHA256 \`3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5\`; its 9,688 independent source island IDs match the RSPB 9,688 one-to-one by \`lowid\`, never island-name fuzzy matching.
- PRIMARY prediction domain \`RSPB low-tide area >10 ha\` exactly 506 island points; parent RSPB source for high-water and low-water areas differs. No extrapolation of fitted probability to 9,182 other, often extremely small, rock islets. Label codes are original published assessments, not surveyed absence.
- Original geographic validation groups: WGS84 \`floor(latitude):floor(longitude)\` 1-degree blocks. 5-fold \`GroupKFold\` holding out all data in a block; reports must show per-fold counts and geographic heterogeneity.

## Fixed model family

- Single standard fixed logistic ridge classifier \`StandardScaler + LogisticRegression(C=1,max_iter=1000,solver=lbfgs)\`, by species. No trying random forests, MaxEnt, different alpha or reordering species based on the predictive result.
- Model G covariates (source morphology/location): \`log1p(low_tide_island_area_ha)\`, original WGS84 latitude, original longitude.
- Model GH (primary probability layer): G plus \`log1p(RSPB resident human population)\` and binary *declared ferry link* (blank/space or "no","none","nil","n/a" is false). Ferry traffic is an access/observation proxy, not a verified mammal introduction.
- Comparison M0 (training-fold fraction of source labels 1 or 2) is a geographic held-out prevalence baseline, and G-only allows attribution of whether GH adds incremental source-label predictive information.
- Do NOT rescore other species or jointly model introduced presence across taxa because covariance includes shared assessment practices.
- For each taxon: report complete-case n, source label 1/2/0/3 counts, predictor missingness, 5-fold held-out Brier, log-loss, AUC/AP only where defined, Brier skill over M0, and calibration-in-the-large and 5 equal-count reliability bins. Never describe source-labelled classifications as true ecological occupancy calibration.
- Frozen evidence gate for **geographically transportable published-label probability model**: ≥30 documented positive (1/2), ≥30 source code 0, ≥5 independent spatial cells, all 5 holdout folds with ≥3 of each class, and **GH held-out Brier strictly lower than M0**. Fail => product remains only a provisional source-label propensity map, NOT a reliable transferable SDM.
- Fit the GH model to all labelled source rows for the candidate 506 islands after the heldout diagnostics. Prediction exports for all 506 source positions, including code3 as out-of-label uncertain. Predictions remain numeric even for models that fail the transportability gate but carry \`RESEARCH_ONLY_NOT_PORTABLE\` status. No unvalidated ecological risk classification into predator-free islands.
- Predictive uncertainty: **199 block bootstrap refits**, \`np.random.default_rng(20261027)\` resampling unique 1-degree geographic blocks with replacement, preserving all labelled islands in each chosen block, using same GH model/parameter set. Store 5%/95% model-resampling quantiles on the original 506 islands. If <100 valid refits, mark bootstrap UNAVAILABLE. These intervals are NOT full Bayesian credible intervals and do not include misclassification/assumed-absence uncertainty or source time changes.
- Labels for output map and CSV always \`P(positive source assessment)\`; avoid calling the output true occupancy or colonisation probability.

## Outputs and checks

Save under GitHub Actions artifact:
- \`JNCC_UK_PREDATOR_SDM_V40_PROBABILITIES.csv\`: one original source island \`lowid\` × predator species (506 × 4 rows) with source longitude/latitude, predictor domain, \`p_documented_positive\`, \`bootstrap_p05/p95\`, model source-status transportability, calibration/source status caveat. No original raw species status values or island names copied.
- \`JNCC_UK_PREDATOR_SDM_V40_MAP.geojson\`: one Feature per eligible island point with derived prediction probabilities by species and model status; map caption states "2017-source assessment probability, not verified occupancy".
- \`JNCC_UK_PREDATOR_SDM_V40_<taxon>.png\`: observed island points colored by GH probability, same color scale 0–1, no visual interpolation over unsampled ocean, note not actual species distribution.
- \`JNCC_UK_PREDATOR_SDM_V40_SUMMARY.json\`: full exact RSPB/ESM5 source hashes, source label incidence, folds, comparative calibration, interval diagnostic, 506 joined domain, limitations and no JNCC seabird outcomes read.
- Synthetic tests: strict source cohort n/lowid matching, source code3 excluded from fit, zero class not interpreted as surveyed absence, fold training/test site isolation, bootstrap quantiles, probability bounds, proper 506×4 output and no predictor leakage.

## Boundaries and next distinct input

- A probabilistic SDM for **actual mammalian occupancy** would require independent island surveys with explicitly verified absences/repeated detection/non-detection and effort, or a separately identified label sensitivity/specificity model. Without those, the true-occupancy intercept, prevalence and calibration are **not identifiable** from ESM5.
- The 506 original site points do not establish historical predator states in 1998–2005 and 2015–2021. No physically validated historic seabird nest/colony polygon crosswalk. Never use these probabilities as verified predator-free indicator in JNCC or Antarctic contrasts.
- Dataset examples for **independent presence-only validation**: UK Mammal Mapper GBIF occurrence dataset, DOI 10.15468/mjw32e (September 2026 publisher refresh), effort tracks stored separately; National Mammal Atlas Project DOI 10.15468/i2eosa (CC BY-NC 4.0). These may support positive-occurrence transfer tests but alone cannot establish true negatives or calibrated ecological occupancy. NBN Atlas direct downloads require login and dataset-specific licences, not bypassed in this work.
