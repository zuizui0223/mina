# 南極の環境変化は一つの「亜南極化」軸なのか：元588繁殖地・18地域・28年のマクロ解析

**2026-11-11 JST｜元データ実測・再解析｜探索的 / 気候の因果帰属・生物将来予測ではない｜mina Draft PR #214**

## 結論：南極の海洋環境は二軸に近い。地域・年代で変化が異なり、ペンギン群集への一対一の転写は未成立

**旧34地点・6地域では見えにくかった構造**が、元の595繁殖地全体に物理海洋データを拡張して明確になった。588地点・18地域、1993～2020年の28年×4か月（元site×month：65,856 GLORYSと一致する既存のOSI SAF）の**欠測なし固定16,464 site×year**を使った3変数PCAでは、標準化PC1=**60.3654%**, PC2=**33.3773%**, PC3=6.2573%。温度正方向のPC1は、海氷濃度**−0.70734**、表層ポテンシャル水温**+0.70583**、表層塩分**−0.03835**。一方PC2は表層塩分**+0.99772**、海氷+0.01216、水温+0.06640で、**塩分は海氷/水温対照とはかなり独立した第2環境軸を形成する**。

元site×yearの実際の相関はSIC×水温 **r=−0.80977**、SIC×塩分 **r=+0.05390**、塩分×水温 **r=+0.00996**。海氷・水温だけの変化を「海氷減少＋淡水化＋陸の緑化＋ジェンツーへの一軸的交代」と呼んではならない。海氷生成の塩分排出・融解水の塩分希釈は物理的に起こりうるが、実際の海洋塩分は移流・混合・水塊形成・再解析の観測同化にも左右される。

**地理的・時間的な非一様性**も明示された。元全域PC1分散の70.705%は18原地域の平均値の違い、29.295%が地域内の差。各siteの28年平均を引いた時間偏差PCAのPC1説明率は**55.252%**、海氷−0.66642、水温+0.66542、塩分**+0.33630**。この符号は年々の共変動の向きであって、塩分の28年間の平均トレンドが正という意味ではない。空間一軸をそのまま時間的な統一方向として解釈できない。

実際の同年2種繁殖計数とこの固定PC1との**地点内**相関は、アデリー/ジェンツーの98地点年・25サイト（うち反復あり11サイト）で **r=−0.00758**、ヒゲ/ジェンツー165地点年・33サイト（反復20）で **r=+0.06097**、アデリー/ヒゲ88地点年・24サイト（反復9）で **r=−0.04201**。この物理PC1だけで南極全域の3種群集比の時間変化を説明したとはいえない。

## 1. 「18地域マクロ」が実際に成立したデータ基盤

| 元データの種類 | 実際のデータ |
|---|---|
| MAPPPD実観測コロニー・繁殖巣数 | 595既知繁殖site、18原報告地域、2,456 site×species×実観測年。欠測は0巣でない |
| EUMETSAT OSI SAF OSI-450a1 v3.1 SIC | 595 source site×1991～2020年×8～11月=71,400原source site-month |
| GLORYS12V1 202311月次表層塩分・水温 | 588サイト×1993～2020年×8～11月=**65,856原site-month**、18地域 |
| 実際のGLORYS海域セル | **378個**。588 colony siteの多くはモデルの同じ海域セルを共有する |
| GLORYS海域セルまで25km以内 | 588/595 sites、18/18 regions。元40サイトの配置・25km判定40/40再現 |
| 全部が同じサイト×年×4か月で揃う物理PCA | **588 sites×28実年=16,464 site-year**、18地域。欠測による補間なし |
| 元34-site旧版への厳格なbackward reproduction | 2011–2020の34サイト340地点年PC1説明率**70.9431%**とPC1負荷量3つすべてが旧数値と1e−8以内で一致 |
| 物理分野の年数 | 1993～2020=28年。1991～1992年のGLORYSとの結合を創作しない |

