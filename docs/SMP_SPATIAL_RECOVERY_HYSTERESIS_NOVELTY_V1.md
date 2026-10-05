# SMP spatial-recovery hysteresis novelty boundary v1

**Date:** 2026-10-05  
**Status:** prospective positioning before SMP outcome opening.

## What is already established

### Colonization and extinction are core metapopulation processes

Classical metapopulation ecology already treats local extinction and recolonization as distinct processes whose balance controls regional persistence. Patch quality, local population size and connectivity are established predictors of turnover.

### Recolonization is not the same as first colonization

Bled, Royle & Cam (2011, *Ecology*, doi:10.1890/10-0392.1) modeled Black-legged Kittiwake nest-site occupancy over 20 years and explicitly separated:

- persistence;
- first colonization;
- recolonization after desertion.

They also showed that these processes respond to local density, site reproductive success and neighboring reproductive success.

Therefore this project must **not** claim novelty for distinguishing recolonization from first colonization or for proposing that social information can affect site occupancy.

### Allee-driven recolonization barriers are already predicted

Schippers et al. (2011, *Ecological Modelling*, doi:10.1016/j.ecolmodel.2011.05.022) used a spatially explicit seabird metapopulation model to show that Allee effects can strongly lengthen recolonization time and reduce effective recolonization distance.

Therefore the project must not claim novelty for predicting that coloniality or Allee effects can slow recolonization.

### Site quality and population state already predict turnover empirically

Franzén & Nilsson (2010, *Proceedings of the Royal Society B*, doi:10.1098/rspb.2009.1584) showed that population size and patch quality both influence extinction and colonization in a fragmented animal metapopulation.

Bennett et al. (2022, *Journal of Animal Ecology*, doi:10.1111/1365-2656.13674) tested site-dependent regulation in common guillemots across increase, decline and recovery.

Therefore the project must not claim novelty for showing that occupancy changes with population size or site quality.

### Hysteresis / alternative stable states are not new concepts

Positive feedback and dynamic-island theory already allow history dependence, alternative stable states and non-reversible recovery.

The word “hysteresis” itself is not the contribution.

## Candidate empirical novelty

The candidate contribution is narrower:

> **For the same repeatedly monitored breeding SiteID, directly pair the surrounding population state at abandonment with the state at later recolonization, then test prospectively across multiple seabird species whether recovery crosses a systematically higher population threshold than collapse.**

The focal paired quantity is

[
H=A_{mathrm{recolonize}}-A_{mathrm{abandon}}.
]

The same SiteID is its own control for persistent place identity.

This design differs from ordinary occupancy analyses because:

1. the focal comparison is abandonment versus later recolonization of the **same physical SiteID**;
2. first colonization is excluded;
3. the focal SiteID is removed from the surrounding population predictor;
4. the exact vacancy spells are frozen before abundance magnitudes open;
5. inference is aggregated SiteID → MasterSite → species with equal species weight;
6. a structured common-phase null preserves the observed multivariate MasterSite abundance trajectory while breaking its alignment with the frozen event dates.

## Why same-site pairing matters

Cross-site colonization/extinction comparisons can confound history with persistent differences among places.

The paired design holds fixed:

[
	ext{place identity}
]

while changing:

[
	ext{occupancy history}.
]

It does **not** remove time-varying habitat degradation, predators, disturbance, management or other non-social temporal mechanisms.

## Why the structured phase null matters

A positive (H) can arise if abandonment and recolonization dates happen to align with different phases of a trending or autocorrelated MasterSite population trajectory.

The frozen common-phase null therefore:

- keeps the same SiteIDs;
- keeps the same species × MasterSite;
- keeps the same completed vacancy spells and event-year pattern;
- keeps the observed multivariate SiteID count trajectory;
- circularly shifts the whole contiguous MasterSite block by one common phase;
- uses the same phase shift for all SiteIDs and spells in that block;
- preserves cross-site covariance and dependence among spells.

Confirmatory support requires the observed species-balanced threshold difference to exceed this null as well as the species sign-flip test.

## Strongest allowed novelty sentence

> **We provide a prospective multi-species test of whether spatial loss and spatial recovery occur at different surrounding-population thresholds at the same breeding sites.**

If supported, a stronger Discussion sentence is allowed:

> **Population recovery did not simply retrace spatial collapse in colonial breeders.**

## Claims that remain prohibited even after a positive result

Do not write:

- “We discovered ecological hysteresis.”
- “We discovered recolonization barriers.”
- “We show for the first time that seabird recolonization differs from first colonization.”
- “Allee effects caused the threshold asymmetry.”
- “Conspecific attraction caused the threshold asymmetry.”
- “Static habitat quality is irrelevant.”
- “The result applies to all island taxa.”

## Link to the penguin discovery

The Antarctic penguin analysis generates the hypothesis because:

- decline repeatedly concentrates breeding effort beyond proportional thinning;
- regional effective breeding-site number can remain reduced while abundance increases.

Those results do not themselves identify abandonment/recolonization thresholds.

The SMP test is independent and stronger because it directly asks whether the **same places** are recovered at the same surrounding population state at which they were lost.

The penguin and SMP datasets are not pooled for inference.

## Pre-outcome novelty stop rule

If a literature search completed before SMP magnitude opening identifies an existing empirical study that already performs an equivalent multi-species same-patch paired abandonment/recolonization population-threshold test, revise the novelty claim before opening outcomes.

Do not alter the estimand after results merely to recover novelty.
