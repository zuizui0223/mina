# CMIP6 将来環境モデルの条件付き投影 v1

作成日: 2026-10-30。植生やペンギンの将来個体数を予測する前の、環境側の実データ抽出である。

## 実行結果

公開GCSにある **3モデル・27 Zarr store** から、固定106座標について **381,600件の月次地点値**を実際に読み、4,770件の20年季節平均と3,816件の過去基準との差を作成した。各地点のモデル集計1,272行すべてに3モデルがそろう。読み込み失敗、選択された月次値の欠測、20年期間の不完全な年はなかった。同じモデルセルに対応する地点を含むため、381,600件は独立した観測数ではない。

モデルは値を見る前に、tas(Amon)、sos(Omon)、siconc(SImon)の3変数とhistorical、ssp245、ssp585の3実験が同一memberでそろう候補から、source_idのASCII昇順で最初の3つを固定した。各モデルではr/i/p/fの数値順で最小のmember、実験間共通のnative格子gn、カタログ内の最新versionを使った。候補表と採用27 storeの完全なURLを保存した。

| モデル | member | 気温のユニークセル | 海氷・塩分それぞれのユニークセル |
| --- | --- | ---: | ---: |
| ACCESS-CM2 | r1i1p1f1 | 28 | 39 |
| BCC-CSM2-MR | r1i1p1f1 | 32 | 31 |
| CESM2 | r4i1p1f1 | 36 | 32 |

この3モデルは利用可能性で選んだ小規模集合であり、CMIP6全体を代表する確率標本ではない。

## 集計方法と位置の扱い

基準は **1995–2014年**、未来は **2041–2060年、2081–2100年**。すべて **8–11月**で統一した。各年の4か月をモデル暦の月日数で重み付けし、20年間を等重みで平均した。cftimeでproleptic_gregorian、noleap、365_dayを保持しており、pandasの通常暦へ強制変換していない。360_day暦も単体テストで確認した。

各変数でhistoricalの最近傍セルを固定し、将来も同じindexを使った。過去と未来の座標配列を絶対誤差1e-6度で比較し、scenarioのparent_variant_labelが選定したhistorical memberに一致することを確認した。海氷と塩分は1995年8月・11月の両方で有限値を持つセルを海洋側の有効候補とし、0%の海氷セルは残した。これはモデルの欠測maskを使う方法で、実測海岸線による陸海判定ではない。気温は大気最近傍セルで、陸面率のfilterは適用していないため、小島の陸地や微気候を表す保証はない。

106地点から対応する海洋セル中心までの測地距離は、ACCESSで中央値24.6 km／最大96.3 km、BCCで36.3／111.3 km、CESMで28.0／84.8 kmだった。この距離は**地点からモデルセルへのずれ**であり、実海岸線からの離岸距離ではない。50 kmを超える地点をCSVでflagし、同一セルを共有する地点数を記録した。

実配列の単位はtasがK、siconcが%、sosが0.001だった。気温だけ℃へ変換した。海氷の変化は相対減少率ではなく **percentage points**。塩分は出典に記載された0.001尺度を保持し、現地海水の測定値と同じとみなしていない。

## Palmer周辺の参考値

座標box（緯度−65.0〜−64.5、経度−64.5〜−63.5）を値の読込前に定義した。106地点中、このboxに入るのは **BISC、LITC、DAMOの3地点**であり、Palmer五島すべてを直接代表する表ではない。海氷・塩分は各モデルで1セルを共有し、気温はACCESS/BCCで2セル、CESMで1セル。モデル内では重複セルを除いて平均し、その後に3モデルを等重みで集計した。

以下は1995–2014年基準との差。括りの範囲は3モデルの最小～最大で、信頼区間・確率区間ではない。

| 変数 | シナリオ | 期間 | 3モデル平均変化 | モデル最小～最大 |
| --- | --- | --- | ---: | ---: |
| 気温 (℃) | SSP245 | 2041-2060 | +1.86 | +1.32 ～ +2.35 |
| 気温 (℃) | SSP245 | 2081-2100 | +2.92 | +1.75 ～ +4.73 |
| 気温 (℃) | SSP585 | 2041-2060 | +2.14 | +1.48 ～ +2.73 |
| 気温 (℃) | SSP585 | 2081-2100 | +4.92 | +3.30 ～ +7.54 |
| 海氷濃度 (percentage points) | SSP245 | 2041-2060 | -16.00 | -29.17 ～ -0.29 |
| 海氷濃度 (percentage points) | SSP245 | 2081-2100 | -45.35 | -92.58 ～ -14.74 |
| 海氷濃度 (percentage points) | SSP585 | 2041-2060 | -20.66 | -30.68 ～ -2.26 |
| 海氷濃度 (percentage points) | SSP585 | 2081-2100 | -59.34 | -93.03 ～ -29.28 |
| 表層塩分 (0.001) | SSP245 | 2041-2060 | -0.080 | -0.253 ～ +0.160 |
| 表層塩分 (0.001) | SSP245 | 2081-2100 | -0.212 | -0.658 ～ +0.136 |
| 表層塩分 (0.001) | SSP585 | 2041-2060 | -0.125 | -0.340 ～ +0.165 |
| 表層塩分 (0.001) | SSP585 | 2081-2100 | -0.384 | -0.949 ～ +0.062 |

