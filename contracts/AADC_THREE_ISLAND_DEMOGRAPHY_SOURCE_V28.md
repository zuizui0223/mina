# V28 — Original AADC three real eastern Antarctic island occupied-nest source audit

2026-10-21. Freeze this source-/schema-only design after the closed V27 APBP within-/between-grid synchronicity consistency test failed. No previous penguin concentration, sync coefficient or climate value will be used to choose years, islands or source spreadsheet. This is an independent original *AADC publisher data family*, but historical surveys may be present in APBP; DO NOT claim statistical independence without source crosswalk.

## Official independently registered original source packages

1. AADC EDS **1103**, metadata key population_counts_BI, original DOI **10.26179/5c9bf6704cf70**. Published original count workbook for **Béchervaise Island, Verner Island, Petersen Island** in Holme Bay near Mawson. Historical data 1971–2004/05 are intermittent; 1990/91+ occupied nests are counted during the incubation stage approximately 2 December. Earlier historical records may be corrected for seasonal timing and must NOT be silently pooled as identical field counts. These are three physical island landmasses, unlike polar 250 km grid cells.
2. AADC EDS **5516**, metadata key AAS_4518_MacRobertson_Land_Adelie_Penguins, DOI **10.26179/s2qa-s344**. Original 1991/92–2019/20 tagged Adélie population dynamics and environmental covariate material. The published larger western Mac. Robertson Land survey describes *2009/10 and 2019/20* metapopulation surveys, and a single continuously studied Béchervaise Island demographic series. DO NOT turn them into annual counts at every offshore island. The time series may include sea ice, weather, success, fledgling mass and marked-individual resight/return; it is partly the SAME Béchervaise birds as EDS1103 (not independent replication).

Original publisher metadata links: https://data.aad.gov.au/metadata/records/population_counts_BI and https://data.aad.gov.au/metadata/records/AAS_4518_MacRobertson_Land_Adelie_Penguins .

## Source-only Stage 1 first

Use only the AADC HTTPS JSON API already working in existing V11/V13 (list /eds/api/dataset?size=10000, each eds_id UUID, /objects?recursive=true&removeBasePath=true, then /object/download?prefix=). Do not assume stale /eds/<ID>/download generic HTML is the spreadsheet. Confirm each exact eds_id and source title/metadata-entry key independently from returned publisher listing; record actual UUID, official API SHA, per-object filename and source SHA256.

Only download:
- **all** original XLS, XLSX or CSV children from eds 1103 (max 12 files, <=18 MiB each);
- for eds 5516 only filenames mentioning environmental covariates, time series or demography and ending XLS/XLSX/CSV (max 5 files, <=18 MiB).
Do not download/re-distribute original individual tagged-bird resight files from EDS5516. If no candidate, HOLD rather than pick a post hoc substitute.

For each exact original spreadsheet, report the publisher's worksheet names, header fields from first row (if title row present, first five rows, but do NOT inspect original Count values), number of nonblank/candidate season-ID values, sheet row and column dimensions. Do NOT calculate island nest counts, demographic growth, population synchrony, trends, correlations, sea ice or prey effects. Store only header/metadata/shas; no source records/positions of identifiable tags in Git.

## Prospective new biological design if suitable long original count series exist
Island grain fixed as 3 named *actual separate islands* and response **observed incubating occupied nests**, with year/season and field-method comparability. Statically pre-1990 historical corrected counts must be analysed separately, not as equally timed field counts. First freeze *post-1990 exact common island-year cohort* and source-defined effort/missing/nil rules **before opening island nest magnitudes**.

Minimum for next V29 matched-island descriptive analysis: at least **8 shared seasons with valid comparable occupied-nest counts from at least two of the three islands**, and **6 strictly consecutive annual pair windows** with the SAME islands (no interpolation or inferred zeros). A three-island comparison requires all three source island series to satisfy this, not 3 copies of one source census. If few years or metadata mismatch, report source feasibility HOLD rather than retrofitting alternative counts, year ranges or approximate nesting stages.

No novel macroecological island mechanism is claimed from V28. Broad pan-Antarctic generality demands many additional island complexes with harmonized source records. The main test is whether original ecological responses can be linked to independently measured breeding success, marked-individual movement and dated sea-ice/atmospheric anomalies to distinguish local environment from recolonization or colony social memory.
