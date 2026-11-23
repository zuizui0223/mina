# Spatial recovery v0.6 — Ecology Article editorial plan v3

**Date:** 2026-10-07  
**Primary target:** *Ecology* — Article  
**Backup:** *Journal of Animal Ecology* — Research Article

## Title

**Population recovery can retrace local losses without restoring spatial structure**

## Editor-level question

> **When a spatially structured population appears to recover, did the local population network recover or did a few large components compensate for incomplete recovery elsewhere?**

## Focal natural experiment

Ross Island Adélie penguins, 1999→2001→2002.

- aggregate breeding abundance loss: **54.3%**;
- aggregate loss restored next census: **96.97%**;
- local restoration range: **10.8–109.8%**;
- median local restoration: **51.8%**;
- Cape Crozier West share of rebound: **80.6%**;
- inverse-path fidelity: **90.59%**;
- baseline compositional displacement erased: **2.4%**;
- observed endpoint distance from baseline: **4.97% TV**;
- exact-inverse endpoint distance from baseline: **0.0717% TV**.

## One-sentence result

> **Near-complete aggregate recovery was produced by strongly unequal local recovery, so abundance returned largely where it had been lost without restoring the previous spatial composition.**

## Why an Ecology editor should care

The general monitoring problem is larger than penguins.

Aggregate population recovery is a weighted sum of local recoveries. In a spatial network with unequal component sizes, a dominant component can compensate numerically for incomplete recovery elsewhere.

Therefore a regional or population-level target can be met while:
- many local units remain incompletely recovered;
- dominance increases;
- effective spatial redundancy decreases;
- the final spatial state differs materially from baseline.

This connects disturbance ecology, metapopulation recovery, spatial resilience, and conservation monitoring.

## Prior-art position

Established:
- aggregate recovery can hide local or compositional collapse;
- local demography and disturbance geometry influence metapopulation recovery;
- trajectory and state are distinct concepts.

Not claimed as novel.

Empirical contribution:
- a documented field disturbance with simultaneous near-complete aggregate recovery, high geographic/path reversal, strongly heterogeneous local recovery, and failure of state restoration;
- exact decomposition showing why the aggregate signal was dominated by one large component;
- complementary decline and capacity-change cases showing the same state-reweighting principle under different demographic directions.

## Supporting cases

### Palmer + Signy

Persistent decline departed from proportional thinning and concentrated breeding structure.

Role:
> unequal local loss reweights spatial state.

### Beaufort

Growth after capacity release departed from proportional expansion.

Role:
> unequal local gain reweights spatial state.

These are process contrasts, not Ross replications.

## Main figures

1. Three answers to recovery: amount 97.0%, path 90.6%, state 2.4%.
2. Local recovery 10.8–109.8% + compositional reweighting.
3. Three Ross down→up episodes: high path fidelity, weak/negative state restoration.
4. Palmer/Signy unequal attrition + Beaufort unequal expansion.

## Editorial risk

### Risk 1: post-result focal analysis

Mitigation:
- explicit in Abstract/Methods/Transparency;
- no confirmatory p-value attached to path/state result;
- counts and algebra are fully auditable.

### Risk 2: one focal independent shock

Mitigation:
- do not claim universality;
- other Ross episodes are only within-series calibration;
- Palmer/Signy/Beaufort are biological contrasts, not fake replication.

### Risk 3: “obvious weighted-average effect”

Mitigation:
- the algebra is obvious once stated, but the field outcome is not;
- median local restoration 51.8% versus aggregate 96.97%;
- exact-inverse recovery would almost perfectly restore the state, yet the observed structured residual produced the largest compositional transition in the series.

## Claim ceiling

Licensed:

> **Near-complete aggregate population recovery can mask strongly incomplete and unequal local recovery, and recovery in the same places as loss does not guarantee restoration of spatial state.**

Not licensed:
- a universal recovery law;
- a novel mathematical theory;
- a universal threshold for meaningful TV distance;
- individual movement inference;
- an exceptional mismatch magnitude.

## Submission architecture

One active manuscript only:

    docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_6.md

All narrower Palmer / Ross / spatial-memory lanes remain on hold.
