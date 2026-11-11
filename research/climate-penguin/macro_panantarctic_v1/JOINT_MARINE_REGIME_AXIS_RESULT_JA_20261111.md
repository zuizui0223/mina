# 南極全18地域で「亜南極化」は一軸なのか：海氷・塩分・水温・植物地図・ペンギン巣数の実測検証

**2026-11-11 更新｜今回の実測済み18地域×1993–2020年の結果が主結論。旧34地点の報告は本ファイル下部に参考として保存。Draft PR #214、凍結Paper 1/2 とmainは無変更。**

## 主結論

> **南極沿岸の海氷と水温には共通する温暖・低海氷の空間的勾配がある。しかし、塩分は大きな独立軸を持ち、地域別の時間変化とペンギン種間の巣数比までが一斉にその軸へ沿って変化するとは確認できない。**

これまでの34地点×6地域のmarine PCAを、元MAPPPDの595繁殖地に対して本来のCopernicusモデル格子から拡張。2011年9月の固定有効海洋格子まで25 km以内の**588地点×18地域×28年×8～11月4か月＝65,856地点月**のGLORYS表層塩分・ポテンシャル水温を実取得。378固有元海洋格子に由来する。元OSI SAF 1991–2020年の71,400地点月SICと照合し、**588地点×1993–2020年の16,464サイト年の3海洋変数が完全に揃った**。以前の34地点の2011–2020 GLORYS1,360地点月は最大元source誤差約7.1e−15（塩分）と4.4e−16（水温）。旧34地点PCAのPC1分散説明率0.7094310203120341を差1.1e−16で再現した。

## 1. 18地域に等しい重みを与えた海洋環境PCA

地域数の違いによる偏りを弱めるため、各地域×年（18×28＝**504地域年**）の海氷濃度・表層塩分・海水温を標準化したPCAを主仕様とした。PC1の表示符号は水温負荷量が正になるよう固定。

| 源海洋物理のPCA | PC1 | PC2 | PC3 |
|---|---:|---:|---:|
| 説明率 | **65.138%** | **31.516%** | 3.346% |
| SIC負荷量 | −0.6882 | −0.1604 | — |
| 海水温負荷量 | +0.6873 | +0.1685 | — |
| 塩分負荷量 | **−0.2325** | **+0.9726** | — |

SIC×水温 r=**−0.8996**、SIC×塩分 r=+0.1648、塩分×水温 r=−0.1578。PC1はほぼ**温暖・低海氷軸**、PC2はほぼ**塩分軸**。旧34地点では塩分がPC1に−0.489で入っていたが、実際の18地域では相対的に独立した環境次元だった。

**重み・地理の感度**：588サイト年を全部同じ重みにするとPC1 60.365%、塩分負荷量−0.0383。378固有海洋格子×年を一票としてもPC1 60.469%、塩分負荷量−0.0545。18地域を1つずつ除いたPC1負荷量のcosは0.9974～1.000、PC1説明率64.36～66.72%。主な温暖・低海氷の空間的勾配は安定だが、3物理量すべてを一軸で扱う妥当性は示されない。

## 2. 地理勾配と同一地点の時間変化を混同できない

18地域等重みPCAを588×28サイト年に投影したPC1の変動の**71.113%は元地域平均間の違い**、28.887%は地域内。**同一サイトの28年間の変化だけ**で3元物理量から各サイト平均を引いてPCAすると：

| PC1負荷量・説明率 | 地域×年等重み | 同地点内の時間偏差 |
|---|---:|---:|
| PC1説明率 | 65.138% | **55.252%** |
| SIC | −0.6882 | −0.6664 |
| 海水温 | +0.6873 | +0.6654 |
| 塩分 | **−0.2325** | **+0.3363** |

2つのPC1負荷量コサインは+0.838。海氷が少なく暖かい**場所**の塩分と、ある**地点の変化**に伴う塩分の向きは一致しない。海氷形成・融解の物理は別にして、海流・混合・氷河融水や2015年以降の表層塩分増加などを固定の一方向へ単純化しない。

## 3. 1993～2020年の18地域の変化：一律の速度ではない

