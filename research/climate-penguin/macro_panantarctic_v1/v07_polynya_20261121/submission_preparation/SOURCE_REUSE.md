# v0.7 source reuse and availability audit

Audit date: 21 November 2026. Inspected source commit `7867969c640e9e1fce627ed0e172e549fb6b4f0f`; no canonical manuscript or provider data were edited. This is a record of observed provider statements and package contents, not an assertion that public accessibility alone establishes reuse rights.

## Findings and completion status

1. **The two central deposited datasets have verified CC BY 4.0 metadata:** Youngflesh Zenodo 17409948 and DEEP-AA Zenodo 13358042. Their attribution, licence links and transformations are recorded in SOURCE_NOTICES.md and SOURCE_REUSE_REGISTER.json. The version-specific Zenodo/API records, rather than the journal article's licence, establish this finding.
2. **Add the Copernicus product DOI and explicit acknowledgement.** The retrieved Marine licence permits creation/distribution of derivatives and original redistribution (Annex 2.2), with credit/DOI and traceability conditions (2.4, 2.6). The prior v0.7 manuscript omitted product DOI `10.48670/moi-00021` and the service acknowledgement. Both were supplied to the manuscript editor for this submission-preparation revision; the exact notices are preserved in SOURCE_NOTICES.md.
3. **Distinguish public code from licensed code.** GitHub reports this repository as public, with `license: null`; its complete recursive tree contains no LICENSE/COPYING/COPYRIGHT/NOTICE-named file. Do not describe the project scripts as open-source licensed until the rights holder selects a licence. No licence has been assigned in this audit.
4. **Keep an explicit limitation for retired G02202 v4.** Its official v4 page and DIF metadata verify required attribution, version and DOI. The DIF marks v4 retired and points prior/planned use to the citation policy; the DataCite rights array is empty. This audit did not establish a version-specific redistribution licence. Retain the archived historical version and provenance; do not replace its values with the current product.

## Source and packaging matrix

| Source used | Provider statement verified | What is in this review package | Record / required action |
|---|---|---|---|
| Youngflesh, Casey, *Data for Youngflesh et al. Submitted*, Zenodo `10.5281/zenodo.17409948` | DataCite registration explicitly lists `cc-by-4.0`, with the CC BY 4.0 legalcode URL. The Zenodo API timed out, but the authoritative DOI metadata succeeded. | Derived seasonal optical proxies, image/pixel counts, calibration-ensemble coefficients and CV summaries. No original reflectance RDS, raw guano spectra or individual laboratory isotope observations. | Add dataset creator/title/DOI and licence link; state that this project aggregated selected image days, reconstructed proxies and recalibrated. Retain the separate full Youngflesh et al. 2026 article citation. |
| Lin, Nakayama, Liang, Huang, Chen & Yang, DEEP-AA v1.1.0-2023, `10.5281/zenodo.13358042` | Zenodo API explicitly lists `license.id = cc-by-4.0`. It lists the exact recommended `SIC60_6.25km_20d.zip` MD5 `f3f958389cc5e67ac1c4e3a6ee164318`. | Source-derived colony-buffer daily, monthly and winter fractions; source-site geometry; no original daily grid archive. | Add creator/title/version/DOI/licence and transformation description. Lin's **article** has different CC BY-NC-ND terms; those should not be copied onto the deposited dataset. |
| Meier, Fetterer, Windnagel & Stewart, NOAA/NSIDC G02202 v4, `10.7265/efmz-2t65` | Official v4 landing page requires data citation. Official DIF `G02202.004` confirms version/DOI and retirement; no version-specific open licence found, and DataCite `rightsList` is empty. | Derived November–February 150-km sea-ice concentration column in the 860/358 joined tables. No original NSIDC grids. | Existing paper citation is present; keep version, derived subset and historical provenance. Record licence as **not specified in retrieved v4 metadata**, rather than inventing CC0 from current v5/v6 products. |
| Copernicus GLORYS12V1 release 202311, product `GLOBAL_MULTIYEAR_PHY_001_030`, `10.48670/moi-00021` | Current Marine licence Annex 2.2 permits derivative creation/distribution and original redistribution. Annex 2.4 requires service origin and product DOI; 2.6 requires traceability records. | Seasonal salinity and potential-temperature columns and source grid-cell indices in joined tables. No original global grids. | Add the product citation and publication/derivative credit below; keep provider terms linked. Do not apply the ECMWF/C3S licence to this Marine product. |
| Natural Earth 1:110m land | Official terms explicitly put all versions of its raster/vector map data in the public domain. | Raw generalized `ne_110m_land.geojson` and derived Antarctic EPSG:3031 display cache. | Already correctly attributed/licensed in `source_manifest.json` and README. Land is display context only. |
| BAS Signy stomach contents v1.0, Dunn et al. 2022, `10.5285/eb421e6d-b93b-4174-904b-9a7b0b401403` | Exact BAS dataset page says no access restrictions and Open Government Licence v3. | Narrative and numerical check summaries in Supplement S5, but no stomach-content source table or executable Signy reanalysis in the compact v0.7 package. | Add a formal data citation to the supplement/source register if needed; keep the OGL link. Do not call this compact bundle a complete reproduction of the Signy analysis. |
| USAP-DC feather dataset `10.15784/602094`, Michelson et al. 2026, v1 | Exact dataset page explicitly specifies CC BY 4.0. | Summary of matching audit only; no 108-row feather table in the four compact ZIPs. | Cite data DOI, creator names and licence in the source register. References list gives article DOI `10.3354/meps15233`; prose description has an extra trailing `1`, so use the linked reference DOI if citing the paper. |
| USAP-DC chick-bone dataset `10.15784/601913`, Reaves, Powers & Emslie 2025, v1 | Exact dataset page explicitly specifies CC BY 4.0. | Literature context; no chick-bone source table in compact package. | Bibliographic/interpretive attribution only. A separate source-data redistribution statement is unnecessary unless its table is later added. |

