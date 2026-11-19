# V40 — Actual original MAPPPD v5 macro sample and author-census deduplication

**Executed 2026-10-24.** Official Oceanites MAPPPD release v5.0 dated 2026-10-21, publisher CC BY 4.0, original 729 site records and **5,487** observations, downloaded from official public API: https://www.penguinmap.com/api/docs/. Initial unpaginated CSV contained 100 original records (publisher default page), corrected to exactly **page_size=5000&page=1 (5,000)** and **page=2 (487)** without altering any biological sample threshold. Original two source page SHA256 receipts and response version are in [V40 JSON](../results/MAPPPD5_MACRO_SOURCE_AND_NZ_PEDIGREE_V40.json). [Successful source CI #40080457954](https://github.com/zuizui0223/mina/actions/runs/40080457954); synthetic tests passed.

## True publisher original source structure

| Original source measure | Measured |
|---|---:|
| Antarctic penguin observation rows | **5,487** |
| Site IDs (not independently surveyed islands) | **729** |
| Source count types: nests / chicks / adults | **4,055 / 850 / 582** |
| Ambiguous repeated site×species×season original groups removed | **426 groups, 1,022 original rows** |
| Strict true adjacent-year same site/species/citation/vantage nest-record opportunities | **771** |
| Distinct source site IDs with such transitions | **95** |
| Distinct original publisher region names | **11** |
| Original species transitions Adélie / chinstrap / gentoo | **414 / 152 / 205** |
| Species×year×region strata with at least 5 site IDs | **54** |
| Different/unknown source citation leading to held adjacent pairs | **104** |
| Different/unknown survey vantage leading to held adjacent pairs | **19** |

The source observational support gate for future ecological macro work **PASSED**. These records are not automatically separate biological islands, nor does same source citation guarantee actual same survey method, nest stage or detection error in each year.

## Already-published underlying source genealogy: avoid pseudo-independent replication

Source original NZ Ross Sea aerial author census DOI 10.7931/kf06-x745 from the earlier V33–V36 analysis is already cited as MAPPPD reference key **manaakiwhenua2021aerial**. In actual original 2026 v5 source, this upstream citekey appears in **519 observation rows**. Exact match between NZ original named colony, same Adélie species, nests stage, original breeding-start season, that citekey and source numeric observation presence gives **316 matching original site×season records across 21 MAPPPD site IDs**. These are **source-lineage overlaps**, not 316 independent ecological replications; exact count-value equality was NOT tested here.

This is material to the paper: claiming Ross Sea NZ results independently replicate Antarctic-wide MAPPPD patterns without removing original shared field census rows would be pseudoreplication. The source's source metadata still cannot certify that two datasets represent independent colony-year field samples simply because their download URLs differ.

## Next ecological question (not fitted at V40)

Can continued physical landmass structure distinguish breeding response similarity across separate islands from among source nesting sites on ONE island at comparable separations? The new source offers 771 stable source site/species adjacent-year transitions in 11 named regions, but requires 2026 SCAR ADD polygon joins, unique source site identities, original measurement metadata and approximate distance-risk matching before any island-boundary hypothesis. Avoid reviving the V27 spatial-grid result as a "new independent confirmation" because APBP v2.3 and MAPPPD v5 contain overlapping observations. Source island vs continental geography is not proven by 729 source site IDs.

### APBP coordinate-field correction
The older V38 test applied 250m to APBP original coordinateUncertaintyInMeters, but the original APBP 2023 data dictionary defines the Adélie metric as **mean colony-polygon vertex distance to colony centre**, not a GPS accuracy measurement. Large values cannot by themselves demonstrate source field-GPS imprecision. The V38 outcome is correctly reinterpreted as missing *independently verified precision*, not 14 bad colony GPS points. See [V38 correction](NZ_ROSS_APBP_EXACT_GEOREF_V38_RESULT.md) and [original 2023 APBP data dictionary](https://pmc.ncbi.nlm.nih.gov/articles/PMC10848690/).

**Scientific status: PROCEED_INDEPENDENT_ISLAND_SITE_EVENT_LINEAGE_DESIGN.** New source and annual sample stage PASS, but there are no new Antarctic-wide island ecology coefficients at V40. The original V36 four named SCAR islands still have mixed responses and unresolved point-position precision. Frozen Ecology Paper1 PR189 unchanged.
