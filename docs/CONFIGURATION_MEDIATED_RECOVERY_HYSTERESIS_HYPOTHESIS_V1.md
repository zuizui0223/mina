# Configuration-mediated recovery hysteresis in colonial seabirds — generated hypothesis v1

**Status:** superseded by `CONFIGURATION_MEDIATED_RECOVERY_HYSTERESIS_HYPOTHESIS_V2.md`. V1 gave configuration-mediated memory too much prominence for the immediate Ross rebound before fully auditing the known colony-specific iceberg/access geometry.

## Biological question

Why can recovery of breeding abundance fail to retrace the spatial configuration present at similar abundance during decline?

A simple carrying-capacity model predicts that once regional conditions improve, depleted breeding nodes should refill toward their earlier composition.

Colonial breeding creates a reason this inverse path may fail.

Local demographic performance can depend on the **current spatial configuration and social density of breeders**, and those states can retain memory of past decline.

## Prior theory and evidence — not new

### Allee effects in colonial seabirds are established

Schippers et al. (2011) modeled positive density dependence in colonial seabirds and showed that strong Allee effects can create alternative local equilibria, restrict recolonization, and slow metapopulation expansion and recovery.

Mechanisms include:
- predator dilution / collective defense;
- information and foraging benefits;
- mating/social benefits at sufficient colony size.

Therefore this project does not claim to discover Allee effects.

### Adélie spatial hysteresis is already modeled directly

McDowall & Lynch (2019) showed that Adélie nesting aggregations can become a "frozen herd."

Their model demonstrates:
- decline can fragment nesting aggregations even in homogeneous habitat;
- edge-biased predation makes fragmentation demographically costly;
- nest-site fidelity and slow spatial rearrangement can trap colonies in suboptimal configurations;
- the response of colony spatial structure to abundance is hysteretic.

Therefore this project does not claim to discover spatial hysteresis in Adélie colonies.

### Cape Royds provides empirical consistency

Schmidt et al. (2021) found higher and less variable reproductive success at the larger Cape Crozier colony than at Cape Royds, with perimeter-to-area ratio the strongest subcolony-quality correlate.

They explicitly proposed that sharp decline at Royds increased fragmentation and the fraction of edge nests, allowing skua predation to hinder recovery and leaving the colony "frozen" in a suboptimal arrangement.

Again, this mechanism is prior evidence, not a new result of PR189.

### New-colony establishment can require sustained immigration

Herman & Lynch (2022) modeled four newly established Gentoo penguin colonies and found that rapid early growth required sustained immigration over multiple years.

They also noted that positive density dependence could increase local survival/reproductive success as a new colony grows, but immigration remained necessary to explain the observed establishment trajectories.

Thus successful founding cannot be reduced to an intrinsic Allee threshold alone.

## Generated scale-up hypothesis

The generated extension is:

> **Configuration-mediated positive density dependence can make regional breeding recovery path dependent: after a decline, fragmented or socially weak breeding nodes may remain demographically disadvantaged, so improving regional conditions are expressed disproportionately at nodes that retained favorable configuration or received enough immigration/capacity release to escape the low-performance state.**

This is a metapopulation allocation hypothesis.

It links within-colony spatial memory to among-colony spatial redundancy.

## State variables

For breeding node i, distinguish:

    B_i(t) = breeding-pair abundance
    Z_i(t) = configuration/social state
    K_i(t) = usable breeding capacity
    I_i(t) = net immigration input
    R_t    = regional environmental forcing.

Z can include:
- compactness;
- perimeter-to-area ratio;
- fraction of edge nests;
- fragmentation among subcolonies;
- local social density.

K is not geometric island area. It is the amount of currently usable breeding space.

## Minimal conceptual model

A local breeding-abundance change can be represented as:

    Delta log B_i
      = R_t
      + q_i
      + A_i(B_i, Z_i)
      - C_i(B_i / K_i)
      + M_i(I_i, B_i)
      + epsilon_i.

where:

- q_i = persistent local demographic quality;
- A_i = positive density/configuration effect at low-to-intermediate state;
- C_i = crowding/resource cost as usable capacity fills;
- M_i = contribution of movement/immigration.

The key source of hysteresis is that Z is slow:

    Z_i(t+1) != Z_opt(B_i(t+1))

immediately.

A rapid decline can therefore move B downward faster than nests can spatially reorganize, leaving a fragmented, edge-rich configuration.

When regional conditions improve, the same B can have a different Z than it had on the declining branch.

## Connection to the Ross matched-abundance result

Post-result branch matching shows:

### ~204,000 breeding pairs

Decline 1997:

    N = 204,837
    E3 = 1.626
    Crozier share = 74.9%.

Recovery 2002:

    N = 203,996
    E3 = 1.507
    Crozier share = 79.0%.

