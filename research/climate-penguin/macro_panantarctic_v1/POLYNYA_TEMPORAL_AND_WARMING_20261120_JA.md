# ポリニヤ負相関の年代安定性、原著コードと温暖化への接続

2026年11月20日。PR #214の追加解析。負方向を見た後に行った年代診断であり、独立確認には数えない。

## 今回確認できたこと

冬季の沿岸ポリニヤ面積割合と夏季のアデリー光学δ¹⁵Nの負の関連は、2004–2006年と2007–2010年の双方で負の点推定となった。ただし後期の地域クラスタ95%区間はゼロを含む。同じ79地点への制限でもこの結論は変わらない。既存の将来年代への予測比較を元ZIPから再計算し、ポリニヤ追加による改善がないことを確認した。2013–2021年の新しい光学応答は今回生成できておらず、独立再現は未成立。

## 原著コードの確認結果

先行のZenodo監査は256,425,816 byteの元ZIPを出版社MD5 `e29a2f68c84e3a515044d554540def2f` と照合して成功したが、1108メンバー中に解析スクリプトはなかった。これは原著コード全体の不在を意味しない。今回、著者GitHub `caseyyoungflesh/penguin_diet_from_space` を取得し、commit `4ab7c992fc2232b7905af0d1aa949d88dc9561ea` の追跡ファイル全13件を点検した。

- `Scripts/3-predict-diet.R` の31行は既選別の `landsat_reflectance_L457-2025-07-16.rds` を読み込む。
- 34・37行の `unique(guano_ret$bad)` と `unique(guano_ret$guano_bin)` は既存ラベルの値の表示。ラベルを生成する分類器や、品質不良画素をここで除く処理にはなっていない。
- 67–75行で衛星4・5・7を分けてPLSR係数を適用し、99行で上記ラベルを削除する。新Landsat 8画像の分類・抽出はこの処理に含まれない。
- 公開スクリプト・README全体を検索し、このRDSを生の衛星画像から生成する処理は確認できなかった。原著側で未公開の処理が存在しない、とは結論しない。

原著の処理を確認したことで解消したのは「公開コードに既存の分類器があるか」という不確実性。新年代の反射率を同じ意味の観測として得るためには、画像の品質と当該年代の糞領域の妥当性を確かめる必要がある。前段のArdley注釈に対する80%純度条件や6地域条件は研究側で設定した検証仕様であり、原著の必須条件とは確認できない。混合画素を扱う代替法にも可能性はあるが、その誤差を新たに評価する必要がある。

[著者コード](https://github.com/caseyyoungflesh/penguin_diet_from_space/tree/4ab7c992fc2232b7905af0d1aa949d88dc9561ea)／[Zenodo監査実行](https://github.com/zuizui0223/mina/actions/runs/44674477466)。コードのパスとハッシュは `diet_salinity_source_20261117/temporal_review_20261120/author_code_receipt.json` に保存。

## 元データを使った年代別追加診断

元439地点季節の定義、100 km圏・6–10月のポリニヤ割合、光学応答、画像日・夏季海氷・水温の調整、地点および地域×季節固定効果を維持。既存の2004–2006年／2007–2010年分割を用い、各期間内で同じ関連モデルを再推定した。下表は夏季塩分も調整したM_SP、面積割合10 percentage points当たりのδ¹⁵N変化。信頼区間は地域クラスタt区間。

|期間|地点季節数|地点数／地域数|係数 ‰|95%区間 ‰|
|---|---:|---:|---:|---:|
|全期間2004–2010|439|85／11|−0.922|−1.349〜−0.494|
|2004–2006|132|79／10|−1.683|−2.615〜−0.751|
|2007–2010、利用可能全地点|307|85／11|−0.362|−0.878〜+0.154|
|2007–2010、前期にもある地点|291|79／10|−0.564|−1.346〜+0.219|

前期だけの有意性と後期の非有意性の比較から、両期間の効果差が有意とは言えない。上表は係数の方向と不確実性の診断。全期間で負方向を発見した後の分割なので、後期を未使用の確認標本と呼ぶこともできない。

元の時間外予測を再実行した。2004–2006年学習、2007–2010年の既知79地点・291地点季節で、地点均等RMSEは海氷・水温等のみ1.83954‰、ポリニヤ追加1.84893‰。塩分ありでは1.80090‰からポリニヤ追加で1.81221‰。予測時に未来の地域×季節効果は使わない。後期で再推定した上表の係数と、この前期学習による予測評価を区別する。

原同位体artifact 14328755565、SHA256 `dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`、元ポリニヤartifact 14539723210、SHA256 `702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96` を使う。今回のコード `diet_salinity_source_20261117/check_temporal_sign_20261120.py` は両SHAを確認して既存の推定関数を呼ぶ。出力CSVと予測評価JSONを同じ場所の `temporal_review_20261120/` に保存。

## 温暖化・海氷減少とのつながり

研究上の問いは「海氷の総量が同じように変化しても、冬季に沿岸のどこで開水面が形成されるかによって、翌夏の食物網関連指標が異なるか」と具体化できる。今回調整した海氷は11–翌2月、ポリニヤは6–10月なので、冬季の同じ海氷量を一定にした空間配置の効果まで示せてはいない。

沿岸ポリニヤでは風による氷の排出と新たな結氷が繰り返され、開水面と活発な海氷生産が共存しうる。温暖化による広域の海氷後退では、開水面が外洋と連続して、閉じたポリニヤとして数えられる面積が減る場合も考えられる。このため「海氷減少量→ポリニヤ面積→δ¹⁵N」の単純換算は成立が未検証。ポリニヤの長期変化には地域周期性もあり、既存の気候モデルによる再現に課題が報告されている。[Duffy et al. 2024](https://doi.org/10.1073/pnas.2321595121)、[DEEP-AA原データ論文](https://doi.org/10.1038/s41597-024-03848-2)。

具体的な将来接続には、まず未使用年代で負方向の相関を確認し、同じ冬季窓の海氷量を調整しても空間配置が情報を足すかを検証する。その後、観測と同じ定義で沿岸ポリニヤを再現できる気候モデル・ダウンスケーリングに限って条件付き投影する。今回の3モデルのCMIP6海氷変化にはこの検証がなく、係数を掛けた将来の餌構成・巣数予測はまだ支持されない。

## 論文本文に使える記述案

“Across 439 colony-seasons at 85 Adélie penguin sites, greater winter coastal-polynya exposure was associated with lower subsequent summer optical δ¹⁵N after adjustment for summer sea ice, temperature, salinity, image timing, site, and region-by-season effects. The negative coefficient persisted in both historical subperiods, but the later-period interval included zero and adding polynya exposure did not improve forward prediction. This exploratory association motivates testing whether the seasonal spatial organization of sea ice contributes information beyond seasonal mean concentration. Independent temporal replication and isotope-baseline measurements are needed to distinguish food-web responses from changes in baseline isotopic composition and optical measurement.”

新規性候補は、冬の沿岸開水面配置を夏の同位体指標と対応させる点。塩分や夏季海氷を調整した負の関連は記述できる。オキアミ消費の増加、繁殖成功の増加、温暖化への適応や将来の個体数変化は直接観測していない。新年代の応答が取得できていない現状では、探索的な結果と時間外予測の不成立を同じ本文で報告する。
