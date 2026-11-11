# 海氷が似ていてもペンギン繁殖巣数が違う？ 南極147近隣コロニー組の元海氷画素を分離した実測結果

**2026-11-11 JST｜探索的なsource-level measurement diagnostic｜mina Draft PR #215。解析完了。**

## 中心結論

**同じ元海氷画素を共有する100km近岸海氷平均で比べると、南極の近隣繁殖コロニー間の海洋環境差が縮小して見える。** 南極の真正MAPPPD巣数100長期site×species系列から事前に抽出した同種・同元地域・同じ固定250kmブロックの**147組の全数**について、元OSI SAF 25km衛星海氷格子を独自に再読出しし、2地点で共有する海域画素を除いて比べた。

- **元衛星NetCDF 120ファイルを出版社サーバーから再取得。全120 SHA256が従来の公式原本receiptと一致。海氷格子の緯度経度fingerprint一致。**
- 対象147組を構成する**64固有source地点×120月＝7,680地点月**の100km元海域平均を、固定海洋画素IDから独立再計算して完全一致。元147組のサイト間SIC差の平均絶対値とSIC傾き差も全件元結果と一致。元観測時点を作り直さず、元の真の共有巣数計数年だけ使用。
- 両地点の重なった海洋画素を除外したあと、左右それぞれに独自の源25km海洋画素が**3個以上**残り、元同年巣数年の5年・10年間以上で源海氷QAに合格した組は**93/147**。
- **54/147組**は固定した独自海洋画素が3個未満：missing, not zero. 事前の全147組は元100kmバッファの海域画素を一部でも共有し、うち9組は両方の100km元画素集合が完全一致。画素集合の元Jaccard重複度中央値は0.677。
- 有効93組では全93組の独自画素海氷濃度の年平均絶対差が、同じ巣数計数年で計算した従来の100km近岸SIC平均の差より大きかった。**元100km差3.491 percentage points 対、独自画素差7.834 pp（いずれもペアごとの中央値）**。ペアごとの倍率を取ったときの中央値は**3.032倍**。これらの異なる中央値の単純比を倍率と報告しない。

**これは「原因が海氷だ」という証拠ではない。** 本研究が直接示すのはSICという**環境測定の空間サポートが近隣地点に共通しており、地点間の差を平滑化する**こと。元海氷データの25kmは格子間隔で、実効的な衛星観測の分解能はさらに粗くなりうる。独自海洋画素が互いに素であっても、衛星footprint・海の連続性・再格子化等による空間依存が残る。海へのアクセス、餌生物、氷山・ポリニヤの位置、着岸可能性、個体の採餌距離を測っていない。

## データソースと再現の真正性

