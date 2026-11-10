# Cross-axis overlap gate — original sea ice × mapped vegetation × observed penguin nests

**2026-11-09 JST.** This is an after-result source-support and identifiability audit, not a new confirmatory environmental test or a search for a positive p-value. Linked to Draft PR #213, not warming manuscript v0.6 or main.

## Single question

**How many truly co-located, contemporary original observations remain if the marine count/SIC panel and the terrestrial mapped-vegetation panel are intersected by exact original site ID and species, rather than concatenated as if they were one dynamic model?** Then, **does the spatial association of measured ice with mapped vegetation persist within broad regions?** Only descriptive Pearson r is used; no new biological p-values are tested.

## Fixed inputs and joins

1. Recreate the exact existing, independently QA-checked **661** 1991–2020 marine site×species×observed-year counts via `nonmaxent_sdm/build_source_panels.py`. Original MAPPPD and OSI source blob pins unchanged. Its original actual zero counts remain; missing species/year is never zero.
2. Recreate **197** 2017–2023 modern site×species median-count rows with *positive* Plantarctica mapped vegetation detection in the 2 km buffer. The mapped terrestrial area is a **single 2017–2023 composite** at a site, not a series of annual vegetation measurements or complete surface greening.
3. Restrict the historical marine panel to **2017–2020 observed census years only**, then exact join `site_id + species` to the modern *positive* vegetation panel. Keep one row per actually observed marine site×species×year. Do **not** replicate missing annual vegetation measurements: the land value is an annotated *static spatial context* even when it is repeated beside observed census years; it may include information after a 2017–2020 census.
4. At the site level, check if mapped vegetation area is **exactly identical across species** at the same site. If yes, keep just **one unique value per site** and never treat repeated species or repeated census years as independent vegetation data.
5. Average actual SIC only across the **census years represented in the matched site** (not all 2017–2020 years if a count is missing); source average is not a prospective predictor and is different from a 4-year climate mean. Calculate `cor(site_mean_observed-year_SIC, log1p(site_static_mapped_vegetation_area))` across sites and after subtracting **unweighted region mean** from both variables. No nominal p-value for these environmental correlations.
6. Count number of sites/regions/species and number of independently observed site×years. Declare **NO-GO** for a confirmatory annual 3-axis niche SDM if: vegetation is composite rather than annual; most sites lack all 3 species counts on same years; or region-independent replication is insufficient. This is an evidentiary gate, not a failure of code.

## Source-locked expected support (counts only, set before algorithm implementation)

- Marine 1991–2020: 661 observations / 40 distinct sites / 56 site×species.
- Marine 2017–2020: **70** original observed site×species×year rows, **30 sites**.
- With co-located *positive mapped vegetation*: **63** observed site×species×year rows, **33 distinct site×species**, **25 sites**, **50 distinct actual site×years**; ADPE 48 rows / 25 sites, CHPE 7 / 3 sites, GEPE 8 / 5 sites.
- 25 sites cover **17 Victoria Land, 4 South Shetland Islands, 4 central-west Antarctic Peninsula**, and have recorded species coverage **20 one-species, 2 two-species, 3 three-species sites**. These are **species presence in source records**, not actual species absence.
- Cross-species 2km mapped area values match at 25/25 sites; thus vegetation measurement n is 25 sites, not 63 rows.
- A preliminary independent source data computation gives pooled site correlation approximately **−0.6083**, region-demeaned site correlation approximately **+0.1239**. Confirm exact values in a separately runnable script; any drift → HOLD. These values are spatial descriptions, *not* evidence that warming causes greening.

## Biological interpretation

A three-axis environmental predictor must not be called a matched long-term joint model simply because it has matching `site_id` on a composite vegetation map. A true 1991–2020 joint dynamic SDM requires actual yearly vegetation in the same cells and years, explicit non-detections or survey availability, and repeated species observations with consistent detection/method metadata. This gate should be reported even if it concludes insufficient source support; no additional `k`, time lags, statistical families, pseudoabsences or resistance coefficients will be searched.

Deliver: `matched_63_observed_rows.csv`, `site_25_environmental_context.csv`, `joint_support.json`, reproducible script, and CI source hash/sanity checks. Draft PR #213, main and frozen manuscripts untouched.
