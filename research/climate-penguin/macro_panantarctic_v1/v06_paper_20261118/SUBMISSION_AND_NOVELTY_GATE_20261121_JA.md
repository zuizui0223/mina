# 南極ペンギン v0.6：2026年11月21日 投稿前監査（科学的新規性・出版物重複・形式・原データ）

**結論：COAUTHOR_REVIEW_WITH_MAJOR_SCOPE_CAVEATS / NO_GO_SUBMISSION。** この文書は元データの再分析ではなく、すでに元GitHub Actionsでsource照合した量的結果に対する査読者視点の編集監査。PR #214 は Draft とし、main・凍結済みv0.5・Ecology Report・Paper2は変更しない。単一のv0.6 working manuscriptを継続し、別論文へ分裂させない。

## 論文の主質問を一本に固定

> How much does the geography of actually recorded nesting, rather than equal weighting of known colony locations, change the estimated marine climate exposure of Antarctic penguins?

**論文の最も防御可能な原データ上の追加**：同じ271個の「2011–2020に実計数を持つ」元siteで、3モデル平均・SSP5-8.5・2081–2100の海氷変化量が、site-equal **−28.634 percentage points**、site×speciesで実観測年を中央値化して合計した元巣数proxy重み **−13.276 pp**。差 **+15.358 pp**。これは元sourceで厳密に **between source reporting regions +15.656 pp / within regions −0.298 pp** と分解される。3モデルは確率的な母集団サンプルではなく、旧historical 1995–2014基準に対する選択された物理モデルのシナリオ結果。**同じ物理環境の曝露集計**であり将来巣数、保全効果、人口補償の予測ではない。

歴史の補助：同じsourceのAdélie固定コロニー19/26/35地点の巣数重み地理が+107.31/+88.41/+99.60km南向きに変わっても、元海氷への巣数重み付曝露変化は+0.022/+0.625/+0.908pp。別の1993–2000対2011–2020元23地点（GLORYS完全17地点）では巣数再配分R=+2.252pp（地域間+2.663、地域内−0.412）、共通17では+5.584pp（地域間+5.336、地域内+0.247）。この17地点は23の後期元巣数中央値重みの39.93%しか保持しない。4,999元調査年復元抽出で23地域間の正符号は全て維持。後付けの四地域増減率入替の「順位が上位」かどうかは観測年の再標本化に不安定（23で上位2位維持53.4%、17で19.4%）。**適応的海氷追跡の発見には昇格しない。**

## 先行研究との科学的新規性の境界

| 文献 | すでに実施したこと | 今稿で安全に追加できること／NO-GO |
|---|---|---|
| Lynch & LaRue (2014), Auk, DOI 10.1642/AUK-14-31.1 | Adélie地域別個体数の不均質性・大規模コロニー | 地域別の増減「発見」と言わない。site-equalとsource nest count-weighted、region-nestedな曝露会計を独自sourceで比較する |
| Iles et al. (2020), GCB, DOI 10.1111/gcb.15085 | 海氷と長期Adélie成長率の関係 | 2026旧265系列を元sourceで再現できない以上、CMIP6に人口応答係数を掛けない |
| Youngflesh et al. (2026), Current Biology, DOI 10.1016/j.cub.2026.06.028 | 同じLandsat原画像のguanoから海氷・diet・長期増減を推定 | 塩分との条件付き関連は元860同じ光学Yで探索的な補足。β+0.834だが13地域CI [−0.016,+1.684]；独立な食性／Phe基線との照合なし。新規の魚食変化発見と呼ばない |
| Ramírez et al. (2026), Diversity and Distributions, DOI 10.1111/ddi.70233 | 12種の将来海洋生息適性と優先海域を将来気候で検証 | 生息適性、MPA、真の将来出現確率ではなく、既知繁殖地の元計数に条件付きの固定重み物理曝露。こちらを「最初の将来予測」と言わない |
| DuVivier et al. (2026), Nature Communications, DOI 10.1038/s41467-026-69011-0 | Antarctic ecosystem value indexの中で巣数・コロニー配置・将来ペンギン人口モデル・アクセスを用いた | 巣数での海域加重や将来人口予測自体も既存。固定同一271 siteのsite-equalとnest-weight、region between/within、source coverageの対比だけを追加とする |
| Ratcliffe et al. (2026), Current Biology, DOI 10.1016/j.cub.2026.09.010 | 2025までのZavodovskiでのヒゲ減少とマカロニ増加を示し大きな種組成変化を実証 | 今稿の6地点同所アデリー／ジェンツー巣数比は新しい一般的な種置換機構ではない。種の比率と2種小計は異なることを観測で示すに止める |
| Silvano et al. (2025), PNAS, DOI 10.1073/pnas.2500440122 | Southern Ocean表面塩分・海氷の物理的構造の変化 | 3変数PCAの第2軸を独立物理機構としない。3モデル間のsalinity–sea ice covarianceの相違は物理的曝露の限定的補助 |

