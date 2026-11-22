# 塩分×アデリーδ15N光学proxy：冬ポリニヤ(A)・表層成層(B)・陸棚深層水(C)を識別する物理ソース事前ゲート

**2026-11-19 JST; mina Draft PR #214 exploratory supplement only.** This is a pre-outcome physical-depth-coverage contract. Main, frozen Ecology Report, Paper 2 and submitted manuscripts are not changed. Existing regression outcomes were already examined in earlier work; this is not a new preregistration or independent discovery.

## 0. Source and fixed study cohort

- Biological cohort is the original-author-derived **860 distinct Adelie Landsat site×breeding-season optical δ15N proxy** from Youngflesh et al. (2026), Zenodo 17409948, original 256425816-byte ZIP MD5 e29a2f68c84e3a515044d554540def2f; original derived artifact **14328755565**, SHA256 dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205.
- 88 original sites, **82 unique GLORYS wet grids**, 13 original source reporting regions, season-start years 1996 and 1999–2012. Exact original site×season coordinates and rows must not be replaced, backfilled, or counted as independent spatial replicates.
- Frozen original GLORYS12V1 monthly **202311** source: `https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/GLOBAL_MULTIYEAR_PHY_001_030/cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr`. Original `so` and `thetao` variable names; actual `elevation` coordinate, no assumed exact nominal depth. Extract with *original recorded wet-grid indices*, never nearest replacement wet cell or land-centered interpolation.
- Breeding season y = November y through February y+1. Previous winter = **June–October y**; summer ocean = Nov y–Feb y+1. A lagged winter measurement is **not** same-season dietary exposure, and a winter ocean cell is **not** proof of a nearby polynya.
- Original M0: optical δ15N proxy ~ observed image DOY, DOY² + Nov–Feb NSIDC G02202v4 150 km SIC + Nov–Feb GLORYS surface thetao + site FE + region×season FE. M1 adds Nov–Feb GLORYS surface salinity. Prior M1 beta=+0.8341458 per salinity unit, partial R²=.02880, 13-region cluster t CI [-.01594,+1.68424]. **Do not refit or reinterpret these as fish proportion.**
- The 2004-frozen 2005–2012 temporal holdout M1 site-equal RMSE 1.40486 exceeds M0 1.39165. Do not project future diet from the observational salinity coefficient.

## 1. Freeze physical feasibility before testing any diet outcome

Run **one depth-coverage preflight** on all 82 original wet cells using **6 source-prespecified months**: July 1996, July 2003, July 2005, July 2010, December 2005, February 2006 (the last two represent an actual Nov–Feb winter-following seasonal pair, not six independent seasons).

- Extract the *same* 82 cells × 6 calendar months × 4 **nearest real model levels** to 0, 50, 200, and 400 m, for both `so` and `thetao`; record the model's actual depth, unique wet-grid IDs and original region. No substitute offshore location; missing below-bottom = missing, **never a numeric 0**.
- The shared full-panel A/B/C design **passes physical depth support** only if all of the following are true at the source 2005-12 probe: surface availability >=80/82 wet cells; 50m availability >=70/82; 200m availability >=58/82 (~70%); 200m support spans >=8 genuine original regions and at least 3 unique wetcells in each of Victoria Land, Wilkes Land, Southwest Antarctic Peninsula. The 200m gate applies to the physical 82-cell denominator, not repeated seasons.
- If not passed, stop claim that 860 rows can enter **equal-support** three-mechanism comparison. Report the actual complete-case site/region/year support and use separate exploratory physical diagnostics. Do not widen deep-cell radius, shift cell location, interpolate into shallows, or secretly change threshold because the result is inconvenient.
- For 400m, report coverage only. Do not use 400m as substitute for the prespecified C=200m test or tune depth to outcome.
- Errors retrieving Zarr, timestamps, coordinate dimension names, or original archive are **`DATA_RETRIEVAL_UNVERIFIED`**, not a negative ecological result. This preflight must produce a numerical receipt with depth/region support before the mechanism-selection test.

## 2. Competing physical candidates and their falsifiable predictions (only AFTER source coverage gate)

