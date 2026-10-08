# Are historically suitable but unused breeding platforms real refuges after fast-ice shock?

**Date: 2026-10-08. Pre-outcome source-identifiability research lane. No new positive ecological result.**

## A sharper ecological question

Antarctic breeding-habitat studies generally classify a site as habitable from a long-term ice or geomorphic surface. **But a biologically viable refuge must be both physically present *when needed* and actually colonized by a reproductive group.** These are distinct processes. In seabirds, the remaining gap may be choice/natal fidelity/social attraction, not missing nesting area.

This project tests the **realized option value** of unused breeding habitat after an unusually large, abrupt disturbance. It is not another distribution model predicting static colony presence, and it does not present penguin colony relocation as a new phenomenon.

> When early fast ice breaks apart at a breeding colony, do nearby **previously unoccupied but historically stable ice platforms** get used for breeding during the next season, or do birds return to the original site (or become unobservable) despite those options?

This is falsifiable. Having unused habitat and observing displacement is not enough. The important response is **verified uptake of a previously vacant option after an independently assessed shock**.

## Why this differs from earlier studies — and where it overlaps

1. **Labrousse et al. (2023), Science Advances, doi:10.1126/sciadv.adg8340:** using 2000–2018 fast-ice features and presence/absence habitats, found no clear present-versus-absent discrimination; however, they explicitly warned power might be inadequate, and themselves proposed ~220-km colony spacing/intraspecific competition, alternative vacant breeding areas, dispersal barriers and social fidelity. **NONE of these ideas are original discoveries here.**
2. **Fretwell et al. (2023/2024):** breeding failure after 2022 and 2023 ice breakups is prior art. **Nineteen of 66** reported affected in 2022, **14 of 66** in 2023; crucially these are **not 19 or 14 verified adult colony extinctions**, nor 33 independent new vacancies. Published denominators may change as colonies are added to the official inventory.
3. **Macdonald et al. (2026):** three historically mapped emperor colonies do not respond identically to ice-shelf calving; Mertz and SANAE relocate, Astrid remains near its original shelter. This comparison is itself already published.
4. **Fretwell et al. (2026), Communications Biology:** the existence of five major shifts/new colonies is already documented; two likely calving-related relocations. Do not relabel those published shifts as novel.
5. **What may be untested:** the site-level **out-of-period matched prediction** from *independently measured 2010–2018 candidate refuge persistence* to *realized use and re-use after 2022–2023 shocks*, with **contemporaneous platform survival/passability independently verified**.

The temporal separation helps prevent retrospective choosing of a 'suitable' landing site solely because penguins eventually appeared there. It is not randomization and does not itself establish causality.

## 2026-10-08 literature-backed boundary: leaving is not the same as choosing a vacant refuge

**Garnier et al. (2025), Ecology and Evolution, doi:10.1002/ece3.71367**, already coupled penguin genetic markers and demographic metapopulation dynamics, and strongly favored *semi-informed dispersal* over both random and fully informed dispersal. Published DICs: **−41 semi-informed**, **684 random**, **676 fully informed**. In the best model penguins **leave deteriorating colonies according to habitat/growth state**, but **choose randomly among other represented breeding colonies** within the dispersal kernel. Published inferred mean successful dispersal distance ~**414 km** (not an actual tag-tracked natal dispersal distribution) and mean modeled emigration 15.7%/colony/year, although many colony-years have median emigration zero. This is powerful prior art; the novelty of environmental triggers for departure and semi-informed dispersal is already taken.

**Read the public author's code, not just the abstract.** In `garnieji/EP_demographic_genetic` pinned main SHA `bae0db2aedf6d18870287110797b9d8d1818ccc0`, `EP_project_informed.m` builds a **fixed list of colony nodes** (the available example reads 54 rows from `COL_EP.xlsx`), initializes carrying capacity `K=2*BE` from baseline census, and dispersal destinations from a connectivity matrix among those listed colonies. This is a valid conditional *among-known-colony* dispersal framework. The paper refers to a 66-colony study network, so **54-code versus 66-paper scope must be reconciled** before treating that one code file as the precise final version. Either way, **a previously empty but physically available nest-site option is not a calibrated destination category in the cited fixed-colony formulation**.

Therefore the new, biological (not methodological) question is **not** "is emigration informed?" but:

