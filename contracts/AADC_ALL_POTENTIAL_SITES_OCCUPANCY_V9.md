# V9 — East Antarctic all-potential-sites and search-effort-aware seabird macroecology

**2026-10-19; original AADC source record inventory BEFORE accessing original response tables.** Independent research trajectory after V6 and V8 environmental effect gates did not pass; do not re-fit those cohorts. This is a **qualitative change in biological data grain**, from only **known breeding colonies** to a published spatial frame of ALL mapped **potential ice-free sites**, including surveyed nonoccupancy and recognized ignorance.

## TWO original Australian Antarctic Data Centre datasets

1. Southwell, Smith, Bender & Emmerson (2021): *A spatial reference system for coastal ice-free land in East Antarctica*, AADC DOI **10.26179/53yk-8z83** (official URL `https://data.aad.gov.au/eds/4344/download`). Unique 4,884 geographic ice-free land features (37°E–160°E), standalone near-shore islands within 100km of the coast and continental outcrops within 1km of coast. These describe potential *geographic* sites, **not 4,884 systematically verified suitable seabird nesting substrates**. Sources include AAT coast 2003 and SCAR ADD v4.0, not dated annual rock availability.
2. Southwell & Emmerson (2025): *Mapping knowledge of seabird breeding occupancy across East Antarctica*, AADC DOI **10.26179/5n29-r073** (official `https://data.aad.gov.au/eds/5959/download`). Public search-event database of eight land-breeding seabird species from 1910–2020, with species × site × breeding season × presence, directly reported absence, or occupancy unreported/unknown, survey vantage, source and certainty. Publisher manuscript DOI **10.1111/ddi.70066** reports **33,297 search event rows, 5,014 reported breeding presence, 11,701 absence and 16,582 nonreporting events**. These counts are prior art and are NOT our new results. The source authors already tested spatial survey bias, known richness, uncertainty and site coverage; **do not market them as our new discovery**.

Both original datasets declared CC BY 4.0 by AADC, with source attribution mandatory, and encourage contacting custodian before analytical reuse. Contact is **not** a prerequisite to inspecting publicly downloadable source format and eligible counts; do not send correspondence on behalf of user.

## What is new enough to test later, IF actual schema/survey support allows

**Upper question:** In extreme Antarctic coastal environments, do differences in breeding mode between a flightless, exposed-ground colonial seabird (Adélie) and seven volant species using exposed ground, cliffs and sheltered crevices interact with **site area, island vs continental substrate and geographical isolation** to predict *verified occupancy*, after separating historical search effort and species-specific detectability?

This is an explicit **guild × spatial habitat interaction** question, not a general statement that small islands have fewer species. H0: after original search effort/certainty, proximity to human research stations, geography, bioclimate and ice-free land area, nest-substrate guild and island isolation do not explain different occupancy patterns. H1 (proposed only): species using small crevices/rock ledges, exposed ground and large colonies show different area/isolation thresholds for persistence in these cold islands. The direction is **not prechosen**, because both snow and shelter may limit colonization in opposite ways; a selected sign after data would be exploratory. A flightless Adélie is not assumed dispersal-limited like terrestrial flightless birds (marine swimming); total occupancy could be enhanced on isolated islands if they avoid terrestrial predators.

### Scientific nesting-mode grounding

Eight original land-breeding species: `Pygoscelis adeliae`, `Thalassoica antarctica`, `Daption capense`, `Fulmarus glacialoides`, `Macronectes giganteus`, `Stercorarius maccormicki`, `Pagodroma nivea`, `Oceanites oceanicus`. Functional nesting guild labels must be assigned by externally documented references **before** seeing effect results, including mode ambiguity; do not infer actual nest type from a Latin name alone. Emperor is deliberately excluded because primarily fast-ice nesting; its distinct non-land recruitment ecology needs another physical habitat frame.

### Stage 1 ORIGINAL source gate now

- Download both original exact DOI-linked URLs using verified official HTTPS AADC host. Stream to bounded source files (100 MB maximum each, 250 MB aggregate). Record HTTP response status, final URL, MIME, Content-Disposition, SHA256 and byte count; accept ZIP, CSV, XLSX (Excel XML ZIP) or PDF/text source metadata. If AADC requires authentication or redirects to unsupported services, **STOP and record**; never invent row counts or a JSON API response.
- Inspect ONLY source archive member list, declared headers / XLSX sheet names, original table row counts per sheet if structural metadata permits, site identifier fields, original status and effort column names, geometry/size/isolation data availability. Keep biological values unopened at this stage.
- Do not treat a `nonreporting` (species not mentioned) as verified absence. Original `absence` certainty H/M/L is not equivalent across taxa and survey methods; when appropriate, analyze high-confidence absence separately. If effort does not explicitly state species searched, do not assign 0.
- Coverage and source age: original site polygons and occupancy records refer to different observation eras; static rock polygons are not actual 2020–26 substrate creation. The 4,884 features are **geographic potential sites** not demonstrated vacant but suitable nests.
- If datasets are complete and linkable by stable site UFI, independently check geographic unit IDs and source overlap with APBP, and only then freeze a substantive before-outcome model specification and fit once, with geographic source and year holdouts. Avoid model rescue by recoding absences.

### What an identifiable new result would need (not yet claimed)

A strong island-biogeography claim requires: (i) **contemporaneous high-certainty search effort at both occupied and unoccupied geographic sites**, (ii) independently measured island-size/isolation/geomorphology/ecosystem class from natural land polygons, (iii) species traits or functional guilds fixed outside outcome selection, and (iv) spatial-region and publisher-source holdouts. If these ingredients are missing, first report sample-support and stop. Previously published uncertainty mapping is prior art; original novelty must come from **new cross-taxonomic interaction tests** not performed by Southwell et al. 2025.

Freeze *Ecology* PR189, previous V6 negative and V8 nonrobust results. No petrel/skua island-size effect has been measured or is inferred here.

## Added prior-art boundary before original V9 outcome rows

Southwell et al. 2017, *The Auk*, "Recent Studies Overestimate Colonization and Extinction Events for Adélie Penguin Breeding Colonies" (DOI to verify in canonical publisher), had **already** challenged apparent colony turnover from historical occupancy records. Southwell et al. 2025 *Diversity and Distributions*, DOI `10.1111/ddi.70066`, directly assessed knowledge, ignorance, presence/absence certainty and known species richness from this same 33,297-record source. These are **explicit prior art**, not V9 discoveries. The prospective distinct question must be a *trait-by-physical-island-feature interaction* with correct detection/absence classes; otherwise do not make another paper.

AADC citation page states it is an expected professional norm for intended research users to contact source originators to discuss use. This is not required to retrieve a released CC BY file and assess schema; any later collaboration or publication using this corpus should honor that guidance. No unapproved email is sent from this workflow.
