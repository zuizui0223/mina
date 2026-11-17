# 南極半島Gentoo繁殖利用の変化×過去の氷河前縁：公開原資料の取得・実画像QA・物理的被覆まで検証

**2026-11-17 JST｜mina PR #214｜SOURCE AND PHYSICAL OPPORTUNITY FEASIBILITY, NOT biological mechanism confirmed.**

## 何が実際に新たにできたか

元MAPPPDで5siteのGentoo初観測0巣→反復正巣数を確認済（BISC/ORNE/GALE/TXRX/VERN）。近傍の10km連結で**3地理グループ**。今回、新たに **(1) Landsat C2 L2原シーンの過去年カタログの実取得、(2) オリジナル衛星QA_PIXELを実地理座標固定点で77件読込、(3) GLIMS WFSの地理的実輪郭38 featureを取得し、1989/2002の同一glacier IDのみに制限した2km/5km内氷河ポリゴン重複面積**を本当のソースから算出・検算した。初めて計数の地理と**独立して計測された陸側の物理量**を近傍へ接続した。ただし、氷河輪郭の変化そのものは新規の営巣可能裸地面積や実個体の定着要因を示さない。

## 1. Landsat：19 cluster-year実検索×元画像77件QA

Microsoft Planetary Computerの公開 STAC collection landsat-c2-l2（USGS Landsat C2 L2、NASA/USGS原観測）へ、3つの地理グループ×1985/1987–2016のオーストラル夏 **1–3月**だけを選んで19件の独立の元検索を送信（検索エラー0）。9/19 cluster-yearsで画像があり、**123シーン**。**Tier 1は0／Tier 2が123**。すべて元QA_PIXEL assetを有していた。Tier2は相対的幾何基準を満たさない画像であるため、細い営巣区画を精密に比較できるとは主張しない。

実元画像のうち、観測機会だけから固定した6 cluster×year（Orne 1997/2003、Galindez付近2003/2007、Biscoe 2006/2016）でシーン雲量順・最初の最大8枚/年を選び、original QA_PIXELを **77シーン×5対象siteの対応した元EPSG:3031基準座標 ±500/250/0 mの25地表点**で読取。77／77 rasterio/Planetary Computer取得成功、元データ読込エラー0、GALE/VERN/TXRXは同じシーンを再利用。QAはfill、dilated cloud、cirrus、cloud、cloud shadow、snow、waterのbitを全て除外（0,1,2,3,4,5,7）。**一度QAが通ればその点はその年に観測された**、ではなく、ソース画像で晴天・無雪・非水域に分類された候補地表の証拠だけ。

| colony ID | 比較した画像暦年 | 各年の元QA読込成功シーン | QAが少なくとも一回非雪/非水だった固定点 | **両年にQA-clearの同じ固定点** |
|---|---|---|---|---:|
| ORNE | 1997 / 2003 | 5 / 8 | 0 / 0 | **0/25** |
| GALE | 2003 / 2007 | 8 / 8 | 8 / 3 | **0/25** |
| VERN | 2003 / 2007 | 8 / 8 | 1 / 2 | **0/25** |
| TXRX | 2003 / 2007 | 8 / 8 | 0 / 0 | **0/25** |
| BISC | 2006 / 2016 | 8 / 8 | 0 / 1 | **0/25** |

この結果は選定した最大8シーン・Jan–Mar・25固定点に条件づけた観測支持であり、年中の全日時の完全画像不在・不変の岩地・全島の露岩面積0を意味しない。最大8 scene選択は**元source scene-level cloud percentage**のみで、地表QAの結果を見て選んだものではない。別時点年の原配列が同じ地表の露岩・植生差を実測できる**共通画素分母が今回0**。そのため、ここで新しいNDSI/NDVI傾き・colonization前後差・統計的p値を作らない。

