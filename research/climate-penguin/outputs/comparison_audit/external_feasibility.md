# External comparison data: downloaded-file audit, 2026-10-29

## Main finding

There is a useful same-species predator-removal time series for a flying diving seabird, and a same-region penguin/flying-seabird × predator-status table. They answer different questions. Neither supplies a balanced flightlessness × predator intervention experiment, nor evidence that individual birds moved between colonies.

## Hauraki Gulf: actual supplemental workbook

Primary article: [Borrelle et al., Oryx, DOI 10.1017/S0030605316000880](https://doi.org/10.1017/S0030605316000880). Article online 2016, journal volume 2018. The actual XLSX and PDF supplements were downloaded and inspected, not inferred from metadata.

File: `work/comparison_audit/external/S0030605316000880sup002.xlsx`, sheet `Appendix 2_Borrelle et al`, 98 rows × 37 columns. One island per row, 16 bird species, all latitude/longitude/area values present. 1,568 species–island binary cells; 308 recorded presences; no missing bird cells. One flightless species (Little penguin), 15 flying species. Species labels retained verbatim; do not silently change historical Eudyptula taxonomy.

| Predator status | Islands | Little penguin recorded present | Little penguin not detected |
|---|---:|---:|---:|
| Uninvaded | 30 | 17 | 13 |
| Invaded | 37 | 6 | 31 |
| Cleared | 31 | 26 | 5 |

Full counts for all 16 species are in `hauraki_species_status_counts.csv`. The complete verified source table is saved in work as `hauraki_verified.csv`.

The complete 98-island table, including exact island names, latitude/longitude, original species labels and all source fields, is also delivered as `hauraki_verified_island_species_table.csv`. The 16 species are Little penguin, Australasian gannet, New Zealand storm petrel, Fairy prion, White-faced storm petrel, Common diving petrel, Black (Parkinson's) petrel, Cook's petrel, Grey-faced petrel, Black-winged petrel, Pycroft's petrel, Little shearwater, Buller's shearwater, Flesh-footed shearwater, Fluttering shearwater, and Sooty shearwater.

**Vegetation/habitat audit:** There is no measured vegetation cover, vegetation time series, habitat patch extent, or nest-level vegetation variable. `EcoClass` is a broad I–VII ecological-condition category. The PDF defines it using a mixture of introduced mammal presence/history, vegetation modification/recovery, land use, and sometimes inshore invasion exposure. It is therefore **not an independent vegetation covariate**; adjusting for it alongside predator status risks circular adjustment and conditioning on historical consequences of predators. It can describe the sample or support carefully justified coarse sensitivity restrictions, but cannot separate vegetation from predator effects. For example class I says mammals have not been known and vegetation may have recovered, class II includes mammals absent/removed and recovering forest, class V includes farmland/grassland/shrubland, class VII includes proximity within mammal swimming range.

**Crucial legend:** bird 1 = presence; 0 = **not detected**, not verified absence. The paper explicitly describes the data as presence-only, assembled from uneven historical reports and confirmations through Austral winter 2015. There is no species–island census year, no visit effort, no repeated census table and no bird abundance. The workbook `Date` column is **last successful eradication year**, not bird observation year: cleared islands 1936–2011; others 0. Never treat these dates as annual bird records.

The 37 invaded + 30 uninvaded islands form a 67-island cross-sectional comparison. They do not constitute 67 independent flightlessness replicates: all flightless records are one penguin species. Cleared islands are not equivalent to never-invaded islands. Their current assemblages reflect invasion history, recovery time, and selection of islands for restoration. Predator presence fields and status require legend-aware interpretation, not indiscriminate 0/1 conversion.

Supported analysis: species-specific *recorded breeding occurrence* associations with predator status, area and geography, with survey/history sensitivity and explicit non-detection caveat. Flight-status interaction is statistically collinear with the contrast between one penguin species and the other taxa if species-specific responses are freely estimated. A hierarchical interaction can be fit only through strong pooling assumptions; it does not identify the causal effect of flightlessness.

**Not supported:** colonization, disappearance, time-to-recovery, source-population abundance, or an annual predator-removal BACI. The manuscript has some historical reference-island comparisons but the workbook is not a longitudinal panel.

## Naked Island Archipelago: actual repeated counts

Primary paper: [Stark et al. 2026, Journal of Wildlife Management](https://doi.org/10.1002/jwmg.70242). Data archive: [DOI 10.7944/m15x-3h89](https://doi.org/10.7944/m15x-3h89), [FWS record 193216](https://iris.fws.gov/APPS/ServCat/Reference/Profile/193216). Downloaded ZIP, 277,081,749 bytes, containing raw counts, survey files, nest data, code and outputs. Manifest includes exact download URL and SHA256.

Extracted `PIGU_Colony_Surveys_1978_2023.csv`: pigeon guillemot *Cepphus columba*, **one flying, diving seabird species**, four spatial groups, 184 nominal group-year rows 1978–2023; 72 have counts, 112 missing. **No observed zero counts.**

| Group label in file | Interpretation | Observed pre-2014 years | Observed 2014–2023 years |
|---|---|---:|---:|
| Naked | Treated archipelago, not one independent island | 14 | 10 |
| Smith | Untreated comparison group | 13 | 10 |
| Fool | Untreated comparison group | 3 | 10 |
| Seal | Untreated comparison group | 2 | 10 |

All four groups share **2008, 2013, 2014–2023**: 12 years and 48 counts; two pre-removal years and ten years starting with removal in 2014. Naked and Smith alone additionally share 1978, 1979, 1990–1997, 2007. The three named large islands in the treated Naked archipelago are not three treatment replicates in this count table.

The response is birds detected during shoreline surveys, **not breeding pairs or nests**. Survey shoreline lengths are provided. Regional survey files and transect coordinates are also in the archive. Raw count comparison is not directly interchangeable with mina breeding-pair counts; use separately estimated within-study standardized changes if comparing patterns.

Additional inspected files:

- `Naked_PIGU_Multiyear.csv`: six nest-count records, 2008 and 2014–2018, pooled `island=all`; no zero nests (17, 11, 28, 41, 51, 52). This is recovery from depletion, not reappearance after zero.
- `Nest_proportion_script_clean.csv`: 18 rows = three substrate categories × six years (1979, 2008, 2015–2018). Categories Cliff_Face, Cliff_Top, Talus. A Talus zero in 2008 is a substrate-specific absence of found nests, not whole-colony extinction.
- The raw ancillary count totals differ in places: 2018 bird count 167 in nest file vs 163 in shoreline-count file; 2016 nest total 41 in nest-count file vs denominator 42 in substrate file. Preserve observation definitions and reconcile with code before combining.

Supported analysis: one-species controlled before/after trajectory associated with mink-removal onset; one treated spatial group, three untreated groups, sparse common pre-period. Retain 2014 as intervention/transition year; sensitivity excluding it. Review pre-trends and survey timing; do not treat ten post-years as ten independent removal experiments. The paper also discusses prior oil-spill and environmental history. Recovery despite nearby comparison populations can be studied descriptively, but source abundance causes, dispersal and immigration cannot be demonstrated by counts alone.

**Not supported:** flightlessness effect, complete mink absence inferred from removal onset, or zero-to-positive recolonization analysis. This is valuable external evidence that can be contrasted with predator-free penguin recovery, but cross-study differences also include species, region, prey, survey measure and historical disturbance.

## Surprise Island

Primary article: [Philippe-Lesaffre et al., DOI 10.1111/cobi.14042](https://doi.org/10.1111/cobi.14042). Article exposes `cobi14042-sup-0003-Data.xlsx` (9.9 KB), but a fresh direct retrieval returned HTTP 403. **Not downloaded; no claim of verified row counts or usable section-level panel.** Article describes 2002–2009 transect monitoring around 2005 rodent eradication and longer follow-up, but that is publication-level evidence, not an audited reusable table. Do not count this as ready input.

## Design implication

For the revised question about failure to recover despite nearby conspecific populations: use mina/MAPPPD to determine whether true surveyed zeros and repeated low-count episodes exist. Hauraki adds a cross-sectional context only. Stark adds a verified predator-removal recovery trajectory but contains no colony extinction/reappearance events. Current external files do not close the causal separation of flightlessness and mammalian predation. Do not manufacture a factorial design by pooling Antarctic penguins with Alaskan guillemots.

All numerical summaries above were computed from downloaded files. Download provenance and hashes: `external_source_manifest.json`. Raw archive and extraction are under `work/comparison_audit/external`; user-facing summary tables are alongside this report.
