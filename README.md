# mina

Research program for **penguin breeding-island ecology**, linking a local
long-term discovery system at Palmer Station to Antarctic-wide comparative
macroecology.

## Research program

### Paper 1 — replicated breeding-space contraction

The current submission line is an **Ecology Report**:

**Breeding-space contraction recurs across declining Adélie and chinstrap penguins**

The paper asks whether declining colonial populations merely thin in fixed
proportion across monitored breeding components, or whether relative breeding
composition changes beyond the finite-count and observation-error consequences
of lower abundance.

Evidence is ordered as:

1. **Palmer Adélie discovery:** three stable-roster island populations;
2. **Signy Adélie prospective geographic replication:** frozen before the
   concentration effect was computed;
3. **Signy chinstrap prospective cross-species replication:** separately frozen
   before effect computation.

Across the five population units, effective monitored breeding-component number
declines by **19–83%**. The two prospectively frozen Signy tests remain extreme
under the most severe prespecified 20% multiplicative-CV sensitivity
(Adélie **p = 0.000010**; chinstrap **p = 0.000020**).

The broad abundance–space principle is not claimed as new. The paper's novelty
is the **within-colony fixed-composition count-error test of excess breeding-
component concentration**, followed by prospective geographic and cross-species
replication.

Canonical submission manifest:
`submission/ECOLOGY_REPORT_SUBMISSION_MANIFEST_V1.md`.

### Paper 2 lane — Antarctic-wide breeding-island macroecology

The next lane asks how breeding-site architecture filters penguin population
fate across Antarctica. APBP/MAPPPD supplies demographic site anchors; mina
will construct a new **Antarctic Penguin Breeding-Island Atlas** from
independent spatial layers (SCAR ADD coastline, Antarctic Ecosystem Inventory,
REMA and related frozen sources).

The conceptual focus is on **externally subsidized breeding islands**:
penguins obtain food primarily from the marine environment while reproduction
is constrained by terrestrial or sea-ice breeding substrate. This lets the
program distinguish regional marine forcing from local breeding-patch
filtering.

The Paper 2 lane has **passed Gate 0**. The pinned MAPPPD snapshot contains
729 sites, 5,487 observations and 4,032 nest-count records. The predeclared
candidate trend gate retains **152 Pygoscelis site × species units** (Adélie
57, chinstrap 46, gentoo 49); a stricter gate retains 92. Emperor, macaroni
and king do not have enough repeated nest-count series for the same primary
trend model.

Gate 1 has now built the first outcome-blind Antarctic Penguin
Breeding-Island Atlas layer. At the frozen 2 km scale, **118/122 candidate
sites (96.7%)** have mapped ice-free ecosystem habitat. The derived traits
span substantial variation (ice-free area 0–928 ha; ecosystem richness 0–9),
so this is now a real user-constructed spatial dataset rather than a plan.

The next stage augments the same frozen sites with terrain and melt/climate
traits. Demographic outcomes remain unopened until the atlas is frozen.

Program documents:
- `contracts/MINA_RESEARCH_PROGRAM_V1.json`
- `docs/ANTARCTIC_BREEDING_ISLAND_MACROECOLOGY_V1.md`

---

## Independent Palmer phenotype reassembly lane

A separate short-paper lane now asks where the conspicuous Palmer
breeding-site phenotype comes from.

The frozen ecological result is hierarchical:

- across the full assemblage, morphology-to-site predictability is dominated by
  species identity;
- within Adélie penguins, fixed island morphology effects are small;
- structural island contrasts repeatedly reverse among years;
- same-year island classification is modestly above chance
  (**balanced accuracy 0.448**), while leave-one-year-out transfer falls almost
  to the three-island chance reference (**0.342** vs **0.333**).

The biological interpretation is therefore **species sorting plus temporal
reassembly**, not a persistent within-species island ecotype.

This lane is independent of frozen Paper 1 and the Antarctic-wide Paper 2
programme. It does not reopen either paper and does not make an ODSP methods
claim.

Canonical files:

- `contracts/PALMER_PHENOTYPE_REASSEMBLY_PAPER_V1.json`
- `results/PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json`
- `docs/PALMER_PHENOTYPE_REASSEMBLY_MANUSCRIPT_SPINE_V1.md`

---

## Current ecological claim

For a spatially structured breeding population, total abundance and relative
spatial composition are distinct state descriptions.

The null model uses each observed annual population total as the **latent
expected annual total**, fixes one time-invariant vector of breeding-component
shares, and then simulates counts under the frozen Poisson / Gamma–Poisson
observation-error family. It therefore includes both the finite-count tendency
for small components to disappear as abundance declines and independent count
noise.