28実年の地域平均Marine PC1傾きは**18地域中15地域で正、3地域で負**。ただし1実年除外で符号が残るのは**正12、負2、未安定4**。Adelie LandとEllsworth Landは各1元サイトであり、18の独立な海洋生態系反復という意味ではない。

| 地域 | 元サイト | PC1 OLS /10年 | 1年除外後の符号 | 海氷 SIC pp/10年 |
|---|---:|---:|---|---:|
| Northeast Antarctic Peninsula | 39 | **+0.257** | 全て正 | −2.052 |
| Northwest Antarctic Peninsula | 16 | **+0.178** | 全て正 | −2.583 |
| Central-west Antarctic Peninsula | 106 | **+0.173** | 全て正 | −2.007 |
| Southwest Antarctic Peninsula | 30 | +0.090 | 全て正 | −0.090 |
| Elephant Island | 51 | **−0.067** | 全て負 | +0.663 |
| South Shetland Islands | 118 | **−0.012** | 未安定 | −0.381 |
| Victoria Land | 43 | +0.015 | 全て正だが小さい | +0.343 |
| South Orkney Islands | 88 | +0.041 | 未安定 | +1.400 |

**期間の違いも重要**。South Shetland IslandsのMarine PC1期間平均は**1993–2000年+2.375 → 2001–2010年+2.832 → 2011–2020年+2.292**。28年の単調な一方向移行ではない。旧34地点の2011–2020年ではPC1正傾きが見えたが、期間・地点・物理PCA較正が同時に異なるため、どれか一つだけが差の原因だと断定しない。全18地域の原年別sourceは成功したCIの18region trend CSVに保存。

## 4. 陸の被覆は年次緑化を観測したものではない

2017～2023年の**1枚のPlantarctica静的マップ**にある、植生・地衣類・雪藻などの統合した2km陸域被覆面積を、1地点に1回だけ結合。元222マップ地点のうち海洋588コホートに重なるのは216地点、正検出は**167地点・8地域**。正検出された陸の被覆面積と28年平均Marine PC1のSpearman rhoは**+0.227**、地域平均を除いたlog1p(面積)×PC1のPearson rは**−0.091**。これは地理的な弱い関連で、年次の緑化速度や「海氷→植物→ペンギン」の時間連鎖を示さない。

**指標の違い**：以前の34地点でrho+0.736だったのはVegetationクラスだけの面積。今回はVegetation/地衣類/雪藻等を統合した元マップ面積なので、2つの相関差を「サンプル数を増やしただけ」と読んではいけない。地図の非検出は植物不在ではない。

## 5. 本当の同一地点・同一年の2種巣数比と海洋軸

元MAPPPDの固定method巣数2,456件のうち、実際に**同じsite×seasonで両種が記録された**場合のみlog1p(種B巣数)−log1p(種A巣数)を計算。未観測の種は0巣に変えない。観測された同一年でも調査日・出典・努力の完全一致を別に検証したものではない。

| 2種 | 同所同年元計数 | 原サイト/地域/250kmブロック | PC1とのraw r | 同サイト平均を除くr |
|---|---:|---|---:|---:|
| ADPE / GEPE | **98** | **25 / 6 / 5** | −0.101 | **−0.008** |
| CHPE / GEPE | 165 | 33 / 6 / 7 | −0.024 | +0.078 |
| ADPE / CHPE | 88 | 24 / 6 / 8 | −0.142 | −0.054 |

海洋環境は18地域を覆うが、**本当に2種同年カウントのある地域はなお6地域**。98等は独立98地域ではなく、25サイトでの実観測の反復。「種入れ替わりとMarine PC1の強い正相関」は全28年では確認されない。

### 旧34サイトで見えたADPE/GEPE正相関の原因を分解

前回の物理PCAを**凍結したまま**地理コホートと観測期間を変える実測表を再計算した。旧source34でのADPE/GEPE地点内r+0.52318586、今回の全source18でのr−0.00836584を全て再現した。