> **After habitat catastrophe, are penguins preferentially absorbed into *already occupied* breeding colonies, or do they establish breeding at physically available but previously unused nearby sites, when both are accessible?**

The Halley→Dawson event is an already-published example of the **occupied receiver** pathway, while the "unused refuge" category demands a genuine repeat-surveyed zero and contemporary habitat/route verification. A model that chooses among known colonies **cannot by itself tell us that unused vacant sites are unattractive or that social information caused their exclusion**; those are ecological alternatives requiring explicit observations.

This also fixes a real spatial-screen error. Since inferred reproductive dispersal can average ~414 km, a **100-km primary screen is local-option screening only**, **not a census of all potential emigrant destinations**. The old 200–400 km "negative control" is retracted: it lies within the inferred movement scale. Use pre-specified 250/500/1000-km strata as regional sensitivity, never assume negligible movement or use them as biologically impossible controls.

Competing mechanism predictions:
- **Established-colony attraction:** documented first breeding or repeated successful occupancy after shock occurs disproportionately in **already occupied** receiving sites, conditional on genuine candidate availability, physical access and existing population size.
- **De novo refuge uptake:** previously verified empty sites gain **documented breeders** after shock, with repeat occupancy when ice permits, beyond the source's effect on emigrant output.
- **Pure exposure/access filtering:** apparent preference for established sites disappears when independent *event-year* access/ice retention/survey effort and travel geometry are compared; social preference would remain unproven.
- **Observation artifact:** new groups were previously present but undetected, or source/receiver polygons changed; site status is not known.

A successful test would change island/metapopulation ecology by separating the **departure decision** from the **creation of a new reproductive network node**. It would not claim the Garnier result was wrong; it tests a destination class that his historical inference did not resolve.

Sources:
- Published full text: https://doi.org/10.1002/ece3.71367
- Audited public code: https://github.com/garnieji/EP_demographic_genetic/blob/bae0db2aedf6d18870287110797b9d8d1818ccc0/EP_project_informed.m
- Prior Halley positive control: https://doi.org/10.1017/S0954102019000099


## Three processes to distinguish, not conflate

| Ecological process | Observable expectation | Strong rival |
|---|---|---|
| **Latent habitat insurance** | Under comparable locally severe early breakups, options historically stable and still physically available in 2022 are preferentially adopted and occupied again in the next surveyed breeding season | Options exist but never used due to philopatry/social attraction or unmeasured quality |
| **Persistence of site fidelity** | Adults return to historically used positions after a bad breeding season despite nearby viable alternatives | Current-season options actually disappeared; remote imagery simply missed subgroups |
| **Competition/social inhibition** | Unoccupied options near an established neighbor are avoided even where their physical environment is similar | Shared food/sea access, observation effort or natal philopatry, **not competition** |

The first two processes are distinguishable in a repeated **colony-site** panel. The third cannot be assigned a **causal mechanism** without independent neighbor population density/contact and matched geographical prey/access.

### A particularly important non-equivalence

- **Breeding failure:** loss of chicks or fledging opportunities because fast ice breaks up too early. Adults may survive, return to the same place, or skip breeding.
- **Colony-site disappearance:** no breeding animals **after verified whole-site imagery/search coverage**.
- **Relocation:** a breeding group is observed somewhere else with a linked former site and a qualified temporal gap.
- **Dispersal / recolonization:** individual origin and successful breeding at a different site, usually *not* recoverable from guano or group position images alone.

**Never count 2022's 19 affected emperor sites as 19 extinction/recolonization opportunities.**

## Matched data that have been located, but NOT downloaded/validated

**Independent historical environmental baseline:** Labrousse et al. Dryad, released 2026-03-19, doi:10.5061/dryad.tmpg4f547. Reproducible data include **2010–2018 fast-ice persistence and seasonal-variation surfaces** as 1-km raster, coastal geomorphology `Antarctic_Cx_11_class.nc`, and colony inventory `colonies.xlsx`. Dryad's data file names and sizes were verified on its public listing. This is a 1.22 GB collection; no entire-repository retrieval is justified.