Publisher original source GLORYS extraction SUCCESS https://github.com/zuizui0223/mina/actions/runs/42958013800 artifact **13827762271**（65,856月次値、18地域カバレッジ、旧1,360月次GLORYS数値一致）。元の595地点ネイティブ海氷source SUCCESS https://github.com/zuizui0223/mina/actions/runs/42612067836 artifact 13671496095。**今回の実解析の成功run #42961084667**、artifact **13829236358**：全16,464元source site-year、年×地域504行、地域別28年の傾き、元3種実同年カウント、静的植生関係、完全JSONを保存。再現コードはこのPRの analyze_original_588_18region_marine_pca.py、5個の独立した原source count/math tests、workflow penguin-original-588-18region-marine-pca-and-species.yml。

ロス島のCape Crozier West / Cape Royds等の7地点は海洋セルまで25km超過のため今回のGLORYS PCAに入らない。PR #215の既知自然実験を今回の軸で説明したと主張しない。588地点と378海洋セルは独立した繁殖環境操作実験ではない。

## 2. 真の二軸性と地理的反復・時系列感度

| 数値 | 原source実測・再解析結果 |
|---|---|
| 全16,464site-year PCA PC1/2/3 | **60.365% / 33.377% / 6.257%** |
| PC1 (SIC, salinity, thetao) | **−0.70734, −0.03835, +0.70583** |
| PC2 (SIC, salinity, thetao) | **+0.01216, +0.99772, +0.06640** |
| 18原地域×28年の各地域等重みPCA PC1 | **65.1375%**、PC1 salinity loading −0.23253。全地点PCAとloading cos +0.98079 |
| 各GLORYS水塊格子×年を1回だけにするPCA PC1 | **60.4693%**、PC1 salinity loading −0.05450。全地点PCAとloading cos +0.99987 |
| 各siteの28年間の気候変数平均を除く temporal anomaly PCA PC1 | **55.2524%**、salinity loading **+0.33630** |
| 全サイトPCAスコアの報告地域between/within分散 | **70.705% / 29.295%** |
| 588 siteごとの28年間の気候平均のみPCA PC1 | 64.8417% |
| 18地域ごとの気候平均のみPCA PC1 | 71.4244% |

**34地点を選んだ従来モデルの全変数「亜南極化」単一軸=70.94%（SIC−0.643, 塩分−0.489, 水温+0.589）は、その地理的サブセットの事実**。588サイトへ拡大するとsalinity loadingが−0.038へ変わるため、以前の塩分関与の強さを全18地域の一般則として外挿できない。各地域等重みでもPC1に塩分が多少寄与するが、いずれにせよ海氷・温度対照と同等の一軸同時変化とはいえない。

この統計はGLORYS海洋再解析×OSI SAF元海氷の同年海域source対応であり、GLORYSの観測同化に海氷/水温情報が入る。**原因変数の独立した実験や塩分の因果効果の識別ではない**。

## 3. 長い28年で見ると、半島・島嶼の温暖側PC1は単調ではない

従来の2011～2020年10年だけでは、半島中西部・サウスシェトランドでmarine PC1の正方向の変化を記録した。しかし1993～2020年へ拡張し、**同じ588地点、全28年、同じ凍結PCA負荷量**で比較すると、一様な単調上昇ではない。各期間のmean PC1はPCの再fitなしで同じ数値軸。1993–2000期間は8年、2001–2010と2011–2020は各10年であり、傾きの比較ではなく水準の時代別記述である。

| 元source地域 | 地点数 | PC1平均 1993–2000 (8年) | PC1平均 2001–2010 | PC1平均 2011–2020 | 全28年PC1線形傾き/10年 |
|---|---:|---:|---:|---:|---:|
| Central-west Antarctic Peninsula | 106 | **+0.365** | **+0.888** | **+0.445** | +0.080 |
| South Shetland Islands | 118 | **+1.181** | **+1.586** | **+1.093** | −0.027 |
| Elephant Island | 51 | +1.251 | +1.735 | +1.111 | −0.090 |
| South Orkney Islands | 88 | −0.500 | −0.029 | −0.480 | −0.037 |
| Victoria Land | 43 | −1.645 | −1.623 | −1.642 | +0.0003 |
| Northwest Antarctic Peninsula | 16 | +0.487 | +0.913 | +0.692 | +0.089 |
| Northeast Antarctic Peninsula | 39 | −0.449 | −0.028 | −0.148 | +0.157 |
| Mac. Robertson Land | 24 | −1.823 | −1.752 | −1.825 | −0.018 |

