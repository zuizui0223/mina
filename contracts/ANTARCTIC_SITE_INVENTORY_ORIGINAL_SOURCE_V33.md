# V33 — Antarctic Site Inventory original field census, site × species × breeding season

**Original source frozen 2026-10-26 before opening this 2013 first-party CSV's individual source rows.** Not another regression on published author effect-size tables. Earlier MAPPPD and AADC analyses are distinct datasets with overlapping original field campaigns: repeated sightings or later republishes of ASI counts are not independent survey confirmation.

Publisher: Lynch, Naveen & Casanovas (2013), *Antarctic Site Inventory breeding bird survey data, 1994–2013*, Ecology E094-243-D1, DOI **10.1890/13-1108.1**. Original raw CSV download verified from publisher Ecological Archives data page:
`https://esapubs.org/archive/ecol/E094/243/Antarctic_Site_Inventory_census_data_1994_2012.csv`,
published MD5 `00871bd47b6ec30cda68d1506120bfb3`, original metadata `https://esapubs.org/archive/ecol/E094/243/metadata.php`. Publisher describes **1,124 original records from 113 site IDs and seven breeding bird species**, including four penguins? Actual species codes ADPE/CHPE/GEPE/MCPE and flying BESH/KEGU/SOGP. Seven source regions CW/EI/NE/NW/SH/SO/SW, 1994/95–2012/13 ASI period, but retrospective citations may span older field dates.

## Why this specific dataset qualifies for *new* macroecology (but not independent sampling from MAPPPD)

Each source row includes four-character `Site_ID`, actual original `Season` (season-start year), source `Date`, count `Count`, `Counted_object` N (active nests/breeding pairs) or C (chicks), `Accuracy` 1–5, `Source` (source ASI or external published source) and explicit original spatial coordinates. These are primary data rows, not previous papers' model coefficients. **Do not pool chick counts with nest counts**; original survey maximum per season was selected for ASI (sometimes >1 original census visit occurred but only maximum published), so recorded counts may be biased relative to phenology/census effort.

## Frozen V33 quality gate

- Download original publisher CSV with <=2 MB total transfer, SHA and MD5 must equal publisher original value; do not source an altered mirror with silently changed file.
- Verify row count and literal required source field names; report exact source `Source` values and original paper citations, number of ASI primary rows versus imported secondary sources. Inferred 'independent' field sample means exact `Source=ASI`; never count multiple copied external bibliography rows as new independent ASI measurements.
- Report counts and distinct site IDs for original nest `N`, chick `C`, original accuracy grade (1,2 vs 3,4,5), validity of breeding season and actual count. `C` means chicks, not nest-pair records.
- Site sampling grain: site × species × original breeding-season start year × stage N, not individual nest, not necessarily one physical island. Count source collisions with duplicate same key or multiple original field sources; no favorable max/min row selected after inspecting count.
- For an eventual 2013-only observation comparison, require **exact original ASI primary, N stage, Accuracy<=2, nonnegative integer actual count, valid coordinates, season, source ID**; original literal zeros are retained as `UNVERIFIED_SURVEYED_ABSENCE` unless field visit effort and true absences are independently documented. No missing → zero.
- Report distinct sites per species and region, number of site × species histories with 2+ N-stage seasons and 2+ separate published observed years, and ≥3 original regional block sample gate. This V33 fits NO ecological effect and makes NO island/colonisation claim.
- Repetition of original data in MAPPPD means this dataset is good first-party **stage-reference & source trace** for original observations, not fresh independent biological replication simply because the raw CSV lives on Ecological Archives.
- Physical island identity requires independent original GIS coastline features or explicit site island lineage (the 113 site IDs may share same physical landmass or continental terrain); do not call 113 independently isolated islands.
- A sub-Antarctic source group is not the Antarctic Treaty mainland and should not be confused with polar sea-ice substrate and emperor colony fast ice.

Next analysis after positive source quality: freeze independent island P vs breeding habitat F comparability using source field-site provenance and held-out multiple **genuinely distinct physical islands**; do NOT retune source choice/accuracy after seeing habitat effects. If geographic parent island identity and actual visited-empty patches cannot be independently established, restrict to descriptive stage-matched regional census synchrony without claiming causal island mechanism.