**Post-disturbance response:**
- Fretwell et al. 2023 Bellingshausen Sea 2022 geolocations and imagery: NERC PDC doi:10.5285/a777e89c-ffcc-4ff4-981c-8f37e5ca84c2, **five regional site records, NOT a complete 66-site census**.
- Fretwell 2024 circumpolar 2023 colony positions: PDC doi:10.5285/fb0547e4-d2c1-4580-8c98-182f1da7d9ae. Published accuracy **~2 km** and snapshot in August–December. Metadata says **Dataset Progress: Planned** (accession exists but full file completeness not verified).
- 2024+ site-by-site equally surveyed records not yet verified. Treat unknown follow-up status as **missing**, not biological absence.

**Contemporaneous access requirement:** the fact an unoccupied ice pixel persisted historically (2010–2018) **does not prove it was still a stable or reachable platform during the 2022 catastrophe**. Independently dated pre-switch 2022 fast-ice images and breakup chronology are a mandatory source, not a sensitivity option. No localization of the bird can substitute for this access measure; that would be circular.

## Source metadata reconciliation — why a tempting 66-site test is NOT ready

The published Dryad **README**, not just the file names, gives additional hard limits:

- Labrousse et al. constructed **3-km presence buffers around 55 emperor colony locations**, not a frozen census of all the 66 colonies later used in the 2022–2023 disruption summaries. A change from 55 catalogued locations to 66/70 known colonies is a **change in discovery/catalogue coverage**, not 11/15 documented new biological colonizations. Link records by exact site identity before cross-period comparisons.
- Their underlying MODIS fast-ice series has **432 half-monthly time steps from 2000–2018**, while their published summary metrics (persistence, volatility, seasonal extrema, trend) and 9-year environmental layers use **2010–2018**. Do **not** combine the 18-year raw ice series with 9-year summary products as if they have identical historical windows.
- The published 'absence habitats' are environmental comparison/control locations, **not explicit records of biologically surveyed zero colonies at all proposed refuge patches**. A physically stable model-absence pixel must pass a separate multi-year actual non-occupation detection gate before its "new colonization" can be claimed.
- The 2022 UK PDC source spatially covers **five Bellingshausen sites** (not 66); the 2023 location source is circumpolar, publicly described as accurate to around **2 km**, and its metadata still says **Planned**. This makes a 2022–2023 66-site join **unverified**, not an available panel.
- Additional prior art: a 2025/2026 *Remote Sensing of Environment* study (PII S0034425725003888) already measured short-range colony habitat displacement under climate extremes for ten emperor colonies through 2023. **Do not present storm-related within-colony movement as the new ecological process.**

The crucial empirical discovery target is therefore now narrower: **independently surveyed vacant habitat that physically survives the extreme event, and is newly occupied with verified breeding in subsequent years**. Neither the Dryad "absence" label nor a failure count supplies that response. At this stage even the eligibility gate for the candidate is **HOLD**, not a positive result.

Source inventory and status: `results/EMPEROR_VACANT_REFUGE_EXISTING_DATA_SUPPORT_AUDIT_V1.json`.

## 2026-10-08 design correction — documented **occupied-colony** rescue vs hypothetical **unused-refuge** rescue

A major flaw in the original 40-km primary distance screen was found from **existing prior art**. A famous fast-ice catastrophe already generated a substantial regional redistribution that crosses **more than 40 km**, and the destination was **not vacant**.

**Fretwell & Trathan (2019)** (*Antarctic Science*, doi:10.1017/S0954102019000099): Halley Bay's breeding ice failed during 2016–2018 while the pre-existing **Dawson–Lambton** colony showed the following satellite-estimated birds/pairs:

| Season | Published Dawson–Lambton satellite-derived pair estimate |
|---|---:|
| 2015 | 1,280 |
| 2016 | 5,315 |
| 2017 | 11,117 |
| 2018 | 14,612 |

That is **+13,332 compared with 2015 (11.4156× the baseline)**, a previously **published** redistribution pattern. The 2019 study explicitly notes that many 2016–2017 Dawson birds were dispersed and likely **not breeding**, whereas the 2018 colony showed large tight groups and intense guano staining consistent with sustained occupancy. None of these aggregate counts identifies the precise natal origin of individual immigrants, individual lifetime breeding, offspring survival or recruit production. The authors inferred a link to Halley's catastrophe; this causal interpretation is **prior art**, not the new result of PR #195. The satellite counts mix stage and attendance uncertainty.

