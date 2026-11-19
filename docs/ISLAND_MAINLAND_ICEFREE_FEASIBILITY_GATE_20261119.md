# 島／本土・露岩とペンギン繁殖：先行研究＋原地図の実行可能性監査（2026-11-19）

**位置付け:** 既存の正式なPaper 1・凍結Paper 2・mainに採用済みの肯定結果は変更しない。既存の検定停止条件を保存し、重複した探索をしないためのsource-first監査。**新しい生物学的効果は推定していない。**

## 結論

- **H1 捕食者不在で島／本土差が消えるか:** 南極の陸生哺乳類捕食者不在は有用な系の特徴だが、UK×南極の島効果の差を捕食の因果効果と読む設計は不可。UKの実捕食者曝露・非検出、地理的土地境界、種組成と調査法が非可換。既存V41の地理マッチングもSTOP。
- **H2 露岩・繁殖オプション:** 南極全域の**横断的な**周辺氷なし環境の量・異質性と、反復可能なPygoscelis個体群変動の関連は実行可能。主説明量は既存のoutcome-blind Paper2に凍結済み。**時間的な露岩増加→新定着・回復**は、単一時点の露岩ポリゴンと既知コロニー595地点では識別不能。
- **採る生態学的命題:** 「陸上の繁殖オプションと海洋アクセスがどのような環境でボトルネックを切り替えるか」。陸上面積の単独効果より、条件付き制限因子の解釈に価値。ただし既存凍結解析に後出しの交互作用を追加しない。

## 1. 先行研究の衝突・新規性

1. Lee et al. 2017, *Nature* 10.1038/nature22996: RCP8.5等の強制下で2100年までの氷なし地が最大約25%増加し得る。これは**将来予測された氷なし地の増加**であって繁殖に利用できる営巣面積や、実際のペンギン個体数の増加率ではない。
2. LaRue et al. 2013, *PLOS ONE* 10.1371/journal.pone.0060568: Beaufort島で氷河後退に伴う営巣地増加・アデリー増加・Ross島群への移出減少が観測済み。「露岩増加は使われない」という一方向主張の反例。
3. Santora, LaRue & Ainley 2020, *GEB* 10.1111/geb.13144: 全南極的なコロニー分布・規模には周辺コロニー配置、海底谷、ポリニヤとの関連。陸上地形のみでコロニーサイズを説明する新規性は弱い。
4. Gallagher et al. 2025, *Ecosphere* 10.1002/ecs2.70091: 南極半島のPygoscelis 3種の占有／非占有を500m格子でモデル化し、陸上地形と海氷・海洋の両方が重要。未占有氷なし地を不在として扱う仮定を明示。これを再実施するだけなら新規性不足。
5. Cimino et al. 2026, *Marine Ornithology* 10.5038/2074-1235.54.2.1707（2026-10-15公刊）: Palmer近傍Point 8で2018–2020の氷河後退後にジェンツーの営巣が2020年、ひなの育成成功が2023年に始まった新規定着の直接事例。
6. 南極には陸生哺乳類捕食者が自然分布しないが、skua等による捕食はある。イギリスの捕食圧との比較は「捕食者一般の有無」ではなく「検証された陸生哺乳類捕食者への曝露」に限定する。UKで「本土には海鳥が繁殖できない」と一般化しない。

## 2. 利用可能データと既存の実行結果

