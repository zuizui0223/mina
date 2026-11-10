# 南極ペンギンの海氷前線とのミスマッチと時間ラグ：地域再現性・経度区間の構成変化を分ける

2026-11-11 | mina Draft PR #214 | original-data, fixed three-decade geographic follow-up | **成功した実測再計算・6単体試験**。
Verified Actions: https://github.com/zuizui0223/mina/actions/runs/42912804192
Full original per-region/per-sector/source-roster output artifact: **13807867719** (source data source runs: 42844104869 and 42791019321).

## 判定：ラグ効果は未再現、巣数再配分と海氷前線の位相差は記述できる

**(A) 先行海氷の地域内相関 r=+0.480 は Victoria Land 主導。** 独立地域を除いた検定では符号が反転するため、アデリーに共通する「10年遅れの繁殖応答」は支持されない。

**(B) アデリーの3期共通観測19コロニーの1990s→2000sの南向き巣数加重緯度変化 +99.55 km は、+94.22 km の **10°経度区間間の相対的な巣数構成変化** と +5.33 km の **同一区間内の既存コロニー間再配分** に厳密に分解できる（数値恒等式）。これは生物個体の南方移住、種の分布境界の前進、海氷追跡速度を意味しない。

**(C) 同一経度区間の局地的な海氷前線と巣数加重緯度の方向は、時期により変わる。** ただし独立な海氷前線・繁殖地の組は各年代に最大2経度区間しか判定できず、普遍的なミスマッチ規則とは言えない。

## 原データ・方法の固定

- Source: 元MAPPPDで既に調査された595地点、3種2,456 source-method固定巣数レコード。1991–2000、2001–2010、2011–2020の**すべてで各2観測年以上**を持つ3期共通同一サイトだけ：Adélie 19、Chinstrap 12、Gentoo 12。未観測は0巣にしていない。
- Sea ice: 1991–2020 8–11月の固定元EUMETSAT OSI SAF海氷データ71,400地点月と、源25km衛星格子から復元した60%海氷等値線。60%は物理比較指標であり生物学的閾値ではない。
- No new source files, new thresholds, lag-window searches, method families, or pseudoabsences. Original 3-decade roster artifact 13776484021; original 2-D 60% ice sector artifact 13751339305. Both were earlier SHA/source/geometry validated in their own successful workflows.
- 3期の同一コロニー群における各10年の元巣数中央値を重みとする。すべての経度区間は事前の10度固定区分のまま使用、250kmブロック・元地域も固定。
- Methods/guard: GEO_REPLICATION_MISMATCH_DIAGNOSTIC_GATE_20261111.md; reproduce/independent tests: diagnose_geographic_climate_legacy_mismatch.py, unit_test_geographic_climate_legacy_mismatch.py.

## 1. アデリーの「先行海氷シグナル」はどこから来るか

3期共通アデリー19地点のうち、地域内Pearson相関に情報を提供するのは**18地点・3地域・5空間ブロック**。もう1地点のAdélie Landは、地域内の比較ができない。

元地域 | 情報を持つ観測サイト | 固定250kmブロック | 地域調整のSIC×巣数変化共分散への符号付き寄与
---|---:|---:|---:
Victoria Land | **13** | **3** | **+1.80268**
Central-west Antarctic Peninsula | 3 | 1 | −0.07454
South Shetland Islands | 2 | 1 | −0.03521
Adélie Land | 1 | 1 | 地域内共分散推定不可

共分散の寄与は、各地域内で中心化した各サイトの original SIC変化(pp) × log1p巣数変化 の積和（単位と分母を統一した比較用の算術成分）であり、因果的な「寄与率」ではない。n=2地点から地域固有の有意な相関を宣言しない。

- 元地域調整相関：**r=+0.4803175**。
- Victoria Land をまるごと除外：**r=−0.3848669**、残る地域内情報はわずか**5地点・2地域**。
- Central-west Antarctic Peninsula除外：r=+0.54646、South Shetland Islands除外：r=+0.49612。Adélie Landを除いても元のrに変化なし（その地域は単一サイト）。
- 元250kmブロック1個ずつ除外では+0.2144〜+0.6302（前回再現済み）だが、**空間ブロック1個除外と地域1個除外は同じ証拠ではない**。

したがって、元の先行SIC→後年巣数の関連は **Victoria Land内の構造に強く支配される探索的な地理依存性** であり、南極全域の10年ラグの証拠に昇格させない。

Chinstrap 12サイト/2地域/3ブロックは先行r=−0.1415、同時r=+0.2537で先行優位なし。Gentoo 12サイト/2地域/4ブロックは先行r=+0.0083、同時r=+0.1517。どちらも地域反復は不足。特定の種類だけ有意pになるまで別のラグを試さない。

## 2. 経度区間の中だけで「海氷とペンギンの向き」を比較

元の同一サイト集合の元巣数中央値から経度区間**内**の巣数加重緯度を計算し、同じ区間の元衛星60%海氷前線の南北変化と比較した。正は南向き。2地点以上、両年代に正の巣数重みがある区間のみ比較し、絶対値1km未満の方向は判定不能とした。