CC BY 4.0 allows sharing/adaptation subject to credit, licence link and indication of modifications; it does not require asking the depositor again for ordinary covered reuse. This audit did not check every upstream source embedded in the two deposits for separately marked exclusions. Preserve any supplied source notices; do not claim a new blanket licence over all third-party inputs.

## Exact inventory observed

The package contains four compact project-generated ZIPs with **24 members total**. None contains a provider LICENSE/NOTICE file.

- `polynya_physical.zip`: 7 members, including 134,334 derived daily exposure rows, 4,390 monthly rows, 878 winter rows, a source-aligned 860-row panel, 176 radius-by-site geometry rows and 11 regional summaries. Both 25-km QA and 100-km measures are present; manuscript inference remains the frozen 100-km design.
- `isotope860.zip`: 3 members: joined 860-row proxy/environment table, salinity verdict and 13-region summaries.
- `polynya_main439.zip`: 3 members: main verdict, 291-row forward-prediction table and 22 leave-region/model rows.
- `author_R1000.zip`: 11 members: 1,000-iteration L4/L5 coefficient tables, 1,000-iteration CV summaries, receipts, 860 reconstructed seasonal responses and leave-region-out results. Despite their filenames, `*_original103_lab_cv.csv` contain **iteration summaries, not individual laboratory samples**.

Additional source files include the 358-row temporal join, small figure extracts, derived projection caches and raw public-domain Natural Earth land. Existing manuscript/README language correctly limits offline reproduction to the supplied frozen 439/358 analyses and five figures. The side checks in S5/S6 still rely on the linked historical repository workflows and their original sources. Do not broaden the claim to the full satellite ingestion chain or every supplementary diagnostic.

## Attribution text and dataset references

`SOURCE_NOTICES.md` contains source-specific credits, licence URLs, transformation descriptions and the verified dataset citations. Source dataset publication years are distinct from article years: the Youngflesh deposit is **2025**, although the associated journal article is **2026**. The deposit's registered title is *Data for Youngflesh et al. Submitted* and its only registered dataset creator is Casey Youngflesh; those fields are retained rather than silently rewritten using the later paper's metadata.

