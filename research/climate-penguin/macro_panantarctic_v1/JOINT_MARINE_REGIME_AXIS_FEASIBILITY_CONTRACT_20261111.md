# Joint marine-regime axis in Antarctic penguin macroecology: source and inference contract

Date: 2026-11-11. Exploratory follow-on in Draft PR #214 based on existing PR #206. Does not modify frozen Paper 1/2 or main.

## Aim: test, do not assume, one "subantarcticization" axis
Test whether surface marine temperature, salinity, and sea-ice concentration (SIC) form one common axis, and whether its cross-sectional site/region structure agrees with the within-site *temporal* changes. An independent competing explanation is more than one environmental axis or differing regional directions. NO predetermined salinity freshening sign: Southern Ocean surface salinity can rise as sea ice retreats, including post-2015 observations.

## Provenance and population gate
- Source-pinned 595 MAPPPD breeding sites/18 original reporting regions/2,456 actually observed fixed-method nests (source build.py). Missing observations are not absences.
- Original EUMETSAT OSI SAF monthly 25km Antarctic marine SIC for 1991–2020, Aug–Nov at all 595 site 100km marine buffers from completed workflow 42612067836 (71,400 original site×month source records, publisher SHA-verified).
- Copernicus GLORYS12V1 reanalysis salinity, water temperature, mixed layer: committed ocean_monthly_2011_2021.csv (106 distinct locations across August–November 2011–2021). Join to the 40 original macro_40 source sites in ocean_grid_support.csv; REQUIRE grid_within_25km True. Do not count other phenology sites as independent MAPPPD macro sites.
- Core PCA only on 2011–2020 site×year means of the four overlapping months, requiring 4 original SIC and 4 GLORYS salinity and seawater temperature values. No interpolation, selective month or fabricated 1991–2010 salinity.
- Static Plantarctica mapped positive vegetation polygon area for 2017–2023 composite at 2km from vegetation_all_location_support.csv. Non-detection is not actual plant absence and composite is NOT a decade climate time series. Static vegetation must NOT be input as 10 fake repeated years in PCA.
- Penguin ratio: only same SITE and SEASON with BOTH actual source count observations ADPE vs GEPE or CHPE vs GEPE. No unrecorded species=zero; same season is not guaranteed same survey date or effort.

## Math and reporting
1. Original source-year-matched 3-column SIC/salinity/thetao matrix. Standardize per variable and compute symmetric eigendecomposition PCA with PC1 positive thetao loading merely for orientation. Report explained fraction all components, loadings and raw pairwise correlations. Do not call PCA physically unique due to site×year pseudo-replication.
2. Source region leave-out PCA under same variable/scaling definition: cosine similarity of PC1 loadings and variation in PC1 fraction. Region sizes should be reported, including one-site regions.
3. Decompose original fitted PC1 variance into between-source-region vs within-source-region contributions. Repeat within-site temporal PCA after removing each site's mean climate. If temporal and pooled eigenvectors differ, a spatial gradient is not a shared climate trajectory.
4. Report 2011–2020 observed source-region×year PC1 averages and numbers of actual source sites for each year. No 18-region time-axis inference if regions lack the matched GLORYS observations.
5. Correlate static positive vegetation mapped area with 2011–2020 mean site PC1 as geographically descriptive only; report n sites and regions. Do not infer greening trend.
6. For true two-species co-counted site-year records, report raw and within-site PC1 × log(1+gentoo nests)-log(1+Adelie/chinstrap nests) correlation only when source region, sites, blocks and source years support it. No p-values; site×year correlations are not independent continental ecological experiments.
7. Explicit overall verdict: (a) 18-region five-variable PCA GO/NO_GO, (b) observed 2011–2020 marine co-gradient supported/unsupported, (c) temporal marine synchronization supported/unsupported, (d) actual penguin composition correspondence source support or NO_GO. No future colony distribution forecast.

## External scientific boundary
- Roland et al. 2024 reported Antarctic Peninsula greening, but Bokhorst et al. 2026 (Nature Geoscience Matters Arising) questioned sampling/vegetation pace; Roland et al. replied in 2026. Never treat the exact 1986–2021 increase as unchallenged local annual source data.
- Sea-ice formation releases brine and melting supplies fresh water, but ice transport, glacial freshwater, circulation, mixing and post-2015 salinity changes can reverse local signs.
- GLORYS marine hydrography is a REANALYSIS, not independent satellite/in-situ confirmation.
- This is descriptive and hypothesis-generating, not causal attribution, species niche preference, climate debt, individual movement, future CMIP6 survival forecast or a proven subantarcticization pathway.
