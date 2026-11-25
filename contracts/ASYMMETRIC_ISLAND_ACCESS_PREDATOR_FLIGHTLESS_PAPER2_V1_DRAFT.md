# Island asymmetric-access hypothesis — canonical mina Paper 2 ecology mainline (DRAFT V1)

**2026-10-27 | Main scientific goal: explain how islands function as refuges OR bottlenecks to breeding, using mammalian predation, the loss of bird flight, and Antarctica as a natural comparative setting.** This is ONE integrated original-data island-biogeography hypothesis, **not** an additional paper, not yet empirically supported or preregistered. Preserve frozen Ecology manuscript PR #189, Antarctica source PR #197/#199 existing endpoints, and UK JNCC descriptive/negative-mechanism PR #201.

## One question and one novel hypothesis

**Question:** When does physical isolation of marine breeding terrain protect seabirds from terrestrial mammals, and when does that same geography constrain marine breeders from reaching usable nests?

**Asymmetric-access / dual-permeability hypothesis:** The ecological function of an island depends on the mismatch between **predator access to nesting terrain** and **breeder access from foraging sea to nesting terrain**, not island area, physical isolation distance or seabird density alone.

Species-specific safe-and-reachable breeding patch is a *potential land cell* satisfying (a) actual seasonally ice-free/substrate habitat, (b) plausible path from the sea for a particular bird, and (c) sufficiently low verified terrestrial mammal reach/pressure. The two reach probabilities/feasibilities must be independently measured; not imputed from the bird nest occupancy outcome. Flight-capable birds may reach ledges unsuitable for walking access, whereas flightless penguins can swim across water but must traverse a terrestrial/snow/ice route from the sea to a nest. Water gap does NOT prevent penguins from swimming between islands; on-land walkability is distinct from at-sea swimming access. Terrestrial mammal island occupancy is distinct from access **within** an island. Penguin flightlessness predates current Antarctic islands; this project does NOT claim Antarctica caused the evolutionary loss of flight.

The causal contrast is **asymmetric access**, not a binary 'island vs mainland' nor 'Antarctica vs Britain' comparison.

## Known literature and novelty boundary

- Introduced terrestrial mammal predation is a well established driver of seabird island losses (NatureScot 2025, `https://www.nature.scot/doc/naturescot-research-report-1370-potential-actions-support-recovery-seabird-populations-scotland`). 'Mammal-free islands are safe refuges' is NOT novel.
- Penguin ice-free nesting, slope/sea access, geomorphology and breeding substrate already documented (Adélie density dependence study `https://pmc.ncbi.nlm.nih.gov/articles/PMC7069296/`; Gallagher et al. 2025 `https://doi.org/10.1002/ecs2.70091`; penguin landscape review `https://doi.org/10.1007/s10531-023-02557-3`). 'Penguins nest on ice-free rock near the sea' is NOT novel.
- Even an ice barrier demonstrably disrupting access at Coulman Island (2026) is already published: `https://www.nature.com/articles/s43247-026-03764-w`. Do NOT sell corridor blockage itself as a unique discovery.
- **The testable synthesis is a crossover interaction:** a breeding terrain feature can **increase refuge value for flying seabirds** on mammal-exposed islands, yet **decrease reachable breeding capacity for flightless penguins**, even when mammalian predators are naturally absent. Need actual land-cell availability and observed bird nests to demonstrate.
- Antarctica on its main breeding coasts lacks **established invasive terrestrial mammalian predators**, but is NOT 'predator-free': skuas, petrels, marine seals and whales can prey on penguin eggs/chicks or adults, according to species and habitat (`https://www.antarctica.gov.au/about-antarctica/animals/penguins/`). Subantarctic islands such as the Falklands and South Georgia may harbor introduced mammals and CANNOT be lumped with the Antarctic Peninsula/continent as predator-free.

## Anatomical/physical access definitions, NOT borrowed ecological outcomes

For an independently mapped candidate ice-free nesting land patch cell c, island i, species s and breeding season t:

