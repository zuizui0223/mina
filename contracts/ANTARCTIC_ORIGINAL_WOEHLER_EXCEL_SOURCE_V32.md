# V32 original historical Antarctic penguin census Excel source-link recovery

**2026-10-26, publisher-source recovery gate after original V30/V31 OBIS field-semantic audit.** The source quality issue is measurable: the published 2,787-row OBIS Darwin Core archive includes `individualCount` but **its original `lifeStage`/citation fields are empty**, so the 2,354 strictly positive counts mix unknown N (nest)/C (chick)/A (adult)/B (unidentified bird) and survey accuracy levels.

The first-party published metadata record for `FAUNA_PENGUIN_COLONY` is reproduced at [Australian Research Data Commons](https://researchdata.edu.au/a-census-penguin-antarctic-region/700932). It explicitly lists original source Excel columns:
SCAR Number, Species, Region, Locality, Longitude, Latitude, Number of Colonies, Number of Pairs, Type and accuracy of count, Data Date, References, Remarks. The declared type-and-accuracy code is N/C/A/B plus 1–5 original survey quality; the **unmodified Excel must be preferred to the publisher's corrected spreadsheet because AADC warns some corrected localities may be wrong**.

The exact first-party link from that metadata is
`http://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216`.
Canonical HTTPS version to probe:
`https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216`.
This is a real publisher metadata link, **NOT yet confirmed downloadable**, and not the generic `/eds/<id>/download` SPA routes found inaccessible in V29.

## Source-only gate

- Issue one bounded (first 128 KiB only) HTTPS GET to this exact source file ID. Record final source domain, content type/disposition, declared file size, binary signature and whether the body is an HTML/JavaScript SPA fallback.
- If XLS/XLSX/ZIP is accessible and not authentication-gated, separate V33 will retrieve full original object with hash and inspection of original source spreadsheet sheet names/record columns, then link direct census rows to the OBIS DWCA observation IDs only when original SCAR identifier + locality + taxon + date + count can be matched unambiguously. **Never derive source count accuracy from OBIS count magnitude or guess stage from penguin species**.
- If HTML/SPA, label SOURCE_DOWNLOAD_HOLD, not zero original nests. Do not bypass email/S3 access controls, invent mirrors or populate synthetic original quality codes.
- Original 207 negative count sentinels in four flying-bird taxa, 23 literal zeros and 200 count missing remain NOT species absence, nor true breeding pairs. Original 'coordinatePrecision=500.0' has unresolved units and all original dated eventDate values are January 1 placeholders; do not treat these as GPS nest/field dates.
- No new ecological effects/models are authorized by recovery of a catalogue or original source ZIP alone. A genuinely comparable source cohort requires direct original stage N, original quality rank ≤2, exact physical island and site identities, observed original survey year, and documented duplicate field/citation lineage, before a transferable pan-Antarctic penguin island effect.

This is work on an independent original public raw database, NOT an integration of other papers' model coefficients. Frozen Ecology PR #189 and already inspected AADC/SSI explanatory model gates remain separate.
