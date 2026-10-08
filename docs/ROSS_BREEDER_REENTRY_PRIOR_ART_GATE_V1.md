# Ross Island breeding re-entry: prior art and identifiability gate v1

**Date:** 2026-10-08  
**Status:** PUBLIC-METADATA / LITERATURE AUDIT ONLY; NO NEW BIOLOGICAL ENDPOINT OPENED  
**Relation to PR #189:** separate future-mechanism gate; the frozen Ecology manuscript is unchanged.

## Scientific motivation

The six-component Ross aerial census records a 54.3% decline in breeding pairs (1999 to 2001) and 96.97% restoration of lost pairs by 2002. The fast rebound does **not** identify whether the birds were experienced breeders resuming reproduction, newly recruited breeders, survivors, immigrants, or previously uncounted birds whose attempts became observable. It measures occupied breeding territories/pairs, **not** a census of all living adults.

A proposed next question was: *Did variation in breeding re-entry rather than mortality or redistribution create the unequal colony recovery?* Before making that the claim of a second paper, we must ask whether it is new **and** whether the exact focal years and states can be identified.

## Prior-art vetoes (read before opening any new outcome)

1. **Adult state dependence during iceberg conditions is established.** Lescroël et al. (2009; DOI 10.1111/j.1365-2656.2009.01542.x) banded 430 breeding adults at Cape Crozier over 1996–2006. For reproductive-state transitions they analysed a subset of 242 breeders resighted in 2002–2006. Their multi-state design separated deferred, unsuccessful, and successful breeders, and found that successful breeders had higher subsequent reproductive success and survival than unsuccessful birds. The general cost-versus-quality and previous-state hypotheses are **not novel** for the focal system. Their adult data are for **Crozier** and cannot be treated as a direct three-colony decomposition.
2. **Colony-specific breeding propensity, survival, recruitment and movement are established.** Dugger et al. (2026; DOI 10.3389/fevo.2026.1868960) analysed 1996–2020 known-age, chick-banded individuals at Crozier, Bird, and Royds using a multistate encounter model. Among existing breeders, subsequent breeding sabbaticals occur at appreciable rates (~20–30% depending on age); breeding propensity is highest at Crozier and lowest at Bird. Established breeders rarely move between colonies (<0.2% in the reported estimates), while prebreeder movement is less rare. These are published **average/stage-pattern estimates**, not an event-specific accounting for the 2001-to-2002 count rebound.
3. **Known-age reproductive performance and sabbaticals are established.** Kappes et al. (2021; DOI 10.1111/1365-2656.13422) analysed breeding history 1997–2013 at the three colonies. The Dryad dataset (DOI 10.5061/dryad.s7h44j15w) includes a *BreedingSuccess.csv* table with recoded individual IDs, colony, season, observed breeder status, fledging-success status, age and experience. The public archive explicitly warns that IDs cannot be linked to those in other releases, and asks prospective analysts to contact the data stewards to coordinate analyses.
4. **Other penguins already exhibit reproduction-versus-survival tradeoffs.** Bohec et al. (2007; DOI 10.1111/j.1365-2656.2007.01268.x) tested breeding versus nonbreeding transitions in king penguins. Do not sell "the first discovery of sabbatical-dependent breeding" as generality.

## Crucial focal-cohort support limit

The Dugger et al. (2026) main analysis banded **chicks** beginning in 1996. At a 2002 breeding season, individuals banded as 1996 chicks can be only approximately six years old. Older experienced adults responsible for much of the pre-disturbance breeding population are not represented by these newly banded chick cohorts. Early age-class and calendar-year effects are also confounded, a limitation explicitly acknowledged in Dugger et al. (2026).

An older *adult*-banded Crozier sample exists in Lescroël et al. (2009), so it would be incorrect to assert that no focal-period adult histories exist anywhere. However, that one-colony sample is **not** a source for an unqualified Crozier/Bird/Royds census decomposition.

**Decision:** neither the 1996–2020 chick-band trajectories nor the Crozier-only adult-band results currently justify claiming that the 2001–2002 three-colony rebound was predominantly breeding re-entry.

## Data inventory and realistic estimands

