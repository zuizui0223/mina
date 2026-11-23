# Ross Island recovery mechanism audit v2

**Status:** corrected post-result mechanism audit. This supersedes V1. It does not convert any post-result mechanism into confirmatory evidence for the frozen Ross V2 effect test.

## Observed census pattern

Frozen Ross Island recovery, 2001 -> 2012:

- Cape Crozier: 67,114 -> 272,340 = **4.058x**
- Cape Bird: 26,317 -> 75,696 = **2.876x**
- Cape Royds: 1,367 -> 3,083 = **2.255x**

All three colonies increased, yet E3 declined 10.7%.

The process to explain is therefore **differential amplification**, not local disappearance or adult aggregation.

## What the 25-year individual study actually says

Dugger et al. (2026) estimated multiple age-, state-, and colony-specific vital rates from 1996-2020 mark-recapture data.

These rates do **not** reduce to one scalar "colony quality" ranking.

### Age-specific recruitment probability

At a given age, recruitment probability was:

    Crozier > Bird > Royds

with Crozier almost twice Royds and Bird intermediate.

This ordering matches the census multiplication-factor ordering.

### But realized cohort recruitment is different

Pre-breeder survival was highest at Bird.

Mean survival over the first two years after fledging was approximately:

- Royds: 0.43
- Bird: 0.55
- Crozier: 0.43

When survival and age-specific recruitment were combined for a hypothetical cohort of 1,000 chicks, the proportion recruited by age 14 was:

- Bird: **19.6%**
- Crozier: **13.6%**
- Royds: **9.8%**

Therefore the realized cohort-recruitment ranking is:

    Bird > Crozier > Royds

not Crozier > Bird > Royds.

The earlier V1 statement that recruitment was the single most concordant explanation was too strong.

### Breeding propensity

Among birds that had already recruited, breeding propensity was:

    Crozier > Royds > Bird.

This favors Crozier relative to Bird, but again does not reproduce the complete census multiplier ordering by itself.

### Movement

Movement among colonies was stage dependent:

- pre-breeders: up to roughly 12% depending on age and colony;
- breeders: below 0.20%.

Thus adult redistribution among colonies is unlikely to be the sole source of the large census allocation differences, although pre-breeder prospecting/dispersal is biologically non-negligible.

## Independent reproductive-success evidence

Schmidt et al. (2021) compared Cape Crozier and Cape Royds.

They found:

- higher mean reproductive success at Crozier;
- lower interannual variability at Crozier;
- lower within-year spatial variability at Crozier;
- strong effects of subcolony geometry and nesting habitat;
- a plausible positive feedback in which growing colonies have lower perimeter-to-area ratio and potentially lower edge-predation costs.

This favors Crozier relative to Royds, but Bird was not included, so it cannot supply a three-colony mechanistic ranking.

## Correct mechanism statement

No single measured vital rate currently explains the full Ross amplification ordering.

A safer demographic representation is:

    r_i(t)
      = shared regional forcing
      + survival contribution_i(t)
      + recruitment contribution_i(t)
      + breeding-propensity contribution_i(t)
      + reproductive-success contribution_i(t)
      + net movement_i(t)
      + residual

The census result only identifies the integrated outcome r_i.

The individual studies show that the components of r_i vary strongly among colonies, and in different rank orders.

Therefore the supported interpretation is:

> **Ross recovery was allocated unevenly because local demographic performance is multidimensional and colony specific; Crozier's amplification is concordant with high age-specific recruitment, breeding propensity, and reproductive success, but cannot be attributed to any one vital rate from the available evidence.**

## Relation to the exact spatial-redundancy identity

For E = 1 / sum(p_i^2),

    d log(E) / dt = 2 (r_bar - r_D).

Thus mechanism does not need to be collapsed to one vital rate.

Any combination of survival, recruitment, breeding propensity, reproduction, and movement that makes the dominance-weighted integrated growth rate exceed the abundance-weighted mean will reduce E.

For Ross recovery:

    Crozier is initially dominant
    + Crozier has the largest integrated census multiplication factor
    -> dominance-weighted growth exceeds aggregate growth
    -> E declines.

This is the exact demographic statement supported by the counts.

## Beaufort remains a distinct capacity case

At Beaufort, newly usable nesting habitat expanded and the small/new subcolony gained disproportionate share.

That case is consistent with a time-varying capacity release changing the allocation of growth.

But Ross versus Beaufort does **not** yet prove a two-mode causal law. The systems differ in multiple ways.

## Prior-work boundary

Southwell & Emmerson (2020) already demonstrated density-dependent limitation of Adélie growth by breeding-habitat availability in East Antarctica.

Dugger et al. (2026) already demonstrated colony-specific vital-rate mechanisms associated with divergent Ross trajectories.

Schmidt et al. (2021) already identified nesting-habitat and colony-geometry effects on reproductive success and proposed positive feedback with colony growth.

Therefore PR189's contribution is not the discovery that:

- capacity matters;
- Ross colonies have different demographic rates;
- large colonies can have demographic advantages.

The distinctive contribution is the **spatial-state decomposition**:

- decline concentration can arise by differential attrition;
- recovery concentration can arise by differential amplification;
- strong numerical recovery can lose abundance-weighted spatial redundancy even when every monitored breeding unit grows.

## What would close mechanism causally

A causal decomposition would require a common period and units linking annual census growth to annual or cohort-specific vital rates, ideally with:

1. survival;
2. recruitment;
3. breeding propensity;
4. reproductive success;
5. net movement;
6. breeding-capacity state.

The present public evidence is sufficient for mechanistic plausibility and falsification of single-rate explanations, not for formal mediation.
