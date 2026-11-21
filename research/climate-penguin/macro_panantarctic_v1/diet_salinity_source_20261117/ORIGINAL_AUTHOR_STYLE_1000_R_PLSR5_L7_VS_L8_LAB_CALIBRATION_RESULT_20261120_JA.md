# 元Youngflesh 2026と同じR 1,000反復PLSR5によるL7とL8の検証：L8の新センサー較正は通過

**2026-11-20 JST | mina Draft PR #214 | 実行完了 | original103 guano laboratory only; 2013–21実L8衛星の光学δ¹⁵Nをまだ計算しない。** 原著の処理済み糞画像データと新しい実糞・非糞画素の区別を崩さない。

## 判定

**`PASS_L8_ORIGINAL_R_1000_ENSEMBLE_SOURCE_ONLY_LAB_CV`**。元著者の公開 [`Scripts/2-PLSR.R`](https://github.com/caseyyoungflesh/penguin_diet_from_space/blob/4ab7c992fc2232b7905af0d1aa949d88dc9561ea/Scripts/2-PLSR.R) の真の較正仕様を使い、同じ103糞標本を使ってL7 ETM+と新しいL8 OLIを同じ1,000 train/test分割で比較した。公開データ元Zenodo [17409948](https://doi.org/10.5281/zenodo.17409948) の本体 `data.zip` は256,425,816 bytes、著者公開MD5 `e29a2f68c84e3a515044d554540def2f`、個別の元 `L1/SIA_spectra.csv` SHA256 `e6822e390a763d6b991819046b8a642fe24f412fe92efdef7a8822e198553d23` と元 `L0/RSR/L7_ETM_RSR.xlsx` SHA256 `b075f8ff6ff8fb894d45c0a2979486a77878e453e7788dc671457d3f9bc0ceee` を照合済。分光L8 6バンドの外部 EUMETSAT/NASA-based OLI RSRのsource SHAも個別に検証。

**実行結果：GitHub Actions [#44676042238 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44676042238)**、artifact **14602063283**, ZIP **sha256:`ac1199ad312df63173f7be73452ccbb5e01b7c55f29d3413ede63e1a1b665669`**。本体はレシートJSON＋ L7/L8 各**1,000行**の真のCV係数CSVと実留保RMSE CSV。GitHub結果を別のPython ZIP/CRC/係数数/スコア中央値確認で読み直し、全て一致。

### 元R手法そのものにそろえた固定計算

- 元103の真の糞実測 `d_15N` とlab波長350–2,500nmを、**それぞれ本来の6-band sensor spectral response** で畳み込む。L7とL8は異なる実物のresponse curvesで、L7の係数を未校正でL8へ移していない。
- `pls.options(plsralg="oscorespls")`、`pls::plsr(..., ncomp=6, scale=FALSE, validation="none")`、**5成分のcoefficient/prediction**、原著の`set.seed(1)`から5同位体分位階級内で**65% train / 35% holdout**、各**1,000回**。2センサーに共通の1,000個の原103行ID train/test分割。
- 元著者と同じRによる1,000組の7列係数（切片＋6bands）を保存。独立の固定新L8用ensembleは、L8 OLI元103標本のlab-only calibration成果として利用可能。新しい同位体Yを使って係数を選択・調整していない。

| 元103糞実標本・同じ1,000訓練検証分割 | L7 ETM+ | L8 OLI |
|---|---:|---:|
| 保留標本RMSEの中央値（‰、小が良） | **1.739038** | **1.741775** |
| 学習標本平均だけのnull RMSE中央値（‰） | 2.325794 | 2.325794 |
| 1,000分割のうちモデルがnullより良い割合 | 99.9% | 99.8% |
| 較正係数モデル数 | 1,000 | 1,000 |

同一分割での `L8 RMSE − L7 RMSE` の中央値 **+0.003419‰**、各分割差の5–95%分位点 **[−0.08231,+0.14228]‰**。これら1,000分割は同一103実標本を繰り返し使う**条件付き感度で、1,000独立地点の95% CIや野外データへの新しい転写検定ではない**。L8の検証誤差は原L7と事実上同程度だが、5%分位区間で優劣が厳密確定したとは言わない。

### 実行・トラブル履歴

1. 最初のsource R実装が `pls::coef` を呼んで停止（R `coef` genericは`pls`名前空間からexportされない）。原著と同じ S3 `stats::coef` へ修正。データ、5成分、seed、1,000分割、判断基準は一切変更なし。
2. 毎回256 MB原ZIPを繰り返し取っていたsource取得を、**元原刊行ZIPのHTTP Rangeで必要な103 lab CSV+L7 RSR XLSXだけ取得し、以前の元アーカイブ全MD5照合から確定していたSHA256を各個別ファイルで再照合**する方法に変更。元source生態Y、波長、L7/8分光値は無変更。原出版ZIP全体を現在再MD5したとは主張せず、公開記録の全MD5メタデータと個別構成ファイルの真source SHAを区別。
3. 最終CI [#44676042238](https://github.com/zuizui0223/mina/actions/runs/44676042238) 全ステップ**SUCCESS**、元のR1,000係数2×1,000行、CV保存、sourceレシート検証も成功。最終artifact ZIP SHA/CRCと係数/スコア数、中央値は会話ローカルでも独立読み出しを再検算した。

### 論文に入れていい範囲

**肯定できる：**「原著の103点lab/原RアルゴリズムでのL8 OLIの同位体分光**実験室モデル**は、同条件のL7と同程度の検証誤差で較正できる」。これは元論文のL7専用PLSRを新センサーへ延長する**測定モデルの実装結果**。

**まだ言えない：**「2013–21の真のAdélie糞反射率からδ¹⁵Nが推定できた」「ポリニヤの負の関連が未使用年で再現した」「δ¹⁵N低下＝オキアミ増加」「南極11地域でL8に生態的転写できた」。原著sourceコードを監査したところ、`Scripts/3-predict-diet.R` はもともと事前に`guano_bin=1,bad=0`に選別された`Data/L0/Landsat/landsat_reflectance_L457-2025-07-16.rds`を入力としており、新年の糞/非糞判定器は**元author repoの公開コードと元Zenodo datasetにはない**。元88site×年の真の糞画素マスクは確立していない。原著の最終Stan DI posterior（`4-diet-est`）も今回再計算していない。

**直接の次のゲート：** 新2013–21のL8像のnative true guano正例と岩/雪等のnegative、source ID、日時、地理座標およびimage QAを固定・外部検証してから、元契約どおり一回だけβ_P<0の追試へ進む。該当データが無いなら`NO_GO_NEW_GUANO_PIXEL_LABEL_SUPPORT`を維持し、過去439行・85地点・11地域に観察された冬100kmポリニヤ×光学δ¹⁵Nの負関連は**事後探索的発見**として保持する。元の事前予測は正であり外れ、元2004–06→07–10予測も改善していない事実を隠さない。

- 実装R：[`fit_author_style_original_103_L7_vs_L8_1000_PLSR5_ENSEMBLE_LAB_ONLY_20261120.R`](fit_author_style_original_103_L7_vs_L8_1000_PLSR5_ENSEMBLE_LAB_ONLY_20261120.R)
- CI：[`penguin-20261120-original-author-R-1000-L7-vs-L8-guano-PLSR-lab-only.yml`](https://github.com/zuizui0223/mina/actions/runs/44676042238)
- ソースコード／糞ROIの不在監査：[`YOUNGFLESH_ORIGINAL_CODE_AND_2013_L8_GUANO_ROI_SOURCE_AUDIT_20261120_JA.md`](YOUNGFLESH_ORIGINAL_CODE_AND_2013_L8_GUANO_ROI_SOURCE_AUDIT_20261120_JA.md)

GitHub Draft PR #214の別枝のみ。元main、凍結v0.5/0.6、Ecology Report、Paper2は未変更。
