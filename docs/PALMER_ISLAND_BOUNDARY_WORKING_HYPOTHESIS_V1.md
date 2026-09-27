# Palmer island-boundary working hypothesis v1

Date: 2026-09-27

This document records the ecological pivot produced by the frozen
`PALMER_ISLAND_PARTITION_V1` diagnostic. It does not upgrade the invalid v1
test to confirmatory evidence.

## Original working hypothesis

The initial insurance hypothesis predicted:

1. weak or compensatory covariance among subcolonies within an island;
2. lower within-island synchrony than expected for comparable pseudo-groups;
3. aggregation from subcolonies to island totals would provide unusually strong
   temporal insurance;
4. loss of within-island spatial diversification / effective colony number could
   precede island-scale collapse.

## What the frozen diagnostic showed

The complete-code panel failed the predeclared identifier-validity gate, so no
confirmatory biological decision is allowed.

Nevertheless, the frozen diagnostic has a clear directional pattern:

- within-island Fisher-mean annual-growth correlation = 0.1991;
- between-island Fisher-mean annual-growth correlation = 0.0937;
- within-minus-between contrast = +0.1054;
- abundance-matched pseudo-island permutation p = 0.0030;
- mean within-island annual-growth synchrony phi = 0.2553;
- among-island-total annual-growth synchrony phi = 0.4405;
- observed hierarchy gap = +0.1853, smaller than the pseudo-island expectation;
- raw-abundance Wang–Loreau phi is high on every retained island
  (approximately 0.876–0.953).

These values are provenance-only because v1 is INVALID.

## Hypothesis that is now deprioritized

**Within-island spatial insurance as the primary Palmer mechanism.**

The observed direction is not one of unusually asynchronous / compensatory
subcolonies. Reopening thresholds or synchrony definitions to recover that
prediction is prohibited.

`N_eff` therefore should not be described as an insurance metric. If retained
later, it is a spatial concentration / distribution metric whose ecological
meaning depends on a physical-colony crosswalk.

## New working hypothesis

> **Geographic islands are candidate local demographic covariance domains
> nested within a more broadly synchronized regional metapopulation.**

Mechanistic interpretation to test, not assume:

`regional marine forcing`
→ shared cross-island component

`island-scale terrestrial / snow / geomorphic forcing`
→ excess covariance among physical subcolonies on the same island

`subcolony-specific habitat`
→ local persistence / extinction and fragmentation within the island domain.

The conceptual novelty is therefore not that islands stabilize populations by
portfolio insurance. It is that a visually obvious geographic island may or may
not coincide with a statistically identifiable demographic boundary in a highly
mobile colonial marine predator.

## Confirmatory gate sequence

1. resolve raw `colony_code` to persistent physical units using independent
   maps / GIS only;
2. establish centroid/polygon coordinates and pairwise distances;
3. check overlap of within-island and between-island distance distributions;
4. only if identifiable, freeze a model testing whether `same_island` explains
   residual covariance after geographic distance;
5. use Torgersen habitat / geomorphology as a mechanism layer only after the
   boundary result is established;
6. defer Signy / Ross / MAPPPD generalization until the Palmer boundary test has
   a valid physical-unit result.

## Falsifiable outcomes

- **boundary supported:** same-island physical units co-fluctuate more than
  equally distant cross-island units;
- **distance-only:** covariance decays with distance but coastline membership
  adds no detectable discontinuity;
- **no local structure:** regional forcing dominates and neither distance nor
  island membership identifies a stable local covariance domain;
- **not identifiable:** within-/between-island distance ranges do not overlap
  enough to separate distance from island membership.

All four outcomes are ecologically interpretable and none should trigger
post-outcome metric search.