**編集上の判断:** Journal of Biogeography等に適用可能な普遍的島嶼生態機構は、今の元調査・4地域内帰無では出ていない。*Antarctic Science* Biological Research Article が実務上の候補ではあるが、元source再解析による環境曝露の会計だけでは新規性が足りないと判断され得る。受理確約や論文完成とはしない。島嶼・植生・食性の独立した因果経路を本原稿で主張しない。

## 本ターンで実行した編集・自動検証

1. **本文のタイトル・要旨・導入・Results 3.4・Discussion 4.3–4.4・Conclusionを一つの問いへ再構成。** Abstractは273語、外部文献引用・略語を避け、論文の本結果「同じ271siteの−28.63対−13.28」を先に提示。keywordsは8→6個へ減らしタイトルの語と重複しないよう修正。
2. **Figure 4を主結果の直接可視化へ。** 元ソース同じ271siteの2種類の重み×4scenarioの将来海氷変化をPanel a、3モデル海氷–塩分地理相関の不一致をPanel bへ。既存Figure 1–3と計4主図を維持。元ZIP5種類と一致するsource SHAのもとでsource-verified再描画CIを行い、実際のequal−28.63413394176649、weighted−13.276240917274327、gap+15.357893024492162をreceiptとして保存。**Figureの表示解像度・地図縮尺・原稿最終レイアウトの視覚監査は別ゲート。**
3. **2026年の実競合文献を文献表に追加。** Ramírez／DuVivier／Ratcliffeの書誌DOIを明示。未調査/真の0、site×species medianの非同時性、GLORYSとCMIP6の格子と季節の差、保護区・未来巣数・食性の非推論境界を保持。

## Antarctic Science投稿形式・未解決事項

確認した2026年11月現在の原文：[Aim and scope](https://www.cambridge.org/core/journals/antarctic-science/information/author-instructions)、[Preparing your materials](https://www.cambridge.org/core/journals/antarctic-science/information/author-instructions/preparing-your-materials)、[Submitting your materials](https://www.cambridge.org/core/journals/antarctic-science/information/author-instructions/submitting-your-materials)。

- 規程：要旨は約300語・文献／略語なし、キーワード最大6（タイトルの単語を避ける）。今回workingの原稿要旨・keywordsの主な文字数ゲートは修正済み。
- 必要：著者・所属・連絡先を持つ**1ページ目のタイトルページ**、**2ページ目要旨/キーワード**、3ページ目本文、Acknowledgements → References → separate figure captions → Tables。現在のGitHub MarkdownはこのWordレイアウトをまだ満たさない。対応著者名やメール、助成、COIを創作しない。
- 図：単段幅84mm/二段170mmの印刷で可読な大きさ、地図scale bar、figure alt text、必要に応じてTIFF高解像度。GitHub Actions PNG+SVGは再現性の成果だが、そのまま投稿指定TIFFの確認済みではない。
- Data/code：雑誌はオープンなデータ寄託とその場所・アクセス明示を求める。GitHub Actions zipは30日で失効する。第三者の元データの再配布権を未確認のままコピーしない。自前のフィルタ/派生分析CSV、source hash manifest、同じ図の出力だけをライセンス確認後に永続DOIへ保存する。**実際の公開DOIはまだ無い。**
- 著者確認・利益相反・資金・原稿Word・完全な参考文献体裁・最終図の視認性は保留。論文本体のサンプルが欠けていることは「有意な結果が出た」ことでは埋められない。

**最終判定**：本文科学の骨格と可視化は共同著者に批判的レビューを依頼する準備へ進めた。投稿はこのまま不可。これ以上の同じ4地域での閾値探索を止め、author approval + frozen long-term archive + publisher formattingを次の実務ゲートとする。
