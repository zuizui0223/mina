# 南極海洋の「亜南極化」は一つの軸なのか：海氷・塩分・水温・ペンギン群集・植生の実測可能範囲

**2026-11-11 JST｜探索的な実行済み検証｜Draft PR #214｜main / frozen Paper 1/2 / PR #206 untouched**

## 結論：地域間には強い一軸。ただし時間変化は多軸で、群集・植生との統合同期は未識別

**物理海洋3変数の空間的共通軸は存在**した（元40マクロ地点のうち近傍海洋再解析格子まで25km以内にある34地点、6報告地域、2011～2020年の各年8～11月4か月平均、340 site×year）。標準化PCA PC1の説明率 **70.943%**、海氷濃度負荷量 **−0.64294**、GLORYS表層塩分 **−0.48903**、GLORYS表層ポテンシャル水温 **+0.58947**（温暖側を正に数値定義）。温暖・低SIC・相対的に低塩分の空間勾配を表す。

**しかしPC1総変動の85.914%は報告地域の平均値の違い**であり、14.086%が地域内の分散。固定された同一34サイトの2011～2020年の年変化からサイト固有の平均を差し引いてやり直した時間変動PCAはPC1説明率 **47.591%** で、変数負荷量は海氷−0.70142、塩分−0.14177、水温+0.69851。空間PCAと時間PCAのPC1方向コサイン+0.9320だが、**時間的な一軸支配は弱くなり、塩分寄与が相対的に小さい**。「18地域が温暖化・淡水化・緑化と同じ1本の時間軸へ変化した」という強い仮説は現在の源データから支持できない。

**地域数を等しく重みづけ**た6地域×2011～2020年のPCAでもPC1説明率 **72.356%**、元全site年の負荷量方向とのコサイン **0.99917**。地域×年の空間パターンは一部のサイト数超過で生まれた見かけの単純な数値ではない。一方、6元地域のうち**3地域はたった1原地点**で、独立したマクロ地域の再現性は限定される。

## 1. 出典と観測支持（18地域全部のPCAはNG）

| 要素 | 元ソース | 実際の支持 |
|---|---|---|
| ペンギンの地域×種×巣数 | original MAPPPD source, site×species×actual observed season fixed source method | **595地点/18元地域、2,456原観測レコード** |
| 海氷濃度 | EUMETSAT OSI SAF OSI-450a1 v3.1, original monthly source files SHA-verified; 1991～2020年8～11月 | **595地点×120実観測月=71,400 site-month** |
| 海洋塩分・水温・MLD | Copernicus Marine GLORYS12V1, ocean_monthly_2011_2021.csv, monthly Aug–Nov 2011–2021; 106 source ocean coordinates | **元macro40は40地点。海洋格子まで25km以内は34地点・6地域** |
| 3変数の共通月・年 | OSI SAF original marine 100km mean × source GLORYS surface salinity and thetao | **2011～2020年 340 site-year、34サイトで各10年×4か月完全** |
| 植生 | Plantarctica 2017～2023年static composite、original Vegetation polygon area in 2km buffer | 34マクロ共通地点で静的地図がある。**正検出25地点**、年変化は利用不可 |
| ペンギン真の2種同年計数 | Source original method fixed, both species observed at same site and same season | Adélie vs Gentoo **23地点年/7サイト/2地域/2空間ブロック**；Chinstrap vs Gentoo **16地点年/5サイト/2地域/2ブロック** |

海洋格子の最短距離が25 kmを超過した元6マクロ地点は**BRDM, BRDN, BRDS, CRZE, CRZW, ROYD**。これらを便宜上の海洋最寄り値で埋めなかった。特に前回PR #215の長期ブライト/ダーク候補 **Cape Crozier West (CRZW) と Cape Royds (ROYD)** はこの海洋3変数の34地点PCAには**入っていない**。したがって、前回の良否差をこのPCAが説明したとは絶対に言えない。

6実際の海洋比較可能地域：Victoria Land 20地点、Central-west Antarctic Peninsula 6地点、South Shetland Islands 5地点、Adelie Land 1地点、Mac. Robertson Land 1地点、South Orkney Islands 1地点。これが理由で、**「18地域×5変数（SIC/SSS/SST/land greening/ice-free land）PCA」と「18地域のジェンツー比率の将来予測」は NO-GO**。静的植生を各年に複製することも、未調査の種類をゼロ巣にしてジェンツーの割合を作ることも禁止。

## 2. 海洋3変数の共通軸がどこまで単一か

### 2011～2020年 34サイト×10年間 pooled PCA

| Axis | 元データ標準化後の説明率 |
|---|---:|
| PC1 | **70.943%** |
| PC2 | **22.882%** |
| PC3 | 6.175% |

PC1は水温+0.58947、SIC−0.64294、塩分−0.48903。PC2は水温+0.52773、SIC−0.15182、塩分**+0.83573**なので、**塩分を含めると少なくとも1つ以上の独立した海洋環境勾配が残る**。単一PCで環境変化の全てを表すことはできない。