- `B(i,s,c,t)` = probability or feasibility of a breeding adult entering nesting cell from the ocean, given surface passability, seasonal snow/sea ice, slope and path length; model/ground-track validation required. For flightless penguins explicitly calculate shoreline-entry-to-nest terrain-constrained LEAST COST route, not straight Euclidean distance and not open-water inter-island gap. For flying birds model landing/ledge accessibility independently, do not simply hardcode 1.
- `M(i,m,c,t)` = terrestrial mammal pressure/access based on separately recorded source species m present on physical island, arrival/history and passable route to nest cell; **status unknown ≠ absent**. Even rats and mink vary in cliff, boulder, swimming and burrow access; do not conflate source species.
- `K(i,s,t)` = independently mapped candidate potential nesting area that is simultaneously accessible to bird AND low exposed to independently documented mammalian predators. Do not compute K on cells defined *because* a bird nests there; mapping must include genuinely surveyed unoccupied potential cells.
- `Marine(i,s,t)` = independent regional/foraging marine forcing (sea-ice, prey, ocean conditions, campaign year) controls, not inferred from the same colony abundances.
- `O(i,s,c,t)` = observed occupancy, pair density, breeding success or same-method seasonally repeated abundance **with verified survey coverage**. Must distinguish occupancy, bird breeding status, nest success, observed count and composition.

### Explicit rival hypotheses and differential predictions

**H_M — Mammalian nesting-predation refuge, conditional on bird reach.**
Within the **Falklands** (same region/matched marine/year and habitat coverage), the association between demonstrated invasive mammal exposure and surveyed breeding use/success is more adverse for accessible ground/burrow nest patches than for independently verified predator-inaccessible ledges or offshore patches. If any effect exists, it should be modified by local predator route accessibility (source-specific mammals), not merely island area. **Competing**: predator presence may be a proxy for human access/survey effort or habitat degradation; some cat/rat co-occurrence may not generate strong seabird predation.

**H_F — Flightless-breeder access constraint in naturally mammal-free Antarctic comparison.**
Within an Antarctic region with documented no established invasive terrestrial mammalian predators and independent verified nest survey coverage, **terrain-constrained shore-to-breeding-patch walking accessibility** should predict penguin nest use or population/patch response more strongly than it predicts flying seabird nest use, conditional on independently mapped substrate, year, marine conditions and observation effort. **Competing**: all seabirds prefer/avoid certain microclimates or coastal substrate regardless of flight, so an interaction by locomotion might vanish after habitat controls.

**H_X — Crossover / reversal in island role (PRIMARY synthesis).**
The *same* terrain/sea access or island refuge contrast should have a different sign or magnitude across bird locomotor ability **conditional on mammals**. In mammal-exposed islands, physical inaccessibility to mammals can favor flying bird refuges while remaining costly or inaccessible to penguins. On mammal-free islands, the mammalian refuge advantage disappears, leaving breeder terrain access as limiting. The formal contrast is a **predator access × bird flight capability × physical access** interaction (or independently estimable within-region contrasts), NOT an England-vs-Antarctica unadjusted contrast.

**H_0 variants:** A marine-only model explains all matched annual nest-count responses; a static ice-free-area-only model explains habitats regardless of terrestrial routes; general isolation/area+human visitation explains predator reports regardless of physical predator movement; different survey program/effort explains apparent turnover. Test all before interpreting H_X.

### Nontrivial falsification
If under verified mammal-free and matched substrate conditions the route-cost penalty is indistinguishable for penguins and volant seabirds, H_F loses support; if independently verified mammal-exposed and mammal-free islands show no guild-conditional refuge benefit after surveillance/effort, H_M loses support. If both mechanisms operate but not with sign crossover, H_X specifically FAILS while its components may still be true. Do not relabel any non-significant result as a success.

## Design: one program, two internally contrasted natural-comparison arms

**Falklands arm — terrestrial mammal invasion / presence and flight contrast INSIDE ONE archipelago.**
Use original Falkland Islands Government FIBDv8 island geography (534 unique source names, 532 plausible WGS84 centroids), 1,212 invasive mammal record rows, 4,964 visit rows over 533 matched location names, and 4,959 original bird source rows (including header). Existing source V43b verified 1,211/1,212 invasive rows exactly matching island names. Bird `Presence`, `Breeding status`, `Count`, and `Time surveying` original columns are candidates, NOT yet verified historical P/A repeated effort. FIBD rat status includes field-surveyed and desktop-assessed absences (explicit publisher warning, `https://dataportal.saeri.org/dataset/fibdv8-20140601-invasives`): **no-record ≠ absent; suspected/desktop ≠ surveyed nondetection**. Need independently classified surveyed mammal statuses / effort to fit H_M. Same-source penguin and flying bird records should be compared within island/region/year/actual survey method, not assume all 534 islands or birds have matched surveys. UK RSPB/Stanbury V40 source-label SDMs and V44 null guild test are historical background, NOT substitute local predator truth.

