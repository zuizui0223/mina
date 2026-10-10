# Penguin island recovery: life-stage gating and delayed demographic debt — novelty/feasibility gate v1

**Date:** 2026-10-08  
**Status:** PROSPECTIVE-DESIGN EXPLORATION / PRIOR ART EXPOSED / NO NEW ECOLOGICAL OUTCOME OPENED  
**Independent from:** frozen Ecology Article PR #189; USAP-DC prospecting-choice PR #142; prior-art PR #190.  
**Submission boundary:** nothing here amends, reinterprets, or unlocks the frozen PR #189 science.

## Scientific question

**Can two disruptions of island-to-sea connectivity with similar physical severity cause opposite *temporal* forms of population loss because the access disruption occurs at different stages of the breeding cycle?** More specifically:

- **Pre-laying / arrival interruption:** suppress breeding participation and the occupied-nest census *now*; the apparent population may rebound quickly when access normalizes.
- **After laying / chick-rearing interruption:** retain some breeding adults or territories initially, but suppress chick production and create a **delayed recruitment deficit** at affected breeding sites, potentially expressed several years after physical access normalizes.

The novel claim under investigation is NOT that icebergs impede foraging, that skippers exist, or that early-life success affects recruitment. The transferable claim to test is an **interaction of disturbance timing × functional island-to-sea accessibility** that determines whether an apparently reversible breeding collapse leaves a local, age-specific cohort debt and later spatial recovery deficit.

## Literature vetoes (do not claim these as discoveries)

1. **Ross iceberg effects and nonbreeding are prior art.** Lyver et al. 2014 and Dugger et al. 2014 already describe Ross/Beaufort iceberg-era colony-specific access and demographic effects. PR #190 reviews Lescroël et al. 2009 adult reproductive-state transitions, Dugger et al. 2026 known-age multistate survival/recruitment/propensity, and Kappes et al. 2021 breeding histories. Existing aggregate Ross 1999→2001→2002 count rebound does not decompose adult skipping, mortality, immigration, recruitment, or detection.
2. **Obstacle geometry and reproductive-stage specificity are already documented.** Park et al. 2026 (Communications Earth & Environment, doi:10.1038/s43247-026-03764-w) report a 2025 Coulman Island grounded iceberg, approximately 69% loss of emperor chick counts, and localized obstruction of the colony–foraging corridor. Their discussion contrasts a previous 2010 adult-attendance/breeding-suspension episode with a 2025 chick-rearing loss. Thus one 2010-vs-2025 comparison is **prior art**, not an untouched independent validation of our claim. The Park authors also treat 2025 as an observational single-event case.
3. **Same-island differential marine ecology is also prior art.** Ratcliffe et al. 2026 (Current Biology, doi:10.1016/j.cub.2026.09.010; published 2026-10-07) reported a 63% 2011–2025 occupied chinstrap nest decline on Zavodovski Island with a contrasting macaroni trajectory; different foraging preferences and available nesting substrate were central to their interpretation. Do not claim discovery of the simple "marine rather than terrestrial competition" explanation.
4. **Spatial memory / Allee / edge effects are prior art.** Ross nesting geometry, fidelity, reproductive heterogeneity and local snow/aspect extinction gradients already appear in Schmidt et al. 2021 and Cimino et al. 2025. A lagged population response or loop in abundance–concentration coordinates by itself does not establish causal demographic memory.

Primary public links:
- https://www.nature.com/articles/s43247-026-03764-w
- https://www.bas.ac.uk/news/penguin-population-collapse-on-volcanic-island/
- https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/02256
- https://github.com/zuizui0223/mina/pull/190
- https://github.com/zuizui0223/mina/pull/142

## Three *competing* causal explanations, not three names for the same pattern

| Mechanism | Immediate response to disruption | Response after access normalizes | Distinguishing measurement |
|---|---|---|---|
| A. Temporary breeding expression / arrival gate | Occupied nests/breeding attendance fall even if marked adults are alive | Existing adults can return rapidly; no necessary damaged birth-cohort signal | Encounter-corrected prior-breeder → nonbreeder → breeder transitions, colony-specific arrival dates |
| B. Reproductive failure and delayed recruitment debt | Adults/pairs may still be present, but chicks per attempted nest fall | An age-specific deficit in **local first recruitment** appears at biologically supported maturation lags, even after apparent adult breeding count rebounds | Sex/age/cohort-aligned chick production and known-age recruits, corrected for juvenile survival and natal dispersal |
| C. Habitat fragmentation / social-fidelity trap | Colony configuration becomes sparse/edge-rich | Recruitment and breeding performance remain depressed beyond temporary access conditions, not limited to a single known-age cohort | Physically mapped nest patches, edge exposure, predator risk, occupancy histories, movement/detection controls |

