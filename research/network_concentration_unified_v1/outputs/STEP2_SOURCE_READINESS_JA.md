# Step 2: 共変量の結合可能性（結果ではなくデータ入力監査）

Step 1 の計数帰無を再実行せず、確定済みの共通表から検定候補のキーを作成した。
対象はマクロ主解析のみ。島内行、皇帝モデル平均は加算していない。

- 主表 675 行／396 ネットワーク／20 種（JNCC 663、MAPPPD 12）。
- 種ペア 378 行／90 ネットワーク（JNCC 373、MAPPPD 5）。
- OISST v2.1 の **年月範囲だけ**を満たす候補: 主表 669/675、種ペア 376/378。
- 同じ定義の数値固執率を原資料で検証した種: 0/20。
- 同じSSTを位置・年月・格子・出典まで検証して結合した行: 1038/1053。
- 入力条件を満たす行: H2 0、H3 662、H4D 376、H4W 376。

## OISST時系列範囲に入らない行（欠測で保持）

- 主表 MAPPPD::Elephant Island / CHPE (1970–2019)
- 主表 MAPPPD::Central-west Antarctic Peninsula / ADPE (1979–1986)
- 主表 MAPPPD::Wilkes Land / ADPE (1961–1989)
- 主表 MAPPPD::South Shetland Islands / GEPE (1979–2002)
- 主表 MAPPPD::South Shetland Islands / CHPE (1977–2015)
- 主表 MAPPPD::South Shetland Islands / ADPE (1980–2018)
- 種ペア MAPPPD::South Shetland Islands / ADPE×GEPE (1980–2012)
- 種ペア MAPPPD::South Shetland Islands / CHPE×GEPE (1979–1996)

## 重要な判定境界

- 時間範囲のみではSST結合成功を意味しない。本表のverified行は元のSite.ID／MAPPPD地点座標から両時点の海洋SSTへ結合し、各原構成単位の同じ海洋セル（50 km以内）と6か月分の有効値を要求した。
- 英国JNCCの水温入力は既存の南極GLORYS thetao（約0.494m深）または南極に限定されたCMIP6 tosから代用しない。両者の物理定義・期間・空間支持が違う。
- NOAA OISST v2.1 (月次0.25°、1981年9月以降) を英国JNCCは3–5月、南極MAPPPDは9–11月で原センサス年へ実際に照合した。取得したNetCDFのURL/SHAは STEP2_OISST_UK_JOIN.json と STEP2_OISST_SOUTH_JOIN.json に記録。公式出典: https://www.ncei.noaa.gov/products/optimum-interpolation-sst 。南極の配信経路は同一OISSTのNOAA ERDDAPを使用した。
- H2は成鳥の翌繁殖機会の同じ繁殖地への条件付き固執率が必要。帰還率、個体の生存率、出生地への帰還、定性評価を代用しない。種が20あってもネットワーク675行を独立20種以上の形質反復と誤認しない。
- H4Dの予定モデルにもWが必要なので、W欠測行をSSTなしモデルへすり替えて検定しない。378ペアは90ネットワークに由来し、同じ種・元計数を共有する。
- ここでのreadyは **データ入力条件のみ**。対象数、解析エンジン、共有計数による依存と不確実性はStep 3の凍結が必要。H2～H4の推定値、p値、支持判定は出していない。

自動生成: audit_step2_readiness.py／入力共通表のSHA256はSTEP2_SOURCE_READINESS.json。
形質の入力テンプレートは既存の場合上書きしない。固執率の定義が確認できるまでFはNAのまま。SSTは原本確認済みの行だけ記入済みで、未適格行の気温値を推測・代入していない。


## 計算済みSST差の記述値（生態学的関連検定ではない）

- 集中の主表・JNCC: 656行／383ネットワーク、SST差中央値 +0.0284 °C/10年、正 354行、負 302行。
- 集中の主表・MAPPPD: 6行／4ネットワーク、SST差中央値 -0.0152 °C/10年、正 0行、負 6行。
- 種ペア・JNCC: 373行／88ネットワーク、SST差中央値 +0.2548 °C/10年、正 214行、負 159行。
- 種ペア・MAPPPD: 3行／2ネットワーク、SST差中央値 -0.3286 °C/10年、正 0行、負 3行。

- 季節・調査年・対象地域が違うため、JNCCとMAPPPDの記述値の差を温暖化の因果効果や種差とみなさない。SST差はH3/H4Wの**説明変数**であり、集中／重なりの仮説支持ではない。
- 両地域の同じNOAA OISST製品を用いたが、同じ月ではなくそれぞれ繁殖期に対応した北半球3–5月／南半球9–11月を事前固定した。