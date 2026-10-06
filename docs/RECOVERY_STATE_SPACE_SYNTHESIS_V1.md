# Recovery state space: abundance and spatial redundancy are separate axes

**Status:** conceptual synthesis after the frozen Ross V2 result, Beaufort proportional correction, mechanism V2 audit, and literature positioning.

## Core idea

A population has at least two distinct recovery coordinates:

1. total abundance, N;
2. abundance-weighted spatial redundancy, E.

For a fixed set of breeding units,

    E = 1 / sum_i p_i^2

with p_i = n_i / N.

The two coordinates need not move together.

## Four demographic states

### I. N down, E down — concentrating decline

Dominant units lose less than the system average.

Typical arithmetic:

    widespread loss
    + unequal attrition
    -> surviving/dominant units gain share
    -> E down

Palmer/Signy provide the strongest empirical example in the current program.

Ross 1985-1999 shows the same direction weakly at the three-colony scale and much more strongly at the six-component scale.

### II. N down, E up — equalizing decline

Dominant units lose more rapidly than smaller units.

Total abundance declines, but relative abundance becomes more even.

This quadrant is biologically possible and must not be mislabeled as spatial recovery without considering the loss in N.

No special label is frozen for it yet.

### III. N up, E down — concentrating recovery

Already dominant units grow more rapidly than the metapopulation average.

Typical arithmetic:

    all or most units grow
    + unequal amplification
    -> dominant unit gains share
    -> E down

Ross 2001-2012 is the key empirical example:

- N +270%;
- 3/3 colonies increased;
- 6/6 census components increased;
- E3 -10.7%;
- E6 -14.0%.

This is **differential amplification**.

Descriptive phrase:

> hidden concentration during recovery

This phrase is not claimed to be established terminology.

### IV. N up, E up — spreading recovery

Smaller or newly available units grow disproportionately.

Typical arithmetic:

    total abundance grows
    + growth allocated toward low-share units
    -> E up

Corrected Beaufort 2004-2010 lies in this quadrant at the two-unit within-island scale.

## Exact boundary between the E-up and E-down states

With instantaneous local growth rates r_i,

    d log(E) / dt = 2 (r_bar - r_D)

where:

    r_bar = sum_i p_i r_i

and

    r_D = sum_i [p_i^2 / sum_j p_j^2] r_i.

Therefore the vertical boundary in this state space is not set by total population growth.

It is set by whether the integrated growth rate of dominant units is above or below the population-average growth rate.

This is why states I and III can have the same E direction despite opposite signs of N.

## Why this is different from hidden collapse

Existing metapopulation recovery theory includes "hidden collapse": aggregate abundance returns while some local populations remain collapsed or patch occupancy remains reduced.

Ross recovery is a different failure mode of aggregate-only monitoring:

- no frozen colony disappeared;
- no frozen component declined over the endpoint interval;
- every monitored unit increased;
- nevertheless, abundance became more concentrated.

Thus occupancy and abundance both indicate recovery, while abundance-weighted redundancy deteriorates.

Three axes should therefore be kept distinct:

    abundance
    occupancy
    abundance-weighted spatial redundancy.

## What island ecology adds

Classical equilibrium island biogeography uses area as a broad surrogate for carrying capacity.

The General Dynamic Model later made island carrying capacity explicitly time dependent through island ontogeny, changing area, elevation, topographic complexity, and habitat diversity.

For Adélie penguins, East Antarctic work further shows that realized breeding-habitat availability can constrain population growth through density dependence at ecological time scales.

PR189 therefore does not introduce dynamic island capacity as a general idea.

Its useful downscaled question is:

> how do dynamic breeding capacity and colony-specific demographic performance allocate population change among breeding nodes within and between islands?

The response variable is not species richness. It is the spatial allocation of breeders within a metapopulation.

## Static architecture versus dynamic state

The current mina Paper 2 analysis found no confirmatory, scale-invariant rule linking static breeding-landscape area/heterogeneity to demographic coupling across Pygoscelis species.

PR189 points toward a different class of predictor:

- current usable breeding capacity;
- current occupancy relative to that capacity;
- age/state-specific recruitment;
- breeding propensity;
- reproductive success;
- net movement;
- recent habitat release or loss.

These are dynamic state variables rather than static island descriptors.

This distinction is now central:

    geometric island area != usable breeding capacity
    usable capacity != demographic quality
    demographic quality != realized growth allocation.

## Ross and Beaufort as contrasting cases

### Ross Island

No single vital rate explains the full three-colony amplification order.

However, multiple demographic components vary strongly among colonies, and Crozier combines high age-specific recruitment, high breeding propensity, and high/less-variable reproductive success.

The integrated outcome is:

    dominant colony grows fastest
    -> differential amplification
    -> E down.

### Beaufort Island

Glacial retreat released usable nesting habitat.

A small/new breeding unit grew much faster than the established main colony and gained more share than expected under proportional growth.

The integrated outcome is:

    new capacity receives growth
    -> spatial spreading within island
    -> E up.

Published movement evidence also indicates reduced export to Ross Island as local habitat became available.

The contrast motivates, but does not prove, a capacity-allocation mechanism.

## Generated general hypothesis

For a recovering colonial metapopulation, the direction of spatial redundancy change depends on where positive local demographic growth is located relative to the current abundance distribution.

More specifically:

> recovery concentrates when persistent demographic advantage is positively aligned with existing dominance; recovery spreads when new or under-used capacity creates sufficiently high growth in low-share nodes.

This prediction is stronger than "large colonies grow more" because it allows capacity release to reverse the sign.

## What an independent test must measure

A decisive external test needs, for several regional metapopulations:

1. fixed local breeding-unit roster;
2. repeated abundance counts;
3. initial abundance shares;
4. local multiplication factors;
5. usable breeding-capacity state or change;
6. ideally local vital rates or movement.

Primary response:

    delta log(E).

Primary demographic predictor:

    dominance-weighted growth minus aggregate growth.

Mechanism predictor:

    alignment of residual capacity / demographic quality with initial dominance.

## Failed external route

The frozen Southwell et al. (2015) East Antarctica 99-site V1 route cannot compute the required E endpoint from its specified S1 source because that file does not expose paired historical and recent site-level standardized abundance.

That route remains SUPPORT FAIL. No substitute statistic is introduced.

## Current paper-level claim ceiling

Supported:

> strong numerical recovery can erode spatial redundancy through differential amplification even when every monitored breeding unit grows.

Supported across phases/cases in this program:

> spatial concentration is not a diagnostic of decline; it can be generated by unequal losses during decline or unequal gains during recovery.

Generated but not externally established:

> dynamic breeding capacity determines whether recovery amplifies dominance or spreads across breeding nodes.
