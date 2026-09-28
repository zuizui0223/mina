# Antarctic-wide development inside mina — v1

## Why this stays in mina

Paper 1 discovered a local process: a shared regional Adélie decline was accompanied by non-proportional reorganization of breeders within Palmer breeding islands.

The next question is not another Palmer sensitivity analysis. It is whether **breeding-site architecture determines how regional change is realized locally across Antarctic penguins**.

mina therefore becomes a research program rather than a single-manuscript repository.

## Conceptual model

Penguins are useful island organisms because the principal trophic resource field is marine while reproduction is constrained to discrete breeding substrates.

```
regional marine forcing
        |
        v
species-specific exposure
        |
        v
breeding-site filter
  - island / coast / sea ice
  - usable ice-free area
  - relief / snow / melt
  - habitat heterogeneity
  - isolation / geometry
        |
        v
local demographic fate
  persistence | decline | extinction | colonization | replacement
```

This differs from a classical resource-area interpretation of islands. A larger breeding island does not necessarily contain more food; instead it can contain more **breeding options**.

## Paper 1 → Paper 2 logic

### Paper 1 / v1: local discovery

Palmer:
- common long-term decline;
- different island endpoints;
- within-island breeder concentration beyond proportional thinning and count error;
- N_eff as a weak conditional demographic-state descriptor;
- physical mechanism unresolved.

### Paper 2: Antarctic-wide macroecology

Test whether local breeding-site architecture explains population fate after broad regional structure is accounted for.

The important novelty is not re-running MAPPPD. It is constructing a new **Antarctic Penguin Breeding-Island Atlas** and linking it to harmonized demographic trajectories.

## Dataset layers

### Layer A — demographic anchors

APBP/MAPPPD:
- `site_id`
- `species_id`
- coordinates
- region / CCAMLR subarea
- historical counts, presence/absence, accuracy and vantage metadata

The pilot inventory is pinned to mapppdr commit `88c73a507e0921b2541c218c71eaf16721bc6502`.

### Layer B — land / island geometry

SCAR Antarctic Digital Database high-resolution coastline polygons, version 7.12.

Derive rather than hand-label:
- whether a site intersects an offshore land polygon versus continental/peninsular land;
- polygon area;
- distance to mainland/nearest larger polygon;
- coastline complexity;
- local rock/ice geometry.

### Layer C — terrestrial breeding environment

Antarctic Ecosystem Inventory v1.0:
- Major Environment Unit;
- Habitat Complex;
- Bioregional Ecosystem Type;
- terrain, processed climate and melt covariates at continental scale.

### Layer D — terrain

REMA:
- elevation;
- relief;
- slope;
- ruggedness;
- aspect/exposure summaries.

Use coarser mosaics for continental-scale extraction unless a finer scale is justified before outcomes are opened.

## Species comparison

Primary macro comparison:
- Adélie
- chinstrap
- gentoo
- emperor

Adélie/chinstrap/gentoo provide terrestrial-breeding contrasts. Emperor provides a breeding-substrate contrast because many colonies depend on sea ice rather than terrestrial island geometry.

Macaroni and king remain secondary until the inventory demonstrates enough site/time replication south of 60°S. A later 50–60°S extension can add sub-Antarctic islands under a separate domain contract.

## Highest-value tests

1. **Habitat-option test**  
   Does ice-free breeding-habitat amount/heterogeneity predict persistence after regional trend is controlled?

2. **Island architecture test**  
   Is local fate better explained by breeding-site geometry than by simple island area?

3. **Species × substrate test**  
   Are terrestrial geometry effects stronger for terrestrial breeders than emperor penguins?

4. **Endpoint test**  
   Do similar regional declines produce vacancy, persistence or heterospecific replacement depending on breeding-site architecture?

5. **Palmer generalization test**  
   Are declining colonies in low-option sites more likely to collapse into fewer remaining breeding sites/components?

## Stage gates

### Gate 0 — inventory

Count real APBP coverage:
- sites;
- species;
- observation years;
- nest-count records;
- sites with ≥2/5/10/20 years;
- temporal span ≥10/20/30 years;
- site-species units satisfying candidate trend criteria.

No ecological model is fit at Gate 0.

### Gate 1 — atlas feasibility

Freeze:
- study domain;
- site type;
- island polygon matching;
- buffers;
- trait list;
- missingness thresholds.

Build traits without opening demographic responses.

### Gate 2 — outcome contract

Only after the atlas is frozen, define:
- trend;
- persistence/extinction;
- colonization;
- replacement;
- minimum temporal coverage;
- observation-method sensitivity.

### Gate 3 — macro analysis

Fit spatial/hierarchical models with region and species structure and compare the predeclared island-architecture hypotheses.

## Boundary

Do not call the current Palmer Paper 1 a macroecological paper. It is the local discovery system that motivates the Antarctic-wide comparison.
