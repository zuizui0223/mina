# V33 DRAFT — Predator realized-invasion niche × seabird breeding-refuge niche

**Source/trait phase only (2026-10-27). No JNCC predator-effect fit, no predator SDM and no historical mammal occupancy inferred.**
Extends the V32 source-first mechanism contract in PR #201, not a new manuscript, not a change to published-in-repository V30 (17 species/1,321 panels/959 declining). Existing observed V30 concentration patterns are known before V33.

## Scientific question

Do mammalian predators compress or relocate the **realized breeding niche** of colonial seabirds within or among mapped breeding sites, conditional on island access, predator establishment, nest accessibility and species-level vulnerability? The *predator niche* in island systems is an **introduced, accessibility-conditioned realized occupancy niche**, not simply a climate-only habitat SDM or fundamental Hutchinsonian niche.

Critical contrast: an entire island can be invaded **while inaccessible cliffs/rock crevices still protect individual nesting patches**; conversely a distant island can be reached by human boats. Island size or gap alone must NOT be coded predator absence. A positive association of seabird colonial concentration with island isolation is neither demonstrated predator avoidance nor directly observed dispersal.

## Four distinguishable components

**P — predator occupancy by species, island and census epoch:**
- Primary species for feasibility: American mink (Neogale/Neovison/Mustela vison synonym lineage), brown rat Rattus norvegicus; black rat R. rattus, red fox Vulpes vulpes, feral cat Felis catus and stoat Mustela erminea are independent secondary guilds only if original verified data support them.
- Store per physical-landmass × predator × epoch: CONFIRMED_PRESENT, PROBABLE, POSSIBLE, VERIFIED_SURVEY_ABSENT, ASSUMED_ABSENT, UNKNOWN, ERADICATED (with year and reinvasion history), and OBSERVATION_NOT_RELEVANT. Never merge ASSUMED_ABSENT with surveyed absence, nor PROBABLE with directly confirmed detections. Record observer, survey effort, source date, georeference and license. **No NBN/GBIF record != predator absence.**
- Time anchor for each JNCC original child survey: earlier 1998–2005 (exception Gannet) and later 2015–2021, using original site-specific source years. A 2017 presence map or 2024 management report is not direct truth for 1998/2021. For both censuses, use closest genuinely dated field evidence only with prespecified temporal window and an explicit UNKNOWN if unsupported.

**K — arrival/connectivity niche** (structural potential, not actual status):
- Fully versioned GSHHG 2.3.7 physical landmasses at original first-party site coordinates; minimum water gap to **nearest independently confirmed occupied source island/landmass**, not only Great Britain; regional marine stepping-stone network, coastline accessibility, island area, human habitation and credible boat/harbor propagule pressure.
- Tidal links and causeways are separate time-varying categories. UK official mammal biosecurity excludes tidally connected islands from its strictly offshore SPA cohort: classify HIGH_TIDE_OFFSHORE versus LOW_TIDE_CONNECTED separately; do not silently assume permanently isolated coastline.
- Independently frozen features only, before any JNCC E, child-site shares, or taxonomic V30 ranking is joined. Swimming distances are taxon-specific and conditioned on source evidence rather than chosen to maximize E.

**A — local predator access / micro-refugia:**
- Verified nest/colony footprint, rock crevice/cliff steepness, position above accessible ground, vegetation, beach/burrow/substrate, predator habitat and verified barrier/fence data. A JNCC source Start.Lat/Start.Long point is NOT a nest footprint, so a 30m DEM cell at that point is not proof of cliff or accessible nest.
- Construct fraction of *independently mapped suitable and surveyed nesting habitat* accessible to each predator. Treat coastal colony placement and local access separately from total area of the parent island. Require true surveyed-but-unused habitat where occupancy/niche breadth is interpreted.

