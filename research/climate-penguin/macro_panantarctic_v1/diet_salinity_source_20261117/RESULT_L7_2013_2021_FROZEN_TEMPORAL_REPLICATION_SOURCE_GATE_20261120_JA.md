# 2013–2021独立検証・Landsat 7原目録ゲート：未使用期間の真のL7撮影シーンなし、同一衛星での検定はNO GO

**2026-11-20 JST | mina Draft PR #214 | source-only inventory | optical δ¹⁵N・ポリニヤ係数は再推定していない。**

## 一文の判定

**`NO_GO_L7_2013_2021_SCENE_SUPPORT`。** 昨日の観測内の負のポリニヤ係数は取り下げない。しかし同じ88原繁殖地について2013–2021年11–翌2月のLandsat 7 ETM+公開USGS Collection2 Level-2シーンを検索した結果、利用可能なシーンの**metadata hitが88/88地点で0**。一方、同じSTAC収集・同じL7プラットフォームフィルタ・同じ3原地域の**2004–2010年歴史的陽性対照は3/3地点で検出**できた。したがって「検索自体が壊れたので全部0になった」とはみなしにくい。

## 原資料・真正の地理/年月と結果

- 新検証仕様はシーン目録開封**前**に凍結： [FROZEN_2013_2021_L7_NEGATIVE_POLYNYA_TEMPORAL_REPLICATION_20261120_JA.md](FROZEN_2013_2021_L7_NEGATIVE_POLYNYA_TEMPORAL_REPLICATION_20261120_JA.md)、commit **`56cfb8e12852ae42b50d2c22884c0edab5acd565`**。
- 元の118〜88地点へ至るYoungflesh source地理照合で事前の88 original colony ID/13 original reporting regionsに固定。実測ポリニヤ地理結果 [`source_original_88_site_polynya_25km_100km_native_grid_geography.csv`](https://github.com/zuizui0223/mina/actions/runs/44545732891) のノイズのない真のMAPPPD植民地座標のみ使用。source-only archive artifact **14539723210** のSHA256 `702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96`。
- 冬季指標のseason `2013..2021` について、撮影検索は当該11月–翌2月で、新sourceの観測季節境界を一つも変更しない。公開STAC: **Element 84 Earth Search v1 USGS Landsat Collection 2 Level-2**, `landsat-c2-l2`、明示的 `platform=landsat-7`、全88原地点の元座標Point/scene intersects。
- 88問い合わせすべて成功、パーサ・sensor、撮影日時・source scene IDを検証。**元新seasonへのL7 scene hit：0件／0地点／0地域／0季節**。歴史的L7陽性照合: Victoria Land、Wilkes Land、Southwest Antarctic Peninsulaの固定先頭siteによる**3/3**。
- [GitHub Actions #44658030485](https://github.com/zuizui0223/mina/actions/runs/44658030485) **SUCCESS**：出力artifact **14593294570** (SHA256 `23e2d605202b4fc45556b207f8d22597231669649b980b90031654ef88ef974a`)。ファイル `ORIGINAL88_L7_2013_2021_SCENE_GATE.json`、全88 query receipts、site×scene一覧（新期間0行）、season×region一覧。
- このsource gateは**画像の欠測率・雲/SLC-off品質の最初より手前**。後期L7 sceneが無い以上、cloudmask/QApixel、真の糞色、5成分PLSRに進む前に統計的検証不可能。観測欠測を0巣、0光学δ¹⁵N、0ポリニヤ面積として数えていない。

## なぜこれは意外ではないか

USGS公式 [Landsat 7 overview](https://www.usgs.gov/landsat-missions/landsat-7) は、Landsat 8運用開始の2013年以降、Landsat 7は南極、孤立島、外洋を**systematically acquiredしなくなった**と明記。独立した[CEOS 2016報告](https://ceos.org/document_management/Meetings/Plenary/31/Presentations/3.4_CEOS%20SDCG%202016%20Implementation%20Report%20v1.pdf) にも2013年11月以降のL7南極定常収集の終了が記載。**衛星は2021年まで稼働していても、元コロニーを撮影する保証はない**。公開カタログに未登録の原raw sceneがある可能性まで普遍的に否定する結果ではないため、主張は「照合した公開USGS Collection2 Level-2商品で0件」に限定する。

## 科学的状態と次の安全な手

1. 2004–2010の発見結果：冬ポリニヤ100km面積割合10 percentage-points増で元δ¹⁵N optical proxy **−0.922‰（塩分調整後）、11地域t(10)95%区間 [−1.349,−0.494]、439 site×season、85 sites**。新しい観測で確認されたわけではなく、同じ著者原衛星データを多数検定した結果の**探索的後付けの負方向**である。
2. 新2013–2021 L7-only temporal hypothesis検定：**未実施（真の撮影入力がない）**。負の係数は再現したとも、否定されたとも言えない。SLC-offが原因と断定するのは誤り：もっと上流のscene acquisitionの不足。
3. 次に真の新画像で独立確認する場合は別契約での**Landsat 8 OLI (2013–)** が現実的な原source候補。ただしL7-ETM+の6バンド/PLSRをOLIに単に転用できない。元103実guanoの350–2500nmスペクトルを元著者の方法でL8 OLI spectral responseへ畳み込む、事前の新センサーPLSR検証、元糞画素ROI/QAを厳格復元する「新センサー観測」設計を**未使用の2013+新画像より前に別途凍結する**。独立2013–2021追試として報告するにはそのセンサー間の測定系の相違を別の不確実性として扱う。
4. この段階でL8/9/Sentinelを元L7のままの型へ無断で置換せず、半径や同位体符号条件を修正しない。**基準POM δ¹⁵Nは未観測**：負の符号が出ただけで「オキアミ食性移行」「基準値では説明不能」とは断定しない。
5. main、v0.5/0.6稿、既存Ecology Report/Paper2へのマージや過大な新規機構主張はしていない。新規データ取得の可否を元の所期判定どおり source-limitedとして保全する。

## 実装

- [Source-only STAC inventory](inventory_2013_2021_original88_landsat7_scene_STAC_gate_20261120.py)
- [Executable GitHub Actions](https://github.com/zuizui0223/mina/actions/runs/44658030485)