**13/18の原地域**は2001～2010年のPC1平均が1993–2000年および2011–2020年の両方を上回った。250kmブロックが2以上、元繁殖site3以上、海洋セル2以上の地理反復に限定しても、**10/13地域**でこの中期ピークが記述的に見える。一方、全28年間のPC1の単純線形傾きは全18地域中**11地域で正、7地域で負**、地理反復13地域に限っても**8正・5負**。

**この意味：** 亜南極化を「いつも毎年同じ方向へ進む」一本の時間軸と仮定すると、特に2000年代後半/2010年代の海氷変動・地域差を見落とす。平均が一度上昇・低下したことから、植生やペンギン繁殖が逆行したとはいえない。ENSO/SAM/海流変化、氷河水量などの影響分離もしていない。気候温暖化そのものがなかったことは意味しない。

## 4. 気候軸とペンギン群集の相関は、データを増やすと一般化できなかった

元MAPPPD site×species×actual count seasonの両種が同じ元繁殖地・年に**共に実計数された**場合のみ、観測巣数の log1p(second) − log1p(first)を作る。採集方法はsite×species内で固定、同年2種間で同じ計数法の比率97/98 Adélie/Gentoo、165/165 Chinstrap/Gentoo、88/88 Adélie/Chinstrap。なお**同じ出典citekey・調査日・努力の完全同一性は未確認**で、「正確な同時センサス」とは主張しない。

| 組 | 実同所同年2種巣数記録 | 元site/地域/250kmブロック | raw PC1 vs log巣数比 | 同一site内の年変動相関 |
|---|---:|---|---:|---:|
| **Adélie / Gentoo** | **98** | **25/6/5** | −0.114 | **−0.008**（反復11site/4地域/3ブロック） |
| Chinstrap / Gentoo | 165 | 33/6/7 | −0.036 | +0.061（反復20site/3地域/5ブロック） |
| Adélie / Chinstrap | 88 | 24/6/8 | −0.131 | −0.042（反復9site/3地域/3ブロック） |

**以前の34site解析との数値一致と、標本/軸の効果の分解を実行済み**。Adélie/Gentooの以下の4条件は新しいデータを都合よく選別せず、前回の34地点セット・2011～2020年共通実カウント年とそのまま比較。

| 生物的な対象site×year | Marine PC1の軸の作り方 | 元同所同年2種カウント数 | 同一site内相関 |
|---|---|---:|---:|
| 元34siteだけ・2011–2020（旧結果の厳密再現） | **その34siteで学習した元PC1** | 23 | **+0.5232** |
| 完全に**同じ23site×year**（軸だけ変更） | **588site全域のPC1** | 23 | **+0.1985** |
| 588siteのうち2011–2020年に実際に2種計数 | 同じ588site全域PC1 | 37 | +0.1985（繰返しsiteは前行と同じ6site/22年） |
| 588site全域の1993–2020年、実際に2種計数 | 同じ588site全域PC1 | 98 | **−0.0076** |

前回の旧PCAと旧生物結果が数値一致しているため、**新旧の相違はコードの再現失敗ではなく、環境軸を決める地理的背景と実観測対象年・地点を拡張したこと**による。2011–2020の実反復siteは増えないので、37記録に増えてもwithin-rが同じなのは新規source siteの多くが1年のみの実計数だから。

**これが生態学的に重要：** 「温暖・低海氷の地域ほどジェンツー比率が高い」「同じ場所がその方向へ変わるとジェンツー比率が上がる」は異なる検証対象で、どちらも今回の元18地域全体の生物現象として支持されていない。海洋物理PCAが明確であっても、種構成変化を時代/地域を越えて転写できるとは限らない。繰返しsiteや海域セルは統計的に独立でなく、p値を試して都合よく結論を出さない。

## 5. 陸の植生・地衣類・藻類との関係も、一軸では説明しきれない

source pinned元modern mapped-land cohortは246 site×species行・222実site。元2017～2023年のPlantarctica**静的な2km陸域地図に正のマッピングがあり、海洋28年物理panelへ結合できたのは167実site・8原地域**。この面積は植生だけでなく**Vegetation/Lichen/Snow Algae等の陸域ポリゴンのunion**であり、これらを分けない場合に単独の「緑化」指標とは呼べない。

