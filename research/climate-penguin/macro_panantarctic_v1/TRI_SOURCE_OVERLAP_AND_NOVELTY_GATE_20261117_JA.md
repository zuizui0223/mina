# 2026年の原資料と mina の結合可能性：食性・繁殖時期・繁殖配分の時間支持ゲート

**2026-11-17 JST／未統合 Draft PR #214 の補助的 source-feasibility audit。論文v0.5、凍結Paper 1/2、主図や既存の数値は変更しない。** 本文は実ファイルをダウンロードして結合した結果ではない。公表資料と公開した著者コードから、ソースの存在と最大の時間的交差を監査したもの。

## 本当に確認した独立の資料と既刊結果

| 系列 | 元の資料・出典 | 年の定義・支持 | すでに出版済みの主張 |
| --- | --- | --- | --- |
| アデリー食性 | Youngflesh et al. (2026), *Current Biology*, https://doi.org/10.1016/j.cub.2026.06.028 ; original archived https://doi.org/10.5281/zenodo.17409948 ; authors' code https://github.com/caseyyoungflesh/penguin_diet_from_space | Landsatによる1984–2013年（season/site/dayを原著コードで保持）。実データは GitHub の `Data/` に含まれず Zenodo。 | 海氷と食性の関連、食性と長期増減の関連（したがってこの単純な2本の相関は新発見でない）。 |
| 3種繁殖時期 | Juarez Martinez et al. (2026), *Journal of Animal Ecology*, https://doi.org/10.1111/1365-2656.70201 ; data https://doi.org/10.5281/zenodo.17642754 | カメラ設置シーズン2011–12〜2021–22；本文の解析結果表記は2012–2022。37コロニー、77カメラ、475 camera-seasonのうち277のみ有効。 | 3種の定着時期前進を既に実証。Appendix S5の個体数トレンド図はMAPPPD計数から作成されている（独立な新人口データでない）。 |
| 巣数 | `mina` 凍結 sourceで選定されたMAPPPD 595 known sites／2,456 method-consistent count records（全てのsite×年が観測されていない） | 指標の比較用固定期間1991–2020。2011–2020に少なくとも1計数が存在するのは271 site、毎年観測という意味でない。 | v0.5の既知サイト間再配分。真の定着率、繁殖成功、移動個体は直接ない。 |
| 海洋環境 | OSI SAF海氷（1991–2020）と GLORYS海水温・表面塩分（1993–2020） | 588 mapped sites／378 distinct ocean wet cells。近海100km SICとモデル格子であり、GPS採餌範囲ではない。 | 海氷・水温PC1と主に塩分PC2。統計的直交は因果的独立ではない。 |

**元論文の使用したpopulation dataに重複あり**。Juarez Martinez et al. Appendix S5がMAPPPD nests を既に図示、Youngflesh et al. は同時にdiet vs population trendを既刊。両研究とminaの元巣数を結合しても、独立個体数の3回の追試として数えない。

## 時間支持の実際の算術（最大値、同地点・同種の一致前）

公開された年度端点の共通部分を `[max(starts),min(ends)]` として交差させた。これは一致する観測レコード数ではなく**結合し得る年の理論的上限**。

| 結合対象 | 年の積集合 | 上限年数 |
| --- | --- | ---: |
| 食性 × カメラ定着 × 巣数 × 海洋環境 | **2011–2013** （定着を2012開始と読めば2012–2013） | **最大3年／本文解析年では2年** |
| カメラ定着 × 巣数 | 2011–2020 | 最大10年 |
| 食性 × GLORYS塩分 × 巣数 | 1993–2013 | 最大21年 |

**主判定：3つの生物応答（食性・定着・巣数）を、原集団の季節に完全に揃えて長期の気候→食性→時期→個体数の逐次媒介モデルにかける設計は時間支持が不足。** 0〜3年の真の重複で複数の地点・年ラグ・空間固定効果を安定推定できると主張しない。

## 著者コードから確かめた結合キーと未確定箇所

- 食性コード `Scripts/4-diet-est.R` では `site_id` × `season` × `doy`、`Scripts/5-diet-model.R` では `site_id` × `season` および `longitude/latitude`。著者 `Scripts/1-process-abiotic-data/1a-process-locations.R` はLandsat由来幾何から site centroids を再構成している。これはMAPPPD site ID一致の証明ではない。
- カメラの `PETE` と `LLAN` は原著本文の colony abbreviations に実在。minaの元厳格両年代標本にも `PETE` と `LLAN` という site_id がある。しかしID文字列一致のみを同一巣区画や同じ場所のカメラとして自動採用しない。Appendix S1 のカメラ座標と原巣数のsite_id/座標に照合し、camera複数→colony一つをまとめて独立標本数を偽増ししない。
- 食性原本 DOI とカメラ原本 DOI は公表文献で確認したが、この監査環境からZenodo本体の実ファイル取得はできなかった。元レコードID、実際の同一地点同一繁殖シーズン件数、測定誤差posteriorは**未検証**。
- 巣数の調査季節と調査日を確認する。食性のLandsat画像撮影が年内の「定着後」なら、同年の食性を「定着の先行原因」に置くのは禁止。海氷も8–11月平均だと10月定着後の月を含むため、前定着期に切るか事後曝露と明記。

## 次に検証する新規性のある一つの条件付き仮説（結果ではない）

**「既刊の sea-ice→diet の関係に対し、同一アデリー colony-season の塩分の地点内偏差は追加情報を持つか？」**

学術的新規性を持つ可能性はあるが、塩分は氷河融水・水塊・混合・海洋生産の代理であり、塩分自体の因果作用を想定しない。実際の検証はまず食性原本と `site_id × season` により1993–2013の原年を突合し、次を順に満たした場合に限る：

1. 元 colony GIS／座標の一致・season一致・測定日の前後順・本当に独立な海洋セル数・食性測定の不確実性を監査。相関の符号やp値を見てサイトを選ばない。
2. 同じ対象の比較で元年/site/原地域を揃え、気候ベース `f(SIC)` に対する **塩分偏差の増分**を評価。可能ならregion-yearの共有条件を吸収、site/region held-out の外部移用を別途検査。原地域と海洋セルが交絡し、独立したwithin-site塩分偏差が乏しければモデルに進まない。
3. 出力は食性と物理環境の**条件付き関連**。改めてその推定係数をCMIP6 salinityへ掛けて「将来の繁殖巣数」を予報することは禁止。食性測定値や予測posteriorが得られず不確実性が持てなければ source NO-GO として記録。

## 現在地

- **完了**：2論文の既刊の到達点と公開データ所在、著者コードのsite×season構造、時間支持上限（2–3 / 10 / 21年）を独立に固定。
- **未完了**：Zenodo原ファイル取得、same-site原地理crosswalk、実際のmatched source records、塩分増分の再計算、独立地域外挿。
- **取り下げる案**：「3応答が同じ場所・同じ年で強く連鎖する」と既知の時系列を連結して断定する案。「3種が食性と時期で気候に応答する」は既刊重複であり、それだけで主題にしない。
- **手を付けない**：凍結済みEcology Report、既存v0.5原稿主文・図・結果数値、2026-11-17 v0.6候補要旨、PR #215の独立ソース海氷検査。

### 参照原本
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12957737/
- https://www.sciencedirect.com/science/article/pii/S0960982226007414
- https://github.com/caseyyoungflesh/penguin_diet_from_space
- https://github.com/zuizui0223/mina/pull/214
