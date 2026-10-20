# V15 — Direct Antarctic penguin–skua co-search support, outcome-blind

Frozen 2026-10-20 before inspecting any focal pair co-occurrence cells. New biotic-interaction question, NOT a tuned V14 island-area/guild model, and independent of frozen Ecology PR189.

## Scientific question and prior art
The south polar skua forages on Adélie eggs/chicks and some breed beside penguin colonies (Australian Antarctic Program account). This association is prior art, NOT a novelty claim. A potentially new macro comparative test would ask whether the local breeding co-occurrence of this predator with Adélie penguins is different from that of a prechosen marine-feeding crevice nester (snow petrel), across geographically independent coastal islands, conditional on habitat and verified comparable original survey effort. This is NOT a causal predation or founding test.

The published AADC study (Southwell et al. 2025; DOI 10.1111/ddi.70066) already mapped occupancy, search effort, richness and ignorance. Avoid reproducing those outcomes as our own ecological discovery.

## Source-only eligibility fixed before outcome exposure
- Original AADC 2025 geography derived V13 CSV SHA256: 48c716c38c41a054eefc20c03de3c21d75047049e6e277d471d9b9135aab7da5 (7,785 geographic rows).
- Original eight-seabird survey derived V13 CSV SHA256: dba39d79f6309f90e23e896415177ea75086aaf2ecb5523256e48895e95dfc5c (33,107 survey rows).
- Native geographic unit: original geog_site_id, not a colony, an individual, a nest patch, or an independent island demographic population.
- Island features only; positive mapped area, finite original location. Original six-digit consecutive breeding season start 1980–2020 inclusive.
- Exactly one source row per geog_site_id × species_code × season. **Exclude all rows of every duplicated key**, whether compatible or contradictory, before selection.
- Valid response eligibility (not response tabulation): author-literal P + exact linked certainty category 5, or literal A + exact category 4; exact original certainty lookup. NR (nonreporting), missing and contradictory are NOT zeros, and V15 may not tabulate P-versus-A counts, compute two-species status contingency, odds ratio, regression or any biological effect.
- Focal pairs are ADP–SK (Adélie–south polar skua, primary) and ADP–SP (Adélie–snow petrel, prechosen contrast). Exact same ORIGINAL geographic site and breeding season. No nearest-neighbour substitutions.
- Spatially independent descriptive groups: 250-km EPSG:3031 grid. Each recorded original site counts once toward support, regardless of repeated site-season records.
- Record: pairs, unique sites, block site counts, exact matched calendar-day pairs (both original day/month/year valid and day_uncertainty zero/empty), unique same-day sites and blocks, same-vantage text, and same obs_number text. **Matching date, vantage or obs_number are NOT proven original joint observation visit keys** and must never be re-labeled as shared survey effort.

### Predeclared gate for prospective external biological inference
Primary ADP–SK requires >=60 distinct island IDs; >=5 geographically independent blocks with >=5 sites each; >=30 same-date site-season pairs across >=20 distinct sites and >=4 blocks. Prechosen ADP–SP comparator requires >=40 distinct island IDs and >=4 blocks with >=5 sites. If any requirement fails, scientific outcome is STOP_INSUFFICIENT_OR_UNMATCHED_INDEPENDENT_COSURVEY_SUPPORT. No adjusting time windows, geographic radii, focal taxa or thresholds after counts.

Even if numeric gates pass, biological fitting requires independent confirmation of common survey event/observer identity or effort and comparable substrate/access risk sets. **This V15 never fits biology**. Absence of qualified co-search is missing identifiability, NOT ecological evidence of no interaction.

References: original DOI 10.26179/5n29-r073; Southwell et al. 2025 DOI 10.1111/ddi.70066; Australian Antarctic Program https://www.antarctica.gov.au/about-antarctica/animals/flying-birds/south-polar-skua/.