| 資料 | 固定情報／利用法 | 注意 |
|---|---|---|
| SCAR Antarctic Digital Database 高解像海岸線v7.13 | 2026-11-12リリース。EPSG:3031。polygon `surface` に `land` / `ice shelf` / `ice tongue` / `rumple`。73MB zip/143MB GPKG。 https://doi.org/10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb | v7.13を今回取得・全点結合したわけではない。公開取得先を確認済み。v7.12の幾何検定失敗を新版で自動解決とはしない |
| Burton-Johnson et al. 2016 | Landsat 8ベース露岩GIS。 https://doi.org/10.5285/f7947381-6fd7-466f-8894-25d3262cbcf5 | 単時点相当、分類精度74±9%（10場面評価）。「営巣可能面積」「年変化」ではない |
| Antarctic Ecosystem Inventory v1.0 | 100m氷なし地、9 Major/33 Habitat Complex/269 Bioregional Type。 https://doi.org/10.5281/zenodo.11629115 | mina既存122候補地点の118（96.7%）に2km半径の氷なし地。面積・タイプ豊富度は凍結済み |
| MAPPPD/APBP | mina Gate0:729 site、152 Pygoscelis site×species候補（57 ADPE /46 CHPE /49 GEPE）、122実site；92長期厳格候補。別の気候物理スコープでは595既知site・271近年実計数site | 595地点すべてを独立した経年個体群／真正不在地点として扱わない |
| UK JNCC原2センサス比較 | PR#198: 1321 source panel、17種、604 country×Master-site network、959個体数減少パネル | ネットワークは物理的島ではなく、サイトの境界／現地捕食曝露が未検証 |
| AADC東南極の定着履歴 | PR#180: 11089件検索イベント。明示的P/Aを連続季節で照合すると A→Pは1件、対象A-risk 29件。遷移ゲート不合格 | missing / not recordedを真のA=不在として補完しない |

### 既存の物理的島比較が停止した定量的理由

PR#197 V41, 2026-10-24: **771**同方法・同出典・隣接年の真正巣数遷移、**95**原site、SCAR v7.12高解像ポリゴンを出典SHA固定で結合。

- site中心が厳密に陸地ポリゴン内 **54**、2km以下の唯一近傍として暫定 **7**、曖昧／一致なし **13**、大陸の最大land proxy **21**。これらは排他的なsource QA分類。
- 同種×同年×同公表地域×同citekey×同vantage×事前距離区分で**同一陸塊 vs 別陸塊**の両方が成立する層×距離区分は**3セル・2地域**のみ。事前ゲートは12セル・3地域・2種・6別陸塊以上。
- 近傍7地点を暫定追加しても14セル中13セルがVictoria Landアデリーで、地域・独立landのゲート失敗。**効果量は推定していない。**
- 新しい海岸線に替えるだけでは元の座標の不確実さ、比較に必要な独立地理単位、交絡を解決しない。正確な現地座標・同等のsource coverageが必要。

UKについてPR#201 V44–V46はアクセス型の種群proxyを比較したが、捕食曝露自体は確認されず、サンプル・観測法の非対称により哺乳類捕食者仮説は支持不能。PR#180の定着動態も遷移数不足で停止。

## 3. 残す解析と、停止した解析を分離

### GO：現在ある構造で可能な関連解析
- **母集団:** 事前凍結Pygoscelis 152 site×species候補、distinct 122 site。AEI面積とrichness完全ケース118 site（相関r=0.164）。
- **事前凍結説明量:** `z(log1p(mapped_ice_free_area_ha_2000m))`、`z(tier2_richness_2000m)`、`z(log1p(elevation_relief_p90_p10_m_2000m))`。既存 `contracts/PAPER2_OUTCOME_BLIND_PREDICTOR_SET_V1.json` に従い、単変数＋構造補正の種別推定から開始。年代・地域・調査法を分ける。
- **意味:** 既知で反復調査された**地点の繁殖個体数変動**と周辺氷なし環境の関連。新しい土地の定着、生息地利用率の時系列、将来個体群の予測ではない。

### GEO-QA ONLY：独立資料から追加できる分類
- SCAR v7.13のlandだけを抽出し、ice shelf / tongueを陸地連続性として扱わない。EPSG3031に全層統一。最大land連結成分を大陸候補にし、南極半島・遠隔島の境界は明示検算する。
- 原コロニー点が単一land連結成分に**厳密に含まれる**場合をexact、独立座標不確実度内の一意landをprovisional、複数候補または大きな外れはambiguousとして保持。新しい任意閾値で救済しない。
- landmass面積、同一land内のrockパッチ面積、海岸からの距離を分ける。2km bufferが海を越えて別の島を含みうるので、氷なし面積を「その島の営巣容量」と呼ばない。面積、斜度、季節積雪、海へ出る可能性は別条件。
- GISのFID=生物学的な島IDとみなさない。更新時ポリゴン分割／結合を監査。source positional uncertaintyを真のGPS精度とみなさない。

