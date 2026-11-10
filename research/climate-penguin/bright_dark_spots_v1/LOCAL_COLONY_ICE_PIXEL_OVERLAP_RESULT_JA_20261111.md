# 南極ペンギンのブライト・ダークコロニー：近隣147組における真の同年計数と海氷画素の共有

**2026-11-11 JST｜探索的実測結果｜PR #215専用｜source SHA-verified original MAPPPD × OSI SAF**

## 最重要の結果

*海氷濃度が似ているのに、なぜ近隣の繁殖地の実測巣数は大きく違うのか*、を実計数年と衛星格子の観測支持で確かめた。元100地点×種の長期カウントから、同種×元地域×極250kmブロック内にある2地点の元観測年が5年以上共通、10年間以上にわたる**147組**の比較が成立し、すべての組で同年の8–11月近岸SIC 100km平均が元の衛星記録で検証可能だった。

**ただし重要な測定上の発見：この147組のすべてが、元の25km海氷画素を共有していた。** うち9組は100kmバッファに採用された元海洋画素集合が完全一致。2地点の元海氷画素集合のJaccard重複度中央値は**0.677419**。したがって「SICが近い＝真の独立な採餌環境が同じ」という解釈は誤り。元データは共通する海域を平均した観測変数であり、海氷/氷山アクセスの局所違いを見逃す。

**独立な大規模気候応答則は未確定**。同じ調査年での巣数変化の異質性は複数の生態地域で見えるが、ペアは同じサイトを複数回使用し同じ海域画素を共有するため、147の独立反復ではない。有効なのは3種×地域×250kmの**10の源ブロック組（うち多くが同一ロス島や半島地区）**。

## 出典

- 独立元台帳：MAPPPD固定法1991–2020年の同種site×season真正巣数。総地理母集団595サイト、固定法原観測2,456件、1991–2020年の長期推定可能系列100 site×species。
- 真の同年同期：以前成功した#42919208344、25厳格候補→9同期支持候補→2外部250kmブロック支持候補、全100系列出力。
- 同じ250kmブロックの147ペア＋元各同年SIC：#42919893846（SUCCESS）、全数pair CSV。
- 元の衛星格子：OSI SAF 25km EASE2月次v3.1から構築した595地点の元1993年9月**有効海域25km画素ID**（#42612067836）。画素の集合交差と和集合からJaccardを計算。陸上画素・元の無効セル・架空海氷0を入れていない。
- **今回の全数実測・5件の純算術テスト成功**：https://github.com/zuizui0223/mina/actions/runs/42923119624 。全147組とグループ別結果のアーティファクト（GitHub Actionsからダウンロード可能）。
- 元データを再ダウンロードせず、前回成功した固定ファイルを直接再利用。海氷閾値/年遅れ/有意p値の試行なし。

## Cape Crozier West と Cape Royds：データベースが再発見した既知の自然実験

| 元観測条件 | Cape Crozier West (CRZW) | Cape Royds (ROYD) |
|---|---|---|
| 元地域／固定250km極ブロック | Victoria Land / 1:-6 | 同じ |
| 実座標 | −77.4536, +169.2377 | −77.5545, +166.1639 |
| 地点間距離 | 74.7909 km | 両地点間の直線的な球面距離 |
| 計数法 | aerial | aerial |
| 実際に同年に計数した年 | 1991–2019中の25年 | 同じ |
| 同年計数log(1+nests)傾き／10年 | **+0.445932** | **−0.051690** |
| 同年の近岸海氷8–11月SIC平均（%） | **81.0717** | **82.8067** |
| 同年近岸SIC傾き（pp/10年） | +0.8966 | −0.8583 |

同年の近岸SIC絶対差の年平均は **2.247 pp**。両地点の固定元海氷画素はCrozier 23ピクセル、Royds 21ピクセル、共通12ピクセル、和集合32ピクセル、**Jaccard=12/32=0.375**。小さい元SIC差の少なくとも一部は100km平均の共通画素に由来しうるが、両者のバッファが完全一致しているわけではない（小さい方の元画素の57.14%が共有）。**局所環境や採餌条件が同じだという証明にはならない。**

全147組内で観測巣数の同年log変化傾き差の絶対値は**46番目に大きい**。同種Adélieの全67組なら**10/67位**。元の100km以内＋同計数法＋共通観測15年以上＋原長期計数に0を含まない21組では**2/21位**（探索後の記述順位であり検定pではない）。海氷の近さはその厳格21組では14/21位であり、**最も同じ海氷の組ではない**。