| Source | Timing / geography | What can be identified | What cannot be justified as-is |
| --- | --- | --- | --- |
| Lyver et al. 2014 Ross aerial census, DOI 10.1371/journal.pone.0091188 | Ross, 1999/2001/2002 | Breeding-pair changes by fixed colony/component | Individual mortality, skipping, recruitment, immigration |
| Lescroël et al. 2009 adult banding | Crozier, 1996–2006 | State transition probabilities for their adult Crozier sample | Three-colony shares of the census rebound |
| Dugger et al. 2026 chick banding | Royds/Bird/Crozier, 1996–2020 | Known-age vital rates with resight model | Full demographic attribution of older adults' 2001–2002 return |
| USAP-DC 601444 and 601443, DOI 10.15784/601444 and 10.15784/601443 | Public resighting and banding records, 1994/1997–2021 | Potential individual state histories, if approved schema and coverage gates pass | Automatic conversion of raw sighting counts to population-wide transition rates |
| Kappes et al. Dryad | Three colonies, 1997–2013 | Conditional breeding/production patterns among included and observed individuals | Links to outside resight IDs, effort-corrected population-wide sabbatical rates |

## Feasibility gate for any *new* focal-year mechanistic claim

Read and freeze a **header-only** schema receipt before opening individual rows. Then require an independently documented support check, without reading outcome magnitudes:

- Adult breeder state explicitly recorded at **pre-shock, trough, and rebound** seasons, not inferred from being missing in the sightings.
- Information on detection/search effort by colony and season; **not seen ≠ nonbreeder ≠ dead**.
- Three-colony support and mark-status/age-class coverage, rather than extrapolating Crozier-only adults.
- Exact mapping of *austral breeding season start year*, census date, encounter date, and dates of egg/chick evidence.
- A documented population-representation or weighting strategy; if the sample is a non-random marked cohort, the estimand must remain within-cohort and **must not** be reported as a 109,198-pair causal decomposition.
- No outcome-adaptive exclusion of years, movement classes, sex, age, or colony.

If these conditions fail, stop the focal 2001–2002 attribution route, irrespective of how striking the aggregate recovery looks.

## What is genuinely still open?

The prior studies establish the existence of nonbreeding, reproductive-state transitions, and strong colony-level demographic heterogeneity. What they do **not** directly establish is a *three-colony, focal-shock, detection-corrected decomposition* linking those states to the disproportionate 2001–2002 recovery.

This is a meaningful empirical gap but is currently **data-limited, not a positive new result**. It cannot be filled by algebra or by assuming that a jump in breeding-pair counts must equal breeder re-entry.

A distinct prospective question for later years could ask whether **within-age-class, colony-specific transitions between nonbreeding and breeding respond differently to independently measured access disruption, beyond persistent colony and year effects**. This must be framed as a new estimand, not a post hoc explanatory label for PR #189. Before preregistration, check age-by-year overlap, Bird effort after 2013, environmental variability, and whether the period supplies truly independent perturbations.

## Existing operational dependency: do not duplicate

Issue #141 and PR #142 already freeze the USAP-DC resighting **first-breeding prospecting/choice** route. That route asks about settlement among colonies previously visited, not adult shock re-entry, and is blocked before opening exact headers by an official USAP-DC API key. Do **not** silently repurpose its current response-blind protocol or its frozen information gate for this different analysis.

- Issue #141: https://github.com/zuizui0223/mina/issues/141
- PR #142: https://github.com/zuizui0223/mina/pull/142
- USAP-DC public resighting data: https://www.usap-dc.org/view/dataset/601444
- USAP-DC banding data: https://www.usap-dc.org/view/dataset/601443
- Dryad study release: https://doi.org/10.5061/dryad.s7h44j15w

## Status / stop rule

**CLOSED as a proposed immediate second paper.** The direct 2001–2002 participation/death/immigration decomposition is not identified by the current accessible evidence. Novelty alone does not license opening and searching alternative outcome columns.

**NEXT ACTION:** obtain the official USAP-DC public API key and complete the already frozen header-only gate in Issue #141 for the *separate* first-breeding-choice test. Any later re-entry study needs its **own** independently justified, pre-outcome design and a demonstrated eligibility/effort/age-overlap gate. Preserve PR #189's scientific freeze.