**V — source-defined seabird vulnerability by breeding species:**
- Independent Scotland Gov 11 Dec 2024 Annex 3 Table A3.7 and A3.14 reports *combined habitat loss and invasive predatory mammal mortality vulnerability*. It gives 15/17 source-matched JNCC taxon labels; **Black-headed Gull and Common Gull are missing** in that table, not low-risk. 'Sensitive' is an AUTHOR LABEL, not a numerical rank between medium/high. Preserve source confidence in Table A3.7.
- This 2024 category is NOT a predator-specific experimentally estimated effect, NOT independent of all historical expert ecological knowledge, and NOT period-correct occupancy. No predictor scaling/ordering or missing species imputation is authorized by this V33 draft. Original nest form (burrow/ground/cliff/crevice) requires separate fully referenced species/habitat source, not assigned based on V30 E rankings.

## Candidate model hierarchy and estimands (pre-outcome)

1. **Predator SDM/occupancy first, from independent original predator survey data alone.** If repeated site visits with explicitly documented true non-detections and effort exist, detection-corrected hierarchical occupancy: z_{j,p,t}~Bernoulli(psi_{j,p,t}); y_{j,p,t,v}~Bernoulli(z_{j,p,t}*detect_{j,p,t,v}). logit(psi) uses pred-pinned island area/physical gap/access/proxy habitat/propagule pressure, region random effects and time if measured. Separately score temporal invasion/eradication states. Spatially block validation by whole landmass/archipelago and source observer; report calibration/Brier and interval. NO sea-gap coefficient fitted to JNCC outcomes while tuning this predator-only model.
2. **If only point detections (GBIF/NBN) exist:** effort-filter and licensing QA, spatially thinned presence/background point-process intensity, accessible-area (M) background and effort bias covariates, geographically blocked tests. Return RELATIVE OCCURRENCE INTENSITY only; NOT calibrated occupancy probability, not true absence, not 'predator-free' classification.
3. **Predator × seabird exposure:** after an externally validated occupancy or status layer, distinguish island establishment P, local site accessibility A, vulnerability V. Risk proxy R_{i,s,t}=sum_p P_{parent(i),p,t} × A_{i,p,t} × V_{s,p}, only if each factor is observed or independently calibrated on a defensible common scale; otherwise output separate components and uncertainty tiers rather than a fictitious scalar risk.
4. **Seabird composition:** frozen conditional on later parent total, compare each child site's p1 relative to p0 under the V32 finite-count-replayed conditional multinomial model. Signed prediction beta_R<0 for observed/validated predation risk when within-parent R differs across children, conditioned on independently measured site quality, earlier site size, original source count-unit/survey method and regional×species strata. Under genuinely dated island eradication/invasion data, a separate history-matched observational contrast is possible, but 2 census epochs do not prove a causal before-after mechanism.

### Fundamental identifiability condition

If all child sites within a parent have the **same island-level predator status** R_i=c, then the predictor cancels exactly from the conditional compositional model:
q_i = p0_i exp(beta_R c) / sum_j [p0_j exp(beta_R c)] = p0_i.

Thus island occupancy alone cannot explain the *relative* change among children of a same-island JNCC Master-site in a within-parent fixed-effect model. V31's 229 source small/157 large parent classes were largely **all children of one island/landmass**, while 1,092 parents had unresolved/ambiguous original geographic children. To identify within-parent predator-driven concentration, secure verified mixed-landmass parents **or** independently mapped within-island variation in local A (accessible versus protected nest patches) with survey footprints. Between-parent contrasts in V30 E are descriptive and must never be called bird refuge moves.

## Data sources and access boundaries