このPalmer周辺boxでは、気温上昇と海氷減少の符号は3モデルで一致した。表層塩分はACCESS/CESMが減少、BCCが増加し、淡水化の符号は一致しなかった。特に海氷のhistorical平均そのものがACCESS 76.57%、BCC 29.28%、CESM 93.03%と大きく異なる。モデル平均だけで現地の将来海氷を精密に述べることはできない。BCCのSSP245気温変化が世紀半ばより末期で小さい点もそのまま残しており、シナリオを単調な年々予測には置き換えていない。

## 解釈と次工程

これは**将来環境モデルの条件付き投影**である。観測に基づく温暖化の検出・原因帰属、植生変化予測、海氷漂流予測、ペンギンの繁殖成功や個体数予測ではない。1 member／モデルなので内部変動の分布も評価していない。最近傍の粗いセル値に局所的downscalingやbias correctionは適用していない。

生物応答に接続するには、まず観測期間内で環境と植生・個体数の時間対応をそろえ、場所内の関係、共有環境セルによる依存、観測範囲外への外挿を検証する必要がある。将来投影に使う応答モデルは時系列を守った予測検証に通す。塩分と植生の関係を今回のCMIP6値だけから補完してはならない。

## 検証と再現

暦の重み、360_day、欠けた月、欠測セル、海氷fraction/%、海氷範囲外、気温・塩分単位、海洋maskと日付変更線、同member選択の10テストを、実装前の失敗確認後に通した。出力を独立に読み直して20年完全性・全3モデル・差分計算・親memberを確認し、月次CSVから別計算した季節平均が1e-10以内で一致した。

独立レビューで再実行時のcache識別を補強した。出典URL/version、格子座標配列、地点CSV、期間・月、コード、暦・単位などのmetadata、さらに実際のhistorical選択セルとその入力identityをSHA256で結びつけ、ファイル名とsidecarの両方で一致を要求する。historicalのmaskやstoreだけが更新された場合もfuture cacheを再利用しない。衝突を防ぐ10ケースを追加し、合計20テストが通過した。修正版で27 storeを再読込し、4,770季節平均・3,816差分・1,272モデル集計が元のfresh取得結果と1e-12以内で全行一致した。

実行入口: `research/climate-penguin/work/cmip6_projection_v1/extract.py`。依存バージョン: 同ディレクトリの`requirements.txt`。xarray 2026.9とZarr 2の非互換を確認したため、実測に用いたxarrayは2025.6.1に固定してある。再実行はcatalogと圧縮された地点月次cacheを再利用できる。

主な成果物は `site_model_changes.csv`（モデルごとの変化）、`site_model_ensemble.csv`（各地点のモデル集合）、`seasonal_climatologies.csv`（基準・未来の絶対値）、`coastal_grid_support.csv`（距離と共有セル）、`source_metadata.json`（単位・暦・tracking_id・license）、`manifest.json`、`validation.json`。`monthly_*.csv.gz`に読み取った月次値を保存した。独立した地点として重み付けしない集計は`model_unique_cell_summary.csv`にある。

## 一次資料

- [Pangeo / ESGF: CMIP6 Zarr公開データ、カタログ、QCの説明](https://pangeo-data.github.io/pangeo-cmip6-cloud/overview.html)
- [取得したGCSカタログ](https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv)
- [WCRP-CMIP: CMIP6実験IDとssp245/ssp585の定義](https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html)
- [PCMDI CMOR: SImon、siconcは海氷面積割合%](https://github.com/PCMDI/cmip6-cmor-tables/blob/main/Tables/CMIP6_SImon.json)
- [PCMDI CMOR: Omon、海洋表層塩分sos](https://github.com/PCMDI/cmip6-cmor-tables/blob/main/Tables/CMIP6_Omon.json)
- [Pangeo / ESGF: 原データ引用とlicense](https://pangeo-data.github.io/pangeo-cmip6-cloud/licensing_citation.html)

個別モデルデータの原URL・version・tracking_id・licenseは採用store表とsource_metadata.jsonで追跡できる。
