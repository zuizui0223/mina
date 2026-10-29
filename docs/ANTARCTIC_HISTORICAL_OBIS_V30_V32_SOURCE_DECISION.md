# Historical Antarctic seabird source — V30–V32 final evidence gate

**Verified 2026-10-26.** This is first-party public archive data/source analysis, NOT a published-paper effect-size synthesis or a new confirmatory ecological mechanism. PR #189 remains frozen. The original-data priority is Antarctic ice/land/nest island biogeography; this source's limitations cannot be bypassed by treating names or gazetteer points as actual island-level independent breeding sites.

## Original OBIS source and actual independent facts

Eric Woehler (2008) historical Antarctic breeding-bird records, first-party
[IPT/OBIS Darwin Core Archive v1.0](https://ipt.obis.org/nonode/resource?r=iasb), October 2018 CC BY 4.0. Original archive publisher SHA256
`c17670be07fed76492a30a59893d059f4ccb11d54f2f73bceeaf007c19e311d5`.

- **2,787 actual original occurrence records**, including **12 penguin and flying-seabird taxon labels**; the dataset titled penguin colony counts actually includes `Macronectes`, `Pagodroma`, `Thalassoica`.
- **2,377** original records contain numeric `individualCount`, 23 literally equal zero; 410 lack a numeric count. Penguin source guild: 2,162 records, 1,959 numeric; flying petrel guild: 625 records, 418 numeric.
- All numeric counts in original IPT core have **blank `lifeStage`**, blank `dynamicProperties`, and no `associatedReferences`, `bibliographicCitation` or `recordedBy`; original `basisOfRecord` uniformly HumanObservation. Some `occurrenceRemarks` mention named personal communications or vaguely say Breeding/Possibly breeding. Original `coordinatePrecision` uniformly reports literal **500.0**; its effective error unit must NOT be asserted to be 500 metres without upstream source documentation. First-party AADC metadata explicitly warns that some coordinates were generated from locality names using the Antarctic Composite Gazetteer.
- Original IPT year fields include records through **1998**, even though resource title/metadata say through 1996. This is a source vintage/metadata mismatch, NOT additional validated 1997–98 field census years.
- Exact original `waterBody, stateProvince, county, locality, scientificName, lifeStage, basisOfRecord` grouping yielded **238 textual repeated-locality/taxon candidate groups with at least 2 distinct reported years** and **94 groups with at least 3 reported years**, but multiple source records also occur at the *same original locality and year*. No original method-specific unique observation/census identifier is established.

**Scientific conclusion:** There is a genuine accessible historical, multi-taxon database and repeat-event *candidate* population. However **238 candidate trajectories are NOT 238 stage-comparable nest census panels**, 23 source numeric zeros are not verified surveyed non-detections, gazetteer coordinates are not original colony/nest GPS, and rehosted Woehler records may repeat observations subsequently entered into MAPPPD. Consequently, **no independent island occupancy/recolonisation, abundance growth, ice/land isolation or flight-guild causal model is currently identifiable**. Do not publish this as 238 independent population trajectories.

Reproducible actual source workflows:
- [V30 original Darwin Core field/count audit — SUCCESS](https://github.com/zuizui0223/mina/actions/runs/40320340756); `results/OBIS_HISTORICAL_PENGUIN_ORIGINAL_SOURCE_V30.json`.
- [V31 original count-stage and exact text-site repeat gate — SUCCESS](https://github.com/zuizui0223/mina/actions/runs/40321748098); `results/OBIS_HISTORICAL_SOURCE_LOCALITY_REPEATS_V31.json`.
- Independent original-source [V31 12-taxon / flightless-versus-flying guild QA](https://github.com/zuizui0223/mina/actions/runs/40285269246); `results/OBIS_ORIGINAL_PENGUIN_FLYING_SOURCE_GRAIN_V31.json` — same underlying OBIS 2,787 records, **not independent replication**.

## Actual original AADC source workbook could rescue count-stage identifiability

The archived [Australian Research Data metadata for AADC `FAUNA_PENGUIN_COLONY`](https://researchdata.edu.au/a-census-penguin-antarctic-region/700932) lists the upstream **untouched original and AADC-corrected Excel spreadsheets**, including actual `Type and accuracy of count`, `Number of Pairs`, `SCAR Number`, original references and survey date. Explicit stage coding is `N` nest, `A` adult, `C` chick, `B` unspecified bird. Accuracy coding `1` through `5` ranges from individually observed counts (about ±5%) to order-of-magnitude estimates. **The original and corrected Excel copies are different versions of the SAME field records**, not independently counted observations; corrected names may themselves be inaccurate.

Official historic AADC metadata download `file_id=2216`:
- Original documented `https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216`;
- First-party 301 redirect to `http://data.aad.gov.au/dataset/file/2216`;
- Safely upgrading only that exact disclosed first-party target to HTTPS reaches `https://data.aad.gov.au/dataset/file/2216`, but returns **HTTP 200, text/html, 1,211 bytes, Vue JavaScript app shell**, **not the original Excel**.
- Neither original nor modified workbook has been recovered from this anonymous HTTP route; source original stage/accuracy row values are NOT known. Do not keep trying the same SPA routes or assume the bytes contain a usable spreadsheet.

Successful publisher-receipted diagnostics: [V32 official original source access attempt](https://github.com/zuizui0223/mina/actions/runs/40323091140); `results/AADC_WOEHLER_ORIGINAL_COUNT_STAGE_DOWNLOAD_V32.json`.

## One necessary external source dependency (no email was sent)

Obtain original unmodified Excel for AADC dataset **FAUNA_PENGUIN_COLONY**, original historical asset ID **2216**, preserving original SCAR Number, Species, exact region/locality, survey year, number of pairs, `Type and accuracy of count`, references and remarks. AADC self-service data request may require the user's contact email; this project has **not** supplied an email or accessed any private URL.

Once authorized original workbooks are available, run a new **source-first stage/quality linkage** via original SCAR Number and literal original species/year/site identifier; verify before interpreting any relocated original coordinates. Only directly observed nest-stage counts with documented comparable effort and independent original field citations can form repeated population histories. Other source field records remain as source-richness/geography references, not numeric demographic replicates.

**Current scientific stop:** Historical IPT source useful as a reproducible 12-taxon original registry, but the missing stage/accuracy and source lineage prevent new causal Antarctic island population inference. Do not retune a negative island model or transform 500.0 coordinatePrecision into confident metre-scale nest locations.