元地点年の変数間Pearson相関：**SIC×塩分+0.5473**, **SIC×水温−0.7766**, **塩分×水温−0.3391**。これは元Sourceの地理・季節が揃った相関で、海氷生成・塩分移流・混合の因果方向ではない。特に「海氷が減るほど塩分も低い」という符号は今回の標本の地理的勾配に限定され、南極の物理的一般法則ではない（気候研究では2015年以降の塩分上昇と海氷縮退の共起も指摘）。

地理と時間の異質性：
- 全34地点年PCAの PC1 分散の**85.914%が元地域平均との差**、14.086%が元地域内。
- 同一site内の2011～2020時間偏差でPCAをやり直すとPC1 **47.591%**、PC2 33.053%、PC3 19.356%。塩分負荷量は−0.1418へ弱くなる。すなわち「地理の一軸」を「全地域の温暖化時間軸」へ単純に写せない。
- 元6地域を各10年の1値で等重みづけしたPCAはPC1 **72.356%**、負荷量方向は元PC1とコサイン0.99917で一致する。元6地域の10年気候平均6点だけをPCAするとPC1 82.175%だがn=6なので統計的に過度の信用はできない。固定34サイトを各1票10年平均PCAはPC1 80.109%。
- 1つの元地域全体をPCAから除くとPC1説明率は**0.6179～0.7782**、元PC1方向との絶対cosは**0.9125～1.000**。地理的方向はあまり変わらないが、地域の有効Nと空間自己相関は減らない。

## 3. 10年の時間変化は地域によって違う

固定した2011～2020年の元地点×年の海洋PC1から、各年の元source地域平均を作り、**全10実年のOLS傾き**を計算。年1つずつ除外したsource診断で符号の一貫性を確認。

| 原報告地域 | 10年通して観測された地点 | Marine PC1 OLS/10年 | 1年除外OLS範囲 | SIC pp/10年 | Salinity native/10年 | 水温°C/10年 |
|---|---:|---:|---:|---:|---:|---:|
| Central-west Antarctic Peninsula | 6 | **+1.438** | +0.661～+1.934 | −8.673 | −0.906 | +0.051 |
| South Shetland Islands | 5 | **+1.911** | +1.619～+2.184 | −18.706 | −0.370 | +0.321 |
| Victoria Land | 20 | **+0.031** | −0.183～+0.142 | −1.286 | −0.147 | −0.054 |
| Adelie Land | 1 | +1.112 | +0.840～+1.331 | −10.269 | −0.409 | +0.120 |
| Mac. Robertson Land | 1 | +0.110 | −0.068～+0.225 | +3.710 | −0.178 | −0.003 |
| South Orkney Islands | 1 | +1.423 | +1.078～+1.805 | −14.082 | −0.623 | +0.110 |

元の3地域は1地点なので、その正負を独立した地域の温暖化証拠として扱わない。生物学的問いとの比較では地点6/5/20の3地域が主な地理的支え。半島・サウスシェトランドでは source-PC1は2011～2020年の10年間に正方向で、**年1つ除外しても正**。Victoria Landはほぼ横ばいで、年除外により正負を跨ぐ。海洋の地域的再編成は**南極全域の同一単調な温暖化傾向ではない**。

なおSICを減らす気候の機構、淡水化を起こす輸送・氷河融解や混合の寄与は分離できない。GLORYSは再解析であり真の現場SSS/海洋温度の独立検証とは異なる。

## 4. 静的植生との対応：地理的な共変動に限る

34元サイトのうち2km範囲内のPlantarcticaのVegetationポリゴン正検出は25地点（5地域）。正検出サイトのみのmapped areaと2011～2020年marine PC1地点平均のSpearman順位相関 **ρ=+0.73591**。元地域の平均を両指標から除いた**23正検出サイト/3元地域**の標準Pearson相関（log1p(mapped area) vs marine PC1）は **r=+0.33012**。

この正の横断的共変動は面白い探索対象だが、元地域の違いが主な交絡要因になりうる。Vegetationは**2017～2023年の1枚のcomposite** であり、1986→2021年の緑化速度や年間の植物増減には変換できない。0 positive polygonsの区画を植物実不在にはしていない。