種 | 時期 | 同一区間内で計算可能な区間数 | 方向一致 | 方向逆 | 方向不定
---|---|---:|---:|---:|---:
Adélie | 1990s→2000s | 3 | 2 | 0 | 1
Adélie | 2000s→2010s | 3 | 1 | 1 | 1
Chinstrap | 1990s→2000s | 2 | 1 | 1 | 0
Chinstrap | 2000s→2010s | 2 | 1 | 1 | 0
Gentoo | 1990s→2000s | 2 | 1 | 1 | 0
Gentoo | 2000s→2010s | 2 | 1 | 1 | 0

元の最重要局地例：**160–170°E**（Victoria Landの12元アデリーサイト、固定250km 3ブロック）。

時期 | 区間内巣数加重緯度の南北変化 | 同じ区間の海上60%海氷前線の南北変化 | 方向
---|---:|---:|---
1990s→2000s | **+7.09 km** | **+3.78 km** | 同方向
2000s→2010s | **−1.96 km** | **+42.40 km** | 逆方向

これは地域限定の確かな**記述的方向のミスマッチ**であり、実際のペンギンの個体が海氷前線に追いつけなかった観測、海岸線沿いの気候速度、種の適地閾値、または繁殖成功の因果効果ではない。そもそも元コロニーは固定座標で、各地点間の巣数重みが変わっただけである。

## 3. 全域の南向き再配分を「経度区間間 vs 同一区間内」に厳密分解

3期すべてで同じ元サイトの巣数中央値を重みに、各期間の元の正規化サイト加重緯度を計算。各10°区間の元巣数シェアの変化（between-sector）と、同一区間内のサイト重み変化（within-sector）への**対称二要因恒等式**を検算した。経度区間ごとの間の寄与は、元19サイトの**重み付けしない固定平均緯度**をアンカーにした（緯度原点による個別寄与の見かけの巨大化を回避）。アンカーを一定平行移動しても総計と個別寄与は変わらないことを単体テストで確認。

種 | 比較 | 全巣数加重緯度の南向き変化 km | **経度区間間の重み変化 km** | 区間内の再配分 km
---|---|---:|---:|---:
Adélie | 1990s→2000s | **+99.55** | **+94.22** | **+5.33**
Adélie | 2000s→2010s | **+7.76** | **+9.35** | **−1.60**
Chinstrap | 1990s→2000s | +2.95 | −1.78 | +4.73
Chinstrap | 2000s→2010s | +3.11 | −1.56 | +4.68
Gentoo | 1990s→2000s | −6.53 | −7.10 | +0.57
Gentoo | 2000s→2010s | +7.56 | +6.50 | +1.05

**1990s→2000sのAdélie大きな南向き数値のほとんどは、地域内の生物の分布限界前進ではなく、隔たった経度区間間の観測巣数比が変化したもの。** この分解結果は研究目的の修正に直結する。問いは「ペンギンが南極全域で海氷とともに何km移住したか」ではなく「地域をまたぐ大規模コロニーの巣数再配分と、同じ地域の海洋環境前線の変化が、時間・方向でどうずれるか」である。

ただし10°という経度区間の幅でbetweenとwithinの数値比は変わるため、この約94.6%を分類群一般の生物学的な割合・因果効果として主張しない。今回の固定地理的解像度での**記述的な恒等分解**だけが支持される。

## 結論の階層と論文へ統合すべき範囲

1. **実測して支持された定量結果**：アデリーの元3期共通19地点で、巣数加重緯度は最初の期間+99.55 km、後半+7.76 kmへ変化。大部分は経度区間間の記録巣数シェア再構成。元衛星60%海上前線は経度区間ごとに南北逆方向へ動き、160–170°Eの区間では後半に海氷前線+42.4 kmに対して区間内巣数加重緯度−1.96 kmという記述的な不一致。
2. **探索的なラグ候補だが地域再現不能**：Adélieの先行海氷×後年の巣数変化r+0.480は、Victoria Landを外すとr−0.385に反転。相関だけを使って10年の遅延応答や「気候負債」と呼ばない。
3. **まだ検証していない**：真の繁殖地の定着・消失を含む分布境界移動、調査努力補正、海岸線に沿う有効海氷適地速度、個体・世代の移住/繁殖成功・気温の因果効果、2040/2100繁殖予測。
4. **論文の上限**：南極の元既知繁殖コロニー網における**breeding-count spatial allocation × marine environmental-front phase mismatch**。先行時間ラグは地理構成の警告として添える。強い「南極のアデリーが温暖化から何年取り残された」主張はしない。

## 再現・変更範囲

- Exact receipt: https://github.com/zuizui0223/mina/actions/runs/42912804192 (SUCCESS), artifact **13807867719**; original region influence and sector tables, plus six standard-library geometry/identity unit tests.
- Full workflow: .github/workflows/penguin-geographic-legacy-sector-mismatch-diagnostic.yml; new ecological code: diagnose_geographic_climate_legacy_mismatch.py; tests: unit_test_geographic_climate_legacy_mismatch.py.
- Earlier immutable original results: https://github.com/zuizui0223/mina/actions/runs/42844104869 and https://github.com/zuizui0223/mina/actions/runs/42791019321.
- This is post-result source-geography auditing, NOT a pre-registered new significant ecological lag finding. The mina climate PR #206, manuscript v0.6, frozen Paper 1/2 and main are not modified. Draft PR #214 is not merged.
