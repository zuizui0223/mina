# 2013–2021真の未使用年によるポリニヤ負方向の検証：L7撮影支持ゼロ、L8目録・新分光較正・旧糞画素地理・実QA検査まで実行

**2026-11-20 JST | mina Draft PR #214 | new L8 is a separately frozen alternate-sensor track, not a rewrite of failed L7 preregistration. No 2013–2021 δ¹⁵N outcome or ecological effect has been opened or fitted.**

## 判定の現在地：新年の生態学的検定はまだ実行していない

| Stage (source-only) | 実測成果・正確な判定 | Evidence |
|---|---|---|
| 本来の2013–21 L7 ETM+ | 元88 sites/13 regionで**0 source Level2 scenes**、旧2004–10陽性対照3/3。L7-only frozen confirmation **NO GO / untestable** | [L7 source Actions #44658030485 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44658030485)、artifact 14593294570 |
| Separate L8 OLI の2013–21 scene inventory | **88/88 original sites, 13/13 regions, all 9 seasonal start years**に少なくとも1 scene、**23,220 original site×scene metadata records**。実際の糞画素数ではない | [L8 metadata Actions #44658813887 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44658813887), artifact 14594208565 |
| Separate L8 instrument's lab calibration | 元103実糞標本の350–2500nm反射スペクトル × native OLI bands 2–7 RSR → 5-component fixed PLSR。100 random calibration CV median RMSE **1.728865‰**, train-mean null **2.308787‰**、元L7 source **1.742214‰**。事前最大2.0‰ passed。**実衛星L8年次Yを検証したわけではない** | [Original 103 lab Actions #44659513320 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44659513320), artifact 14594991900 |
| 元原著の guano ROI spatial provenance | old source original published RDSの **88 site/139,756 filtered 1984–2012 source pixels / 15,347 stable geolocated point cells**、元CRS **EPSG:3031**、全元source点 `guano_bin=1` and `bad=0`。原archiveに**非糞・reject例はない** | [RDS source geometry Actions #44660639485 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44660639485), artifact 14594649354 |
| 新L8 2018 QA-only imagery feasibility | 固定した三地域の各最初の元site、season 2018、最初に撮影されたsource sceneとlowest overall catalog-cloud scene、合計**6 same-USGS-C2 original L8 scenes**。Microsoft Planetary Computerが無料配布する**同一USGS scene ID**のQA_PIXEL/QA_RADSATをSAS署名で参照して全6有効読取。**1/6 sceneのみ元位置で品質合格の画素が存在**（BERK 37/39）、他5 scenesは0 | [L8 native QA Actions #44662127603 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44662127603), artifact **14595733363**, ZIP SHA256 `9df4b3331ca368d0184a87102d01bcfefaa3f46e44a72f8c6374b1d089dca2a0` |

### 固定した3地域×2原シーン：新しい2018年QAの実観測

| Region/site | Original L8 C2 source scene (season 2018) | 元source ROI location count | 対応QA両バンドでのgood pixels | 主要な不合格理由 |
|---|---|---:|---:|---|
| Victoria Land / ADAR | LC08_L2SR_064110_20181104_02_T2 | 920 | **0** | native cloud/cirrus/shadow **920** |
| Victoria Land / ADAR | LC08_L2SR_062111_20190125_02_T2 | 920 | **0** | **fill 920**。catalog scene cloud=0.74%でも元ROI部分は真の画像欠損 |
| Wilkes Land / BERK | LC08_L2SR_105106_20181104_02_T2 | 39 | **0** | cloud **39** |
| Wilkes Land / BERK | LC08_L2SR_104107_20190217_02_T2 | 39 | **37** | snow **2** |
| Southwest Antarctic Peninsula / ANDR | LC08_L2SR_219107_20181102_02_T2 | 7 | **0** | cloud **7** |
| Southwest Antarctic Peninsula / ANDR | LC08_L2SR_220107_20181109_02_T2 | 7 | **0** | snow **7** |

**Six native QA images retrieved**, using the open data Planetary Computer API public [SAS authorization](https://planetarycomputer.microsoft.com/docs/concepts/sas/) for the **identical scene IDs** rather than trying to access official AWS `usgs-landsat` Requester Pays without credentials. Raw signed SAS URLs were **not** emitted or archived. The first AWS source test failed `AccessDenied: Anonymous users cannot invoke requests against Requester Pays buckets` [#44661717273](https://github.com/zuizui0223/mina/actions/runs/44661717273); second distribution source was accessible but revealed a single-band raster `sample()` array shape (`n,1`) handling bug [#44661965023](https://github.com/zuizui0223/mina/actions/runs/44661965023). Corrected **only** distribution and raster shape, without changing QA bit flags, scene selection, site selection, response, or model; successful #44662127603 is reproducible.

## What the result does not say

- **L8 catalog presence 23,220 ≠ 23,220 image observations/guano pixels/independent isotope measurements.** Scene-level overall cloud cover can be misleading for a specific colony; ADAR low-cloud scene had all source points as USGS `fill`.
- **Raw original 15,347 geolocated positive guano points ≠ validated new-year guano locations.** Colony guano cover changes, new rock/snow, season and sensor differ. Original RDS is already filtered to positive `guano_bin=1` and `bad=0`, with no negative training examples or archived complete binary per-scene classifier; obtaining QA-valid reflectance does not reclassify actual guano. New image spectroscopic δ¹⁵N must NOT be computed on unverified old pixels and called an independent test.
- **Original Youngflesh et al. 2026** explicitly excluded L8/L9 OLI from their three-decade published isotope series because the spectral widths differ and harmonization is nontrivial (original preprint [source](https://www.youngfleshlab.com/assets/papers/Youngflesh-et-al-EcoEvoRxiv.pdf), published [Current Biology](https://doi.org/10.1016/j.cub.2026.06.028)). Our reconstructed L8 **lab** calibration addresses one component but does not by itself validate C2 L8 surface-reflectance scene-to-old-L7 transfer or guano polygon classifier.

## The independent replication is presently blocked at exactly one scientific input

**Missing original/new annual guano classification method with validated true-positive and negative labels, not Landsat 8 scene supply or original laboratory spectral calibration.** A new L8 classification validation should require a source-verified sample of 2013–21 actual guano and matched negative snow/ice/rock points with fixed blind accuracy thresholds, true site-season pixel counts, regional coverage, and comparable atmosphere/spectral units **before testing** source-known winter polynya coefficient on 2013–21. Independent externally documented multi-sensor automated guano workflows such as Schwaller et al. (2013, [RSE](https://doi.org/10.1016/j.rse.2013.08.009)) and modern L8 examples can be considered **only in a new separately frozen source-label QA protocol**, not after browsing for a direction that matches the 2004–10 old result.

## Scientific outcome retained / exact stop

Old polynya finding remains **exploratory**: 2004–10 `M_SP` Δoptical δ¹⁵N **−0.9216‰ per +10 percentage point source Jun–Oct 100km coastal polynya area**, 439 source site×seasons / 85 sites / 11 regions, source-region cluster 95% CI [−1.3493,−0.4939] and all leave-region-out negative; old 2004–06→2007–10 source-year RMSE **not improved**. Post-2013 same-instrument L7 source **NO GO**; alternate L8 scene+lab+old ROI+small QA passed, **new actual guano classifier / new 2013+ isotope response unvalidated**. New 2013–21 conditional association and prospective temporal replication have **not** been calculated, neither supported nor contradicted. Baseline POM δ¹⁵N and prey fractions still not identified.

Branch/PR: [#214](https://github.com/zuizui0223/mina/pull/214). Main, v0.5/v0.6 and protected Ecology Report/Paper2 unchanged. No material commits past QA that fit any new δ¹⁵N–polynya effect.
