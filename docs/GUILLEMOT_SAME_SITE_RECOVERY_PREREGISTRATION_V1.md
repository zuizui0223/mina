# Guillemot same-site recovery preregistration v1

**Date:** 2026-10-05  
**Status:** frozen before opening the raw EIDC outcome values.

## Why this route exists

The Antarctic penguin analyses show that breeding-space concentration can persist or deepen even when abundance increases, but those data do not contain a prospectively frozen same-place loss/recovery test.

The Isle of May common guillemot data provide a different level of observation: individually mapped breeding sites nested within five long-term sub-colonies over 1981–2018.

The test asks one question only:

> **Does a previously used breeding site tend to be reoccupied only after the surrounding sub-colony has returned to a higher population state than the state at which that same site became vacant?**

## Literature boundary fixed before outcome opening

Bennett et al. (2022, Journal of Animal Ecology, doi:10.1111/1365-2656.13674) already established that:

- site quality predicts breeding-site occupancy;
- sub-colony size affects occupancy;
- the study spans population increase, decline and recovery;
- historically occupied sites can be distinguished from newly occupied sites;
- reoccupied and new sites were compared by trend phase and site quality.

The paper did **not** pair each site's transition to vacancy with its later reoccupation and test whether the surrounding population state differed between those two transitions.

Kokko et al. (2004) already established site-dependent population regulation in this same guillemot population.

Therefore novelty is **not** buffer effects, reoccupation, site fidelity, or density-dependent site use. The candidate contribution is the paired same-site state asymmetry.

## Data known before freeze

Only published metadata and methods were used to design this test:

- 1981–2018;
- five long-term sub-colonies;
- breeding sites have unique IDs assigned when first occupied;
- sites were mapped to allow consistent monitoring through time;
- sub-colony boundaries remained constant;
- the published series contains increase, decline and recovery.

No raw EIDC CSV values were inspected before this preregistration.

Dataset:
Bennett et al. (2022), EIDC DOI 10.5285/33b42f0a-12a5-47fe-aaaf-25f4ee5e13a5.

## State definition

For breeding site j in sub-colony c and year t,

[
N_{-j,t}=N_{c,t}-I_{j,t},
]

where (N_{c,t}) is the published sub-colony size and (I_{j,t}) is focal-site occupancy.

The focal site is therefore excluded from the population state used to explain its own transition.

## Completed vacancy-reoccupation spell

A primary eligible spell is

[
1 ightarrow 0 ightarrow cdots ightarrow 0 ightarrow 1.
]

Requirements:

- the site must already have been occupied, so first colonization is excluded;
- every year from the occupied pre-vacancy year through reoccupation is calendar-consecutive;
- site state must be observed for every included year;
- at least one complete vacant year is required;
- missing years terminate the candidate spell;
- repeated completed spells may occur at a site.

Annual site vacancy is the measured event. It is not assumed to mean permanent abandonment or disappearance of the same individual.

## Primary effect

For the transition to vacancy (t	o t+1),

[
A_v=rac{log(1+N_{-j,t})+log(1+N_{-j,t+1})}{2}.
]

For later reoccupation (u	o u+1),

[
A_r=rac{log(1+N_{-j,u})+log(1+N_{-j,u+1})}{2}.
]

Then

[
H=A_r-A_v.
]

Prediction:

[
H>0.
]

## Aggregation

To avoid treating repeated events from one site or one sub-colony as independent:

1. average repeated spells within site;
2. average site effects within sub-colony;
3. give each of the five sub-colonies equal weight.

Primary statistic:

[
T_{obs}=mathrm{mean}(H_c).
]

## Support gate before effect interpretation

The test proceeds only if the frozen raw-to-standardized mapping establishes:

- at least 30 completed spells;
- at least 20 distinct sites with completed spells;
- all five sub-colonies represented;
- at least three completed spells in each sub-colony;
- at least three valid non-circular offsets for every retained temporal-shift group.

If an absent site-year cannot be distinguished from a monitored but unoccupied site-year, the route stops.

## Confirmatory inference

Support requires all four conditions:

1. (T_{obs}>0);
2. exact one-sided sign-flip across the five sub-colony contributions gives (ple0.05);
3. observed (T) exceeds the median structured-shift null;
4. the 9,999-replicate structured non-circular common-offset null gives upper-tail (ple0.05).

### Temporal null

Spells are assigned to maximal calendar-consecutive state-complete blocks.

Within each sub-colony × identical block, calculate the intersection of all integer offsets that keep every transition year needed by every spell inside that same block.

For each null replicate, draw one common offset for that group and shift all its events together.

No circular wrapping is allowed.

This preserves the observed surrounding population trajectory and shared local temporal structure while breaking the specific alignment of vacancy/reoccupation events with that trajectory.

## Prespecified sensitivity

Repeat the identical analysis using only spells with at least two consecutive vacant years.

This is interpretive only. It cannot rescue a failed primary analysis.

Its purpose is to determine whether a supported primary result is also visible when one-year vacancy events, which may include temporary non-breeding, are removed.

## Decision language

If all confirmatory conditions pass:

> Previously used common-guillemot breeding sites were reoccupied at higher surrounding sub-colony population states than those associated with their earlier transition to vacancy, beyond generic temporal alignment with the observed sub-colony trajectory.

Program-level interpretation:

> Numerical recovery need not retrace prior breeding-site loss.

Do not claim:

- individual-level return thresholds;
- causal Allee effects;
- causal social attraction;
- permanent abandonment;
- seabird-wide generality from this single population.

## Integration with the penguin paper

If supported, the guillemot result is an independent same-place test of the hypothesis generated by the Antarctic penguin spatial results.

The combined logic is:

1. Antarctic penguins: spatial contraction is replicated and can persist while abundance grows;
2. common guillemots: test directly whether previously used places are recovered at a different local population state from that associated with vacancy.

If this test fails, the Antarctic penguin manuscript remains unchanged and no guillemot subgroup or phase-specific rescue is opened.

## Immutable after raw outcome opening

Do not change:

- site-state semantics;
- first-colonization exclusion;
- completed-spell definition;
- minimum support thresholds;
- leave-one-site-out population state;
- log1p transform;
- transition midpoint;
- aggregation hierarchy;
- equal-sub-colony weighting;
- exact sub-colony sign-flip;
- structured non-circular common-offset null;
- null replicate count or seed;
- the two-year-vacancy sensitivity definition.
