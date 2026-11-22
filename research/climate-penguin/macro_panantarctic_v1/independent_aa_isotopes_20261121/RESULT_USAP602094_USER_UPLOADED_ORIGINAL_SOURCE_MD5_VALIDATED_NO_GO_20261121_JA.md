# USAP-DC 602094 真正2026年アデリー羽毛アミノ酸同位体データの実体監査：取得成功・ポリニヤとの独立検定はNO-GO

**2026-11-21追補：** 真正65個体の独立羽毛4指標を**55 Site×採集年・35原Siteラベル**へ集計した[bulk δ15N vs source-AA Phe / TPの測定解釈比較](RESULT_FROZEN_ORIGINAL602094_BULK_PHE_TP_55_SITEYEAR_20261121_JA.md)を新たに凍結・実行。35 Site丸ごと除外予測はPhe-only RMSE 0.869‰、TP-only 0.816‰、両指標 0.704‰。Phe vs TPの誤差差のsite bootstrap区間が0を含み、単独指標の優位は未確定。同Site複数年に限定すると両指標モデルでもwithin-site R²約6.3%。さらに[実際に元88地点と地理照合](RESULT_USAP602094_AA_FEATHERS_OLD88_REAL_SPATIAL_OVERLAP_NO_GO_20261121_JA.md)したところ、2004–10実AA4指標完全7標本/6 Site×採集年の最寄り距離は30.5–79.9km、25km以内の直接ペア**0/6**。これは別測定系の指標解釈検証と直接新年ポリニヤ追試を明確に区別する結果。

**2026-11-21 JST | PR #214 の別枝のみ | 実際のアップロードされたZIPをPythonで展開して検証 | 同位体・栄養段階の数値は未解析、環境ポリニヤの回帰なし。** 遡及的検証の時期・支持域を固定した事前契約 [`FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md`](FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md) に従った結果。

## 1. 取得問題は解決：公開原CSVのMD5に一致

ユーザー提供の原ZIP `usapdc_602094_download_20261121_011638.zip`、SHA256 **`185dca693aa9cef96019e379308fa999d6985e010f9ddd9358e706c69ff9b1ce`** を直接読み、ZIP CRC正常、内容物は次の元CSVのみ：

`usapdc_602094/Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv`

- 原CSV **39,736 bytes**、CRC32 **`8116e07d`**、SHA256 **`d9b24f994896130c6afed1c8359c9a8835f70b3cfb8bea40b54b3529f23b5cb9`**。
- **MD5 `f9a91c9d9bf3dba9607bf0767df8c206` — USAP-DCの公式配布原ファイルの公表チェックサムと完全一致。**
- 実 **108試料×45列**、`Sample_ID`は108すべて一意、種 `Pygoscelis adeliae`、`Sample_type=Breast feather` が全件一致。`Species`の元値は `Adelie penguin ` と末尾空白あり：照合時のトリムは識別子正規化であって種変更ではない。
- 原 `Region` は **Ross Sea 53個体、Antarctic Peninsula 55個体**。 `Specimen_type` は Museum study skin **79**、Live capture **27**、Molted feathers **2**。原 `Latitude`・`Longitude` は複数資料に由来する**45固有座標ペア**。Museumや地名由来の座標は直接の採餌位置ではない。
- `d15N`、`Phe_d15N`、`Glu_d15N`、`Trophic_position` の列が実在し、全108行で**少なくともフィールドの有無だけ**を検査した。同位体・TPの値、分布、群間差、ポリニヤとの関連は開封・検定していない。

以前の[公式API監査](RESULT_USAP602094_INDEPENDENT_AMINO_ACID_SOURCE_GATE_JA.md)は、APIがCSVでなくHTMLを返したため`NO_GO_USAP_SOURCE_DOWNLOAD_UNVERIFIED`だった。これは**解消**した。一方、新しい生態学的解析の標本支持条件は別問題である。

## 2. 事前固定した年に何件あるか — 元の採集年を使用

