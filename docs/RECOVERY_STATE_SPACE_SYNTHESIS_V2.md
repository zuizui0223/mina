# Breeding-recovery state space v2: abundance, redundancy, and dominance identity

**Status:** superseded by `RECOVERY_STATE_SPACE_SYNTHESIS_V3.md`. V2 treated Ross 2001-2012 as a single recovery trajectory; V3 incorporates the 2001 iceberg-shock baseline and separates shock, immediate rebound, and longer recovery.

## Why V2 is needed

Ross Island and Heard Island can both be summarized over long intervals as:

    total abundance up
    every monitored breeding unit up
    effective breeding-unit number E down

but their spatial histories are not the same.

Ross:
- Cape Crozier is dominant at both endpoints;
- Crozier gains additional share;
- concentration strengthens around the same node.

Heard:
- Spit Bay North is initially dominant;
- South catches up;
- the two are nearly balanced;
- South overtakes North;
- concentration then strengthens around a different node.

Therefore N and E alone do not uniquely describe spatial recovery.

## Three recovery coordinates

At minimum, characterize a colonial metapopulation by:

### 1. Total breeding abundance

    N = sum_i n_i.

### 2. Abundance-weighted spatial redundancy

    E = 1 / sum_i p_i^2.

### 3. Compositional identity

Track:
- identity of the dominant node;
- whether dominant identity changes;
- total-variation distance between starting and ending shares:

    TV = 0.5 * sum_i |p_i1 - p_i0|.

TV is not a replacement for E. It measures how much composition moved, while E measures how even or concentrated composition is.

## Focal examples

### Ross Island recovery

2001 -> 2012:

    N: 94,798 -> 351,119
    E3: 1.729 -> 1.543
    TV = 0.0677
    dominant: Crozier -> Crozier.

Classification:

    persistent-dominance amplification.

### Heard Island Spit Bay recovery

1963 -> 1988:

    N: 18 -> 3,315
    E: 1.670 -> 1.138
    TV = 0.6574
    dominant: North -> South.

Classification:

    dominance-reversal amplification.

### Beaufort recovery

2004 -> 2010:

    N: 48,185 -> 64,717
    E: 1.019 -> 1.030
    TV = 0.00524
    dominant: main colony -> main colony.

Classification:

    weak within-island spreading.

## Same endpoint signs, different paths

Ross and Heard both occupy the endpoint quadrant:

    delta N > 0
    delta E < 0.

But:

    Ross = low compositional turnover, retained dominant identity
    Heard = high compositional turnover, reversed dominant identity.

This proves that the signs of delta N and delta E do not reconstruct recovery history.

## Heard also shows non-monotonic redundancy

Observed Spit Bay sequence:

| year | total | E | dominant |
|---|---:|---:|---|
| 1963 | 18 | 1.670 | North |
| 1965 | 45 | 1.471 | North |
| 1969 | 86 | 1.962 | North, weak |
| 1980 | 482 | 1.393 | South |
| 1988 | 3,315 | 1.138 | South |

Total abundance rises at every observed step.

E does not.

A recovering system can therefore pass through a transient maximum of spatial redundancy and subsequently reconcentrate.

## Relation to existing recovery theory

Spatial metapopulation recovery theory already shows that aggregate abundance can recover while:
- patch occupancy remains depressed;
- local patches remain collapsed;
- regional production remains below nonspatial expectations.

The Ross/Heard cases identify an additional dimension.

Even when occupancy is unchanged and every monitored breeding count increases, the abundance distribution among those nodes can:
- become more concentrated;
- change dominant identity;
- move non-monotonically through time.

Thus recovery monitoring should distinguish:

    abundance recovery
    occupancy recovery
    redundancy recovery
    compositional/dominance recovery.

## Demographic geometry

Instantaneously:

    d log(E)/dt = 2(r_bar - r_D).

This determines whether abundance becomes more or less even at that moment.

Over long intervals, however, dominance can reverse.

Therefore a long-interval E decline can arise by:

1. persistent-dominance amplification;
2. dominance reversal followed by amplification of the new dominant;
3. mixed trajectories that cross equality multiple times.

The exact finite-interval identity remains valid, but endpoint E alone does not identify which path occurred.

## Ecological mechanisms

Different paths can arise from different combinations of:

- local survival;
- recruitment;
- breeding propensity;
- reproductive success;
- immigration/emigration;
- dynamic breeding capacity;
- habitat release or loss;
- density-dependent social or edge effects.

No single mechanism is implied by E.

## Island-ecology interpretation

Island structure matters here not only as isolation or geometric area.

For colonial breeders, an island contains a network of breeding nodes whose:
- usable capacity changes;
- local demographic return differs;
- dominance can persist or turn over.

The useful island-level question becomes:

> how does dynamic capacity and local demographic performance determine the trajectory of abundance across the internal breeding-node network and across island boundaries?

This is distinct from a static area -> carrying capacity -> species-richness framing.

## Current empirical support

Frozen focal result:
- Ross breeding-pair recovery fails to restore spatial redundancy, with no endpoint decline in any monitored breeding count.

Independent post-result triangulation:
- Heard king-penguin recovery shows the same endpoint sign combination under a different species and island, but through dominance reversal.

Contrasting case:
- Beaufort within-island recovery weakly increases E after habitat release.

## Claim ceiling

Supported:

> numerical recovery of breeding abundance can be spatially non-monotonic and can reduce abundance-weighted redundancy even when every monitored breeding-unit count increases.

Supported by Ross + Heard triangulation:

> the loss of redundancy can occur either by amplification of an existing dominant node or by replacement of the dominant node during recovery.

Not yet externally established:

> a general predictor that determines which recovery path a metapopulation takes.

Dynamic breeding capacity and multidimensional local demographic performance remain the leading generated mechanism candidates.
