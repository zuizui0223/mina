# mina

Development and manuscript repository for the **Palmer Archipelago penguin
island-ecology** study.

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
