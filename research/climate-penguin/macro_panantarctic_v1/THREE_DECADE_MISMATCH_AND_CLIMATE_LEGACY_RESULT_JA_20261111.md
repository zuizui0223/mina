# 南極のペンギン3種で「海氷前線とのミスマッチ」と「温暖化ラグ」をどこまで検証できるか

**2026-11-11｜実測済み / Draft PR #214 / 原本固定 / 結論: phase mismatch は記述可能、biological climate debt or 10-year lag is NOT established**

## 一文の科学的結論

1990〜2010年代の3期に同じ地点で実測巣数がある原MAPPPD観測から、アデリーの繁殖巣数重心は最初の十年期に大きく南へ変化した一方、対応する経度区間の海上60% SIC等値線は次の十年期により大きく南向きへ変化した。これは**単純な「海氷が先に南進し、ペンギンが後から追う」という空間ラグとは一致しない**。別の問いとして、後年の各地点の元巣数変化は先行する海氷変化との地域調整相関が同時期の海氷変化との相関より大きかったが、この関連は地域の一括除外で符号が反転した。**単一の温暖化遅延係数や気候負債の年数を推定できたわけではない。**

## 元データ・追加実行

- 生物: MAPPPD 595元繁殖サイト、18原地域、3種2,456件の実巣数×年記録。最頻元計数法で固定、原0巣と未観測を区別。1991–2000、2001–2010、2011–2020の**各10年すべてで元計数が少なくとも2年**ある同一 site×species のみ。
- 気候: 1991–2020年8〜11月に各595地点100km沿岸の元OSI SAF v3.1 25km海氷。実120月源NetCDFのSHA照合済み、595地点で元参照値一致、元71,400地点月。各地点の各年代の海氷は元全10観測年が有効な場合のみ算出。海氷の減少をそのまま局所気温上昇量や採餌適性にはしない。
- 60% marine front: 元2次元海氷格子から抽出済みの海上等値線の10°経度区間別 **緯度変化**。これは陸上繁殖の適地閾値、海岸線に沿う気候速度、採餌場所の実観測ではない。
- 計算と独立算術テスト: https://github.com/zuizui0223/mina/actions/runs/42844104869 **SUCCESS**、artifact **13776484021**（元3年代同一地点CSV、相関・空間ブロック除外・地域除外・逆時間対照の完全JSON）。
- 仕様を新結果より先に固定: FROZEN_THREE_DECADE_CLIMATE_LEGACY_GATE_20261111.md。本文に出すのは1つの先行 vs 同時の対照と逆時間負対照。複数の年遅れ・海氷閾値・GAM構造を探索して選ぶのは禁止。

## 1. 3年代すべて観測された実際の規模と巣数重心

| 種 | 厳格共通コロニー site ID | 原地域 | EPSG3031 250km固定ブロック | 10°元海氷前線経度区間 |
|---|---:|---:|---:|---:|
| Adélie ADPE | **19** | **4** | **6** | **5** |
| Chinstrap CHPE | 12 | 2 | 3 | 2 |
| Gentoo GEPE | 12 | 2 | 4 | 2 |

各種内で**全く同じ3期共通地点**の巣数中央値を各期別に合計1へ正規化した相対構成・加重緯度で比較。前回の1990s→2000sと2000s→2010sで使用地点集合が違う表をつないだものではない。

| 種 | 巣数重心1990s→2000s南向きkm | 2000s→2010s南向きkm | 1990s→2010s合計km |
|---|---:|---:|---:|
| Adélie | **+99.554** | **+7.757** | **+107.310** |
| Chinstrap | +2.950 | +3.115 | +6.065 |
| Gentoo | −6.534 | +7.555 | +1.021 |

同じ地点集合なので、2つの十年期の加重緯度差は20年間の差に算術的に望みどおり加算できることを確認。アデリーの+107.31 kmは以前の**両端期のみ観測が条件**の26地点の+88.41 kmと分母が違い、そのまま比較した正味の変化・生物学的速度の違いではない。どちらも真の分布重心・個体の移動ではない。

## 2. 対応する海上60%前線の位相（同じ共通19地点と原経度区間）

| 時期 | アデリー19地点の巣数加重南北変化 | 対応5経度区間の海氷60%前線南北変化（時点初めの巣数重み） |
|---|---:|---:|
| 1990s→2000s | **+99.55 km** | **+7.10 km** |
| 2000s→2010s | **+7.76 km** | **+31.81 km** |

- **位相の不一致**は数値で記述できる。海氷前線の後退に対して巣数が遅れて同じように移動したとは見えない。むしろこの統計では巣数の再配分が初期に大きく、marine front の変化は後期に大きい。
- ただし、全経度区間を通る海氷前線の緯度、対応サイト間の重みづけ緯度、そして各サイト100km内の海氷曝露は**別の物理的・生物学的空間指標**。この表の2列を引き算した数字は、生物の気候追跡成功・失敗・実移動の距離・気候負債ではない。
- ヒゲとジェンツーは各2経度区間しかなく独立な front lead/lag replication として不十分。特に海氷前線が2区間で同調していることは2つの気候実験を意味しない。
- 全南極の36経度区間では1990s→2010sの60%等値線は17区間で南進、19区間で北進（中央値−7.26 km）。**南極一様の「温暖化前線が南へ動く」前提は実測に合わない**。

## 3. 繁殖巣数変化と先行/同時海氷変化（別のラグ仮説）

固定同一地点について、2000s→2010sの元巣数中央値の log1p 差を応答とし、
- earlier = 海氷2000s平均−1990s平均（先行する海氷変化）、
- concurrent = 海氷2010s平均−2000s平均（同時期の海氷変化）、
- forbidden future control = **過去1990s→2000sの巣数差**を **後の2000s→2010s海氷変化**に照合（生物因果的には未来）。

