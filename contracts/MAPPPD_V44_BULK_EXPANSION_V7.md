# V7 — Independent MAPPPD v4.4 whole-census database extension (before new source outcomes)

Date 2026-10-19. V6 first source-backed 12-region predictive test was NOT SUPPORTED (B0 0.200104166, B1 0.227392335, B2 0.259979114). This *newly versioned temporal extension* is to increase temporal independence, NOT to rescue the original V6 land–sea hypothesis by adjusting its 406-pair roster, buffers, lags or thresholds.

## Original current website source

MAPPPD (Oceanites; public portal v4.4), URL https://www.penguinmap.com/mapppd/DownloadAll/ provides a direct CSV through 2024/25 breeding season. Publisher site: https://www.penguinmap.com/mapppd/ . Original header checked before deeper ingestion:

site_name,site_id,cammlr_region,longitude_epsg_4326,latitude_epsg_4326,common_name,day,month,year,season_starting,penguin_count,accuracy,count_type,vantage,reference

This is mutable, **NOT identical to 2023 APBP Darwin Core Archive DOI 10.48361/zftxkr**. Archive the actual retrieval timestamp, SHA256, row count, license/attribution and original publisher URL. Original count references (HTML in the source CSV) are bibliography metadata, not executable instructions. Current MAPPPD terms govern re-distribution; original full dataset is not automatically assigned 2023 APBP DwC-A CC BY rights. No full third-party raw CSV will be committed to GitHub.

## Eligibility fixed before processing original row-level counts

- Restrict main biology candidates to measured penguin nests, exact integer penguin_count >=0; original adults/chicks stay separate. Preserve every original survey day/month/year, explicitly supplied season_starting, 1–5 accuracy, vantage, original reference, and original census site_id.
- Accept species name variants via one explicit canonical table: Adelie/Adélie, Chinstrap, Gentoo (primary). Emperor, Macaroni and King recorded for sample coverage but not added to V6 fits.
- Use season_starting as explicitly supplied by curator; flag records where dated December year and January–February year disagree with curator season start, but do not invent a start year from a day/month that is missing. New data for 2022/23, 2023/24, 2024/25 = season_starting >=2022 and <=2024. 2025 calendar year is not necessarily 2025/26.
- Original source site_id is four-letter *colony census site*, NOT an island. Report overlap with known 719 APBP v2.3 site IDs and newly appearing site IDs. Do not classify island vs mainland from source names or infer true occupancy zero from unreported site/species/year.
- Keep within-site×species×season duplicate surveys as independent source rows, but EXCLUDE such ambiguous year groups from a strict one-row-per-site panel for the candidate temporal holdout. Never favor the larger population count. Compute 2022+ new survey rows, distinct sites, species, years, and older-to-new bridging consecutive-year pairs.
- Dates, count units, site IDs, and source-reference metadata must be auditable. Poorly parsed rows or a changed header/schema are a scientific HOLD rather than hidden exclusion.
- An APBP old record with the same site/species/year/count is an *overlapping repeated publication*, not a second biological sample; compare source row overlap, count conflicts, source accuracy and new years objectively.
- Model outcomes are NOT inspected in V7: no population growth regressions, marine correlations, island vs mainland effect, p-value or new land×sea coefficient. To evaluate new 2023–25 nests prospectively later, obtain matching new-year October+November NOAA SIC and matched independently checked static coast/rock data; do not impute 2022 SIC as 2024.

## Required outputs and limits

A GitHub Actions run should download from the live official CSV URL over verified HTTPS, reject HTML and >25 MB, SHA256 the original raw bytes, report row counts and coverage by species/count unit/survey accuracy/season, site-ID overlap/new, 2022+ strict one-year repeated nest sample counts and old-to-new bridging pairs. Preserve the source content version as original URL + timestamp + hash, not invented archival DOI.

The source-identified 2023 APBP includes 4,055 Event / 4,768 Occurrence / 4,750 eMoF with 3,514 nest rows; v6 406 one-year paired observations from 61 sites. These are different coverage measures; more portal rows do not guarantee more comparable breeding histories or independent colony population time series.

If actual original direct download fails, report HTTP/source HOLD and do not substitute pre-2022 source as "latest". The prior frozen Ecology PR189 remains untouched and the V6 ecological negative result remains on record.
