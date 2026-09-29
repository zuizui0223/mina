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

Primary macro trend comparison:
- Adélie
- chinstrap
- gentoo

Gate 0 shows **152 candidate Pygoscelis site × species units** with at least five nest-count years spanning at least 10 years (Adélie 57, chinstrap 46, gentoo 49), and **92** under the stricter ≥10 years / ≥20-year-span gate.

Emperor does **not** provide enough repeated nest-count sites in the pinned APBP snapshot for the same trend analysis (1 candidate unit). It is retained only as a future breeding-substrate contrast that requires a separate frozen demographic source or a different predeclared response such as colony persistence/occupancy.

Macaroni (2 candidate units) and king (0) are excluded from the primary south-of-60 trend lane. A later 50–60°S sub-Antarctic extension must have its own data-coverage and domain contract.

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

### Gate 0 — inventory — PASSED

Pinned MAPPPD inventory:
- **729 sites**
- **918 site × species links**
- **5,487 observations**
- **4,032 nest-count records**
- **1892–2026**
- **155** candidate trend-eligible site × species units
- **94** stricter trend-eligible units
- candidate Pygoscelis total: **152**
- stricter Pygoscelis total: **92**

Result receipt: `results/MAPPPD_MACRO_INVENTORY_RESULT_V1.json`.

No ecological outcome model was fit at Gate 0.

### Gate 1 — breeding-option atlas — PASSED

The primary atlas lane no longer depends on literal island-polygon assignment.
Using the Antarctic Ecosystem Inventory v1.0 at 100 m resolution, mina derives
site-centered breeding-option traits before any demographic outcome is opened.

Frozen primary scale: **2 km** around each candidate breeding site.

Coverage:
- **118 / 122 sites (96.7%)** contain mapped ice-free ecosystem cells at 2 km;
- the same four sites remain uncovered at 1, 2 and 5 km: FRAE, FRAW, GOPT, WPEC;
- these four remain missing by contract rather than being rescued by widening the radius.

At 2 km among the **118 covered candidate sites**:
- mapped ice-free area: **6–928 ha**, median **258 ha**;
- Habitat Complex richness: **1–9**, median **3**;
- ecosystem Shannon diversity: **0–1.86**, median **0.83**.

The four uncovered sites are represented as missing ecological metrics in the
derived table; they are not interpreted as true zero-area or zero-richness sites.

Result receipt:
`results/ANTARCTIC_BREEDING_OPTIONS_ATLAS_GATE1_RESULT_V1.json`.

The atlas is a newly derived mina dataset. It is not occupied nesting area;
it is a site-centered proxy for the quantity and heterogeneity of terrestrial
breeding options.

Literal offshore-island/mainland identity, total landmass area and mainland
distance remain a secondary geometry lane because raw SCAR coastline FIDs are
not themselves biological islands and public FeatureServer throttling made
per-site landmass resolution an unsuitable critical path.

### Gate 1D — terrain and melt augmentation — NEXT

Add terrain and melt/climate traits to the same frozen 122-site set and the
same 2 km primary scale before demographic outcomes are opened.

### Gate 1E — primary predictor set — FROZEN

Before demographic outcomes are opened, Paper 2 now has three co-primary
site-side ecological dimensions at the frozen 2 km scale:

1. **Breeding-space amount** — log1p(mapped ice-free area).
2. **Breeding-option heterogeneity** — Habitat Complex (Tier 2) richness.
3. **Terrain heterogeneity** — log1p(relief p90–p10).

All are standardized within modeling datasets after the frozen transformation.
Tier 2 Shannon diversity is sensitivity-only because it correlates **r = 0.856**
with richness. Elevation SD is sensitivity-only because it correlates
**r = 0.991** with relief. Ice-free area and Habitat Complex richness remain
distinct (**r = 0.164** after the frozen missingness rule is applied).

No additional co-primary static melt, temperature, precipitation, wind or
insolation variables are opened: those abiotic dimensions already contribute
to the AEI Habitat Complex classification. Time-varying environmental forcing
belongs in the demographic model rather than in the frozen site-architecture
trait block.

Contract:
`contracts/PAPER2_OUTCOME_BLIND_PREDICTOR_SET_V1.json`.

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
