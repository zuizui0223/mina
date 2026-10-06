# Configuration-memory allocation hypothesis v1

**Status:** post-result generated mechanism hypothesis. Not confirmatory for PR189.

## Prior-work boundary

This hypothesis does **not** claim novelty for Allee effects or hysteresis in Adélie penguins.

Prior work already shows:

- nest-site fidelity and slow spatial rearrangement can trap Adélie colonies in suboptimal "frozen herd" configurations;
- declining abundance can fragment nesting aggregations;
- edge-biased predation can create positive feedback that lowers reproductive success;
- Cape Royds has higher perimeter-to-area ratios, more edge exposure, lower/more variable reproductive success and slow post-iceberg recovery relative to Cape Crozier;
- local spatial configuration can therefore carry memory of past abundance.

The new generated question is one spatial level higher.

## Cross-scale question

Does **local configuration memory** affect how a region-wide improvement in breeding conditions is allocated among colonies?

In other words:

> after a shared disturbance, do colonies that retain compact/high-quality breeding configuration absorb more of the breeding rebound than colonies that have been fragmented, even at similar current breeding abundance?

This would propagate local hysteresis into metapopulation-scale spatial recovery.

## State variables

For colony i at time t:

    B_it = observed breeding-territory / breeding-pair abundance
    Z_it = spatial/social configuration
    K_it = usable breeding capacity
    Q_it = habitat / demographic quality
    R_t  = shared regional forcing
    M_it = net movement / recruitment contribution.

Useful Z components include:

- perimeter-to-area ratio;
- number of subcolonies;
- mean subcolony area;
- edge-nest fraction;
- nearest-neighbour / fragmentation metrics;
- fraction of historic nesting mounds occupied.

A minimal conceptual process is:

    Δ log B_it
      = f(B_it, Z_it, K_it, Q_it, R_t, M_it).

The key claim is that Z has predictive information beyond current B.

## H1 — branch dependence after disturbance

At similar current breeding abundance, a colony on the recovery branch after fragmentation should have a different configuration than the same colony/system had on the decline/pre-disturbance branch.

Generated direction:

    post-collapse / recovery branch
    -> higher fragmentation / perimeter-to-area ratio
    -> lower effective breeding quality.

Count-only Ross evidence already gives a weak cross-colony-network signature:

    1997: N = 204,837, E3 = 1.626
    2002: N = 203,996, E3 = 1.507

and:

    1985: N = 224,414, E3 = 1.625
    2004: N = 221,301, E3 = 1.413.

These matched-abundance comparisons are post-result and do not measure Z directly.

## H2 — configuration predicts rebound beyond current abundance

Primary prospective prediction:

> conditional on current breeding abundance and shared environmental conditions, more compact breeding configuration predicts stronger subsequent breeding rebound.

For local unit i:

    future_growth_i
      ~ current_abundance_i
      + configuration_i
      + environment
      + ...

Expected signs:

    lower perimeter/area -> higher future growth
    lower edge fraction -> higher future growth
    larger contiguous occupied patch -> higher future growth.

A null result after conditioning on B would reject the configuration-memory explanation.

## H3 — recovery threshold is configuration dependent

The relevant "Allee threshold" need not be a fixed pair count.

Instead, the effective threshold should vary with geometry and habitat.

Prediction:

> the abundance at which positive feedback begins should be lower for compact/high-quality nesting configurations and higher for fragmented/high-edge configurations.

Therefore do **not** freeze one universal numerical colony-size threshold.

## H4 — regional rebound should be spatially asymmetric

After a disturbance that reduces breeding participation across multiple colonies, rebound allocation should depend on pre-existing or disturbance-generated configuration.

If one already-dominant colony retains a favorable configuration while smaller colonies become fragmented:

    shared improvement
    -> larger rebound at favorable colony
    -> colony-level E can fall.

This is consistent with the Ross 2001 -> 2002 pattern but is not proven by it.

## H5 — capacity release can change the route

New contiguous usable nesting habitat can alter Z and K simultaneously.

Beaufort is consistent with:

    habitat release
    -> new/small breeding unit gains disproportionate share
    -> within-island E increases.

Thus configuration-memory hysteresis does not predict universal concentration.

A sufficiently strong capacity release may create an alternative high-quality node and redirect recovery.

## Ross shock-rebound interpretation

The Ross sequence is:

    1999 -> 2001
    iceberg disturbance
    all six breeding counts decline
    E rises
    -> shock-induced equalization

    2001 -> 2002
    all six breeding counts rebound
    Crozier rebounds most
    E falls sharply
    -> asymmetric breeding rebound

    2002 -> 2012
    continued growth
    E partially rises
    -> partial spatial re-expansion.

A configuration-memory mechanism could explain why rebound did not simply invert the shock arithmetic, but current count data alone cannot identify that mechanism.

## What would falsify this hypothesis

The hypothesis loses support if, in an independent or withheld spatial dataset:

1. prior/current configuration adds no predictive information for subsequent growth once current B and environment are controlled;
2. more fragmented/high-edge configurations recover as fast as or faster than compact configurations;
3. configuration changes track B essentially instantaneously, leaving no temporal memory;
4. observed branch dependence disappears when matched for environment and breeding participation.

## Best prospective design

Use a dataset with repeated spatial maps of occupied nesting units before and after a disturbance.

For each colony/subcolony-year:

- current breeding abundance;
- perimeter-to-area ratio;
- occupied area;
- fragmentation;
- reproductive success;
- next-year breeding abundance;
- snow/ice/access covariates;
- movement/recruitment if available.

Freeze the primary model before looking at future-growth outcomes:

    next-year log growth
      ~ current log abundance
      + configuration
      + environment
      + colony effects.

Primary generated prediction:

    compactness/configuration coefficient > 0 for subsequent recovery.

## Available same-system data

McDowall & Lynch (2019) provide a public Dryad archive for the frozen-herd analysis, and additional Ross demographic/reproductive datasets are public.

However, because the published study already demonstrates local configuration hysteresis, reanalysis of that same archive can only provide methodological linkage or effect-size extraction; it cannot serve as an independent novelty test.

The highest-value next test is therefore an independent colonial system or a temporally withheld Ross spatial series not used to formulate the mechanism.

## Claim ceiling

Current PR189 can say:

> the shock-rebound trajectory is consistent with configuration-mediated spatial memory, a mechanism already established at Adélie subcolony scale.

It cannot say:

> configuration memory caused the colony-level rebound allocation.

That causal link remains a prospective hypothesis.
