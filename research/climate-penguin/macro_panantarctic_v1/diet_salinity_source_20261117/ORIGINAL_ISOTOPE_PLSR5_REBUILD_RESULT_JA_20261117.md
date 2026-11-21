# 南極アデリー食性 proxy：Youngflesh 2026 著者公開Landsatと原標本からPLSR5を実再構成

**2026-11-17 / mina Draft PR #214 / source-preserving exploration; original biological outcome and model diagnostics are distinct.**

## 新しく実行し、成功したもの

[GitHub Actions #44078492773](https://github.com/zuizui0223/mina/actions/runs/44078492773) **SUCCESS**。Zenodo original [10.5281/zenodo.17409948](https://doi.org/10.5281/zenodo.17409948) の `data.zip` (256,425,816 bytes、MD5 `e29a2f68c84e3a515044d554540def2f`) を再取得し、オリジナル `L1/SIA_spectra.csv` と3センサーのRSR.xlsx、`L0/Landsat/landsat_reflectance_L457-2025-07-16.rds` を抽出した。RDSのベクトル画素行、各センサーの原RSRを350–2500nmで校正し、6バンドに畳み込んだ103校正実標本のδ15Nを5成分PLSRで推定。Python scikit-learn `PLSRegression(scale=False)` 再実装は原著R `pls::plsr(..., method=oscorespls)` と同一実装では**ない**。出版社によるオリジナル完成Stan `DI_df.rds` posteriorはまだ復元していない。

元原画像RDS **179,462 画素 / 146 sites / 1,410 site×season / 4,038 site×day**。原著 `Scripts/4-diet-est.R` と同じ `n_pix` を各画素に割り当て、そのsiteで `mean(n_pix)>=2` として再計算すると **119 sites, 179,346 pixels, 3,938 site×day**。これは同原著コードのコメント（119,179346,3938）と全3項目**完全一致**。1,410 site×seasonのraw 1,410について `L0` RDS源の画素数とPLSR入出力のsource集計は一対一一致。画像日同等重みと画素数重みを明示的に別列にした。

## 校正スペクトルの内部予測性能（外部生態検定ではない）

δ15N=103 original samples。各センサーで元原著と同じ**5成分**に固定し、δ15N階級別の65%学習/35%留保を固定seedで100回再標本化した。比較相手は**学習標本のδ15N平均**を検証標本に予測する無情報ベースライン。原研究の独立leave-colony-outや最終Stan posterior検証ではない。

| センサー | 100留保の中央値RMSE（δ15N ‰） | 学習標本平均帰無RMSE | 帰無に対する記述的低下率 |
|---|---:|---:|---:|
| Landsat 4 | **1.722** | 2.295 | 25.0% |
| Landsat 5 | **1.741** | 2.355 | 26.1% |
| Landsat 7 | **1.742** | 2.354 | 26.0% |

100回の留保は同じ103 lab source sampleを何度も分割したもの。100独立した生態学的追試や将来巣数予報ではない。分光データとペンギン餌種の組成を混同しない。

## 元地理でのsource matchingと効果を検定できる分母

前段の元Landsat地点重心 (EPSG:3031) に対し、595原MAPPPDサイトとのID一致・一意な最近接距離<=2km・元GLORYS海洋格子を同時に要求した raw source crosswalk は **892 site×season, 99 sites, 92 wet cells, 14 regions**。

上記**原著平均画素数フィルターを追加すると** **860 site×season, 88 sites, 82 original marine wet cells, 13 regions**。独立地域の反復は依然薄く、Central-west Antarctic Peninsula及びSouth Shetlandsは**それぞれsource site-season 1件**である。沿岸物理セルやsite×seasonを独立実験として数えない。

Source panel: original RDS image years 1984–2012 start seasons. Source isotope day-equal meanの推定変化は測定値ではなく、image reflectancesからの **proxy**。元PLSR 103 lab calibrationのCV分散も最終Stan uncertaintyとは異なる。原著と無関係な2090年代環境を代入しない。

## 次の検定を進めるための条件

1. Original GLORYS **11〜翌2月** の各wet cell表層塩分・水温を同源0.083°202311製品から取得、11–翌2月の元NSIDC SIC **150km** と本当の期間を一致させる。既存8–11月SIC 100kmを勝手に同一曝露と呼ばない。
2. 元の作者と同じ分散構造を持つ `DI_df.rds` はZenodo原ZIPに**含まれない**。本PLSR再構成は食性proxy探索の条件付き候補であり、`δ15N=魚食率`と変換しない。Stan4本体の事後モデルを計算しない限り original diet indexを得たと述べない。
3. 環境データと860の観測機会が結合でき、地域の独立な条件付き変化が存在するときにのみSIC＋水温＋塩分の増分比較へ進む。地域一つでしか信号がない、時間で交絡、元物理格子重複が厳しい場合、結果はsource-limited としてNO GOを維持する。

## 実行・成果物

- 元Zenodo MD5確認 [#44075244428](https://github.com/zuizui0223/mina/actions/runs/44075244428)、後続のLandsat RDS原本版図層 [#44076012021](https://github.com/zuizui0223/mina/actions/runs/44076012021)（いずれも成功）
- 原PLSR再構成 [workflow成功 #44078492773](https://github.com/zuizui0223/mina/actions/runs/44078492773)；artifact **14326122826** （モデル留保100回×3センサー、全1,410地点×季のδ15N proxy、4,038地点×日、検証受領JSON）
- 実装：[`reconstruct_isotope_proxy.py`](reconstruct_isotope_proxy.py) ; 旧source gate [`probe_zenodo_diet_source.py`](probe_zenodo_diet_source.py)
- Strict re-filter & join QA成果物は会話に提供した派生CSVと独立計算コードに保存。原Zenodo生ZIPをGitHubへ再配布していない。

**Scientific disposition:** the actual isotope source reconstruction is a source reproducibility result. It is **NOT** a measured new diet–salinity association, prey-fraction change, causal climate response, transferable Antarctic-wide warming effect, or penguin abundance forecast. Frozen Paper 1/2 and main v0.5 figures unchanged.
