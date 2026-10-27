# V34 — Source-documented predator label niche across UK islands (exploratory)

**Frozen relative to V34 model fitting on 2026-10-27, AFTER source V33 counts and distributions were seen. NOT a pre-registered biological confirmation.** Original authors: Stanbury et al. 2017; RSPB 2014 UK Islands ArcGIS point inventory. This step opens *no* JNCC seabird count/outcome columns.

## Biological scope and measurement ceiling

The 2017 supplement is not a repeated-visit or detection-calibrated occupancy survey. Predator source status **1 confirmed, 2 probable, 3 possible/incidental, 0 assumed OR known absent** is explicitly asymmetric; 0 cannot serve as verified absence. The fitted label is a **documentation/source-assigned confirmed-or-probable indicator versus a mixed assumed/known-absent reference**. Predictions are relative *source-label propensity*, NOT a predator occurrence SDM probability, island attack intensity, realized ecological niche, or causal island risk. This is a diagnostic scaffold for future authenticated 1998–2021 predator occurrence source.

## Frozen input and cohort

- Original RSPB ArcGIS first party 9,688 unique `lowid` source point geometries and island area, human-population and coordinate fields, crossjoined to original Stanbury supplementary ESM5 workbook (source SHA256 `3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5`) using exactly 9,688 uniquely matched integer IDs. No site names or fuzzy geographic joining.
- **Primary cohort = original low-tide island area `mlwsarea_h > 10` hectares**, 506 islands, independently verified by source V33. Do not alter the area cutoff or filter on predator score, site count change, or climate.
- Five source taxa fixed at this stage (not an independently selected trait-level replication): **American mink, Brown rat, House mouse, European hedgehog, Stoat**. Reference status 0 is a mixture of unconfirmed absence labels; source rank 3 is withheld as UNKNOWN. Both 1 and 2 are source-positive, not instrumentally validated.
- Exclude per-taxon only source rank 3, malformed labels and nonfinite coordinates/area. Keep zero resident human population as a documented zero, NOT missing; explicitly flag missing/negative human population and do not coerce to zero. No imputation to predator status.
- Individual islands are records nested in original geographic localities. Island points are not observed nest site boundaries. There is no independently verified predator survey effort or island/year-specific site visit effort.

## Frozen source-label niche tests

1. Descriptive source-coded positive frequency by original low-tide island area bins **(10,50], (50,500], >500 ha** and by source resident human population **0 versus >0**, with status 3 counted separately. Do not claim a change with island size is a causal colonization gradient.
2. Compare two *a priori* source-label logistic regression classifiers:
   - **G (geography):** standardized `log1p(mlwsarea_h)`, WGS84 centroid latitude and longitude.
   - **GH (geography + human):** same G plus standardized `log1p(source_population)`, only if valid for all or apply explicit complete-case matched cohorts. Human population may directly influence the original *assumed* source label itself; GH improvements are documentary/source-information only.
3. Use original **1-degree WGS84 latitude×longitude cells** (floor independently) as no-leakage spatial group; `GroupKFold(n_splits=5)`, fixed deterministic group keys/split and no random feature search. Each test fold must contain >=3 original positive and >=3 reference 0 records or else report that taxon's five-fold spatial support as FAIL and do not report a pooled CV score. Each training fold needs both classes.
4. `sklearn.pipeline.make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=1, solver="lbfgs"))`. No class balancing/resampling/calibration by outcome. Same eligible rows/folds across G and GH; candidate outcomes may remain uneven and are only an exploratory model diagnostic. Report all five species even if weak/negative.
5. Equal-island held-out **Brier and binary log-loss** versus a fold-specific prevalence-only constant baseline; differences G−baseline and GH−G. Brier improvement is positive when comparator worse than model. AUPRC/ROC optional descriptive; classification improvements do not demonstrate predator biological niche. Baseline and predictors must use no bird counts/E response.
6. Warn if zero-label dominates or positivity fails at geographic-fold level; keep source country/region and cell counts and all five folds. AUC, coefficients, and descriptive gradients cannot be interpreted as ecological occupation/detection probabilities. Do not hunt better resolution/area thresholds/folds after result.

## Status gate

- The V34 biological question is **not whether predation explains JNCC change**. No JNCC original early/late abundance, total, site share, concentration E or species-specific decline is read here.
- Only after independent island identification, time-appropriate predator detection/repeated-visit effort, and enough mixed-landmass JNCC parent panels will a separate signed predator vs seabird share-loss model be considered in a distinct preregistered lane.
- A source-label predictor that does not generalize cannot be rescued by post hoc labels, positive selection, or using rank 0 as certain predator absence.
