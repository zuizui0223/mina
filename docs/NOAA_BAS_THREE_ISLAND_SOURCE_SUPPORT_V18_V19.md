# V18–V19 — Genuine NOAA two-island × BAS Signy comparative season support

Date 2026-10-20. Original publisher sources have been downloaded and source-SHA verified; original metric magnitudes have **not** been opened or fitted. [V18 primary-source audit](https://github.com/zuizui0223/mina/actions/runs/39404715461) and [V19 frozen season support](https://github.com/zuizui0223/mina/actions/runs/39405220452) both passed synthetic tests and source retrieval. The new information is availability of a **three-physical-island temporally overlapping observed gentoo panel**, not a new Antarctic island ecological mechanism.

## Distinct source systems and units
- **NOAA US-AML R** accession 0185113 DOI 10.25921/58yq-7g68: verified original 9,861 byte workbook SHA256 a57370f82adf82b53da11ce5d85dada1ae3f3750ef246312b59d0f168763eef4. Publisher XLSX has exact sheet 'census data', header YEAR, Copa_Adelie, Copa_Gentoo, Copa_Chinstrap, CapeShirreff_Chinstrap, CapeShirreff_Gentoo, **38 original austral-season rows with start years 1977–2014**. Copacabana = monitored breeding location on **King George Island**, Cape Shirreff = monitored breeding location on **Livingston Island**, not independent whole-island censuses.
- **BAS UK Polar Data Centre** Signy Island gentoo DOI 10.5285/883c6b40-024e-41e8-9c3e-2668a44b5751: verified original 4,851 byte CSV SHA256 53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b. **43 source rows**, stage-separated breeding pairs/eggs/chicks/fledglings, and source-season labels. This source concerns monitored Signy colonies, not a complete independent census of every suitable breeding patch.
- NOAA in its [original metadata](https://www.fisheries.noaa.gov/inport/item/55435) explicitly says **blank census fields mean no data or census errors**, not zero animals. Its original field dictionary ([InPort 55436](https://www.fisheries.noaa.gov/inport/item/55436)) describes generic 'species census count' and does not establish that the quantity matches BAS 'TOTAL_NUMBER_OF_PAIRS'. NOAA calendar year column denotes austral season.
- BAS's annual pair and breeding-stage data are collected under CEMP protocol from 1996/97 onward, but effort, completeness, and breeding-stage definitions are NOT safely identical to the NOAA census field. A count-vs-pair comparison is not yet justified.

## V18 original structural findings
- NOAA 5 series raw nonblank census cells: Copacabana Adélie **32/38**, gentoo **34/38**, chinstrap **22/38**; Cape Shirreff chinstrap **18/38**, gentoo **18/38**. These 124 source cells are annual observations, not 124 independent island replicates.
- BAS gentoo CSV has 43 original records and distinct source reproductive-stage columns. Source display includes one empty trailing heading and text-filled placeholders; **nonblank does not establish numeric-valid**. Consequently V19 adds a purely lexical numeric-validity screen, counting 0 as a possible genuine recorded number but not converting/matching actual values. No numerical biological count was read or reported at this stage.

## V19 exact original-season three-island availability
Frozen before inspecting magnitudes, V19 verifies the two original source SHA256s and exact austral season codes with no imputation of absent years. NOAA original start years **1977–2014**, BAS parsed valid labels cover **1978–2020** (42 distinct valid season starts of 43 rows, and 40 numeric-lexical-valid 'total pairs' entries). Exactly **one original BAS season label '1998-8895' is invalid** and explicitly excluded rather than reinterpreted. No duplicate year groups in the parsed sets.

| Source or combination | Support |
|---|---:|
| NOAA Copacabana original gentoo usable annual count entries | **34** |
| NOAA Cape Shirreff original gentoo usable annual count entries | **18** |
| BAS Signy original gentoo total-pairs usable annual entries | **40** |
| **All 3 sources in the same austral breeding start year** | **16 seasons** |
| **Adjacent breeding-start years with all 3 sources present** | **14 year-pair windows** |
| Within Copacabana, all 3 Pygoscelis census series usable same year | **22 seasons** |
| Within Cape Shirreff, chinstrap + gentoo series usable same year | **18 seasons** |

The 16 shared original start years are 1998–2009, 2011–2014 (2010 not three-way eligible). Thus the preregistered >=10 common years / >=8 adjacent-year windows **passes** at the *source-coverage* level. A two-island NOAA monitoring series and BAS single-island breeding-stage series make a **three-island** comparative panel, not a circumpolar macroecological dataset.

**V19 scientific decision: HOLD_NOAA_BAS_CENSUS_STAGE_DEFINITION_AND_INDEPENDENT_ENVIRONMENT.** Future biological model fitting needs a validated common unit or independently documented consistent transformation, and a temporally measured independent habitat/marine covariate. A positive correlation among three existing breeding populations would not itself identify island area, access bottlenecks, interspecific competition or environmental mechanisms and is likely prior-art-compatible. Do not rescue V14–V17 or claim novel species ecodynamics from these metadata numbers.

### Original sources and durable numerical receipts
- [NOAA archival spreadsheet and metadata](https://www.ncei.noaa.gov/archive/accession/0185113)
- [BAS Signy gentoo original data record](https://doi.org/10.5285/883c6b40-024e-41e8-9c3e-2668a44b5751)
- [V18 source-only JSON](../results/NOAA_BAS_ISLAND_STAGE_SOURCE_QA_V18.json)
- [V19 same-year original-source JSON](../results/NOAA_BAS_THREE_ISLAND_SEASON_SUPPORT_V19.json)
