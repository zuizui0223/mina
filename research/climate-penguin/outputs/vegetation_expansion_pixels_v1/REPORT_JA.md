# 既知植生域の月別観測支持と2018年の代替画像候補

追加候補9地点について、1月・2月を別々に確認した。50地点×年×月、249地点別シーンを読み、2件の読み取り失敗を記録した。失敗のある月は年ペア比較から除外した。地図上の植生域に画素中心が入る部分のみを対象とし、同日の重複画像は一日として数えた。

## 比較できる年ペア

各年2日以上の観測を必要とする既存基準では、共通する植生画素がある年ペアは0だった。各年1日以上へ緩めた場合の支持も、基準変更による違いとして全件併記する。

| 地点 | 月 | 年 | 共通する既知植生域の画素 |
|---|---:|---|---:|
| ARDL | 1 | 2020–2022 | 1095 |
| ARDL | 1 | 2020–2023 | 1015 |
| ARDL | 1 | 2022–2023 | 1003 |
| CUVE | 2 | 2019–2020 | 66 |
| CUVE | 2 | 2019–2022 | 16 |
| CUVE | 2 | 2020–2022 | 21 |
| TUXE | 2 | 2021–2024 | 2 |

Ardleyの1月は1000画素以上の共通支持があるが、各年の観測が1日なので年内変動を評価できない。3年ペアは同じ地点・年を共有し、独立な3反復ではない。ここから広域の植生効果や有意差は推定していない。2日基準を満たす年ペアがないことは、別季節・別製品でも植生変化を調べられないことを意味しない。

## 2018年の代替画像を検索

2018年1～2月のSentinel-2 L2A候補がなかった8地点について、配信先の公開コレクション一覧を確認し、Sentinel-2 Collection 1 L2AとLandsat Collection 2 Level 2を検索した。

- Sentinel-2 Collection 1 L2A：16検索すべて候補0。
- Landsat Collection 2 Level 2：16検索すべて候補あり。地点別参照120件、重複を除く画像IDは47件。
- 全32検索のページ送り完了と保存JSONのハッシュを確認。QA・反射率の画像アセットはまだ読んでおらず、晴天地表や植生の支持は未確認。

Landsat画像をSentinel-2のNDVIへそのまま継ぎ足すことはしない。解像度・観測日・品質情報・反射率処理・センサー差を確認し、まずLandsat内で同じ処理をした年比較を検討する。候補の存在だけで2018年の欠落を補えたとは判断しない。

## 保存と再現

pixel_sources.zipに日別マスク・全シーンのURLと読み取り状態、fallback_sources.zipに代替コレクションの取得応答を保存した。

`python research/climate-penguin/work/scenario_support_v1/vegetation_expansion_pixels.py --map <PlantarcticaVegetationMap.shp>`

`python research/climate-penguin/work/scenario_support_v1/validate_expansion_pixels.py`

`python research/climate-penguin/work/scenario_support_v1/vegetation_2018_fallback.py`

50個の画素配列について、ハッシュ、日付の重複なし、地図上の植生域内で1日／2日以上見えた画素数を検証した。植生分類の真偽や植生量を検証したものではない。
