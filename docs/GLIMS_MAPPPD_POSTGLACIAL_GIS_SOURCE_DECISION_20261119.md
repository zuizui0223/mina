# 南極氷河後退×ペンギン繁殖地：実測地理ソースの適格性（2026-11-19）

## 観測が終わった部分

- GLIMS公式WFSで3調査矩形内の氷河輪郭639件を取得。取得日付き同一GLIMS IDの複数輪郭をもつ候補は172 ID（58 King George周辺、75 Livingston周辺、39 Anvers周辺）。この数は独立した島・定着イベントではない。原source GitHub Actions **44480527812**、artifact **14508760799**。元レシート `results/GLIMS_ANTARCTIC_ISLAND_SOURCE_SUPPORT_20261119.json`。
- GEOS真正輪郭をEPSG3031へ投影し、同じGLIMS IDの最古-最新の輪郭差（最低5年間）をGISで計算。欠陥のある輪郭は修正せず除外。正の見かけ差分を持つGLIMS ID **144**（Anvers 21、King George 51、Livingston 72）。これらの差分は海への崩落・画像/ポリゴン作成差・座標ずれを含み、実露岩ではない。
- MAPPPD固定コミット `88c73a507e0921b2541c218c71eaf16721bc6502` のPygoscelis既知 **664 site IDs**中、3矩形に**133 site**。ポリゴン差への距離で**59 site≤1 km、109 site≤5 km**。Anvers 10/16（計28）、King George 23/38（計40）、Livingston 26/55（計65）。一部0mの値は元サイト座標と作図の不整合の可能性があり、新規営巣とは呼ばない。Actions **44481091708**、artifact **14509050447**。機械可読台帳 `results/GLIMS_MAPPPD_APPARENT_RETREAT_SOURCE_PROXIMITY_20261119.json`。サイト別CSVはartifact。
- SCAR ADD v7.13公式ArcGIS FeatureServer layer 1 (`surface=land`) は使用可能。上記3矩形内の「陸地ポリゴン地物数」はAnvers **1571**、King George **1236**、Livingston **1716**。Actions **44481966050**、artifact **14509510392**。**landは岩ではない、氷に覆われた陸地も含む。** v7.13は1990年代〜2026年原資料を合成している静的地図であり、版差から露岩の暦年変化を求めてはならない。
- `scripts/audit_glims_scar_landmasked_proximity.py` と `tests/test_glims_scar_landmasked_proximity.py`、原データでの静的陸地マスクCIを登録済み。対象SCARマスクは海へ突き出たGLIMS見かけ差分を除く補助フィルタで、新規露岩を証明しない。**CI 44482381462** は起動済みであり、元結果が検証されるまではクリップ後の該当地点数を記載しない。

## 現在の結論・停止条件

1. **SOURCE AVAILABLE:** 同じ氷河IDで複数年代の輪郭と、近傍にペンギンの既知コロニーがあることは原ソースで確かめられた。
2. **TRUE NEW ROCK UNVERIFIED:** GLIMS旧−新差分は、新規に露出した実地岩盤領域、営巣に利用可能な面積、または陸地を増やした因果効果の証拠ではない。将来は各元画像の日時・氷から露岩への遷移・当時の海岸線と積雪を別途検証する。
3. **A/P RISK SET MISSING:** 133既知コロニー地点は旧来の観測された繁殖地であり、未占有候補地の調査済み真の不在は含まない。既存AADC東南極連続A→P 1件の失敗ゲートを無断で救済しない。
4. **NO ECOLOGICAL MODEL:** 本日新たな個体数係数、定着率、p値、将来繁殖予報、捕食者差の因果結果は算出していない。以前Paper2 2km面積×異質性の確証結果はp=0.0947のまま。凍結済みPaper1/Paper2を編集・上書きしない。

## 出典と原ジョブ
- GLIMS/NSIDC WFS `https://www.glims.org/geoserver/ows`。
- BAS SCAR ADD v7.13 `https://doi.org/10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb`。
- 原GitHub Actions: https://github.com/zuizui0223/mina/actions/runs/44480527812 ; https://github.com/zuizui0223/mina/actions/runs/44481091708 ; https://github.com/zuizui0223/mina/actions/runs/44481966050 ; https://github.com/zuizui0223/mina/actions/runs/44482381462 .
