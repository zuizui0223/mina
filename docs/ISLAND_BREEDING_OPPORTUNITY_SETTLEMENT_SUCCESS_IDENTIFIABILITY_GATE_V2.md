# V2 — where physical breeding opportunity, settlement and actual reproductive success can be joined

**2026-10-08 — prospective data-feasibility audit, NOT new biological outcome.** Independent of the frozen PR189 Ecology manuscript, the PR195 Ledda georeference source audit, and PR142 locked individual-resight workflow.

## Target causal question that is not simply prior-art fast ice or colony size

**Can a perturbation create an *ecological mismatch* where an Antarctic breeding place becomes attractive or accessible to nesters but contributes few chicks, or conversely has good expected offspring survival but remains underused because of settlement fidelity?**

This is a question about **stage-specific effective colonization**, not mapped island area or satellite guano. It requires separating:
- **E: physically available, persisting substrate and an independently measured usable approach corridor before initial choice**;
- **S: a genuine breeder attempted to nest at a dated colony-year footprint**, not a model-zero, site label or nonbreeding group;
- **F: a correctly aligned egg/chick survival or fledging endpoint**, not an adult attendance count;
- **R: a later known-age first breeding event traced back to its natal location**, needed only for delayed cohort-debt claims.

Possible rival mechanisms: (a) physical platform disappears after settlement (temporary habitat/ecological trap); (b) opportunity persists but social fidelity suppresses settlement; (c) settlement occurs but food/predation/snow/microclimate suppresses fledging; (d) count/detection stage or coordinate mismatch creates an apparent ecological effect. These alternatives produce different expected E→S→F patterns but are **not identifiable from any two variables alone**.

### Decisive differentiation, when actual field sources become available

| Pre-choice physically usable option | Settling breeders | Verified offspring result | Permitted preliminary mechanism |
|---|---|---|---|
| Sustained | high | high | functional breeding opportunity; not a social trap |
| Sustained | high | low | suitability/settlement mismatch; requires predation, food and weather controls before mechanism |
| Sustained | low | unmeasured | does **not** prove social avoidance; low detection/arrival opportunity possible |
| Short-lived | high | low | possible ecological trap; needs measured nest initiation then substrate loss |
| Short-lived | low | low/unknown | ordinary access/habitat limitation, not a novel biological feedback |

A true **recruitment debt** would additionally require following marked offspring to their first breeding season several years later. A fall in nest or chick numbers is not observed recruitment.

## What actual external records offer, and what they fail to identify

**Best geographical fidelity but no matching nest success:** AADC [Clarke et al. 2003, Bechervaise Island nest positions](https://data.aad.gov.au/metadata/records/bech_nest_locations), doi:10.4225/15/595350e32bffc: K/L/Q nests, nest IDs, spatial measurement quality including some ~0.05 m total-station surveys; historical snapshot around 2000/2002. Independent [Kerry & Emmerson 2017 whole-island breeding success](https://data.aad.gov.au/metadata/records/breeding_success_BI), doi:10.4225/15/59829c7ed97b1: occupied nests and chick totals from 1990/91 through 2004/05, but documented fields are Year/Breeding success/Occupied nests and outcomes are **whole-island aggregated**. A year match cannot transform whole-island chicks into reproductive success at a particular K/L/Q nest. This route **fails the identity/response grain gate** as currently described.

**Best individual reproductive endpoint but no georeferenced exposure:** NOAA [Hinke et al. 2018 original nesting-camera data](https://www.fisheries.noaa.gov/inport/item/52182), doi:10.7289/V5Z036F7, includes [`repro v1-1.xlsx` schema](https://www.fisheries.noaa.gov/inport/item/52186) for rookery, colony, camera, nest, date, lay, hatch and maximum chicks. These permit photo-derived nest-level fate summaries; however the advertised schema has no nest latitude/longitude, year-specific nest platform polygon or independent ice-access corridor. An outcome CSV without E linked to the same nest does not identify an island-habitat mechanism. Site/date keys should be inspected **only after a distinct physical/source endpoint is independently fixed**.

**Rich behavioral field data but both prior art and availability stop:** AADC [Windmill Islands 2011/12–2020/21 nesting data](https://researchdata.edu.au/reproductive-success-adelie-201112-202021/3651217) include 450 marked camera nests at five camera sites, relative periphery rank, nest bowl structure, snow and moisture. However public metadata state **not yet publicly downloadable**, and [McLatchie et al. 2024](https://doi.org/10.1002/ece3.10988) already tested occupation timing, nest construction and moisture interactions, finding a nest-structure survival benefit that strengthened when wetter/snowier. Do not present this already-published result as a new mechanism.

**Potential linked subcolony and breeding-success panel but source is down:** [Signy Island long-term nesting and reproductive success](https://doi.org/10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d) includes GPS points and site-level nest/chick counts, but BAS' primary file service currently reports it temporarily unavailable. Even a clean subcolony×year file would lack known individual origins and a demonstrated externally dated stage-specific perturbation; site-year brood counts do not identify immigration versus birth-cohort recruitment.

**Best geographic breadth but no success linkage:** AADC [East Antarctic multi-year colony boundaries](https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_breeding_colony_boundaries), doi:10.4225/15/58f59b52edfef, comprises many dated spatial subgroups with heterogeneous collection methods and site identifiers. It is excellent for **defining the spatial unit** but not automatically linked to individual nest fate or independent access shocks; each group-year needs stable ID, digitization/effort and breeding stage checks.

## Prior-art exclusions that substantially narrow novelty

- **Cape Crozier 2018**: LaRue et al. (2019; doi:10.1017/S095410201900018X) documented 426 Adélie penguins displaying apparent nesting behaviour on fast ice about 3 km from the mainland colony, present for at least a month before ice loss in December; **eggs, fledging and later recruitment were NOT verified**. A distinctive example of potentially attractive ephemeral habitat, not proof of a demonstrated fitness trap.
- **Coulman 2025**: Park et al. (2026; doi:10.1038/s43247-026-03764-w) already reports a grounded iceberg obstructing emperor colony access with approximately **69% decline in chick counts**. Obstruction and stage effects are **not new**; source chick counts are published, no independent counterfactual for exact age-cohort debt.
- **Cape Hallett 1960/1983/2019**: Kim et al. (2023; doi:10.3390/d15010051) has already described penguin recolonization after removal of an anthropogenic station and artificial mound opportunities. The authors did **not** independently tag return founders or measure controlled nest-specific fledging in occupied versus unoccupied reconstructed plots.
- **Edmonson Point 2019**: Kim et al. (2026; doi:10.1002/jgo2.70001) documents redistribution following flooding on a **continental coastal point**. This demonstrates redistribution need not cross an island boundary; nest-count changes cannot be interpreted as tracked movement or net survival.

## Decision / next usable data gate

**Status: HOLD_NEST_HABITAT_FITNESS_JOIN_AND_IDENTIFICATION.** There is no verified public-source data pair yet that simultaneously identifies an externally timed pre-choice physical opportunity, an actual settling breeder at that footprint, and aligned reproductive outcome with detection controls, let alone known-origin first recruitment. The identified datasets are useful **components**, but forcing a join across incompatible years/IDs/grains would manufacture evidence.

A future independent test must first show a machine-checked exact join on (year, site/patch, reproductive stage, nest or breeding-unit ID), then independently measured physical access and at least two disturbances with controls. If the data only support a within-island settlement-versus-productivity contrast, restrict the claim to that contrast and **do not call it a novel general island law**.

No new biological row opened in this V2 audit; no model fit, p-value, or newly established fitness effect. No change to PR189.
