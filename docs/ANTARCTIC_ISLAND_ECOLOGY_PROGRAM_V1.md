# Antarctic island ecology program v1

**Status:** forward research program built on the closed cross-scale concentration paper.  
**Branch:** `research/antarctic-island-ecology-v1`  
**Rule:** this document does not reopen or modify the frozen Paper 1 inferential endpoints.


## Paper 3 empirical status — 2026-10-04

The mobile-node lane is now empirically supported.

### Long-term interannual node identity

Using source-provided season reference locations for Astrid, Mertz and SANAE across 2014/15–2023/24:

- 30 annual colony anchors;
- 27 consecutive-season transitions;
- fixed-node false-turnover fraction = 96.3% at 0.5 km, 88.9% at 1 km, 59.3% at 2 km, 29.6% at 5 km and 14.8% at 10 km;
- median consecutive displacement = 2.30 km;
- q95 = 14.52 km.

### Independent within-season validation

A separate 2024 six-colony SAR dataset gives:

- 596 mapped huddles;
- 48 post-anchor colony-dates;
- false absence = 2.1% at 0.5 km and 0% at 1 km or larger;
- within-season minimum-group-distance q95 = 0.389 km.

The two datasets are independent and should not be treated as a paired timescale experiment. Together they establish a bounded but striking state distinction:

> **geographic site identity can be stable within a breeding season while failing as a persistent identifier across breeding seasons.**

Paper 3 therefore adds a third Antarctic island-ecology axis to the program:

1. Paper 1 — breeder allocation contracts within persistent nodes;
2. Paper 2 — changing capacity of persistent nodes does not generally predict relative use;
3. Paper 3 — the occupied node itself can relocate while source-provided colony identity persists.

The strongest synthesis is that **population identity, geographic node identity and breeder allocation are distinct ecological state variables**.

## Program question

> **How do island populations lose, gain, and relocate breeding space when the matrix that separates breeding sites is also the habitat that feeds them?**

The Antarctic system should not be described loosely as “one giant island.” The stronger formulation is a **nested island system**:

1. geographic islands and coastal headlands;
2. ice-free terrestrial habitat islands within an ice/snow matrix;
3. discrete breeding colonies or census components within those habitat islands;
4. regional networks of breeding sites embedded in a marine matrix;
5. for emperor penguins, seasonally created fast-ice breeding platforms whose positions and even existence can change.

This hierarchy lets the program ask island-ecology questions without pretending that all Antarctic breeding sites are literal islands or closed populations.

## Why penguins are unusually useful for island ecology

### 1. The matrix is both barrier and resource

Classical island models usually treat the matrix primarily as a dispersal barrier. Breeding penguins invert that logic.

- reproduction is spatially tied to discrete land or fast-ice breeding sites;
- food is obtained in the surrounding ocean;
- breeding birds therefore function as central-place foragers;
- distance through the marine matrix can increase movement cost while the same matrix supplies the prey needed to sustain the colony.

This makes **geographic isolation** and **functional isolation** separable quantities.

Santora, LaRue & Ainley (2020; *Global Ecology and Biogeography*, doi:10.1111/geb.13144) already showed that present-day penguin colony geography is related to colony neighbourhoods, foraging range, polynyas and submarine canyons. The new program therefore should not repeat a static “island area + marine environment -> colony size” analysis. Its niche is **dynamic spatial response**.

### 2. The amount of terrestrial breeding opportunity is itself changing

Antarctic ice-free land covers a tiny fraction of the continent and is naturally fragmented into habitat islands. Climate-driven deglaciation can expand and connect these patches.

- Lee et al. (2017; *Nature*, doi:10.1038/nature22996) projected strong expansion of ice-free habitat, especially on the Antarctic Peninsula.
- Hughes et al. (2022; *Global Change Biology*, “Islands in the ice”) formalized the distinction between structural and functional connectivity in expanding Antarctic ice-free habitat.
- LaRue et al. (2013; *PLoS ONE*, doi:10.1371/journal.pone.0060548) showed a concrete penguin case at Beaufort Island: glacier retreat increased nesting habitat, Adélie abundance increased, and emigration within the Ross Sea metapopulation changed.

