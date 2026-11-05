# Signy食性差論文ドラフト v1

- [本文・図説明](MANUSCRIPT_JA.md)：日本語本文、英語題名・要旨、主図3点。
- [主表・補足表](TABLES.md)：主表3点、補足表2点。個別CSVが数値の再利用用。
- [補足方法・結果](SUPPLEMENT_JA.md)：試料構成、細かい食性軸、将来移用の制約。
- [引用監査](REFERENCES_VERIFIED.md)：8文献の書誌と引用範囲。
- [CMIP6出典](CMIP6_SOURCE_STORES.csv)：用いた9ストアのモデル、実験、メンバー、版。
- figures/：同じ3図のPNGとベクトルPDF。

主張：Signyの対応9季節で低海氷年ほどジェンツーと他二種の魚割合差が小さい。観測関係固定の海氷減少感度を示す。南極全域、因果効果、競争増加、ニッチ全体の収束、検証済み将来予報は主張しない。

## 再生成

mina cloneルートで実行する。

```powershell
python research/climate-penguin/work/diet_niche_manuscript_v1/build_assets.py --out research/climate-penguin/outputs/diet_niche_manuscript_v1
python research/climate-penguin/work/diet_niche_manuscript_v1/verify_assets.py
```

Python依存はnumpy、pandas、matplotlib。原解析コードと既存検証は隣接するwork/niche_multiscale_v1およびwork/diet_niche_scenarios_v1にある。本文は手動編集、数値図表は元集計から生成。図は目視で文字・凡例の重なりを確認した。

## 投稿前に残る事項

著者・所属・著者貢献・研究費・利益相反の記入、対象誌への体裁調整、気候モデルの指定データ引用確認が必要。探索的選択と9環境年という制約は本文に記載済みであり、文章の修正だけでは解決しない。完全な三種採取時期調整、独立地点・年代の予測検証は未実施。