The observed decline in effective breeding-component number is more negative
than that null in all five studied population units:

- Palmer Cormorant Adélie: **3.54 → 2.86** (**−19%**), CV20 p = **0.038**;
- Palmer Humble Adélie: **4.62 → 2.28** (**−51%**), CV20 p = **0.000010**;
- Palmer Litchfield Adélie: **5.78 → 1.00** (**−83%**), CV20 p = **0.000010**;
- Signy Adélie: **3.08 → 1.94** (**−37%**), CV20 p = **0.000010**;
- Signy chinstrap: **4.44 → 2.19** (**−51%**), CV20 p = **0.000020**.

Palmer is explicitly the **discovery system**. Its public colony codes are
treated as monitored census components, not verified fixed GIS polygons. The
confirmatory weight rests on the two prospectively frozen Signy tests.

The endpoint is inverse-Simpson effective component number, a Hill-number
measure of relative concentration. It can fall while every monitored component
remains occupied. It is therefore **not** occupied-site richness, physical
breeding area, genetic effective population size (Ne), or genetic effective
number of breeders (Nb).

The closest general literature includes positive abundance–occupancy
relationships, geographic range contraction, and marine-fish
proportional-density versus basin models. Accordingly, mina does **not** claim
that abundance and spatial extent are newly separable. The transferable result
is narrower: a discrete breeding-component composition can depart systematically
from proportional thinning, and that departure can be tested conditional on
the observed abundance trajectory.

## Ecological framing

mina treats penguin breeding islands as **externally subsidized breeding
patches**. Food resources are primarily marine; breeding surfaces are discrete
and terrestrial. Regional marine processes can therefore impose a shared
demographic direction while local snow, geomorphology, colony history and
remaining nest-space organization shape vulnerability.

Direct biotic interactions are not assumed absent. They are treated as
localized and testable rather than as the default explanation for whole-island
trajectories.

## Submission status

The canonical submission is **Ecology Report v0.5**.

Current package:

- manuscript: `submission/MANUSCRIPT_ECOLOGY_REPORT_V0_5.md`
- cover letter: `submission/COVER_LETTER_ECOLOGY_REPORT_V3.md`
- main captions: `submission/FIGURE_CAPTIONS_ECOLOGY_REPORT_V0_4.md`
- supplementary caption: `submission/SUPPLEMENT_ECOLOGY_REPORT_V0_4.md`
- copy fields: `submission/ECOLOGY_SUBMISSION_COPY_FIELDS_V2.md`
- readiness audit: `submission/SUBMISSION_READINESS_ECOLOGY_REPORT_V3.md`
- reviewer stress test:
  `submission/PRE_SUBMISSION_REVIEWER_STRESS_TEST_ECOLOGY_V1.md`
- scientific freeze: `contracts/ECOLOGY_REPORT_SUBMISSION_V3.json`

The old Ecosphere, JBI and integrated manuscripts are **provenance only** and
must not be treated as parallel submissions. The integrated JBI line is formally
superseded.

## Development state

The Ecology Report scientific content is **frozen**. Before initial submission,
do not add:

- new ecological endpoints;
- alternative concentration metrics;
- tuned thresholds or time windows;
- additional error models selected after outcome inspection;
- extra species as post-result rescue analyses;
- new mechanism claims.

Allowed work is limited to reference completion, copyediting, journal
formatting, author metadata, archival metadata, figure QA, and clarification
from the Palmer data providers about colony-code continuity.

The remaining submission blockers are author-controlled metadata: author order,
affiliations, corresponding author, funding/acknowledgments, CRediT roles,
conflict-of-interest statement, complete AI-tool inventory, overlap statement,
and ORCIDs if requested.

## Reproduce

Install:

```bash
python -m pip install -e ".[dev,figures]"
```

Fetch the frozen census:

```bash
python scripts/fetch_lter_census.py build/adelie_census.csv
```

Primary analyses:

```bash
mina-lter --census build/adelie_census.csv --out build/lter.json
mina-colony-network --census build/adelie_census.csv --out build/colony.json
mina-hierarchical-variability --census build/adelie_census.csv --out build/hierarchy.json
mina-neff-momentum --census build/adelie_census.csv --out build/neff_momentum.json
```

The manuscript figure workflow additionally exports pinned APBP/MAPPPD site
metadata and regenerates Figure 1–5 data before rendering PNG and PDF outputs.

## Provenance

The project began as a biological follow-up to the frozen ODSP Palmer Penguins
audit. ODSP remains the methodological provenance source; all current biological
development and manuscript work belongs in `mina`.
