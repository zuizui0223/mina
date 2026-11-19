# V32 — Mac. Robertson Land 2009/10–2019/20 regional population bootstrap has no verified island ID

2026-10-22. Original Australian Antarctic Data Centre 5516 "W Mac. Robertson Land Adelie penguin population estimates.xlsx" was retrieved by its exact public HTTPS dataset UUID and original member name. Source: DOI https://doi.org/10.26179/s2qa-s344. Binary original is **51,218 bytes**, SHA256 **cc9711ebcfa8088b11b4959a40715f7c56b2f65e4f559e47a1a882d641010c2a**. Original source/test [Actions #39721482630](https://github.com/zuizui0223/mina/actions/runs/39721482630) succeeded after a missing transitive xlrd test-runner dependency was added.

Publisher workbook sheets:
- "data description": 10 rows × 15 columns, text says regional western Mac. Robertson Land Adélie metapopulation survey.
- "2009_10 2019_20": **1,001 rows × 8 columns**, metadata field names include replicate and O.N.bootstrap.estimates.2009_10 / O.N.bootstrap.estimates.2019_20, with Median, L95, U95 labels.

No island_id, site_id, colony_id, region_id, or equivalent physical landmass identifier was exposed by the source header inspection. The publicly documented analysis contains **1000 uncertainty bootstrap realizations**, not 1000 independently observed islands. This file cannot be used by itself as a temporally matched multi-island population panel. Its regionally aggregated estimates cannot be assigned to Béchervaise, Verner and Petersen islands individually. The quantitative estimate values were never accessed, fitted, or duplicated.

**Scientific decision: HOLD_SOURCE_HEADERS_NOT_PROOF_OF_ISLAND_REPLICATION.** The header-only audit does not logically prove no geographic ID could exist in less obvious content elsewhere, but the workbook clearly presents a regional bootstrap grain with no verified multi-island census ID. Source-specific relocation, colonization and island-area effects remain unavailable. A larger genuinely multi-colony database with independent geographic metadata is needed, rather than making uncertainty draws into ecological units.

Source-backed original machine-readable audit: [AADC_METAPOP_2009_2019_SOURCE_GRAIN_V32.json](../results/AADC_METAPOP_2009_2019_SOURCE_GRAIN_V32.json). No original count data placed in Git.
