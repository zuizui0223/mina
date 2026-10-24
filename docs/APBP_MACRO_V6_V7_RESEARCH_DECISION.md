# PR197 macroecological decision after V6 and updated MAPPPD V7 (2026-10-19)

**Status:** one original-publisher source-backed ecological effect test completed and REJECTED as unsupported; follow-on updated database quantified but not refitted. Separate from frozen *Ecology* PR189.

## Hypothesis actually examined, in penguin biology terms

Does modern mapped coastal ice-free rock availability, conditional on true island versus continental land, predict whether land-nesting Adélie / chinstrap / gentoo penguin colony *observed breeding-pair/nest count changes* are buffered against offshore October–November sea-ice anomalies?

This is **not** a test of observed local fast ice access, krill availability, migration or breeding success. 2025 exposed-rock polygons are static proxies, not time-varying 1980s–2022 available nesting capacity.

### First independent original-data V6 result

[Full numerical receipt](../results/APBP_LAND_SEA_ISLAND_CV_RESULT_V6.json) and [original-sources Actions #39207033264](https://github.com/zuizui0223/mina/actions/runs/39207033264):

| Predictor set | 12-block, equally weighted MSE | Same data, point-weighted MSE |
| --- | ---: | ---: |
| B0: year, species, initial nest count, survey precision, location | **0.200104166** | **0.172317767** |
| B1: B0 plus summer offshore sea ice change | 0.227392335 | 0.180675144 |
| B2: B1 plus modern rock extent and island×rock×sea-ice interaction | 0.259979114 | 0.189579382 |

The B1→B2 change *worsens* blocked MSE by **0.032586779**; 1/12 geographic blocks improved, including **no improvement** in largest observed region (217/406 nest-count change pairs). Proposed triple-interaction coefficient changes sign from −0.291254 to +0.089362 when the largest block is excluded. It passes **NONE** of the contracted ecological support conditions. No p-value/causal origin is claimed.

**Data capability:** 3,370 originally measured source nests of three Pygoscelis species were eligible in the broad source, but after matching exact Dec–Jan–Feb source dates, excluding **all** duplicate site/species/season observations, independently matching static island/rock and prespecified marine SIC years, only **406 truly consecutive breeding-season comparisons at 61 original site IDs, 31 mapped land polygons and 12 gross 250-km regions** remained. 350 rows occurred at provisional island sites and 56 mainland rows; 217 rows alone are from one region. Some remaining spatial blocks contain only 1–2 pairs. Species: Adélie 280, chinstrap 46, gentoo 80. The spatial comparison is both geographically and taxonomically unbalanced. `NOT_SUPPORTED_BY_THIS_DATA` is evidence against this model's transferability **under its defined sources**, not proof that any habitat limitation effect is identically zero in penguins.

### One bona fide database extension — original Oceanites MAPPPD v4.4

After the V6 result was closed, original `https://www.penguinmap.com/mapppd/DownloadAll/` was downloaded and audited directly (not scraped from published results); [MAPPPD V7 verified source and coverage receipt](../results/MAPPPD_V44_SOURCE_EXPANSION_QA_V7.json) and [Action #39208414355](https://github.com/zuizui0223/mina/actions/runs/39208414355).

Original MAPPPD live CSV SHA256 `5d1a5a3f136aeb999a5b429b2d8593f72e3c37b0a38fc15cf30eceb29daf10c4` at 2026-10-19, 2,114,238 bytes. **5,487 raw survey rows**, **4,055 source nest-type records** (remaining 582 adult, 850 chick), across **729 site IDs**. Same four-letter locationID format overlaps **706** of the 711 site IDs represented in the old APBP occurrence/measurement record table (8 additional old Event-only locationIDs were in the earlier 719 Events roster). A newer portal export is **NOT an independent second observation** of the old matching years.

**Actual recent extension:** among 2022/23, 2023/24 and 2024/25 source seasons, 244 measured nest-type records (44,121,79 by season), but only **102 eligible single-survey Dec–Jan–Feb primary Pygoscelis site×species×season cells**, over **80 site–species histories**, with 16 histories covering at least 2 new seasons. Including 2021→2022 bridges, **27 distinct strict consecutive nest-count pairs** ended in 2022–24, of which **10** were at the 2021→2022 frontier. Out of 27, **18** were from six Ross Island Bird/Crozier/Royds constituent colony census sites (3 consecutive transitions each). After crossmatching earlier versioned SCAR high-res geography, these 27 came from **15 original site IDs**: **24 provisional island**, **1 provisional mainland**, **1 GIS HOLD** and **1 site without original geographic match**. New-to-new strict recent pairs within 2022–24 number **17** across 11 source sites, with no mainland comparison. Therefore a holdout land×sea **island/mainland** interaction test has no independent geographic representation; *DO NOT* claim a credible external validation from those 27, or reuse the six Ross site time series as six independent islands.

Of 5,487 CSV records, 23 original rows lacked acceptable nonnegative integer source count (held), 1,886 lack an unambiguous Dec/Jan/Feb dated season and 45 of the 154 latest nest site/species/season groups are duplicates in the original portal and not selected. Source includes calendar year 2025 and even some season_starting=2025; the declared version through 2024/25 only authorizes a frozen 2022–24 start-season extension. Do not infer new survey dates or automatically include provisional latest entries.

## Scientific inference: identified gap, not just a data cleaning failure

1. **There is not yet evidence of an Antarctic-wide, island-specific coastal rock buffer of marine sea-ice-driven breeding-pair changes.** The prespecified negative region-holdout result is an ecological result about this observational model's predictive insufficiency, with large uncertainty in interpretation.
2. **The central ecological constraint is data coupling, not just raw count:** penguin databases provide site, species, timestamp, original nests and measurement error; the independently observed **annually varying accessible terrestrial nesting capacity** (not just modern rock presence) and matching intra/inter-island individual/site exchange remain largely absent.
3. As a result, the original question "why does an island patch reactivate versus stay empty when climate changes?" remains **unidentified**. The existing database has only known colonies; nonreporting is not known suitable-but-unoccupied patch, and no individually verified displacement/return can be estimated.
4. **Do not continue fitting extra radii, time lags, sample subsets, `nests=0` imputations, different ridge penalties, or arbitrary thresholds in V6 to obtain a favorable sign.** The only defensible expansion would change the type of evidence: dated high-resolution coastal habitat footprints, verified colony survey coverage including unoccupied suitable patches, matched climate exposures, repeated adults or contemporaneous individually resighted movement, ideally across multiple independent island systems.

## Repository state and safeguards

- Original official population, geospatial and marine source SHA256s are in V1–V5 receipts; V6 model's exact 12 held-out blocks and source fingerprints frozen in result JSON. V7 separate publisher original and its updated source checksum committed in QA receipt.
- No model fitted on the newer 2022–24 MAPPPD data, so the negative H1 remains a genuine independent observation of the original analysis and no double counting.
- *Ecology* PR189 frozen original Ross amount/path/state result is untouched. PR197 remains a methodological and macroecological exploratory study, NOT yet an additional causal penguin-island manuscript.
