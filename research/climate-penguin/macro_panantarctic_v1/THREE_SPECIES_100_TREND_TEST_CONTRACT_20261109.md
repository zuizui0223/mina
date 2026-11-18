# A pre-specified macro association after full 595-site SIC extraction

**2026-11-09 JST, planned before seeing full 1991–2020 macro SIC output.** This is an outcome-aware follow-up to prior 39-site Adélie and small non-MaxEnt GAM attempts, not an independent preregistration. The purpose is to keep the project a **multi-region, three-species macroecological analysis**.

## Central question (one biological estimand)

> Across original Antarctic surveyed colonies with comparable long-term observations, do **site-matched 1991–2020 sea-ice trends** covary with **breeding-nest abundance trends**, and do these associations transfer among Adélie, Chinstrap and Gentoo after removing regional geographic differences?

**Biological response:** for each species×site, OLS slope per decade of `log1p(original observed nest count)` over *observed census years*, using exactly one fixed most-often-used source census method per site-species. This is a **relative observed-nest trend**, not actual fitness, site occupancy or counted population growth rate.

**Marine environment predictor:** for those exact same observed census years, annual August–November mean from the **original 1991–2020 native OSI SAF monthly 25-km nearshore 0–100 km buffer**, with the 595-site fixed 1993-09 source-ocean reference mask. OLS annual nearshore SIC slope per decade (percentage points) on the **same observed years**, not a full 30-year site slope unrelated to the census interval. No backfilling missing years and no copying species count rows to create zeros.

## Locked cohort and support known BEFORE new 595-site climatic fits

The independently source-hash-verified full pan-Antarctic 595-site atlas yields **1,691 originally observed count rows at 410 distinct sites** in 1991–2020, **495 site×species**. Lock the minimum **≥5 actual different census years** and **≥10 calendar years span** per site×species. Before inspecting 595-site ice trend values this produces exactly:
- **100** observed site×species trend series;
- **77** original colony site codes in **7** original broad regional categories;
- **Adélie 37**, **Chinstrap 27**, **Gentoo 36** site×species trends.

Other observed sites remain in the **595-site macro atlas** and 30-year sea-ice study, not falsely transformed into trends. The **single fixed eligibility rule** cannot be relaxed if climate evidence is not significant.

## Primary fixed analysis

1. Keep the 100 source-defined site×species records, with raw observed survey dates/counts and the exact same census-year Aug–Nov SIC. If original SIC month completeness or ≥80% source-native ocean pixels fails in any of the required 4 months for a counted year, mark and retain the site×species as incomplete; **do not patch a new climate source or shift windows after results**.
2. OLS linear slope `breeding_log_nest_trend_per_decade` and `SIC_trend_pp_per_decade` by site×species across the exact same >=5 source year observations. Record all source year counts, survey methods, 1991–2020 span, region, native ocean pixel reference group, and original 100/250 km polar block IDs.
3. Primary association is **one bivariate slope relationship within each species**; report raw Pearson r (species-specific and combined with species demeaning), as well as a **region-demeaned r** within each species and an interpretable linear slope for the original same-species site groups. No quadratic threshold, new lag or nonlinear tuning.
4. For each species with ≥5 independent polar 250km grid blocks, draw 2000 **fixed-seed 250km spatial-block bootstrap replicates**, keeping repeated site×species inside the same block, and report a percentile 95% interval for region-demeaned r. Do not substitute a naive independent-site p-value. If <5 source blocks or bootstrap singular, report **UNDERPOWERED_REGION_ADJUSTED**, not a p-value. Spatial blocks are diagnostics, not independently randomized experiments; region-count is only seven.
5. Track sign/reliability after leave-one-region-out; if correlation sign changes upon omitting a single region, classify **GEOGRAPHY_SENSITIVE**. Do not select the better of three species after seeing the result as the paper's pre-registered winner; this is a three-species descriptive family with source and multiple-testing warnings.
6. No calibration of future 2050/2100 nests from in-sample slopes, and no causal claim of climate-driven inter-colony migration or sea ice controlling true absences. Warming is a separate atmospheric/physical axis to be added with matching geographic sampling and independent validation; vegetation static composite has no 30-year time series and cannot be inserted as a dynamic mediator here.

## Why this is genuinely macro rather than another 25-site pilot

The **ecological survey scope** is full 595 sites / 18 regions; matched 100 **longitudinal observed-site-species** and 7 regions is the actual information available for the **environmental association**, not 2456 pseudoindependent site-years. The 595-site / 120-month original marine climate expansion aims to remove the old 40-site climate sampling bottleneck. A statistically significant r must survive region/space conditioning; failure is a valid macro constraint, not an invitation to add more predictors or different model families.

The first full original source run is [GitHub Actions #42612067836](https://github.com/zuizui0223/mina/actions/runs/42612067836). It must report a success receipt for the entire 71,400 original site×month panel before this analysis can claim actual climate results.

**Outputs when sourced:** source-pinned 100 observed site×species paired climatic/biological slopes, spatial 250km blocks and per-species descriptive region-demeaned bootstrap/leave-region-out results, and a complete Japanese interpretation. Keep `main`, frozen Paper1/2 and climate manuscript v0.6 intact. Stop model p-fishing.