**Distance audit:** Fretwell & Trathan 2019 state **55 km**; Fretwell et al. 2025 state **85 km**. WGS84 great-circle from Fretwell & Trathan 2019 published site coordinates (Halley 75°33′S, 27°32′W; Dawson 76°04′S, 26°40′W) is **62.12 km**. These are not interchangeable spatial/route definitions, and the origin at a moving ice shelf can itself move. This inconsistency requires explicit distance provenance in spatial analysis. **All three estimates exceed the old 40-km primary radius.**

**Frozen design amendment BEFORE opening site-level 2022–2024 outcomes:**
- Primary candidate neighborhood = **100 km** straight-line eligibility, sensitivities **40, 80, 160 km**. Distant comparator = **200–400 km**. These are literature-informed scales, *not blind confirmatory choices*. Use physical travel/passability paths rather than straight-line kilometers if externally measured.
- Distinguish **occupied receiving colony** (Dawson 2015; demonstrated potential to absorb displaced adults) from **previously vacant option** (requires independently surveyed prior zero and verified availability). The original "vacant refuge" theory must not score Dawson as successful previously-unoccupied colonization.
- At each receiver separate **arrival/colony attendance** → **documented current breeding** → **successful offspring** → **next-year persistence**. These cannot be silently conflated.
- Halley is an **in-sample prior-art positive control** for the *existence of receiving-colony concentration*, not a prospective confirmation of a new capacity/competition/fidelity model.

**Interpretation for mechanism:** there are at least two biologically different forms of 'rescue'. One is redistribution into a **known, socially occupied colony**, potentially yielding rapid adult spatial recovery without immediate chick production; the other is de novo use of a **previously vacant but environmentally suitable** breeding alternative. The social-attraction-versus-new-site-choice contrast might matter, but the Halley case alone does not identify an Allee/social mechanism. Prior breeding success of the receiver and local ice stability must be independently documented, and comparative origin data are currently absent.

Primary sources: https://doi.org/10.1017/S0954102019000099 ; https://doi.org/10.1038/s43247-025-02345-7

## Before looking at any 2022–2024 site-specific displacement values

1. Freeze a cohort-ID crosswalk that resolves relocated, renamed, rediscovered or newly recognized colony records without using biological outcome sizes. **Historical 66 vs subsequent 70 known colonies cannot be treated as identical rosters.**
2. Freeze study units as physical colony-zone × breeding season, with repeated imagery and independently reported missingness/coverage.
3. Map pre-2019 historical stability for candidate alternatives independently of later occupancy. Separate local choice (<100 km), 40/80/160 km sensitivity, and regional 250/500/1000 km source-receiver strata. Do not equate far distances with no dispersal.
4. Independently certify that each potential alternative existed *before the observed 2022/2023 relocation*, was reachable in the relevant breeding phase, and was not occupied in the prior detection-qualified period. The 2010–2018 grid itself **is not enough**.
5. Match by breakup dates, regional wind/forcing, latitude, old-colony size and satellite survey opportunity. Exclude any site that cannot be distinguished from a moving subdivision of the original group.
6. Analyze realized uptake **and qualified subsequent persistence** separately. A positive zero→occupied event cannot be deduced from missing 2021 imagery.
7. Gate sample power on **independent documented relocation/persistence episodes**. If fewer than 10 have complete origin-destination and matched pre-switch alternatives, no general causal claim, regardless of the number of 1-km candidate pixels.

## What a discriminating result would change

- **Positive uptake and persistence into historically stable available pockets, beyond current ice and exposure:** unoccupied options can supply realized demographic/spatial insurance. Still not evidence of inter-island *individual breeding migration*.
- **No uptake despite independently verified viable option availability and adequate effort:** refutes a strong *automatic capacity creates rescue* hypothesis; points to settlement history, social attraction or some unmeasured limitation, which must then be separated rather than declared as fact.
- **No pre-switch access/effort data:** the candidate is **not identifiable**, even if one can build a visually impressive relocation map. Stop; don't promote a descriptive result into a novel ecological cause.

**Critical island-biogeography boundary:** emperor ice platforms move and break; they are not offshore terrestrial islands. The mechanism can inform *dynamic habitat-opportunity limitation*, but it cannot be used as a new MacArthur–Wilson island immigration finding without real island-to-island breeder origin evidence. Frozen PR #189, source-island PR #192, and separate GitHub PR #194 remain unchanged.

## Public sources

