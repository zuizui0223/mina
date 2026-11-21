# 2013–2021年独立ポリニヤ検定の実現条件：L8撮影・較正は取得、真の糞ピクセル識別は外部ラベル未支持

**2026-11-20 JST｜mina Draft PR #214 only｜新期間のδ¹⁵N光学proxyとポリニヤとの関係は一回も検定していない。**

## 結論・現状

**`NO_GO_TRUE_POSITIVE_AND_NEGATIVE_GUANO_PIXEL_LABELS_NOT_OPENLY_VERIFIED`**。Source-onlyの段階で、初期の観測失敗を解消できた。Landsat 8 OLI の2013–2021年の画像在庫、元103標本による新センサー分光較正、元1984–2012年の地理一意の糞画素座標、native QA_PIXEL/QA_RADSAT の実測読み出しが再現成功した。一方、新画像での「糞 vs 岩・土・雪・影」の独立した真のクラスラベルと、元88地点・少なくとも6地域での外部精度は**まだ未取得**。画像在庫や元座標だけで検定用の新2013–2021 δ¹⁵N proxyを計算しない。

## 1. 検証できた原資料の分母

| Original source / reference | 実確認したデータ | 厳密な判定 |
|---|---|---|
| 昨日のポリニヤ探索 | 2004–10年に元**439 site×season、85 sites、11 regions**、冬6–10月100kmの元DEEP-AA coastal-polynya割合と光学δ¹⁵N proxy、夏塩分調整後 **−0.9216‰ / +10 percentage points**、11地域cluster CI [−1.3493,−0.4939]。地域1抜きで全負、2007–10時間外予測改善なし | **負方向は探索的発見**。過去の多検定を含み、その場での事前予測は正だった |
| 本来のL7 ETM+の2013–21新年 | USGS C2 L2原88地点の新シーン**0**（歴史的陽性対照3/3） | L7-only時間外追試は**撮影ソースが無く実施不能** |
| L8 OLIの2013–21 | 原88/88 sites、13/13 regions、9/9 start seasonsに原シーン候補、23,220 site×scene metadata | これは**有効な新糞画素数ではない** |
| L8 laboratory spectroscopy | 元103実糞標本×固有OLI RSR band2–7、固定5-PLSで100回holdout median RMSE **1.728865‰**、null 2.308787、元L7 1.742214 | L8向け**実験室較正PASS**。実衛星の真のguano分類ではない |
| 元Youngflesh RDSの旧候補 | **139,756 過去選別済みsource pixel rows、15,347固定位置の旧糞画素**（元88 site, EPSG:3031）。原 `guano_bin` は全件1、`bad` は全件0 | 旧場所は真正source。しかし未選別の岩・土・雪の**負例ゼロ**、2013–21現在の糞生息境界も不明 |