### NO-GO：今の公開sourceのみでは検定できない
- UK（島有利）×南極（島差ゼロ）⇒哺乳類捕食が原因、という二地域間因果比較。
- 氷なしの面積が増えたので繁殖地が新設・廃止された、と単一露岩地図から識別すること。
- 既知コロニーの分布を真の占有／非占有データとすること。未記録の露岩地は未調査であって真のゼロとは限らない。
- Palmerのモニター用colony codeに対応する物理営巣パッチを未検証のまま「新しい露岩パッチ」と扱うこと。
- 既存のSTOPした比較を、同じsourceの距離ビンや曖昧割当てを後付け変更して再試行すること。

## 4. 次の判定条件（データ変更が必要な方向を明示）

1. **最短:** 凍結Paper2の118 covered-site・3種類の既存説明量を、正式なoutcome契約下で検証する（H2横断的関連）。新しい仮説探索を混ぜない。
2. **その次:** SCAR v7.13のsource SHA、land面積、コロニー点が陸地に入る／入らない内訳を**outcome-blind**で再記録する。V41を上書きせず地図版間の品質比較として記録。ダウンロードできなければ取得未完として停止。
3. **将来の面積増加→新定着:** 少なくとも二時点の独立な氷河後退／露岩マップと、各候補地での時点別の調査努力付きP/A（未調査≠不在）、コロニー時刻、必要なら海氷・海洋条件が揃ってから事前契約。既存AADCで定着の遷移が少なかった事実を尊重。
4. **捕食者効果:** UK物理地形とdated predator detection / non-detection / effortに、対象海鳥の現地比較できるコロニーデータを結合して初めて機構検定。南極は機構の対照例・予測の一般化可能性を検討する外部系として置くが、無条件の差分の差分とは呼ばない。

## Sources/receipts

