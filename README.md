# mina

Research program for **penguin breeding-island ecology**, linking a local
long-term discovery system at Palmer Station to Antarctic-wide comparative
macroecology.

## Research program

### Paper 1 / v1 — Palmer discovery system

Paper 1 is scientifically frozen at **v1**. Its manuscript implementation is
the concentration-led Ecosphere v0.8 package. The central result is that
regional Adélie decline was accompanied by progressive within-island
concentration of breeders beyond proportional thinning and the frozen
independent count-error family.

Canonical manifest: `docs/PAPER1_V1.md`.

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

Five neighboring Adélie penguin island populations share an exceptionally
strong long-term decline, but the decline also has an **internal spatial-demographic
architecture**.

Across the complete 1991–2017 five-island Palmer LTER panel:

- PC1 explains **96.4%** of standardized log-abundance variation;
- median pairwise annual-growth correlation is **0.373**;
- year uniquely accounts for **53.5%** of total log-abundance variance;
- island identity accounts for **33.0%**;
- Litchfield reaches local extinction while neighboring islands persist at
  low abundance through 2017.

The strongest new ecological result is within islands. In the three islands
with unchanged colony-code rosters, effective colony number declines
progressively during population loss:

- Cormorant: **3.54 → 2.86** (**−19.1%**), slope **−0.0310 yr⁻¹**;
- Humble: **4.62 → 2.28** (**−50.6%**), slope **−0.0855 yr⁻¹**;
- Litchfield: **5.78 → 1.00** by its final positive census in 2006
  (**−82.7%**), slope **−0.3681 yr⁻¹**.

A fixed-composition null retains the exact observed island-total trajectory and
adds independent Poisson, Gamma–Poisson CV10%, or Gamma–Poisson CV20% count
error. Even under the severe uncalibrated CV20% sensitivity, the observed
concentration slopes remain unusual (Cormorant **p = 0.0380**; Humble and
Litchfield **p = 0.000010** each), and zero of 100,000 simulations reproduce
slopes simultaneously as negative on all three islands (plus-one joint
**p = 0.000010**). The decline is therefore not adequately described as
simple proportional thinning of a fixed breeding distribution plus independent
count noise: breeders become concentrated among a smaller effective set of
colony-code breeding components.

Effective colony number also remains positively associated with next-year
growth after island, current abundance, secular time and the preceding two
growth intervals are controlled (**+0.1126**; structured-null p = **0.00102**,
exact joint p = **0.0120**). Its incremental held-out MSE gain is only
**+0.000444**, so it is retained as a weak conditional state association, not a
supported predictor, mechanism, or early-warning indicator.

Independent Torgersen mapping documents physical contraction from **23**
historic active subcolonies to **five** active footprints by 2022 and
habitat-structured extinction. This is phenomenon-level spatial convergence,
not colony-ID-level validation: public LTER colony codes have not been
crosswalked one-to-one to the GIS polygons.

The Wang–Loreau beta hierarchy remains secondary context. Observed raw beta is
**1.0737** from colony-code components to islands and **1.0112** from islands
to the aggregate, but an uncalibrated CV20% fully synchronous count-error null
can reproduce that difference. It is therefore not used as proof of biological
spatial insurance.

## Ecological framing

mina treats penguin breeding islands as **externally subsidized breeding
patches**. Food resources are primarily marine; breeding surfaces are discrete
and terrestrial. Regional marine processes can therefore impose a shared
demographic direction while local snow, geomorphology, colony history and
remaining nest-space organization shape vulnerability.

Direct biotic interactions are not assumed absent. They are treated as
localized and testable rather than as the default explanation for whole-island
trajectories.

## Submission status after breeding-concentration analysis

The current scientific draft is **Ecosphere-oriented v0.8**. The central
positive result is progressive within-island concentration during Adélie
decline. The v0.7 measurement-error audit remains important because it prevents
the observed beta hierarchy from being overinterpreted as biological
buffering.

The scientific claim stack is now:

1. shared regional decline with divergent island fate;
2. progressive concentration of breeders among a smaller effective set of
   colony-code components, robust to the full frozen count-error family;
3. a separate weak N_eff–next-year-growth conditional association;
4. independent Torgersen spatial contraction as phenomenon-level
   triangulation;
5. a measurement-sensitive beta hierarchy retained only as context.

Submission metadata remain author-controlled. v0.7 and earlier manuscripts are
provenance only.

## Development state

Core same-census endpoint development is **closed at v0.8**. The terminal rule
forbids alternate concentration indices, intermediate count-error CV values,
tuned time windows, colony-roster reconciliation, transformed rescue
endpoints, additional topology metrics, or new same-census climate searches.

New biological interpretation must come from external evidence:

- colony-code / GIS-polygon crosswalks;
- replicate-observer count-error calibration;
- direct habitat attributes of retained and lost breeding components;
- independent replication in another monitored Adélie system.

See:

- `docs/MANUSCRIPT_ECOSPHERE_V0_8.md`
- `docs/MANUSCRIPT_SPINE_V7.md`
- `docs/FIGURE_CAPTIONS_V7.md`
- `docs/REFERENCES_V6.bib`
- `results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json`
- `results/PALMER_NEFF_DEMOGRAPHIC_MOMENTUM_RESULT_V1.json`
- `results/PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json`
- `docs/MANUSCRIPT_ECOSPHERE_V0_7.md` (provenance)

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