- UK Marine Strategy official 2024 Invasive Mammal indicator: Stanbury et al. 2017 summarized UK island statuses, mink 23% and brown rat 21% of islands >10 ha reported confirmed/probable. This proves genuine broad island heterogeneity, NOT that source raw 9,688-island table is currently downloadable or census-epoch matched.
- Stanbury et al. 2017 doi:10.1007/s10344-017-1084-7 previously modelled **invasion/eradication potential using island size, human population and predator-specific swimming/reinvasion distance**. Thus a model of island area + distance alone is PRIOR ART, not this project's discovery.
- Gov Scotland 2024 Vulnerability report Annex 2 shows a qualitative four-predator map (mink/brown rat/feral cat/black rat) from Stanbury 2017 with CONFIRMED/PROBABLE/POSSIBLE/ASSUMED_OR_KNOWN_ABSENT; the figure IS NOT downloadable point-level verified survey data, and the last category cannot be used as verified absence.
- 2024 Gov Scotland Annex 3 Table A3.7 (species sensitivity, exposure, vulnerability, confidence) is an accessible original agency table; Table A3.14 contains the 15/17 species categories in the JNCC crosswalk. Exact URLs and verbatim fact extraction recorded in V33 register JSON, with explicit two-species coverage gap.
- NBN Atlas occurrence downloads require user login and dataset-specific licenses. Do NOT bypass controls, send an email, bulk download restricted data, or infer no detection as absence. GBIF public mirrored NBN data are a possible source of records but may cover only provider-permitted datasets and are not automatically an island predator-status census.
- NatureScot March 2026 biosecurity plan documents rat removal from Ailsa Craig, Canna, Handa with later reinvasion, Shiant Isles, and ongoing work elsewhere. Timeline, not current absence alone, is required for the old JNCC epochs. Period-correct exposure remains unverified.

## Data support gates (before predator × JNCC associations)

**Stage A: source-only inventory.** Obtain exact publisher original predator status inventory and rights, field status/dates/effort/island IDs, then crosswalk to frozen GSHHG landmasses and JNCC pre-outcome 1,483 structural parents. Report count of verified present/verified surveyed absent/unknown by predator×epoch and geographic hierarchy. No E, N1/N0 or share outcomes read. If first-party Stanbury/status data unavailable, stop calibrated status modelling; do NOT backfill guessed absences from GBIF.

**Stage B: predator-only model.** For each predator, require >=30 separately mapped independently verified present landmasses and >=30 effort-audited surveyed-absent landmasses spanning >=3 survey regions, with at least 10 sites per class in geographically held-out regions. Threshold is a proposed sample gate not proven feasible. If fail, retain status-only comparisons and uncertainty, no SDM occupancy or predation probability.

**Stage C: site-scale JNCC link.** At least 20 count-eligible **mixed-exposure within-parent** panels across >=5 physical landmasses, >=5 JNCC species and >=3 Country×Master networks, each with >=2 differently exposed child nesting sites (verified site footprint and original habitat/predator accessibility). Parent with uniform exposure supplies no within-parent beta_R information. If fail, stage STOPS without interpreting a negative ecological effect.

**Stage D: stratified historic contrasts.** A temporal invasion/eradication contrast requires source-dated state on both sides of each JNCC census pair plus surveyed controls and original effort/method comparability. Records dated only 2017/2024 cannot supply both times. No pseudo-event study or causal difference-in-differences without support.

**Separation of hypotheses:** H1 size/social retention and H3 independent habitat-quality remain separate and may confound predator risk. Report model variation/uncertainty without choosing the most positive mechanism after observing outcomes. Predation by avian predators (skuas/giant petrels) in Antarctic penguins is a different guild/observation system, not inferred absence of predator pressure. UK tidal/boat connectivity and Antarctic annual fast-ice connectivity may become a future comparative dynamic-boundary hypothesis, NOT an effect demonstrated here.

## Next executable step

1. Freeze source inventory and 15/17 verifiable external vulnerability labels with original cited uncertainty. Preserve two unmatched species as UNKNOWN.
2. Ask for/source-access check of downloadable island-level Stanbury 2017 original predator table from rights holders; separate the map from a censused absence dataset.
3. Independently check coverage and time alignment for GSHHG-mapped JNCC children, without importing any effect values.
4. If Stage A/B pass, fit predator occupancy model alone and validate on held-out physical islands. Only after Stage C opens, fit seabird share response.

**No current predator niche probability surface, actual predation overlap, or predator-driven JNCC beta has been estimated.**