Thus Antarctica contains a rare natural experiment in which **physical island opportunity may expand while populations elsewhere decline**.

### 3. Breeding substrate permanence differs radically among penguins

Land-breeding *Pygoscelis* occupy geographically persistent nodes. Emperor penguins can breed on fast ice, ice shelves, icebergs, or occasionally land, and entire breeding sites can relocate.

Recent work makes this contrast especially timely:

- Fretwell et al. (2026; *Communications Biology*, doi:10.1038/s42003-026-10961-y) documented five emperor colony locations that moved substantially over the preceding decade.
- Macdonald et al. (2026; *Communications Earth & Environment*, doi:10.1038/s43247-026-03906-0) mapped year-round movement for three emperor colonies and released colony-tracking shapefiles.
- Long-term satellite reconstructions (1984–2024) show relocation after calving and repeated use of fast ice, ice shelves and icebergs at Astrid, Mertz and SANAE.

This creates a second island-ecology axis: **persistent breeding islands versus ephemeral/mobile breeding islands**.

### 4. Penguins export the marine ecosystem onto land

Penguin colonies are not only populations occupying islands; they are vectors of marine-derived nutrients into extremely nutrient-poor terrestrial systems.

A continent-wide 10 m vegetation baseline (Walshaw et al. 2024; *Nature Geoscience*, doi:10.1038/s41561-024-01492-4) found that roughly 40% of mapped green vegetation and lichens in ice-free areas occurred within 5 km of Antarctic Important Bird Areas. Ancient colony guano can continue supporting moss systems long after penguins move away.

This means breeding-space reorganization can, in principle, reorganize **ecosystem subsidy topology** as well.

---

# Paper sequence

## Paper 1 — already closed: how decline occupies space

### Question
When a penguin population declines, is breeding activity proportionally thinned across existing components, or does effective breeding space contract faster than abundance alone requires?

### Existing answer
Across Palmer and Signy, declining *Pygoscelis* populations repeatedly concentrate breeding into fewer effective monitored components beyond proportional thinning. The MAPPPD extension gives bounded cross-scale directional recurrence.

### Island-ecology interpretation
Paper 1 identifies a **spatial form of population decline**. It does not yet identify whether contraction is caused by terrestrial breeding opportunity, marine opportunity, dispersal, social organization, or other processes.

### Claim boundary
Do not retitle Paper 1 as a general “island rule.” It remains a penguin result with island-ecology implications.

---

# Paper 2 — highest priority: when habitat islands grow while breeding space shrinks

## Working question

> **Does newly exposed terrestrial breeding opportunity prevent breeding-space contraction, or can effective breeding space shrink while ice-free habitat expands?**

This is the cleanest next step because it directly connects the Paper 1 state variable to a distinctive Antarctic process.

## Competing hypotheses

### H2-LAND — terrestrial opportunity limitation
If usable nesting land limits population organization, deglaciation should release that constraint.

Predictions:
- increasing accessible ice-free land -> increasing or more slowly declining abundance;
- increasing accessible ice-free land -> increasing or more slowly declining effective breeding-space representation;
- sites with little new terrestrial opportunity should contract faster, all else equal.

Beaufort Island is a known positive example and therefore must be treated as prior evidence, not as an independent discovery.

### H2-MARINE — marine limitation / land-space decoupling
If breeding decline is driven mainly by the marine side of the life cycle, land opportunity can expand without preventing spatial contraction.

Critical prediction:

[
\Delta A_{icefree} > 0
quad\text{while}\quad
\Delta E_{breeding} < 0
]

after accounting for abundance thinning.

This is the high-value Antarctic result: **physical island area can grow while biological use of breeding space contracts**.

### H2-COUPLED — dual-domain limitation
Terrestrial opportunity should matter only when the surrounding marine matrix remains functionally favourable.

