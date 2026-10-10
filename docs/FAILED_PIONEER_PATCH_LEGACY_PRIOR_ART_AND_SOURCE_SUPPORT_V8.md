# V8 — Failed pioneers: a necessary three-way patch control is absent, and physical legacy already has prior art

Date 2026-10-10. Project `mina` exploratory mechanism branch, PR #193. Frozen Ecology paper PR #189 and locked individual-source PR #142 unchanged.

## What actually passed the source gate

[Source-pinned GitHub Actions #38010646818](https://github.com/zuizui0223/mina/actions/runs/38010646818) **success** for the *structural audit*, not the ecological hypothesis. Original author release `pointblue/solo_nests@04517cedac18950408abd4d0b510f4aae3447f05` contains **50** unique GPS nest-site/outcome IDs. Of the original site entries, **37** have `breeder=1` (includes one poorly observed focal `solo27`) and **13** have `breeder=0`. Among 37 breeder codes, `cr_confirm > 0` at **11**, equal zero at **25**, and missing at **1**. A negative direct-confirmation code **does not prove failed fledging, egg failure or zero offspring**, particularly when observations are incomplete.

There are **zero sampled never-used *physically usable* habitat patches** in the source as a matched comparator; the roster was constructed by detecting solitary nest sites/individuals. The 13 nonbreeders are **not** previously failed egg-laying pioneers, and they are **not** surveys of unused empty suitable ground. The matched risk-set needed to estimate a failed-pioneer effect (true failed site vs never-used comparable site) has **no common support** in this dataset. Subsetting these same 50 nest sites further will not create it.

The source byte contract and no-ecology fits: `contracts/ANTARCTIC_FAILED_PIONEER_LEGACY_NOVELTY_IDENTIFIABILITY_V2.json`; `scripts/audit_failed_pioneer_legacy_risk_set_v2.py`; `tests/test_failed_pioneer_legacy_risk_set_v2.py`; `.github/workflows/failed-pioneer-legacy-risk-set-v2.yml`.

## Why broad claims of new biological mechanisms would be false

- **Social guarding/protection by nonbreeders is not new.** Tamiya & Aoyanagi (1982), [doi:10.3312/jyio1952.14.35](https://doi.org/10.3312/jyio1952.14.35), reported nonbreeding Adélie reoccupation, group defense and adults temporarily supporting incubation/guarding.
- **Physical nest engineering is not new.** Schmidt et al. (2021), [doi:10.1038/s41598-021-94861-7](https://doi.org/10.1038/s41598-021-94861-7), describe stone/guano construction of Adélie subcolony mounds and ridges at Cape Crozier and Royds.
- **Artificial habitat improvement and colony growth are not new.** Kim et al. (2023), [doi:10.3390/d15010051](https://doi.org/10.3390/d15010051), map Cape Hallett station cleanup and artificial mounds intentionally created to encourage penguin nests, with aerial observations of subsequent recolonization.
- **Using successful neighbors as public reproductive information is not new.** Danchin, Boulinier & Massot (1998), [Ecology 79:2415–2428](https://pubs.usgs.gov/publication/70020662), articulate performance-based social attraction (studied in colonial seabirds).
- **Failed/solitary pioneers followed by nearby clusters are not new observations.** Penney (1968) and Cox et al. (2024), [doi:10.1007/s00300-024-03246-9](https://doi.org/10.1007/s00300-024-03246-9), already document low-success pioneering and nascent neighborhood groups.

The one **sharply distinguishing future test**, not a present finding, is whether a *genuinely failed egg attempt* leaves a **quantified persistent physical substrate change** that increases next-year **new nearby first nesting** *over otherwise equivalent never-used patches*, while differences caused by reproductive-success cues and preexisting habitat quality are separately assessed.

## Causal alternatives and observable predictions

| Rival process | Prediction with matched pre-use quality and genuine never-used risk patches | What would specifically contradict it |
|---|---|---|
| H1 Failed-attempt legacy via nest stones, microterrain or guano | New settlement higher near a verified failed prior egg attempt than at never-used patches; change in physical cue predates new arrivals | No measurable persistent cue after failed attempts, or effect vanishes when original physical quality and observation effort are compared |
| H2 Success-dependent public information | New settlement higher after prior breeding success; failed-attempt sites behave like never-used sites | Equally strong attraction around independently verified failed attempts even without previously successful conspecifics or contemporary social cues |
| H3 Stable microhabitat sorting | Once early dry gravel, snow, slope, aspect, predator access, proximity to water and census effort are matched, prior nesting class adds no discernible predictive value | A repeatable cue-mediated settlement contrast, anchored to an exogenous patch change, in replicated sites and years |

Purely observational differences can still be confounded by unmeasured quality; neither the H1 row nor cue mediation becomes causal just because a regression coefficient is positive. Crèche entry is not fledging or natal recruitment. A single island’s nest territories do not constitute an independently replicated *inter-island* colonization experiment.

## Source-aware plan capable of rejecting mechanisms

**Before the first season:** Map and repeatedly survey *all* physically usable 3–10 m patches, including empty patches, using fixed boundaries and common image dates. The unoccupied patch risk set must be selected without looking at the next year's outcome. Measure dry-rock substrate, stone mound elevation/volume, historical guano, slope/aspect, snow, predation geography, sea access and nearby colony density.

**During first season:** Link exact nest and individual IDs to dates of arrival, confirmed egg laying, chick outcome and observation effort. Define a genuinely failed patch by positive evidence for the original nesting attempt and its known fate, not by failure to see a chick. Record contemporaneous successful-patch, failed-patch and unused-patch states.

**After season and before next arrivals:** Measure whether attempted nesting left a physical substrate change (stone mound, microtopography, residual guano), separate from ephemeral actual penguin presence or visual/call cues.

**Next breeding season:** At the same frozen patches, distinguish a truly *new* first breeding attempt in the neighborhood from exact nest-site reuse or an already existing nearby colony. Identify recruits’ marked origin when possible, and independently observe nest and chick outcomes. Use multiple colonies/islands and multiple years for a claim beyond Cape Crozier.

**Control and ethics:** No unauthorized manipulation of nesting birds, guano, stones, social decoys or nest structures. Test natural habitat disturbances before proposing controlled interventions. Document detection of empty patches with repeated visits; missing observation is not absence.

## Decision

**CURRENT: HOLD_UNIDENTIFIABLE_H1_VS_H2_VS_H3**. All 50 source rows have already been selected as solitary-nest locations; **no survey of never-used suitable comparison patches** was present. The 25 non-confirmations at breeder nests do not become verified failures simply by treating missing chicks as dead. The old literature already covers most broad mechanism vocabulary. The exact mechanistic contrast remains a valid *future hypothesis* but cannot support a new ecology paper from the currently accessed published Cox data.

There is likewise **no demonstration of island-boundary effects**, inter-island source–sink transfer, or first colonizers’ origin. If that is required for a new island-biogeography theory, the complete patch experiment must include explicit island-to-island opportunities and movements.

Stop outcome tuning of this 36/50-nest source; retain it as validation of why an independent experiment needs three classes and dates. PR189 scientific submission frozen.