The public repository source at the audited commit is accessible, but neither this register nor a third-party CC BY notice assigns a licence to project-created scripts. A code-licence choice remains an author/rights-holder item in the submission preparation form. No blanket archival licence has been imposed.

## Open items with exact reasons

| Item | Status and reason | Smallest concrete next step |
|---|---|---|
| Provider credits and transformations | Recorded in this preparation packet | Retain SOURCE_NOTICES.md and SOURCE_REUSE_REGISTER.json alongside the derived tables. The editor has the verified Copernicus product citation and credit. |
| Project-created code licence | Author decision; repository licence absent | Record a proposed scope and ask the rights holder to choose/confirm the intended licence when collecting author metadata. Do not silently add MIT/CC BY to the full repository. |
| Historical NSIDC v4 redistribution label | Not established by retrieved version-specific records | Preserve exact data citation and register the absence; if a blanket archival data licence is desired, consult original downloaded metadata/terms or provider guidance before assigning it. Do not infer terms from later versions. |
| Full offline reproduction of S5/S6 | Outside compact bundle's implemented claim | Keep the current limited claim and link historical workflows explicitly; add those inputs only if a full supplementary audit is requested. |
| Public archival DOI | Not assigned | Prepare the deposit description and source notices; publishing a DOI is a separate author-authorized action. |

## Primary evidence and retrieval record

The compact, machine-readable record is `evidence/provider_metadata_receipt.json`. It preserves the exact source-response hashes and extracted fields listed below. Original response files were inspected locally; full provider HTML is not republished in this packet:

- Youngflesh DataCite: https://api.datacite.org/dois/10.5281/zenodo.17409948 — `rightsList[0].rightsIdentifier = cc-by-4.0`; raw SHA256 `7b4c328aa44e615af2b6f4dfe767d5f0ff2d33d0117194fb9e7c6bbbd9d6f40e`.
- DEEP-AA Zenodo: https://zenodo.org/api/records/13358042 — `metadata.license.id = cc-by-4.0`; raw SHA256 `314b97a2a21ce58472fa0ae880a0cac5a1b9f4d4663a1f7c7539ebd9c3f559a3`.
- Copernicus Marine licence: https://marine.copernicus.eu/user-corner/service-commitments-and-licence — official English HTML retrieved directly, SHA256 `c85529261de591a4865e9627149b6ae7f3fc16efe2cf856463c889df3a1d530d`; relevant sections Annex 2.2, 2.4, 2.6. Web parser returned 403, which did not prevent the direct public-page retrieval.
- NSIDC exact v4 DIF, linked from its official page: https://nsidc.org/api/dataset/metadata/v2/oai?verb=GetRecord&metadataPrefix=dif&identifier=G02202.004 — SHA256 `3cf69b8dedb65bef06b640ccce397fa8c4d7692bb3fcee31a247d4297f97ec78`.
- NSIDC DataCite: https://api.datacite.org/dois/10.7265/efmz-2t65 — empty `rightsList`, SHA256 `6778259eab253d95c3596826b727d2e8c633122c2da3b3250518922d9f453d9c`.

Additional primary pages consulted:

- Copernicus current citation guidance, updated 20 October 2026: https://help.marine.copernicus.eu/en/articles/4444611-citing-copernicus-marine-products-and-services.
- GLORYS official product: https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description.
- NSIDC v4: https://nsidc.org/data/g02202/versions/4.
- NSIDC citation policy: https://nsidc.org/about/data-use-and-copyright.
- Natural Earth terms: https://www.naturalearthdata.com/about/terms-of-use/.
- Exact BAS Signy dataset: https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01549.
- Exact feather dataset: https://www.usap-dc.org/view/dataset/602094.
- Exact chick-bone dataset: https://www.usap-dc.org/view/dataset/601913.
- CC BY 4.0 deed: https://creativecommons.org/licenses/by/4.0/.

No provider was contacted, new licence assigned, or DOI published by this audit. It prepares source attribution for the existing derived-data review materials.