### ~222,000 breeding pairs

Decline 1985:

    N = 224,414
    E3 = 1.625
    Crozier share = 74.7%.

Recovery 2004:

    N = 221,301
    E3 = 1.413
    Crozier share = 82.5%.

Thus approximately equal total breeding abundance does not imply the same breeding distribution.

This is consistent with branch dependence.

It does **not** establish configuration-mediated endogenous hysteresis, because the environmental states differ between branches.

## Connection to the 2001 iceberg disturbance

The Ross response variable is breeding-pair abundance, not total adult abundance.

Lyver et al. (2014) identify the 2001 common low point with the B-15A/C-16 iceberg disturbance and report widespread early breeding failure/abandonment.

Therefore the early 2001-2002 concentration pulse may combine:

- recovery of breeding participation;
- survival/recruitment;
- movement;
- local environmental accessibility;
- spatial configuration feedback.

The generated hypothesis is explicitly about how these processes are **allocated spatially**, not about one-year adult population multiplication.

## Heard Island as an Allee-like triangulation

Historical King penguin work summarized for Heard Island reports that very small colonies (roughly <=150 pairs in the cited subantarctic studies) produced few or no fledglings because small chick groups were vulnerable to giant petrels, whereas colonies of several hundred pairs had much better recruitment potential.

At Spit Bay:

    South: 5 -> 9 -> 37 -> 400 -> 3,100
    North: 13 -> 36 -> 49 -> 82 -> 215.

South crossed from a tiny breeding unit to several hundred pairs and then became dominant.

This is qualitatively compatible with positive density-dependent acceleration.

The numeric threshold is species/site specific and must **not** be transferred to Adélie or Gentoo penguins.

## Beaufort as a capacity-release contrast

At Beaufort, glacial retreat increased usable breeding space.

A small/new subcolony began with 460 pairs and grew disproportionately relative to the established main colony.

This suggests that dynamic capacity release can create an alternative route out of concentration:

    capacity release
    + sufficient founders / immigration
    -> viable low-share node
    -> spreading of breeding abundance.

It does not prove an Allee threshold.

## Five generated predictions

### P1 — branch dependence at matched breeding abundance

For the same total or local breeding abundance, a recovering system should retain a spatial/configuration penalty after sharp decline if spatial reorganization is slow.

Prediction:

    E_recovery(N) != E_decline(N)

and, at finer resolution,

    configuration_recovery(B) != configuration_decline(B).

Ross provides post-result consistency at the metapopulation scale.

A prospective test must freeze matched-abundance rules before opening the outcome.

### P2 — configuration predicts recovery beyond current size

Among breeding nodes with similar current B_i, nodes that are:
- more compact;
- less fragmented;
- lower in perimeter-to-area ratio;
- lower in relative edge exposure

should show higher subsequent breeding success or breeding-abundance recovery.

This is the clearest test of configuration-mediated memory rather than simple size dependence.

### P3 — regional recovery is allocated to nodes above the low-performance state

During a positive regional phase, proportional residual growth should be larger at nodes with favorable Z_i or strong local demographic performance.

At the metapopulation level this can generate:

    breeding N up
    occupancy unchanged
    E down.

### P4 — founding requires both opportunity and demographic support

New usable capacity alone need not produce a persistent new breeding node.

A new node should require enough:
- immigrants/founders;
- local recruitment;
- social density / compactness

to avoid the low-density failure state.

This predicts sustained immigration during early establishment, consistent with the Gentoo establishment literature.

### P5 — capacity release can break recovery hysteresis

If new usable habitat allows breeders to assemble a sufficiently viable new node, recovery can spread rather than remain concentrated.

This predicts that abrupt positive K_i(t) changes can reverse the sign of the spatial-redundancy response, conditional on establishment success.

## What would falsify the scale-up mechanism

The hypothesis would be weakened if, in prospectively chosen systems:

- decline and recovery have the same spatial configuration at matched breeding abundance;
- past fragmentation/configuration adds no recovery information after current abundance and environment are controlled;
- local recovery allocation is unrelated to configuration, social density, immigration, or usable capacity;
- low-density fragmented nodes recover just as rapidly as intact nodes under comparable external conditions.

## Why this is not merely "Allee effects matter"

The novel target, if confirmed, is not the existence of positive density dependence.

It is a **cross-scale consequence**:

    local spatial memory / positive density dependence
        ->
    asymmetric allocation of regional recovery
        ->
    delayed or non-monotonic restoration of breeding-network redundancy.

That linkage is currently generated, not established.

## Relation to the paper

The focal empirical paper can remain about:

    decline and recovery are not spatial inverses.

Configuration-mediated recovery hysteresis belongs in the Discussion as a mechanistic explanation and next hypothesis.

It should not replace the frozen Ross result as the main result until tested prospectively.