- 南極3種（Adélie ADPE / chinstrap CHPE / gentoo GEPE）の元の595地点／2,456 fixed-method巣数レコードから、1991–2020の100長期site×speciesを得て、同じregion×species及び固定250kmブロックで実際に同年に計数された147組（>=5同年計数年、10年span）を選択した先行の成功 run #42919893846 と、元の147組画素重複 run #42923119624 を**そのまま固定使用**。
- EUMETSAT OSI SAF OSI-450-a1 v3.1, 2025年補正版, original monthly 25km Southern EASE2, 1991–2020年8〜11月（1991–2020年30年 × 4月 =120元ファイル）、原本 DOI 10.15770/EUM_SAF_OSI_0023。元publisher SHA / native ocean mask (基準1993年9月) / pixel IDs / native geolocation fingerprint / original site QA を別ソースrun #42612067836から取り出して独立検算した。
- 元海洋画素A, Bについて重複C=A∩B、個別海域 L=A\B と R=B\A。左右L/Rとも固定画素≥3、各月≥3有効海域画素かつ有効画素割合≥80%、各元観測巣数年の8–11月全4か月valid、元の共通巣数計数年で≥5年・span≥10年間が必要。両側の差は同年の月4等重み SIC平均の絶対差を元巣数観測年で平均した。
- source raw outputs: **[official full-grid 120-file SHA-verified recomputation run #42951867959](https://github.com/zuizui0223/mina/actions/runs/42951867959)**, artifact **13825970398**。147組全数CSV、実際の共通巣数年ごとの独自海氷平均CSV、元120 files SHA receipt JSON、元region×species×250km summary JSON/CSV。SOURCE ORIGINAL QA/全147組の再現が完了した。

## 独自海洋画素数に関する感度：選択された小画素の例に依存していないか

≥3画素は元の源海洋SIC支持に沿った基本条件。後からsource QAとして ≥5/8/12画素へ引き上げた感度は**事後感度診断であり、最適化された生態学的閾値ではない**。

| 左右の源独自海洋画素の下限 | 有効源ペア組数 | 独自画素差が従来の100km平均差より大きい組数 | 元100km差の中央値 pp | 独自海洋画素差の中央値 pp | 元ペア倍率の中央値 | 元種×地域×250km層 |
|---|---:|---:|---:|---:|---:|---:|
| ≥3 | **93** | **93** | **3.491** | **7.834** | **3.032** | 10 |
| ≥5 | 73 | 73 | 3.615 | 7.834 | 2.733 | 9 |
| ≥8 | 56 | 56 | 3.905 | 7.031 | 2.273 | 8 |
| ≥12 | 34 | 34 | 4.214 | 6.670 | 1.570 | 7 |

元3種×原地域×250kmブロックという固定区分でも、有効データがある全10層の中央値で独自画素差のほうが大きかった。ただし**93ペアも10層も独立な気候や個体群の実験ではない**。全組が元コロニーIDや海氷区域を共有する。単純二項検定で93/93が有意などとは宣言しない。

厳格な元巣数比較の補助条件「左右で同じ元計数法・元計数0を含まない・同一巣数計数年が15年以上」では**11組（元種×地域×250km層は2）**が残り、11/11で独自画素差のほうが大きい（ペア倍率中央値2.973）。地理的広がりは限定され、robust biological climate effectという意味ではない。

## 既に選択されていた3つの局地例を全件開示

| 元から注目していた2サイト・種 | 本当の同年巣数観測年数 | 互いに独自の海洋画素L/R | 従来100km平均 SIC 絶対差 pp | 共通画素を除いた元海洋SIC 絶対差 pp | 同ペアの倍率 | ≥8画素感度 |
|---|---:|---|---:|---:|---:|---|
| **Cape Crozier West – Cape Royds** (Adélie) | **25** | **11 / 9** | 2.247 | **4.673** | **2.080** | **PASS** |
| Biscoe Point – Port Lockroy (gentoo) | 11 | 6 / 3 | 5.054 | **37.816** | 7.483 | **FAIL** |
| Barton Peninsula – Demay Point (chinstrap) | 10 | 4 / 4 | 0.636 | **7.796** | 12.250 | **FAIL** |

- Cape Crozier West–Cape Royds：元実計数年1991–2019の25年、元巣数log1p傾き差+0.497622/10年、両側元 aerial 固定計数法・元系列に真の0なし。独自画素でのSIC傾き差は**+3.918 pp/decade**、従来の重なった元100km平均値では**+1.755 pp/decade**。単なる同年差だけでなく、海氷の時間変化のコントラストまで大きくなる。ただし氷山障害・採餌海域は直接測っていない。Roydsの氷山/B15A-C16応答は既知の文献（Lyver et al. 2014, Ainley et al. 2024）からの外部機構候補であり、本解析の新規発見ではない。
- Biscoe–Lockroy：13.49kmしか離れていないが、右側の海域の**独自画素は3個だけ**で、源100km平均差5.05ppを除くと独自画素差37.82pp。右側3個の観測場所が特定の開水面・外洋・湾などに偏っている可能性があり、これを生物にとっての実際の採餌海氷差とみなしてはならない。>=5/8 source grid cells感度では無効。
- Barton–Demay：18.62km、元100km海氷差0.64ppは、独自4/4画素では7.80pp。ただし>=5/8源画素の感度では無効であり、生物学的原因の特定には使わない。
- 三例の結果を見てから閾値を変更して有意差を探していない。元の前回自然実験ベンチマークを、成功・小画素数による失敗ともにそのまま提示した。

## なぜ元のマクロ解析が「海氷から繁殖を予測できない」で止まったのか：一つの検証可能な説明

同じ元海氷100km平均は近隣で広く共通するため、**元source SICの空間的分散・コントラストが記録の平均化で減少する**。その反面、巣数カウントは既存の別々の繁殖コロニー単位で観測され、対照が消えない。こうすると、海氷の説明力が弱く見える一因として**空間サポートの不整合 / spatial support mismatch** が考えられる。

ただし**「説明力が失われた原因がこれだ」との検証は未完了**である。今回は SIC予測モデルを再fitしていないし、非重複画素のSICが実際の利用ニッチを測っている保証もない。元海氷観測そのものの識別性と地理的QAを数値化したにとどまる。

**今後の新しい生態学的仮説**：コロニー間の差は、同じ広域海氷レジームでも、個別にアクセスできる海の範囲（ポリニヤ・氷山遮断・採餌距離）というチャネルに沿って増幅される可能性がある。これは現在の実測では検証していない仮説であり、真の採餌動線、局所氷山時系列または独立のバソメトリー等のデータが必要。

## 論文への位置づけ・境界

主結果：**Observed penguin colony responses exhibit local heterogeneity obscured by shared-footprint sea-ice averages.**

- YES: 595-source site satellite QA、全147実ペアと元計数法、同年・source 25km cell extent、93 source-supported exclusive differences, 全10地理層と画素数感度における測定スケール効果。
- NO: independent colony-level climatic causal effect, penguin biological niche tracking, 10-y warming debt, sea-ice iceberg-access effect, source data-unsupported environmental zero, population recovery or real distribution edge changes.
- Original latitude/longitude original site points, known source 100 spot map and 147 local pair vector layers remain GIS artifacts from successful [#42923759660](https://github.com/zuizui0223/mina/actions/runs/42923759660). This result adds marine exposure metrics, not inferred bird movement.
- Do **not** create a new independent manuscript. Keep the strong original 2-site Cape Crozier West vs Cape Royds comparison as a mechanistically well-contextualized known literature benchmark; the macro finding is the **systematic source spatial-scale problem** across regions and species, not rediscovery of iceberg response.
- No source files on main or frozen Paper1/Paper2 were modified. This remains exploratory branch PR #215.

## Exact reproducibility and official attribution

- Recompute source: extract_exclusive_ocean_original_SIC_120months.py, six source-free math/missingness unit tests, workflow penguin-original-147-exclusive-ocean-ice-v1.yml, [source success #42951867959](https://github.com/zuizui0223/mina/actions/runs/42951867959), artifact **13825970398**.
- Read-only post-result exclusive ocean depth: summarize_exclusive_ocean_source_sensitivity.py, tests unit_test_exclusive_ocean_source_sensitivity.py, [SUCCESS #42952441121](https://github.com/zuizui0223/mina/actions/runs/42952441121) (artifact in run).
- Official original SIC product: EUMETSAT OSI SAF, Global sea ice concentration climate data record 1978–2020 (v3.1, 2025), DOI **10.15770/EUM_SAF_OSI_0023**, CC BY 4.0, https://osi-saf.eumetsat.int/products/osi-450-a1.
- Limitations of 25km passive microwave grid: UCAR Climate Data Guide https://climatedataguide.ucar.edu/climate-data/sea-ice-concentration-data-reprocessed-ssmr-ssmi-eumetsat (true effective resolution coarser, interpolation/status filter).
- Biological first-stage source: original MAPPPD breeding site×species×season fixed-method counts, initial original source 100 trend and 595-site metadata, this PR #215 scripts/documents.
