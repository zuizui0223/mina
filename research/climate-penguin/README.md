# Climate, sea ice and penguin breeding: exploratory progress

Research checkpoint, 2026-10-30. This directory is a draft research lane. It does not replace the frozen Paper 1 / Paper 2 analyses or establish publication readiness.

## Start here

- **[3種のMAPPPD長期繁殖数×実測海氷のマクロ解析・CMIP6統合（2026-10-31）](outputs/breeding_count_macro_v1/REPORT_JA.md):** 元729地点・5,487観測から3種の計数を抽出、40地点海氷と一致した725地点×種×季、56地点×種、連続年467区間、長期傾き54地点×種、CMIP6 224地点×種×シナリオを実行。3種の海氷年変化との関連は探索的で補正後有意なし。アデリーの歴史的減少地に将来海氷減少の大きい地域が偏るが、地域内相関は約0。AEI/REMA陸上環境の追加比較も保存。
- **[最優先研究主題 v3：温暖化はペンギンの繁殖をどう変えるか](RESEARCH_GOAL_WARMING_IMPACTS_V3.md)** — 温暖化→繁殖時期・繁殖数・種構成の実測と条件付き2050/2100生物予測。単なる気候曝露地図・繁殖集中の理論を主線にしない。
- **[観測された同地点の種間繁殖構成変化](outputs/warming_species_breeding_v1/REPORT_JA.md)** — 同じ方法・同じ地点・同年の繁殖数比でGentoo/Adélie 7/7、Chinstrap/Adélie 6/6が長期増加方向。8地点のCMIP6未来気温/SICへ同位置で接続（将来種比は未較正）。
- **[39地点アデリー：長期海氷×繁殖成長とCMIP6の条件付き変化](outputs/historical_ice_breeding_transfer_v1/REPORT_JA.md)** — 1991–2020実測の空間相関 r=+0.622。線形移植は世紀末SSP585に成長率傾向の負方向を出すが、二次モデルでは符号が反転しうる。
- **[同地点・過去2時期の生物応答の答え合わせ](outputs/historical_temporal_transfer_v1/REPORT_JA.md)** — 23地点の1991–2005/2006–2020海氷変化と実繁殖数傾向変化はr≈+0.269。空間係数を時間効果へ単純に転写する較正は未成立。


- **[南極40地点・30年の実測海氷：距離別の地域共通変動（2026-10-31）](outputs/sic_spatial_coherence_macro40_v1/REPORT_JA.md):** 40地点の元SICを30年・4月・近傍／沖合に接続し、6,240件の地点ペアの年次海氷相関を再計算。9月の50km未満r中央値=0.991、250–500km=0.315、1000km以上=0.011。広い沖合では250–500kmでもr=0.797。全件の独立照合と地点除外感度を保存。
- **[実測海氷の地域共通性と局所年変動の分解（2026-10-31）](outputs/observed_sic_covariance_scale_v1/REPORT_JA.md):** Palmer周辺から南の6固定地点×1991–2020年×8–11月の0–100km／100–500km衛星海氷を元値から再集計。9月近傍の分散内訳は年共通87.94%、地点固定10.93%、地点×年固有1.137%。海域が重複するため島内区画の独立海氷とは言えない。独立検証・地理座標・全数CSVを保存。
- **[観測された近隣の海氷変動の同期性と局所差（2026-10-31）](outputs/observed_nearby_sic_covariance_v1/REPORT_JA.md):** 2011–2020年の元衛星SIC、沿岸参照5地点×8–11月×2製品バッファ。年変動は共通成分97%以上だが絶対値の局所差も残る。Palmerの真の5島・繁殖区画ポリゴンとの一対一対応ではない。

- **[繁殖集中×局所ショック：階層別N_effの定量化（2026-10-31）](outputs/climate_concentration_leverage_v1/REPORT_JA.md):** Palmer5島の実効島数3.45→3.08と実効センサス区画数31.06→6.15を分離。共通海氷ショックでは島内集中の増幅は数学的に起きない。Palmer/Signyの5系とρ感度、独立原本照合。
- **[局所海氷差の比較可能性ゲート（2026-10-31）](outputs/within_region_pair_support_v1/REPORT_JA.md):** 同種・同地域の全331ペア/将来条件から50厳密比較ペア（11地点、アデリーのみ）を確保。ただし同じモデル海域格子を共有し、ヒゲ・ジェンツーの厳密対照は未成立。


