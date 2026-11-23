# Spatial-memory process classification audit v1

**Date:** 2026-10-07  
**Contract:** `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`  
**Decision:** the spatial-memory framing is biologically stronger than a standalone “high reversibility” Report, but the existing archive does not support a formal three-class omnibus test.

## 1. Main conceptual revision

The useful contrast is not:

> short shocks are reversible; long changes are irreversible.

Ross itself falsifies that simplification because most of the 2001-2012 change in redundancy is an early 2001-2002 pulse, while 2002-2012 shows little monotonic erosion.

The stronger question is:

> **what kind of biological change preserves an old spatial template, and what kind rewrites it?**

This produces three distinct process predictions.

### Memory-preserving breeding-state perturbation

A temporary access / breeding-participation shock can remove breeding expression without necessarily removing the adults or the breeding network that generated the previous spatial pattern.

Ross 1999-2001-2002 is the cleanest case.

Lyver et al. (2014; doi:10.1371/journal.pone.0091188) identify the B-15A/C-16 period as an exceptional disturbance and report widespread failed or abandoned breeding under poor access conditions. The Ross census measures breeding pairs / occupied nesting territories, not total adult abundance.

Independent mark-recapture evidence also shows that breeding adults in the Ross Island metapopulation usually have very high breeding-site fidelity; the most recent 25-year analysis reports breeder movement among colonies below 0.20%, while breeding sabbaticals remain common (Dugger et al. 2026; doi:10.3389/fevo.2026.1868960).

This does **not** prove that the same individuals generated every lost and regained count. It makes a memory-preserving interpretation biologically plausible.

### Demographic turnover / attrition

Palmer and Signy are different.

Their focal intervals are persistent declines with durable losses of breeding units, not a one-season participation trough.

Frozen results:

- Palmer: effective colony number fell by 19%, 51%, and 83% on the three stable-roster islands, beyond proportional thinning plus the frozen count-error family.
- Signy: 1998-2009 Adélie breeding pairs fell from 2,688 to 901 and effective colony number fell 29.7%, again beyond the frozen proportional-thinning/count-error family.

The independent Signy population study reports decades-long Adélie decline and disappearance of multiple Adélie colonies, while noting that local counts also reflect immigration/emigration (Dunn et al. 2016; doi:10.1371/journal.pone.0164025).

For the western Antarctic Peninsula more broadly, mark-recapture and demographic models identify survival and recruitment as important drivers of persistent Adélie decline. That evidence supports a turnover interpretation at regional scale, but does not identify the exact vital-rate decomposition of each Palmer census code.

Therefore B is justified as **persistent demographic attrition**, not as a claim that one specific vital rate caused the spatial concentration.

### Capacity change

Beaufort is a different kind of intervention.

LaRue et al. (2013; doi:10.1371/journal.pone.0060568) reported a 71% increase in usable nesting habitat while the population increased 84%. Banded-bird movement from Beaufort toward Ross Island rose to about 3% around 2005 and later declined as local habitat became available.

The corrected census decomposition shows that the small/new Beaufort breeding unit gained 3.15 times the increase expected under proportional allocation and increased its share from 0.95% to 1.48%.

The important point is not “recovery spreads.” It is:

> **capacity can change the spatial level at which redistribution occurs: more birds can remain on the island while growth is disproportionately expressed in a previously small within-island unit.**

## 2. Why the omnibus three-class test is blocked

The three mechanisms do not share a clean common estimand.

Ross A has a true three-state question:

    baseline -> shock trough -> rebound

and therefore supports an inverse-path quantity.

Palmer/Signy B are long attrition trajectories:

    baseline -> persistent decline / local extinction

Beaufort C is a capacity-release expansion:

    old capacity -> increased capacity / changed settlement

A common two-state composition distance could be computed, but it would be confounded by interval duration, aggregate-change magnitude, and endpoint choice. That would convert a biological hypothesis into a convenience metric.

So the correct current claim ceiling is:

> **existing evidence is consistent with process-dependent spatial memory, but does not yet estimate a universal class effect.**

## 3. The strongest paper structure now

### Question

> **What determines whether population change preserves or rewrites spatial organization?**

### Hypothesis

> **Changes that suppress breeding expression while retaining site-faithful adults and the existing breeding network can preserve a recoverable spatial template; demographic turnover and capacity change can rewrite that template by changing who contributes or where breeding can occur.**

### Evidence roles

1. **Ross acute iceberg disturbance — memory-preserving case.**  
   54.3% breeding-abundance loss, 97.0% of aggregate loss restored, loss/rebound cosine 0.99695, inverse-path mismatch 9.41%.

2. **Palmer + Signy persistent decline — replicated attrition case.**  
   Concentration exceeds proportional thinning; durable local breeding-unit loss is part of the ecological setting.

3. **Beaufort capacity release — capacity-rewriting case.**  
   New/small unit gains disproportionately while inter-island export falls.

4. **Bird + Heard + Emperor — boundary evidence.**  
   These should not be forced into process classes. Their role is to show why aggregate N direction alone cannot identify the spatial path.

## 4. Terminology correction

Prefer:

> **breeding-site fidelity can act as a carrier of spatial memory**

rather than:

> philopatry is spatial memory.

The first is both more precise and more defensible. Site fidelity is already known to influence colonial metapopulation dynamics, so the novelty cannot be the existence of fidelity itself.

The potentially new contribution is the empirical process distinction:

> **the same fidelity that can restore a previous breeding configuration after a temporary participation shock can also preserve a suboptimal configuration after a structural disturbance; whether “memory” helps restore the past depends on what the disturbance changed.**

That last point is especially important because Ross literature already notes that high nest-site fidelity can slow reorganization after habitat/access disruption at Cape Royds.

## 5. Island-ecology contribution

The island should enter as an active spatial operator in two ways.

### Island as environmental compartment

Different faces / colonies on the same island receive a shared regional event through different access, sea-ice, snow, and breeding-habitat geometries.

Thus an island is not a homogeneous environment.

### Island as demographic container

Beaufort shows that increasing local capacity can simultaneously:

- retain more breeders on the island;
- redistribute growth within the island;
- reduce movement to another island.

This links:

    within-island redistribution
        <- local capacity ->
    between-island dispersal

The contribution is therefore not a restatement of classical area + isolation. It is a nested demographic view of island boundaries.

## 6. Submission decision

The standalone PR189 Ecology Report should be placed on **scientific framing hold**.

Reason:

- the focal high reversibility result is real but not exceptional within Ross;
- breeding-site fidelity makes strong reversal biologically plausible;
- the broader abundance-versus-spatial distinction has prior art;
- the integrated spatial-memory question is more biologically informative and better uses the already-opened evidence.

This hold does **not** reopen the PR189 mechanism search.

No new covariates, lags, species, or favorable subsets should be opened.

The next decision is manuscript architecture, not effect hunting.
