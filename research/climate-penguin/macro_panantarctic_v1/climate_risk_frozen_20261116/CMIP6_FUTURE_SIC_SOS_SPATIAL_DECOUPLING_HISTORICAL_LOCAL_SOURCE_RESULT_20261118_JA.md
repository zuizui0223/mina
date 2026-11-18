# 温暖化で海氷が後退しても低塩分化の「場所」は一意に決まらない：南極595繁殖地点のCMIP6 3モデル×4シナリオと過去の近岸海域支持

**2026-11-18 JST | mina Draft PR #214 | 真正原本再現済みの沿岸マクロ物理結果。** 原source全595地点に観測巣数があるとは仮定しない。将来のδ¹⁵N・実食性・営巣巣数・移動／絶滅を推定しない。既存main、凍結済みEcology Report/Paper2、v0.5本文/主4図は変更しない。

## 1. 中心となる新しい実計算

**SSP5-8.5、2081–2100年（各モデルの1995–2014年historicalからの差）：海氷変化ΔSICと表層塩分変化ΔSOSが、どの繁殖地で共に大きいかという空間相関の符号はモデル間で一致しない。** 全595同一site IDを一票とし、地域差を除いた原region within-site相関および重複の多い元CMIP6モデルsos native grid cellを同じ元source region内でまとめた相関は次の通り。

| 原モデル（1 member/model） | 595 site等重み raw r(ΔSIC, ΔSOS) | 18元地域内site等重みr | **原model海洋cell×regionを1票にした地域内r** | native SOS unique cells |
|---|---:|---:|---:|---:|
| **ACCESS-CM2** | **+0.743** | **+0.709** | **+0.404** | 103 |
| **BCC-CSM2-MR** | **−0.296** | **−0.332** | **−0.178** | 87 |
| **CESM2** | **−0.333** | **−0.079** | **−0.350** | 98 |

18元regionを一つずつ除いた18通りのsource within-region再計算では、**3モデルとも元の相関の符号は18/18維持**。ただし本来の観測コロニー数595が595独立GCM海域という意味ではなく、CMIP6の粗いモデル同一格子の重複による影響がある。元site等重み vs model独立格子に近い集計で相関の大きさが変わるが、3モデルの互いに異なる方向は維持される。相関の符号は場の地理的共分散であって、海氷形成・融解の塩分因果係数ではない。

3モデル**平均**の将来SOS変化は全595 siteで負、同時に海氷も減るところに3モデル合意したsiteは384/595。しかし、モデルごとの`ΔSIC–ΔSOS`空間結合の向きが逆である以上、**アンサンブル平均だけを見て「海氷後退と海洋淡水化が同じ強さで同じ場所で生じる」とは言えない**。これは物理二軸を分ける重要な結論。南極の種別気候応答や因果経路を示したわけではない。

## 2. 12通りすべての元モデル×SSP×将来期間を固定検証

下表は元siteごとに各モデル差を計算し、18元regionの平均値を物理2変数それぞれから除いた**within-region r**。右列は同じ元モデルの`SOS native grid cell×region`を一票にしたr。モデルによって同じ地域内でも場所の物理変化の対応が異なり、ACCESS-CM2は途中から符号が変化する。モデル分散・不確実性の記述であって「将来の確率」や生物種の適応差ではない。

| SSP／将来期 | ACCESS site / cell | BCC site / cell | CESM2 site / cell |
|---|---|---|---|
| SSP2-4.5／2041–2060 | −0.316 / −0.085 | −0.353 / −0.263 | −0.649 / −0.391 |
| SSP2-4.5／2081–2100 | **+0.110 / +0.307** | −0.463 / −0.206 | −0.347 / −0.398 |
| SSP5-8.5／2041–2060 | −0.315 / −0.105 | −0.217 / −0.132 | −0.645 / −0.420 |
| **SSP5-8.5／2081–2100** | **+0.709 / +0.404** | **−0.332 / −0.178** | −0.079 / −0.350 |

各12 source model scenarioについて地域を1つずつ除外（18パターン）、**216検算すべてで元site-region-within rの符号は維持**。ただし同じデータでの感度であり、216独立気候観測や一般化の確証検定を意味しない。

## 3. 過去の海洋環境を局所に再現する精度も、塩分と海氷で異なる

CMIP6のモデルhistorical 1995–2014、8–11月の平均`sos`と`siconc`を、**元と同じsite ID／同じ20年／同じ月**で原GLORYS12V1近岸`surface salinity`とOSI SAF観測源の100km海氷へ結合した別source監査の結果も一緒に算術再現。オリジナル588site、18region、GLORYS distinct wet cells378。これは**歴史期間の地理的な平均場の対応**であり、CMIP6の内部変動の年別一致でも、未来変化のskill testでもない。GLORYSも再解析であり、海水の独立in-situ観測ではない。

