# 南極アデリーペンギン食性×塩分：真正原本の取得・時期と地理の識別可能性

**2026-11-17 JST | mina Draft PR #214 補助 source gate | 未投稿・未主張。** 主原稿 v0.5、候補要旨 v0.6、凍結済み Ecology Report / Paper2、PR #215 を変更しない。結果は元資料の**観測支持と物理環境の情報量**であり、食性と塩分の実際の生物学的関連係数ではない。

## 1. 取得済みの真の著者データ

- Youngflesh et al. (2026), *Current Biology*, DOI **10.1016/j.cub.2026.06.028** のData availabilityのリンク **Zenodo 10.5281/zenodo.17409948** に、原著者提出データ「Data for Youngflesh et al. Submitted」が存在。GitHub Actions [#44075244428](https://github.com/zuizui0223/mina/actions/runs/44075244428) が **256,425,816 bytes** の `data.zip` を真にダウンロードし、出版社登録 MD5 **e29a2f68c84e3a515044d554540def2f** に完全一致。
- ZIP内は **1114 entries**, うちNetCDF **1084**、`L0/Landsat/landsat_reflectance_L457-2025-07-16.rds` (5,373,135 uncompressed bytes)、`L1/SIA_spectra.csv` (2,655,706 bytes)、Landsat RSR xlsx、海底地形など。**著者コードが参照する L2 PLSR係数、L3 `diet_pred`、Results `DI_df.rds` はこの元zipにない**。元ZIPを勝手にdiet-response tableだと呼ばない。
- 再抽出 [GitHub Actions #44076012021](https://github.com/zuizui0223/mina/actions/runs/44076012021) **SUCCESS**: R の `readRDS` で真の L0 Landsat RDS からsite×seasonとEPSG:3031座標を抽出し、元ZIPを成果物へ再配布せず、地点集計だけartifactへ保存。列名：site_id, ccamlr_id, region, Landsat.Product.Identifier.L1, satellite, season, year, month, day, cell, red, blue, green, nir, swir1, swir2, bad, guano_bin, geometry。**原画素行数・画像年の存在は、有効な食性`DI`推定値の存在や捕食率を意味しない。**

## 2. mina真正海洋資料とのjoin実行

比較対象：minaの出典確認済み [原MAPPPD 595地点+2,456計数](https://github.com/zuizui0223/mina/actions/runs/42610664607) と [original 588サイト×28年 GLORYS/OSI SAF](https://github.com/zuizui0223/mina/actions/runs/42959103493) artifact **13828472111**。後者の1993–2013年（21 calendar years）は **12,348 site×years、378 wet marine grid cells ×21 = 7,938 cell×years**。GISで同一点への重複を独立反復としない。

著者Landsat原本：**146 source sites、1410 actual site×seasons、24 different start seasons（1984–1992, 1996, 1999–2012）**。このうち1993–2013の環境期間に収まる原本source site-seasonsは **1225**。季節の開始年2012は2013年1–2月を含み得るため、2013年 start season の不存在を論文の暦年矛盾と呼ばない。

pre-outcomeの地理照合：原site_id完全一致 + EPSG:3031 source Landsat pixel centroid meanとMAPPPD site点との距離。マッピング方法を生物学的DI結果で選択していない。

| 地理照合の基準 | 食性原画像由来site×season×元海洋資料の一致 | site | wet grid cells | 対応region |
| --- | ---: | ---: | ---: | ---: |
| **A. ID完全一致、本人が最短で2 km以内、他のsiteが2 km以内にない** | **892** | **99** | **92** | **14** |
| B. ID完全一致、本人が最短2 km以内、ただし近接他siteあり | 999 | 118 | 106 | 15 |
| C. ID完全一致、本人が2 km以内、近傍他IDがさらに近くても認める | 1012 | 121 | 107 | 15 |
| 記述感度のみ: 同一IDで5 km以内 | 1045 | 125 | 111 | 15 |

Aが保守的な次の解析対象。**892は892独立生物実験ではない**。真のoriginal wet-grid×seasonの重複除去で**828 cell×season**、15 observed season starts（1996,1999–2012）、地点あたり季節数の中央値は**10**。Aの中央西部南極半島1 site-season、South Shetlands1、Victoria Land197、Northeast Peninsula150、Wilkes Land149で、地域・時代の支持は極端に不均等。

BではCentral-west Peninsula5 source sites／11 site-seasons/6 seasonsと増えるが、**複数地域での反復的salinity×diet応答の確証を保証しない**。近隣site IDを独立した物理気候レプリケートにしない。

## 3. 塩分独自の物理変動はあるが、生物作用を意味しない

真正の588 sourceサイト×1993–2013年の `GLORYS_salinity`, `SIC_pp`, `GLORYS_thetao_C` を抽出した。変数ごとに **site平均・region×year平均を差引きregion平均を足す**バランスパネル二重残差を計算してから、salinity残差をSIC残差＋thetao残差へ線形投影した（説明力ではなく物理共変動のpreflight）。

- 塩分残差SD **0.089219**（モデルの表層塩分単位）、元全site×year塩分分散の**8.038%**がsite+region-yearを取り除いた後に残る。
- SIC＋thetaoにより、この局所塩分残差分散の **20.364%**が線形説明、**79.636%**が未説明（この未説明部分にはノイズ/解像度不一致も入り得る）。重複wet-cellを1セル1年にしても説明分散は **17.171%**（未説明82.829%）。
- しかしsite/region-year残差平方和の **約67.48%**は中央西部・南西部・北東部の南極半島3地域に集中。したがって`salinity`を独立な温暖化の普遍軸や機構と呼べない。今回のA地理対応は中央西部がほぼ欠け、同じ変動量がdiet sourceで利用可能とは確認できない。

## 4. 実際の季節支持差と識別境界

[著者元 `Scripts/5-diet-model.R`](https://github.com/caseyyoungflesh/penguin_diet_from_space/blob/main/Scripts/5-diet-model.R) はsite SICを**11月〜翌2月、150 km、seasonの開始年**で集計し、海底棚面積とDOYを含める。[本来のStan model](https://github.com/caseyyoungflesh/penguin_diet_from_space/blob/main/Scripts/model_files/5-diet-model.stan) には `DI`, `sd_DI`, 11–Febのsite/year SICとsite SIC, bathymetryがあるが、**塩分を含めていない**。minaの既存物理 `SIC_pp` は**8–11月100 km**、GLORYS水温・塩分も8–11月で、author原SIC同季節・半径ではない。

**新しい生物統計結果は今の段階ではゼロ。** 偽のdiet posterior、season一致、SSSの独立効果、有意確率、気候に因果的な魚/オキアミ転換、SSPに基づく繁殖増減予測は報告しない。

## 5. ここからの一つの確認的な検定（未実施）

**質問：同一アデリー繁殖地×繁殖季節の推定食性へ、元研究が扱った海氷・海底地形・季節日を超える塩分偏差情報があるか？**

1. 元ZIPのL1 SIA/スペクトル→センサーごとのRSR投影→著者同仕様の1000回PLSR→Landsat反射率からsource `DI` と `sd_DI`→季節内推定を厳格に再現する。原著のCV評価と吻合するまで新しい食性効果を宣言しない。
2. original 11〜翌2月（必要なら食性観測日前の月のみ）についてGLORYS海水温・塩分と海氷を**共通時期で再抽出**。既存8–11月との混用は禁止。実海洋格子とregion-year/same-site の支持域を記録。
3. 元地点の真のmatched seasonとwet cellを凍結した上で、same-unitの `M0 = site history + DOY + ice + temperature + bathymetry + region-year support` と `M1 = M0 + salinity anomaly` を比較。最終評価はregionまたはmarine-cell群を留保し、単なるin-sample pや予測改善の後付け調整をしない。塩分の物理代理（融水、成層、水塊）は競合解釈として残す。
4. 独立のmatched sites/海洋セル/regionの支持が乏しければ統一マクロ因果説を棄却し、source limitationを結果として停止する。

参照背景：南極の融水・淡水の影響は[2026年の総説](https://doi.org/10.1016/j.avrs.2026.100386)が既に議論しており、塩分そのものの因果的な新発見を簡単に主張できない。今の新規性候補は**真正地点・季節での海氷/水温条件付き関連の追加検定**に限定される。

**再現用入力**：Zenodo 17409948 source-MD5; GitHub Actions #44075244428 / #44076012021 (original archive and RDS source gate); MAPPPD artifact 13669533413; marine artifact 13828472111. 実計算したgeographic/season crosswalkとsalinity site+region-year residualの派生コード・結果はローカル会話成果物として保存。凍結論文/主lineの既存結果は未変更。