| 実2種同所同年観測 | 元比較行 | 旧34サイトPCAを固定したwithin-site r | 新18地域PCAを固定したwithin-site r |
|---|---:|---:|---:|
| 旧34サイト、2011～2020 | **23** | **+0.523** | +0.393 |
| 全588サイト、同2011～2020 | 37 | **+0.523** | +0.393 |
| 全588サイト、**1993～2020** | 98 | **−0.006** | **−0.008** |

同じ2011～2020年に地理範囲を拡大しても、**地点内に反復観測を提供するサイトは同じ6サイト・22行**のままだったため、within-site rは変わらなかった。1993～2020年へ拡大すると、地点内に反復情報を提供する元サイトが**11地点・84行**へ増加し、旧物理PCAを固定していてもrはほぼ0になった。主要な不一致は生物カウントの時間窓・同サイト内反復集合であり、「広域で気候の因果効果が消えた」とは推論しない。

## 結論：この論文の仮説と証拠の境界

**YES**: original 588サイト・18地域・28年、温暖−低海氷PC1（65.1%）と塩分PC2（31.5%）の明確な物理環境構造、地理・時間の分離、時間方向の地域間異質性、site-year/sourceの再現性。

**NO**: 海氷・塩分・温度・植物・ペンギン転換の5変数一軸、18地域の実2種繁殖構成の同期、因果的な温暖化の動因、実際の繁殖地の移住・新規定着と将来の個体数。これらは別の予測モデルを試すだけでは解決しない。

**研究主線の一文**：*Antarctic marine environments share a warming–sea-ice gradient but retain a distinct salinity dimension; their regional temporal trajectories and observed penguin assemblage responses cannot be reduced to one transferable subantarcticization index.* 「亜南極化」は作業仮説名のままとし、既存文献を踏まえた初発見の名称とはしない。元温暖化・海氷・繁殖巣数の主論文から分割しない。

## 再現可能な結果とデータ原典

- [元595×2011年9月GLORYS海洋格子構築／元40サイトcrosscheck #42957439858](https://github.com/zuizui0223/mina/actions/runs/42957439858)、588地点・18地域・378固有モデル格子。
- [真正Copernicus GLORYS12V1 1993～2020元月次65,856行 #42958013800](https://github.com/zuizui0223/mina/actions/runs/42958013800)、artifact **13827762271**、元34サイト2011～2020の1,360記録完全再現。
- [元OSI SAF 71,400月×GLORYSを結合した18地域PCA・本当の種間計数 #42959103493](https://github.com/zuizui0223/mina/actions/runs/42959103493)、artifact **13828472111**。主な成果：16,464 site×year物理CSV、504 region×year CSV、18地域trend CSV、静的地図対応、元2種同年巣数比、source検証JSON。
- [34vs588サイト・2種同年計数の期間と物理PCA軸の独立感度 #42959683248](https://github.com/zuizui0223/mina/actions/runs/42959683248)、artifact **13828123433**。
- 調査法を地点×種で固定したMAPPPD元巣数2,456レコード、元EUMETSAT OSI SAF OSI-450a1 v3.1 monthly SIC（DOI 10.15770/EUM_SAF_OSI_0023）、[Copernicus GLORYS12V1 202311](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description)のモデル再解析。植物はPlantarctica 2017～2023 compositeの元地図。
- コード・guard: map_original_595_GLORYS_wet_grid.py、extract_original_588_GLORYS_1993_2020.py、analyze_original_18region_marine_regime_1993_2020.py、diagnose_regime_species_source_cohort_factorial.py と各synthetic unit tests。18地域の生態種間実2種カウントや植物年次に関する欠損は偽の0で埋めていない。

---

## 旧34地点×6地域の歴史的結果（新18地域主結果を上書きしない）

以下は当時の限定サンプルで計算自体は正しく再現できた内容であるが、**「18地域の塩分水温が取れていない」という当時のデータ制約は今回の原本取得で解消済み**。古い18地域NO-GOの文章は過去の時点の説明としてのみ残し、今回の論文結論には採用しない。


### 34地点時点の旧結論：地域間には強い一軸。ただし時間変化は多軸で、群集・植生との統合同期は未識別

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