出典： [L7 #44658030485](https://github.com/zuizui0223/mina/actions/runs/44658030485)、[L8 imagery #44658813887](https://github.com/zuizui0223/mina/actions/runs/44658813887)、[L8 103-lab #44659513320](https://github.com/zuizui0223/mina/actions/runs/44659513320)、[old source ROI #44660639485](https://github.com/zuizui0223/mina/actions/runs/44660639485)、[3-region native 2018 QA #44662127603](https://github.com/zuizui0223/mina/actions/runs/44662127603)。

## 2. 本物の独立外部guano areaは見つかったが、真正同一siteでは3件/1地域

**Strang et al. (2025), Remote Sensing in Ecology and Conservation**, DOI [10.1002/rse2.70040](https://doi.org/10.1002/rse2.70040) は、2009–2021年のMaxar非常高解像度衛星画像から4 colony clusterの実際のguano stain **面積**を取得。著者の公開 [original data GitHub](https://github.com/AlexandraStrang/ADPE_Remote_Sensing/tree/759935d0a16f731af44d568ec47f686f6fb050e4/Data) は30件のsource `ADPE_guano_area_trends.csv`、Git blob SHA `d279d3f0d1cbcce6c027d0457ce685d0d8bf378d`。元88 original site IDとsource-onlyにjoinした [GitHub Actions #44668190981 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44668190981)、artifact **14599485662**、SHA256 `cbd2f443e88300caef449eb428e571d9123f77d47e5a1087f5e30f2afd9fcd2e`。

原サイトIDが直接一致するのは **INEX** 一地点（**Victoria Land**）だけ。2013、2017、2018 start seasonの3つの実guano area（m²）は：

| Season | 真のVHR撮影日 | VHRで測られたguano面積（m²） |
|---|---|---:|
| 2013 | 2013-12-04 | 68,654.6981 |
| 2017 | 2018-02-21 | 75,564.0224 |
| 2018 | 2019-01-10 | 83,632.1267 |

公開表の `CROZ` は元sourceの `CRZW/CRZE` 複数地点の集約であり、`BIRD` は `BRDN/BRDS/BRDM` などの集約。 `ROYD` は**元の固定88サイト集合には含まれない**。これらを勝手に新しい独立サイト／regional replicationへ対応させない。

## 3. INEX：VHR実測日とL8シーンの日付が一致、native画像QAも実測完走

2013–2021元L8 USGS source catalogに対し `INEX` 3実VHR日をsource-onlyでjoin。近接最短日と**±8日以内でのカタログ総雲量最小**を先に固定して、元サイトの本来の**128旧糞画素座標**へL8のnative C2 `QA_PIXEL` / `QA_RADSAT` を直接sampleした。raw spectral bandsは未開封。

| VHR season | VHR日 | L8ソース比較画像日 | 日差 | カタログ全シーン雲量 | native QAが有効な**旧位置画素** |
|---|---|---|---:|---:|---:|
| 2013 | 2013-12-04 | 2013-12-03 (日付最接近) | −1日 | 87.97% | **0/128** |
| 2013 | 2013-12-04 | 2013-11-26 (±8日・雲量最小) | −8日 | 0.07% | **127/128** |
| 2017 | 2018-02-21 | **2018-02-21（VHRと同日）** | **0日** | 1.75% | **107/128** |
| 2018 | 2019-01-10 | 2019-01-09 (日付最接近) | −1日 | 36.85% | **0/128** |
| 2018 | 2019-01-10 | 2019-01-11 (±8日・雲量最小) | ＋1日 | 16.97% | **128/128** |

Source-locked calendar crosswalk [Actions #44668950666 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44668950666)、artifact **14598104169**、SHA256 `e439ae605988981b807954b763e145bdd9083f7beeb5f4d18ab22ec61e65c688`。同一scene IDの地理・波長・品質条件を変えず、本物の `QA_PIXEL/QA_RADSAT` をPlanetary Computerの同USGS scene ID無料公開mirrorからnativeでsample。[Actions #44669179557 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44669179557)、artifact **14598688254**、SHA256 `98e72e00b89ab82fb69ecfbf514dde74adc3542a88ed0d469c735f807d2cb52b`。使用した5 distinct L8 scenesの署名付きSAS URLは成果に残さない。

**ここで言えるのは「新L8で、VHR参照年に同じ元地点の旧糞画素が実際に可視・未飽和で撮影された」まで**。元の場所に新年も糞があるかどうかはデータに記載されていない。Strangのarea=正解面積は**地理画素ごとの0/1マスクではない**。従って下流の光学δ¹⁵Nは未検証。

## 4. 機械読取できる外部正解ラベルへのソースゲート

1. **Le et al. (2019), [Weakly Labeling the Antarctic: The Penguin Colony Case](https://arxiv.org/abs/1905.03313)** は193殖民地の2044 VHR imageと24 colonyに属する31手動maskを報告。指定された [lynch-lab/CVPR19-CV4GC-WeaklyLabeling](https://github.com/lynch-lab/CVPR19-CV4GC-WeaklyLabeling/tree/b2b5a61a32137c250d1f26fd6bdb6c8ea03babef) のpin source treeを全件確認したが、**61ファイルはコード中心で、pixel-level polygon/mask原本をその公開treeには含まない**。元モデルは1–2.4mの商用画像向けでL8の30mに未検証のまま係数/分類器を移せない。論文にデータ存在とあることと、現在machine-readable原本が取得できることは別。
2. **Park et al. (2026), DOI [10.1002/jgo2.70027](https://doi.org/10.1002/jgo2.70027)** は2018年Cape Hallettの手描きUAV糞maskを基準にしたLandsat8 guano分類について **commission 59%, omission 21%** と報告。論文のデータは著者への合理的な請求による提供と記載。したがって**実測糞領域の誤判定を無視できない**。
3. **KOPRI-KPDC-00003118.1** [2018–2025 Cape Hallett UAV orthomosaic metadata](https://kpdc.kopri.re.kr/search/8ef94868-4924-4363-a862-b9d34678e86f) はWGS84/UTM59S同地点の画像・co-registration metadataを列挙。しかし公開metadataでは新maskの正負真値が独立の座標ファイルとして直接確認できない。この研究にも編集者・対応著者の提供が必要。

## 残タスクと凍結規則

**残っているのは分類精度を検証できる、独立に地理参照された「現年の糞＝1／岩・雪・土＝0」の真のラベル**。ラベルは撮影年、元site ID、真のpolygon/point、pixel QAを添えて入手し、元の事前凍結した少なくとも30sites、6原地域、4season、注目3地域各3サイトの2013–21新画像実支持が確認できた場合だけ、改めてδ¹⁵N optical proxyと冬ポリニヤ100kmの負方向を一回検定する。単一INEX地点の面積3値でL8 pixel-level精度や南極汎一般の機構を認証しない。時間外予測改善が過去には無かった事実も残す。

**現状判定：** **`NO_GO_EXTERNAL_MULTI_REGION_PIXEL_TRUTH`（機構仮説反証ではなく外部ラベル源の不足）**。新2013–21 δ¹⁵N Yなし、ポリニヤとの新係数なし。旧観測内439件の負係数は探索的発見のまま正しく保持する。別センサーでの独立追試を済ませたと書かない。

**主線：** mina Draft PR #214にのみsource auditと実行コードを保存、`main`・既存v0.5/v0.6・Ecology Report/Paper2は一切変更しない。新しい半径・ラグ・proxy選択でp値を取りにいかない。