Conceptually:

[
breeding\ space =
f(land\ opportunity, marine\ opportunity, land\times marine)
]

The interaction, rather than either domain alone, is the genuinely penguin-specific prediction.

## Why this is not Santora et al. 2020 again

Santora et al. addressed present-day geographic structure using breeding habitat, colony neighbourhoods, polynyas and submarine canyons.

Paper 2 must instead test **change against change**:

- change in terrestrial opportunity;
- change in abundance / effective breeding space;
- change in marine accessibility or resource conditions.

The target is a longitudinal decoupling or coupling process, not a static geographic correlation.

## Candidate data

### Penguin response
- MAPPPD v4.4: four species; public records now extend through the 2024/2025 breeding season.
- Existing pinned MAPPPD cohort and observation-calibration machinery in `mina`.
- Palmer/Signy remain useful for local validation, but should not be allowed to determine the Antarctic-wide outcome rule.

### Terrestrial opportunity
- Landsat archive for historical rock/ice classification.
- Sentinel-2 for modern validation.
- SCAR Antarctic Digital Database (ADD) 2026 rock-outcrop/coastline layers for geometry and QA.
- REMA for elevation/slope constraints.

**Important:** sequential ADD releases are not a clean annual time series because features are compiled from sources of different dates. They should not be differenced naively to infer habitat change. Dynamic exposure must come from imagery or a source with explicit observation dates.

### Marine domain
Candidate covariates for an outcome-blind audit:
- fast/pack sea-ice duration or concentration;
- distance/access cost to open water during breeding;
- persistent polynyas;
- bathymetry / shelf break / submarine canyons;
- remotely sensed productivity where temporal coverage is adequate.

The program should prefer a small biologically motivated marine set over another large environmental fishing exercise.

## First implementation gate

**Do not fit ecological outcome models yet.**

First build an outcome-blind support table for every candidate colony/site:

| field | purpose |
|---|---|
| site_id / species | unit identity |
| count years and methods | demographic support |
| earliest usable Landsat epoch | terrestrial-change support |
| latest usable Landsat/Sentinel epoch | terrestrial-change support |
| cloud/shadow coverage | image quality |
| coastline / rock classification confidence | habitat QA |
| topographic accessibility support | nesting-opportunity QA |
| marine covariate completeness | land-sea coupling support |
| eligible / reason excluded | deterministic gate |

Only after this table is frozen should any relationship with population trend or effective breeding-space change be opened.

## Key methodological risk

“More ice-free land” is not automatically “more penguin nesting habitat.”

The habitat metric must exclude or down-weight:
- cliffs / inaccessible slopes;
- terrain too far from practical sea access;
- lakes / wet ground where identifiable;
- newly exposed substrate not yet physically suitable for nests.

Therefore the primary variable should be **accessible ice-free breeding opportunity**, not raw rock area.

---

# Paper 3 — dynamic islands: stay, contract, or move?

## Working question

> **Does breeding-substrate permanence determine the spatial mode by which penguin populations respond to environmental deterioration?**

### Fixed-node response
For land-breeding *Pygoscelis*, the current evidence suggests:
- the node remains geographically available;
- breeding allocation contracts within or among persistent terrestrial units.

### Mobile-node response
For emperor penguins:
- the breeding platform can disappear, advect, fracture or relocate;
- whole colonies can shift tens of kilometres after local sea-ice or ice-shelf change;
- breeding on ice shelves or icebergs can substitute for fast ice in some years.

### General hypothesis
Environmental deterioration has at least two spatial response modes:

1. **stay-and-contract** — persistent habitat nodes, declining use;
2. **move-and-reassemble** — transient habitat nodes, colony relocation/splitting.

The new object of comparison is not raw population trend. It is the **mode of spatial response conditioned on substrate permanence**.

## Immediate feasibility advantage
Macdonald et al. (2026) provide open shapefiles for year-round colony tracking at Atka Bay, Coulman Island and Cape Washington (UK Polar Data Centre doi:10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9).

