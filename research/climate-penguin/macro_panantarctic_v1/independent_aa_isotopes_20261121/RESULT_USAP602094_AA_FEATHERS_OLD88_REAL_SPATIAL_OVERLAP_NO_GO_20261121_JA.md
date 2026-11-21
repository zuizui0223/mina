# 元の冬ポリニヤ439観測と独立AA羽毛：同一地点の対を作れるか、元88地点の地理で直接検証

**2026-11-21 JST | Source-only spatial geodesic audit | 別データの実同位体・TP値も、元光学Yも、ポリニヤ効果も一切fitせず。** 元の厳密な地理判定仕様 [`FROZEN_AA_OLD88_SOURCE_GEOGRAPHY_MATCH_ONLY_20261121_JA.md`](FROZEN_AA_OLD88_SOURCE_GEOGRAPHY_MATCH_ONLY_20261121_JA.md) をcommit `e5e4fa8`で距離を計算する前に固定した。使用したソースは真正USAP602094元ZIP（元CSV MD5 `f9a91c9d9bf3dba9607bf0767df8c206`）と元Youngflesh88地点のsource-only geog artifact 14539723210（SHA256 `702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96`）、元860 site×season membership artifact 14328755565（SHA256 `dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`）。

## 明確な結果：同じ繁殖地の直接ペアは0件

実AA `bulk d15N, Phe_d15N, Glu_d15N, Trophic_position` の4値が存在し、旧解析で冬ポリニヤが実測された**2004–2010年に採集された**元羽毛は7個体、3 `Site`ラベル、6地点×**採集年**。元のpreselected88地点（元の光学糞ROI座標に由来するcenter）とWGS84の測地線を計算した。

| 真正USAP羽毛元Site | 該当採集年 | 最寄りの旧Youngflesh 88地点ID | Source地理的最短距離 | ≤25km一致 |
|---|---|---|---:|---|
| COPA | 2006, 2007, 2008 | `TSIS`（South Shetland Islands） | **30.545 km** | **0/3** |
| Cape Crozier | 2004, 2005 | `BEAU`（Victoria Land） | **79.943 km** | **0/2** |
| Ross Island（Source表記、地域に幅のある座標） | 2009 | `BEAU`（Victoria Land） | **65.178 km** | **0/1** |

固定した採集地点との一致基準**2km、10km、25km の全てで0/6地点×採集年**。旧860に「最近接」地点IDの**同じ採集年ラベルのproxy原記録**自体が存在するケースは2/6だったが、どちらも実距離**65–80 km**であって同じ繁殖地とは呼べない。25km不一致の地点を「100kmポリニヤに入るから同じコロニー」と扱わない。

- 元AAはSourceの`Latitude`/`Longitude`（COPA −62.167°, −58.467°、Cape Crozier −77.458°, 169.263°、Ross Island −77.5°, 168.0°）。後者はWikipedia由来の島代表座標で実採羽位置と断定不可。COPAはAustralian Antarctic Data Centre、Cape CrozierはMAPPPDの出典。
- 元Youngflesh中心は `TSIS` (−62.0779°,−57.9135°)、`BEAU` (−76.9694°,166.8978°)。元の光学糞選別地点重心に由来するsource geographyであり、独立な巣GPS真値ではない。地理距離は標本元Siteラベルの精度に依存する。
- さらに`Year_collected`は羽毛形成/換羽年ではない。よって仮に地理距離2kmでも、その年の冬沿岸ポリニヤと羽毛TPを直接結合する時間整合性は別ゲートで必要。

## 研究の帰結

**`NO_ORIGINAL88_SAME_COLONY_25KM_AA_SITE_SOURCE_SUPPORT_BEFORE_Y`。** 独立AAデータを今回の439光学糞・冬ポリニヤ元サイト年へ直接校正/照合する道は、同じ採集地の支持が**0**で通らない。実測AA datasetは、[別問いの55 site×採集年のbulk vs Phe/TP](RESULT_FROZEN_ORIGINAL602094_BULK_PHE_TP_55_SITEYEAR_20261121_JA.md)の同一羽毛での測定解釈検証には有用だが、**冬ポリニヤ→食性変化の直接独立再現にはならない**。

正方向の帰無を外した後に見つかった旧439の負関連、原著R1000への置換での頑健性、358の直前冬vs翌冬差を変更しない。2013–2021のL8糞現年Yと現年糞分類も未確認。今後は**同じ場所で同年に採取された実糞/実血液/実AA**と地理情報の出所が必要で、既存AAを近傍へ恣意的に再割当てしない。

## 再現

- 凍結源：[2026-11-21 pre-distance site overlap rule](FROZEN_AA_OLD88_SOURCE_GEOGRAPHY_MATCH_ONLY_20261121_JA.md)
- 原data：Michelson et al 2026, USAP-DC [DOI10.15784/602094](https://doi.org/10.15784/602094)、Youngflesh元88 source site geography artifactと元860 source site-year keys。
- [実装](audit_original88_AA_2004_2010_source_geospatial_overlap_NO_Y.py)は公開元CSVと元2 artifactを別引数として供給し、数値 isotope outcome 未読で3固定距離しきい値を判定する。ローカル初回のsource-only距離出力6行および判定JSONを保存。原CSVをGitHubで再配布せず、`main`/凍結原稿を変更せず、PR214 draftのみ。
