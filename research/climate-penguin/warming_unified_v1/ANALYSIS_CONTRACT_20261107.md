# Warming-unified v1: single climate/penguin manuscript, cohort freeze

Date 2026-11-07. This is a **post-result harmonization** of previously viewed primary observations. Not independently preregistered, not demonstrated climate causality, not a validated future breeding forecast.

## Main ecological question

Do Antarctic penguin breeding-community composition, marine food-niche separation and seasonal breeding-time separation respond in the same way or at different temporal/spatial scales to sea-ice change?

Biological outcomes are primary. Legacy UK JNCC breeding concentration is a separate paper and is NOT climate main evidence.

## Source-pinned inputs

- Strict same-location pair source: warming_species_breeding_v1/matched_species_breeding_change.csv, Git blob f17b4a21e9e5a045a40f5a4af9019e3bbc011758
- Site-specific observed long-term trends: warming_species_breeding_v1/historical_species_site_trends.csv, blob 2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b
- Six-site CMIP6 co-located future physical: warming_species_breeding_v1/future_climate_coobserved_sites.csv, blob 97ae24e98a0cb5f6b36e275d036cb4b71c953312
- Signy 3 species x 9 shared 2001–2009 seasons, source stomach fish/(fish+crustacean), original GOPT Aug–Nov SIC: signy_diet_components_v1/species_season_components.csv, blob 715364538b0542cf1198e9a2ab0ae2133495ba9a
- Signy published 17-season source annual mean hatching days, Adélie/Chinstrap gap and SIC as ice10 (= actual percentage/10): hatching_gap_climate_v1/signy_17_seasons.csv, blob f12581366ce908bafec1bd1b450efe8f41eeb605
- Independently earlier source report for six strict same-site positive colonies and observed-year versus full-30-year SIC: niche_timescale_divergence_v1/REPORT_JA.md. This is a verified historical report, not an independent source experiment. Same six sites are ARDL BISC LION LLAN PCHA PETE in 2 regions.

All paths relative to research/climate-penguin/outputs, except this contract. Original source reports are preserved.

## Fixed joint analysis (new quantities not opened before commit)

1. Keep exactly six historically confirmed Adélie–Gentoo co-breeding sites with strictly positive counts at every shared monitored year. Validate both species' opposite absolute trend signs using source reports; do not count 13 log1p pairs as 13 replacements. Verify original 1991–2020 Aug–Nov SIC slopes are negative all six, but matching observation-year September SIC trends are positive in 4/6, as source report already recorded.
2. Filter 6 original site IDs x four future SSP/horizon conditions =24 source scenario records. Tabulate site-equal average future 3-model ensemble tas °C, sea-ice SIC pp, salinity sos in ORIGINAL CMIP6 units, plus all-model sign consensus. Do not convert to future nesting populations or frequencies.
3. Join by exact season-start year the 9 original Signy three-species diet means (2001–09) and independently sourced 17 annual Adélie–Chinstrap hatching-gap records. Require all 9 and verify published GOPT SIC equality between diet and hatching sources to ±1e-5 pp. Nine climate years, NOT 772 independent climate trials.
4. Calculate a pre-specified paired nine-year descriptive axis comparison: D_fish = Gentoo mean fish fraction – average(Adélie and Chinstrap mean fish fractions), G_hatch = Chinstrap–Adélie mean hatching days. Report means, Pearson r(D_fish,SIC), r(G_hatch,SIC), r(D_fish,G_hatch), r(each absolute hatch date,SIC), leave-one-year-out ranges for first two, and difference of absolute correlation magnitudes. This difference is **not a newly confirmatory hypothesis test**: previous individual axis correlations were known. No selective p-value search.
5. Evaluate land habitat/vegetation separately as a source-support gate; annual NDVI imagery around colony points is not validated as vegetation-only pixels within nest polygons. This axis is marked unidentifiable rather than assigned 0 effect. Historical salinity/SST are climate context only unless temporally matched and predictive performance established.
6. Keep source-year/geographic coverage, ecological overlap, model grid reuse, and prior negative transfer diagnostics visible. Temperature and SIC future projections are physical-only. Freeze Paper1/Paper2/main and prior JNCC full paper; no BTO correspondence or new data request.

## Output

Source-locked 9-row same-season niche table, 24-row six-site future physical table, QA JSON, Japanese interpretation, unified English manuscript outline and full draft in this warming folder. State historical evidence, new paired diagnostic, unsupported causal/forecast claims separately.