| 1995–2014の実source空間対応 | ACCESS | BCC | CESM2 |
|---|---:|---:|---:|
| 海面塩分 raw 588site r | +0.384 | +0.679 | +0.522 |
| **海面塩分 within-source-region site r** | **+0.204** | **+0.208** | **+0.248** |
| **海面塩分 within-region unique GLORYS cell r** | **+0.178** | **+0.194** | **+0.258** |
| 海氷 within-region site r | +0.676 | +0.367 | +0.610 |
| 海氷 within-region GLORYS cell r | +0.673 | +0.346 | +0.595 |
| model − GLORYSの塩分平均差 | +0.076 | −0.059 | −0.440 |
| model vs GLORYSの塩分サイトRMSE | 0.257 | 0.198 | 0.507 |
| model − OSI SAFの海氷平均差 (pp) | −13.215 | −14.348 | +11.407 |

**3モデルとも、同じ近岸source報告地域内の塩分の地点差に対するrが海氷のrより小さい。** GLORYS 378 unique wetcellを等重みとしても同方向。地域1つ除外後もsource site-local r(SIC)−r(SOS)>0は18/18で、源の物理空間粒度を揃えた単純な情報支持の差は残る。ただし相関指標の差を「CMIP6海氷の将来予測skillが塩分より厳密に高い」と断言しない。海氷と塩分で観測誤差・実空間平滑化・物理応答スケールが違う。

**物理予測の解釈に必要な線引き：** 3モデルmeanの長期SOS低下は物理変化の独立した候補として報告できるが、局所海域の`sos`の絶対値や局所負荷量、海氷-塩分の同所推定を生態的なシナリオ発症予測にするには、元GLORYS・海氷の測定支持とモデル格子およびモデルの歴史偏差が無視できない。過去の塩分絶対値のズレは、未来`Δsos`の符号を形式的に否定するものでもない。

## 4. 生態論文へ統合する位置

- **既存の全源物理肯定結果**：原588の海洋PC1＝温度–海氷軸60.3654%、塩分主体PC2＝33.3773%は維持。これは過去の観測・再解析データが示す独立した共分散構造の記述で、塩分の因果独立性までは示さない。
- **生物の塩分肯定結果も維持**：原Youngflesh Landsat 860 source site×seasonでδ¹⁵N光学proxyの塩分に対する条件付きβ=+0.8341458422‰/塩分単位、partial R²2.88018%。13地域単位の保守的区間は0を含み、別データの未来予測へ直接外挿しない。
- **今回新しく確かめた点**：元将来3モデル×4シナリオの物理分布では、海氷減少–低塩分化の対応自体が**モデル・年代に依存**し、historicalのlocal塩分平均場再現は海氷より相対的に弱い。よって「海氷は巣数を動かし、塩分は食性を動かす」等のモデル由来単一機構を作らない。SIC/sosを別々に図示し、同時符号一致をsite数／実計測巣数proxy重みと合わせて示す。
- **不支持**：未来のδ¹⁵N値（元δ¹⁵N画像はNov–Febに観測、GCMはAug–Nov）、魚/オキアミ率、生残、地域移住、繁殖巣数、植生の将来緑化。旧δ¹⁵N–塩分のβを単純にCMIP6未来`sos`へ掛けて予測しない。CMIP6`tas`は大気温であり、元GLORYSの海水温`thetao`ではない。

**論文一文案：** “Projected sea-ice loss and surface freshening broadly co-occur at Antarctic penguin breeding-site locations, yet the spatial coupling of these changes reverses across climate models and is less well resolved for historical local salinity than for sea ice.”

## 5. 原本再現と変更範囲

- 2026-11-16元の本真正CMIP6 27 remote store source (3 models / 3 variables / historical +2 SSP ×2 future): [#43845907301 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/43845907301) artifact 14214704362, raw 21,420 source model×site×variable×scenario row。
- MAPPPD元595site original inventory: [#42610664607 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/42610664607) artifact 13669533413。
- 元588 GLORYS＋OSI SAF historical同期間のsource model comparability: [#44239541320 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44239541320) artifact 14397794445。
- **今回**再現Python [audit_future_sic_sos_spatial_coupling_and_historical_support.py](audit_future_sic_sos_spatial_coupling_and_historical_support.py)、[#44244226558 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44244226558) artifact **14400524546**。原3source ZIP SHA256ピン照合、将来source原site×変数21,420行／SIC-SOS sourceペア7,140行／3model×4scenario＝12表、18地域の1地域除外計216ケース、588元site×378 GLORYS wetcellの歴史比較3表、検算PASS。
- 出力はfuture12 model scenario spatial grain table、historical3 model × SIC/SOS source support table、機械可読監査JSON。raw 27 Zarr store自体は複製せず、原作者sourceのダイジェストのみ残す。

**最終判定**：海氷減少と沿岸低塩分化は同じ単一軸に縮約せず、時期・空間粒度・モデルの違いを軸として示すことにマクロ的な情報がある。ただしこれは**物理的な気候変動の構造**を検証した結果であり、ペンギン食性/巣数変化の普遍機構の確認ではない。
