# Generated hypothesis: colonial hysteresis redistributes recovery among breeding nodes v1

**Status:** post-result generated hypothesis. This is not a result of PR189 and must not be presented as confirmatory.

## Motivation

Ross Island shows:

1. a shared mega-iceberg shock that reduces occupied breeding territories across all frozen components;
2. temporary compositional equalization at the shock trough;
3. a strongly unequal immediate rebound, concentrated at Crozier;
4. slow long-term recovery at Royds relative to Bird and Crozier.

Independent work already shows that:

- Adélie subcolonies fragment as abundance declines;
- high perimeter-to-area ratio is associated with lower reproductive success;
- Cape Royds has more edge-dominated subcolonies and lower/more variable reproductive success than Cape Crozier;
- individual-based models with nest-site fidelity produce a hysteretic "frozen herd" in which fragmented nest configurations can persist after the original decline.

Therefore **Allee effects and hysteresis themselves are prior knowledge**.

The new generated question is whether those local colonial feedbacks scale up to determine how metapopulation recovery is allocated among breeding nodes.

## Hypothesis

> A disturbance that pushes some breeding nodes into fragmented, low-performance configurations can make subsequent metapopulation recovery spatially path dependent: growth is preferentially expressed at nodes that remain above the colonial-performance threshold, so regional abundance can rebound without proportional restoration of the damaged nodes.

## Mechanistic sketch

For breeding node i:

    realized breeding growth_i
      = external recovery forcing
      x accessible capacity_i
      x colonial configuration feedback_i
      x demographic state_i.

The colonial configuration feedback may depend on:

- subcolony size;
- perimeter-to-area ratio;
- edge predation;
- nest-site fidelity;
- local information/social attraction.

After a sufficiently strong decline:

    abundance down
    -> fragmentation / more edge
    -> lower reproductive success
    -> slower local rebuilding
    -> persistent spatial memory.

This creates hysteresis: the path back is not the reverse of the path down.

## Ross predictions generated from this hypothesis

These are post-result explanatory predictions and are not independent tests in the current Ross data.

### P1 — small damaged nodes recover more slowly after common release

After a shared disturbance relaxes, colonies/subcolonies with stronger fragmentation and edge exposure should show lower subsequent occupied-territory growth than compact nodes, after controlling for initial count.

### P2 — geometry mediates part of local recovery

Within a colony through time:

    decline -> higher perimeter/area or greater fragmentation
    -> lower reproductive success
    -> slower recovery.

The key variable is actual occupied geometry, not total geometric island area.

### P3 — hysteresis is strongest where nest-site fidelity is high

If individuals rarely reorganize among nest sites, a fragmented configuration should persist longer after environmental conditions improve.

### P4 — capacity release can bypass the trap

If environmental change exposes new high-quality nesting space that can seed a sufficiently large breeding unit, recovery may be redirected toward that node rather than rebuilding a fragmented old configuration.

Beaufort is qualitatively consistent with this possibility, but is not a test.

## Heard Island connection

Historical king-penguin work reports strong positive density dependence in small colonies and poor fledging at very small colony sizes.

Spit Bay South increased from a small subordinate colony to the dominant colony during long-term recovery.

This is qualitatively compatible with threshold-like colonial feedback, but the historical case does not provide the spatial-geometry or individual data needed to test the mechanism.

## What would be novel

Not:

- "colonial seabirds have Allee effects";
- "penguin colonies show hysteresis";
- "edge nests have lower success";
- "small colonies can recover slowly".

Potentially novel:

> **local colonial hysteresis as a mechanism that redistributes regional recovery among breeding nodes, creating a mismatch between aggregate recovery and local spatial restoration.**

This moves the established within-colony frozen-herd mechanism up one organizational level to metapopulation recovery.

## Decisive test

A prospective test should use multiple disturbed breeding nodes with repeated spatial maps.

For each node measure before, during and after disturbance:

1. occupied abundance;
2. subcolony fragmentation/perimeter-to-area ratio;
3. reproductive success;
4. usable nesting capacity;
5. local recruitment/breeding propensity if available.

Primary prediction:

    post-disturbance recovery rate
      decreases with disturbance-induced fragmentation,
      conditional on pre-disturbance abundance and external forcing.

Mediation prediction:

    disturbance
      -> fragmentation
      -> reproductive success
      -> local recovery.

A multi-island or multi-colony replication is required before treating this as a general island-ecology mechanism.

## Boundary

The current Ross count series does not directly measure subcolony geometry in 1999-2002.

The hypothesis is therefore generated from the combination of:
- frozen census response;
- independent Ross habitat/reproductive-success studies;
- prior frozen-herd theory.

No causal hysteresis claim is made from PR189 alone.
