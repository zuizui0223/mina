# Ross subcolony configuration -> next-year breeding growth v1

**Status:** pre-effect mechanism contract. Frozen before downloading or inspecting the numerical Schmidt et al. 2021 subcolony count/geometry tables for this question.

## Public source

Schmidt et al. (2021), *The influence of subcolony-scale nesting habitat on the reproductive success of Adélie penguins*, Scientific Reports 11:15380.

Public analysis repository:

    pointblue/adpe_subcol_success

Public data location is linked by that repository README.

The published analysis code identifies the processed tables:

    croz_selected_meas_ct_all_v19.csv
    royds_selected_meas_ct_all_v12.csv

with fields including:
- colony;
- subcolony ID;
- season;
- active nest / active territory count;
- chick count;
- subcolony area;
- perimeter-to-area ratio;
- terrain attributes.

The publication already establishes that perimeter-to-area ratio is strongly associated with same-season reproductive success. That same-season result is prior knowledge and is **not** retested as novelty here.

## Biological question

Does subcolony spatial configuration predict **next-season change in breeding abundance**?

Generated hypothesis:

> subcolonies with greater edge exposure / fragmentation, represented by higher perimeter-to-area ratio, should rebuild or grow more slowly in the following breeding season after accounting for current breeding abundance and subcolony area.

This is a direct, denominator-independent test of the configuration-memory mechanism suggested by the Ross recovery paper.

## Why this route is measurement-safer than the Bird success ratio

Primary predictor:

    perimeter-to-area ratio

is derived from mapped subcolony geometry.

It does not contain current nest abundance.

The response contains current and next-year breeding abundance, but there is no shared denominator between predictor and response.

No chicks/nests ratio is used in the primary test.

## Outcome-blind support gate

After this contract is committed, inspect only:

- file existence and checksums;
- column names;
- colony labels;
- subcolony identifiers;
- season labels;
- structural missingness;
- whether perimeter-to-area ratio and polygon area are static within subcolony as expected;
- whether active breeding count is available for consecutive seasons;
- number of eligible subcolonies/transitions.

Do **not** summarize:

- active-count magnitudes;
- perimeter-to-area magnitudes;
- growth responses;
- trait-growth correlations;
- coefficients.

Require:

1. both Cape Crozier and Cape Royds processed tables accessible;
2. at least 2 consecutive season transitions represented;
3. at least 50 eligible subcolony-transition rows in total;
4. at least 10 distinct eligible subcolonies at each colony.

Otherwise record SUPPORT FAIL.

## Fixed eligibility

A subcolony transition i,t -> t+1 is eligible if:

- the same subcolony ID is present in consecutive seasons;
- active_ct is finite and >0 at both t and t+1;
- perimeter-to-area ratio is finite;
- mapped polygon area is finite and >0;
- colony identity is Cape Crozier or Cape Royds.

No pseudo-counts.

No bridging of missing seasons.

No subcolony is removed based on growth direction or trait magnitude.

## Response

For eligible transition i,t:

    Y_it = log(active_ct_i,t+1 / active_ct_it).

This is next-season breeding-abundance growth at the same mapped subcolony.

## Primary predictors

Use the frozen geometry variables:

    P_i = z_colony(log(perimeter_to_area_i))
    A_i = z_colony(log(area_i))

and current breeding abundance:

    B_it = log(active_ct_it).

Standardize P and A within colony over the fixed eligible subcolony roster.

## Primary model

Fit:

    Y_it =
      alpha_(colony x start_year)
      + gamma * B_it
      + beta_P * P_i
      + beta_A * A_i
      + error_it.

The colony × start-year fixed effect removes common annual growth conditions separately at Crozier and Royds.

The focal prediction is:

    beta_P < 0.

Interpretation:

higher edge exposure / fragmentation predicts lower next-season local breeding growth after current breeding abundance, subcolony area, colony and year are controlled.

beta_A is adjustment, not a co-primary hypothesis.

## Frozen permutation inference

Use:

    B = 9999
    seed = 20261006.

Permutation unit:

    complete static geometry tuple (P_i, A_i).

Within each colony:

1. permute the complete geometry tuple among distinct subcolony IDs;
2. keep every subcolony's entire breeding-count time series unchanged;
3. refit the identical primary model;
4. record beta_P_perm.

This preserves:
- within-subcolony temporal dependence of abundance;
- annual colony-wide forcing;
- correlation between P and A;
- number of observations per subcolony.

It breaks only the assignment of mapped configuration to demographic trajectory.

Directional p-value:

    p = (1 + count(beta_P_perm <= beta_P_obs)) / 10000.

Primary support requires:

    beta_P_obs < 0
    and
    p <= 0.05.

A null or positive result is terminal.

## Effect size

Report:

- beta_P;
- permutation p;
- SD-scaled change in growth multiplier:

      exp(beta_P)

  for +1 SD higher log perimeter-to-area ratio;
- number of transitions and distinct subcolonies by colony.

## Frozen robustness

### Leave-one-subcolony-out

Report range of beta_P after omitting each distinct subcolony one at a time.

This is robustness only.

### Colony-specific descriptive fits

Fit the same model separately at Crozier and Royds, omitting the colony factor.

Report signs and estimates.

Do not require both to be significant.

### Remove chick information entirely

The primary analysis already does not use chicks. No chick-derived alternative is allowed to replace it.

## Interpretation boundary

A PASS supports:

> mapped subcolony configuration carries prospective information about next-season breeding-abundance change beyond current local breeding abundance and mapped area.

It does **not** prove:
- edge predation is the causal mediator;
- individual movement;
- an Allee threshold;
- metapopulation-scale hysteresis;
- the Ross 2001–2002 rebound mechanism.

A FAIL means the published same-season configuration–reproductive-success relationship does not translate into detectable one-season local abundance growth under this frozen design.

## Relation to PR189

This route is optional mechanism evidence.

The main PR189 result remains:

    aggregate breeding change does not determine spatial allocation.

If this configuration test passes, it supplies a denominator-independent prospective predictor of the local contrast mode.

If it fails, the mechanism remains unresolved and no alternative geometry metric is searched in the same opened data.
