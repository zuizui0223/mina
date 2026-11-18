# 2026-10-29 — Adding Antarctic warming impacts without post-hoc FDR rescue

**Status:** original data and intermediate calculations; no confirmatory climate mechanism, climate-attribution model, or future penguin forecast. Only draft PR #206; frozen Ecology Paper 1 PR #189 and physical-island predator-access Paper 2 PR #199 are not reopened.

## 1. What the 216-test result does (and does not) mean

The existing 216 post-exploration combinations cover 18 environmental covariates, 3 penguin taxa, 2 source-calendar cohorts, 2 adjustment models. A direct new audit of the committed `wild_cluster_sensitivity_results.csv` finds 214 estimable rows (2 insufficient), including 148 models with at most 12 **site** clusters and all 214 with 6–10 **year** clusters. Lowest observed one-way site-wild p = 0.001953125; year-wild p = 0.00390625; largest of site/year p for each model has minimum **0.015625**. Corresponding minimum family-wide BH adjusted q: site **0.10546875**, year **0.3375**, max-p **0.606741573**. No comparison survives BH after the full family.

This is a small-cluster and multiplicity-limited post-exploration screen, **not a negative test of climate biology**. For instance, a two-sided ±1 sign-flip statistic with 7 site clusters has only 128 sign configurations and an attainable nonzero two-sided p floor of approximately 2/128=0.015625 under the symmetric draws. Do not relax the 216-comparison family after reading effects. A future biological model can predefine **one warming exposure**, one outcome, sample support, effect-size interval and regional controls, but it must be labelled a new post-exploration hypothesis until evaluated on independent source support.

## 2. Source-origin 40-site sea ice: seasonal trajectories are not uniform

Original committed `macro_monthly_seaice_2011_2020.csv`: 40 sites × 10 years × Aug–Nov × 2 concentric windows = 3,200 validated complete monthly observations. Recomputed individual-site linear slope for original nearshore (0–100 km) monthly SIC, without selecting the trend sign.

| Month | Negative / 40 site slopes | Median site slope (SIC percentage points per decade) |
| --- | ---: | ---: |
| August | 36/40 | −3.4442 |
| September | 14/40 | +0.4818 |
| October | 31/40 | −0.8400 |
| November | 23/40 | −0.5638 |

The **40 sites are not 40 independent grid-cell climate replicates**: exact matching complete nearshore monthly series include `BRDM–BRDS` and `LLAN–PTHO`, leaving only **38 distinct 2011–2020 fingerprints**. Spatially correlated remaining series are also not independent. The first 10-year interval is not sufficient for anthropogenic trend attribution. A linear slope in bounded monthly SIC is also sensitive to floor/ceiling effects and to regional shifts; do not infer a 40-island climate law or homogenized loss.

## 3. Count chronology removes most cross-region comparison support

Original 1991–2020 MAPPPD matched constant-known-method Adélie count intervals: 301 positive count pairs across 33 sites / six source regions. Both years' census dates verified **after September**: 203 intervals at 26 sites / three source regions, of which **187 (92.1%)** are Victoria Land. For exposure windows through November, strict *both after November* leaves 191 intervals across 23 sites / three source regions, **187 (97.9%)** Victoria. No substitution of missing source month with the standard survey season is permitted.

For 2011–2020, the count×September SIC overlap contains 76 original adjacent pairs; strict chronologically verified after-September support is **61 pairs at 16 sites in 3 regions**, including 55 Victoria Land pairs. Early descriptive count-growth versus year-on-year September SIC-change regressions flip depending on pooled versus within-site adjustment; these post-exposure slopes are **not evidence of a climatic causal effect**, especially given sparse non-Victoria comparisons, interannual dependence and potential time/confounder effects. Do not select a favorable sign and call it the temperature response.

## 4. First source-verified 30-year warming data