| Candidate | Prespecified physical proxy | Necessary but not sufficient prediction | Why not causal identification |
|---|---|---|---|
| A: preceding winter brine/polynya regime | June–Oct same-season-start-year 0m salinity; *independent* coastal polynya occurrence/nearby footprint for actually covered years | Stronger winter-vs-summer salinity association near independently identified polynyas | Winter surface salinity cannot by itself distinguish brine rejection, advection, melting, sea-ice formation, or foraging |
| B: summer fresh surface stratification | Mean Nov–Feb model `sigma0(50m)-sigma0(surface)` from same-cell temperature and salinity with TEOS-10 GSW; MLD as sensitivity | Source-coincident salinity signal attenuates/changes after density stratification proxy on the same complete cases | Density can reflect summer heating as well as freshwater; not direct glacial runoff. `rho50-rho0>0` denotes greater stratification |
| C: shelf deep-water intrusion | Same-cell 200m thetao **jointly with** 200m salinity at Nov–Feb, no forced deep level at shallow site; 400m supplementary | Paired warm/salty water-mass signature explains local cross-season association better than surface-only candidate on shared cells | CDW may occupy >200m and nearshore shelf bathymetry constrains wet support; 200m salinity alone is not proof of CDW or upwelling |

**Important:** These physical processes need not be mutually exclusive: CDW can drive glacial melting and stratification, while polynyas modify brine/freshwater budgets. A single highest R² is not evidence of exclusive causation. Mechanism baseline δ15N and optical calibration may account for the association without any fish/krill change.

## 3. Outcome-stage design, locked pending physical receipt

- Only original complete-case **same site×season** rows for A, B, C and M0/M1 enter a fair comparison. Show retained site, wetcell, reporting region, and source seasons *before* modeling. If a paired exposure has no 4 Nov–Feb months or 5 June–Oct months, mark missing; no invented year.
- Fit source-conditional explanatory **M0, M1** and predeclared augmented A/B/C candidates on *identical outcomes*, site and region×season FE. Standardize each added continuous predictor on the **training/complete-case source**; preserve actual physical units in receipt. Penalize model-complexity differences and report multicollinearity; avoid in-sample R² winner claims.
- As a *separate* check, use the previously frozen 1996–2004 vs 2005–2012 known-site temporal holdout with FE fit only on training. Predict heldout isotope proxy using contemporaneously observed predictor physics, not target-year region×season FE or target Y. Main performance is site-equal RMSE and paired region-reselection uncertainty; a mechanism only qualifies as **predictive physical proxy** if it beats M0 and M1 with stable heldout loss difference. This is retrospective known-covariate hindcast, never a future food-web forecast.
- Prior alternative region signs (Victoria, Wilkes positive; southwest Peninsula negative) are **post-hoc observations**, not independent validation. Test the fixed sign pattern only as a falsification; require >=3 independent original wet cells per candidate region and a coherent physical signature before interpreting.
- Any test based on the DEEP-AA daily polynya mask is a **time-limited replication** (2003–2022 with missing 2011-09 to 2012-07). It cannot provide validated yearly polynya labels for all 860 seasons. Use documented `SIC60_6.25km_20d` subset without fabricating missing time.

## 4. Literature and alternative explanations

- Youngflesh et al. 2026, `10.1016/j.cub.2026.06.028`: satellite guano spectroscopy, sea ice and diet. The new analysis **reuses** a proxy from their original imagery, not independent diet data.
- Arrigo & van Dijken 2003, `10.1029/2002JC001739`: polynya productivity and East Antarctic Adelie colony association, **already known**.
- Lin et al. 2024, `10.1038/s41597-024-03848-2`, DEEP-AA Zenodo `10.5281/zenodo.11379147`: coastal polynyas, day-by-day, with coverage gaps.
- Michelson et al. 2023, `10.1002/lno.12446`: amino-acid-specific isotope baseline variation in Adélie history is non-trivial.
- WAP CDW/water-mass work `10.3389/fmars.2019.00144` and `10.1098/rsta.2017.0164`: intrusion, melting and upper 200–400m source properties.
- Original independent POM δ15N station overlap was only **20/860** within 100km same source breeding season, and source SCAR direct diet geographically collapses to only a few localities; therefore **isotope baseline vs trophic-choice identity remains unresolvable** with the 860 optical proxy.

**Decision rule:** first physical probe; if the source-depth-support gate fails, issue `NO_GO_FULL_ABC_EQUAL_SUPPORT` and do not claim an A/B/C biological winner. Even a passed physical gate makes `GO_MECHANISM_IDENTIFICATION` false until same-support statistics, temporal transfer, spatial controls and baseline caveats are addressed.
