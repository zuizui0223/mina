# Penguin two-timescale extinction forecast v1

**Status:** generated prospective design for an independent physically mapped breeding-patch dataset. No new outcome is opened here.

## Biological proposition

Penguin breeding-patch extinction is a two-timescale process.

1. **Slow environmental filtering:** patch quality and residual breeding capacity determine which local breeding populations are driven toward low abundance over several years.
2. **Fast state-dependent pruning:** once a patch is already small, current local abundance is sufficient to predict near-term disappearance.

This proposition is generated from two independent evidence streams already known before this design:

- Palmer/Signy operational components: current local size predicts next-year exact-zero loss extremely well, while recent one-year decline, relative share and coarse whole-network integrity add little transferable prediction.
- Torgersen physical sub-colonies: extinction timing is associated with historic area and aspect/snow-related geomorphology; similarly sized south-facing sub-colonies disappear earlier than north-facing ones.

## Why the prediction horizon matters

A one-year forecast is too late to test environmental mechanism: by then current abundance already contains much of the relevant information.

The informative test is whether physical habitat predicts **future approach to the low-abundance margin** before current abundance alone makes extinction obvious.

## Required independent data

A valid dataset must provide, for the same physical breeding patches:

- stable patch identity / polygon;
- annual or near-annual breeding-pair counts;
- exact observed zero versus missing observation;
- patch area or breeding-capacity estimate;
- aspect/northness, elevation, slope;
- snow exposure or a frozen terrain-derived snow-risk proxy;
- coordinates / physical adjacency;
- at least 10 physical patch extinctions with >=3 years of pre-extinction observations.

If these conditions fail, stop. No census-label proxy may substitute for physical patch identity.

## Frozen forecast horizons

Primary:
- **3-year extinction:** exact zero observed within t+1...t+3.

Secondary:
- **5-year extinction:** exact zero within t+1...t+5.
- **1-year extinction:** retained only as the near-term baseline where current size is expected to dominate.

Missing surveys censor a horizon rather than being converted to absence.

## Frozen predictor blocks

### Demographic state
- log1p current breeding pairs;
- relative time within population trajectory.

### Static / slowly varying physical habitat
- log patch area or frozen local breeding-capacity metric;
- northness;
- elevation;
- slope;
- frozen snow-risk score if available before outcomes are opened.

### Local spatial context
- nearest occupied physical patch distance;
- number or breeder mass of occupied physical neighbours within one predeclared distance scale.

Only one distance scale may be chosen from source geometry before extinction outcomes are modeled.

## Frozen model comparison

For each horizon:

- **D**: demographic state only.
- **E**: environmental/physical habitat only.
- **D+E**: demographic state + physical habitat.
- **D+E+S**: add local spatial context.

No nonlinear terms, interactions or threshold search in the primary analysis.

## Core predictions

### P1 — short horizon
At 1 year, D should perform strongly; adding E may provide little gain because current abundance is already a proximal extinction state.

### P2 — earlier warning
At 3 years, D+E should outperform D if physical habitat is an upstream driver of entry into the low-abundance margin.

### P3 — longer horizon
At 5 years, the relative contribution of E should be at least as large as at 1 year.

### P4 — local rather than global connectivity
If spatial rescue matters, physically local S should improve prediction. Coarse whole-network occupancy is not used because the Palmer/Signy screen did not support it.

## Evaluation

Use leave-one-patch-block or spatially blocked cross-validation defined from geometry before outcome modeling.

Report:
- log loss;
- Brier score;
- calibration;
- event ranking within each annual risk set;
- gain of D+E and D+E+S over D at each horizon.

No in-sample p-value can establish the primary prediction.

## Mechanistic interpretation

Support for D+E at 3–5 years but little added E value at 1 year would support:

```
physical habitat / capacity
        ↓
slow local abundance erosion
        ↓
current low-abundance state
        ↓
near-term patch extinction
```

This would connect Antarctic island environment to penguin extinction order without claiming that static island properties alone determine fate.

## Recovery extension

The same physical capacity variables should later be used to test the expansion–intensification switch:

- after decline, surviving patches with residual capacity should absorb numerical recovery;
- colonisation/reoccupation should become more likely as residual capacity at occupied patches is exhausted.

This recovery analysis must be prospectively separate from the extinction analysis.
