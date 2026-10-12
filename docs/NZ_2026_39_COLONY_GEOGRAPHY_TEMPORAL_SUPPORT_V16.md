# V16 — The 2024 "39-colony" dataset has no contemporaneous off–Ross-Island comparison

**2026-10-10, mina PR193. Actual 2026 NZ source-file audit.** The source and geometry originate with Anderson, Meredyth-Young & Robinson 2026, [doi:10.7931/kf06-x745](https://doi.org/10.7931/kf06-x745), licence CC-BY-NC 4.0. Original census XLSX publisher MD5 = `195a9027a0d18012812b09fb345ac60e`, verified in [source workflow #38014975839](https://github.com/zuizui0223/mina/actions/runs/38014975839) and in [geography-year audit #38036057389](https://github.com/zuizui0223/mina/actions/runs/38036057389). Supplementary site-location XLSX is official CKAN resource `f82c5e1d-f04d-446d-9338-e9d0603360f8`: **the publisher metadata has NO MD5** for this supplementary file; we used HTTPS official resource URL and recorded its retrieved SHA256, not falsely claiming author-checksum identity.

## A stricter answer to the focal new-cause question

The full XLSX includes **39 named breeding-census site rows** and year columns 1981–2024. However, the counts available in the four source *actual* calendar-year cross-sections are:

| Census season year | Sites with actual numeric source breeding-pair counts | Outside Ross Island? |
|---|---:|---|
| 1999 | **6** | **No**; Cape Bird M/N/S, Crozier E/W, Royds |
| 2001 | **14** | **Yes**; e.g. Cape Hallett, Coulman, Franklin, Foyn, Terra Nova Bay |
| 2005 | **18** | **Yes**; e.g. Beaufort, Balleny, Inexpressible, Terra Nova Bay |
| 2024 | **6** | **No**; exactly the same six Ross Island survey units as 1999 |

Thus **the 1999-to-2024 six-site contrast represents spatial subunits of ONE ISLAND**. It cannot by itself test an inter-island causal recolonization theory or replicate a Ross-versus-other-islands 2024 recovery treatment. The 39-site count does NOT mean 39 complete annual time series, 39 separate islands or 39 long-term independent 1999→2024 replicates. The complete table has **522 positive numeric counts, 2 source-encoded zeros and 1192 missing site-year cells** out of 1716. A 2024 outgroup cannot be imputed from prior years.

Prior source [Dugger et al. 2026](https://doi.org/10.3389/fevo.2026.1868960) already reports lowest Royds recruitment among Royds/Bird/Crozier, with estimated first-two-year chick survival ~0.43 Royds and Crozier versus ~0.55 Bird and hypothetical-cohort recruited by age 14 ~9.8% Royds, ~19.6% Bird, ~13.6% Crozier. Thus Royds-specific slow growth is already discussed with actual individual vital-rate contrasts, although the mechanisms behind each vital-rate difference remain open. This retrospective comparison does **not** newly discover low recruitment or establish that a cohort's chicks immigrated to another colony. Bird/Crozier/Royds are three colony complexes within the same Ross Island; Beaufort Island is genuinely another island but its 2024 census is absent in this release.

## Official geography crosswalk is not fully one-to-one

The source location supplement has **40** named site rows, each with name / parent regional descriptor / approximate latitude and longitude (DMS strings, typically degrees+minutes), versus **39** named census series.

- **33/39** census site names match a literal normalized location-site name.
- Six **census-only** names: `Aviation Islands`, `Beaufort Island New`, `Foyn Island`, `Terra Nova Bay`, `Thala Island`, `Wood Bay`.
- Seven **location-only** names: `Beaufort Island North`, `Conical Island`, `Dome Island`, `Edmonson Point`, `Northern Foothills`, `Southwest Island`, `Svwend Foyn Island`.
- Ambiguous pairs *may* include changed aliases, grouping or misspellings, but **NO fuzzy or nearest-coordinate matches have been accepted**. Foyn vs Svwend Foyn, for example, cannot automatically be treated as a proven identical physical sampling unit.
- In the 33 matched site rows, **four pairs of different labels share identical approximate rounded latitude/longitude**: Cape Cornish / Cape Davis, Cape Symthe / SE Promontory, Chinstrap Island / Sabrina Island, and Franklin Island East / Franklin Island West. Coordinates rounded to the minute are **site locators**, not the GPS geometry of colony patches, individual bird positions, true zero separation or interchange.

The matched local source geographic descriptor groups comprise Adare Peninsula (2 site rows), Balleny Islands (6), Coulman Island (4), Daniell Peninsula (3), Hallett Peninsula (3), Pennell Coast (4), Possession Island (1), Ross Island (6), Southern Ross Sea (3), Wood/Terra Nova bays (1). **A parent descriptor is NOT always a single physical island**: an archipelago, peninsula, coastline or sea region cannot silently count as an independent island replicate. Location source crosswalk is presently `PARTIAL_LITERAL_SOURCE_NAME_CROSSWALK_NO_GUESSED_SYNONYMS`, not a verified 39/39 join.

## How this stops a false "new Antarctic island ecological law"

A statistically flashy regression explaining 1999→2024 change as a function of island distance or historical nesting might seem possible using 39 site rows; **it is structurally impossible** because 2024 has counts at only the six Ross Island units. Even an all-39 missing-data model would extrapolate modern off-island response without a contemporaneous observation, and would not identify island-specific settlement. Original NZ 2026 monitoring data may be the same underlying bird counts reused in earlier Ross papers; a **new archive** is not automatically a new biologically independent survey.

2001 and 2005 supply off-Ross observations and may support a **shorter-window descriptive geographic comparison**, but no independently measured pre-iceberg 1999 baseline exists beyond Ross in this resource, so a non-Ross causal difference-in-differences estimate of the 2001 iceberg event is unsupported. Evidence for physical access, source populations, marked arrivals, parental egg/chick outcomes or nest-substrate legacy is also not in these aerial breeding-pair counts.

Actual scripts/CI:
- [2016-era-independent main source and missingness gate](https://github.com/zuizui0223/mina/actions/runs/38014975839)
- [V14 exact six-site longitudinal count panel](https://github.com/zuizui0223/mina/actions/runs/38015280933)
- [V15 publisher location-source layout](https://github.com/zuizui0223/mina/actions/runs/38035757744)
- [V16 exact 33/39 source site geography crosswalk](https://github.com/zuizui0223/mina/actions/runs/38036057389)
- `contracts/ROSS_NZ_COLONY_GEO_CROSSWALK_AND_PARENT_UNIT_V16.json`
- `scripts/audit_nz_2026_ross_geographic_parent_support_v16.py`
- `tests/test_nz_2026_ross_geographic_parent_support_v16.py`
- `.github/workflows/nz-ross-39-site-geography-crosswalk-v16.yml`

**Scientific decision: HOLD INTER-ISLAND 2024 COUNTERFACTUAL.** The 1999→2024 Royds disadvantage is directly observed and reproducible but already consistent with published Ross demographic differences. Future discovery requires independent cross-island periods with age- and stage-corrected individual recruitment and dated physical habitat; do not invent statistical independence by renaming capes "islands." PR189 Ecology original manuscript, PR142 locked USAP mark–resights, and PR195 emperor-colony georeference audit remain unchanged.