- **[地域構成と将来気候曝露の交絡・気候格子による見かけの分散（2026-10-31）](outputs/exposure_geographic_decomposition_v1/REPORT_JA.md):** 現在のAEI/REMA無氷地・地形46地点と将来のCMIP6海洋変化を照合し、5地域・25海洋格子指紋へ階層分解。地域内/地域間の相関、全3気候モデル、4将来条件、現地巣数の地点単位・モデル格子単位の実効数を比較。**生態学的な避難所選好や将来の巣数予測とは解釈しない。**

- **[Breeding allocation versus future climate exposure (2026-10-31)](outputs/breeding_allocation_exposure_v1/REPORT_JA.md):** Quantified 2017–2023 observed site-median nest allocation across three penguins against physical CMIP6 warming/sea-ice/salinity changes, compared equal-site, nest-weighted and region-conditioned exposures. Original AEI/REMA 122-site source artifacts supply 46 matched site-code land-context traits. The observed geographic allocation is not a forecast of nest survival nor a mapped subcolony refuge test.
- **[Climate–breeding/vegetation spatial crosswalk (2026-10-31)](outputs/land_marine_colocation_v1/REPORT_JA.md):** 58 original site×species rows across 48 site IDs matched to 106 fixed CMIP6 climate coordinates; 188 unmatched source rows preserved. Includes land-mask QA, CSV, GeoJSON and source-level audit.
- **[Matched-colony conditional future direction audit (2026-10-31)](outputs/future_direction_identifiability_v1/REPORT_JA.md):** 19 strict camera-geographic site×species matches, 76 scenario panels, 912 original two/four-environment model predictions. All 76 panels contain both earlier and later conditional predictions; no calibrated breeding forecast.
- **[Spatial CMIP6 exposure atlas (2026-10-31)](outputs/cmip6_exposure_atlas_v1/REPORT_JA.md):** physical air-temperature, sea-ice and salinity change at 106 fixed locations, grouped into 43 repeated three-model marine-grid fingerprints.

- **[Latest integrated findings: correlations and conditional scenarios](outputs/research_synthesis_v1/RESEARCH_STATUS_JA.md)**: updated inference, salinity, annual NDVI, mapped vegetation support, tracking limits and remaining work. Earlier reports below are dated checkpoints.
- [Full correlation atlas](outputs/correlation_atlas_v1/REPORT_JA.md), [salinity sensitivity](outputs/salinity_sensitivity_v1/REPORT_JA.md), and [conditional response decomposition](outputs/scenario_components_v1/REPORT_JA.md).
- [Salinity site-deletion sensitivity](outputs/salinity_site_influence_v1/REPORT_JA.md): 48 fixed specifications and 656 deletion fits. Adelie retains positive direction after each camera deletion; previous year-deletion sensitivity still crosses zero.
- [Matched-period salinity scenario component](outputs/salinity_scenario_component_v1/REPORT_JA.md): 144 conditional salt-only summaries, with coefficient deletion sensitivity and extrapolation flags. Not a complete future response and not additive to the previous two-variable prediction.
- [Surface-temperature projections and period alignment](outputs/surface_temperature_projection_v1/REPORT_JA.md): nine additional public stores, 30,528 September values, same three model members and salinity cells. Widespread future extrapolation and the tos/top-level potential-temperature definition difference remain explicit.
- [Four-environment conditional scenarios](outputs/four_environment_scenarios_v1/REPORT_JA.md): 288 joint air/ice/salinity/water scenarios, component decomposition, coefficient deletion sensitivity and four-dimensional observational support. Model specification can reverse the direction; these are not calibrated breeding-date forecasts.
- [Observed predictor separation and extrapolation scale](outputs/environment_identifiability_v1/REPORT_JA.md): Adelie water-temperature VIF is about 1.1, but future changes are 8–34 times its conditional observed residual SD. Large projected components do not establish strong observed future responses.
- [Observed nonlinear shape sensitivity](outputs/nonlinear_association_v1/REPORT_JA.md): all 48 one-quadratic-term specifications. Adelie water-temperature curvature remains negative in site/year deletions and the overlapping appendix cohort; this questions linear extrapolation but does not identify an ecological optimum or justify quadratic future forecasts.
- [Current versus previous September associations](outputs/previous_september_v1/REPORT_JA.md): 36 paired-cohort comparisons with mutual temporal adjustment and site/year deletions. Previous-year associations are exploratory and do not establish individual carryover mechanisms.
- [ERA5 snow grid support](outputs/snow_grid_support_v1/REPORT_JA.md): original snow-water-equivalent and land-mask snapshots acquired. Only 14 of 106 nearest cells have land fraction at least 0.5; local breeding-ground snow remains unvalidated, not a missing-value-to-zero join.
- [September regional snow series and associations](outputs/september_snow_v1/REPORT_JA.md): 330 daily 00 UTC snapshots, 1,166 complete location-months, and 36 descriptive land-support/species/cohort comparisons. Land-dominated coverage is too sparse to interpret this as a broad local-nest snow effect.
- [Annual NDVI/count comparison](outputs/vegetation_annual_ndvi_v1/REPORT_JA.md), [mapped vegetation overlap](outputs/ndvi_vegetation_overlay_v1/REPORT_JA.md), and [Landsat support](outputs/landsat_vegetation_support_v1/REPORT_JA.md). NDVI differences are not validated vegetation changes.
- [Completed historical count association analysis](outputs/long_count_seaice_v1/REPORT_JA.md) and [timing support](outputs/long_ice_timing_v1/REPORT_JA.md): 1991–2020 sea-ice acquisition and the 301-interval association analysis are now available, superseding the acquisition-in-progress statements in the earlier checkpoints below.

