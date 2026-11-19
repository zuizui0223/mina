# V33 — New original 2026 Ross Sea 39-colony Adélie aerial census supports a macro observation panel

The **original, independently published Manaaki Whenua / Landcare Research** DOI https://doi.org/10.7931/kf06-x745, updated 2026-02-24, was obtained via the official CKAN API. Original data, location and methods resources were verified and source-hashed. [Actual original-data Actions #39722542914](https://github.com/zuizui0223/mina/actions/runs/39722542914) and five synthetic tests succeeded. CC-BY-NC-4.0, acknowledgement and noncommercial data licence apply.

## Original sources and authenticity
- Census XLSX Ross Sea 1981–2024, 12,578 bytes, original publisher MD5 195a9027a0d18012812b09fb345ac60e; SHA256 **23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6**. One original sheet **All data**, 41 source rows; 44 census-year columns.
- Georeferenced colony names/locations original XLSX, 8,025 bytes, SHA256 **d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6**. Has 40 geographic source rows; original first columns contain colony name, regional landmass/locality, latitude and longitude text. It provides a prospective external ID/location crosswalk but must not be misused to assume every colony is an independent physical island.
- Original methodology PDF, 29,666 bytes, SHA256 **6525afbdb5cc68c4312d33280f81f21af53ae89f8bb50c5439eaa9d9ab3f185f**. The older descriptive PDF still refers to 1981–2017; the 2026 census workbook itself includes years to 2024, illustrating a source-document version difference that must be acknowledged before using field methods. The publisher explicitly states no surveys in 2020 due to COVID-19, not extinction.

## Actual original source-coverage result, OUTCOME BLIND
| Original colony-source support | Value |
|---|---:|
| Named colony rows | **39** |
| Calendar year columns | **44**, 1981–2024 |
| Colonies with at least 5 explicit numerical records | **27** |
| Years with at least 5 explicitly numerically recorded colonies | **41** |
| Years with at least 10 such colonies | **21** |
| Same-colony strictly consecutive-year observation opportunities | **305** |
| 2020 explicit numeric count entries | **0** (source survey missing) |

The most consistently monitored colonies include Cape Bird North/Middle/South, Cape Crozier East/West, and Cape Royds — many nested on **Ross Island**, so 305 consecutive observations are **NOT 305 independent island-year populations**. Coulman and other remote colony series are substantially less frequently surveyed and methods/precision need source metadata validation.

The predeclared COLONY source and year support thresholds passed. **Biological abundance effect models fitted: zero.** No source absolute nests/pairs counts, synchrony, spatial contrasts or ecological slopes were opened. Physical island grouping, site identity aliases, survey stage and analytical independent-island units are still under verification.

## Next action
V34 freezes exact public original colony-location name matches and groups only independently named landmass references. Do NOT silently convert geographically nearby coastal caps/continental peninsulas or multiple Cape Bird subcolonies into independent oceanic islands. Report missing aliases and geographic effort, then define a prospective V35 effect test only if sufficient independent island×year contrasts are available.

- [Source and eligibility contract](../contracts/NZ_ROSS_SEA_AERIAL_CENSUS_SOURCE_V33.md)
- [Original source/temporal coverage result JSON](../results/NZ_ROSS_SEA_39_COLONY_SOURCE_QA_V33.json)
- [Publisher original dataset](https://datastore.landcareresearch.co.nz/dataset/adelie-penguin-census-data)
