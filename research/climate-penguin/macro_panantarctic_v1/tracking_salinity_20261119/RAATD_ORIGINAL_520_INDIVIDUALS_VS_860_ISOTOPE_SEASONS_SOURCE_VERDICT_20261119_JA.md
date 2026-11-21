# 原RAATD追跡×アデリーδ¹⁵N光学proxy：同一繁殖地点・同年で統合できるか

**2026-11-19 JST｜Mina draft PR #214｜source-pinned tracking data feasibility audit DONE｜判断：既存δ¹⁵N 860地点×季節への大陸横断の追跡統合は現状NO-GO。** `main`にマージした5つの原source検証済み肯定結果、凍結済み論文本文・図を**変更しない**。本レポートで新しい追跡×塩分の有意係数は推定していない。

## 1. 実際に元追跡データを取得した

- 2020 **RAATD filtered-noTMB** 著者版 https://zenodo.org/records/3722948 。取得した元 `SCAR_EGBAMM_RAATD-filtered-noTMB.zip` **263,549,220 bytes**、元発行者MD5 **168e5b9b5c4ed20bb84dd00145acb0a5**と完全一致。これは**source data original**であり抽象論や論文の図にある推計個体数だけから推測したわけではない。
- ZIP内部は `RAATD_metadata.csv`と`ADPE_ssm_by_id_predicted.csv`等、CSV 18 original members。原filteredアデリー *Pygoscelis adeliae* **520 original individual IDs、90,202 state-space-position estimates**。デバイスはmetadata上 **PTT 372／GPS 148**。元RAATDの対象全体は1991–2016年、今回の11〜翌2月・1996–2012年だけでは**458 original individual×breeding-season rows、16季節**。個体IDはdeployments / device trajectoriesであり、同一採餌trip・独立コロニー数とは異なる。
- 元同位体：Youngflesh et al. (2026) Zenodoに基づく **860 original site×season、88 site、13 regions（1996および1999–2012の15 seasons）**、2026-11-17 source freeze original isotope artifact 14328755565。原595 site MAPPPD inventory artifact 13669533413。両元sourceのダイジェストを別々に検証。
- 元RAATDデプロイ地点WGS84と元MAPPPD catalogueの**δ¹⁵N観測済み88 site**との楕円体測地距離で5、25、100kmを計算。**RAATD filtered estimated位置のtimestamp**が元δ¹⁵Nに実観測のある**11月〜翌2月の同じbreeding season**かを原individual IDで確認。単なる「同じ地域でどこかの年に追跡した」を重複と呼ばない。

## 2. 元sourceの厳格な真時空間重複

| 地理対応の基準 | δ¹⁵N site×season一致 /860 | 区別できる原同位体site | 原報告地域 | 一致する追跡individual IDs（地域の独立レプリケートではない） |
|---|---:|---:|---:|---:|
| **最寄り原isotope site ≤5km、次点site >5km** | **4 (0.47%)** | **2** | **2** | **136** |
| 最寄り原isotope site ≤25km（別siteも近くにあってよい、暫定最寄り割当） | **6 (0.70%)** | **3** | **3** | **156** |
| **原isotope site ≤25km、次点site >25km（一意な25km帰属）** | **0** | **0** | **0** | **0** |
| 最寄り原isotope site ≤100km（広域上限感度・帰属不明） | **14 (1.63%)** | **6** | **4** | **268** |
| 100km以内で二番目のisotope siteは範囲外（厳格な100km一意） | 7 | 2 | 2 | 105 |

**半径を拡大したのに一意帰属数が減るのは矛盾ではない。** 例えば本来site Aから1km・Bから10kmのdeploymentは、5km検索ならAへ一意、25km検索ならA・Bどちらも範囲内で一意帰属不能になる。最初のQAはこの論理に反して「5→25→100kmの一意照合数は単調増加」と誤って仮定していた。**元追跡データや集計ではなくQAの仮定が誤り**。2026-11-19再実装では「nearest within km」と「unique within km」を別々に記録、唯一単調増加が必要なnearestの同site×year数で確認した。

### 5km一意に対応した4 site×season（元GPS/PTT）

| 元MAPPPD isotope site | 元breeding season | 元tracked individuals | 元RAATD Nov–Feb filtered position estimates |
|---|---:|---:|---:|
| INEX, Inexpressible Island (Victoria Land) | 2001 | 2 | 935 |
| PGEO, Point Géologie (Adelie Land) | 2010 | 42 | 9,423 |
| PGEO, Point Géologie (Adelie Land) | 2011 | 36 | 8,526 |
| PGEO, Point Géologie (Adelie Land) | 2012 | 56 | 11,755 |

**25km nearestを使うと**さらにMAWS（Mac. Robertson Land）2001（8個体）・2002（12個体）が加わる。ただし**同一25km内に少なくとも2つの元isotope colony siteがある**ため、これら6 site×seasonは原観測個体の特定コロニー帰属を証明しない。もちろん元Landsatδ¹⁵Nがこれら追跡個体の糞を測った証拠もない。

