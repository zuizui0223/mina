# V28 and V29 — Original AADC true-island source and season support

**2026-10-21: publisher original Excel source download and source-presence audit completed.** Both tests, [V28](https://github.com/zuizui0223/mina/actions/runs/39528890416) and [V29](https://github.com/zuizui0223/mina/actions/runs/39529328337), were successful.

Official AADC DOI 10.26179/5c9bf6704cf70 source file population_counts_BI.xlsx, original publisher SHA256 8377fd17d4d84ccb791229ebdf5926605ae34aeffd0c1a21a0a7ae75d4facdf6, 17,968 bytes, is a three-physical-island occupied-nest census archive. An extra publisher worksheet contains earlier counts from Giganteus, Shirley, Whitney Point and Rookery groups; these may be geographically and methodologically incompatible and Rookery groups include overlapping aggregates/components. Another AADC original archive DOI 10.26179/s2qa-s344, source file Time series demography and environmental covariates.xlsx (15,637 bytes; SHA256 91862ed4f607c5031adbd220372a274b1376c68f535e5dcbc4b19412c1e48b67), includes 1991–2019 Béchervaise demographic, temperature, windchill and nearshore sea-ice variables. Those are a single regional environmental proxy, not independent island-specific exposure measurements.

## Pre-outcome 1990–2004 original-year results

| Named true physical island set | Seasons with explicit numeric census-field presence | Strictly consecutive start-year pairings | Fixed >=8 years, >=6 pair gate |
|---|---:|---:|---|
| Béchervaise | 15 | not a between-island comparison | — |
| Verner | 10 | not a between-island comparison | — |
| Petersen | 5 | not a between-island comparison | — |
| **Béchervaise and Verner** | **10** | **8** | **PASS** |
| Béchervaise and Petersen | 5 | 1 | FAIL |
| Verner and Petersen | 5 | 1 | FAIL |
| All three islands simultaneously | 5 | 1 | FAIL |

The two-island source seasons are 1991 and 1996–2004, with strictly consecutive changes starting 1996 through 2003 (8 transitions). Source row notes classify the post-1990 records as occupied nests, whereas pre-1990 source may record adults or corrected counts from photographs, excluded. The original single date column does not demonstrate identical counting dates on each separate island.

The other named-island worksheet gives Giganteus population presence only in 1972/1981/1988 and Shirley in 1971/72/76/77/89/90/92, so it cannot directly provide a contemporaneous comparable 1996–2003 cross-region test.

**Scientific decision:** the source gate passes only for Béchervaise–Verner, two physical islands and one local island complex. This does not establish a pan-Antarctic macroecological law. No biological count levels, growth correlations or marine effects were computed at V28–29. Next V30 should verify original occupied-nest stage and season dates, then measure observed near-island covariance with a frozen small-sample estimator, without imputing missing Petersen years.

- [V28 verified source schema receipt](../results/AADC_THREE_ISLAND_SOURCE_V28.json)
- [V29 actual matched-season receipt](../results/AADC_THREE_ISLAND_SEASONS_V29.json)
