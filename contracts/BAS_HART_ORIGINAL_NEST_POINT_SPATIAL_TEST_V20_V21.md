# V20–V21 — first-party individual-nest geographies and fixed within-locality spatial segregation test

**2026-10-26, frozen after BAS Hart V19 original CSV HEADER checks and V18 original count table, BEFORE downloading individual nest-coordinate rows for these four multi-species localities.** This is original-database secondary analysis, not an independent new field survey nor prospective test of a novel universal law.

## Source-only eligibility fixed in advance

BAS/UK PDC Hart et al. 2022, DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b, original archive snapshot SHA receipts in V16. V19 directly verified `nest_number,lat,lon` headers in 20 original coordinate files (other 11 source files are outline vertices and one original total table). For an initial same-UAV-survey multi-species test select precisely these original CSV labels, **regardless of how many nests they contain**:

- Ashen Hills (candidate Saunders Island): `ASHE_{Adelie,Chinstrap,Gentoo,Macaroni}_coordinates.csv`, 4 original species.
- Bellingshausen (candidate Bellingshausen Island): `BELG_{Adelie,Chinstrap}_coordinates.csv`, 2 original species.
- Beach Point (candidate Thule Island): `BEAC_{Adelie,Chinstrap}_coordinates.csv`, 2 original species.
- Hewison Point (candidate Thule Island): `HEWI_{Adelie,Chinstrap}_coordinates.csv`, 2 original species.

**10 first-party species-labelled nest-coordinate files, four survey localities, three provisional physical-island names.** These source files have no literal year in their filenames; do NOT invent daily dates. The original publisher dataset reports the **2019–2020 survey campaign**. Verify original acquisition metadata/orthomosaic source before asserting each file represents an exactly simultaneous same-season per-species sample; otherwise temporal co-occurrence remains a documented limitation.

- **Exclude all Zavodovski direct 2022 chinstrap points** from 2020 maca comparisons. Other ZAVO 2020 maca/mixed/unknown original points are already tested in PR #196, not independent island replication.
- Candlemas Island and Herd Point contain only one confirmed species point file each. Source lack of other point files is **not biological absence**. Mixed and unknown points at Ashen/Bell/Hewison/Zavo remain unassigned to source species and are not silently redistributed.
- `SSI_count_results.csv` is a separate 10-category tabular local census source (V18). Never treat this published site total as a full-coverage island population or infer a species' zero from a blank cell.
- Top-level survey locality → named parent island is a **gazetteer provisional identity**, not three independently surveyed physical islands with unbiased complete habitat census. Both Beach and Hewison must stay nested within the same Thule candidate parent island.

## V20 source-point integrity QA (BEFORE spatial phenotype comparison)

Fetch only 10 original CSV first-party files through their frozen V16 exact publisher ID/HTTPS URLs; record SHA256, original row count, source `nest_number` count/uniqueness, numeric latitude/longitude validity, exact coordinate duplicate proportion, fixed south-polar geographical envelope `−61° <= lat <= −54°`, `−30° <= lon <= −24°`, and separate source species/locality. Convert WGS84 to WGS84 UTM Zone 26S EPSG:32726; original site-locality site bounding boxes and source row counts are inspectable provenance, not confirmed observation masks. If a file has invalid/missing original coordinates or duplicate `nest_number` **within the source**, source file remains HOLD rather than rescued by synthetic values.

Validate original coordinate file row count against same-locality species-labelled `SSI_count_results.csv` direct reported counts as a *diagnostic*. A discrepancy may reflect orthomosaic exclusions/source bookkeeping and is NOT corrected by dropping or duplicating nest points. Source original coordinates represent annotated nest centres, not telemetry of bird movements.

Write a small source QA JSON and a compressed derived UTM point-set NPZ per locality. Preserve the exact 10-file sample frozen here; do not select higher effect species or entire sites after reading labels. Do not Git-commit individual point files; CI artifacts with original SHA receipts and names are sufficient.

## V21 fixed post-source geometric test (EXPLORATORY)

If all 10 files pass coordinate integrity, compare within each of **the four survey localities** only. No cross-island nearest-neighbor computations on jointly pooled points. **Primary descriptor**: among the individual confirmed-species nest points with a physically distinct nearest nonself source nest centre ≤ **10 metres** away, report the proportion whose nearest neighbour belongs to a *different* species, `P_heterospecific_NN`. Points whose nearest neighbour is farther than 10m are **not missing observations**, but are excluded from this local 10m descriptor with their count stated. The 10m radius is fixed before outcome analysis; 5m and 20m secondary horizons may be descriptive but cannot replace primary.

- Exclude all nest points at **exactly duplicated projected coordinates within a locality**, even if different species/source IDs, from primary nearest-neighbor calculations; report duplicate clusters and count. This avoids species-file ingestion order creating false ties. If ≥10% of source rows are excluded as duplicate/invalid, STOP ecological comparison at that locality.
- Require **≥100 physically distinct source nest coordinates for each of ≥2 species** and **≥1000 eligible nearest-neighbour nest centres** in a locality, before fitting the source-label permutation control. A valid locality count in one taxon cannot be added by source imputation.
- Frozen null: **199 independent site-internal permutations** of original species labels across identical fixed surveyed nest coordinates. This preserves each source species total and all overall nest spatial clustering, but **does not preserve species-level group-structured habitat selection or colonial neighbourhoods**; it is a minimal exchangeable-label diagnostic, not a null of interspecific competition or dispersal.
- Fixed `numpy.default_rng(20261026 + 1-based frozen locality order)`. Test observed `P_heterospecific_NN` vs permutation median and p10/p90; define source site-level `segregation_delta = P_heterospecific_NN,nullmedian − P_heterospecific_NN,observed`. Positive implies conspecific neighbour enrichment relative to exchangeable labels on the same source point cloud. Report per-site effect size, not pooled hundreds of thousands of nest points as independent field replicates.
- **No pan-Antarctic inference**: four sites nested in three candidate sub-Antarctic islands, one original campaign, source-visible nest substrate/coverage not independently verified. Scientific novelty is *self-derived, quantitative cross-locality nest geometry*, not proof that interspecific competition creates niche partition, not new historical colonization, not a causal island-distance function, and not independent original source replication of the earlier 2020 ZAVO work.
- If all species form giant physically separate mapped colony regions, the null can produce a trivial positive segregation delta. This must be interpreted as *mapped-scale spatial clustering* only. It does not identify physical habitat suitability, niche breadth, priority effects, territorial exclusion, or species interactions. The test is context, not the manuscript's final mechanism.

## Next source-independent generality gate

For a transferable Antarctic island ecology result, independently acquire *multiple* geographic regions and years with full survey footprints, explicit observation effort and source-stable nest counts, and independently mapped habitat availability (island land continuity `P`, breeding substrate `F`, ice continuity `T`). User's research programme contrasts Antarctica with global physical islands from `zuizui0223/island`; these point patterns alone cannot be statistically pooled with island traits from unrelated plants.
