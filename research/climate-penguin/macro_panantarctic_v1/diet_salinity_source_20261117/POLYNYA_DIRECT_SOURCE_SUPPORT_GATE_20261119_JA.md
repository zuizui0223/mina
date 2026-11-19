# 塩分A仮説の次段階：独立ポリニヤ実測の時空間照合を先に検証する

**2026-11-19 JST | mina Draft PR #214 | new source feasibility only, no new isotope coefficient or main manuscript edit.**

## Current verified state

- The original optical δ15N cohort: **860 site×season, 88 source sites, 82 original GLORYS wetcells, 13 reporting regions**, breeding season starts **1996 and 1999–2012**. Source artifact **14328755565** (SHA256 `dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`).
- 2026-11-19 physical 82-cell gate: 0m **82/82**, 50m **68/82**, 200m **39/82**, 400m **8/82**. Full three-way A/B/C comparison is `NO_GO_FULL_ABC_EQUAL_SUPPORT`.
- Actual same-source 693 complete A/B seasons (72 sites, 68 wetcells, 12 regions) and fixed historical hindcast: M0 RMSE **1.38307**, M_S **1.38889**, M_B **1.39506**, M_A **1.47409**. `NO_GO_AB_MECHANISM_WINNER`. [Successful source CI #44541379015](https://github.com/zuizui0223/mina/actions/runs/44541379015). **No further post-hoc salt-depth-radius parameter search.**

## The genuinely different source

Direct coastal polynya observations, rather than ocean salinity used as a polynya surrogate. Candidate published DEEP-AA daily coastal-polynya data (Lin et al., 2024; Scientific Data DOI 10.1038/s41597-024-03848-2). Its published span is 2003–2022 with reported missing period **September 2011–July 2012**. The exact coverage of each requested source day, its projection, product type, QC mask, and grid must be verified from original provider metadata/files, not inferred from publication year.

### Source-first contract

1. Before opening any isotope response or fitting coefficients, retrieve the *original published* DEEP-AA file manifest / data dictionary, DOI/version, native daily date coordinate, true missing dates, source polar stereographic CRS, pixel dimensions, valid sea/ice masks and QC. Record provider checksums when supplied. If original files cannot be fetched or date/projection semantics cannot be verified, return `DATA_SOURCE_UNVERIFIED`; do not substitute a guessed map or annual interpolations.
2. Fix the original 88 isotope site IDs/coordinates and observed breeding-season years only. No new colonies, no nearest observed polynya selected using δ15N. For each real source year y, **preceding winter = June 1–October 31 of y**, five months. Require >=80% of *calendar days with genuinely available native imagery* **and** separately report missing source days, including the 2011–2012 gap. For a strict complete-winter test require **all five months represented with >=80% days each**; do not fill missing months. At least 2003–2010 are candidate years from calendar span, not yet verified observations.
3. Preselect spatial exposure as **polynya-area fraction / valid marine area** within a 100-km geodesic circle around the fixed original colony site, and a separate direct nearshore 25-km descriptive sensitivity. Record the ocean-mask denominator and pixels used; use equal-area weighting and report projected geometry. The 100km radius is a **new prespecified physical exposure** and not automatically the actual foraging area; it must not be tuned by isotope significance. If native data measure polynya presence rather than area, report fraction of valid days with detected polynya, not a fabricated area.
4. Before testing any response, output **real site×season overlap**, unique sites, original source reporting regions, independent polynya pixels/footprints, missing years and 2003–2010 support, and a map of site-to-polynya observation geography. Duplicate pixels/neighboring sites do not count as independent geographic replicates.
5. A mechanism test is only eligible if >=**30 original sites**, >=**6 original source reporting regions**, >=**4 complete distinct source winters**, and **at least 3 independent sites in each of Victoria Land, Wilkes Land and Southwest Antarctic Peninsula** have truly observed polynya exposure. These are minimum *support* criteria, not sufficient evidence of mechanism or power. If any fail, record `NO_GO_DIRECT_POLYNYA_MACRO_SUPPORT` and do not run a pooled 860 regression with filled values.
6. If eligibility passes, only then fit the original optical δ15N proxy against observed polynya activity with same-season sea ice, temperature, source site, and original region×season effects. Use only the identical truly observed overlap rows for the salinity and polynya comparisons. Report original source-wetcell and region cluster sensitivity. No cherry-picked year/region or novel claim of fish vs krill feeding; local nitrogen isotope baseline still unidentified.
7. Direct source may not independently test all original regions or all 860 seasons. Any finding on 2003–2010 is a **restricted historical subset**, not an independent reproduction of Youngflesh's optical response and not a pan-Antarctic causal finding. No 2050/2100 projections from this analysis.

## What a negative result means

- If real polynya observations lack geography/years: **the source cannot test the mechanism**, not proof polynyas do not matter.
- If overlap is adequate but independent polynya activity has no robust conditional association: the *specific polynya-mediated interpretation of the salinity proxy* is unsupported, not proof that polynyas have no effects on foraging.
- If a positive association appears: still cannot infer a diet switch without actual prey, trophic-baseline isotope measurements and foraging footprints.

## Boundaries

The original 860 optical δ15N vs Nov–Feb surface salinity β=+0.8341458 and residual partial R² 2.88% are maintained **as conditional observational association** (13 region t CI [-0.01594,1.68424] includes zero). The 2004-frozen holdout salinity M1 did not improve M0. Neither original nor new source supports fish proportion, a salinity causal pathway, or future penguin abundance forecasts. Main, Ecology Report and Paper2 remain untouched.