このロス島2地点の対照は生態学上の「初発見」ではない。既にLyver et al. 2014 PLoS ONE (doi:10.1371/journal.pone.0091188) とAinley et al. 2024 Antarctic Science (https://www.cambridge.org/core/journals/antarctic-science/article/varying-population-size-of-the-cape-royds-adelie-penguin-colony-19552020-a-synthesis/BD030317CBC63A9054E064CBEE49450D) は、Roydsの2001–2005年のB15A/C16巨大氷山に伴うMcMurdo Sound polynya消失／海洋アクセス制限、Crozierなど他地点との差、および繁殖・海況・捕食圧の文脈を示している。本研究の147組自前元データ再解析は**その既知機構の候補対照を自動的に抽出できた**という方法学上のチェックポイントである。元バッファSICは氷山の障壁と海へのアクセスを計測していないため、ここで因果メカニズムを再証明したとは言わない。

## ロス島以外にも実測で現れた候補（強度と難点を併記）

| 組 | 元地域と種 | 地点間距離 km | 同年計数年数 | 観測巣数の同年log傾き差（絶対値/10年） | 元SIC同年平均絶対差 pp | 元画素重複度Jaccard | 判定 |
|---|---|---:|---:|---:|---:|---:|---|
| **Biscoe Point – Port Lockroy** | 西南極半島・Gentoo | 13.49 | 11 | **3.829** | 5.054 | 0.757 | 元法一致・0巣なし、ただしBiscoeの全観測span18年なので元厳格20年条件未達 |
| **Barton Peninsula – Demay Point** | サウスシェトランド・Chinstrap | 18.62 | 10 | **1.151** | 0.636 | **0.849** | 元法一致・0巣なし、原SICの画素が強く共有 |
| **Coulman Middle – Cape Jones** | Victoria Land・Adélie | 27.57 | 5 | 0.883 | 0.573 | 0.769 | 5共通観測年の下限、年変化の推定はまだ薄い |

ここでは元の同時期観測年を両地点にそろえたことは改善だが、さらに厳格な複数空間ブロックの独立確認はしていない。Biscoe/Port Lockroyのように局所対照が大きい例も、最初の源ブライト・ダーク判定が独立に十分だったとは限らない。複数種間の傾き差を1つの同じ生物学的単位として比較することもしていない。

## 分野上の解釈・優先順位

1. **YES: source-backed same-year differences** — 少なくとも元の調査年・計数法を揃えられる近隣コロニーで、相対的な巣数の変化は一様ではない。ロス島はそれを代表する長年支持された例。
2. **YES: climate-scale measurement mismatch** — 同じ近岸100km平均というSICの観測変数自体が近隣で強く共有され、局地的な氷山/ポリニヤへのアクセス、採餌到達距離や小スケールの気候ニッチを区別できない。147組全数に元画素共有がある。
3. **NO: causal ice mismatch/refugia** — 元SICとの差が小さいことを根拠に「海氷では説明できない適応の避難所」と宣言しない。すでにロス島の例にはより具体的な氷山／ポリニヤ・捕食圧の先行研究があり、源のSIC平均はその機構を測っていない。
4. **Do not multiply papers/tests** — 本探索は単一の南極マクロ論文の「地理的・観測解像度に応じて見える異質性」の一つの図候補。次に元サイト画素と異なる独立な**海へのアクセスの遮断・海底地形・局所ポリニヤ**データが得られた場合だけ、候補に優先順位を付けて機構仮説を外部検証する。

## 5. 地図で結果と観測支持を探索する（GIS）

元のWGS84地理座標を持つ **2つの独立GeoJSON FeatureCollection** を元観測sourceだけから生成し、GISで開けるようにした。

- **penguin_original_bright_dark_100_species_site_points.geojson:** 全100地点×種。5年以上・10年spanの元系列は全部保持し、地域内比較不能10点を絶対に0/普通の繁殖地と誤ラベルしない。元のspecies×region peerが使える6群、真の同年観測support、元Theil–Sen/endpoint sensitivity、外部250kmブロックから支持されるCape Crozier West（正）とCape Royds（負）の2点の判定、真正0観測履歴を属性として保持。
- **penguin_original_147_same_year_nearby_colony_pair_contrasts.geojson:** 前回実測147組の元同年巣数差・100km SIC差・元25km海域画素Jaccard、距離・ブロック・計数法を保持。線は2つの元サイト座標を幾何的につないだだけであり、**GPS移動・同じ個体の行動圏・実際の海洋輸送路を描いたものではない**。
- 地理的に十分比較可能なグループ（元種×地域）が6つに限られることと、25の初期頑健source候補から9の同年観測支持、さらに2の外部空間ブロックを満たす候補へ縮むことがレイヤー上でも確認可能。
- 生成CI [Actions #42923759660](https://github.com/zuizui0223/mina/actions/runs/42923759660) **SUCCESS**、地図アーティファクト **13812977461**（GeoJSON 100ポイント、147比較ライン、原source legend JSON）、source-independent 4単体テスト。
- 生成には元atlas / #42916058266 / #42919208344 / #42923119624 の固定入力をそのまま使用。表示されない地域は「ペンギンがいない」という意味ではなく、源1991–2020長期カウントの条件を満たしたデータがない地域。

**論文候補の図にするなら**、(A) 全100真正サイトの地理的サポート階級、(B) 明暗2候補と比較地理、(C) 元100km海氷画素共有を同じ地図の分図にする。候補の点の色は相対変化の支持ラベルであり、絶滅リスクや適地確率ではない。

## 再現コード

- Source overlap all-pair code: audit_pair_nesting_ice_buffer_overlap.py
- Pure test: unit_test_pair_nesting_ice_buffer_overlap.py (five original-pixel geometry / ranking checks)
- Execution: .github/workflows/penguin-original-nearshore-source-pixel-overlap.yml
- Physical output artifact name: penguin-original-147-local-pairs-source-25km-ice-pixel-sharing-v1
- Full original pair input: #42919893846, count common-year check #42919208344, native source ocean-pixel map #42612067836.
- Map code: build_spot_and_neighbor_map_geojson.py, original GIS source tests: unit_test_spot_and_neighbor_geojson.py, workflow: .github/workflows/penguin-bright-dark-source-map-gis.yml.
- External published benchmark: Lyver et al. 2014 (10.1371/journal.pone.0091188), Ainley et al. 2024 Antarctic Science (Cambridge), not a new mechanistic discovery.
- Draft PR #215 is independent of climate-front PR #214; do not merge main or frozen Paper 1/Paper 2.
