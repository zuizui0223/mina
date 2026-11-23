# Independent high-resolution winter polynya × Adélie nest-count candidate: completed physical-data gate (2026-11-23)

**Gate verdict: physical exposure distinguishable from mean sea ice; pan-Antarctic demographic inference NOT identifiable with sufficient independent replicated groups. NO ecological response model was fitted.**

## Fixed original-source design and actual coverage

- **DEEP-AA** Lin et al. 2024, Zenodo record 13358042, original `SIC60_6.25km_20d.zip` (237 MB, MD5 `f3f958389cc5e67ac1c4e3a6ee164318`). The satellite classifier identifies native 6.25 km coastal polynyas as **positive even Map IDs**; total mapped open water is `Map>0 OR Map==-1 OR Map==-2`, with landfast ice and unknown areas excluded from the open category.
- **Independent continuous sea ice:** NOAA/NSIDC G02202 v4 25-km southern monthly CDR original `cdr_seaice_conc_monthly` (0–1), EPSG:3412, sourced via CoastWatch ERDDAP original data, not an unmeasured 60% open/closed proxy.
- **Original nests:** MAPPPD v5 `DownloadAll`, 5,487 all-species records at 729 sites; Adelie `count_type=nests` and actual nonmissing annual count support. SHA256 `d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89`. Missing census years are not zeros. The ~11 real zero nest-count site-years among primary sites are maintained (Pléneau Island).
- **Fixed exposure:** 100-km original geodesic footprint of each colony, winter June–October y for `season_starting=y`, monthly equal weighting, source month requires >=80% daily coverage. 2003 October has 15/31 source days and is **not complete**; 2011/2012 are unavailable owing to DEEP-AA product hiatus. Thus 17 complete physical winters **2004–2010 and 2013–2022** (DEEP-AA original daily files 2,922 Jun–Oct days in all the nominal 2003–2022 dates).
- **Daily ocean denominator correction (source-physical, before any Y result):** a first run requiring 98% of a static ocean mask suppressed genuine Cape Royds etc. Verified source-only QC identified changing map masks. A revised, explicitly documented extraction uses *daily native available* ocean area and keeps days with >=80% originally defined ocean support, retaining the pre-specified >=80% daily date coverage for each month. First-run QA is retained separately; never compare its lower number of sites as demographic absence.

## Completed source-only counts

| Original-source stage | Site-years | Sites |
|---|---:|---:|
| NOAA/NSIDC SIC, 18 available reference winters including 2003 | **774** | **43** |
| DEEP-AA + NOAA 17 complete winters jointly | **731** | **43** |
| Primary census candidates (>=4 distinct years; >=8-year count-span) | **284** actual observed nest site-years | **32** |
| Same primary nest site-years also with complete five-month winter physical pairs | **271** | **32** |
| High-quality consistent survey vantage + maximum accuracy code <=2 within original source candidate | **158** matched site-years | **14** |

**Independence:** 32 original named sites form 7 centroid groups using 100-km adjacency and **only 6** geographically connected groups at the conservative **200-km adjacency** for possible overlap between two 100-km physical footprints. Restriction to 14 constant-vantage/accuracy-code<=2 sites yields **four** 200-km groups. This fails the *frozen before output* requirement of at least eight independent groups; do not fit/publish a pan-Antarctic nest-count effect with six or four clusters.

## New result: physical *measurement* distinction, NOT penguin population evidence

All correlations below compare physical proxies **after removing site and calendar-winter effects**. Fixed effects in the unbalanced census sample were removed by a full-rank pivoted QR. The original demographic response is never used as an explanatory or fitted variable in these calculations.

| Actual source panel | Rows | Adjusted corr: coastal polynya vs measured NSIDC mean SIC | Adjusted corr: total open water vs (1-SIC) | Coastal polynya variance remaining after additionally residualizing SIC |
|---|---:|---:|---:|---:|
| Balanced 43 sites x 17 winters, physical-only | **731** | **+0.0073** | **+0.9787** | **99.995%** |
| Census-supported 32-site unbalanced original site-years | **271** | **+0.0905** | **+0.9805** | **99.181%** |
| Constant-vantage, accuracy<=2 census subset | **158** | **+0.1100** | **+0.9798** | **98.790%** |

Census-supported 271 site-years have **1.978 percentage points** of coastal-polynya SD after site/year fixed-effects removal, still **1.970 pp** after conditioning on annual mean NSIDC SIC. This means a spatially structured winter polynya *physical* signal exists independently of the local mean ice fraction under the joint source definitions and date supports. It does **not** show that the local polynya class causes nesting success, population growth, or persistence. Product grid sizes, sea ice masks and class thresholds differ (DEEP-AA 6.25 km vs NSIDC 25 km). Correlation with independent open water provides an expected physical-data QA, not a biological replication.

**Observed nursery/census support is uneven among spatial groups:** group 0 has 13 sites but 71 observed 2004+ count years; group 2 (Ross Island-linked) has 8 sites but 106 count years (95 passing strict site quality); two groups contain a single site each, one with four census years. This reinforces why 271 source rows do not approximate 271 independent climate contrasts.

## Reproducibility

Successful source jobs:
1. DEEP-AA original daily extraction and dynamic ocean masks: https://github.com/zuizui0223/mina/actions/runs/45098580921
2. NOAA/NSIDC original 18-winter monthly griddap source and 43-colony match: https://github.com/zuizui0223/mina/actions/runs/45098221668
3. **Independent Actions source-only audit, with original source ZIP re-downloaded and sample QR re-projection:** https://github.com/zuizui0223/mina/actions/runs/45099456982

Source scripts: `scripts/extract_adelie_2003_2022_DEEPAA_coastal_and_open.py`, `scripts/extract_adelie_2003_2022_NSIDC_v4_sic.py`, `scripts/audit_ad_2004_2022_271_matched_source_physics.py`. The action outputs hold native-source monthly/annual physical series and original census-only quality audit in inspectable CSV/JSON, preserving source checksums.

## Publication decision

**NO-GO for a new independent pan-Antarctic polynya–nest-count coefficient with this 2003–2022 panel**, because 6 independent groups (4 high-quality) miss the frozen spatial replication threshold. Do not search alternative radii, year windows or quality cutoffs to get an interesting p-value. The physical distinction is a valuable measurement feasibility result for future multi-region monitoring; it is not independent ecological evidence. The current v0.7.5 Adélie optical isotope manuscript, Draft PRs #214/#216 and other analyses remain unchanged. A future study would need quality-standardized, non-overlapping census time series across additional geographic groups, or a smaller geographic claim with independently measured demographic outcomes.

