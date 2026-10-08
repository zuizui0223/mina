# Signy Chinstrap ratio-free output-to-allocation result v1

**Status:** prospective mechanism **FAIL**. Contract, seven-colony support amendment and support receipt were committed before late-fledgling magnitudes were summarized for this test.

## Frozen design

Fixed colonies:

- C15
- C18
- C46
- C47
- C79
- C80
- C81

Support-only audit yielded:

- 15 eligible consecutive start seasons;
- 105 colony-season rows;
- no partial-colony panels;
- no gap bridging.

The predictor was deliberately ratio-free.

### Step 1 — size-adjusted late output

For colony i and season t:

    X_it = log(1 + late fledglings_it)

was residualized against:

    colony FE
    + start-season FE
    + gamma log(current breeding pairs).

The residual is Q_it.

Estimated:

    gamma = +0.32343.

### Step 2 — next-season allocation

Frozen model:

    log(p_i,t+1)
      = colony FE
      + start-season FE
      + rho log(p_it)
      + beta Q_it
      + error.

Prediction:

    beta > 0.

## Primary result

Observed:

    beta = -0.02248

rather than positive.

Current-share persistence:

    rho = +0.68528.

Fully standardized partial coefficient for Q:

    -0.0637.

The year-vector permutation distribution was centered near zero:

    q05    = -0.0751
    median = -0.00047
    q95    = +0.07185.

With 9,999 frozen permutations:

    exceedances >= observed = 6,836

and:

    p = 0.6837.

Therefore the preregistered support criterion fails on both required conditions:

- beta is not positive;
- p is not <= 0.05.

## Leave-one-colony-out robustness

LOO beta values:

| omitted colony | beta |
|---|---:|
| C15 | -0.0439 |
| C18 | +0.0135 |
| C46 | -0.0272 |
| C47 | -0.0254 |
| C79 | -0.0261 |
| C80 | -0.0235 |
| C81 | -0.0124 |

Six of seven remain negative.

The one weak positive omission does not alter the terminal primary decision.

## Backward diagnostic

Where a structurally supported previous season was available:

    Q_t -> previous share change

gave:

    beta = +0.0969.

This is secondary and not interpreted as a biological reverse-time mechanism.

It reinforces that the failed forward result should not be rescued by post hoc temporal reinterpretation.

## Relation to Bird Island Gentoo

Bird Island's frozen ratio statistic showed a very strong forward association:

    beta = +0.324
    permutation p = 0.0001.

But post-result audit showed:

- shared current-nest denominator geometry;
- chicks/nest values above two because of monitoring/phenology semantics;
- a large denominator-only negative-control association;
- near-symmetric backward structure.

A post-result ratio-free Bird model remained weakly positive, but was not confirmatory.

Signy was designed specifically as an independent, prospective, ratio-free test.

It **does not reproduce the positive Bird mechanism signal**.

Therefore the correct program-level conclusion is:

> **the spatial-allocation state result is strong, but local reproductive output is not yet an established predictor of the contrast mode.**

## No rescue

Per the frozen contract, do not now search:

- two- to six-year lags;
- earlier chick counts;
- alternative colony subsets;
- chicks/pair ratios;
- alternative productivity transformations.

Those would be new hypotheses after a terminal null result.

## Paper consequence

This result strengthens the interpretation discipline of PR189.

Keep as main result:

> aggregate breeding change does not determine spatial allocation.

Keep Bird's success signal only as a qualified, measurement-sensitive lead.

Do not claim:

> breeding success determines which breeding nodes receive the rebound.

The next mechanism test should use a predictor independent of current abundance, such as mapped subcolony geometry or disturbance-induced access cost.

## Claim boundary

Supported:

- the exact frozen Signy beta is slightly negative;
- the directional permutation test fails;
- six of seven LOO estimates are negative;
- independent ratio-free replication of the Bird reproductive-output mechanism failed.

Not supported:

- reproductive output never matters for spatial allocation;
- a different biologically justified lag is necessarily null;
- configuration/access predictors are null;
- the state/allocation conclusions of the main paper are weakened.
