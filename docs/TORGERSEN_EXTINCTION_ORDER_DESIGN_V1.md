# Torgersen Adélie extinction-order route v1

**Status:** pre-data dynamic-process route. Independent follow-up only; it must not delay, reframe, or rescue Paper 1.

## Biological question

As an Adélie penguin breeding network collapses within an island, **what determines which sub-colony disappears next?**

Published Torgersen results already establish that static habitat matters: small historic sub-colonies disappear earlier and south-facing sub-colonies have higher extinction risk. Those effects are not new endpoints here.

The new process question is whether **loss of nearby occupied sub-colonies creates dynamic functional isolation that adds predictive information beyond static habitat quality.**

## Generated hypothesis

For focal sub-colony i in year t, define the nearest still-active neighboring historic sub-colony distance

D_i(t) = min_j d_ij among j active immediately before year t.

If local social/network connectivity matters, extinction hazard should increase as D_i(t) increases after neighboring sub-colonies disappear.

Primary directional prediction:

> greater dynamic nearest-active-neighbor distance predicts earlier next extinction after accounting for historic sub-colony area and north/south aspect.

This is a penguin population-process hypothesis. Island topography sets baseline habitat quality; dynamic breeder configuration modifies effective isolation through time.

## Why this is not a retest of the published result

Already known from Cimino et al. 2025:
- 23 historic Torgersen sub-colonies;
- 18 extinct by 2022;
- all historic south-aspect sub-colonies extinct;
- larger historic sub-colonies generally disappear later;
- area–extinction-year correlation is positive.

Those findings are treated as known covariates/context.

The new endpoint requires the **spatial relation among individual historic sub-colonies and their extinction order**, which was not the published hypothesis.

## Stage A — data bridge only

Before any dynamic-connectivity statistic is computed, establish whether public material contains a machine-readable bridge with:

1. stable historic sub-colony identifier;
2. extinction year or annual presence/count series for that same identifier;
3. historic area;
4. north/south aspect;
5. polygon or centroid geometry in a common coordinate system.

Permitted Stage A inspection:
- supplement file structure;
- table names, headers, dimensions;
- archive file names;
- shapefile/GeoPackage layer names and schemas;
- identifiers and coordinate-reference metadata.

Not permitted before the bridge is frozen:
- calculating inter-subcolony distances;
- computing dynamic connectivity;
- fitting extinction models;
- choosing a distance radius after seeing outcomes.

If geometry and extinction identity cannot be bridged exactly from public data, this route stops. Do not digitize Fig. 5 by hand and do not infer polygon identities visually.

## Stage B — support gate

If Stage A succeeds, count only:
- number of historic sub-colonies with complete ID + extinction/censoring + area + aspect + geometry;
- number of observed extinction events;
- number of distinct extinction years;
- number of events for which at least two other sub-colonies remain at risk.

Proceed only if:
- >=18/23 historic sub-colonies have the complete bridge;
- >=12 extinction events are usable;
- >=6 distinct extinction years;
- >=10 extinction events occur while at least two alternatives remain at risk.

No effect estimates are opened at this stage.

## Stage C — frozen primary model

If Stage B passes, freeze before calculating distances:

Primary time-varying predictor:
- log1p nearest-active-neighbor distance immediately before each risk year.

Known static controls:
- log historic sub-colony area;
- binary south aspect.

Primary model:
- discrete-time extinction hazard or Cox model, chosen before distance values are opened based only on temporal sampling structure.

Primary test:
- coefficient for dynamic isolation > 0.

No alternate radii, graph thresholds, k-nearest-neighbor grids, or connectivity kernels are searched.

## Calendar-time / common-decline safeguard

Dynamic isolation inevitably tends to increase as the island-wide network shrinks. To avoid mistaking secular decline for a local cascade, the model must also include exactly one predeclared common-state control:
- calendar year if only extinction-year data are available; or
- total Torgersen breeding abundance if annual total abundance can be bridged without outcome-informed choices.

Choice is made at Stage A from data support, before dynamic distances are computed.

The dynamic-isolation claim is supported only if its coefficient remains positive after the static controls and common-state control.

## Predictive test

Mechanistic interpretation requires more than an in-sample coefficient.

If support permits, use leave-one-extinction-event-out ranking:
at each extinction year, use only information available immediately before that event to rank the colonies still at risk. Report the percentile rank of the colony that actually disappears.

A useful process must rank the next extinction better when dynamic isolation is included than with area + aspect + common state alone.

## Interpretation

Supported result:
> As the Torgersen Adélie network contracted, loss of neighboring occupied sub-colonies increased effective isolation and improved prediction of which sub-colony disappeared next beyond static habitat susceptibility.

Not supported:
- individual penguins consciously following a social-information rule;
- inter-island dispersal;
- causality from conspecific attraction specifically;
- a universal Antarctic cascade law.

The result would identify a population-level spatial feedback compatible with a rescue/social-connectivity mechanism.

## Stop rule

No hand digitization from figures, no post-outcome distance threshold search, no alternate sub-colony matching, and no use of the Palmer LTER colony-code crosswalk unless a source-provided exact identifier bridge is found.
