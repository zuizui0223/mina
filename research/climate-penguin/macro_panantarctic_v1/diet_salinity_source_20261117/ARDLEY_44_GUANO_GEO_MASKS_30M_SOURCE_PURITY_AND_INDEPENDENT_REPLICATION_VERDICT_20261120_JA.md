# 2013–2021年ポリニヤ負方向の独立確認：44真正Guano SHPからのLandsat 30m分類支持判定

**2026-11-20 JST | mina Draft PR #214 research branch only | source+classifier audit, no new isotope Y and no new polynya association.** ここまでの進行における「実際に動作したもの」と「実験未成立」を一つの場所に固定する。旧論文の主張や発見標本を修正しない。

## 現在地：真正日付付き外部糞被覆ポリゴン44個を取得・検証、しかし30mアデリー純画素には厳しい上限

**新しい本物の元資料**：Pfeifer et al. (2025), *Ecological Indicators*, DOI [10.1016/j.ecolind.2024.113011](https://doi.org/10.1016/j.ecolind.2024.113011) の公開 [Zenodo DOI 10.5281/zenodo.14503437](https://doi.org/10.5281/zenodo.14503437) 。著者の元ZIP `Dataset distinguish breeding penguins drone imagery.zip` (4,109,917,595 bytes; published MD5 `62bb5a89ca7f5f06e54b74e26bf5de5d`) から**whole 4.11GB imageryは一度もダウンロードせず**、ZIP64中央ディレクトリと小さな必要sidecarファイルだけをHTTP Rangeで読んだ。

- ZIP元本2448 native members、日付・種ごとの `Guano/YYYYYY/Ardley_YYYYMMDD_adelie.shp` と `*_gentoo.shp` **計44個**。各SHP+SHX+DBF+PRJが実在し、元Shapefileから**44/44の真正ポリゴン・各日・CRSを原ファイルとして読取成功**。
- すべて原EPSG **32721**（WGS84/UTM21S）、実座標はArdley付近（−62.21°、−58.92°）、全ファイルPolygonでinvalid source geometry=0。元属性は `green`, `green_red`, `darkred`, `guanorings` 等。実際に22撮影日 × 2種。期間は元2013/14, 2014/15, 2016/17, 2017/18の4季節。Adélie=227 polygon objects, Gentoo=914、計1,141 polygon objects。対象は**注釈された糞関連被覆領域の正例側**で、別の草地・雪・岩の地理参照付き真の負例は未確認。
- [Zenodo ZIP64 source index Actions #44670929449 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44670929449)；原ZIP2448ファイルmanifest artifact **14600415833**、sha256 `ef4afd6db995ac83cdd51c798d08d00dcd729e2e39c85b096b91785cb36a6ebc`。
- [原native 44 SHP geospatial QC Actions #44671441478 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44671441478)；44-date/source polygon summary+fields+CRS+geometry/dissolve area artifact **14599603634**、sha256 `95289f3dad6e8604f8116e60e230616b36b167874623951be6fee95dac8e75c4`。

### 30m Landsat 8に対する厳密なsource-only面積上限

30m×30mの**名目投影画素面積900 m²**。同じ日・同じ種の外部原ポリゴンの全部を一つの画素に詰め込んでも、どの画素の真正注釈糞被覆割合も `min(1, source_positive_union_area_m² / 900m²)` を**越えられない**（位置・画素格子位相に依存しない**上限**）。逆に総面積が900m²を越えても、パッチが離散しているため高純度pixelの存在は保証されない。元SHPは元著者が選択した領域であり全営巣地の真糞被覆総量ではない。

| 元Guano真source | 原本22日分の注釈ポリゴン合併面積（最小／中央値／最大） | ≥80%糞純度の**名目30m画素が数学上作れない日** | ≥50%糞純度の画素が数学上作れない日 |
|---|---|---:|---:|
| **アデリー** | **247.9 / 379.7 / 566.8 m²** | **22/22** | **20/22** |
| ジェンツー | 1,062.3 / 1,792.0 / 3,237.2 m² | **0/22**（ただし存在証明ではない） | **0/22**（存在証明ではない） |

- アデリーの**最大でも566.8/900=0.6298=約63%**にしか達せない。糞面積の**実際の画素配置をどのように調整しても80%純Adélie糞のL8 30m画素はこのsourceの22日すべてで作れない**。50%純度でも20/22日は不可能。これは実画像の雲/SLCや残差モデルの有意性とは**独立な、原注釈幾何からの強いsource制限**。
- ジェンツーは注釈総面積が各日900m²を超えるが、現実の格子上で80%糞画素があるとはまだ言えないし、ジェンツーだけの分類成功をアデリー食性proxy検証に転写できない。
- この厳密な上限は**同一UTM側の名目30m投影面積**について。公式USGSシーンごとの投影変換・ネイティブ地理格子に重ねて正確な画素数を検査したものではないため、L8格子整列での実際の純画素数は未測定。
- [面積上限のsource-only CI Actions #44672597312 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44672597312)、出力 artifact **14600323152** sha256 `7eb634a65184844bc457b05eeb08b42845d70ca8218e769b1d1bf14e0924a812`。入力は44幾何原監査のアーカイブ（SHA固定）のみ。新Zenodoダウンロード・新同位体Y利用ゼロ。
- より詳細な位相9組で実ポリゴンと名目30m格子の重なりを測る exploratory-only CI [#44672198517](https://github.com/zuizui0223/mina/actions/runs/44672198517) は**原元ファイルを再取得している途中、31/44付近で提供元ZenodoがHTTP 429に到達して停止**。これは物理データが欠落した/研究の相関が失敗した意味ではない。単一の再試行を繰り返すのを避け、**既存SHA検証済みジオメトリー監査から数学的な厳密上限に切り替え**て成功した。429を「9位相で高純度画素なし」と誤記しない。

## 元88との地理的独立性：偽の検証を回避

- **Ardley島は元Youngflesh光学δ15N×ポリニヤ発見コホート88サイトに一致しない。** 元88で地理的最近接 `TSIS` 距離約54.85 km。同じ島や近所の植生であっても新同位体サイトと同一観測地点としては扱えない。Ardleyの面積22日を元88の空白Yへ挿入しない。
- 真正手動ペンギン画像Polygonなら `hao-yu-wu/penguin_colony_registration` の `Devil_Island-GT/DEVI_1_081.json` は確認済みで、`DEVI` は元88サイトに一致する。ただし**画像座標(x,y)のみで地理CRS・撮影年月が無く**、2013–21の真の地理参照付きL8糞・非糞マスクではない。[外部真正ソース&ID監査 Actions #44670647953 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44670647953), artifact **14599846337**。
- VHR guano-area public records（Strang et al. 2025）に直接ID一致するのは `INEX` の3季節/1地域のみ。これは定量面積であり真正pixel-maskではない。2013/2017/2018実VHR日にL8同日〜8日差のnative QAを照合した時も**現在の糞かどうかの真偽は未確認**。[実QA #44669179557 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44669179557)。

## 科学的処理：ポリニヤの負の関連は維持、独立再現はまだ未成立

旧発見条件2004–2010の実測 DEEP-AA冬沿岸100km面積が+10 percentage pointsのとき、元光学δ15N proxy **−1.003‰**、夏塩分調整後**−0.922‰**、元11region cluster保守CI [−1.349,−0.494]、全部一つずつregion omitしても負、M0から残差追加説明率3.8%、旧2004–06→07–10時間外予測改善なし。この符号は事後探索であり、元の事前予測（正）は失敗している。**真のオキアミ消費量・実POM δ15N baseline・因果は未測定**。

Landsat 7原著と同じ測定器で2013–21撮影 source が元88サイトに0件（陽性対照3/3）というL7 validation no-goを維持。別Landsat 8 OLI sourceは88/88地点・9 seasonのシーン在庫と元103糞標本の分光RSR較正(5-component PLSR) holdout median RMSE1.729‰まで検証済み。しかし**実年2013–21の真の糞・非糞識別精度を、独立で複数原地域における画素単位で検証できていない**。Ardley sourceのAdélie注釈は30m純画素に不足、DEVIは写真座標のまま。**最終outcome `NO_GO_INDEPENDENT_2013_2021_L8_GUANO_PIXEL_GROUND_TRUTH`、δ15N係数は再推定せず、負の発見を独立確認と呼ばない。**

## 次工程を絞る

外部UAV/衛星の**新年（2013–2021）日時付き**、地理参照付きのAdélie guano positiveと、雪・岩・土の**真のnegative**を含むピクセル/ポリゴン原図を、少なくとも6地理region・元site crosswalkができる観測範囲で取得することが、次の科学的入力条件。**L8原native30mでguano-positiveな高純度画素が得られること**も必要。既知の色を見て事後的に閾値を調整した新Yや、純度が不明なhistorical pixelsを現在guanoとして流用しない。新データが実際に得られた場合だけ、既存の新期間検定契約に従って2013–21の負方向を一回実施する。

**コード**：
- [真のZip64 2448 original source file inventory](inspect_zenodo14503437_remote_zip64_GIS_without_4GB_download_20261120.py)
- [真の44個Geographical SHP native QC](extract_ardley_original_true_guano_44_shapefiles_source_only_20261120.py)
- [44個元面積からの名目L8純度上限](audit_ardley_true_guano_source_30m_mathematical_pixel_upper_bound_20261120.py)
- [L8独立検証source契約](L8_ALT_SENSOR_NEGATIVE_POLYNYA_PRE_Y_SOURCE_AND_CALIBRATION_GATE_20261120_JA.md)

Protected `main`、v0.5/v0.6原稿、Ecology Report、Paper2は無変更。Draft PR #214のみ。
