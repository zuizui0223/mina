# V13 — Original AADC 7,785 potential-site and 33,107 search-record source integration (before opening biological rows)

**2026-10-19 23:08 JST follow-up.** Original site, Adélie, flying-seabird and ascertainment workbook headers have been decoded from authentic AADC files in successful V12. **No biological response rows have been read by the V11/V12 workflow, and no novel occupancy interaction has been fitted.** This V13 contract is committed before ingesting original spreadsheet observation values. Original sources are separate from the 2023 APBP site-only breeding-count database.

## Exact original publisher source files (already SHA-verified in V12)

AADC 2025 East Antarctic breeding occupancy, DOI `10.26179/5n29-r073`:
- `geog_sites_all.xlsx` SHA256 `ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294`, sheet `2_geog_sites_all`, 7,785 geographic site records by spreadsheet dimensions. Attributes `geog_site_id`, `geog_site_feature`, `geog_site_area`, `geog_site_area_cat3`, `distance_station`, `distance_inland_coast`, lat/lon and `sub_group`.
- `occupancy_penguin.xlsx` SHA256 `8b38aa86f0ef2a0a9fe8c5bb13da904a9f2431cd503644b962b6e116ac3187ac`, sheet `2_search events`, 11,089 original Adelie search-event rows.
- `occupancy_seabird.xls` SHA256 `4a03d8efc8f1579b2eafd982811c39edc00d2c87d49e990f93c6411db6860360`, sheet `2_search events`, 22,018 flying-seabird rows.
- `occupancy_certainty.xlsx` SHA256 `b7aba52732102441b4edbe438b854cb9d2dbf39542fd6fbfcd62647ae9fdd156`, sheet `2_occurrence certainty`, 216 category rule rows.

AADC 2021 potential ice-free geography reference, DOI `10.26179/53yk-8z83`:
- `Spatial reference systemn coastal East Antarctica.xlsx`, source SHA256 `2236269e754962f9af082a0853993fc65a4afd20c7489a65fae81bdd1899ffaa`, sheet `2_Geographic sites`, 4,884 site features, originally 37–160 E. The older geographic frame is **not** interchangeable with the 2025 7,785 geographic-site table; compare exact site identifiers and coordinate agreements before combining.

## Data integrity before ecology

1. Use official AADC API `/eds/api/dataset?size=10000`, UUIDs `4344` and `5959`, original `/eds/api/dataset/{uuid}/objects` and authenticated publisher object-download paths. Validate file size/SHA256 against V12 pinned originals. Parse original Excel XLSX/XLS sheets by exact sheet title and source column names, *not* inferred column positions. Preserve metadata tab text (contains original coding definitions) without treating it as biological response.
2. Report all original counts and nonmissing `geog_site_id` link. Distinct potential geographic locations and survey events cannot be treated as individual islands, new colonization events or independent biological replicates. Audit original site area units and positive-valued area before using habitat/isolation predictors. Provisional `geog_site_feature` categories and `geog_site_area_cat3` source values MUST be reported unchanged (their meanings not guessed).
3. For each source search row preserve source `species_code`, `occurrence`, `vantage`, `geog_site_id`, `breed_site_id`, observation `day/month/year/season`, `obs_number`, all three original expert-validation fields. Compare all occurrence category codes against original metadata sheet and the certainty table. In particular, **absence** is usable only where the original record explicitly reports absence AND certainty class/detection criterion is identified. **Nonreporting is unknown**, not an absence. If `occurrence` labels/units lack explicit documentation, stop and report a coverage-only result without recoding statuses.
4. Link certainty table by exact categorical `species_code × occurrence × vantage × geog_site_area_cat3` only if keys and categories match. If two possible certainty rows, count them as ambiguous rather than choosing by apparent effect. Preserve original `site_search_completeness`, `product`, `occurrence_cert_cat`. Do not infer observation effort from data density alone. Opposite-status reports in the same site/species/season remain **conflicts to retain and classify**, not averaged or resolved by choosing presence.
5. Require temporally and geographically validated inputs before any model: original site/sub_group and code mappings, true breeding absence versus nonreporting and reliable survey completeness, date/season support and coastline-feature area. Never treat all 7,785 candidates as surveyed breeding-negative sites.
6. Stage V13 reports only source-geography/study support: first-party dataset fingerprints, original occurrence/status/precision categories, site coverage and area/isolation availability, site×species×year/season duplication/conflicts, and species-level high-certainty absence/presence counts. NO species trait-effect regressions, island-size effect, flight mechanism or p-values at this stage.

## Separate later ecological question, not yet answered

After explicit effort/observability is linkable, compare occupancy vs known-absent **within documented searched sites**, with original eight species strata and pre-defined nesting strategy:
- Exposed-ground: Adelie, south polar skua, southern giant petrel (requires nesting-source confirmation);
- Rock ledge/sloping rock: Antarctic petrel, Cape petrel, southern fulmar (taxonomy/source citations and mixed-mode sensitivity required);
- Sheltered/crevice: snow petrel, Wilson's storm petrel.

The original publisher already reported known occupancy patterns and sampling bias (Southwell et al. 2025, DOI 10.1111/ddi.70066): not original novelty. A distinctive **species-guild × physical island-feature size/isolation interaction** would be new only if supported beyond that prior work under geographic held-out validation. Shared regional environmental gradients, species-specific detection, historical survey status and site-area unit/geometry must be controlled. No claim that Adelie flightlessness means low marine dispersal is allowed.

Do **not** alter closed V6 or V8 negative effects or frozen Ecology PR189.