- **[Earlier checkpoint: vegetation, sea ice, salinity and warming scenarios, 2026-10-30](CLIMATE_RELATIONSHIPS_AND_SCENARIOS_20261030.md):** same-cohort relationships on 169 species/site/seasons; vegetation associations on 246 site/species units; actual 3-model CMIP6 extraction at 106 coordinates. Future environmental changes are quantified; biological future responses remain uncalibrated.
- [Current research objective](outputs/climate_penguin/RESEARCH_GOAL_V2.md): correlation-first work across climate, sea ice, drift, ocean conditions and vegetation, leading to conditional future scenarios. Predictive performance and descriptive relationships are distinct questions.
- [September relationships and conditional historical prediction](outputs/relationship_response_v1/REPORT_JA.md): identical complete cases, between/within-site comparisons, and chronological evaluation using realized heldout-year environments at previously observed sites.
- [Vegetation and observed breeding counts](outputs/vegetation_response_v1/VEGETATION_RELATIONSHIPS_RESULTS_JA.md): 2017–2023 map/count period alignment, regional contrasts, detection sensitivity and species comparisons on common observed site/seasons.
- [CMIP6 future environments](outputs/cmip6_projection_v1/REPORT_JA.md): 27 actual store reads, 381,600 monthly point values, 1995–2014 baseline and two future periods under SSP2-4.5/SSP5-8.5. Three models, one member each; native-grid, uncorrected environmental projections.
- [Exploratory significance](outputs/climate_penguin/EXPLORATORY_SIGNIFICANCE_RESULTS_JA.md) and [wild-cluster sensitivity](outputs/climate_penguin/WILD_BOOTSTRAP_RESULTS_JA.md): 216 post-exploration comparisons. The initial approximate tests had 3 BY-adjusted candidates; none retained BH-adjusted significance in either one-way wild-cluster sensitivity. This is not evidence of no ecological relationship.
- [Year alignment](outputs/climate_penguin/ENVIRONMENT_YEAR_ALIGNMENT_JA.md): source October sea-ice covariates support the current season-start-year environmental join; individual camera dates and settlement calendar origin remain unresolved.
- [Offshore association analysis](outputs/climate_penguin/OFFSHORE_ASSOCIATION_RESULTS_JA.md) and [seasonal sea ice](outputs/climate_penguin/SEASONAL_ICE_RESULTS_JA.md).
- [NOAA tracking audit](outputs/climate_penguin/NOAA_TRACKING_AUDIT_JA.md): public raw tracks obtained, but winter coverage ends in August and cannot calibrate September–October return directions.
- [Satellite common support](outputs/climate_penguin/SATELLITE_MULTISCENE_RESULTS_JA.md): 106 coordinates screened; unequal observation opportunities and limited common clear land constrain vegetation comparisons.
- [Original-pixel reflectance validation](outputs/climate_penguin/REFLECTANCE_ORIGINAL_VALIDATION_JA.md): 28 sampled band comparisons resolve the offset convention for the selected 14 images. No vegetation trend has yet been estimated.
- [Matched-pixel NDVI comparison](outputs/climate_penguin/MATCHED_NDVI_RESULTS_JA.md): seven coordinates, identical clear-land pixels, dates matched within five days, and boundary-mask sensitivity. These are two-date spectral differences, not validated vegetation change or warming attribution.
- [Historical count support](outputs/climate_penguin/HISTORICAL_COUNT_SUPPORT_JA.md): the 1991–2020 scope has 301 eligible consecutive-year comparisons at 33 sites across six regions. The historical sea-ice series and count association analysis are now complete within the specified scope; see the updated links above.
- [Historical observation timing](outputs/climate_penguin/HISTORICAL_COUNT_TIMING_JA.md): 203 of the 301 comparisons have both counts confirmed after September, with stronger regional imbalance. The monthly aggregation pipeline reproduces all 3,200 existing 2011–2020 macro-site monthly SIC values; historical acquisition is now complete; see the updated timing and count analyses above.

