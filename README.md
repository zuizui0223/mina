# mina

Development repository for the **Palmer Archipelago penguin island-reassembly**
project.

## Biological question

Do neighboring Antarctic breeding islands maintain persistent local penguin
phenotypes, or is archipelago-scale functional differentiation generated mainly
by **species turnover plus temporally labile within-species states**?

This project grew out of the frozen ODSP Palmer Penguins audit. The ODSP result
is retained as provenance, not as the biological endpoint:

- pooled morphology -> island gain: **+0.3895**
- species-identity component: **+0.5360**
- morphology increment after conditioning on species: **-0.0837**

That reversal motivates an ecological decomposition:

1. **between-species sorting / turnover among islands**;
2. **persistent within-species island differentiation**;
3. **island x year reassembly within a species**.

The focal within-species control is Adélie penguins, which occur on Biscoe,
Dream and Torgersen in the Palmer Penguins data.

## Current exploratory result

Using the pinned raw Palmer Penguins data (2007/08--2009/10):

- fixed island effects within Adélie are small for most measured traits;
- island x year structure is stronger for bill depth, body mass and delta15N;
- most pairwise island contrasts reverse sign among years;
- leave-one-year-out island classification is essentially at the three-island
  reference:
  - structural morphology: balanced accuracy **0.342**
  - isotopic niche: balanced accuracy **0.340**
  - reference: **0.333**

The current interpretation is therefore **community/colony reassembly**, not
evolutionary local adaptation or demonstrated individual plasticity.

## Repository layout

- `src/mina/palmer.py` — Adélie-only island x year analysis.
- `src/mina/longterm.py` — APBP/MAPPPD abundance -> island community trait
  trajectories and turnover.
- `contracts/PALMER_ISLAND_REASSEMBLY_V1.json` — hypotheses and scope.
- `results/EXPLORATORY_RESULT_V1.json` — current three-year result receipt.
- `docs/LONGTERM_EXTENSION_V1.md` — long-term island-biogeographic design.
- `scripts/fetch_palmer_raw.py` — fetch the pinned Palmer raw table.
- `scripts/export_mapppdr.R` — export focal APBP/MAPPPD tables.
- `tests/` — synthetic tests that do not depend on network access.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Reproduce the three-year analysis

```bash
python scripts/fetch_palmer_raw.py data/penguins_raw.csv
mina-palmer --raw data/penguins_raw.csv --out build/palmer_result.json
```

Pinned Palmer source:

- repository: `allisonhorst/palmerpenguins`
- commit: `8957207b78d6ccd1b4654a9dd9c9041b657478ab`
- Git blob: `ba99fbd527f0bb983b3d9615ef5c81a5917ab7d9`

## Long-term extension

Export the APBP/MAPPPD focal observations in R:

```bash
Rscript scripts/export_mapppdr.R build/mapppdr
```

Then build the conservative island-year panel:

```bash
mina-longterm \
  --palmer-raw data/penguins_raw.csv \
  --sites build/mapppdr/sites.csv \
  --species build/mapppdr/species.csv \
  --observations build/mapppdr/penguin_obs.csv \
  --out build/longterm.json
```

The default long-term analysis is deliberately strict:

- nests/breeding-pair counts only;
- missing species observations are **not** silently converted to zero;
- an explicit absence may become zero only when the source record says
  `presence = 0`;
- repeated same-site/species/year counts are summarized by their median;
- island-year transitions are marked primary-eligible only when the set of
  contributing APBP sites is unchanged.

## Provenance

The biological project was migrated from
`zuizui0223/odsp` branch `ecology/penguin-island-reassembly-v1`
(draft PR #186). Frozen ODSP N2 evidence remains in ODSP and is not rewritten by
this repository.
