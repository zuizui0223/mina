# V33 — Original 2026 New Zealand Ross Sea Adélie 39-colony census source and year coverage

2026-10-22, source-only before opening any new bird count magnitude or fitting new ecological effects. New source family: Manaaki Whenua - Landcare Research / Antarctica New Zealand Ross Sea aerial breeding survey DOI 10.7931/kf06-x745. This is NOT another reanalysis of V27 APBP or the two-island AADC source.

## Exact public source and limits
Canonical CKAN dataset UUID fb407798-f399-4875-81a0-51976b4c759c; package name adelie-penguin-census-data; official API:
https://datastore.landcareresearch.co.nz/api/3/action/package_show?id=adelie-penguin-census-data

The 2026 original census XLSX is resource 5fd490e5-92c4-4f2c-a82e-c66db2320eb1, file Ross-Sea-adelie-penguin-census-record_1981-2024.xlsx, 12,578 bytes, published MD5 195a9027a0d18012812b09fb345ac60e.
Original site-location workbook resource f82c5e1d-f04d-446d-9338-e9d0603360f8, file colonylocations.xlsx, 8,025 bytes. Publisher field-method PDF resource e081bd92-4e27-44eb-8d5b-065906e97cc2, 29,666 bytes; the original document describes 39 Ross Sea colonies but its data-year listing through 2017 predates the publisher's 2026 amended census XLSX extending through 2024. Source methods require cross-checking before any biological change analysis.
Original publisher license CC-BY-NC 4.0, user attribution required, noncommercial research only unless licensed. No workbook bytes or raw population-count observations committed to Git.

Published original metadata: occupied nests/Adélie breeding-pair aerial census for 39 colonies Ross Island to Cape Adare, 1981–2024, with *no field data in 2020 due to Covid-19*. Not all colonies were censused each year; missing is NOT zero and zero counts are only recorded if explicitly supplied.

## Frozen, outcome-blind source structural checks
- Via official CKAN JSON API, verify dataset UUID, DOI, resource UUIDs, declared size, MD5 and publisher download URLs, final HTTPS under landcareresearch.co.nz. No unofficial mirror.
- Decode XLSX via original ZIP/worksheet/shared-string structure; audit sheet names, dimensions, first header tokens, orientation (colony by year OR year by colony), original publisher colony labels and numeric-present/missing observation cells without inspecting or reporting animal count magnitudes.
- Detect original calendar years 1981–2024 in exact numeric or standard austral season YYYY, YYYY-YY/YY, YYYY-YYYY forms. No reinterpretation of textual qualifiers as new surveys; 2020 source gap is not biological extinction.
- Exclude duplicate exact colony IDs or duplicated year keys entirely, and distinguish SOURCE COLONIES from INDEPENDENT PHYSICAL ISLANDS. Colony labels or coordinate rows do not prove that any given pair lies on independent island land polygons.
- Audit site-location workbook only for source sheet/field structure and possible identifiers, NOT for bird counts. Publisher PDF is verified by PDF header+SHA only, no direct bird observations.
- Source feasibility for later frozen biological V34: >=20 independent source colony IDs with >=5 numeric-present original years AND >=10 calendar years with >=5 individually listed observed colonies; separately report same-year and strictly consecutive coverage. The **island physical landmass** eligibility remains HOLD until the site-location crosswalk and true coastal land polygons are independently matched, even if >=39 colonies.
- No biological counts, correlations, synchrony, kappa, climate/sea ice, dispersal, extinction or causal tests are authorized at V33. Prespecified future macro study will require independently replicated physical islands and stable matched census stages; the 39 source colonies could be nested in several landmasses.
- Original 2026 data newly released may overlap historic APBP/MAPPPD colony counts. Must match species, original site IDs, dates, units, methods, references and overlaps before calling it biological replication of those systems.

Closed V14–V17/V24/V27 gates and V31 regional exploratory result are unchanged. Frozen Ecology PR189 remains separate.