| 対象（元の`Year_collected`） | 原標本 | 原`Site`×**採集年** | 異なる原`Site` | 原`Region` |
|---|---:|---:|---:|---:|
| 全時代（1841–2016） | 108 | 74 | 41（表記の末尾空白を含む元値） | 2 |
| 現代採集年2000–2016 | **36** | **22** | 12 | 2 |
| 固定窓2004–2010 **または**2013–2016 | **25** | **15** | 8 | 2 |
| 同窓内でbulk δ15N＋Phe δ15N＋Glu δ15N＋TPの**4値すべてが実測値として収録** | **10** | **9** | **5** | **2** |

固定窓の元標本25に対し、bulkは17行、Pheは13行、Gluは13行、TPは13行に値がある。**4指標共通の完全データ**は10行/9地点×採集年。該当するのは **COPA（2006,07,08）、Cape Crozier（2004,05,2013）、Gourdin Island（2015）、Heroina Island（2015）、Ross Island（2009）** の5地点。元の胸羽標本年は**必ずしも形成年ではなく、同地点の採食行動を観測した年でもない**。年だけで実際の食性やその前年冬ポリニヤへ直結できない。

※元`Area`にはVictoria Land、Western/Eastern Antarctic Peninsulaなどのサブ地域ラベルがある。しかし、`Region`にはRoss SeaとAntarctic Peninsulaの2つしかなく、`Area`を事後的に「3つ以上の独立海洋生態地域」と読み替えて事前ゲートを通さない。

## 3. 定義済みゲート判定

事前凍結の必要条件のうち：

1. **20以上のsite×真の羽毛形成年（同位体3軸共通）**：実際は最大9のsite×**採集年**なので**不合格**。
2. **5以上の地点**：原`Site`ラベル5で、数だけは満たす。ただし実際の精密な繁殖地点同一性は未保証。
3. **3以上の独立広域海洋地域**：元`Region`は2、**不合格**。
4. **羽毛成長・換羽時期を一意に先行冬へ対応**：`Year_collected`しかなく`moult_year`/発生月・羽毛形成年なし、**不合格**。
5. **同じ地点に最低2形成年×3地点**：今回の完全な9地点×採集年のうち2年以上あるのはCOPAとCape Crozierの2地点のみ（**不合格**）。
6. **その真正羽毛形成冬について同じDEEP-AA100 km源データの月別有効海面率**：まだ照合していない。成立したと仮定しない。

**結論：`NO_GO_INDEPENDENT_TP_POLYNYA_IDENTIFICATION_SOURCE_TEMPORAL_AND_REGION_SUPPORT`**。事前固定した必要条件が複数不足するため、原CSVの新TP/phenylalanine δ15Nをポリニヤに結合して回帰・有意性を計算してはならない。これは「生態学的効果が0」の実証ではない。

## 4. 研究主線への帰結

- 光学推定δ15Nは海洋の同位体基準値・糞の被覆・水分・青/緑の反射率などによっても変わりうる。元439地点×季節のポリニヤ負関連と元358地点×季節の時間特異性は、元著者1000係数のPLSR再解析でも負。だが、それらは**旧同じ糞画像から作った光学Y**であり、2026年AA羽毛データによる新しい基線／TPの再現は得ていない。
- 新公開AA原データ自体は**長期の窒素同位体基線と栄養段階を歴史対現代で比較するための有力な独立ソース**である。しかし古標本と新標本で場所・年・試料収集形態が違う可能性があり、単純な年代差を温暖化の因果効果とはしない。この論文の元ポリニヤ負関連の事後追認として使わない。
- 独立の実胃内容物Signy14季節のポリニヤ関連は不確実、OC-CCI chlorophyllでの経路も未確立。今回の入力でこれらの既存の判定は変わらない。

## 5. 再現性と保存範囲

本監査は**公開ZIP/CSVのMD5・SHA256・CRCと原CSV 108×45列を実際に確認した**。元標本の数値同位体の配布は行わず、独立した`Site×Year_collected`の**メタデータのみ**を出力して再現性を確保した。解析スクリプトはユーザー提供ZIPの正確なパスを入力とする。`main`・v0.5/v0.6・Ecology Report・Paper2には一切変更しない。
