# Admiralty Bay: published long-period numerical compensation on the same two sites (2026-11-25 JST)

Status: **DESCRIPTIVE_LONG_PERIOD_CONTRAST; NOT ANNUAL REPLICATION OR MOVEMENT ESTIMATE**.

Previous strict annual matched-count result and breeding-dispersal identification decision are preserved at f1207464ae8e72c90888ba9be5eaa4c43852098b. Prior evidence from Dugger (2010, 2026), Clucas (2018), Levy (2016), and Herman & Lynch (2022) is already reviewed there. Do not label Adélie/chinstrap immobile or gentoo mobile. Low genetic differentiation over generations is not a direct annual movement estimate.

## Source and verification

ATCM 46 Final Report, revised ASPA 128 management plan, Western shore of Admiralty Bay, Table 1: https://documents.ats.aq/recatt/att773_e.pdf . Official PDF text extraction located table across a page break. Web screenshot requests returned cache miss; local PDF download failed DNS. No downloaded PDF SHA or visually verified original table is claimed. All ten two-site species-period sums independently agree exactly with the published species totals. Source caption describes four-year averages, but 1992–96 spans five calendar labels; actual survey dates and averaging support are unverified. Preserve literal labels; do not expand into annual counts. Same named locations and two species, not guaranteed identical census dates/footprints. This post-result descriptive source extension is not a rescue of the failed preregistered-style annual comparison.

| species/site | 1978–81 | 1992–96 | 2009–12 | 2014–17 | 2019–22 |
|---|---:|---:|---:|---:|---:|
| ADPE LLAN | 10859 | 6073 | 2454 | 2853 | 2231 |
| ADPE PTHO | 11899 | 9886 | 4578 | 4740 | 3196 |
| ADPE sum | 22758 | 15959 | 7032 | 7593 | 5427 |
| GEPE LLAN | 2174 | 1765 | 4646 | 6162 | 8083 |
| GEPE PTHO | 715 | 267 | 90 | 76 | 0 |
| GEPE sum | 2889 | 2032 | 4736 | 6238 | 8083 |

The 2023/24 species totals elsewhere in the management plan are not allocated to the two sites, so they are not used.

## Executed arithmetic

Same loss/gain definition as earlier: L=sum of decreases in the two observed site means, G=sum of increases, C=min(L,G)/L if L>0. First to last periods: ADPE LLAN -8628, PTHO -8703, L17331 G0 net -17331 (-76.15344%), C0. GEPE LLAN +5909, PTHO -715, L715 G5909 net +5194 (+179.78539%), C1; uncapped G/L 8.26434. GEPE also loses a breeding site at the level of the published means; not a verified extinction year. No claim that the 715 pairs moved to Llano Point.

| adjacent periods | ADPE L/G | GEPE L/G | ADPE C | GEPE C |
|---|---:|---:|---:|---:|
| 1978–81 to 1992–96 | 6799/0 | 857/0 | 0 | 0 |
| 1992–96 to 2009–12 | 8927/0 | 177/2881 | 0 | 1 |
| 2009–12 to 2014–17 | 0/561 | 14/1516 | undefined | 1 |
| 2014–17 to 2019–22 | 2166/0 | 76/1921 | 0 | 1 |

Three adjacent periods with observed losses in both species: ADPE C 0 in all, GEPE C 1 in two and 0 in one. Equal-window mean 0 vs 0.6666667; loss-weighted capped ratio 0 vs 0.2279279. The two summary methods answer different questions. One two-site area, coarse period means, varying duration, shared period endpoints. No independent windows/p-values, no claim of a universal scale-dependent effect. Short-term annual matched comparison did not show robust GEPE advantage; do not pool the two time grains.

## MAPPPD overlap audit

Reopened actual v5 original archive 14934334550 (SHA256 0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4, CSV d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89, CRC passed). 154 numerical nest rows for these four site-species series. Latest season ADPE LLAN/PTHO both 2018, GEPE LLAN 2014, GEPE PTHO 2002. All four lack any annual nest observations during 2019–22. Earlier period support overlaps Ciaputa & Sierakowski (1999), Hinke (2019), and other original references used in this official table/monitoring programme. No event-level independence certified. New later-period published aggregate extends coverage but does not supply the original annual observations needed for the frozen common climate model. Do not treat a period mean as a single season or create pseudo-replicates.

Executed script admiralty_aspa128_period_means.py commit 8f270cccdbac76de0aa9990ed6e6d0deadc2964e, exact Git blob 50912abe6e111c7aa2efba97260cebc58c97a37e matches local file; SHA256 8a075e42d5c56e628b2a45e49c24158b978f2618f651ee780c3ba0df779517e5. Output result.json SHA256 3e580efb9d3284dc2848ccf36b6dfaa9a7401252de7eb7f48e5f115e247c9833. Reproduce: python research/signy_seal_spatial_pressure_v1/admiralty_aspa128_period_means.py ARTIFACT_DIRECTORY OUTPUT_DIRECTORY.

## Next identification gate

Arctowski official ecological monitoring https://arctowski.aq/nauka/monitoringi/monitoring-ekologiczny/ describes monitoring since 1977, three-species breeding chronology, band register, nest/chick counts with UAV support. Zmarz et al. 2015 DOI 10.5194/isprsarchives-XL-1-W4-189-2015 identifies six colonies in two bays. Original individual-level encounter histories and synchronized year×site×species counts were not located in open downloadable form by this search. NOAA annual census DOI 10.25921/58yq-7g68 covers Copacabana and Cape Shirreff, already overlaps MAPPPD/NOAA programme, not six matched sites. Korczak-Abshire et al. 2026 DOI 10.1111/ibi.70030 cites DSM DOI 10.5281/zenodo.14614877, whose inventory contains three DSMs and README, not multi-season nest/band histories; no large raster download initiated. The Polish programme is a targeted original-data request candidate, not evidence data are accessible or permission given.

Request scope (not sent): annual occupied/incubating nest counts for the same survey footprints for ADPE/CHPE/GEPE, all six monitored sites, especially LLAN and PTHO, 1993–2024 and complete historic series if available; actual census dates, coverage, methods and observed zeros vs missing, parent/subcolony crosswalks, original count/source IDs, four-year mean calculation years. For direct breeding dispersal, request pseudonymized individual identifiers, species, natal marking site and age, confirmed breeder/visitor status at each reobservation, site and year, effort/detection coverage and reporting restrictions. Do not request personal/private researcher details or send contact without user's direction. No original annual data or band histories received, no ecological regression or movement model fitted. Main and frozen manuscripts unchanged.