## Caution
A direct causal comparison between emperor and *Pygoscelis* is confounded by many species differences. The first analysis should therefore establish a common spatial-response vocabulary and quantify movement/contraction modes, not claim that substrate type alone causes the species contrast.

---

# Paper 4 — from population contraction to island ecosystem memory

## Working question

> **When penguin breeding space contracts, does the active marine-subsidy network contract faster than the terrestrial ecological footprint it created?**

## State variables
- active breeding footprint / active colony distribution;
- estimated current marine-derived nutrient source footprint;
- terrestrial vegetation / soil legacy around current and abandoned colonies.

## Hypothesis
Breeding activity can change quickly, whereas nutrient-enriched soils and vegetation respond slowly.

Therefore:

[
active\ penguin\ footprint\downarrow
]

can coexist with

[
legacy\ terrestrial\ footprint\approx persistent
]

creating **ecological memory after demographic spatial collapse**.

## Why this is island ecology
This links marine subsidy theory to the spatial organization of the consumer that transports the subsidy. It asks not simply whether seabirds enrich islands, which is established, but whether **population-space contraction changes the number and arrangement of subsidy entry points**.

## Feasibility
- continent-wide 10 m vegetation baseline is public (Walshaw et al. 2024);
- MAPPPD colony locations/counts are public;
- historical/abandoned penguin colonies exist in palaeoecological records;
- dynamic inference will require stronger temporal data than the current vegetation baseline, so this is not the immediate next empirical paper.

---

# A unifying Antarctic island model

The program can be summarized with two coupled domains.

For terrestrial or fixed-node breeders:

[
B_t = f(A_t, M_t, C_t, S_t)
]

where:

- (B_t) = realized breeding-space state;
- (A_t) = accessible terrestrial breeding opportunity;
- (M_t) = marine foraging opportunity;
- (C_t) = functional connectivity among breeding sites;
- (S_t) = social/spatial memory such as site fidelity and established colony structure.

For mobile fast-ice breeders, breeding-node position itself becomes a state variable:

[
L_{t+1} = g(L_t, I_t, M_t, S_t)
]

where (I_t) describes substrate stability.

The conceptual advance is that **island area, isolation and matrix quality are not fixed covariates**. In Antarctica they can all change, and the organisms can sometimes respond by contracting within a node and sometimes by moving the node itself.

---

# What would count as a genuinely surprising result?

The strongest outcomes are not “environment matters” or “larger habitat supports more penguins.”

High-value results would be:

1. **Habitat expansion without biological spatial expansion**  
   Ice-free breeding opportunity increases while effective breeding space contracts.

2. **Functional isolation beats geographic isolation**  
   Colony turnover/relocation is better explained by dynamic access through the marine/ice matrix than by straight-line distance.

3. **Different response modes to node permanence**  
   Persistent land nodes show concentration; ephemeral fast-ice nodes show relocation/reassembly.

4. **Demographic collapse precedes ecosystem collapse**  
   Active nutrient-source space contracts while terrestrial subsidy legacies remain.

These are all more distinctively Antarctic than another static area–abundance regression.

---

# Immediate next action

The next computational task should be **Paper 2 feasibility audit only**:

1. enumerate MAPPPD sites with sufficiently long demographic histories;
2. locate repeatable historical and modern optical imagery around those sites;
3. quantify whether accessible ice-free land change is estimable without looking at population outcomes;
4. audit marine-covariate completeness;
5. freeze the eligible roster and habitat metric;
6. only then open the land-opportunity × breeding-space relationship.

If this gate fails, the program should move to Paper 3, because the emperor colony movement shapefiles already provide a cleaner public dynamic-habitat dataset.

## Stop rule

Do not reopen the 66-endpoint search, retune the Paper 1 concentration endpoint, or add post-hoc island predictors to the closed Paper 1 submission. New island-ecology claims require new data support or a separately frozen extension.
