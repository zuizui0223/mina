# V31 — original OBIS historic Antarctic seabird/penguin observation comparability gate

**2026-10-26, designed after observing V30 original data schema and aggregate counts, before inspecting record-level source lineage/stage/duplicate attributes. This is a POST-SCHEMA source-quality audit, not a preregistered biological effect fit.**

## Core original empirical facts from V30

Original first-party IPT/OBIS original FAUNA_PENGUIN_COLONY archive, exact version 1.0 publisher ZIP SHA256 `c17670be07fed76492a30a59893d059f4ccb11d54f2f73bceeaf007c19e311d5`, original 2,787 source rows, original 12 species/taxon labels **including four flying seabird taxa** (hence the title 'penguin colony census' is taxonomically broader), and original 1900–1998 rows despite 1900–1996 source title. The original source value field `individualCount` has only 2,377 numeric nonnegative rows, **23 literal zero records**, **207 literal -1 records** (unknown/sentinel, NOT negative population size), ~200 empty and three other invalid count cells. The 23 zero cells are NOT automatically an explicit survey with species absent; source observation/census method must establish that.

Original source has 2,550 dated source records, 766 literal `locality` values, 2,592 valid decimal coordinates, and **852 repeated locality × year × species cells** (not necessarily duplicates, because localities may aggregate many colonies). The raw `eventDate` commonly defaults to January 1, which is not defensible as exact field effort date.

## Quality audit performed *without* fitting animal ecology

1. Re-download exact publisher original v1.0 archive; hard STOP if original ZIP or occurrence.txt SHA changes from saved `results/OBIS_ORIGINAL_1900_1996_PENGUIN_SOURCE_V30.json`.
2. Preserve literal count-status frequencies (positive, original zero, original negative sentinel, empty, invalid). The original `lifeStage`, `occurrenceRemarks`, `dynamicProperties`, `preparations`, `basisOfRecord`, `coordinatePrecision`, `bibliographicCitation`, `associatedReferences`, `recordedBy`, `catalogNumber`, `recordNumber`, and `fieldNumber` are inspected for **source semantics and explicitly documented census stage**. Do NOT translate nested records into breed pairs merely because `individualCount` exists.
3. Quantify true distinct `core_id`/catalog/reference provenance, unavailable/missing source identifiers, first-party citation family cardinality. **Data from the same publisher/field survey cited twice must not be counted as independent biological replication** from MAPPPD.
4. Compute independent source support as *descriptive* distinct `locality + original coordinate pair + species + original year`, without claiming that unverified place names and rounded original gazetteer coordinates identify the same patch across years. Exact original duplicate full observation signatures are flagged, not picked by count.
5. Report repeated original `locality + species` with ≥2 dated seasons and ≥2 truly nonnegative numeric count rows separately from those repeated only under a rounded coordinate condition. For an eventual island-level longitudinal biological model, require original effort and stage-compatible distinct independent islands, not repeated aliases.
6. Report named penguin taxa versus flying seabird taxa explicitly. Original flying-bird data can be useful as comparator only after matching field census stage/effort; the dataset name does not make all 2,787 records penguins.
7. Source source temporal year 1998 compared with publisher title 1996 is documented, not silently truncated. Do not restrict years to create nicer habitat associations post outcome.
8. Report direct site-level survey presence/non-detection field availability. An original 0 count could be a true surveyed absence or unknown census category; unless a source method/effort variable resolves it, treat as `ZERO_REPORT_UNVERIFIED` and **never model colonisation/extinction**.

## Stop conditions

Any missing source-level author/citation genealogy or insufficient geographic precision makes a conventional occupancy/island-hysteresis or annual demographic-rate test **not identifiable**, even with 2,787 original records. Stop rather than tuning source region names or using a standardised colony area from unrelated data as a demographic count. A favorable `individualCount` distribution alone is NOT a measured island effect. Output is signed source QA receipt and a prospective-to-any-new-source model readiness decision, no source-dependent island hypothesis p-value.
