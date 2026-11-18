# 南極ペンギン・マクロ生態学：主張する肯定結果（main採用台帳）
    
**2026年11月18日／選択的統合。** これは既存の `mina/main` が採用する**原データ照合済みの肯定的結果と、その推論の上限**を明記した結果台帳です。v0.6草稿全体、PR #214、未確定の解析を丸ごとmainへマージしたわけではありません。凍結済みEcology Report・Paper 2・既存main成果物は不変更。区分は「物理的な観測」「実巣数の記述」「条件付きの探索的生物相関」「選定気候モデルの物理予測」です。

## 中心命題

> **南極の海洋環境は温度–海氷だけでなく塩分という別の変動軸を持ち、アデリーペンギンのδ¹⁵N光学指標は塩分とも条件付きで正に関連する。実巣数の空間再配分と種構成の変化も確認でき、将来の海氷減少と低塩分化は広く予測されるが、その空間的な連動はモデルで異なる。**

これは**複数の異なる観測・物理結果を結ぶ論文上の主張**であって、温暖化→塩分→餌→繁殖という一本の因果経路を証明するものではありません。

## mainで主張する肯定結果

| 種類 | 肯定結果 | 真の比較単位・大きさ | 主張の上限 |
|---|---|---|---|
| **海洋物理の二軸性** | 温度–海氷PC1が分散**60.3654%**、塩分主体PC2が**33.3773%** | 原海洋588地点×28年＝16,464地点年、**378原海洋wet grid**、18地域 | PCAの直交性は独立した原因を証明しない |
| **塩分×アデリーδ¹⁵N** | 海氷・海水温・画像日・地点・地域×季節を調整しても**β=+0.8341‰/塩分単位**、追加残差R² **2.880%** | 元Landsat**860地点×季節、88地点、82海洋格子、13地域**。格子クラスタ区間**[+0.389,+1.280]** | **肯定的な探索相関**。地域クラスタ保守区間**[−0.016,+1.684]**は0を含み、地域間で係数の符号が異なる |
| **既知アデリー繁殖地間の巣数再配分** | 固定した繁殖地の巣数重み付き位置が**南へ+107.31/+88.41/+99.60km** | 19/26/35地点の**入れ子ロスター**、1990年代対2010年代。巣数重みの近岸SIC差は**+0.022/+0.625/+0.908 pp** | 個体の移動・繁殖地新設・海氷ニッチ追従ではない |
| **局所2種の繁殖構成** | 厳格な同出典・同方法の6地点すべてで**ジェンツー/アデリー巣数比が増加（6/6）**。同じ2種の観測巣数合計は**5/6地点で増加** | 真の6繁殖地、**2原地域**。アデリーの対数巣数傾き6/6負、ジェンツー6/6正 | 相対構成の変化は群集合計の減少や種間競争を意味しない |
| **将来の海氷と低塩分化の物理曝露** | SSP5-8.5・2081–2100、選定3CMIP6モデル全てで塩分低下**464/595**、海氷減少も一致**384/595**。現在の実計数巣数中央値重みでは、低塩分化地点**93.54%**、両方一致地点**59.08%** | 元595既知site／2011–2020年に実巣数のある271site、3気候モデル×2SSP×2未来期 | 予測したのは**物理的な変化**。巣数が将来減少する割合ではない |

将来の物理関係の追加肯定結果：同じSSP5-8.5世紀末に、3モデルの**Δ海氷–Δ塩分の地点間相関**は **ACCESS-CM2 +0.743、BCC-CSM2-MR −0.296、CESM2 −0.333**。つまりモデル平均で低塩分化していても、海氷減少と塩分変化がどこで強く同時に起きるかは一様ではない。

### 塩分の肯定的関連を消さずに限定する

塩分–光学δ¹⁵Nの正相関は**実際に計算・再現された**。未同定なのは「魚食割合が塩分によって変わった」という**機構**である。

