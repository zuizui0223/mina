# V31 historical Antarctic seabird primary-source observation eligibility (post V30)

**Locked 2026-10-26 after V30 confirmed the exact 2,787-row OBIS archive and 2,377 finite numeric individualCount entries.** This is a source-scientific audit, not a preregistered hypothesis test; no new island effect may be fitted by this stage.

## Question

Does the original first-party OBIS/Woehler 1900–1996 source contain actual repeated **same-colony × same-taxon × same-count-stage** annual observations, or merely presence occurrences carrying loosely-defined counts with assigned site names? The title "penguin census" is insufficient to assume every numeric individualCount is a nest/breeding pair observation.

Original first-party source must match pinned ZIP SHA256 `c17670be07fed76492a30a59893d059f4ccb11d54f2f73bceeaf007c19e311d5`; original version 1.0 https://ipt.obis.org/nonode/archive.do?r=iasb&v=1.0 . IPT 2018 publication CC BY 4.0. V30 confirmed the source actually includes **12 seabird taxon names**, not only penguins: flying petrels and giant petrels are present.

## V31 audit, prior to ecological model

1. Inspect literal source `individualCount` by taxon, year and its measurement context. Source `lifeStage`, `dynamicProperties`, `occurrenceRemarks`, `recordedBy`, `bibliographicCitation`, `associatedReferences`, `basisOfRecord`, `collectionCode`, `catalogNumber`, and original accuracy / locality fields are descriptive metadata. Do NOT infer egg/chick/adult stages if not explicitly and consistently encoded.
2. Validate count values: finite integer >=0 as an *unverified reported quantity*, separately record missing/nonintegral/huge values, 23 original explicit numeric zeros. Numeric zero without original field survey effort and detection documentation is **not a verified surveyed absence**. Never convert missing count to 0.
3. Identify repeated **exact source textual locality** plus taxon plus literal `lifeStage` and original count source; use exact `waterBody`, `stateProvince`, `county`, `locality` (no fuzzy name/coordinates), year from explicit `year` or valid original `eventDate`, and numeric count. Report candidates with >=2 and >=3 *distinct* years, record names and count-stage proportions, but **this does not establish identical biological colony footprints or independent source citations**. Coordinate-only matches are not independent nest GPS and may be gazetteer assigned.
4. Report maximum source count, original chronology, taxon and geography frequency, source IDs, repeated count records within source same key/year, original `coordinatePrecision` categories and missingness. At this stage there is no confirmed `MAPPPD` original survey crosswalk: do not count re-hosted OBIS records as independent original field observations in a meta-analysis.
5. A biological island-time-series test becomes eligible only if source count stage, original site identity, original year, effort/citation and source geography pass a prospective independent test; otherwise source STOP for demographic/island dynamics. No post hoc regional/GIS buffer, life-stage assumption, or scientific exception from source year/gazetteer ambiguity.

## Output

Pinned reproducible JSON with counts by source taxon, exact-literal stage quality, location-year-taxon group candidate counts, duplicate and original zero source diagnostics. No raw occurrence table committed. The goal is to identify if this genuinely new open archive contributes extra ecological **observations**, not to multiply meta-effect sample size.
