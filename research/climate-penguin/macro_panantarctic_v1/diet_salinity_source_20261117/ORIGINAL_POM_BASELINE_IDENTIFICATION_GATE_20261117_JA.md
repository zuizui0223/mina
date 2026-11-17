# ペンギンδ15N–塩分：食性と窒素同位体基準値の識別ゲート

2026-11-17 JST | mina draft PR #214 | 補助探索・原資料独立監査。main / Ecology Report / Paper 2 / v0.5の本文・主図を変更しない。

## 結論

**同一繁殖地・同一季節に対応する実測POM基準値が少なすぎる。塩分とδ15Nの正の関連が食性変化なのか、食物網の同位体基準値変化なのか、現資料では識別できない。**

## 独立原資料

St John Glew et al. (2021) Global Biogeochemical Cycles, DOI https://doi.org/10.1029/2020GB006901 。公開GitHub https://github.com/KatieSJG/SO_isoscape から元Appendix A.csvを原Git blob SHA1 e44eb37cd772781b986e1a1776cf104eaaddd716 で固定。全3360行のうち実δ15Nを有するPOMは2718。今回のペンギン繁殖開始年1996–2012に合わせ、11–12月=t年・1–2月=t+1年に対応する実POM標本は802件、725異なるstation key、9原研究ID。ペンギン側はYoungflesh et al. (2026) Zenodo originalに基づく860 site×season、88 source sites、82 GLORYS wet cells、13 source reporting regions。元MAPPPDの真の地点座標とPOM測点間をWGS84楕円体測地距離で算出。

| 同一実繁殖季節のPOM観測を許容する距離 | 対応site×season | 対応site | 元地域 | season | POM stationが3以上のsite×season |
|---|---:|---:|---:|---:|---:|
| 50km | 5/860 (0.58%) | 5 | 1 | 1 | 1 |
| **100km** | **20/860 (2.33%)** | **20** | **3** | **3** | **8（1地域、1season）** |
| 250km | 37/860 (4.30%) | 37 | 5 | 4 | 29（3地域、3season） |
| 500km | 65/860 (7.56%) | 52 | 6 | 5 | 46（4地域、4season） |

100kmの20 site×seasonは**20の異なるsiteに各1season**、250kmでも37 site×seasonは37の異なるsiteに各1seasonである。したがって、元の固定地点内で変動するδ15N proxyと同時期にPOM baseline変化を直接補正できる時系列は**0**。250km以内の重複371 site–POM対応も独立POM source stationは**59**、StudyIDは**3**、seasonは**4**。371反復とは呼ばない。

事前固定したゲート：100km以内で異なるPOM stationが3個以上あるsite×season 344/860以上、独立3地域、6season以上。実際は8/860、1地域、1seasonで不合格。未採取年、遠方500km、一つの季節平均POMマップを「その年の局所基準値」として補完しない。

## 既存の正の関連の識別感度

先行の860 source固定モデルは同一site・地域×season・観測日・海氷・水温調整で塩分β=+0.8341458422 δ15N‰ / salinity unit、残差partial R2=2.88018%。site・region×seasonの残差塩分SD=0.2230なので、塩分1SDに対応するδ15N線形差は0.8341458422×0.2230=**約0.186‰**。光学δ15N proxyの原103校正試料に対するランダム留保RMSEは約1.7‰（各個別標本の予測誤差であり、サイト平均や傾きの標準誤差ではない）。

概念的な加法分解では、同位体基準値や光学計測由来の偏りが塩分1単位当たり+0.834‰だけ条件付き共変動していれば、食性効果がゼロでも上記の傾きが観測できる。**これは仮定上の境界計算で、実際のPOM baseline–塩分係数を測定した結果ではない。**

前回の同一source空間検査では、実海洋格子R2 2.880%、同地域内1000回の湿潤格子全時系列入替え中央値R2 0.116%。ただし時間の負対照では、観測当年塩分β+0.809に加えて翌年塩分β−0.653が残った。これらはlocal環境と同位体proxyの統計的関連を示す一方、実採餌変化、局所同位体基準値変化、海流・画像処理交絡を区別しない。

## 誤った修正をしないための限定

St John Glew et al. 2021の季節isoscapeは空間・季節の**気候学的予測**であり、1996–2012の各site×yearで実際に観測されたPOM同位体基準値ではない。site固定効果のある年次モデルに静的site baselineを入れても、時間的な同位体基準値の情報を増やさない。

独立のUSAP-DC DOI https://doi.org/10.15784/601210 は2007/2009南シェトランドと北南極半島のオキアミδ15N/δ13C観測を含むが、他地域や年を補完しない。今の860ペンギン系列を新しい食性「因果」または温暖化→魚食率→将来繁殖数の経路に昇格するのは禁止。

## 再現

- 原POM同季節・地理照合 GitHub Actions #44091101888 SUCCESS: https://github.com/zuizui0223/mina/actions/runs/44091101888。Original source Git blob SHA検証・POM欠測区別・元860 ID/季節/595原地点検算・50/100/250/500km距離別補助集計。artifact 14331772347に派生coverage・研究ID・地理対応だけを保存し、第三者原POM CSVを再配布しない。
- 再現コード：audit_pom_baseline_overlap.py（本ディレクトリ）。
- 860同位体proxy×塩分 GitHub Actions #44083346932、およびsource-fixed空間・逆時間診断 #44088674449は不変更。

**判定：baseline-adjusted annual macro slope＝NO-GO。** 真の同じ採餌期間・海域でのPOM/krill同位体基準値または直接魚・オキアミ利用、CSIA-AAが反復して測定されない限り、基準値や食性の因果方向を論じない。
