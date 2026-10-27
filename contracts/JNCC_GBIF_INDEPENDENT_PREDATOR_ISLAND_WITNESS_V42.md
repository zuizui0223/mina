# V42 — Independent GBIF mammal observations: feasibility of UK island predator probability validation

**Status SOURCE-FIRST audit, 2026-10-27.** This follows **observed V40–V41** published-label predictions and cannot be presented as prospective confirmation. Do not retune the source-positive labels, 506-island geographic training domain, or frozen V40 map. This V42 source audit must precede comparing GBIF independent sightings to V40 probability values.

## Question
Are there any **original independently collected, sufficiently precise, recent mammal positive sightings** on uniquely mapped RSPB source islands large enough to evaluate source-label predictor ranking against truly observed positives? Distinguish this from actual ecological occupancy probability, which still cannot be estimated from GBIF presence-only sightings.

## Independent published sources and permissions
- GBIF **Mammal Mapper App Sighting Records**, dataset UUID \`8898e990-9d39-4871-9e6e-d1031c19e24b\`, DOI \`10.15468/mjw32e\`, 2026-09-07 publication, **CC BY 4.0**, Mammal Society/NBN.
- GBIF **National Mammal Atlas Project, online recording**, dataset UUID \`67e2335c-4303-4ee3-9bfe-ecfe65662629\`, DOI \`10.15468/i2eosa\`, 2026-09-07 publication, **CC BY-NC 4.0**, Mammal Society/NBN. Internal research audit only, no raw republishing.
- Both use iRecord / NBN workflows and may contain records from overlapping survey networks. Never count them as taxonomically independent replication and deduplicate shared original occurrence IDs when possible. Both lack complete published **negative survey histories/track effort**, as the app effort GPS routes are stored separately.
- Access the documented public **GBIF GET** endpoints only: \`/dataset/{key}\`, \`/species/match\`, \`/occurrence/search\`. No login, account email, bulk GBIF download job, NBN restricted API bypass, or partner outreach.

## Pre-declared source roster and date window
- Original Mammal Mapper and Mammal Atlas datasets above and no opportunistic additional GBIF datasets.
- **2022-01-01 through 2026-10-27** records, georeferenced, \`occurrenceStatus=PRESENT\`, GBIF no-geospatial-issue flag; compare 2014/2017 Stanbury original source as **historically mismatched**, never assert contemporary occupancy at the 2014 label date.
- Focal taxa \`Neogale/Neovison/Mustela vison\` (American mink), \`Rattus norvegicus\` (brown rat), \`Mus musculus\` (house mouse), \`Felis catus\` (cat). **Cats are NOT proof of feral cat** unless independent source proves free-ranging/unowned status. GBIF scientific name must be taxonomically matched with accepted species and synonym lineage; never lump arbitrary rodent/mustelid spp.
- GEOGRAPHY: UK/Ireland ROI lat 48..63.5, lon −13.5..3.5, original GSHHG v2.3.7 **full (f) L1** shorelines SHA256 \`8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41\`, original RSPB 9,688 \`lowid\` source points, only original **506 islands >10 ha MLWS** for V40 probability layer. Match a record **strictly inside one uniquely identified true small-island physical coastline polygon**, with exactly one corresponding original RSPB source lowid. No spatial nearest centroid, region, postcode, text name, coastal snap or arbitrary radius as verified observation location.
- GBIF record \`coordinateUncertaintyInMeters\` must be finite \`<=250 m\` and \`>0\`; empty/zero/greater is **precision-unverified** (reported separately). A 250 m uncertainty radius may cross coastlines: primary **SOURCE precision** eligible point must be >250 m inside polygon coast, not merely point-in-polygon. Thus uncertainty radius is conservative minimum, not full certainty.
- Source record \`decimalLatitude\`, \`decimalLongitude\` must be numeric within ROI; \`eventDate\` or \`year\` in fixed period. Deduplicate within dataset by \`gbifID\`, across datasets by original \`occurrenceID\` + source survey protocol + species/date/coordinate, flag possible unresolved overlaps, no forced matching of different sightings.

## Exact operational gates
1. **Public API access** and dataset registration/licence confirmed (else SOURCE_ACCESS_HOLD).
2. Retrieve taxon-key metadata and complete public GET occurrence/search pages \`limit<=300\` per dataset×species×period; 100000-record API hard window. Fixed maximum **5,000** records per dataset×focal species (or positive source-bound result); if count>5000, **TOO_MANY_PUBLIC_SEARCH_ROWS_STOP** rather than partial sample masquerading as exhaustive. No invented zeros.
3. Source-only record counts reported per dataset/species, input coordinate / species quality, uncertainty known/unknown, event years and duplicate IDs. Do **not read V40 probability values** in this source feasibility job.
4. If source records are retrievable, apply strict GSHHG physical-island and original RSPB \`lowid\` crosswalk, report **only anonymous aggregate source positive sightings and unique >10ha physical source islands**, without publishing raw sensitive mammal locations.
5. **Comparison-to-V40 gate for each mammal species:** ≥10 unique GBIF source-positive events, ≥5 distinct **strict inside one original RSPB physical island** and ≥2 geographical independent source archipelagos, with all original point uncertainty radius away from shoreline. Otherwise STOP_INDEPENDENT_ISLAND_WITNESS_SUPPORT, not biological absence.
6. Even if gate passes, an enrichment comparison of V40 source-label probability on independent sighting-positive islands vs all 506 source islands is a **positive-only ranking audit**; it does not estimate specificity, absence, true island occupancy, predation pressure or contemporary species mortality. Observation effort and reporting intensity can produce apparent enrichment. No true-occupancy AUC/Brier without observed true negatives.
7. No external island predator effect fitted to JNCC bird counts; V36 H2 remains STOP.

## Deliverable
Original-source identity and exact-source automated audit in \`scripts/audit_jncc_gbif_independent_predator_positive_v42.py\`, synthetic tests, run JSON artifact with dataset DOI/licence, request result counts, taxon resolution and strict GSHHG identification-gate support. If no unique genuinely independent sighting evidence, record a precise source ST0P and leave V40/V41 prediction-only ecological interpretation unchanged. Separate any later enrichment analysis behind its own explicit contract.
