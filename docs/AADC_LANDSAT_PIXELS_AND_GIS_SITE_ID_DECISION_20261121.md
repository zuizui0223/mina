# AADC実観測16件 × Landsat全件メタデータ・画素品質・元GISの照合（2026-11-21）

## 結論

**衛星画像が「ある」ことと、南極の営巣地が「新たな露岩へ変わった」ことは別問題。** 16件の観測上A→P報告、14 source site IDから、時期の前後に画像があるのは8件。その8件に同じ処理を当てて **32画像の Landsat QA_PIXEL 5×5画素を実際に読めた**が、前後両年に雪氷・水面・欠測等を除いた**候補画素がある事例はゼロ**。これは**調査地点中心だけ**の品質診断であり、周辺の岩場不存在や氷河後退の否定ではない。

AADC 2016/2025公式Shapefileにも14イベントの元`geog_site_id`と完全一致する属性キーはない。**地点中心→営巣パッチの地理対応が欠けている**ことが今の決定的な制約。

## 実行したことと数値

| 証拠段階 | 結果 |
| --- | --- |
| AADC原データ expert/grade検証済みA→P観測報告 | 16件・14 site ID（真の新規定着16件とは呼ばない） |
| 2つの繁殖季節の両方にLandsat sceneメタデータあり | **8件**（P季節のみ4件、両季節なし／時代外4件） |
| 16件のEarth Search original sceneメタデータ取得 | 32クエリ成功、第一ページのscene延べ349。20の非空クエリでnextリンクあり、全scene数とは断言しない |
| 元USGS S3 QA_PIXEL read | 2地点・8画像を試行 → **8件すべてRequester Pays匿名制限**。画質の不良ではない |
| 代替のMicrosoft Planetary Computer STAC署名付きCOG | **8件×前後各2画像=32/32 QA_PIXEL読取成功**。画像は20ユニークSTAC ID（同一衛星画像を複数地点が共有） |
| 各画像の地点中心5×5画素（30 mピクセル） | 32画像中3画像で雪氷/水面/雲等を除いた候補画素あり。**3画像ともA報告の季節**、2地点（IS_70714、IS_70731） |
| 画像の前後とも候補画素あり | **0/8地点**。これは氷河後退の否定ではなく地点中心の画像品質ゲート |
| AADC 2016 original source geology polygons | 4,881ポリゴン。属性 FEATCODE/UFI/Subgroup、14 source geog_site_id直接一致 **0** |
| AADC 2025 original source continental site polygons | 2,923ポリゴン。Site_ID等はあるが14 geog_site_id直接一致 **0** |

### 由来と再現性

- Source 16高確実度 A→P: [Actions #44530909415](https://github.com/zuizui0223/mina/actions/runs/44530909415)
- Landsat catalog 16全件: [Actions #44850629480](https://github.com/zuizui0223/mina/actions/runs/44850629480), artifact 14684739302; `results/AADC_16_EVENT_LANDSAT_STAC_SOURCE_QA_20261121.json`
- USGS requester-pays access attempt: [Actions #44851029702](https://github.com/zuizui0223/mina/actions/runs/44851029702), artifact 14685995012
- Microsoft PC pilot: [Actions #44851249554](https://github.com/zuizui0223/mina/actions/runs/44851249554), artifact 14685526579
- Microsoft PC **8件全実画素**: [Actions #44851408828](https://github.com/zuizui0223/mina/actions/runs/44851408828), artifact 14685108425
- AADC publisher original GIS IDs: [Actions #44851710270](https://github.com/zuizui0223/mina/actions/runs/44851710270), artifact 14685966256

QA_PIXELはUSGSのビット定義でfill, dilated cloud, cloud, shadow, snow/ice, waterを除外。Landsat4–7で既知の問題があるclear bit6単独判定は使わない。[USGS QA](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands) / [Known issues](https://www.usgs.gov/landsat-missions/landsat-collection-2-known-issues)

## 次の地理データで確認すべき一つの条件

`geog_site_id`に**実際の物理的営巣パッチ境界**が紐付く必要がある。直接一致はなく、候補として元2016 site workbookのSCAR Gazetteer Place IDとoriginal SHPのUFI間の**著者が定義した同一ID規則**を原資料で検証する余地がある。これが確認できない場合は空間結合を後付けの最近傍・数値部分一致で救済しない。

元データだけでは「氷河後退で出現した露岩へコロニーが新規定着」も「島が避難所になる捕食者因果効果」も検定不能。**追加のp値や相関係数は作らず、mainとPaper1/Paper2は変更しない。**

## 最終補足：著者による間接ID対応も検定済み（2026-11-21）

2016年AADC原資料の `2_Geographic sites` 4,884地点を開くと、今回の16 A→P記録に含まれる**14地点IDすべて**が存在した。したがって「古い地点表に載っていない」問題ではない。

ただし、間接的に原GISへ結ぶことも現時点では支持されなかった。2016年スプレッドシートの `SCAR_Gazeteer_Place_ID` は**12/14地点で存在、2地点（IS_121、IS_70694）では空欄**。同じ出版社配布の4,881原ポリゴンDBFの `UFI` と照合すると、**12件中完全一致0、複数一致0**。2025年continental site shape（2,923ポリゴン）の `Site_ID` も14件の原 `geog_site_id` とは完全一致0。

つまり、**原データに地理的ポリゴンが存在しても、今回の実際の地理地点IDから、正確な営巣パッチポリゴンへたどる信頼できる鍵がない**。別系統のID文字列を数値部分や最近傍などで強引に結び付けてはならない。もし取得できるなら著者定義のcrosswalk、UFIの命名ルール、または現地巣分布GISが決定的な追加資料である。

- 原sourceでの独立検証: [Actions #44851935846](https://github.com/zuizui0223/mina/actions/runs/44851935846), artifact **14684964739**
- 原コード: `scripts/audit_aadc_gazetteer_UFI_original_crosswalk.py`
- 凍結した判定: `results/AADC_GAZETTEER_UFI_GEO_SOURCE_GATE_20261121.json`

**この時点で本線のGO/NO-GOを確定:** 画像一覧取得GO、局所QA読取GO、対象コロニー巣パッチの同一性確認NO-GO、新たな露岩出現の実証NO-GO、新規定着の因果検定NO-GO。AADCの観測A→P 16件は確実なsource観測差だが、氷河後退因果の16件ではない。凍結済みPaper 1、Paper 2、main、従来の旧PR #180は変更しない。