- 海岸線v7.13 https://data.bas.ac.uk/items/1c81cf24-576f-43df-be72-a5c7dbb51ffb/
- Burton-Johnson 2016 https://doi.org/10.5194/tc-10-1665-2016
- Ecosystem Inventory https://zenodo.org/records/11629115
- 先行研究: https://doi.org/10.1038/nature22996 ; https://doi.org/10.1371/journal.pone.0060568 ; https://doi.org/10.1111/geb.13144 ; https://doi.org/10.1002/ecs2.70091 ; https://doi.org/10.5038/2074-1235.54.2.1707
- 凍結した主説明量: `main/contracts/PAPER2_OUTCOME_BLIND_PREDICTOR_SET_V1.json`
- v7.12原幾何停止: `docs/MAPPPD_V5_LAND_CONTINUITY_V41_RESULT.md`; [PR#197](https://github.com/zuizui0223/mina/pull/197)
- JNCC site組成: [PR#198](https://github.com/zuizui0223/mina/pull/198); UK捕食者proxy限界: [PR#201](https://github.com/zuizui0223/mina/pull/201)
- 東南極時系列P/Aの遷移不足: [PR#180](https://github.com/zuizui0223/mina/pull/180)

## 5. 2026-11-19 継続監査：既存Paper 2は「未実行」ではない（重要な訂正）

前節「GO：現在ある構造で可能な関連解析」は**既に2026-09-29に本解析から置換検定まで完走済み**。ここを新規解析候補として扱わない。凍結Paper2: 1980–2025、2,100真正巣数観測、107時間ブリッジ済み系列のうち説明量完備104 site×species（ADPE 41/CHPE 34/GEPE 29）。主要モデルは種ごとの共通潜在年要因に対するサイト応答（loading）と2 km繁殖オプション面積A、Habitat Complex richness H、A×Hとの関連。**単純な個体数増減の回帰ではない**。

- 凍結主効果 `gamma_AH`: ADPE **−0.303571**（Holm p=0.2162）、CHPE **−1.184398**（Holm p=0.1689）、GEPE **−0.318226**（Holm p=0.1689）。3種の中央値 **−0.318226**、9,999回地域ブロック置換のpaper-level **p=0.0947**。否定でもなく確認でもなく、一般則に対する**非確証**。
- A-only 3種の方向は全て負だがHolm p=0.4278 / 0.6134 / 0.6134：単純な「広いほど気候変動を緩衝」も支持されず。
- 半径を1/2/5 kmにするとcross-species gamma_AH中央値は **−0.057655 / −0.318226 / +0.106781**。5kmでは3種とも正。複数半径の帰無まで含め、真の生物学的scale-dependenceの確認としては扱わない。
- この試行は**既に凍結した結果**。同じ点・同じ説明量を使用して閾値・年範囲・環境時期を後付け変更して新しいp値を探すことは禁止。

根拠：`main/results/PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json`、`main/results/PAPER2_A_BUFFERING_SECONDARY_RESULT_V1.json`、`main/results/PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json`、`main/docs/PAPER2_MANUSCRIPT_SPINE_V0_1.md`。前節の「次の判定条件1」は**完了・非確証**に訂正。

## 6. 公開資料の追加：新しい空間データと真の時間軸を区別

- **SCAR ADD v7.13高解像land polygon**（2026-11-12） https://doi.org/10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb 。`surface`=land/ice shelf/ice tongue/rumple。出版社は1990s–2026の多年代素材を合成すると明記。**v7.12とv7.13のland差分は真の「2026年に露出した露岩」ではない。** v7.13のShapefileは約73 MBだが、今回の実ファイルをこの環境にダウンロードできず、site 95件の再照合は**未実行**。版更新はGEO-QAの独立資料であって旧V41の生物学検定の再開ではない。
- **BAS Zavodovski polygon time-series 2010/2011/2016/2020/2022/2025** https://doi.org/10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308 。原時点ごとにデジタイズしたchinstrap/macaronisの占有コロニー領域があり、2023-12に高解像UAV + nesting density calibration。**重要:** 雲などで欠落した部分は近接時期のpolygonを補完したと明記。原polygon year/validationと画像被覆率を照合せずに増減を「真の変化」と扱わない。しかもZavodovskiは**約56.3°S**にありSCAR ADD南緯60°以南の対象域外。これを本土/島のADDと無理に結合しない。独立なphysical landmassは**1島**なのでマクロ法則の種間・島間反復はない。
- **Loebel et al. (2025) 南極半島42氷河の2013–2023カービングフロント** https://doi.org/10.5194/essd-17-65-2025 。時間的氷河前線情報はあるが、**全面的な露岩パッチ/巣適地の年ごとのpolygonではない**。沿岸後退前線を営巣可能面積増分と等置しない。42氷河と調査ペンギン地点の重複をoutcome-blindに照合する段階が必要。
- **Cimino et al. (2026)** https://doi.org/10.5038/2074-1235.54.2.1707 。Point 8（Anvers島）：2018–2020の氷河後退、2019初観察、2020初営巣、2023ひな成功。先行実証例なので、この「発見」自体は今回の新規知見にはできない。
- **既存AADC東南極P/Aサポート** [PR#180](https://github.com/zuizui0223/mina/pull/180) は連続年の真のA→P **1件**、A-risk **29**。ここから単年度の定着 hazard を共変量付きで識別できない。

### 更新した次の主目標

既存Paper2の露岩×個体数負傾向を再計算するのではなく、**『新規露岩曝露パッチを実地に確認した候補地全体』と『同じパッチの訪問済み明示的A/P』を組にした新しいrisk-setデータベースが複数の独立したlandmassで成立するか**のsource-only gateとする。必要なデータ列：`patch_id, landmass_id, actual_image_date, previously_icecovered_evidence, first_exposed_date_interval, survey_site_id, survey_season, survey_effort_verified, surveyed_A_or_P, spatial_identity_status, publisher_citation`。未訪問をA、日付不明を直近年、静的ADDの版差を真の新露岩に変換しない。

**設計結論:** 完了済み Paper2 の新しいp値は追加しない。Zavodovskiは「時系列繁殖地polygonの取得可能性」を示す1島のpilotに限定し、Zavodovskiを含む群島間比較や、露岩増分→colonization生物学検定を始めるには、別の独立した土地・観測risk setが必要。現時点では新しい生態学的効果を主張しない。
