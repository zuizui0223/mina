# V16 — 2011 same-scene digitizer disagreement and classification-sensitive site succession

2026-10-13. **Post-outcome exploratory robustness specification**, prepared after V10 and V15 results were seen but BEFORE calculating the distinct V16 between-map agreement and substitute-baseline E/F endpoints. Ecology PR189 remains frozen.

## Verified inputs and existing results

- Primary original-year 2011/2016 pair: V10 gain-overlap E = 0.669617, reverse F = 0.079741; no observed movement or causal competition inference.
- 2011 original Lynch redigitization has **CHPE 442**, **MCPE 18**, **MIXED 46** historic polygons. MIXED was not assigned to one species. V15 found 5,427.387 m² of V10 new mapped macaroni habitat and 5,169.202 m² of apparent chinstrap-loss→macaroni-gain overlap inside historic MIXED polygons. Historic first-map observation is the **same Jan 2011 scene**, not a replicated year.

## New endpoints, computed without choosing a favorable result

All geometries in independently verified EPSG:32726; years anchored at 2011-01-08 and 2016-01-09. Comparison support *S* is the union of all 2011/2016 revised and historic colony geometries, minus the entire union of independently mapped 2011 and 2016 original-year cloud polygons. Both competing map interpretations use exactly the same *S*. Exclude every under-cloud replacement and 2020–22 composite.

1. **Agreement diagnostics**: Compare revised 2011 C map against CHPE, revised M map against MCPE. Report intersection/union Jaccard per species on *S* minus historical MIXED and any overlap among incompatible historic pure species labels. Report fraction of revised species-occupied area intersecting each historic CHPE/MCPE/MIXED class separately. Do not force a partition when two historic categories intersect spatially.
2. **Fixed nonmixed-support alternative-history test**: define *S_nonmixed* = *S* minus historic MIXED minus CHPE∩MCPE. Compare E and F under revised 2011 C/M and under historic CHPE/MCPE **on that identical support**, while retaining unchanged revised 2016 C/M. Report all four denominators and absolute gained/lost m². Values defined only for nonzero mapped gain and loss, otherwise null. This does NOT mean historic polygons give a true alternative ecological state; it is a same-scene cartographic sensitivity.
3. **Independent historical-absence diagnostic**: report fraction and m² of V10 *macaroni gain* and apparent *chinstrap-loss∩macaroni-gain* outside historic MCPE∪MIXED on *S*. This is absence of historical depicted macaroni, NOT verified absence of breeding.
4. **Coordinate consistency**: verify original .prj and current .prj; independent CRSs matching EPSG:32726, reject empty/invalid polygon shapes. The original historic DBF label/record roster must exactly match V14 source counts, and all native files have SHA256 stored. No shape-repair or retroactive polygon source switching.

## Interpretation gates

- If same-scene alternate-digitizer E differs materially from V10, downgrade exact micro-patch succession claims to map-classification-sensitive.
- If E remains relatively similar, only claim map-level co-location robust to *this specific* alternate digitization, not verified biological site replacement. Distinct satellite image co-registration, within-interval order, observation effort, accessible nest substrate and ecological site-preference null remain untested.
- MIXED is a polygon with both species potentially co-occurring somewhere inside, **not** guaranteed species overlap at every square metre.
- No p-values, no independent biological validation and no ecological causal inference.

Original data DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308, V15 script reused for historic class geometry and V10 strict date-specific cloud masking.