既知の元MAPPPD Gentoo 0→最初正はBISC 1984→1994、ORNE 1998→1999、GALE/VERN 1999→2007、TXRX 2003→2006。肝心のsource first positive 1994 BISC、1998/1999 ORNEにはこのJan–Mar C2L2でscene0。BISC 2006/2016とTXRX 2007は**新しい定着の後の画像**であり before-after event effectとは呼ばない。

**初期データ源の再評価**：元repos \`landsat_vegetation_support_v1/REPORT_JA.md\` でも2018/19の8site計227 Landsat8 QA source imageの全件がTier2、両年2日以上同一QA-clear mapped-vegetation pixelsは1地点のみの結果があり、今回のQA支持不足は新しい探索閾値の失敗だけではなく、測定幾何・季節・雲雪の系統的な限界と整合。

## 2. GLIMS：初めて独立の地形・氷河輪郭を元GISで数値取得

NSIDC/GLIMS **WFS** の元レイヤー \`GLIMS:GLIMS_Glacier_Outlines\`、公開サービス \`https://www.glims.org/geoserver/ows\`。実WFS GetCapabilitiesはHTTP正常、全50 feature types中7つに氷河関係の名称。対象3元sourceクラスターbboxで**8 BISC／25 ORNE／5 GALINDEZの元glacier polygons**を実際に取得（WFSクエリエラー0）。同じglacier IDが**1989-11-26と2002-12-31**で存在したものに絞ると、BISC **2 glacial IDs**、ORNE **7**、GALINDEZ **0**。GALINDEZが0だから氷河無し、という意味ではなく **観測年が1957/1989などで一致しない**。

元各geometryをWGS84→EPSG:3031に変換、same-glacier-ID × source date毎に複数ポリゴンをunionし、元source colony中心固定半径2kmまたは5kmの球形バッファにclip。glacier IDsが片年だけのポリゴンを0として補完せず除外。A(1989)−A(2002)=(1989にだけ存在する部分面積)−(2002にだけ存在する部分面積)のShapely幾何恒等式をCIで再確認。

| 固定中心 | 半径 | 同じ氷河ID | 1989の元ポリゴン被覆 km² | 2002の元ポリゴン被覆 km² | **正=氷河ポリゴン被覆減少 km²** |
|---|---|---:|---:|---:|---:|
| **Biscoe Point** | **2km** | 2 | 3.2691 | 2.7366 | **+0.5326** |
| Biscoe Point | 5km | 2 | 33.3490 | 34.5867 | **−1.2377**（増加方向） |
| **Orne Islands** | **2km** | 7 | 0.8856 | 0.3902 | **+0.4954** |
| Orne Islands | 5km | 7 | 9.2814 | 8.2986 | +0.9828 |
| Galindez/Vernadsky | 2km/5km | **0** | **NA** | **NA** | **NA** |

**重要な幾何学的境界**：Biscoeの結果は2kmではポリゴン減少だが5kmでは符号が逆。従って一律の「氷河後退で新規の営巣地が増えた」を意味しない。GLIMSの各時代で異なる海岸・氷河部分のdigitizingや登録精度、2002-12-31が実衛星撮影日でなく年末元ソース時点表記である可能性、元ポリゴンで認識される氷氷河の境界と海・陸区別が曖昧などの制限がある。これは二期だけの**著者依存の氷河描画集合に条件づけた地理的量**である。

GLIMSの2002年輪郭は**Biscoe 1992/93年Gentoo発見と1994年source正巣数の後**、Orne1999年正巣数の後。したがって1989→2002の物理変化量を**繁殖成立の先行要因**として回帰に入れることは時間順序違反になりうる。どちらも2002年以前に氷の減少が始まっていたかを確実に区切る別の地形データは、今回入手した2期源だけではない。

**氷河ポリゴンの消えた面積 ≠ 2002年の営巣可能裸地。** 氷が後退した場所は開水面かもしれず、現代の地図上の露岩でもその時点での雪・排水・巣のための面積とは異なる。Biscoeでは歴史的氷ランプ喪失によりAnversとの接続が分断されたことは別文献で裏付けられるが、GLIMSの半径2km氷河ポリゴン面積差だけでそのランプの季節・年代を特定できない。

## 3. Cook–Fox–Thomson (2021) の原海岸線GISを取得し、1989/1998年の地理同一性まで検査

英国極地データセンターDOI **10.5285/07727663-9B94-4069-A486-67E4D82177D3** の原ファイル Coastal_change_EPSG.zip を実際にダウンロードした。**7,493,252 bytes**、原SHA256 **cd17b91692d2f110acbe84553b950161f03f3e4c01c0d622ffaca1682af972d4**。原EPSG:3031のShapefileには**13,436本**の実海岸・氷河前縁の線分があり、元観測年、信頼性、地形区分、元ソース出典を各行で確認した。1843–2008年というデータセット期間は、各地点の年次連続観測を意味しない。

各source繁殖地群の中心半径2kmにある本物の線分の元年・種類：

| 群 | 2km内原線分 | 実際にある測定年 | 対応する巣数記録 |
|---|---:|---|---|
| **Biscoe Point** | **24** | 1956,1968,1973,**1989**,1998 | 1984年0→1994年14巣 |
| Orne Islands | 7 | 1956,1973,1989 | 1998年0→1999年3巣 |
| Galindez/Vernadsky/Tuxen | 28 | 1956のみ | 1999/2003年0→2006/07年正巣数 |

Biscoe1989の資料は0→最初の正巣数の記録間に位置する。1989年の岩石海岸4線分・氷海岸5線分、1998年の岩石海岸3線分・氷海岸5線分はそれぞれ元で区別できた。一方OrneやGalindezでは変化期間の前後を独立に覆う海岸線がない。

### 決定的な確認：異なるsource年・IDでも地図の大部分は全く同じ線分だった

Biscoe半径2kmの1989年と1998年を、元source EPSG:3031で地物ジオメトリそのものの完全一致と共通ライン長で比較した。

| Source類型 | 1989年線分 | 1998年線分 | 別年で幾何的に完全一致した線分ペア | 1989年の総線長に占める重複 | 1998年の総線長に占める重複 |
|---|---:|---:|---:|---:|---:|
| 氷の海岸線 | 5 | 5 | **3ペア** | **91.87%** | **83.24%** |
| 岩石海岸線 | 4 | 3 | **3ペア** | **80.75%** | **100.00%** |

GISの元地物IDは異なるが、全く同じ座標列を持つ別年ラインが実際に存在した。したがって、**2つの年号があることを2つの独立した地形変化測定と呼ぶのは誤り**。1998年岩石海岸線長の100%は1989年の地図にもすでにあり、1998年に「新しく露出した岩石海岸」をこれらの線から算出できない。1989と1998の全海岸線が変化しなかったという意味ではない。欠損ラインや測量範囲の差、元の画像幾何と原編集履歴を分離しない限り、真の氷ランプ切断日や裸地増加面積は不明。

このことは、旧MAPPPDの既知コロニーだけに複数の時代の海氷や海岸線を加えても、**独立して観測された生態学的応答の反復数が増えない**という、今までの探索の実測された問題点である。

ソース再現：公式7.5MB原ZIPの実取得 [#44037197204](https://github.com/zuizui0223/mina/actions/runs/44037197204)、13,436線分の観測年・岩/氷分類照合 [#44037806473](https://github.com/zuizui0223/mina/actions/runs/44037806473)、Biscoeの完全同一geometry照合 [#44038011806](https://github.com/zuizui0223/mina/actions/runs/44038011806)。3件ともSUCCESS。元ZIPと派生CSV/JSONをGitHub Actions artifactへ30日保持。

## 4. 先行研究と照合した、今回できたこと・まだ識別できないこと

**新たに実測した肯定的な物理量**：公開の同じglacier ID・2源時代の元geometryから、Biscoe/Orneの2km周辺でそれぞれ約0.53/0.50 km²の描画済み氷河被覆減少を再現した。元MAPPPDでは両地点のGentooが0記録から繰返し正巣数へ変化した。ただし**2期氷河地理と繁殖遷移の完全な同時ペアではなく、独立の複数地域反復ではない**。

**新しい機構か？ NO**：Herman & Lynch (2022, Ornithological Applications, DOI 10.1093/ornithapp/duac014) が既にBiscoeとOrneを含むGentooの4新規コロニーの増加に**長期移入が必要**と推定。Cimino et al. (2026) はPoint8で氷河後退後の営巣・雛成功の出現を別の観察で示す。Gallagher et al. (2025) は陸×海の静的SDMを3種で検証済み。したがって「温暖化で氷河減少→Gentoo増」という2点の一致だけでは、独立した新しい島嶼生態学の原因ではない。

**何が本当に足りないかが特定できた**：①同じ利用可能パッチ×季節の記録0/正と検出努力、②日付を持つglacier/rock/seaの地形状態を区別する**再検証可能な陸マスク**、③同一採餌期の実餌資源・海へのアクセス、④独立地域での同じ生物状態と物理共変量。現状の「既知siteの巣数」「近岸100kmSIC」「1989/2002の海岸付近氷河ポリゴン」ではこれらを揃えられない。

**論文への境界**：これをv0.6の主要旨に新しい気候適応・新規コロニー発生法則として加えない。supplementには**source support finding**として入れられる。マクロ論文を本当に新しい動的海陸機会論へ変えるには、過去を空き地として調査した比較候補裸地パッチを揃え、未開封の別地域で事前仕様を一度だけ検証する。

## 5. 実行の真正ソースとCI

- 元MAPPPD2,456 original counts, 35 observed 0/positive transitions, 5 repeated GEPE site IDs: [original count/sea-ice source audit #44025152509](https://github.com/zuizui0223/mina/actions/runs/44025152509) SUCCESS。
- Landsat元検索19件/123 scene（source coverage/status): [#44035241809](https://github.com/zuizui0223/mina/actions/runs/44035241809) SUCCESS、artifact **14306602925**。
- 実元Landsat QA_PIXEL read77/77 with 5 site 2-year same-location diagnostics: [#44035592053](https://github.com/zuizui0223/mina/actions/runs/44035592053) SUCCESS、artifact **14306748172**。WGS84元坐標→EPSG:3031地表固定5×5格子へ投影、QA bit/source timestamp/source IDを全部記録。
- GLIMS WFS original 38 features / source times and glacier IDs: [#44036033057](https://github.com/zuizui0223/mina/actions/runs/44036033057) SUCCESS。
- GLIMS source geometry/2km-5km actual polygon accounting: [#44036259707](https://github.com/zuizui0223/mina/actions/runs/44036259707) SUCCESS、artifact **14307467301**。
- 元公式情報：USGS [Landsat Collection 2 Level-2 Surface Reflectance](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance)、[Planetary Computer STAC](https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2)、[GLIMS Database](https://www.glims.org/glacierdata/)、[Cook/Fox/Thomson 2021 historical coastlines, DOI 10.5285/07727663-9B94-4069-A486-67E4D82177D3](https://doi.org/10.5285/07727663-9B94-4069-A486-67E4D82177D3)。Cook原GISについても上記の通り**実際に取得・位置照合・幾何同一性を検証済み**。ただしCookの海岸線とGLIMSの氷河ポリゴンは異なる推定対象なので、共通の裸地面積として足し合わせない。
- 実行script: \`probe_public_historical_land_source_coverage.py\`, \`audit_original_landsat_pixel_QA_event_windows.py\`, \`probe_GLIMS_coastal_glacier_date_support.py\`, \`derive_GLIMS_1989_2002_fixed_neighborhood_glacier_cover.py\`。ソースZIPは成果保存、期限30日。main・Paper1/2・単一マクロ原稿v0.5は変更しない。