- 塩分係数はVictoria Land/Wilkes Landで正、南西南極半島で負、北東半島でほぼ0。共調査が実際にある4地域に限定するとβは+0.080に減弱する。別母集団への地理転写は確立しない。
- **翌年の塩分**もδ¹⁵Nと逆向きに関連する時間負対照が出た（同じ721系列でβ≈−0.653）。当年係数の因果方向は識別できない。
- 同年同場所のPOM同位体基準値は100 km以内で**20/860地点×季節**のみ。δ¹⁵Nの変化を魚食率と呼ばない。
- 同じsource地点・季節のアデリー実巣数との重複は70件だが、反復年のある地点は8地点・29件。巣数への関係は不確実で、独立地域へは一般化できない。

この限定を含んだ**肯定的生物相関**として採用する。旧265系列の未再現係数や、未来CMIP6の塩分差に過去のδ¹⁵N係数を掛けた餌・巣数予報は採用しない。

## 観測期間とsourceを混ぜない

- 物理PCA・巣数再配分の近岸SIC：**8〜11月**。GLORYS海水温・塩分の主解析は1993–2020。
- δ¹⁵Nの衛星由来相関：**11月〜翌2月**の元NSIDC SIC（約150 km）とGLORYS水温・塩分、主データ1996および1999–2012の原繁殖季節。
- 将来CMIP6：**8〜11月**。参照期1995–2014、将来2041–2060/2081–2100。CMIP6 `tas` は大気温であり、過去のGLORYS `thetao` は海水温。これらを置換して未来の食性・繁殖を予測しない。

## 主張に入れないもの

「塩分が魚/オキアミ切替を引き起こした」「南極全域で一律に塩分が効く」「アデリー個体が南へ移住した」「ジェンツーが競争で他種を排除した」「2030–2100年の巣数・局所絶滅を予報できる」「検証できなかった旧265系列の気候係数でCMIP6人口予報をした」は、このmain採用台帳には含めない。

## 原本・再現根拠

全数値は [Draft PR #214](https://github.com/zuizui0223/mina/pull/214) 上で原sourceから再計算した。対応する原文書と成功CI：
  
- [海洋588地点二軸（原本結果）](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/DUAL_MARINE_AXIS_PENGUIN_RESPONSE_RESULT_JA_20261111.md) / [原source ocean workflow #42961084667](https://github.com/zuizui0223/mina/actions/runs/42961084667)。
- [塩分–δ¹⁵Nの探索的肯定結果](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/diet_salinity_source_20261117/SAME_SEASON_ISOTOPE_SALINITY_EXPLORATORY_RESULT_JA_20261117.md) / [原本固定CI #44083346932](https://github.com/zuizui0223/mina/actions/runs/44083346932)。
- [実際に固定されたAdélieロスター元CSV](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/latitudinal_scale_20261115/adelie_latitude_nesting_scale_3rosters_summary.csv) / [厳格6組の原source種間巣数](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/strict_pair_20261115/REPLACEMENT_VS_COMMUNITY_TOTAL_JA_20261115.md)。
- [全595既知地点の3モデル将来海氷＋塩分](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/climate_risk_frozen_20261116/JOINT_FUTURE_ICE_FRESHENING_AND_ISOTOPE_SOURCE_GEOGRAPHY_RESULT_JA_20261118.md) / [CI #44238218203](https://github.com/zuizui0223/mina/actions/runs/44238218203)。
- [将来モデルごとの海氷×塩分空間関係](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/climate_risk_frozen_20261116/CMIP6_FUTURE_SIC_SOS_SPATIAL_DECOUPLING_HISTORICAL_LOCAL_SOURCE_RESULT_20261118_JA.md) / [CI #44244226558](https://github.com/zuizui0223/mina/actions/runs/44244226558)。

**採用範囲：** 上記の科学的結果・推論範囲の台帳のみ。本体のv0.6原稿（約5,000語）・図4枚・410以上の探索ファイルはこのコミットに含めない。必要な本文・図は独立にレビューしてから別PRで扱う。投稿済み、確証的因果、または研究データDOIの発行は主張しない。