すべて同じ地点・同じ元地域で地域平均を引いた**地点を1票とするPearson r**で、相関の符号を保って比較。地域内同種1地点だけの地域は相関に情報を与えないため除いた。

| 種 | 3期共通サイト | 地域内相関に寄与するサイト/地域 | earlier の r | concurrent の r | future負対照 r |
|---|---:|---|---:|---:|---:|
| **Adélie** | **19** | **18地点/3地域** | **+0.4803** | +0.2704 | −0.2146 |
| Chinstrap | 12 | 12地点/2地域 | −0.1415 | +0.2537 | −0.2023 |
| Gentoo | 12 | 12地点/2地域 | +0.0083 | +0.1517 | −0.0487 |

アデリーは**先行SIC変化との記述的な絶対相関が+0.210大きい**。これは既存データにおける探索的な発見だが「10年の時間ラグが特定できた」「遅れの因果方向が確認された」とは言えない。時系列3期・地理の極端な偏り・海氷の季節・採餌海域・繁殖年同期欠如を埋めていない。

### 地理感度が決定的

Adélie earlier r=+0.4803 の
- 250kmブロック1個を除いた signed r 範囲：**+0.2144〜+0.6302**。
- 元地域1個を除いた signed r 範囲：**−0.3849〜+0.5465**（符号反転）。
- concurrent r=+0.2704 は block 1個除外：**−0.3351〜+0.5289**、元地域除外：**+0.0343〜+0.3010**。
- 逆時間の負対照 r=−0.2146 は block除外：**−0.6048〜+0.5710**、元地域除外：**−0.3036〜+0.6841**。空間構造から見かけの time-directed 相関が生まれうることを排除できない。

**判定: DESCRIPTIVE_EARLIER_SIGNAL_CHANGES_SIGN_AFTER_REGION_OMISSION**。
Chinstrap/ Gentoo はわずか3/4固定250kmブロックしかなく厳格地理分割の比較は支持不足。二種で earlier 優位の兆候はない。

## 4. 実観測年差の監査：十年遅れは「正確な10年遅延」ではない

| 種 | 実計数年中央値1990s / 2000s / 2010s | 地点ごとの実観測年中央値差 (前→中 / 中→後) |
|---|---|---|
| Adélie | 1995.5 / 2005 / 2015 | **9.5 / 10.0 年** |
| Chinstrap | 1997 / 2005.75 / 2014.75 | 9.5 / 7.25 年 |
| Gentoo | 1997.25 / 2005 / 2015 | 7.0 / 8.75 年 |

アデリー19地点のうち、実調査年中央値の前→中間隔が5年未満は1地点、後半は0地点。しかし、観測密度が限られ、本研究の earlier SIC は10年平均どうしの差、nest response はそれぞれの期間内で非同時の元計数年中央値に基づくので、**反応遅延を5年／10年と点推定することはできない**。

## 5. 既報との違い、今後の判定

2026-03-18のFoster-Dyerほか（Proc. R. Soc. B, DOI 10.1098/rspb.2025.2431）は、**コウテイペンギン**のロス海7コロニーにおいて、5年前の冬春海氷異常と繁殖地来訪数指標の年次変化の関連を報告している。今回のAdélie/Chinstrap/Gentooは別種・別環境指標（原SIC10年平均差）・別応答（非同時計数の巣数中央値差）であり、5年の生物機構や同じ海氷選択圧を流用しない。

最終判定を以下に分ける。
1. **YES, descriptive geographic mismatch:** Same sampled Adélie colony-network nesting allocation and offshore ice contour have different timing at broad decade resolution, with independent original source checks and exact three-period roster.
2. **YES, exploratory historical-ice association:** Adélie later nest changes have greater region-demeaned association with earlier than concurrent nearshore SIC changes on this restricted roster.
3. **NO, established climatic debt / 5- or 10-y lag:** Regional deletion reverses earlier association; only 18 informative sites in three regions; no independent chronological/region holdout; no biologically preferred SIC front, true colony absence or known breeding dispersal, no independently calibrated future warming/vegetation mediation.

Do not resume p-value/threshold/lag-length fishing. A meaningful subsequent study needs at least two independent regional multi-year same-method cohorts with identical census effort and a physiological or foraging-based sea-ice niche reference, or independently followed individuals and a validated time series of establishment/absence. Before those, integrate as one **timing and metric mismatch** panel in the single Antarctic macro paper. This does NOT prove that global warming does not affect penguins; it shows what these original broad observations identify and do not identify.

## Exact reproducibility
- [Draft PR #214](https://github.com/zuizui0223/mina/pull/214)
- [Successful frozen 3-decade original source / negative-time-control Actions run #42844104869](https://github.com/zuizui0223/mina/actions/runs/42844104869); artifact ID **13776484021**
- [Successful original full-grid marine 60%-SIC front #42791019321](https://github.com/zuizui0223/mina/actions/runs/42791019321); original sector data artifact IDs **13751339300 / 13751339305**
- Frozen same-roster design: FROZEN_THREE_DECADE_CLIMATE_LEGACY_GATE_20261111.md
- New genuine input analysis: test_three_decade_climate_legacy.py
- Exact synthetic independent tests: unit_test_three_decade_climate_legacy.py
- Existing primary original source: macro_panantarctic_v1/build.py and analyze_decadal_fixed_network_reweighting.py

Paper 1, Paper 2, main and the older warming manuscript v0.6 remain untouched. No automatic merge.
