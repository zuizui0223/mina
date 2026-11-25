# V6 modern marine–breeding–land bridge: executed result and scope decision
2026-11-25. Outcome-aware support audit, not a new ecological effect or evidence of no relationship.

## Source and execution
Primary contract commit 622d429460a1e266d88f40d9b049da11e7642e48; MAPPPD v5 method-sensitivity contract commit 431bea54ca66b664a8b855e88e5c417c8ed190de. Four original Actions artifact ZIPs downloaded and SHA256/CRC checked in the current local runtime:
- 13669533413: 595 source sites and 2,456 method-selected nest counts.
- 13829236358: 16,464 site-years / 588 coastal sites and 167 positive modern mapped terrestrial Vegetation+Lichen area records.
- 14926710177: 21,420 radius-site-winter rows, 17,850 complete; missing winters retained.
- 14934334550: original MAPPPD v5 full 5,487-row CSV, source member SHA256 as prior PR219.
Same nominal site ID and atlas coordinates/source regions verified for all count, hydro and polynya rows; map table has ID/region and static date only, not independent plant field coordinates. Modern area is positive mapped union in a 2-km neighborhood; neither land-normalized cover nor annual vegetation.
Both scripts ran locally twice and produced byte-identical JSON. Exact executed code and result blobs verified after writing to GitHub, commit 9e8fa76c2bc1cd51a404335ba77d6cf88db6fa2d. Code blobs 3cf6e3f558a86eeff4182bc9265a6332dc002bd5 and dd8eb114fc5473c2b5cff6b64f3cd549d4641c5c; result blobs ba50612e031249b9b837544b30d7f1028b7859e3 and 46fff368049469dbf244a030a859f619d8be92df. This is actual local execution, not a new Actions run.
Reproduce from unmodified ZIPs in one directory:
`python modern_marine_land_bridge.py ARTIFACT_DIRECTORY RESULT.json`
`python modern_bridge_v5_sensitivity.py ARTIFACT_DIRECTORY V5_RESULT.json`
No raw publisher records republished here.

## Exact modern-period support
2017–2020 all four annual nest counts, and separately 2017/2020 exact endpoints, same known census method, complete SIC/SSS/SST and 25/100km polynya exposure, with positive-map nested subset. No relaxation or regression.

| Species | Primary four years: raw / full marine / positive map | 2017/20 endpoints: raw / full marine / positive map | V5 endpoints before method gate | V5 endpoints after all gates |
|---|---|---|---:|---:|
| ADPE | 0 / 0 / 0 | 1 / 1 / 1 | 1 | 1 |
| CHPE | 0 / 0 / 0 | 1 / 1 / 1 | 2 | 1 |
| GEPE | 0 / 0 / 0 | 5 / 5 / 5 | 7 | 5 |

All endpoint supports are Central-west Antarctic Peninsula, one 250-km block. GEPE five sites share three wet cells. All four-year supports zero. The original v5 extraction reconstructed every old key, method and count exactly (2,456/2,456), and adding 268 alternative-method groups to 2,724 known-method agreed groups did not increase endpoint support or give complete four-year series. Counts from different methods were not averaged or selected using ecological outcomes. Thus all six primary/endpoint species cohorts fail the pre-fixed >=3 sites AND >=2 regions accounting gate; no new N/H/TV/C or weighted land/marine coefficient was estimated.

| Same nominal site-season, same known method, all physical exposure and positive map | Legacy site-seasons | V5 site-seasons / sites / 250km blocks |
|---|---:|---|
| ADPE–CHPE | 5 | 5 / 3 / 2 |
| ADPE–GEPE | 8 | 9 / 6 / 3 |
| CHPE–GEPE | 20 | 20 / 12 / 4 |

These occur in just two reporting regions in the legacy data. The alternative-method addition is one ADPE–GEPE paired site-season; not independent observations of interactions. Same nominal site/year/method does not imply same dates/footprints. No species interaction coefficient. The map itself is a 2017–2023 composite and cannot identify plant change even if animal time series were complete. Isotope seasons 2004–10 do not coincide with modern map.

## Scientific decision
Retain the existing direct long 23/17 and short 15/9 breeding-allocation × marine exposure accounting (V5), not an imagined continuous marine-to-land chain. The modern complete-cohort gate is closed; no new radius/window/model tuning. Existing original-source Palmer seal/vegetation local overlap and Shirley historic-status contrasts are empirical **spatial** evidence, not plant recovery, and Signy population composition contrasts are not demonstrated competition. The broader Antarctic manuscript is now an explicit author-review synthesis alternative, with separate units and evidence levels. It is not a single validated mechanism paper. The narrower seabird v0.2 remains the stronger self-contained empirical paper. Do not submit overlapping manuscripts or automatically replace frozen papers.
