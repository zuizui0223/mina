# Results draft — Breeding-census geography separates absolute coastal sea-ice variability from shared environmental anomalies

**Study goal:** Does the present geographic distribution of sampled colonial breeding counts produce the same pattern of physical sea-ice fluctuation under absolute and site-standardized environmental scales? This is an observational physical exposure analysis, not an inferential population portfolio effect or forecast of future breeding.

## Sources and comparison

Thirty years (1991–2020) of original August–November OSI SAF coastal sea-ice concentration (SIC) at 39 geographically biased Adélie penguin census site codes (1,170 annual site records) were analyzed in nearshore (0–100 km) and offshore (100–500 km) source-defined windows. Each year’s SIC was aggregated under equal site-code weights, the latest original MAPPPD recorded counts (1,074,279 across differing years 2001–2025, methods and census targets), matched historic-method counts, preserved region totals with uniform within-region site weights, and a Cape Crozier exclusion. Victoria Land contained 26 of 39 source codes and 94.455% of the latest count weight; the 39 codes are not 39 independent ocean observations.

For each fixed weighting, we calculated the 30-year sample standard deviation (SD) of the weighted mean *raw* SIC. As a distinct index of spatially shared anomalies, each site's own 30-year SIC was standardized to mean zero/unit sample SD before a weighted regional average was formed and its year-to-year SD computed.

## Two opposing physical descriptors of the same census allocation

| Observational SIC metric | Equal site-code weights | Latest count weights |
|---|---:|---:|
| Nearshore raw annual SIC SD (percentage points) | 2.971 | **1.707** |
| Nearshore standardized common-anomaly SD | 0.481 | **0.682** |
| Offshore raw annual SIC SD (percentage points) | 1.962 | **1.308** |
| Offshore standardized common-anomaly SD | 0.611 | **0.815** |

Thus the current count distribution corresponds to a smaller amplitude of absolute annual sea-ice fluctuations but **1.42-fold greater nearshore and 1.33-fold greater offshore variance-scale-normalized common anomaly SD** relative to an equal-site geographic portfolio. Removing a linear annual trend at each site yielded nearshore standardized SD of **0.476 (equal)** versus **0.693 (recorded count weighted)**. Counts restricted to the original historic survey method also preserve this contrast (nearshore raw SD 1.702 pp, standardized SD 0.680). Excluding Cape Crozier from all weights did not reverse the pattern (raw 1.658 pp, standardized 0.707).

When original *regional total census weights* were held fixed but all source sites within each region were assigned equal weights, nearshore standardized SD remained 0.645. Across **12,000 fixed-seed within-region reallocations** of the recorded weights, the mean nearshore standardized SD was 0.693 (5–95% mathematical reallocation range 0.589–0.777), which included the original 0.682. Therefore a special beyond-region alignment of giant colonies with synchronously fluctuating nearshore SIC was **not established**. Reallocation quantiles do not represent calibrated ecological p-values.

## Connecting historical anomalies to future physical scenario means

For the same 39 sites and weights, CMIP6 model changes (ACCESS-CM2, BCC-CSM2-MR, CESM2) were added to the observed 1995–2014 nearshore SIC baseline and clipped to 0–100%. Under SSP5-8.5 in 2081–2100, the three-model range in mean physical SIC change was **−11.190 to −6.539 percentage points** with equal site weights but only **−4.053 to −1.681 points** with fixed latest count weights. Weighting by each site's historical survey method produced **−3.994 to −1.756 points**. The smaller weighted mean retreat is compatible with more strongly shared standardized annual SIC fluctuations: projected mean exposure and historical covariance are different attributes of the geographic breeding distribution.

This coexistence is a spatially structured environmental exposure pattern, **not a demonstrated decrease in aggregate breeding variability or a consequence of adaptive site selection**.

## Generality and limits

Ecological insurance/portfolio frameworks (e.g. Loreau et al. 2021, DOI: 10.1111/brv.12756) link demographic buffering to asynchronous performance responses. Here we analyze *environmental* SIC covariance only; the climate-to-nest-count coefficient has failed external validation, so such demographic buffering cannot be inferred. Repeated coastal windows share ocean pixels, the sampled source codes overrepresent Victoria Land, the census weights combine incompatible years and units, and future SIC covariance may differ from the 1991–2020 observed pattern. This cohort is also distinct from the Palmer/Signy subcolony temporal effective-number analysis and must not be equated with it.

## Suggested integration into a single paper

**Results subsection:** “Current colony-count geography simultaneously reduces absolute sea-ice variance and concentrates standardized environmental anomalies.”

**Main figure panel:** Pair historical raw annual SIC SD and standardized shared-anomaly SD for equal versus census weights, with separate panels for the 0–100 and 100–500 km bands. Beside these, display SSP5-8.5 late-century observed-baseline-anchored SIC changes for the same weights and three CMIP models. Supplement should report complete 30-year weighted SIC series, detrending, original survey method, Crozier exclusion, regional-weight preserving counterfactuals and native marine cell overlap.

[Original source and CI verified outputs](https://github.com/zuizui0223/mina/actions/runs/41298114646), artifact 13080017127. Results remain on Draft PR #206 without modifying frozen Paper 1/2 or main.
