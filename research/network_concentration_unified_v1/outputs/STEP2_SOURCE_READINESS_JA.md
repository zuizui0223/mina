# Step 2: 共変量の結合可能性（結果ではなくデータ入力監査）

Step 1 の計数帰無を再実行せず、確定済みの共通表から検定候補のキーを作成した。
対象はマクロ主解析のみ。島内行、皇帝モデル平均は加算していない。

- 主表 675 行／396 ネットワーク／20 種（JNCC 663、MAPPPD 12）。
- 種ペア 378 行／90 ネットワーク（JNCC 373、MAPPPD 5）。
- OISST v2.1 の **年月範囲だけ**を満たす候補: 主表 669/675、種ペア 376/378。
- 同じ定義の数値固執率を原資料で検証した種: 0/20。
- 同じSSTを位置・年月・格子・出典まで検証して結合した行: 1029/1053。
- 入力条件を満たす行: H2 0、H3 656、H4D 373、H4W 373。

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

- 時間範囲の一致はSSTの結合成功を意味しない。元のSite.ID／MAPPPD地点の座標を原出典から再取得し、海洋セル・沿岸マスク・季節・端点年の一致を別途検証する。
- 英国JNCCの水温入力は既存の南極GLORYS thetao（約0.494m深）または南極に限定されたCMIP6 tosから代用しない。両者の物理定義・期間・空間支持が違う。
- NOAA OISST v2.1 (月次0.25°、1981年9月以降) は今後の取得候補。公式案内: https://www.ncei.noaa.gov/products/optimum-interpolation-sst 。同一変数の採用と月別・空間規則はモデルを当てる前に固定する。
- H2は成鳥の翌繁殖機会の同じ繁殖地への条件付き固執率が必要。帰還率、個体の生存率、出生地への帰還、定性評価を代用しない。種が20あってもネットワーク675行を独立20種以上の形質反復と誤認しない。
- H4Dの予定モデルにもWが必要なので、W欠測行をSSTなしモデルへすり替えて検定しない。378ペアは90ネットワークに由来し、同じ種・元計数を共有する。
- ここでのreadyは **データ入力条件のみ**。対象数、解析エンジン、共有計数による依存と不確実性はStep 3の凍結が必要。H2～H4の推定値、p値、支持判定は出していない。

自動生成: audit_step2_readiness.py／入力共通表のSHA256はSTEP2_SOURCE_READINESS.json。
入力用テンプレートは既存の場合上書きしない。出典と原定義の検証が済むまで数値は埋めず、欠測として保存する。
