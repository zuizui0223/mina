# Original MAPPPD nest-count, survey-method, and shared-citation audit

**2026-11-10 | P0 source-compatibility check, not a new biological hypothesis.** This audit follows manuscript v0.1 and independently examines the validity of terms like "nest" and "same-colony/year co-census".

## Already verified upstream

The original source generator `research/climate-penguin/work/comparison_audit/audit.py` explicitly filters `obs.type == 'nests'` with measured count **before** constructing `mapppd_unambiguous_site_seasons.csv`. The 2,999 original site–species–year groups, then 2,456 selected method-consistent observations, therefore **exclude adult and chick counts**. Publisher MAPPPD as a whole includes nest/adult/chick rows, so this filter must be cited accurately. Pinned local original input `work/data_audit/mapppdr/penguin_obs.csv`, SHA256 `99503478b42af82c77fe9f1e5e18bb76a91a9636bf84daa59e8997b09e7812e4` from source manifest (raw CSV not necessarily committed).

### Original same-colony/year pairs to audit

Previously frozen `macro_panantarctic_v1/COCENSUS_THREE_PAIR_NICHE_CONTRACT_20261110.md`: 1991–2020 pair-year occurrences **ADPE/GEPE=100**, **ADPE/CHPE=89**, **CHPE/GEPE=168**, total **357 pair-records** (some site-years reused across species pairs). Each individual site×species series has a stable selected `method`, but that alone **does not require both species to share a counting method or publisher citation**.

An independent original `mapppd_unambiguous_site_seasons.csv` method join (no climate response examined) found **one survey-vantage mismatch in 357 comparisons**, **PEIN, 2015 ADPE ground photo vs GEPE ground**. All other 356 comparisons have identical method strings. This is now a disclosed *post-result survey-definition sensitivity*, not a revised preregistered cohort.

## Fixed original publisher source audit

Read MAPPPD 5.0 2026-10-21 **729 original sites, 5,487 observation records**, pinned uncompressed publisher SHA-256s from existing `derive_MAPPPD5_original_macro_source_v1.py` on the *same* repository branch:
- release `8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65`;
- sites `36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34`;
- observations page 1 `cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075`;
- observations page 2 `c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3`.

For all 357 observed source pair/site/years, join each species back to the publisher's `(site_id,species_id,season,type=nests,count,vantage)`, retaining all matched original `citekey`s. Categories: (a) original nest count+method matched for both species; (b) known same vantage; (c) **at least one shared nonempty original citekey**; (d) uniquely mapped source row vs multiple published candidate rows; (e) no source match. No count values or niche-effect p-values are selected or fitted. Report pair cohort support by original colony, region and 250-km source block, and attribute any mismatch rather than artificially calling the pair "simultaneous census".

If same source and same vantage are absent, current manuscript's **"co-censused"** should be softened to **"both species recorded in the same nominal breeding season"**. Even same citekey/vantage does not verify exact day, paired field effort or a confirmed ecological absence. Later papers should require exact survey dates/effort for formal co-census.

**Stop rule:** This is the one publisher provenance check for the already reported three-pair subpanel, not an invitation to fit more climate models or select a subgroup with lower p-values. Preserve original 100/89/168 results as historical, and disclose strict comparable evidence separately. Do not alter MAPPPD all-595 source base, climate data, main, or frozen Paper1/Paper2.
