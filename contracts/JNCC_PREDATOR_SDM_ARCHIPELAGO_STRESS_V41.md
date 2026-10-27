# V41 — Archipelago-held-out stress test of island predator source-label probability maps

**Designed after V40 predicted source-label probability maps and fixed 1-degree-block held-out scores were already seen: openly post-result robustness. No new ecological predator occupancy model or seabird response. Preserve immutable V40 island probabilities and calibration output, no model retuning.**

## Question
Does the four-taxon published-label probability model generalize to geographically AND monitoring historically separate UK island groups, or is strong 1-degree-cell held-out skill partly archipelago/source-group information leakage?

## Frozen original sources
- Exactly same RSPB UK Islands 2014 9,688 source \`lowid\` and Stanbury 2017 ESM5 original XLSX source hash \`3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5\`. Retain exactly **506** original islands with low-tide area >10 hectares, same 4 species and same training label code 1/2 versus combined source 0; exclude status 3 from validation.
- **Archipelago grouping solely by original RSPB \`group_\` string**, normalized case/underscore/blank. When truly missing/blank, fixed fallback \`region:<country>:<coast>\`; do not choose alternate groupings based on numeric results.
- G covariates \`log1p(area)\`, latitude, longitude; GH adds \`log1p(original resident population)\`, source-listed ferry presence. Training model must be identical to V40 StandardScaler + LogisticRegression C=1. No class weights, smoothers, new distances, trained calibrated labels, tuned thresholds or alternative taxon subsets.

## Measurement and evaluation
- Five-fold GroupKFold on entire original RSPB group strings, with complete withholding of all islands in heldout original group. Each island has exactly one prediction from a model never trained on any original island sharing its group.
- Per species report source labels 1/2 positives, source code 0 comparison, source code 3 excluded; original source archipelago group counts and largest-group fraction, five-fold test count and positive counts, Brier model G / GH / training-fold prevalence M0, heldout logloss/AUC/5-bin ECE where defined, group-balanced fold Brier difference and globally pooled Brier difference.
- Geographic-support requirement: at least five different original archipelago groups and in **every heldout fold** at least three original status1/2 and three source code0 islands. Failure -> \`SOURCE_ARCHIPELAGO_FOLD_SUPPORT_FAILED\`; prediction scores remain descriptive and MUST NOT be described as transportable outside source groups.
- Transportability interpretation additionally requires strictly positive **pooled** heldout Brier gain GH over source prevalence baseline AND positive equal-fold Brier gain. No claim of ecological occupancy / detection-corrected calibration even if both pass.
- This is post-V40 stress testing, not a prospective confirmation. Record difference from 1-degree block V40 for same original 506 cohort as evidence about spatial scale sensitivity; failure does NOT retroactively delete V40 maps.
- Output compact result JSON and per-fold source-only summary, no raw original lowid predator-label table, no JNCC seabird response. Original Source V36 physical-island mixed-group contrast remains STOP.

## Core limitation
RSPB \`group_\` strings include groups of very unequal size and fallback source regions; GroupKFold balances island counts rather than ecological source islands. Group-imbalanced test positives can dominate a fold. True survival/occupancy still requires an independent effort-calibrated original field survey with surveyed non-detections.
