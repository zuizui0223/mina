# L7が撮影されていない場合の別系統：Landsat 8 OLIを使う新センサー時間外検証（source/calibration gateを先に凍結）

**2026-11-20 JST | mina Draft PR #214 | outcome-blind source planning, not a substitute for L7 original test.**

## L7検証の既定結果は維持

- 前に凍結した `FROZEN_2013_2021_L7_NEGATIVE_POLYNYA_TEMPORAL_REPLICATION_20261120_JA.md` のデータソースを途中で変更**しない**。
- [L7 meta-only source CI #44658030485](https://github.com/zuizui0223/mina/actions/runs/44658030485) source 88 sites/13 regions・2013–21 Nov–Feb のL7 Collection2 Level2 scene **0**、同カタログの原2004–10 source controls 3/3陽性 ⇒ `NO_GO_L7_2013_2021_SCENE_SUPPORT` を確定。元L7で時間外δ15N検定をしたとは言わない。

## 新しい独立入力（元の負方向仮説を変更しない）

Landsat 8 Operational Land Imager (**OLI**、L7 ETM+とは**異なるセンサー**）の2013–2021 original 88 colonies、元の同じ前冬Jun–Oct/100km DEEP-AA沿岸ポリニヤ面積割合と同一元source-site/region定義。新しい新年画像から独立したδ15N proxy Yが使えるかどうかを観測値抜きで段階的に確認。

1. **source availability**：USGS Collection2 Level2 L8 OLI scene footprints、2013–2021 source seasons Nov–following-Feb、原88地点の本来のMAPPPD centroid、scene ID/day/年/region。検証前のカタログ走査。sensor = `landsat-8`のみ。3つの元regional sitesを含む地点・source seasonを数え、同一シーンの重複排除と元作者1984–2013画像の重なりを確認。集計は元source sighted 88全体を分母。現段階のcatalog hitは**雲・雪・糞ROI有効であることを意味しない**。
2. **strict source coverage gate**（現段階は候補stage）：scene metadataで少なくとも30 original sites, 6 original source regions, 4 valid candidate winter-start years, and ≥3 sites each in Victoria Land/Wilkes Land/Southwest Antarctic Peninsula。満たさなければ `NO_GO_L8_SCENE_SOURCE_SUPPORT`。満たしても「校正OK」は主張しない。
3. **original lab-to-L8 optical calibration gate**：Youngflesh et al. 2026 source original 103 laboratory guano isotopic assays + full 350–2500nm laboratory reflectance (same originally archived real samples) を source MD5 で確認。USGS/NASA公表のL8 OLI真のRelative Spectral Response (**RSR**, e.g. official Ball_BA_RSR.v1.2.xlsx) を取得、帯域 2=blue,3=green,4=red,5=NIR,6=SWIR1,7=SWIR2 の6バンドのみ合成。元L7のRSR 6 bandsと新L8のRSRを混同せず、再現可能な統一波長格子を使用。元論文のL7 5成分PLSR (scikit PLSRegression(scale=False) derivative) と同条件の **5 components** 以外を試さず、新L8を同103標本のlab isotopeにfit。古いoriginal 103 laboratory sampleの固定検証split (seed=20261117+8, 100 stratified 65/35 splits) によるL8留保median RMSEが `<2.0‰`かつ単純なtraining-mean nullより良いこと、及び元L7 lab CV median RMSE ~1.742‰との比較を要求。これらは**lab calibration gate only**、実衛星分光が同品質であることを保証しない。RSRはsource provenance/digest/センサー名をピン留めする。**新2013+のYとポリニヤ関係を使って較正を選ばない**。
4. **true guano ROI / satellite harmonization gate**：原著Original pixel selection/scene quality/guano ROI polygon/source months/day-equal aggregationを、元88地点で元著者の原実装のまま使えることを検証。原RDS画像がpixel-centroid/bandだけで、実測の糞ROI境界や最終raw cloudmaskを復元できない場合 `NO_GO_GUANO_ROI_UNREPRODUCIBLE`。USGS Collection2 L8 QA_PIXEL QA_RADSAT、雲/影/snow/water/fill、valid SR scale/offset をnative資料どおりに扱う。同一地点のL7旧guano反射率とL8を**未較正単位のまま同一の色と見なさない**。
5. **physical same-source gate**：2004–10で使用した DEEP-AA native `SIC60_6.25km_20d.zip`の同一100km測地円・真冬6–10月5か月各80%＋元GLORYS (Nov–following-Feb) θo、salinity、元source NSIDC V4 150km SIC。2003–12の元画像は新Yに含めない。各新季節のnetCDFの実ファイルがなければ欠測であり補間禁止。
6. **Y-open gate**：真のL8 guano pixelが確認できた時点で、候補30sites/6regions/4wintersと各注目region3 sitesのsource supportが維持され、かつ2 season以上真に観測できるoriginal sites≥20。それ以前に新Yをfittingしない。未達なら `NO_GO_L8_TEMPORAL_REPLICATION_SUPPORT`。

## Outcome-run はまだ許可しない

上記1–6を本当に成功した順にsource receiptsに保存した場合だけ、旧発見方向を反転させない `M_SP` same FE・same source δ15N optical proxy, β_P<0、region cluster t(地域−1)95%上限<0、全地域抜きでも負（`M_P` 方向補助）を**未見2013–2021新画像だけ**で一回検定する。過去2004–2010の元係数を新Yとscoreする外部時間予測も別に報告。L8から一つでも条件未確認なら解析せず原稿主結果へ昇格させない。

**Source facts**: USGS official [Landsat C2 reflectance instrument availability](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance), [official spectral characteristic viewer](https://landsat.usgs.gov/spectral-characteristics-viewer), [Landsat 7 acquisition policy](https://www.usgs.gov/landsat-missions/landsat-7). 既存のL7 negative-polynya associationは事後探索のまま維持、基準POM δ15N/真の餌種は未同定。

**No edits to main / frozen macro manuscripts.**
