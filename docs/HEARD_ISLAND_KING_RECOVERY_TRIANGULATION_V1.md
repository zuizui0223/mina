# Heard Island king-penguin recovery triangulation v1

**Status:** post-result external literature triangulation discovered after the Ross V2 result. It is independent in species and island, but not confirmatory because the case was selected after the Ross result was known.

## System

King penguins (*Aptenodytes patagonicus*) at Spit Bay, Heard Island.

Historical ANARE records report two repeatedly censused breeding colonies:

- Spit Bay North
- Spit Bay South

The counts are estimates of breeding pairs derived from chicks/nests under the historical census coding system. Early counts are high-accuracy C1 chick counts; the 1980 south count is lower-precision C/N3. Gales & Pemberton later standardized historical records to compare projected breeding-pair trajectories.

## Published paired counts

| year | North | South | total | E |
|---|---:|---:|---:|---:|
| 1963 | 13 | 5 | 18 | 1.6701 |
| 1965 | 36 | 9 | 45 | 1.4706 |
| 1969 | 49 | 37 | 86 | 1.9618 |
| 1980 | 82 | 400 | 482 | 1.3935 |
| 1988 | 215 | 3,100 | 3,315 | 1.1380 |

The 1963, 1965, 1969 and 1980 values come from ANARE Research Notes 9. The 1988 comparison is reported in the Heard Island recovery synthesis, which notes 3,100 eggs/chicks at the south colony and 215 at the north colony.

## Main observation

Both breeding units increased across the long recovery.

Yet spatial redundancy was non-monotonic:

    1963  E = 1.670
    1965  E = 1.471
    1969  E = 1.962
    1980  E = 1.393
    1988  E = 1.138

Total abundance increased throughout:

    18 -> 45 -> 86 -> 482 -> 3,315.

Thus numerical recovery did not imply monotonic spatial recovery.

## Dominance reversal

In 1963:

    North share = 72.2%
    South share = 27.8%.

By 1969 the two colonies were nearly balanced:

    North = 57.0%
    South = 43.0%.

By 1980 dominance had reversed:

    North = 17.0%
    South = 83.0%.

By 1988:

    North = 6.5%
    South = 93.5%.

This is not the Ross mechanism.

Ross recovery preserves the identity of the dominant node and amplifies it further.

Heard recovery first reduces dominance, passes near maximum evenness, then produces a **new dominant node**.

## Interval arithmetic

### 1963 -> 1965

- total: 2.50x
- North: 2.77x
- South: 1.80x
- E ratio: 0.881

The initially dominant North colony grew faster, so E fell.

### 1965 -> 1969

- total: 1.91x
- North: 1.36x
- South: 4.11x
- E ratio: 1.334

The subordinate South colony caught up, so E rose.

### 1969 -> 1980

- total: 5.60x
- North: 1.67x
- South: 10.81x
- E ratio: 0.710

South overshot equality and became strongly dominant, so E fell.

### 1980 -> 1988

- total: 6.88x
- North: 2.62x
- South: 7.75x
- E ratio: 0.817

The new dominant South colony continued to amplify, so E fell further.

## Why this changes the general interpretation

A long-interval decrease in E does **not** require the initially dominant node to grow fastest throughout the interval.

There are at least two recovery-concentration routes:

### Persistent-dominance amplification

The same dominant node remains dominant and gains further share.

Example: Ross Island, Cape Crozier.

### Dominance-reversal amplification

A subordinate node grows so rapidly that it first equalizes the system and then overshoots, becoming the new dominant node.

Example: Heard Island, Spit Bay South.

Both can yield:

    N up
    all monitored nodes up
    endpoint E down.

But their spatial histories are fundamentally different.

## Consequence for monitoring

Endpoint N and endpoint E are not sufficient to reconstruct the recovery path.

A third quantity is needed:

    identity and turnover of the dominant breeding node.

For Heard, the dominant node changes from North to South.

For Ross, Crozier remains dominant.

This means two metapopulations can have the same signs of delta N and delta E while undergoing very different spatial reorganization.

## Count-comparability boundary

The historical series combines census codes and dates that are not identical across years.

The broad dominance reversal is much larger than the stated count uncertainty:

- 1963 and 1965: South was much smaller than North;
- 1969: nearly equal;
- 1980 onward: South was several-fold to >10-fold larger.

The case is therefore useful as qualitative/quantitative triangulation of the recovery-state geometry, not as a precision time-series estimate of annual E.

## Literature-mechanism context

Historical syntheses report that the south colony began smaller, then grew faster, while the north colony grew more slowly. They also suggest site shelter/sun exposure and immigration/local recruitment as possible contributors.

No single cause is established here.

The value of the Heard case is the spatial-demographic pattern: continuous numerical recovery can pass through equalization and then return to strong concentration under a new dominant colony.