- Historical occupied/vacant habitats: https://doi.org/10.1126/sciadv.adg8340
- 2010–18 raster/data release: https://doi.org/10.5061/dryad.tmpg4f547
- 2022 Bellingshausen positions: https://doi.org/10.5285/a777e89c-ffcc-4ff4-981c-8f37e5ca84c2
- 2023 circumpolar positions: https://doi.org/10.5285/fb0547e4-d2c1-4580-8c98-182f1da7d9ae
- Fretwell 2026 relocations: https://doi.org/10.1038/s42003-026-10961-y
- Macdonald 2026 long-term calving response: https://doi.org/10.1017/S0954102025100515

## 2026-10-08 V4: four reported sites against 66 actual listed options, plus an observation-state veto

The question is now constrained by **two new empirical source checks**, both retrospective:

**1. A real geographical roster calculation.** Crosswalk the 4 emperor nesting locations reported in Fretwell (2024) onto a **fixed public list of 66 emperor colonies** (Garnier 2025-associated `bilgecansen/Emperor_dispersal`, pinned commit `8254f7014dd749e5497165ab854b7f76b276e791`, exact `data/empe_sitesNewNB.csv`). Distances are great-circle (not marine travel), from each report's published WGS84 coordinates to the nearest row **in that list**:

| Newly reported site | Nearest *listed* established-catalogue location | WGS84 geodesic |
|---|---|---:|
| Lazarev North | Lazarev (old site) | **54.24 km** |
| Verleger Point | Cruzen Island | **124.72 km** |
| Vanhoeffen | Karelin Bay | **63.23 km** |
| Gipps Ice Rise | Dolleman | **215.34 km** |

**2/4** are farther than the literature-informed 100km local candidate radius from **every location on the 66-row list**; all four are below **414km**, which is *the inferred mean dispersal distance, not a hard movement limit*. This is an **actual public catalogue × published-site proximity computation**. It does **not** show true first foundation, usable accessible vacant habitat, migration, or that the nearest *listed* old colony was biologically occupied in the target year (Lazarev old is specifically a discontinued site). This list is an author-distributed **candidate catalogue**, not proof of a single synchronous 66-node fitted probability model, and the 2016/2018 new-site positives need not have existed in earlier fitting eras.

Files: `scripts/audit_emperor_2024_new_sites_against_66_catalogue.py` (checks pinned remote Git blob SHA) and `results/EMPEROR_66_CATALOGUE_NEWLY_REPORTED_SITES_GEODESIC_V1.json`. Tests reject altered source SHA and false first-colonization claims.

**2. A critical original observation-codebook identifiability trap.** The publicly released LaRue et al. (2024, *Proc R Soc B*, DOI `10.1098/rspb.2023.2067`) source `empe_satellite_2023-05-25.xlsx` monitors **50 known colonies in 2009–2018**. **Their `bpresent=No` means either a valid image had no birds *OR THE FAST ICE WAS ABSENT***; `bpresent=NA` means no usable image/inconclusive status; and an empty `catalog_id` can mean older Fretwell (2012) imagery rather than no image. The area of penguin pixels is not successful breeding. Source: [Dryad DOI `10.5061/dryad.m63xsj48v`](https://datadryad.org/dataset/doi%3A10.5061/dryad.m63xsj48v), README and [public authors' analysis code](https://github.com/davidiles/EMPE_Global/tree/13f71112da43c1fd082273677757b41c550457ed). This is an **author-codebook source fact**, not a new re-analysis of bird response rows.

Consequently, fitting 'unoccupied suitable platform' directly from `bpresent=No` would confound **physical nesting opportunity loss** with **socially/behaviorally unoccupied but available habitat**. It would create the very false biological conclusion this project aims to avoid. To use this 50-site source, first independently classify fast-ice availability, image quality, appropriate season and repeated actual negative surveys. Never treat all 50 known colony locations as known unused *alternative* refuges.

**Biological conclusion from V4:** recorded positions in 2024 demonstrate historical use across gaps of approximately 54–215km to listed nodes, but do **not** distinguish *new-node establishment* versus *survey discovery/relocation*; source `No` observations also do **not** distinguish vacant sites from missing ice. Under the existing data streams the social-choice alternative remains **unidentified**. A different matched before/after source with **independently surveyed vacant but physically available ice** is needed for a genuine ecological causal test. No new 2022+ dataset was opened, no inferential outcome was fitted, and PR #189 remains scientifically frozen.

