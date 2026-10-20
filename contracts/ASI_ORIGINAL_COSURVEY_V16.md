# V16 — independently archived Antarctic Site Inventory same-day multi-species support

Frozen 2026-10-20, before looking at original census Count values. The ASI programme is a distinct source pathway from AADC V14/V15, but some underlying observations also appear in MAPPPD and prior ASI publications. A separate archive is not automatically an independent biological replication.

Original Lynch, Naveen & Casanovas (2013), Ecology, DOI 10.1890/13-1108.1, publisher Ecological Archives E094-243-D1. Official file: https://esapubs.org/archive/ecol/E094/243/Antarctic_Site_Inventory_census_data_1994_2012.csv. Official MD5 00871bd47b6ec30cda68d1506120bfb3, advertised 1,124 rows / 113 site labels / 7 seabird species, 1994/95–2012/13.

## First gate, outcomes untouched
Download publisher CSV via official HTTPS, reject mismatched MD5 or unexpected source schema. Examine header and metadata ONLY. No numerical Count magnitudes, no nest success, no ecological fitted effects.

Eligibility:
- Source literal ASI, Counted_object literal N (nests, not chicks).
- Count quality Accuracy 1–3 only; six-digit/census date exact mm/dd/YYYY and original Season start year 1994–2012, consistent with austral summer calendar year.
- Original 4-character Site_ID, source Region one of CW/EI/NE/NW/SH/SO/SW, known seven Species codes.
- Exclude *all* repeated same Site_ID × Date × Season × Species groups rather than picking high counts.
- Count same exact site/date/season penguin pairs (ADPE, CHPE, GEPE, MCPE), and penguin×flying bird pairs (BESH, KEGU, SOGP), across original independent site and regional labels. No implied zero for a species without its own census.
- A shared site/day within the literal ASI original source is suggestive of a common field visit, but lacks a verified shared-observer/visit ID and still does not prove simultaneous same-effort detection.

Prespecified primary support gate: at least 60 site/day multiple-penguin nest census units, 20 original sites and 4 source regions. Penguin/flying cross-guild gate: at least 25 site/day units, 10 sites and 3 regions. With neither gate supported, STOP and do not tune thresholds. Even with support, biological modelling needs a separately frozen question, provenance non-duplication against MAPPPD, an independent environmental covariate and geographic holdouts.

The 2013 data paper and Lynch et al. 2012 already published population trends and spatial change. Report a *source feasibility result*, not a newly discovered ecological relationship. Islands must be classified from independently grounded geography; a four-letter site is not itself a physical island.