- 同じ167実siteだけのoriginal mapped positive terrestrial polygon areaと1993～2020 marine PC1 site平均の**Spearman ρ=+0.2369**（地理的に全8地域をプールした記述）。
- **元地域平均を除く**と、log1p(positive static mapped terrestrial union area)とのsite等重みPearson **r=−0.0954**（全167実site/8地域）。
- 従来の34site subset の25 positive-only Vegetation classでの ρ+0.7359 は、環境PCAのaxis、地理的対象site、測定していた陸域対象クラスが変わるため、直ちに同じ推定量として比較しない。それでも以前の強い+0.74だけで全南極の陸・海・生物が統一的一軸であるとは主張できない。
- 元site×yearカウントや年別海洋scoreに静的mapを28年繰り返し貼り付けて緑化速度・海氷後退の先行ラグを推定していない。0 mapped polygonは植生実不在と同義でない。

## 6. マクロ生態学として残せる主張と限界

**Yes (実計算で支えられる):**
1. 南極18地域の既知繁殖サイトに接続した沿岸物理データでは、*海氷–水温*の連関が明瞭であるが、表層塩分はその一本に統合されず第2軸を作る（PC2 salinity loading+0.998、全site yearのSIC–salinity r+0.054）。
2. 海洋物理axisは地理的に強いが、年単位/年代によって地域の方向・時点が異なる。13/18地域の2000年代中期平均が前後を上回り、28年の単調進行は支持されない。
3. 以前の小さい6地域・34siteのPCAと相関が再現したうえで、新規18地域・588siteの独立source frameでは物理axisが変わり、同年実2種巣数と温暖側PC1のwithin-site対応は一般化しない。
4. 2020年以前の元衛星海氷と1986～2021年などの公表植生変化を同じ元時系列と扱わず、緑化の実効率は未検証。

**No (識別できていない):** 温暖化/氷山/漁業/ポリニヤ/塩分の個別因果効果、18地域の未記録種の実不在・colonization、海氷/塩分/植生の同時進行する5変数指数、species trait/foraging niche inference、未来CMIP6の「ペンギンが何羽生き残るか」、生態学的10年ラグ/ climate debt。海水温はGLORYSモデルのsurface potential seawater temperatureであり、地上気温とは違う。

**論文の1文（検証対象として）：**
> Antarctic coastal thermal–ice covariation forms a spatially coherent environmental axis, while surface salinity, temporal trajectories, and recorded penguin breeding assemblage changes do not collapse onto one universal subantarcticization gradient.

独立のsource locationを地域数/海域セル数/カウント年数として報告し、PCAのsite×yearを個体群の独立反復と数えない。Causal warming adaptationを直接特定した研究として売り出さない。提出用の単一マクロ論文の物理・ニッチスケール図の主要候補として保管し、新規paperへ発散しない。

## 原本・実行成果物

- [全18地域の本解析 GitHub Actions SUCCESS #42961084667](https://github.com/zuizui0223/mina/actions/runs/42961084667)、原データ・配列・6CSV・JSONを含むartifact ID **13829236358**。
- Original marine GLORYS12V1実1993～2020年の588site/65,856site-month再取得・元34 site照合: [GitHub Actions #42958013800](https://github.com/zuizui0223/mina/actions/runs/42958013800) artifact **13827762271**。
- 595 original site×1991～2020年EUMETSAT OSI SAF original v3.1 Aug–Nov NetCDF source SHA receipt: [#42612067836](https://github.com/zuizui0223/mina/actions/runs/42612067836) artifact **13671496095**。Official DOI 10.15770/EUM_SAF_OSI_0023。
- GLORYS12V1 202311 original URI frozen in climate_penguin/ocean_monthly_manifest.json; https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description。
- コード: analyze_original_588_18region_marine_pca.py、unit_test_original_588_18region_marine_pca.py（5数学/原countテスト）、.github/workflows/penguin-original-588-18region-marine-pca-and-species.yml。
- 契約: GLORYS_588_18REGION_SPATIOTEMPORAL_PCA_CONTRACT_20261111.md。GitHub Draft PR #214 の専用ブランチのみ。main と凍結 Paper 1/2、PR #206、先行PR #215は触れていない。
