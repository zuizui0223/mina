# Signy食性差論文ドラフト v1

- [本文・図説明](MANUSCRIPT_JA.md)：日本語本文、英語題名・要旨、従来の主図1–3と外部地域比較の図4。
- [主表・補足表](TABLES.md)：主表3点、補足表2点。個別CSVが数値の再利用用。
- [補足方法・結果](SUPPLEMENT_JA.md)：試料構成、細かい食性軸、将来移用の制約。
- [引用監査](REFERENCES_VERIFIED.md)：9文献の書誌と引用範囲。2026-11-06にPalmer原著のPickett et al.（2018）を追加。
- [CMIP6出典](CMIP6_SOURCE_STORES.csv)：用いた9ストアのモデル、実験、メンバー、版。
- figures/：同じ3図のPNGとベクトルPDF。
- [Palmer–Signyの外部比較](../palmer_signy_diet_external_v1/REPORT_JA.md)：二種の原年次値、出典照合、固定モデル移用の結果と図4。別出力ディレクトリの図を本文から相対参照する。

主張：Signyの対応9季節で低海氷年ほどジェンツーと他二種の魚割合差が小さいという三種の結果（r = 0.784）を維持する。外部比較はAdélie–Gentooの二種・食物中魚割合差という別指標で行った。Palmerの6季節では二種差が小さく、SICとの関連は弱く、Signyで固定した式は全6季節を過大予測した。地域・年代・コロニー・採集条件の違いを残し、地域間の気候効果の有意差とは解釈しない。海氷減少感度はSignyの観測関係を固定した条件付き計算として提示する。

## 再生成

mina cloneルートで実行する。

```powershell
python research/climate-penguin/work/diet_niche_manuscript_v1/build_assets.py --out research/climate-penguin/outputs/diet_niche_manuscript_v1
python research/climate-penguin/work/diet_niche_manuscript_v1/verify_assets.py
```

Python依存はnumpy、pandas、matplotlib。原解析コードと既存検証は隣接するwork/niche_multiscale_v1およびwork/diet_niche_scenarios_v1にある。上記build_assets.pyは従来の図1–3・主表1–3・補足表1–2・入力manifestを再生成し、本文は書き換えない。Palmer比較は[専用の解析仕様](../../work/palmer_signy_diet_external_v1/DESIGN.md)と[再実行案内](../palmer_signy_diet_external_v1/REPORT_JA.md)に従い、別出力内の元年次値・図4を再生成する。本文内の二種比較表はそのsummary.jsonから転記した表示値である。本文は手動編集のため、数値更新時には図表と本文の両方を確認する。

## 投稿前に残る事項

著者・所属・著者貢献・研究費・利益相反の記入、対象誌への体裁調整、気候モデルの指定データ引用確認が必要。完全な三種採取時期調整は未実施。Palmerの公開年平均を用いる地域外移用診断は実施済みだが、個体別胃・採取日がなく、元Table 1のGentoo n = 129と方法本文n = 128の不一致、丸め、異なるコロニー・年代という制約が残る。この比較を将来予測精度や生物学的な地域効果の検証成功とは扱わない。
