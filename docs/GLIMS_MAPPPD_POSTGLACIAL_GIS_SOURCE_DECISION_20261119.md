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

## Final continuation: publisher GIS → rock chronology → actual MAPPPD survey support (2026-11-19)

**This section supersedes the earlier note that SCAR landmask CI #44482381462 was still running.** That original ArcGIS GeoJSON attempt completed at a protective **HOLD** because the region response exceeded the 60 MB cap. It is **not** evidence for no Antarctic land. We changed source-delivery mode rather than relaxing any ecological threshold.

### A. Original authoritative source downloads verified

- BAS SCAR ADD 7.13 **original 73 MB high-res coastline shapefile ZIP** read successfully from the official catalog, SHA256 `1e9103e9afaa012b0746eec487c0a473c70834bfc85220f89082e747658aaa66`. It contains **17,689** polygons, including **17,257** valid land polygons and **432** non-land polygons (source row IDs are not biological island IDs). [Source zip CI #44506963769](https://github.com/zuizui0223/mina/actions/runs/44506963769).
- BAS ADD 7.11 **original high-res rock outcrop ZIP** read independently, SHA256 `e21f76b886e723ba5009d971946de55a6f6eb43fd0e9c9d2920bb265a6df9d76`. Original DBF has **74,781** rock records, including **40,019** whose `sourcedate` is **2019 or later**, and **34,590** without usable `sourcedate`; date precision is provided by `sourceprec`. The rock layer is compiled from multiple decades and does not establish exposure timing by itself. [Rock source CI #44508221303](https://github.com/zuizui0223/mina/actions/runs/44508221303).
- GLIMS remains the earlier, source-acquisition-date audited WFS of old/new same-ID glacier outlines (possibly differing map identity), 144 positive apparent old-minus-new geometries across the 3 pilot boxes. Historical source dates may differ from colony observations and do not prove newly exposed rock.

### B. Sample-funnel: **same grain is original penguin site ID** except first row

| GIS/source data gate | Retained original MAPPPD site IDs | Meaning |
|---|---:|---|
| Pygoscelis known sites inside 3 fixed source pilot bounding boxes | **133** | This is not 133 surveyed vacant habitats |
| Exact unique original SCAR land polygon feature | **101** | Not 101 independent islands |
| Source land + apparent GLIMS old-minus-new geometry <=1km within *same source feature* | **36** | Source geography, not rock |
| + later source-dated mapped rock polygon on that land and in GLIMS-difference geometry, <=1km | **25** | **Geographically and temporally coherent source candidate**, not new exposed breeding patch |
| Of 25, some original MAPPPD nest counts recorded | **15** | Known breeding sites (20 site×species with counts) |
| Of 25, any nest count observation **strictly after 2024 rock source year** | **3** | 2025 observations at Jougla Point, Py Point, Truant Island. Only **4 site×species** records |

For 5km the same-source-land numbers are **51**, and after later-source-dated rock screening **41**. The 1km candidate count is **4 Anvers, 10 King George, 11 Livingston**; these 25 site IDs fall on **10 original SCAR land map features**. Not independent 25 physical islands, and some source FIDs may depict subparts of one landmass.

Source rock maps for the 25 candidates use **2024** source acquisition years; the paired later GLIMS outline years range **2002/2005/2013/2019**. The rock was imaged later, **but it could have been bare already** at the earlier glacier-date period.

Original code: `scripts/audit_glims_scar_v713_official_zip_landclip.py`, `scripts/audit_glims_scar_rocktime_source_support.py`; numerically successful [source landmask CI #44507460876](https://github.com/zuizui0223/mina/actions/runs/44507460876) artifact 14520326734, and [three-source chronology CI #44508816915](https://github.com/zuizui0223/mina/actions/runs/44508816915) artifact 14520279224. Result receipts on this branch: `results/GLIMS_SCAR_V713_OFFICIAL_LANDMASK_QA_20261119.json`, `results/POSTGLACIAL_THREE_SOURCE_SURVEY_SUPPORT_DECISION_20261119.json`.

### C. Crucial actual annual survey support check

We opened only the provenance-pinned `mapppdr` original `penguin_obs.rda` metadata for the 25 frozen source candidate sites; we did not fit any demographic or climate coefficient. Original MAPPPD has recorded nest counts at **15** of the 25 sites, for **20 site×species** units. Only **3 original site IDs** (Jougla Point, Py Point, Truant Island; 4 site×species units) have any recorded nest-count season strictly after the 2024 rock image year.

One candidate site, **Llano Point**, has original chinstrap nest records including numerical zeros in **14 breeding seasons**, but the external **survey effort, exact physical patch definition, complete non-detection protocol and census boundary continuity are NOT established**. A numeric zero therefore does **not** become confirmed surveyed absence A. No source-supported `A→P` can be calculated.

A particularly clear warning against inferring a new colony from 2024 mapped rock: **Jougla Point gentoo** already has observed nest counts going back to **1982** (33 distinct nest-count seasons 1982–2025), and **Py Point gentoo** likewise has historical records from **1982**. These examples mean *near later-mapped rock* is not logically *first use of that formerly glaciated exact nest patch*. Even original 0m geometry overlap is not a confirmed nest-footprint ↔ glacier-outline crosswalk.

Source-only code `scripts/audit_glims_rocktime_mapppd_survey_support.py`; [successful original MAPPPD survey provenance CI #44509366291](https://github.com/zuizui0223/mina/actions/runs/44509366291), artifact **14521900139**. The required truly surveyed unoccupied risk-set rows are missing, not ecologically absent.

### D. Final ecological decision and next data requirement

**STOP_ECOLOGICAL_COLONIZATION_INFERENCE_SOURCE_RISK_SET_NOT_IDENTIFIABLE.** We have a useful, independently derived 25-site **GIS reconnaissance shortlist**, but it is not an island-ecology generalization, environmental effect, new-colony count, or future population forecast. Paper2 2km abundance-response architecture effect remains preregistered **non-confirmatory (p=0.0947)** and is not rescued.

To make the intended macroecological colonization analysis possible, the next *decisive* dataset is not a fourth static map. It is a common **candidate exposed-patch risk set** with (i) dated original imagery proving ice→bare-rock at that exact patch; (ii) source-verified exact penguin nest-patch polygon correspondence; (iii) repeat visits documenting explicit A and P and year-specific survey effort, including **vacant** patches; (iv) independently verified physical landmass IDs. Without that new source, do not fit another climate/rock/settlement regression or retrofit `NR/missing` to A.

Original script and source-only tests remain in branch `analysis/postglacial-glims-sourcegate-20261119`; main, frozen Paper1 and Paper2 are unchanged.
