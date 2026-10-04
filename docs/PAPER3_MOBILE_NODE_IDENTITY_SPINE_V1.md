# Paper 3 spine v1 — mobile breeding islands and population-node identity

**Status:** prospective design; no movement-coordinate outcome has been opened in `mina`.  
**Branch:** `research/emperor-mobile-islands-v1`  
**Parent program:** `docs/ANTARCTIC_ISLAND_ECOLOGY_PROGRAM_V1.md`

## Core question

> **What is a “population site” when the breeding substrate itself is mobile?**

Paper 1 asked how breeding space contracts within persistent breeding systems.  
Paper 2 asked whether changing terrestrial opportunity redirects breeding use among persistent sites.

Emperor penguins create a different island-ecology problem. Their breeding node can be fast ice, ice shelf or other transient frozen substrate, and the geographic position of a named colony can move during a breeding season and between years.

The new question is therefore not whether emperor colonies move; that is already established.

The question is:

> **How much colonization/extinction turnover would a fixed-coordinate monitoring framework infer from a biological colony whose identity actually persists while its breeding node moves?**

This treats colony identity and geographic site identity as separable state variables.

## Why this is not a reanalysis of Macdonald et al. 2026

Macdonald et al. tracked the year-round movement of Atka Bay, Coulman Island and Cape Washington from 2017–2024 and quantified movement through the breeding season.

Paper 3 does not claim novelty for:
- detecting the colonies in winter SAR;
- showing that colonies move;
- seasonal movement distances;
- movement away from the fast-ice edge.

Instead, those published trajectories are used as a natural experiment on **monitoring-unit identity**.

Fretwell et al. 2026 independently show that longer-term relocation occurs: five West Antarctic colonies changed location substantially over the preceding decade, including cases associated with ice-shelf calving.

Together these systems expose a premise that is usually hidden in island/population monitoring:

> a biological population node may persist even when its coordinates do not.

## Two definitions of persistence

### Biological / identity persistence

A named colony remains the same colony across observations or breeding seasons when the source data identify it continuously as the same colony.

This does not imply demographic closure.

### Geographic-node persistence

A colony remains in the same spatial node only if its observed position remains within a fixed geographic neighbourhood of a reference position.

A fixed-node analysis can therefore report:

- disappearance from an old node;
- appearance at a new node;

even when named biological identity is continuous.

## Primary estimands

No single radius is chosen as the “true” colony boundary.

### 1. Fixed-node aliasing curve

For a distance threshold (r):

[
A(r)=P(D>r),
]

where (D) is displacement of the same named colony between relevant observations.

Report (A(r)) at the frozen scale set:

- 0.5 km;
- 1 km;
- 2 km;
- 5 km;
- 10 km.

These are a diagnostic curve, not five hypothesis tests.

### 2. Interannual false-turnover risk

For each colony and successive breeding seasons:

1. define the annual anchor as the centroid of all mapped groups on the earliest observation date of that season;
2. calculate displacement between successive annual anchors;
3. ask whether a fixed spatial node of radius (r) would retain the named colony identity.

If displacement exceeds (r), a fixed-coordinate definition would count turnover although the named colony persists.

### 3. Within-season false-absence risk

For each season:

1. use the earliest-date centroid as the seasonal anchor;
2. on each later observation date, calculate whether **all** mapped groups lie outside radius (r);
3. quantify the fraction of observation dates that would appear empty to a fixed-radius revisit of the original node.

This converts movement into a monitoring/occupancy consequence rather than re-reporting distance.

### 4. Identity-preserving radius

Descriptively estimate the empirical radius required to contain:

- 50%;
- 90%;
- 95%;

of same-colony interannual anchor displacements and within-season date centroids.

This is reported with the very small number of independent colonies clearly stated.

## Primary data

Macdonald et al. (2026), UK Polar Data Centre:

> *Year-round estimates of penguin colony locations at the Atka Bay, Coulman Island, and Cape Washington colonies, 2017–2024.*

DOI: 10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9.

The paper states that shapefiles contain the colony tracking data.

Expected biological units:
- Atka Bay;
- Coulman Island;
- Cape Washington.

Expected temporal support:
- 2017–2024.

## Independent context layers

### Global 2023 colony snapshot

Fretwell (2024), UK Polar Data Centre:

DOI: 10.5285/fb0547e4-d2c1-4580-8c98-182f1da7d9ae.

This is used only to quantify the spacing of emperor-colony nodes and to show how movement scales compare with between-colony geography.

The source explicitly states that 2023 positions are snapshots and that colonies move, so these coordinates are not treated as immutable true colony locations.

### Long-range relocation cases

Fretwell et al. (2026), *Dynamic emperor penguin colonies*, supplies independent evidence that node movement is not restricted to the three intensive tracking sites.

Those five cases are contextual/external evidence unless machine-readable longitudinal coordinates can be independently recovered without digitising plotted results.

## Support gate before spatial analysis

The primary tracking analysis opens only if the public source provides:

1. all three expected named colonies;
2. at least seven breeding seasons per colony;
3. a parseable observation date or date recoverable deterministically from filenames/attributes;
4. geographic coordinates or geometries for mapped colony groups;
5. at least three observation dates in at least six seasons per colony.

No abundance data are needed.

If group identity is absent, groups may be treated as multiple locations on a date, but cannot be linked individually through time.

## What would be biologically interesting?

### Strong coordinate aliasing

Named colony identity is continuous, but fixed spatial definitions repeatedly generate apparent disappearance/reappearance.

Interpretation:

> **population persistence can be topological/identity-based before it is geographic.**

### Scale-dependent identity

Small-radius site definitions show high turnover while larger-radius definitions retain identity.

Interpretation:

> persistence depends on the spatial scale at which an island/population node is defined.

### Low aliasing despite movement

Movements remain small relative to monitoring-node scales.

Interpretation:

> emperor colony mobility is biologically conspicuous but does not materially undermine site-based monitoring at those scales.

All three are useful outcomes.

## Relationship to island biogeography

Classical island and metapopulation models usually assume that habitat patches/nodes have fixed coordinates while occupants colonize or go extinct.

The emperor system makes patch position itself dynamic:

[
L_{t+1}=g(L_t,I_t,ldots),
]

where (L_t) is the breeding-node location and (I_t) is substrate/ice state.

Observed occupancy at coordinate (x) then combines two processes:

[
	ext{occupancy change}
=
	ext{population turnover}
+
	ext{node movement}.
]

Ignoring the second term can turn relocation into apparent extinction and colonization.

## Claim boundaries

- Do not claim that named emperor colonies are demographically closed.
- Do not equate movement with dispersal of identifiable individuals.
- Do not rebrand Macdonald et al.'s movement-distance result as new.
- Do not infer substrate causation from three intensively tracked colonies.
- Do not compare emperor and Pygoscelis as a causal substrate experiment without a broader matched design.
- Do not digitise figures to manufacture precision when machine-readable coordinates are unavailable.

## Stop rule

If the primary public shapefiles cannot be reproducibly obtained or parsed, stop the quantitative Paper 3 lane rather than reconstructing tracks manually from figures.

If support passes, freeze the geometry/date parser and the aliasing estimands before opening displacement summaries.
