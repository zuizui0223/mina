# V34 — Frozen geography and same-year eligibility of the 2026 Ross Sea colony panel

Frozen after V33 verified original 2026 39-colony census 1981–2024 and its 305 same-colony consecutive-year opportunities, but BEFORE original bird count magnitudes, correlations, size trends, or any ecological effects were examined. The source site-location workbook has 40 rows of colony names, named places (e.g. "Ross Island", "Coulman Island"), latitude and longitude. Geographic names may represent source aggregation or regional labels: a COLONY ≠ independent physical ISLAND.

## Original source and scope
Exact original publisher CKAN API, download paths/MD5/resource UUIDs fixed by V33:
https://doi.org/10.7931/kf06-x745
Census xlsx SHA256 23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6, 12578 bytes.
Location xlsx SHA256 d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6, 8025 bytes.
Original PDF already source-hashed V33; its older 2017 date coverage metadata may be stale relative to the 2026 2024-colony XLSX.

## Predeclared geography-only join and support
1. Re-fetch exactly the V33 source files and abort on SHA drift. Use only source colony ID/name from the first column of census worksheet All data and original location worksheet first col, literal named-place second col, source coarse coordinate text third/fourth col. Match IDs by casefold Unicode NFC normalization and whitespace ONLY, never by coordinates, count magnitude, post hoc proximity, name prefix or fuzzy matching. Exclude duplicate source IDs wholesale.
2. Distinguish source localities explicitly named "... Island" from named peninsulas, cape/continental slopes and broad regional descriptors. A source named-island string is a candidate LANDMASS UNIT, not an independent GIS-certified island boundary. Unmatched names remain HOLD, including "Beaufort Island New" versus "Beaufort Island North" if those arise; no silent alias.
3. Direct original second-field explicit singular "... Island" can be a source-island grouping. If second field is only a broad oceanic region, accept colony name itself ONLY when it exactly ends with singular " Island"; do not transform "Cape Bird" into an island by capes alone. Terms ending in plural " Islands" or composite island groups are not independent single landmasses.
4. Parse original latitude/longitude metadata text ONLY when unambiguous degrees/minutes and cardinal indicators; no invented precision, map geometry or census count outcomes. A location row lacking explicit island reference is NOT an island.
5. Using original fixed 44 census years, count colony×year NUMERIC OBSERVATION PRESENCE only, not abundance. Any colony's missing year is never a true biological zero; publisher reports 2020 as unobserved. For each named-island group and annual y→y+1, require >=1 SAME original colony with source numerical measurements in both y and y+1. This is the independent-landmass source support unit (number of physical islands still conditional on geometry).
6. Numeric sample gate for a subsequent independent V35 two-island annual growth contrast: at least THREE explicitly named distinct island units with >=5 annual same-colony paired windows each, and >=8 annual windows with >=2 separate named island units monitored. A stricter within-vs-between COLONY contrast needs >=2 islands EACH with >=2 common same-colony within-year transitions in >=6 shared windows. If fail, no effect/lag/radius/sample relaxation.
7. Even if source count gates pass, actual V35 ecology needs source stage, survey timing, original aerial count methods and physical island polygon identity verified. The known old method PDF describes data through 2017 and may not document 2018–2024 continuity; no assumption that new columns used an identical observation protocol.
8. Coastal/nonisland named peninsulas can be retained as a separate future mainland comparison, but do not make them islands. Do not count Cape Bird North/Middle/South as three physical islands; these are component colonies on Ross Island.
9. This is new independently collected public original data but APBP/MAPPPD may republish overlapping Ross Island source counts; matching identical original events is not independent replication.

No original animal count magnitude, growth correlation, island-distance model, metapopulation rescue or macroecological causal effect may be opened in V34. Frozen Penguin Ecology PR189 and closed APBP V27 remain unchanged.
