# 23地点を回復すると、海氷への巣数再配分効果は「地域間で正・地域内は不安定」

**2026-11-21 JST | mina Draft PR #214 | Source-fixed retrospective coverage audit | [GitHub Actions #44890825170 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44890825170)。** これまでに観測した17地点の正の配分効果を**見た後の感度分析**であり、独立な確認や事前登録した効果検定ではない。

## 科学的に追加された結果

元の1993–2000年対2011–2020年のアデリー巣数（同じ原地点・各期間2実測年、実際の方法で記録した巣数中央値）の23地点すべてに、元source OSI SAFの8–11月海氷濃度がある。一方、海氷・塩分・水温をすべて揃えると、大きなVictoria Land 6地点（BRDM, BRDN, BRDS, CRZE, CRZW, ROYD）を欠く17地点になる。後者が保持する23地点の非同時・地点別観測巣数中央値の合計は前期 **50.59%**、後期 **39.93%** だけ。欠落6地点のGLORYS値を別の海洋格子で補充しなかった。

すでに知られている海氷の「配分成分」Rを、元報告地域間・地域内の成分に同じ対称恒等式で厳密分割した（[地域内分解の仕様](EXPLORATORY_REGIONAL_SORTING_NULL_FREEZE_20261121.md)と同じ式）。

| 対象 | 海氷の現地変化成分(pp) | 巣数配分成分R(pp) | Rの地域間(pp) | Rの地域内(pp) | Rの地域間割合 |
|---|---:|---:|---:|---:|---:|
| 全23地点・海氷だけを要求 | −0.636301 | **+2.251585** | **+2.663382** | **−0.411797** | 118.29% |
| 共通17地点・海氷＋塩分＋水温を要求 | −2.482273 | **+5.583701** | **+5.336436** | **+0.247266** | 95.57% |

地域間割合100%超は統計的説明力の意味ではなく、地域内成分が負で相殺しているための算術結果。17地点の既公表した地域内帰無の右尾割合0.34962は「17地点での成長率交換可能性に対して、正の地域内選別を示せなかった」という診断で、23地点への有意確率の流用はしていない。

**23地点では、地域内の符号が17地点と逆。** 地域間の正方向のみが両データ支持域に共通する。海氷曝露を「維持した」／「増えた」と一括りにせず、(1) 各固定siteの物理的変化、(2) 地域間の巣数比率変化、(3) 地域内の巣数比率変化を区別する必要がある。

## 原観測の除外感度と限界

- **23地点leave-one-site：23/23で地域間成分が正**（値域 **+1.204〜+3.920 pp**）。配分Rの合計も23/23で正。ただし地域内成分は23/23すべて負ではなく、**CRZWを外す1通りだけ正（+0.120 pp）**に反転。他の22地点除外では負（最小約−0.506 pp）。したがって「同じ地域内の繁殖地で海氷選好が負」とも断定しない。
- **23地点leave-one-region：地域間成分は4/4で正**。しかしR全体の正方向は4/4で維持されない。South Shetland Islandsを除外するとRは約**−0.266 pp**（地域間+0.159、地域内−0.425）。地域間再配分だけの符号は頑健でも、合計の生態学的曝露変化は地域構成に依存する。
- 地域単位の早期/後期巣数比率と各regionの物理環境は同じ地域報告区分から計算。**4つの地域は無作為抽出された独立反復ではない。** 地域内の大巣地点CRZWの巣数中央値は前期105,103、後期251,250。これは非同期の源報告巣数であって、同じ個体が移動した証拠ではない。
- 23地点には0→0のPLENが含まれ、**真の0を欠測に置換しない**。独自監査の最初のCI [#44890780584](https://github.com/zuizui0223/mina/actions/runs/44890780584)は、誤って全site巣数>0を要求し停止。**判定式も元データも一切変更せず**、0→0を正当な原観測として許容し、0→正（後期の新定着）は本データにないことを検査するよう修正。最終CI #44890825170 SUCCESS。

## 論文として言える主張

> In a fixed panel of 23 source-observed Adélie colonies, a positive nest-weight redistribution component of coastal sea-ice exposure (+2.25 percentage points) came from **between-region nesting composition (+2.66 pp)**, partly offset by **within-region reweighting (−0.41 pp)**. Restricting the cohort to 17 colonies with complete ocean salinity and temperature coverage changed the within-region term to +0.25 pp and excluded around 60% of the late observed nest-median sum. These sensitivity results identify a geographical-composition effect on an exposure summary, not active colony choice, individual migration, an ecological compensatory adaptation, or a forecast of population resilience.

主論文は「地域間の巣数構成変化と物理環境変化のズレ」を提示し、**同じ地域内の気候ニッチ追跡を確定したとはしない**。港湾管理・島嶼生息地の性質・繁殖地の定着/放棄などの因果過程はこの集計から切り分けられない。今までの正の海氷配分項を、独立な新しい相関が得られたかのように二重カウントしない。

## ソースと再現

- 入力はすでにコミットされた [matched_support.csv](matched_support.csv) の同一`comparison=long,radius=0`の23 source observations、[parent_roster_support_diagnostic.csv](parent_roster_support_diagnostic.csv)、[REGIONAL_SORTING_NULL_RESULT_20261121.json](REGIONAL_SORTING_NULL_RESULT_20261121.json)。期間・環境定義・巣数フィルターはすべて2026-11-20の既存資料から固定のまま。
- [独立実装のPython標準ライブラリ検算](recompute_parent23_vs_complete17_SIC_region_sensitivity_20261121.py)：親23の既存local/R/total・前後重み海氷、共通17の既存R/between/withinを**1e−9以内**で照合。さらに地域一つ除外・地点一つ除外、空白と0の区別を再実行。別途JavaScriptの逐次集計でも同じ値を算出。
- [最終GitHub Actions](https://github.com/zuizui0223/mina/actions/runs/44890825170) **SUCCESS**、artifact **14702220764**、ZIP SHA256 `b8580c48faf6298360ffc712dafd374f37df0928a6b2d84b1356ca1c29de9902`。出力JSONはワークフロー内で再生成できる。外部ソースの恣意的な新データ取得なし、将来気候による巣数効果の外挿なし。
- **Draft PR #214のみ**。過去の海洋同位体・ポリニヤとは異なるsource rosterであり、これらの応答を一つの因果鎖として結ばない。main、凍結v0.5、Ecology Report、Paper2未変更。
