# V16 — Original ASI exact-day multispecies nest census: quantitative source result

Date 2026-10-20. Publisher-MD5-verified ORIGINAL Antarctic Site Inventory (Lynch, Naveen and Casanovas 2013, Ecology 94:2653, DOI 10.1890/13-1108.1). Original CSV at https://esapubs.org/archive/ecol/E094/243/Antarctic_Site_Inventory_census_data_1994_2012.csv, exactly 115,952 bytes, publisher MD5 00871bd47b6ec30cda68d1506120bfb3, SHA256 e01ee9bfbd8337bcaca7c71aea0b00162f9015cf4954d3ad76eed536cad37634.

**Scientific progress:** V15 AADC site×season search-event linkage could not verify co-dated surveys; in this distinct, real original field census archive, **99 exact same site/date nesting-census multi-taxon units at 37 original sites and three regions** were found. Every cohort uses original ASI source, nest not chick, quality ≤25%, exact same original site+day and season. This is more specific than co-seasonally inferred AADC records. It is **not yet a supported Antarctic-wide biological interaction**, because 99 events are not 99 independent islands, sites may be mainland, the same-day observer/visit ID is unverified and original penguin records overlap published earlier series/MAPPPD.

## Source discovery and quality

- **1,124** original source census records and **113** advertised original locations; quality/date restriction retains **633** original nest census rows at **99** original site IDs.
- First real source audit stopped: some Site_ID values have inconsistent Region codes. Two Site_ID values contributing 12 otherwise eligible rows are excluded **wholesale before any abundance values**, not assigned to whichever region is convenient.
- No duplicate original Site_ID × season × day × species group survived the strict cohort.
- Across all seven species, **131 same-site exact-day events** have ≥2 species, at 49 original site IDs in four regions (CW 85, EI 1, SH 37, SW 8).
- At least 2 penguin species co-censused: **53** same-site days, 23 sites, 3 regions (**prespecified gate requires 60, 20, 4; fails**).
- Penguin × flying seabird co-census: **99** same-site days, **37** sites, **3** regions (**prespecified gate requires 25, 10, 3; passes**).
- Pair opportunities among the flying guild are dominated by blue-eyed shag (BESH): ADPE×BESH 21, CHPE×BESH 42, GEPE×BESH 40; counts are overlapping because multiple penguins can be surveyed the same day. These counts are **paired observation opportunities, NOT nest abundance effects**.
- The three cross-guild regions contribute CW 62, SH 29, SW 8 exact-day events, which is insufficient to infer circumpolar or all-island generality.
- **Zero Count magnitudes used; zero biological model fits**, no inferred zeros for unsurveyed species.

## Scientific decision

The *cross-guild observation panel* is **feasible for a subsequent test of longitudinal same-site co-change**, unlike the V15 inferred event series. But a cross-sectional raw count correlation is not evidence for predator subsidy/competition, because census site area, crew effort and breeding timing are shared confounders. Only a model with **within-site repeated independently timed cross-guild nest counts**, verified overlapping source provenance and independently measured environmental forcing can address potential differential response.

Next permitted step: freeze an independent **temporal-pair support gate** before opening numerical nest counts; count independently repeated cross-guild site-pairs in adjacent years, then model growth covariation only if sufficient site/region support. Do not promote source feasibility to mechanism evidence, relabel sites as literal islands, or count original ASI as independent of overlapping MAPPPD census observations.

- Frozen contract: ../contracts/ASI_ORIGINAL_COSURVEY_V16.md
- Executed verified original source: https://github.com/zuizui0223/mina/actions/runs/39402110777
- Machine-readable original structural result: ../results/ASI_ORIGINAL_SAME_DAY_NEST_COSURVEY_V16.json

## External context

- Southwell et al. 2025 East Antarctic historic eight-species search-event dataset DOI 10.26179/5n29-r073. This is a different region, source genealogy and observational grain than ASI; not treated as a common survey network.
- CCAMLR CEMP standardizes phenology, breeding success and abundance, but **CCAMLR's underlying complete CEMP original biological datasets are restricted to members by request** (2026 CCAMLR Data Inventory, https://www.ccamlr.org/en/data/ccamlr-data-inventory). Do not pretend the public CEMP site geometry repository contains its underlying penguin breeding-success records.