外部先行文献でRoland et al. 2024, Nat. Geosci. DOI 10.1038/s41561-024-01564-5 は1986 0.863 km²→2021 11.947 km²と報告したが、Bokhorstら2026のMatters Arising (https://www.nature.com/articles/s41561-026-02076-0) とRolandら2026のReply (https://www.nature.com/articles/s41561-026-02080-4) が**衛星可観測域・速度・植生の成長可能性を巡り議論**している。元論文の増加量を反証不能の事実や本研究の時系列元データとすることはできない。

## 5. 種構成は本当に marine PC1 と連動するか？

元MAPPPDのsite×species×season固定方法において、**本当に同じ地点×年に両種の実巣数がある**ものだけで log1p(ジェンツー巣数)−log1p(他のペンギン巣数)を作った。未観測の種が0巣として計数されたわけではない。混在源の同年記録には調査日・出典・努力の完全一致を強制していないので「同時期の観測」と限定する。

| 真のペア | サイト年 | 原地点/地域/250kmブロック | raw Pearson r (marine PC1 vs log巣数比) | within-site Pearson r | 1元サイト除外のwithin-r範囲 |
|---|---:|---|---:|---:|---|
| **ADPE/GEPE** | **23** | **7 / 2 / 2** | **−0.508** | **+0.523** | **+0.448～+0.608** |
| CHPE/GEPE | 16 | 5 / 2 / 2 | +0.107 | +0.193 | +0.084～+0.364 |

Adélie/Gentooでは、**元地点間の違いを混ぜたrawの符号と同じ地点内の年変動の符号が逆**。これは地理的構成の変化とsite-level応答を区別する必要がある探索的な発見だが、within-rの独立同所比較は**わずか2つの250km空間ブロック**。23は独立生態サイト23ではなく、同じ7サイトの観測繰返しである。地点1つ除外は正方向を保ったが**独立地域反復にはならない**。真の「ジェンツーに入れ替わる」地域年の割合、定着や消失、将来分布を推定していない。

2011～2020年のsource GLORYSに関して25km以内の地理QAから外れた**CRZW/ROYD**は、前回PR #215で見つけたRoss Islandの局地的ブライト/ダーク2候補である。**このPCAでその2つの環境応答差を説明したと主張するのは誤り**。

## 最終判定と一本の論文への位置づけ

| 問い | 現時点の答え | 根拠 |
|---|---|---|
| 海氷・塩分・水温に共通した空間軸があるか？ | **YES, descriptive** | PC1 70.9%、地域等重み72.4%、site平均80.1% |
| その共通軸が**時間変化そのもの**を一軸支配するか？ | **PARTIAL / not universal** | site内PC1 47.6%、塩分負荷量低下、Victoria Land時間傾向ほぼ0 |
| 半島とサウスシェトランドで実際の10年marine PC1に時間的な変化があるか？ | **YES in source-matched subset** | 地点6/5、2011–2020 OLS+1.44/+1.91; 年除外でも正 |
| 海洋軸と陸植生が同じ年々の速度で進むか？ | **NO_GO** | 静的2017–2023 compositeだけ、2011–2020との時間同期データなし |
| 18地域の3種の群集が指数とともにジェンツーへ転換したか？ | **NO_GO** | 正当な同所同年2種計数は23/16サイト年、2ブロックだけ |
| 2050/2100 CMIP6でこの**5変数**指数を将来推定できるか？ | **NO_GO** | 本時点で18地域のGLORYS＆植生の同期・未来生物較正なし |

**より一般化しやすい問い**：Antarctic marine environmental covariance is spatially coherent, but its temporal expression and biological assemblage responses may be geographically non-transferable. 「亜南極化／subantarcticization」は検証対象の**作業仮説の名称**であり、新たな自然現象として定義済み、または世界初の概念として立証されたわけではない。

結論はあくまで海洋再解析と衛星元海氷の探索的・同年整合性のある測定結果。生物学的な重要性は**全時系列の地域年群集比較と独立した陸植物時系列が増えてから**独立検証する。どの変数が因果的にペンギンを増減させるかを別の多重探索に置き換えない。

## 実行・成果物・出典
- [Original source-pinned combined marine/Penguin computation SUCCESS #42955337180](https://github.com/zuizui0223/mina/actions/runs/42955337180), artifact **13826841593**. Includes exact 2011–2020 340 source site×year climate values/PC1, 60 region×year climate summaries and raw variable means, source QA, mapped plant positive-only site table, real penguin same-year co-census source support, full machine-readable PCA.
- Source contract: JOINT_MARINE_REGIME_AXIS_FEASIBILITY_CONTRACT_20261111.md; code: test_joint_marine_regime_axis.py, source-free 5 arithmetic tests: unit_test_joint_marine_regime_axis.py; workflow: .github/workflows/penguin-original-joint-marine-regime-axis-feasibility.yml.
- EUMETSAT OSI SAF OSI-450a1 v3.1 original monthly: DOI 10.15770/EUM_SAF_OSI_0023 (source frozen 120 monthly receipts and QA verified in #42612067836).
- Copernicus Marine GLORYS12V1 202311 ocean reanalysis: https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description, 2011–2021 Aug-Nov 106 source mapped locations (40 macro40).
- Plantarctica static mapped vegetation 2017–2023 original positive polygons.
- Southern Ocean observed post-2015 upper-ocean salinification and reduced ice: https://pmc.ncbi.nlm.nih.gov/articles/PMC12260588/ ; mechanisms are complex and no universal freshwater sign is assumed.
- Roland et al. 2024 greening DOI 10.1038/s41561-024-01564-5; 2026 methodological dispute/reply DOI 10.1038/s41561-026-02076-0 and 10.1038/s41561-026-02080-4.
- Known spatially heterogeneous peninsula penguins: Lynch et al. 2012, PNAS regional analysis (https://www.bas.ac.uk/data/our-data/publication/spatially-integrated-assessment-reveals-widespread-changes-in-penguin-populations-on-the-antarctic-peninsula/). Another spatial climate/temporal structure differentiation is not by itself first discovery.