## Scope and evidence limits

Settlement, nest counts, breeding success and migration behavior are distinct outcomes. Sea-ice concentration retreat is not necessarily physical melting. Directional drift near colonies is not an observed bird trajectory. Vegetation composites are not annual observations. All current environmental associations are exploratory; source-calendar uncertainties, small cluster counts and spatial/temporal dependence constrain inference. There is no validated future breeding-date projection in this checkpoint.

The broader goals remain open: migration-route identification, validated vegetation and breeding-patch measurements, and climate-scenario calibration; full-period count associations and conditional index scenarios have been delivered. No goal completion is claimed by this PR.

## Layout and reproducibility

The original workspace-relative layout is retained inside this directory:

- `work/`: analysis and acquisition scripts authored during this research.
- `outputs/`: reviewable reports, derived tables, source inventories, checks and compressed daily environmental extracts.
- `SNAPSHOT_MANIFEST.json`: the earlier synchronization snapshot, not a manifest of later additions. The latest synthesis inputs are listed in `outputs/research_synthesis_v1/current_evidence_manifest.csv`.

Python scripts usually resolve the analysis root from their file location. Run from this directory when a script uses relative paths. Requirements vary by task; used packages include Python 3.10, numpy, pandas, scipy, statsmodels, rasterio, pyproj, shapely, geopandas, xarray, netCDF4, zarr, fsspec, requests and Pillow. The inference checkpoint used statsmodels 0.14.6. Dependency locking and a single end-to-end runner are not yet provided.

Raw external caches are intentionally not copied: satellite rasters, large NetCDF downloads, downloaded source documents, and some upstream data. The reports/manifests identify sources, versions and hashes where collected. Acquisition scripts cover many, but not all, inputs; a fresh clone cannot yet reproduce every step without restoring or downloading those inputs. Do not interpret a successful syntax/hash check as end-to-end reproduction. Older reports preserve the chronology; the newest reports linked above supersede their earlier unresolved/negative status where explicitly noted. Some image links in archived reports refer to omitted local previews.

External data and derivatives retain their source-specific licenses and attribution requirements; the repository's code license does not relicense external data. See source inventories and cited data DOIs, including Zenodo settlement data, NOAA/NCEI, OSI SAF, Copernicus Marine and Plantarctica.

## Synchronization

This is the rolling progress PR. At meaningful milestones, update the existing branch, manifest and summary rather than opening a new PR for each analysis. Synchronization does not imply merge or publication. No automatic scheduled task or unattended push has been installed.

The original workspace's `work/climate_penguin/sync_progress_snapshot.py --checkout <checkout>` copies the scoped outputs and scripts into this directory without committing or pushing. It is an additive sync: deletions must be reviewed explicitly. Never run it with source and destination set to the same directory.
