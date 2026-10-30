# 原音響年次の出典衝突：2024報告Table 2と2023原論文Table 3

**優先度：critical source-lineage correction（2026-10-30）**

## 発見

Skaret et al. 2023, *ICES Journal of Marine Science* 80:1472–1486, [DOI 10.1093/icesjms/fsad076](https://doi.org/10.1093/icesjms/fsad076), Table 3 が南北各層とCombinedの年・CV・密度の原解析を記載。一方、IMRの[2024調査報告書Table 2](https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14) では数値の年ラベルに不整合がある。2023原論文の **Combined 2013年の値は存在しない**（2013は北層だけ部分調査）。2024表では2013年Combined=76.5g/m²となっているが、原論文ではこの76.5は2014年Combinedに該当。以降の2014～2020年も順次ずれる。正確な出典上の原因（再計算、転載、植字など）は確認できないので断定しない。

これまでminaで入力した \`inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv\` と、その上の \`south_orkney_krill_fledgling_v1\` による見かけの関連は**元出典の年次対応に問題があり、原論文Table3を基準とした結論で置き換える**。過去ファイルは失敗の証跡として保持、黙って置換しない。

## 修正する元データ

新 \`inputs/skaret_2023_krill_stratum_table3_reconciled_v2.csv\` は、Combined 9年（2011、2012、2014–2020）、North 10年（2011–2020）、South 9年（2011、2012、2014–2020）、Shelf edge 3年（2015/19/20）の**原出版推定値**をstratum別に固定。2013のCombinedとSouthを欠測とし0に置換しない。2015南側は海氷による不完全調査で別フラグを持つ。2011/12は調査線が以後と少し異なることも保持する。これらは論文表の**手動転記であり生の音響サンプル**ではない。

## 数値的影響

以前は誤年次Table2を使ったSigny3種・2011〜2019年の9季 Pearson r が、アデリー−0.2116、ヒゲ−0.5591、ジェンツー−0.5461。原論文の年へ直して2013が欠測の8季に限定すると**+0.057、−0.212、−0.413**へ変更。両者の標本年は違うので、同じ8季に制限しても前値から変化することを検証する。2015年不完全調査をさらに除いた7季、事後的に2012年を除いた6季も全件保存する。ある仕様だけを結果により選択しない。

原論文のNorth/South観測密度・比も補助比較する。ただし北層・南層は広大な調査区であり、Signy島からの距離・アクセス可能な餌場・採餌圏ではない。Freer et al.の年次ラスタとの照合にも同じIMR元音響調査が含まれるため、独立な調査の再現ではない。推定年の修正は海氷・塩分からの因果関係や未来巣数の予報精度を生み出さない。

## 科学的判断

**旧v1のオキアミ資源量×雛生産結果はSUPERSEDED**。音響原論文Table3の年次を統制してもSigny雛生産への安定した因果・予測係数は出ていない。今後は「実測の元音響密度の時系列」と「既存GAMが生成した2011〜2020年の空間予測ラスタ」を明確に分け、2013年の北層だけの値を統合南北値に代入しない。

独立した生態学的予測は未検証。2050/2100年の繁殖数やN_eff、植生の未来数値予測はNO-GOを維持。原音響の南北サブ領域とペンギンの採餌時空間の実測が必要。

## 再現

原論文Table3とIMR2024Table2の行単位差を全10年CSVに保存し、元3種BAS繁殖記録を再取得して年次を検証する。 \`python research/climate-penguin/work/climate_penguin/south_orkney_krill_source_reconcile_v2.py --stage-dir build/signy_stage_derived --out build/skaret_reconciled --check\`。

既存Paper1/PR189、Paper2/PR199、216比較、他の海氷予測失敗結果は未変更。異なるデータ年次を後から混合しない。
