# Exact 23-colony marine exposure audit — 2026-11-24

Executed locally on original source-derived marine archive [run 42961084667, artifact 13829236358](https://github.com/zuizui0223/mina/actions/runs/42961084667/artifacts/13829236358); SHA256 `64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5` matches GitHub digest. Original 16,464 rows / 588 sites / 1993–2020; all four Aug-Nov source months. Target fixed union 21 endpoint sites + ARDL/LION/PCHA same-year three-species panel = 23 distinct sites. Exact site IDs, coordinates (absolute difference <1e-7 degrees), source regions and uniqueness checked. All 644 site-year records recovered, 17 distinct GLORYS native wet cells. Original OSI SAF sea ice and GLORYS salinity/thetao. Reanalysis is not direct in-situ or foraging exposure. No outcome-climate regression or causal attribution.

## Fixed physical window comparison
1993–2000 versus 2011–2020, each site weighted equally. Early biological endpoint window starts 1991; 1991–92 GLORYS absent; these are physical period means, not source-matched count medians.

| Region | Sites / native wet cells | Δ SIC pp | Δ salinity | Δ thetao °C | Freshening sites |
|---|---:|---:|---:|---:|---:|
| South Shetland Islands | 11 / 9 | -0.5494 | -0.0967 | -0.0575 | 11/11 |
| Central-west Antarctic Peninsula | 12 / 8 | -1.7390 | -0.2241 | -0.0021 | 12/12 |

SIC declines at 19/23 sites. Salinity negative at all 23 (17 marine cells); cell-equal regional mean salinity changes -0.0928 and -0.2276. SST is not uniformly warming for these site-specific Aug-Nov source windows. No pan-Antarctic generalization or claim of anthropogenic causal freshening. Previously observed regional nest-change totals (-11,507 and +6,118) have opposite directions despite common freshening; those totals cover observed species subsets only.

## Match actual same-year three-species counts, rather than interpolate
Reconstructed 34 unique co-survey site-calendar-years from archived strict original pair source blob `7e86b2eb5f5a4e012f128101ebec02d51cbfe41c`. Compact table FNV-1a b59e253c, SHA256 b2f164ef5fd809a6a9844ffdccd620985bee3bbd8bd1c197d0cbcc4f4e25ec35. All 34 marine rows match exact site/year; max original recorded SIC difference 0. Count records have same year, source citation/method, not necessarily same date or verified census effort. Do not assume year means austral season start.

| Site | Common census years | First→last total count change % | All-year fixed-window Δ salinity | Salinity slope / decade on actual census years | SIC slope pp / decade on actual census years |
|---|---:|---:|---:|---:|---:|
| ARDL | 21 | +37.670 | -0.078204 | +0.021924 | -0.731529 |
| LION | 7 | -25.248 | -0.122999 | +0.132607 | -9.258203 |
| PCHA | 6 | +27.724 | -0.231311 | -0.212399 | +6.260238 |

Trend signs are not equivalent to physical fixed-window differences: on irregular observed census years, e.g. LION slopes positive for salinity whereas full annual period means decline. On the 33 common observations with a previous-calendar-year marine row, shifting the physical year changes the ARDL SIC slope from -1.8600 to +0.0751 pp/decade and PCHA salinity slope from -0.2124 to +0.0409/decade. This is a date-label sensitivity, not selection of a better model. No effect of climate on counts estimated. True dates and independent geographic replication remain insufficient.

Independent recalculation of six regional mean changes (stdlib statistics) and nine site climate trends (pairwise covariance slope identity) max absolute differences 1.776e-15 and 1.111e-16. Original count table used once; not independent biological replication. Local `peninsula23_marine_exposure_20261124.zip` SHA256 `6b4e125d88b5650bce7290fb31e419de8a143438f87a66b995f878e825aec5bf`; includes executed analysis script, input compact rosters, 644 physical rows, 34 matched count-year rows, summaries, sensitivity and receipt. Original full publisher archives not republished.

## New direct polynya source retrieval
[Commit 591f0df](https://github.com/zuizui0223/mina/commit/591f0df14cdc1cbcbdc0bd64aadf771a423cf2a6), [run 45400435208](https://github.com/zuizui0223/mina/actions/runs/45400435208). Same canonical extraction functions as previous original 439/85 study, pinned code blob 4cec92b98728dd5538a3d2671dc122e4b16a56bb. Publisher-recommended DEEP-AA ZIP MD5 f3f958389cc5e67ac1c4e3a6ee164318 and SHA256 b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9; source acquisition checksum step completed successfully. 23 colony centres, June-Oct 2003–2020, 100km primary / 25km secondary; native areas corrected for projection, real marine denominators, minimum 80% actual calendar days per month and all five months. 2011–12 unavailable as full winter windows. Extraction still executing at checkpoint; no completed new polynya values asserted here. Physical-only output intended; no isotope observations or plant temporal responses created.

No main merge, frozen manuscript revision or restricted AADC source publication.