**Antarctic arm — flightlessness and terrain without introduced land mammals.**
Use authenticated SCAR land/rock atlas (17,269 mapped land polygons, 31,480 source rock polygons); AADC candidate points and explicit P/A (7,785 original geographic site records) but original P/A programme-specific selection/missingness must be resolved; MAPPPD v5 strictly eligible 771 nest year transitions at 95 site IDs/11 regions (original NZ 316 duplicated site-year records must NOT be counted independent). Independent BAS/Hart 2019–20 **122,139 penguin nest points** from 10 original species×locality CSVs, at only four localities nested in **three provisional physical islands**, with 30m Copernicus DEM. **These BAS nest points are exclusively penguin taxa** (Adélie, chinstrap, gentoo, macaroni); they CANNOT by themselves serve as a flying-vs-flightless comparison, and full unoccupied potential nesting-area survey polygons are NOT authenticated. Original DEM elevation+slope effect did NOT transfer across all three islands (only 1/3 test); do not sell a universal slope mechanism. A distinct independently co-surveyed flying-seabird nest inventory is needed for the H_F contrast. Antarctic emperor breeding on fast ice is a separate source/habitat stratum and must NOT be forced into rock nesting geometry.

**Why this is a natural experiment and why it is not randomized.**
Antarctic introduced-land-mammal absence removes one class of potential terrestrial selective pressure **by biogeography**, not by randomized predator removal. Regional climate/ice/prey/coloniality/traits are confounded with Falklands/UK, so a direct Antarctic-vs-Britain coefficient cannot identify 'mammals cause X'. Identify contrasting trait/terrain responses *within each region* and then check cross-region direction. For stronger mammal causal inference use source-dated eradication/reintroduction with surveyed detection histories, comparable sites and control islands—not merely two JNCC census epochs.

## Primary outcomes and source-independent analysis units (must exist BEFORE fitting)
1. **Within archipelago occupancy / breeding success** for independently surveyed island × local patch × species × season, accounting for coverage and detection. A Source `P` in a map is NOT a monitored colony or demographic trend.
2. **Functional habitat utilization:** area of *independently surveyed candidate* reachable rock cells (within-island), distinguishing measured occupied from measured unoccupied cells; spatially blocked holdouts by physical island with sites nested, not 122,139 nest points treated as independent islands.
3. **Demographic changes** (when repeated same-method surveys align with island + species): colony change and source component reconfiguration including V37/V46, treated as downstream responses and NOT initial mechanism predictors.
4. **Negative controls:** within-survey species/season with the same observer, verified non-mammalian avian predator/ marine conditions, no invented missing = absence.

## Pre-outcome identifiability and interpretation gates
- H_M needs ≥2 independently surveyed physical island groups with both verified mammal-positive and **survey-confirmed** negative statuses, and enough same-program monitored bird species in two locomotor groups; a large record count does not replace island-level biological replicates.
- H_F needs both penguin and volant seabird verified nest use/available empty habitat under the SAME survey region/year and mapped coastal paths. BAS all-penguin nests alone fail.
- H_X needs H_M and H_F support and at least two *within-region*, source-comparable flight groups; otherwise H_X remains a hypothesis without fitted cross-system interaction.
- Freeze minimum viable sample counts and covariates **only after checking source metadata / denominators**, before opening the future new focal effects. Don't tune shoreline buffers, change guilds or transfer unverified negative labels after effect results.
- No overclaim of actual predator impact in Antarctic/UK, flightlessness evolved due to isolation, biological species extinction/colonization from source metadata editions, or universally valid access corridor penalty.
- A legitimate empirical negative result should close only its tested prediction, not trigger 20 alternative reanalyses.

## Single-manuscript storyline (Paper 2)
**Working title:** *Islands protect and constrain seabird reproduction through asymmetric access by predators and breeders.*

Intro: island size/isolation are incomplete without *whose access* is constrained. Methods: original island × surveillance × nesting-patch × shore-path atlas in two arms. Results 1: mammal-conditioned refuge function inside Falklands. Results 2: flight-conditioned nesting reach function in Antarctic naturally mammal-free system. Results 3: crossed / opposite implications of isolation and steep terrain; domain transfer diagnostics. Discussion: physical isolation is not one-dimensional; external ocean subsidy coupled to finite reachable nesting habitat and risk. Observed source-component switching only in mechanism-verified subset or as background, never substituted for actual access.

**State 2026-10-27: DRAFT HYPOTHESIS, NO NEW ECOLOGICAL EFFECT FIT OR CONFIRMED.** Previous positive concentration/leader results remain independent source facts. This is the canonical new Paper2 central ecological question and does not create/submit another manuscript.
