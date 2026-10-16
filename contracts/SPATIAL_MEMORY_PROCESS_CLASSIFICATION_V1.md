# Spatial-memory process classification contract v1

**Date:** 2026-10-07  
**Status:** post-result source-side eligibility audit; not preregistered and not analyst-blind.  
**Purpose:** determine which already-opened penguin endpoints can be assigned to a biological process class without using their spatial-response direction or magnitude.

## Scientific question

> What determines whether population change preserves an existing spatial template or rewrites it?

The working biological distinction is not short versus long duration. It is whether the perturbation primarily changes breeding expression while leaving the prior breeding network available, changes the demographic composition of that network, or changes the network's breeding capacity itself.

## Terminology

Use **breeding-site fidelity** for the return of known breeders to previously used colonies or nesting areas. Do not use `philopatry` as a synonym unless natal origin is actually known.

The phrase **spatial memory** is a population-level interpretation, not a measured cognitive variable. It refers to persistence of a previous breeding allocation that can be re-expressed after a perturbation.

## Forbidden classification cues

Process class must not be assigned from:

- effective colony/unit number (`E`, `N_eff`);
- total-variation distance;
- loss/rebound cosine similarity;
- inverse-path mismatch;
- dominance reversal;
- whether a case appears to support the spatial-memory hypothesis;
- manuscript convenience.

Any case requiring those quantities to choose its class is **AMBIGUOUS / EXCLUDED**.

## Process classes

### A. TEMPORARY_BREEDING_STATE_OR_ACCESS_SHOCK

Required source-side evidence:

1. an independently documented acute exogenous disturbance;
2. the response is breeding-pair / occupied-nest abundance rather than total adult abundance;
3. the source explicitly reports substantial skipped, failed, abandoned, or access-limited breeding as part of the event;
4. the pre-existing breeding geography remains available enough that return to the prior network is biologically plausible.

This class does **not** require proof that mortality, recruitment, or movement were zero.

Primary prediction:

> conditional on aggregate rebound, the rebound should substantially retrace the spatial footprint of the loss.

### B. DEMOGRAPHIC_TURNOVER_OR_ATTRITION

Required source-side evidence:

1. persistent multi-year population change rather than a single-season breeding-participation pulse; and
2. independent evidence of durable demographic change such as survival/recruitment change, emigration, persistent local extinction, or colony loss.

Long duration alone is not sufficient.

Primary prediction:

> relative local abundances can be rewritten because different breeding units experience different integrated demographic multipliers; proportional thinning is not required.

### C. BREEDING_CAPACITY_CHANGE

Required source-side evidence:

1. an independently documented change in usable breeding habitat or nesting capacity; and
2. a temporal link to altered settlement, within-island expansion, or inter-island movement opportunity.

Primary prediction:

> growth can be reallocated toward newly available or previously small breeding units, and redistribution may change spatial scale rather than simply reverse a previous loss.

### M. MIXED

Use when more than one process is strongly supported and the available evidence cannot isolate a dominant class for the chosen interval.

### X. NOT CLASSIFIABLE

Use when the endpoint has a spatial result but lacks independent source-side evidence sufficient to assign A, B, or C.

## Frozen case adjudication

| System / interval | Class | Confidence | Source-side rationale | Use in synthesis |
|---|---|---:|---|---|
| Ross Island Adélie 1999 -> 2001 -> 2002 | A | high | B-15A/C-16 disturbance; Ross census is breeding-pair abundance; published account reports widespread failed/abandoned breeding and access limitation | primary memory-preserving natural experiment |
| Ross Island Adélie 2002 -> 2003 -> 2004 | A-candidate | moderate | C-19 produced another documented one-season productivity/sea-ice disturbance, but the direct link to breeding participation is less explicit than for the focal event | within-system calibration only; not an independent replicate |
| Palmer Adélie 1991 -> 2017 | B | moderate-high | decades-long decline with durable island/subcolony loss and independent regional demographic evidence for survival/recruitment limitation; exact local vital-rate decomposition is unavailable | replicated attrition pattern |
| Signy Adélie 1998 -> 2009 | B | moderate | long-term island decline, disappearance of Adélie colonies, and evidence that local counts also reflect immigration/emigration; exact vital-rate decomposition unavailable | external attrition replication |
| Beaufort Adélie 2004 -> 2010 | C | high | usable nesting habitat increased and independent band/resighting evidence shows movement changed as local habitat became available | primary capacity-change contrast |
| Ross Island Adélie 2001 -> 2012 | M | high | interval begins at an acute breeding-participation trough but later dynamics integrate colony-specific survival, recruitment, breeding propensity, reproductive success, and movement | mechanism context only |
| Bird Island Gentoo 1981 -> 2024 | X | high | strong spatial endpoint but no independently isolated process class for the full interval | directional counterexample only |
| Heard Island King 1963 -> 1988 | X | high | historical expansion and dominance reversal, but no independent process classification adequate for A/B/C | literature triangulation only |
| Global Emperor 2009 -> 2018 | X | high | broad regional decline with heterogeneous local trajectories; no single source-side process class | directional counterexample only |

## Estimand boundary

A single three-class omnibus comparison is **not currently licensed**.

Reason:

- Class A naturally supports a three-state inverse-path estimand (pre-shock -> trough -> rebound).
- Class B is observed primarily as persistent attrition across two endpoints or long trajectories.
- Class C is a capacity-release contrast with expansion and movement evidence.

Forcing all three into one scalar `spatial reversibility` score would change the biological question and introduce interval-duration and endpoint-selection confounding.

Therefore the current synthesis is **contrastive and prediction-specific**, not a meta-analysis of one common effect size.

## Allowed next analyses

Allowed without reopening endpoint search:

1. compute the already-defined Ross inverse-path metrics for A cases;
2. summarize existing Palmer/Signy attrition results under B without changing their frozen endpoints;
3. summarize the corrected Beaufort proportional-growth and movement evidence under C;
4. test manuscript coherence using only the frozen case assignments above;
5. treat X cases as boundary/counterexample evidence against simple abundance-direction rules.

## Stop rules

Do not:

- add a new species or site merely to fill A/B/C cells;
- reclassify a case after reading its spatial outcome;
- call the present adjudication blinded or preregistered;
- infer individual identity from colony counts;
- claim that breeding-site fidelity alone caused Ross reversibility;
- claim a universal A/B/C law from the present case set;
- turn Bird, Heard, or Emperor into B simply because their intervals are long.

A future confirmatory test requires a new dataset in which process class is frozen from source-side evidence before the spatial recovery outcome is opened.
