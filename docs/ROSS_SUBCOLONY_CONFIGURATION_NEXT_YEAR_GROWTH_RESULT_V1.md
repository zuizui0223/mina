# Ross subcolony configuration -> next-year breeding growth result v1

**Status:** prospective mechanism **FAIL**. The contract and support receipt were committed before active-count growth and geometry-effect magnitudes were opened.

## Frozen design

Public Schmidt et al. subcolony tables supplied:

- Cape Crozier: 16 seasons, 15 consecutive transitions;
- Cape Royds: 4 seasons, 3 consecutive transitions.

After the frozen structural rules:

- Crozier: **426** eligible transition rows from **92** distinct subcolonies;
- Royds: **65** rows from **22** subcolonies;
- total: **491** rows / **114** distinct subcolonies.

Perimeter-to-area ratio and mapped area are static within each subcolony in the supplied processed tables.

## Question

Does an edge-rich / fragmented subcolony configuration predict lower next-season breeding-abundance growth after accounting for current abundance and mapped subcolony area?

Frozen response:

    Y_it = log(active_ct_i,t+1 / active_ct_it)

Frozen focal predictor:

    P_i = within-colony z[log(perimeter-to-area ratio)].

Adjustment:

    log(current active count)
    + within-colony z[log area]
    + colony x start-season fixed effects.

Directional prediction:

    beta_P < 0.

## Primary result

Observed:

    beta_P = -0.01959.

The direction is as predicted, but the effect is small.

A +1 SD increase in log perimeter-to-area ratio corresponds to:

    exp(beta_P) = 0.9806

or roughly a **1.9% lower next-season growth multiplier**, conditional on the frozen model.

Other fitted coefficients:

    beta_current_abundance = -0.3088
    beta_area              = +0.3539.

Area is an adjustment term, not a frozen co-primary hypothesis.

## Frozen geometry permutation

The complete static geometry tuple:

    (P_i, A_i)

was permuted among distinct subcolony IDs **within colony**, while every subcolony breeding-count time series and every colony-year response remained fixed.

With:

    B = 9,999
    seed = 20261006

the beta_P null distribution was:

    q05    = -0.03075
    median = +0.00010
    q95    = +0.03246.

Observed beta:

    -0.01959.

Directional extreme count:

    1,513 / 9,999.

Plus-one p-value:

    p = 0.1514.

Therefore the frozen support condition:

    beta_P < 0
    AND
    p <= 0.05

**fails**.

## Leave-one-subcolony-out robustness

All 114 LOO coefficients remain negative:

    min    = -0.02887
    median = -0.01958
    max    = -0.01343.

So the weak negative pooled estimate is not created by one extreme subcolony.

But LOO stability does not override the failed permutation inference.

## Colony-specific descriptive fits

### Cape Crozier

    beta_P = -0.02875.

This is directionally consistent with the generated configuration-memory hypothesis.

### Cape Royds

    beta_P = +0.01257.

This is in the opposite direction.

Royds contributes only three consecutive transitions, so this is descriptive rather than a stand-alone test.

Still, the sign heterogeneity argues against a simple universal one-season configuration-growth rule.

## Interpretation

The strongest allowed statement is:

> **Mapped perimeter-to-area geometry does not provide confirmatory prospective prediction of next-season local breeding growth under the frozen two-colony design.**

The pooled estimate is weakly negative and robust to individual-subcolony omission, but it is not unusual under within-colony random reassignment of the static geometry.

Therefore this route does **not** confirm that edge-rich configuration is the mechanism selecting which breeding nodes receive rebound abundance.

## Relation to prior Schmidt et al. result

Schmidt et al. already showed same-season associations between nesting geometry and reproductive success.

This new test asked a different question:

> does the mapped geometry carry forward into next-season local breeding-abundance growth?

Under the frozen design, the answer is not confirmatory.

A same-season reproductive-success relationship therefore cannot simply be promoted into a prospective abundance-growth mechanism.

## Relation to Bird and Signy mechanism routes

Bird Island:

- strong frozen chicks/nests association;
- substantial shared-denominator and monitoring-semantic concerns;
- post-result ratio-free signal smaller but positive.

Signy Chinstrap:

- independent prospective ratio-free design;
- beta = -0.0225;
- p = 0.6837;
- terminal FAIL.

Ross subcolony geometry:

- denominator-independent static predictor;
- beta_P = -0.0196;
- p = 0.1514;
- terminal FAIL.

Together these routes now support a clean program-level conclusion:

> **the state/allocation result is reproducible, but the predictor of the contrast mode remains unresolved.**

## No rescue

Per the frozen contract, do not now search the opened Schmidt tables for:

- slope;
- elevation;
- wind shelter;
- flow accumulation;
- skua proximity;
- another geometry transform;
- a favorable subcolony subset

as a rescue for this route.

Those variables were not the frozen primary mechanism hypothesis.

## Paper consequence

Mechanism searching should stop for PR189.

The main paper should remain a **state/allocation paper**:

1. Ross natural disturbance/rebound;
2. calibrated 9.41% inverse-path mismatch;
3. Bird prospective positive-net-change sign test;
4. Emperor prospective decline-side sign test.

Mechanism belongs in Discussion as an open problem, not in the title or main Results.

## Claim boundary

Supported:

- pooled beta_P is negative;
- all LOO beta_P estimates are negative;
- frozen permutation p = 0.1514;
- Crozier and Royds descriptive signs differ;
- the prospectively specified configuration predictor fails the support criterion.

Not supported:

- configuration never matters;
- same-season reproductive success is unrelated to geometry;
- access geometry is irrelevant to Ross;
- another independently justified future mechanism predictor must fail.