Exact original response from the Open-Meteo Historical Weather API, choosing **ERA5 only** (not the changing `best_match` combination), 1991-01-01 through 2020-12-31, 2 m air temperature, UTC, site-nearest 0.25° grids, and no elevation downscaling. The 3 source prepilot coastal sites were **ADAR, ARDL, BECH**, fixed before fetching. Actual authenticated GitHub Actions source retrieval: [successful source run #40856533117](https://github.com/zuizui0223/mina/actions/runs/40856533117), 3 of 3 exact source response locations, 3 distinct API grid coordinates, raw source-batch SHA256 `dd5fea2310b3dec24d8b5c934a2a5fbe59aad8fa7ed6d4bddd7789a03250be1c`.

3-site site-level median **full-year slope +0.2171°C per decade** and **August–November slope +0.1750°C per decade** over 1991–2020. Both medians include only three sites and are *not* Antarctic-wide estimates. The selected three full-year slopes are positive. They measure ERA5 reanalysis-grid exposure trends, not field-measured local temperature, forced attribution or penguin demography. The exact 40-site source and grid duplication support must be audited before comparing climate with penguins.

Reproducible source code and full 40-site source command: `work/climate_penguin/acquire_era5_warming_macro_v1.py --mode full --output <directory>`. Outputs include original compressed API response, exact requests, SHA256, 40-site monthly series and 1991–2020 / 2011–2020 descriptive climate trends.

## 5. Primary post-exploration effect design and stop rules

- **Climate exposure:** 1991–2020 ERA5 2m temperature site-specific trends plus monthly seasonality, independent of breeding outcome selection; 2011–2020 site-specific near/far SIC monthly trends separately. Temperature and ice are **not independent physical causes** (reanalysis and sea-ice state are coupled).
- **Biological outcome:** published unchanged-method exact-positive MAPPPD Adélie consecutive-season log count ratios, with month status preserved. Pair current September air anomaly to count interval only when both counts are strictly later than September; use August–November exposure only when **both later than November**. The 301 unverified-month intervals are a distinct descriptive scope, not eligible causal pre-exposure observations.
- **Effect metric:** `delta log(count)` per +1°C `delta September temperature`, within-site and within-site+year contrasts, retain zero/nonzero change and leave-one-site-out ranges. **Explicitly model calendar and regional support**; no uncorrected p-value threshold or 216-test subset mining. New `analyze_warming_count_link_v1.py` runs only after full ERA5 source acquisition; it must not announce an effect if 40-site source data are missing.
- **Island mechanism remains HOLD:** changing snow, ice-free rock/available patches, migration paths, marine prey and productivity are separate mechanisms. A temperature/count association alone neither measures the breeding-patch capacity nor validates predator × flightless access. Physical island area and penguin occupancy/space must be co-measured to support that claim.

**Priority:** obtain the fixed 40-site ERA5 source and original count join, quantify the supported effect sizes and region/time uncertainty, then decide whether the observational signal justifies an independent-source holdout. No change to published phenology claims, the frozen Ecology submission, or already-failed island/predator source gates.


## 6. Actual full-source 40-site temperature and count execution (2026-10-29, executed)

**Open-Meteo-mediated ERA5 reanalysis delivery and derived source audit succeeded** in [Actions #40856645581](https://github.com/zuizui0223/mina/actions/runs/40856645581), with full daily 1991–2020 source, 40 original sites, **30 distinct ERA5 API grid coordinates** (not statistically independent), and 40×30×12=14,400 monthly source-site windows. Raw compressed API response, URL/response hashes, monthly and season-year climate summaries, site trends and source checks were saved in original [artifact #12889668094](https://github.com/zuizui0223/mina/actions/runs/40856645581/artifacts/12889668094).

Descriptive 30-year site-slope median (°C/decade): **full-year +0.44016** (39/40 positive); **Aug–Nov +0.34029** (38/40 positive); Aug +0.82321 (33/40 positive); Sep +0.20896 (37/40 positive); Oct +0.41149 (38/40 positive); Nov +0.02356 (21/40 positive). These are *unadjusted temporal slopes*, not anthropogenic attribution, formal confidence intervals, or 40 independent ecosystem replicates. Some ERA5 locations are coastal coarse grid analogues and not penguin nest microclimate measurements.

**Original MAPPPD count × ERA5 pairing actually executed** using that verified full-source artifact on [Actions #40857800306](https://github.com/zuizui0223/mina/actions/runs/40857800306), [numerical original output artifact #12889423234](https://github.com/zuizui0223/mina/actions/runs/40857800306/artifacts/12889423234). All **301 of 301** originally qualified 1991–2020 consecutive-season count intervals have valid September temperature pairs. Strict timing support remains 203 after-September pairs, 191 after-November pairs, with overwhelming Victoria Land concentration.

The below numbers are `delta log(count)` **per +1°C year-to-year temperature change**, not long-term warming causal coefficients. Source-verified outputs and leave-one-site-out ranges:

| Chronology + temperature | Sites / intervals | Site fixed | Site + year fixed |
| --- | --- | ---: | ---: |
| Sep temperature, both counts after Sep | 26 / 203 | **−0.00548** (LOSO −0.00778 to −0.00353) | **+0.02666** (LOSO +0.01846 to +0.04484) |
| Aug–Nov temperature, both counts after Nov | 23 / 191 | **+0.01986** (LOSO +0.01398 to +0.02389) | **+0.09134** (LOSO +0.06676 to +0.11034) |
| Sep temperature, **Victoria only** | 20 / 187 | −0.00280 | +0.05919 |
| Sep temperature, **other regions** | 6 / 16 | −0.03005 | **not identifiable** |

The September coefficient changes sign when the common year effect is included: **the annual biological association is not stable to how shared year variation is treated**. A year FE can also remove actual spatially shared climatic variation, so do not automatically declare the year-adjusted coefficient the more causal estimate. The Aug–Nov strict cohort is 187/191 (**97.9%**) Victoria; the apparent positive coefficient is not an Antarctic-wide replicated warming effect. LOSO describes which monitored sites leverage an *observed fitted slope*, not an interval with valid spatial/temporal dependence calibration. No multi-source causal model, formal p-values or confidence intervals were reported for this temperature/count fit.

**Decision:** Significant source-level progress on the **exposure** side (climate warming signal measured in ERA5 and month-specific ice heterogeneity), but **breeding response to warming is not confirmed**, and physical-island substrate/competition mechanisms are still unmeasured. An independent south/peninsula versus Victoria count chronology and coast/ice-free land data are necessary before asserting a general Antarctic breeding mechanism.

The source-verified machine-readable summary with run IDs and hashes is `CLIMATE_WARMING_ERA5_40SITE_SOURCE_RESULT_20261029.json` in this directory, not to be confused with the original raw-source run artifact.
