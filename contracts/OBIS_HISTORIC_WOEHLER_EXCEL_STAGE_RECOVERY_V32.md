# V32 first-party ORIGINAL Excel recovery for Woehler Antarctic seabird census

**2026-10-26 — official historical original ZIP/Excel access check, source-first.** OBIS IPT version 1.0 2,787 records and 2,377 numeric individualCount records have been verified. Original source has 238 exact literal locality × species × stage multiyear candidates, but **all 2,377 counted OBIS records have a blank lifeStage**, original `coordinatePrecision` uniformly 500.0 (units unverified), no recordedBy/citation, and multiple same-site/year records. Those cannot be treated as comparable annual breeding-pair census events.

## The missing, genuinely original source columns

The Australian Antarctic Division's **first-party 2008 metadata** explicitly documents that the original *Excel* table contains `Type and accuracy of count`, `Number of Pairs`, `SCAR Number`, `Locality`, `Data Date`, `References`, and `Remarks`. The codes are:
- Count stage: `N` nests, `A` adult, `C` chicks, `B` birds when adult/chick stage unknown;
- Accuracy: `1` individually counted (approximately ±5%), `2` spatially extrapolated from counted area, `3` reasonably accurate estimate (~10–15%), `4` rough estimate (~25–50%), `5` order-of-magnitude guess.

Source-preserved metadata https://researchdata.edu.au/a-census-penguin-antarctic-region/700932 explicitly supplies the original AADC portal URL with **file_id 2216**, claiming that it contains both the untouched original Excel and an AADC *modified/corrected locality* copy. The metadata warns that locality harmonization may be wrong. Corrected rows must not be treated as independent observations of the untouched original source.

**Exact publisher-linked source URI** (HTTPS form of original documented HTTP source):
`https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216`.

## Frozen V32

A bounded, first-party HTTPS-only 15 MiB source request. Validate publisher redirect hosts, response HTTP/content-type, original raw bytes, source SHA256, safe zip filenames, and first-party file-type signatures. Do not assume that a 200 HTML SPA response is a spreadsheet. Never submit a personal email, forge authentication, bypass registration or follow off-publisher links. If original archive is not publicly delivered, report ACCESS_HOLD; no biological values have been restored.

If original XLS/XLSX is actually available, Stage V33 can map the original `SCAR Number` + exact source species/year/locale with OBIS directly and quantify how many of 238 repeated candidate units retain consistent `N1/N2` nest count stage, true observation year and original record lineage, instead of assuming individualCount is measured pairs. V32 does not itself fit ecological island effects.

No ecological claims from older count-source Woehler 1993/2008 until original stage/quality recovered and the source genealogy checked against MAPPPD, which may republish identical source events.
