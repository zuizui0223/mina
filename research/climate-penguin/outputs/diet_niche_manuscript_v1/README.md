# Signy食性差論文ドラフト v1

**2026-11-06：完全英語版を作成。** [英語原稿一式](../diet_niche_english_v1/README.md)に、[本文Word](../diet_niche_english_v1/Signy_diet_manuscript.docx)（15ページ、主図4点）と[補足Word](../diet_niche_english_v1/Signy_diet_supplement.docx)（14ページ、補足図2点）、編集用Markdown、独立数値照合と全ページ確認の記録を収録した。既存の食性結果・Palmer比較・Gentoo成分・条件付き将来計算を一続きにし、CMIP6の全9入力ストアに対応する正式な実験コレクション引用を補足S9へ整備した。以下は日本語版と元解析への入口である。

- [本文・図説明](MANUSCRIPT_JA.md)：日本語本文、英語題名・要旨、従来の主図1–3と外部地域比較の図4。
- [主表・補足表](TABLES.md)：主表3点、補足表2点。個別CSVが数値の再利用用。
- [補足方法・結果](SUPPLEMENT_JA.md)：試料構成、細かい食性軸、将来移用の制約。S7にGentooの正魚湿重量胃率・条件付き組成の算式と補足図S1、S8に同じ三応答の条件付き将来計算と補足図S2を追加。
- [引用監査](REFERENCES_VERIFIED.md)：9文献の書誌と引用範囲。2026-11-06にPalmer原著のPickett et al.（2018）を追加。
- [CMIP6出典](CMIP6_SOURCE_STORES.csv)：用いた9ストアのモデル、実験、メンバー、版。
- figures/：同じ3図のPNGとベクトルPDF。
- [Palmer–Signyの外部比較](../palmer_signy_diet_external_v1/REPORT_JA.md)：二種の原年次値、出典照合、固定モデル移用の結果と図4。別出力ディレクトリの図を本文から相対参照する。
- [Gentooの食性変動の内訳](../signy_diet_components_v1/REPORT_JA.md)：同じ9季節・73胃で、正の魚湿重量を記録した胃率pと該当胃の平均魚割合cを分ける。補足図S1・年次値・傾きの数式上の割当は別出力を相対参照する。
- [Gentooの条件付き将来計算](../signy_component_scenarios_v1/REPORT_JA.md)：三応答p・c・mを別々に適合し、全12気候条件、観測域内11条件の食性値・変化量、年別気候支持と補足図S2を収録する。

主張：Signyの対応9季節で低海氷年ほどジェンツーと他二種の魚割合差が小さいという三種の結果（r = 0.784）を維持する。外部比較はAdélie–Gentooの二種・食物中魚割合差という別指標で行った。Palmerの6季節では二種差が小さく、SICとの関連は弱く、Signyで固定した式は全6季節を過大予測した。地域・年代・コロニー・採集条件の違いを残し、地域間の気候効果の有意差とは解釈しない。海氷減少感度はSignyの観測関係を固定した条件付き計算として提示する。

追加したGentoo単種の内訳では、pとSICのr = 0.7829、二成分内補正p値 = 0.02293。cはr = 0.6241、補正p値 = 0.12956で証拠が不明瞭だったが、平均食性の傾きの数学的割当はp項45.9%、c項53.5%、共変動項0.6%だった。頻度だけが原因、またはその寄与が優越するという結論ではない。pは正湿重量の記録率で、Palmerの骨・耳石も含み得る検出頻度とは区別する。

将来成分の追加は同じ9季節の関係を固定した条件付き展開で、独立した温暖化影響の証拠を増やさない。域内11平均条件でp・c・mの点変化はOLS・fractional-logitとも低下した。基準SIC 48.683%での適合p／c／mは75.88%／55.64%／46.29%で、1995–2014年の食性観測ではない。mは自身の回帰から求め、適合p×適合cへ置き換えない。将来20年すべてがSIC観測域内なのは7/12条件で、年別食性は予測していない。

## 再生成

mina cloneルートで実行する。

```powershell
python research/climate-penguin/work/diet_niche_manuscript_v1/build_assets.py --out research/climate-penguin/outputs/diet_niche_manuscript_v1
python research/climate-penguin/work/diet_niche_manuscript_v1/verify_assets.py
```

Python依存はnumpy、pandas、matplotlib。原解析コードと既存検証は隣接するwork/niche_multiscale_v1およびwork/diet_niche_scenarios_v1にある。上記build_assets.pyは従来の図1–3・主表1–3・補足表1–2・入力manifestを再生成し、本文は書き換えない。Palmer比較は[専用の解析仕様](../../work/palmer_signy_diet_external_v1/DESIGN.md)と[再実行案内](../palmer_signy_diet_external_v1/REPORT_JA.md)に従い、別出力内の元年次値・図4を再生成する。本文内の二種比較表はそのsummary.jsonから転記した表示値である。本文は手動編集のため、数値更新時には図表と本文の両方を確認する。

Gentooの成分解析は[専用の解析仕様](../../work/signy_diet_components_v1/DESIGN.md)と[再計算案内](../signy_diet_components_v1/REPORT_JA.md)に従う。本文3.5節と補足S7の値は専用summary.jsonと年次CSVに対応する。従来の入力manifest・図1–4・文献9件は維持し、成分解析の出典・検証は専用出力に保存する。

将来成分解析は[固定仕様](../../work/signy_component_scenarios_v1/DESIGN.md)と[再実行案内](../signy_component_scenarios_v1/README.md)に従う。本文2.7・3.6節と補足S8の表示値は専用summary.json、component_scenarios.csv、controlled_reductions.csvに対応する。補足図S2のPNG/PDFと16入力のmanifestは専用出力を参照し、既存の図1–4・補足図S1・入力manifest・文献9件を再定義しない。

## 投稿前に残る事項

著者・所属・責任著者・著者貢献・研究費・利益相反・謝辞・必要な倫理／許可声明の確定、対象誌への体裁調整、コードと結果の恒久的リリース識別子の付与が必要。気候モデルの指定引用は[英語版の出典対応表と監査](../diet_niche_english_v1/CMIP6_CITATION_AUDIT.md)で全9入力分を確認済み。完全な三種採取時期調整は未実施。Palmerの公開年平均を用いる地域外移用診断は実施済みだが、個体別胃・採取日がなく、元Table 1のGentoo n = 129と方法本文n = 128の不一致、丸め、異なるコロニー・年代という制約が残る。この比較を将来予測精度や生物学的な地域効果の検証成功とは扱わない。
