# APBP v2 — original count-to-site-year joining contract (2026-10-18)

**Frozen before opening original individual count values or derived site–species–year sample distribution.** Stage1 is complete and source-locked (full official 2023 v2.3 publisher ZIP SHA256 `afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf`; 389,798 bytes). Stage1 showed Event 4,055, Occurrence 4,768, ExtendedMeasurementOrFact 4,750, 719 original locationIDs, 479 siteIDs in 2+ years, 149 in 5+ years. eMoF has 3,514 nest/breeding-pair measurement types and 1,236 chick/adult measurement types. **None of these records has yet been joined to independently mapped true islands or climatic time series and no environment effect has been fitted.**

**Taxonomy correction required before stage2:** Original publisher lists `Pygoscelis antarctica` 1,371 occurrence rows, a documented synonym of the accepted name `Pygoscelis antarcticus` (NCBI Taxonomy 79643; WoRMS Aphia 225783). Stage1 original-name raw counts are correct, but its preliminary `known_six_species_occurrence_rows` left out those 1,371 solely because a lookup expected the accepted spelling. Store BOTH original scientificName and explicitly canonicalized name, never silently drop this species or create a seventh species.

## Required unambiguous relational join

- `Event` core XML `<id>` links original extension `<coreid>`.
- An Event may contain observations of MULTIPLE species. NEVER merge eMoF measurements with species by Event ID alone.
- First bind the original `Occurrence.occurrenceID` with the original `eMoF.occurrenceID`, and verify the eMoF core-event ID matches the matched Occurrence's core-event ID. Unique matching is necessary; ambiguous/missing occurrenceID is a scientific STOP. Do not infer species by site or event if linkage is incomplete.
- Only assign exact original units if `Occurrence.organismQuantity` and `organismQuantityType` are compatible with eMoF `measurementType` and `measurementValue`. Inspect exact original source field meaning; raw eMoF measurements may reflect precision rather than abundance and must not be treated as nest number without direct evidence.
- Zero is accepted **only** if explicitly reported as a measured nest count on a verified survey row. No unsurveyed site-year or absent species is assigned zero.

## Result allowed at Stage2

- Produce a **traceable original record-level** CSV of measured `Event × Occurrence × Measurement` records with original eventID, occurrenceID, measurementID, locationID, islandGroup (publisher metadata ONLY, not island ID), eventDate/year, latitude/longitude + uncertainty, original and accepted taxa, observation units/count scale, raw quantity and precision, protocol and associatedReferences.
- QA JSON reports missing foreign keys, duplicate primary keys, unmatched taxon/unit, parseability of numeric counts, count type composition, original precision classes, observed zero counts, repeated site+species+year support, and distribution of number of distinct survey years. **No trend, slope, effect, climate association, or p-value.**
- A prospective `site × species × year` nest trajectory is **eligible only** for directly observed nest/breeding-pair records with original quantitative count and compatible eMoF measurement-type evidence, known locationID and a valid year. Preserve all repeat surveys and count methods; do not choose a favorable duplicate. For follow-up summary, report site–species–year group size, one-year-only groups, same-year duplicates, and matched years. No source-site is assumed to represent an island.
- Output complete public-derived row CSV solely as CI artifact with explicit CC BY 4.0 dataset attribution and SHA; commit ONLY schema and QA numeric coverage receipt to GitHub, not an unsupported island classification.
- If a source measurement/accuracy label is opaque, mark `HOLD_QUANTITY_SEMANTICS` for the corresponding rows. If original keys are unmatched, mark `HOLD_RELATIONAL_AMBIGUITY` instead of choosing an arbitrary species. No model fitting at this stage.

## What this cannot yet identify

Original APBP event records are collected for previously known colony sites and may include duplicate survey accounts. They cannot establish island-wide survey zeros for unreported species or previously unrecorded vacant habitats. The APBP core often defines coastal 'sites' rather than whole islands. The 2026 ADD rock map cannot independently reveal historical year-specific land-ice changes. The user-facing goal remains a future analysis of independent substrate capacity × marine access × nesting ecology conditional on observed breeding histories. All inferential claims remain untested until true island/continent GIS joins, offshore ice anomalies, and independent observation-effort matching are validated.
