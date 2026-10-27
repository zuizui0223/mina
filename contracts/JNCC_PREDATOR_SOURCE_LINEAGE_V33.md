# JNCC V33 — Stanbury (2017) UK-island predator source lineage and niche-identifiability gate

**State: SOURCE-FIRST AUDIT; post-V30 follow-up exploratory, no predator ecology result**  
**Branch:** research/jncc-v32-mechanism-contract (PR #201)  
**Prepared:** 2026-10-27

## Actually identifiable public original sources

1. RSPB's published UK Islands feature service, a 2014 OS MasterMap-derived **point** dataset with exactly **9,688 original island records**, official ArcGIS item \`8cf249483ca540c792aee44c3029cb0b\`, spatial reference British National Grid EPSG:27700. Public REST source:
   https://services1.arcgis.com/h1C9f6qsGKmqXsVs/arcgis/rest/services/Islands_database/FeatureServer/0
   Attributes directly verified before ecological outcomes: \`lowid\`, island name, high-tide/low-tide areas \`mhwsarea_h\`/\`mlwsarea_h\` (hectares), 2014 human population, ferry and grouping metadata. **The feature layer contains NO field indicating predator presence or survey effort.** Geographic island point ≠ original island polygon or nest-site GPS.
2. Stanbury et al. (2017), DOI 10.1007/s10344-017-1084-7, publisher's publicly linked supplemental files **ESM 1 (.xlsx, 15.3 kB)** and **ESM 5 (.xlsx, 1.55 MB)**:
   - https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs10344-017-1084-7/MediaObjects/10344_2017_1084_MOESM1_ESM.xlsx
   - https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs10344-017-1084-7/MediaObjects/10344_2017_1084_MOESM5_ESM.xlsx
   The RSPB publisher metadata explicitly says its \`lowid\` permits a join to the article's *non-native species supplemental data*. **Actual workbook headers, species coding, date/effort fields and lowid coverage MUST be audited before claiming an island predator presence–absence dataset.** The first-party files may be blocked for automated access; an unavailable download is \`HOLD\`, not biological zero.
3. JNCC's authentic census comparison (1998–2005 vs 2015–2021) remains **frozen V30**; known source-derived concentration across 17 taxa is not a new prospective finding. **Do not import or open any JNCC bird count cells in V33.**
4. NBN Atlas public occurrence-search web service and downloadable records are an independent possible supplementary predictor/evidence stream. Public species records may be biased toward monitored/accessed islands and cannot certify absence without effort. Ordinary web/API queries may require access/authentication (the current occurrence API returned HTTP 403 during source check), and NBN documents state direct full record downloads require login and licence compliance. **No authentication bypass or hidden data use.**
5. Biosecurity for LIFE and NatureScot sources indicate differing swimming ability, introduced status and nesting guild vulnerability, but statements such as mink can cross water gaps do **not** prove an island was predator-free; ferry/cargo introductions break any deterministic swimming-distance rule. Historical eradication date is an intervention, not time-invariant habitat suitability.
6. CEFA/UK government marine assessment summarises 2017 survey **confirmed or probable** predator presence on islands >10 hectares: mink 23%, brown rat 21%, feral/domestic cat 17%. These percentages are only aggregate external sanity checks. They are not values to impute into individual missing islands.

## Mechanistic model scope

Two distinct processes must never be conflated:

- **Predator occupancy / colonization niche**, \`P(predator p present on physical island i in year t | area, water gap, human access, climate/habitat, region, propagule supply)\`. Train/validate **only if an independent occurrence status with provenance/date and true survey denominator is available**. A background/unvisited island is NOT a negative/pseudoabsence. Consider multi-species occupancy and detection with repeated visits only if original effort data exist.
- **Predator–nest encounter and prey vulnerability**, based on whether a verified predator can reach the original nestable habitat (ground / burrow / cliff / crevice) and an independently coded species×predator susceptibility. Neither cliff coordinates from JNCC site points nor a general breeding-guild name alone establishes measured nest accessibility.
- **Seabird compositional response**: prespecified positive predator-risk effect on within-network local *loss of share* only when an original JNCC parent contains **at least two accurately georeferenced independent landmasses with variation in verified predator status or predicted risk**, and remains subject to the V32 mixed-island cohort minimum. With only within-one-island panels, compare between-network differences **descriptively without directional refugee/transfer claims**. No movement, mortality, or predator-competition conclusion from two censuses.

Proposed future risk feature for separate validation, not now estimated:

\`risk(i,s,t) = 1 - product_p [1 - occupancy_probability(i,p,t) * physical_nest_accessibility(i,p,s,t) * susceptibility(s,p)]\`

This bounded multiplicative exposure index is a **potential risk proxy**, not measured kills or independent predator effects. It requires independent calibration for all three terms, a time window relevant to each JNCC census, and uncertainty propagation. If only first-party predator-status labels are available, use categorical status and stop before quantitative risk modelling.

## Frozen source-only V33 stopping/continuation gates

1. Service metadata must have \`lowid\`, source provenance and area/population fields; return count must remain exactly 9,688, with unique finite integer \`lowid\` and paginated deterministic FID retrieval. The source geometry is a **point**, so model any join to physical-island GSHHG polygon at an independent geographic QA step, not by text or nearest-neighbour alone.
2. Publisher supplemental original XLSX SHA256 recorded with bounded (6 MB per workbook) HTTPS download, ZIP/XML validation and non-executable extraction. Inspect first source rows and **literal categorical statuses** without mapping \`0\` or blank to confirmed predator absence.
3. A *candidate* exact \`lowid\` key overlap must be demonstrated using the publisher XLSX and RSPB feature service; duplicates, unknown keys, unmatched cells and possible alternate island ID namespaces cause a source HOLD until resolved. Do not choose a sheet based on outcome fit.
4. Map original predator taxa, surveyed presence/absence/probable/unknown/eradicated/reintroduced to explicit dated codes ONLY after the source legend/metadata explains the labels. Island inventory completeness and the 2014 census frame must be checked; 2017 species labels cannot be substituted as 1998 or 2021 observations.
5. **No post-outcome JNCC effects fitted until the separate original observation, geography, and dated-status sample gates pass.** Only then freeze a predator-specific niche/occupancy model with region-held-out predictive performance against independent observation labels. Full species-level ecological comparisons remain explicitly exploratory because the global V30 pattern was already known.
6. If additional predator record access requires NBN/RSPB authentication or a publisher file request, record exact blocked source and preserve the legitimate request path. Never claim data obtained or user consent submitted. H2 predator-specific causal interpretation stays \`NOT IDENTIFIED\` without time-correct, effort-calibrated status.

## Reproduction

- Source-only script: \`scripts/audit_jncc_predator_island_source_v33.py\`
- Synthetic tests: \`tests/test_jncc_predator_island_source_v33.py\`
- Workflow: \`.github/workflows/seabird-jncc-predator-source-v33.yml\`
- Source-only result: GitHub Actions artifact \`JNCC_UK_PREDATOR_ISLAND_FIRST_PARTY_SOURCE_V33.json\` (not a JNCC biological result).
- V32 main hypotheses contract: \`contracts/JNCC_COMPETING_MECHANISMS_GSHHG_V32_DRAFT.md\`

**Scientific distinction:** primary geographic plus primary predator records can improve **predictor measurement**; they do not themselves demonstrate a new effect on seabird breeding networks. Stanbury 2017's island assessment may use Seabird 2000 as conservation prioritisation input, so freeze record lineage and avoid describing shared bird source material as independent outcome replication.
