# V24 — An overlooked *official data* download in the AADC Béchervaise RFID record

**12 October 2026, mina PR193.** Data provenance and ecological novelty audit, not a new penguin biological analysis. The scientifically frozen Ecology PR189, Ross tagged-bird source gate PR142 and emperor georeference audit PR195 are not modified.

## Real source breakthrough: publisher labels 5849 a DATASET, 5228 a GUIDE

The [actual Australian Antarctic Data Centre record for AAS_4086 Béchervaise weighbridge](https://data.aad.gov.au/metadata/records/AAS_4086_Weighbridge) contains TWO separate download links. Earlier V20–V23 inspections used the NASA CMR/STAC catalogue, which exposed **only** the technical guide URL. This was incomplete, not evidence of no publisher-original data-download link.

Source-locked [GitHub Action #38220014105](https://github.com/zuizui0223/mina/actions/runs/38220014105) **SUCCESS** retrieved *official public metadata HTML* and reproduced literal anchor labels:

| Publisher document link | Literal original publisher anchor label | Actual remote retrieval |
|---|---|---|
| [AAS_4086 /eds/5228/download](https://data.aad.gov.au/eds/5228/download) | **Download a copy of the technical guide** | HTTP 206 + JS/HTML shell, NOT authenticated PDF binary |
| [AAS_4086 /eds/5849/download](https://data.aad.gov.au/eds/5849/download) | **Download the dataset.** | HTTP 206 + JS/HTML shell, NOT authenticated original RFID data file |
| [AAS_4518 /eds/5516/download](https://data.aad.gov.au/eds/5516/download) | Separate Mac. Robertson Land same-island demographic tag-on-nest resight data | HTTP 206 + JS/HTML shell, NOT authenticated resight archive |

**Interpretation:** The correct *official entry point* for the 2006–2018 weighbridge dataset is **5849**, not 5228. Yet original RFID raw-file contents, member years, publisher binary checksum, actual tag IDs, passage direction codes and timestamp corrections remain **unverified**. The AADC download system may require a normal interactive email/S3 delivery request. No one has supplied a download email, no original data or raw tags have been used, and no browser gate was circumvented.

The previous V20–V23 statement that the AAS_4086 publisher source **does not advertise an actual data download** is withdrawn. Its original binary *availability in our programmatic environment* remains on hold.

## Practical safe intake once the authorized publisher file is in hand

We added `scripts/intake_private_bechervaise_5849_archive_manifest_v24.py`, a **local-only** tool for an original file downloaded legitimately from the publisher; it never fetches from the internet, unzips contents, reads tag rows or prints constituent filenames. It only writes the local ZIP central-directory member-count, safe extension counts, potential season tokens in member filenames, source file bytes and SHA256. ZIP members with path traversal are counted (and never extracted); HTML returned instead of data is reported as HTML rather than interpreted as an animal table. No raw file, file path, individual tag ID or requester credential is committed to public GitHub.

A locally run, source-independent example using a downloaded original *only after publisher access*:

```bash
python scripts/intake_private_bechervaise_5849_archive_manifest_v24.py \
  --publisher-download "/PRIVATE_LOCATION/your_authorized_aadc_download.zip" \
  --out "/PRIVATE_LOCATION/aadc_5849_source_receipt.json"
```

This computes a **local** hash, *not* proof that the bytes match the author's original unless the publisher furnishes an official manifest/checksum. It is a *format/provenance receipt only*; actual RFID crosswalk and year-specific candidate cohorts remain untested. The public CI uses **synthetic ZIPs only**, not any original IDs or animal records.

See `contracts/BECHERVAISE_AADC_5849_RAW_LINK_SOURCE_V24.json`, `scripts/probe_bechervaise_second_5849_official_download_v24.py`, `tests/test_bechervaise_second_5849_official_download_v24.py`, `tests/test_private_bechervaise_5849_archive_manifest_v24.py`, and `.github/workflows/bechervaise-aadc-second-data-url-v24.yml`.

## Science novelty gate tightened by directly relevant 2026 data

[Dugger et al. (2026), *Frontiers in Ecology and Evolution*, doi:10.3389/fevo.2026.1868960](https://doi.org/10.3389/fevo.2026.1868960) already separately estimated **prebreeder movement while staying prebreeder** (often called prospecting) and **prebreeder-to-new-colony breeder recruitment** at Royds, Bird and Crozier on Ross Island, from 25 years of marked birds (1996–2020).

- Peak **Royds→Bird prospecting** at ages **5–7: ~8–12%** in their model. Most other intercolony prospecting transitions were below 3%.
- Recruitment by switching colony while becoming a breeder was typically **<0.10%** as a separate state-transition probability. These percentages do **NOT** form a fraction, since the prospecting and recruitment estimates represent *different conditioned Markov transitions*.
- Movement once already breeding was **<0.20%**. Breeder sabbatical rates about **20–30%** depending on age. The lowest age-specific recruitment rates were Royds; Crozier highest, with Bird having highest early-life survival and more recruits from a hypothetical natal cohort.

Thus the broad result **"some penguins visit alternative colony locations without switching their first breeding colony"** is already in the 2026 literature. We must not present it as a new discovery, nor infer the observed *cause* from the two distinct transition probabilities. The 2026 paper largely quantified the ecological stages previously sought in PR193; the remaining truly novel question must be a **specific causal driver of low transition from prospecting to nesting**, in independent affected/control settings with dated access, density/quality or other physical cue changes and own-egg outcomes.

## Scientific status

**V24 progress is source access provenance, not biological causality.**

- VERIFIED: exact official AADC weighbridge **dataset link** (5849) versus technical guide (5228); original metadata anchor text source-checked in CI.
- HOLD: publisher-original binary download, tag schema and RFID normalization, union with nest resight original IDs, verified own first egg, a proper unbred-at-risk denominator, and an independent between-island natural contrast.
- PRIOR ART: 2019 same-season tagged breeder/nonbreeder comparison; 2026 Ross prospecting and switching-colony first recruitment model; 1970 nest-neighborhood prospecting, and broader seabird competition-for-habitat.
- PROHIBITED: doubling RFID feeding crossings as new immigrants, assuming nest-scan absence is confirmed no egg, inferring a visited micro-patch from a multi-subcolony gateway, or claiming a causal Antarctic island law from a new AADC URL.

Study custodian guidance: [AADC source record](https://data.aad.gov.au/metadata/records/AAS_4086_Weighbridge) asks prospective users to contact **Louise Emmerson** and cautions that raw data are unprocessed and may need specialised normalization. The V22 inquiry draft `docs/BECHERVAISE_CUSTODIAN_DATA_REQUEST_DRAFT_V22.md` remains **UNSENT**.

**V24 decision: OFFICIAL AADC DATASET LINK VERIFIED; ORIGINAL RFID INDIVIDUAL TRANSITIONS NOT ACCESSIBLE IN THIS RUN; NO NEW CAUSAL RESULT.** Ecology PR189, source-data PR142 and emperor PR195 remain scientifically unchanged.
