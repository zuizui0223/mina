# 非MaxEnt巣数SDMと「年次植生」原画像検証（2026-11-09）

**最終状況：実巣数GAMと負の二項GAMは動作・検証済み。ただし海氷効果は分布族・地域で不安定。海氷×巣数×静的植生の25地点データは結合済み。新たに原Landsat 8から年次の光学反射率を取得し、比較可能な夏季NDVIペアは2地点3組、厳密な12月同月は1地点1組。これは*植物の年次緑化*を実証するものではない。**

> **本日の追加判定（元Plantarctica 87,391ポリゴンを本当に取得して照合）：** [原Landsat 8固定154位置の植物分類と最終NO-GO](ORIGINAL_PLANTARCTICA_L8_BOTANICAL_OVERLAY_RESULT_JA_20261109.md)。真正の原植物ベクター（SHAを固定）との比較で、厳密に12月を揃えたInexpressible IslandのNDVI比較13地点のうち、2024版植生/地衣類の地図に重なる点は**0**。Cape Crozierの夏季比較6地点には各1点が植生地図に重なるものの、月揃えでは比較不成立。**`BOTANICAL_SOURCE_SUPPORT_TOO_WEAK`**。これは植物の真の不在ではなく、400m間隔の疎な点と小パッチの空間不一致、および元図が2017〜2020各年の植生を測っていない制約による。ここから統合SDMに新規の有意な緑化応答を追加しない。[実行CI #42610756412](https://github.com/zuizui0223/mina/actions/runs/42610756412)／[元154位置の分類artifact](https://github.com/zuizui0223/mina/actions/runs/42610756412/artifacts/13670666086)。

## 直近に実際に完了した作業

1. [原50地点×繁殖季のUSGS Landsat 8 QA/NIR/red取得と結果](ORIGINAL_LANDSAT8_YEARLY_SPECTRAL_RESULT_JA_20261109.md)。元の50地点×年に対し**150サイト×シーン読取（64ユニーク元シーン）**が成功。77固定地理位置×150読取＝11,550測定候補、QA・反射率通過983。
2. 対応する巣数計数の実年で比較できる候補33組のうち、**夏季全体で3組／2地点**（Cape Crozier西部2017→2018、2018→2019、Inexpressible Island2018→2019）。**厳密な12月同月で1組／1地点**（Inexpressible Island13位置）、差の符号が夏季全体と異なる。
3. [取得スクリプト](acquire_original_landsat8_seasonal_spectra.py)、[元画像の同一月品質監査](audit_original_l8_same_month.py)。本体[Actions成功 #42608609143](https://github.com/zuizui0223/mina/actions/runs/42608609143)／[元全画素QA artifact 13669078857](https://github.com/zuizui0223/mina/actions/runs/42608609143/artifacts/13669078857)。別コードの[12月固定月品質検査成功 #42609671701](https://github.com/zuizui0223/mina/actions/runs/42609671701)／[artifact 13670170765](https://github.com/zuizui0223/mina/actions/runs/42609671701/artifacts/13670170765)。
4. [現代の3資料を結合した63観測／25地点の同時位置資料](JOINT_ICE_VEGETATION_AND_ANNUAL_SUPPORT_RESULT_JA_20261109.md)は、**年次ではない2017–2023年Plantarctica合成図**が元の限界。元の同一地点年の3種計数は5地点年だけ。
5. [観測巣数GAMの初回結果](RESULT_JA_20261109.md)、[整数巣数の負の二項尤度検証](NEGATIVE_BINOMIAL_RESULT_JA_20261109.md)：海氷項ADPE近似pはGaussian対数変換時0.0000666、元整数巣数NBでは0.07075、Victoria Land除外NBでは0.65155。モデルを変更して有意pを救済する作業は停止。

## 現在の主線と次の一つの作業

**原Plantarcticaポリゴン照合は完了し、固定77点×2地点では植生の年次変化を測る支持が不足することが確定。次のデータ要件は、すでに地図化された小さな植物パッチを独立に固定したROIで10m級の元画像・同月・複数年・雪/裸地対照をそろえられるかの調査であり、現行の巣数SDMに「緑化」変数を足すことではない。**

最初の対象は厳格な12月検査を通過した**Inexpressible Island 13地点**。Cape Crozier西部の夏季6地点は比較時期が揃わず、植物の増減解釈から外す。静的地図上で植物に分類されなければ、元のNDVI年差を植生変化とみなさず終了する。静的ポリゴンで植物と一致したとしても、それだけでは2018〜2019年の生物量変化を示さない。

**STOP規則：** 同じ地点・同じ元画素の植物検出が独立して確認できない限り、これ以上GAM/SICラグ/MaxEnt/INLA/JSDMの分布族を変更して有意結果を探さない。温暖化による海氷後退→緑化→海洋・陸ニッチ移動の因果連鎖や2041〜2100年巣数予測を確証したと主張しない。

**作業場所：** `codex/penguin-nonmaxent-abundance-sdm-20261109`（Draft PR #213）で保留。本線PR #206、元の統合原稿v0.6、`main`、凍結Paper1/2は変更せず、原データの正当な支持のあるところまで独立に検証する。
