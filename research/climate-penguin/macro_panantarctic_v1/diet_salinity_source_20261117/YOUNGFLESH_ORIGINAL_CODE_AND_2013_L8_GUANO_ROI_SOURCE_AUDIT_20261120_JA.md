# 原著の「糞画素の選別」コードが本当に公開されているか：Youngflesh 2026完全データ・ソースコード監査

**2026-11-20 JST | mina Draft PR #214 | source-only provenance audit | 2013–21年L8反射率由来δ¹⁵N Yを開かず、ポリニヤ負方向を再検定していない。**

## 最も重要な今回の発見

**原著の公開R分析コードは確認できた。しかし生のLandsat画像から `guano_bin=1`, `bad=0` の糞被覆画素を選別してRDSを生成した上流の処理は、公開リポジトリにも公開ZenodoデータZIPにも存在しない。**

原著のPLSRを精度よく移植できたとしても、2013–2021年の新しいLandsat8で*実際の糞画素*を抽出する処理を同一条件で再現したことにはならない。これは技術的な不明点（どのモデルを使ったか）ではなく、提供されている**処理前後のデータの境界**として確定。

### 完全に検証した原本

1. [原著preprint v3](https://ecoevorxiv.org/repository/view/10720/) が明示する、[原著GitHubコード（main）](https://github.com/caseyyoungflesh/penguin_diet_from_space/tree/4ab7c992fc2232b7905af0d1aa949d88dc9561ea)、保存コード DOI [10.5281/zenodo.17363042](https://doi.org/10.5281/zenodo.17363042)、元データ DOI [10.5281/zenodo.17409948](https://doi.org/10.5281/zenodo.17409948)を識別。GitHubのmain headは **`4ab7c992fc2232b7905af0d1aa949d88dc9561ea`**（2026-06-26）。
2. GitHub原コードは `Scripts/1-process-abiotic-data/{1a,1b,1c}`, `Scripts/2-PLSR.R`, `3-predict-diet.R`, `4-diet-est.R`, `5-diet-model.R`, `6-gr-diet.R`, `Scripts/model_files/`。**Landsatシーンを収集して糞maskを作る0番のプログラムは見当たらない**。README自体が `L0/Landsat/landsat_reflectance_L457-2025-07-16.rds` をraw inputとして明記。
3. 元データ Zenodo record `17409948` は元 `data.zip` **1ファイルのみ**（256,425,816 bytes, MD5 `e29a2f68c84e3a515044d554540def2f`）。全ZIPを実ダウンロード・MD5とZIP CRCを検証し、**native 1108 members中、コード拡張子 `.R`,`.Rmd`,`.py`などのsource scriptは0件**。 `L0` 551 native membersは原RDS、RSR Excel、SIC NetCDF、bathymetryなどで、 `L1/SIA_spectra.csv` が1件。残り556はmacOS資材の `__MACOSX`。 [GitHub Actions #44674477466 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44674477466)、artifact **14601496370** SHA256 `7cce487c44e31aac8cb6781e7063b4d0e2aeec64ba009dee311f54edbfff209f`。
4. 元 [`Scripts/3-predict-diet.R`](https://github.com/caseyyoungflesh/penguin_diet_from_space/blob/4ab7c992fc2232b7905af0d1aa949d88dc9561ea/Scripts/3-predict-diet.R) は `guano_ret <- readRDS(...landsat_reflectance_L457-2025-07-16.rds)` から始まり、`unique(guano_ret$bad)` と `unique(guano_ret$guano_bin)` をチェックした後、6バンドを選びL4/L5/L7 PLSR係数を適用。新しい画像から「糞である／ない」を分類するコードは含まない。
5. 実 original RDSは `sf` EPSG:3031、88 siteで139,756過去選別済みpixel rows、15,347の固有座標。 `guano_bin` は **全行1**、 `bad`は**全行0**。負例（雪・岩・汚染画素）が残っていないことを[ソース元監査 #44660639485 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44660639485)で確認。過去の選別済み正例点を2013+の真の糞判定ラベルとして扱うことはできない。

## 元の正しいPLSR較正は再現可能だが、測定過程は別問題

[原著 `Scripts/2-PLSR.R`](https://github.com/caseyyoungflesh/penguin_diet_from_space/blob/4ab7c992fc2232b7905af0d1aa949d88dc9561ea/Scripts/2-PLSR.R) に、原103糞実標本から各L4/5/7センサーのRSRを畳み込み、`pls.options(plsralg = "oscorespls")`、層化5bin65% train、`set.seed(1)`、**1,000回**、6成分をfitして5成分の係数を取得し、1,000係数をアンサンブルする仕様が確認できる。原著 `Scripts/3-predict-diet.R` はその1,000本の係数から画素ごとの平均・SDを出す。元 `4-diet-est.R` はさらにStanモデルで日・サイトのDIを推定する。2026-11-17の自前Python単一PLSR5＋100回CVによるsource optical δ¹⁵N proxyは**原著の最終Stan posteriorではなく測定誤差の範囲も違う**。

**原著に準拠した1,000係数較正まで実際に再現成功した。** [GitHub Actions #44676042238 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44676042238)、artifact **14602063283**（SHA256 `ac1199ad312df63173f7be73452ccbb5e01b7c55f29d3413ede63e1a1b665669`）。元103実糞標本、真のL7/L8各6RSR、著者元R `pls::plsr`/`oscorespls`、5同位体分位の65%学習・35%検証、`set.seed(1)`と**同じ1,000分割**で、6成分fit→5成分採用、各センサー1,000組の係数アンサンブルを出力。RMSE中央値は元 **L7=1.739038‰**、新 **L8=1.741775‰**、標本平均null=2.325794‰。同じ分割でL8−L7差の中央値 **+0.003419‰**。保存した両センサーの1000行係数CSVとCVスコアCSV、実行JSONを再展開し独立に数値を確認した。原著と同じ**実験室測定モデルの比較**であって、真の2013–21糞画素認定・原著DI posterior・時間外ポリニヤ負相関の再現ではない。[完全結果・method/bounds/エラー修正履歴](ORIGINAL_AUTHOR_STYLE_1000_R_PLSR5_L7_VS_L8_LAB_CALIBRATION_RESULT_20261120_JA.md)。

## なぜ元アーカイブだけでは2013–21の独立再現に進めないか

- **L7 2013–21の既存88 original sites** は USGS public C2 L2 scene inventory zero、historical positive control 3/3。別センサーL8は88/88 site・9/9 seasonで23,220 metadata source scenesあり。
- L8向け本来の103 lab spectra較正が有効でも、原著が使った **`guano_bin=1,bad=0` の画像選別の仕組み**が公開されていない。元の地点は同じでも糞被覆は時間で変化し、旧元画素に新たなL8スペクトルを取ることを現在の糞実測と呼べない。
- 別公開 external Ardley positive guano polygon 44 original shapefiles/22日・4季節は原native EPSG32721と日付を真に検証した。しかしアデリーの元注釈は247.9〜566.8m²で、**30m×30m=900m²の80%以上純正例は22/22日で面積上不可能**。その地域も元88のどのsource IDでもない。
- INEX external VHR total guano area 3年とDEVI manual photo polygonsはあったが、それぞれ現年pixel-level真のnegativeがなく、後者は写真x/yだけでGIS/取得日がない。**6 regionの新同位体観測を検証できる真正pixel classifierは現時点では未成立**。

## 次の科学的に必要な入力

**元著者に求めるべきなのは新しいYではなく、まず `L0/Landsat` の処理コード**：
- Source USGS scene selection, radiometric/atmospheric harmonization, winter summer `season` labeling, native pixel geolocation, QA cloud/snow/land/water filtering; `guano_bin`/ `bad` に正負を割り当てる方法・閾値・学習ラベルと、元site IDs のsource ROI polygon.
- 可能なら独立2013–2021 Landsat8/9用に著者が開発中のsource QC/OLI spectra transfer、現年guano判別の感度・特異度・date support。
- 元103 lab sampleの1000 ensemble原モデルの `L7_coef_en.rds` と将来の`L8_coef_en.rds`、source climate&Stan DIの不確実性（既存元L0 datasetには完成DI posteriorなし）。
- その後、事前固定した元30sites/6regions/4winters＋注目region3sitesずつの「真の同年guano正例で品質適合」ゲートを満たしてから、L8新sourceの100km冬ポリニヤ負方向を一回のみ検定する。

**元の439観測の頑健な負係数は探索的なまま保持する。** 著者コードの入手は元Yの独立再測定ではない。主論文の海氷・繁殖生態マクロ主線と混同しない。Draft PR #214のみ追記、`main`/v0.5/v0.6/Ecology Report/Paper2は変更しない。