A and B can coexist. A positive test needs a discriminating contrast, not just a plausible story for an aggregate abundance curve.

## Prospective causal contrast for an *independent* external system

Let `AccessShock_{i,t}` be an externally mapped change in feasible colony–open-water pathway cost or obstruction, not simply distance to ice edge. Let `Stage_{i,t}` classify obstruction timing **before** its reproductive outcomes are read, at minimum pre-laying versus incubating/chick-rearing.

Primary hypothesis if data permit:

> With otherwise comparable independently measured access obstruction, **pre-laying** exposure preferentially changes breeding participation; **post-laying** exposure preferentially changes offspring output and later cohort-specific first recruitment. Any subsequent local abundance debt should align with the affected birth cohorts, not be inferred solely from aggregate breeding-pair counts.

Test-level negative controls:
- contemporaneous comparable breeding sites with no obstruction of their usable sea-access corridor;
- unrelated pre-exposure birth cohorts (cohort-specific placebo);
- pre-disturbance levels/trends in breeding propensity and chick output;
- sea-ice extent, prey/foraging conditions, storm exposure, count protocols, breeding phenology and colony-level baseline size as confounders.

Stage-based exposure needs independent event dates and nest/chick phenology. For multi-year recruitment, do not mislabel within-colony pair-count change as observed recruits.

## Structure-first information gate — **NOT YET PASSED**

Before opening any previously unexamined focal biological outcomes, require all of:

1. At least **two independent disturbance episodes** with independently documented obstruction timing and credible unexposed comparator(s); repeating Ross 2001 or Coulman 2025 analyses does not satisfy independence merely because the sites are different.
2. Each candidate episode has **both** breeding participation/attempts and offspring success with aligned census windows. A single chick series alone is inadequate for distinguishing A from B.
3. At least one event has an independently measured known-age recruitment pipeline spanning the implicated birth cohorts and appropriately matched earlier/later cohorts, including documentation of natal dispersal and detection. Otherwise B is not identifiable.
4. The estimated access metric is independently mapped from contemporaneous ice/obstacle geometry; geometric distance and broad regional sea-ice mean cannot be substituted silently for functional path accessibility.
5. No mixing of occupied breeding territories, live adults, chicks, nests, and counted subcolonies as if they were the same endpoint. Stable spatial units and observation effort must be verified.
6. Event, stage, endpoint, lag range derived from observed age at first breeding, comparator and exclusions are frozen **before** any newly accessed outcome magnitudes.
7. A feasible design has enough independent shock clusters for a cluster-level uncertainty analysis; a 3-colony × one-event interaction cannot be described as broadly replicated causal evidence.

If any gate fails, the route remains descriptive/prior-art synthesis and must not generate a causal discovery claim.

## Source status / blockers as of 2026-10-08

- Ross PR #189: numerically informative recovery but frozen, with no individual identification.
- Ross PR #190: published age/propensity evidence is mechanistically relevant, but available records do **not** identify the full 2001–2002 three-colony return.
- USAP-DC PR #142: first-breeding prospecting route is a *different estimand* and is blocked before exact headers by the official API-key requirement; its protocol must not be reused as a shortcut.
- Coulman 2025 (Park): clear potential stage-specific natural history but already published, single-event observational case and not a prospective replication.
- Zavodovski 2011–2025: BAS metadata describes both species' geo-referenced colony boundaries in 2011/2016/2020/2022/2025, with >90% survey coverage and some cloud gaps filled using other dates. Metadata lists no access restriction, but a current direct repository request was **HTTP 401**, so no geospatial rows/polygons were recovered, and no spatial replacement/competition test is claimed. Temporal imputation must be separated from true change if access becomes possible.
- Paper 2 static island-architecture interaction is non-confirmatory (frozen median 2 km interaction p=0.0947, and scale-sign unstable), so do not rescue its effect by relabeling this new temporal mechanism as its result.

## Decision

**PASS:** novelty can be formulated as a *future* testable, life-stage-specific causal interaction, not as any known direct iceberg or demographic effect.

**FAIL / HOLD:** an independent, jointly observed event–stage–recruitment panel has not been demonstrated. No new causal coefficient, positive finding, or formal preregistration is authorized yet.

**Priority:** audit structure and independence of candidate cohort/outcome sources; do not search additional already-exposed Ross outcomes, move PR #189's endpoint, or compute favorable alternative lag windows.
