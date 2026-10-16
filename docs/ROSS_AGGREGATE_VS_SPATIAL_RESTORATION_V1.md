# Ross Island aggregate versus spatial restoration v1

**Status:** post-result decomposition of the documented 1999 -> 2001 mega-iceberg shock and 2001 -> 2002 breeding rebound.

## Question

Did the immediate rebound restore the losses caused by the shock in reverse?

Use:

- 1999 = last complete pre-shock six-component census;
- 2001 = documented common breeding-disturbance trough;
- 2002 = immediate rebound census.

The response is occupied breeding territories / breeding-pair abundance, not total adult abundance.

## Aggregate loss and rebound

1999 total:

    207,411

2001 total:

    94,798

Shock loss:

    112,613 breeding pairs / occupied territories.

2002 total:

    203,996

Rebound gain from 2001:

    109,198.

Thus the immediate rebound restored:

    109,198 / 112,613 = 96.97%

of the aggregate count lost between 1999 and 2001.

Equivalently:

    N_2002 / N_1999 = 98.35%.

At the aggregate level, breeding abundance was therefore almost back to the last complete pre-shock benchmark after one rebound interval.

## But local restoration was highly unequal

Define for each fixed breeding unit:

    loss_i = n_i,1999 - n_i,2001

    regain_i = n_i,2002 - n_i,2001

    restoration_fraction_i = regain_i / loss_i.

If rebound exactly retraced the shock, every restoration fraction would equal 1.

### Three biological colonies

| colony | shock loss | rebound gain | fraction of loss restored | 2002 minus 1999 |
|---|---:|---:|---:|---:|
| Cape Royds | 2,253 | 872 | **38.7%** | -1,381 |
| Cape Bird | 21,033 | 14,361 | **68.3%** | -6,672 |
| Cape Crozier | 89,327 | 93,965 | **105.2%** | +4,638 |

Crozier alone overshot its 1999 breeding count by 2002.

### Six frozen census components

| component | shock loss | rebound gain | fraction restored |
|---|---:|---:|---:|
| Cape Royds | 2,253 | 872 | **38.7%** |
| Cape Bird South | 4,515 | 487 | **10.8%** |
| Cape Bird Middle | 1,499 | 523 | **34.9%** |
| Cape Bird North | 15,019 | 13,351 | **88.9%** |
| Cape Crozier West | 80,216 | 88,054 | **109.8%** |
| Cape Crozier East | 9,111 | 5,911 | **64.9%** |

The dominant Crozier West component overshot its pre-shock abundance while several other components restored only a small fraction of their losses.

## Spatial restoration conditional on nearly restored total N

If the 2002 total breeding abundance had simply restored the **1999 composition** at its slightly lower total N, expected three-colony counts would be:

- Royds: 3,560
- Bird: 46,570
- Crozier: 153,865.

Observed 2002 minus that composition-preserving expectation:

- Royds: **-1,321**
- Bird: **-5,892**
- Crozier: **+7,214**.

Thus the remaining 1.65% aggregate shortfall does not explain the compositional difference.

At six-component scale, the largest conditional residual is:

- Cape Crozier West: **+10,133**

while Cape Bird South is:

- **-3,836**.

## Redundancy restoration

Although total breeding abundance returned to 98.35% of the 1999 value:

    E3_2002 / E3_1999 = 0.9366
    E6_2002 / E6_1999 = 0.8848.

So the immediate rebound restored aggregate breeding abundance much more closely than it restored abundance-weighted spatial redundancy.

Three-colony total-variation distance between 1999 and 2002 shares:

    TV3 = 0.03536.

Six-component total-variation distance:

    TV6 = 0.04967.

## Direct test of inverse-path recovery

A literal inverse path would require:

    regain_i = loss_i

for every local unit.

That is strongly contradicted descriptively.

Instead:

    shock:
    local losses are heterogeneous

    rebound:
    local gains are also heterogeneous
    but not in the inverse proportions.

The aggregate can therefore nearly recover while the spatial allocation does not.

## Ecological interpretation

The strongest empirical statement from the immediate Ross shock/rebound is:

> **Nearly all aggregate breeding abundance lost during the 1999–2001 disturbance was regained by 2002, but it was regained in different places: Crozier overshot its pre-shock count while Royds and Bird remained below theirs.**

This is more direct than describing the interval only as an E decline.

It shows that aggregate restoration and spatial restoration are distinct recovery properties.

## Measurement boundary

The rebound cannot be read as births or population growth one-for-one.

The aerial count measures occupied breeding territories near incubation, so the rebound can contain:

- resumed breeding participation;
- reduced abandonment;
- survival;
- recruitment;
- immigration/emigration.

The spatial restoration result is exact for the measured breeding counts regardless of which vital rates produced them.

## Claim boundary

Supported:

- aggregate breeding abundance was nearly restored by 2002;
- local restoration fractions differed strongly;
- Crozier overshot while Royds and Bird remained below pre-shock values;
- composition and E were not restored in proportion to aggregate N.

Not supported:

- endogenous hysteresis as the sole cause;
- total adult abundance returned to 98%;
- all local differences were caused by social configuration.

The known iceberg/access geometry provides an important exogenous mechanism for the early asymmetry.


## How different is the rebound from an exact inverse path?

The broad loss and rebound vectors are actually strongly aligned because Cape Crozier West dominates both:

    cosine(loss, rebound) = 0.99695.

Therefore the result should **not** be described as a wholesale relocation of the breeding network.

A more interpretable exact-inverse baseline is:

1. retain the observed aggregate rebound of 109,198;
2. allocate that rebound across the six components in proportion to each component's 1999->2001 shock loss.

Under this baseline, the observed rebound differs by:

    10,270.6 breeding pairs

in half-L1 allocation distance.

That equals:

    9.41%

of the entire observed rebound.

All of the balancing positive excess is at Cape Crozier West:

    +10,270.6

relative to exact proportional reversal.

The other five components are below their inverse-path allocations.

Thus the correct effect-size statement is:

> **The rebound recovered almost the full aggregate loss and broadly followed the spatial footprint of the shock, but roughly one tenth of rebound abundance was redistributed relative to an exact inverse path, disproportionately toward Cape Crozier West.**

This is a moderate but highly structured spatial mismatch, not a complete reorganization.