## 3. 結果前に固定した開始ゲート（不合格）

[事前コミットした契約](FROZEN_RAATD_ISOTOPE_OVERLAP_AND_NOVELTY_GATE_JA_20261119.md)：25km一意に対応する元GPS/PTT≥3個体のsite×breeding-seasonが**12以上、3独立報告地域以上、3繁殖季節以上**であれば、個体used–available塩分環境比較の追加候補とする。

- 25km一意対応の ≥3個体site-season **0 / 基準12**、元報告地域 **0 / 基準3**。
- 5kmというより厳格な距離でも、生物学的なsite-season対応は4/860、追跡個体3以上のsite-seasonは**PGEO 2010–2012の3件**、ただの**1個の独立報告地域**。
- 25km nearestを全て認めても**6/860 site-season、3地域**であり、12site-season基準には届かない。後付けで半径・site帰属・季節・個体数の基準を緩めて「AがGO」とはしない。
- RAATD元filtered個体520は、既存88同位体観測地点との同時期site×seasonでは**136個体／4 matched site-seasons**（5km条件）。個体が多いことは4独立生態系試験を136に増やさない。

**正式判断：NO_GO_TRACKING_ISOTOPE_MACRO_JOIN。** 同じ元δ¹⁵N観測site×seasonに追跡データを機構の第2部として結合するA案は、現有公開RAATDでは**地理・年の実測重複が足りない**。追跡した個体の直接食性（胃内容・DNA・δ¹³C/δ¹⁵N・CSIA-AA）もないため、仮に個体の塩分環境選択を確立しても「塩分が魚食率を変えた」は直接検定できない。

## 4. 新規性はどこにあり、何が既に知られているか

- Ropert-Coudert et al. (2020), `Scientific Data`, DOI https://doi.org/10.1038/s41597-020-0406-x：RAATD原データ品質と全南極・南大洋のトラッキング。Hindell et al. (2020), `Nature`, DOI https://doi.org/10.1038/s41586-020-2126-y：元RAATDで捕食者重要海域と保護区を定量化。
- 2019 `Scientific Reports`, DOI https://doi.org/10.1038/s41598-018-35901-7：Palmerアデリー・ジェンツーが海流収束を選ぶことが示され、2021 `Limnology and Oceanography`, DOI https://doi.org/10.1002/lno.11750 はPalmerの種別の違う水塊・塩分環境を記載。
- 2026 `Global and Planetary Change`, DOI https://doi.org/10.1016/j.gloplacha.2026.105518：南極半島アデリー追跡×海洋再解析から採餌生息地の将来適地予測。2026 `Progress in Oceanography`, DOI https://doi.org/10.1016/j.pocean.2026.103798：5種・**3,189個体／59コロニー**、RAATD再利用も含めた中規模渦と行動の関連（ARS）を解析。いま「RAATDを使った広域追跡研究」を新発見と呼ぶことはできない。
- 今後独立の実測が揃った場合の新規性は「**同じ個体・日付・到達可能範囲での塩分水塊環境選択が、海氷・水温・海流/渦・地形を超える追加情報か、それが独立3地域以上で再現するか**」。ただしRAATD filtered SSM位置の密度は採餌成功ではない。

## 5. 主線の判断と成果物

**今のv0.6主線を弱めない**：mina/mainに5つの原検証済み肯定結果が残る。塩分–衛星推定δ¹⁵Nの全860系の条件付き**正相関**は維持する（β=+0.834‰ per original salinity unit; partial residual R²=2.88%; 13地域保守区間は0横断）。今回の追跡site×season不足はその観測相関を「否定」するものではないが、因果食性や未来の巣数を支持する新しい独立データにもならなかった。

**確認済みsource–algorithm**：[2020元RAATD overlapの原本アクセス・Python](audit_original_raatd_adelie_isotope_overlap.py)、[元source digest＋元source年月×site照合 GitHub Actions #44444166200 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44444166200)、artifact **14492462605**。本コミットに第三者の原追跡軌跡・個体ID・研究者メールアドレスを再公開しない。出力は **5 derived files**：元2020 MD5と源860/88 source SHAを持つ判定JSON、5/25/100km nearest/unique観測数表、5km uniqueと25km unique/nearest のsite×season現存性表だけ。

**エラー経路と修正**：初回sourceダウンロードとdigest成功→発表元metadataは非UTF8で最初のschema読込が停止→legacy文字コードとしてASCII地理ID保全の上読込成功→誤った半径単調性QAが失敗→nearest/uniqueを区別して固定25km主判定のままCI成功。何れも、観測閾値を動かして有利な生態効果を探索したのではない。

**結論：Aは元88site/860seasonとの直接機構接続には非適合。** 広域RAATDだけの独立したused–available水塊環境解析は別の研究として設計可能だが、これを同source δ¹⁵N食性変化の独立証拠・将来食性予測として統合しない。今後は同year・同生物/採餌時期の独立地域の直接餌試料または追跡＋餌データが必要。
