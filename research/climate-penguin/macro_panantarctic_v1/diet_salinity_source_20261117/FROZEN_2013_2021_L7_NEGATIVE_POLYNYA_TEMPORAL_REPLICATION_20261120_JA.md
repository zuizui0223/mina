# 2013–2021年の未使用画像による「冬ポリニヤ→翌夏の光学δ¹⁵N負方向」時間外追試：事前凍結

**2026-11-20 JST | PR #214 実測ポリニヤ派生仮説の独立検証契約 v1 | 後年の衛星シーン検索・反射率の開封・新係数推定に先行して凍結する。** 旧主原稿、main、Ecology Reportおよび旧原著データは変更しない。

## 発見標本と帰無仮説を分ける

- **発見側（再検定禁止）**：元Youngflesh原Landsat由来の optical δ¹⁵N *proxy*、2004–2010 source season、439 original site×season/85 original site/11 reporting regions。DEEP-AA v1.1.0-2023、6–10月100km geodesic沿岸ポリニヤ実測、現地site+原region×season効果／DOY,DOY²・翌夏11–2月NSIDC SIC・GLORYS水温・塩分調整で `M_SP` β=-9.2161‰/曝露面積比1.0 (=10percentage-pointsあたり-0.9216‰)。11地域cluster t(10)95%区間[-13.493,-4.939]‰/比1.0。元の正方向仮説は失敗、負方向は探索による**事後発見**。[元再現CI](https://github.com/zuizui0223/mina/actions/runs/44547277067)。
- **新たに前向きに評価する方向はひとつだけ：負方向**。2013–2021の新しい2013年11月–2022年2月間のLandsat 7 ETM+（同じ衛星・同じ6反射バンド・同じ103標本5成分PLSR校正）から生成した optical δ¹⁵N proxy が、本当に2013–2021同年6–10月DEEP-AA沿岸ポリニヤ実測面積比と **負** に関連するか。
- **2012以前の元作者Landsat画素、既存860/439のδ¹⁵Nと同年の物理量を新標本に混ぜない**。2013年が元作者論文の「1984–2013」という表記と重なるかは原著のseason/date単位で検証し、同じシーン・日付があれば厳格除外する。新規衛星画素を使っても同じ103校正標本は再使用するため、「新しい同位体実測」ではなく**時間外の衛星画像検証**と呼ぶ。

## 最初に実行する出典・観測可能性のゲート（生態結果や新反射率を未使用）

1. 対象地点は旧sourceの**88 original colony IDs/元MAPPPD真の繁殖地点座標**のみ。別殖民地・他の調査地点・事後的な立地選択を含めない。原MAPPPD Atlas (artifact 13669533413)とYoungflesh原画像地点重心 (artifact 14324288144)のsite ID/距離≤2kmの地理整合を以前と同じ方法で確認。
2. **Landsat 7 ETM+ だけ**をUSGS Collection 2 Level-2からmetadata-onlyで真のscene footprint/撮影日・処理レベル・Collection・instrument/scene IDごとに調査。2013–2021のNov–Feb新規season 9年、同一date/scene重複排除、元Author raw archive 1984–2012（作者説明は1984–2013）とのオーバーラップ検査。**Landsat 8/9 OLIとSentinel-2は、この契約では使わない**。
3. **重大な事前リスク**：USGSは2013のLandsat 8運用開始後、Landsat 7がAntarctica、孤立島、外洋を**体系的に観測しなくなった**と明記。衛星稼働2021≠原88地点への2013–21データ供給。Scene footprint「候補数」と、下記のSLC-off/雲/ギャップを通過した真の糞ピクセル数を別記。定常撮影でない観測努力を年0のδ¹⁵Nとして代入しない。根拠: [USGS Landsat 7](https://www.usgs.gov/landsat-missions/landsat-7)。
4. 原著Youngflesh 2026の公開 source pipelineの**正確な島・コロニー糞画素選択領域・6バンド対応・品質マスク**を同一条件で引き継げることをソースで先に検証。元RDSに画素の真位置がなく同じ糞被覆判別ができない場合は `NO_GO_GUANO_ROI_UNREPRODUCIBLE`、恒常的な基地周辺pixelを糞と自称しない。USGS Collection2 Level-2 scaling/QAと原著旧データの反射率単位を直接照合する。PLSRの5成分・103元標本・L7の元RSRは**完全固定**（元Python sklearn PLSRegression(scale=False)で元Yと同じ再実装。新画像で係数、センサー分光較正、補正係数を再学習しない）。Collection 2画像の処理差で同一測定量に換算できないなら `NO_GO_SENSOR_PROCESSING_INCOMPARABLE`。
5. **SLC-off**（2003–）scan gaps / cloud / cloud-shadow / snow / saturation / fill / QA不適合の各pixelをnative QAで除く。補間・inpainting・他年モザイク・旧画像から穴を埋めない。日ごとに有効に抽出された本物のguano pixel n、画像scene ID、独立撮影日数を保存。元著者の `mean(n_pix)>=2` を元site eligibilityに適用する。site×seasonの少なくとも1本の実撮影日・その各日2有効guano pixelsを最小条件とし、元の画像選別をより厳しく変える場合は生態効果を見る前に固定して別名記録、**後から閾値を下げない**。複数シーンを得る地点のdate-equal平均を本解析Yにする。
6. 気候先行時点はsiteのseason開始年 y の6月1日–10月31日。真の `SIC60_6.25km_20d.zip` 原DEEP-AA v1.1.0-2023 (MD5 `f3f958389cc5e67ac1c4e3a6ee164318`) のEPSG:3412原native gridから、旧検証コードと**同一**100km測地圏内の正の偶数IDだけを沿岸ポリニヤ分子とし、同じ海域分母・面積重みで計算する。毎月80%以上の実日別ソースを持つ5か月のみ完全冬季。25kmは事前の説明用だけ。海氷・水温・塩分は元実現のNov–Feb/同一sourceモデル・原wetcell基準で同時期の再抽出を行う。時間・地理の代替ラグは無し。
7. **応答を開く前のゲート**：実撮影日から有効pixelが得られ、真DEEP-AA冬季が5か月揃い、同年Nov–Feb SIC・GLORYS `thetao`・`so`が同一site×seasonで揃う行について、独立 site≥30、元 reporting region≥6、別の source season年≥4、Victoria Land≥3 sites、Wilkes Land≥3 sites、Southwest Antarctic Peninsula≥3 sites、かつ少なくとも2季で撮影されたsite≥20。地域内に独立のsiteの反復がない場合はNO GO。**この条件は検証精度の保証ではなく最小支持**。不達なら `NO_GO_L7_2013_2021_GEO_TEMPORAL_SUPPORT` を出力し、δ¹⁵N係数は**推定しない**。
8. catalog API/cold storageの403/429/timeout/一時障害は `DATA_SOURCE_UNVERIFIED` と報告。0件と区別するため過去2005–2010年の同一siteについて**真の既存L7 imageryに対応するscene hit**を陽性コントロールで検証。独立カタログで同一sourceの0件を確認するまで後期の無撮影を断定しない。

## 完全な新画像の品質・実験独立性が確認できた場合だけ：唯一の確認検定

- 主解析式と4モデルは2019昨日のモデルを**変更せず**：`M0 = δ15N_proxy ~ DOY + DOY² + Nov–Feb SIC + Nov–Feb thetao + site FE + original region×season FE`; `M_S=M0+summer so`; `M_P=M0+winter observed coastal polynya 100km`; **`M_SP=M0+summer so + winter 100km observed polynya` (主モデル)**。追加の地域特異ラグ・半径・非線形・閾値・相互作用は結果を見て入れない。
- **成功条件を2層**：主条件は未見9 seasonだけにおける `M_SP` の β_P<0 **かつ**地域cluster保守的 t(df=regions−1)95% CI上限<0、元報告地域を1つずつ除いてもβ_P<0。整合性条件として `M_P` も β_P<0 を報告。反転またはCIをまたげば `NO_GO_TEMPORAL_REPLICATION`。これは現象の新期間**観測内関連の方向確認**であり独立した因果推定ではない。
- 同じsource/同じsite×seasonで各モデルの残差説明率とregion cluster CIを報告。過去の発見標本から係数を推定したまま未来の新proxyのRMSEを比べる厳格な真正時間予測は別指標で、`M0/M_S/M_P/M_SP` を**過去2004–2010だけでfitして未来2013–2021のみでscore**（利用可能site/interceptのみ）する。不足で推定不能なら無理に補わない。RMSEを改善しなくても主効果の独立年での符号再現は示せるが、「予測改善」は主張しない。
- 新シーン欠測・欠損は0・平均・近傍画像で補完しない。**非撮影年には生物応答が存在したと主張しない**。新しい2013–2021年は地理的な新地域実験ではないため、地域効果と生態機構には依然制約が残る。
- 「δ¹⁵N低下は一般にオキアミ利用側と整合」は**元103標本食性較正に依存する生態的解釈候補**。海洋粒子状窒素・硝酸利用率の基準同位体が常に上昇するとは証明されていない。ポリニヤ周辺でのPOM δ¹⁵N実測/採餌場所/実餌を追加せず、`baselineでは説明しにくい→確定した食性シフト`とは書かない。

## 決定と発散防止

- `PASS`：同条件で負方向再現、独立年月の頑健な観測関連として論文の主候補に昇格する**権利**がある。ただし実餌・基準同位体・個体移動・長期気候原因を未同定と明記。
- `NO_GO`：新L7供給不足は「仮説が否定された」ではなく**独立テスト不可**。負方向不再現は「探索方向の時間外再現を確認できず」、独立再現済みとは主張しない。パラメータを後から探して陽性化しない。
- 既存本文に直接上書きしない。調査主線の温暖化/海氷/繁殖空間の結果は維持。8/9/10/11を混ぜて日付だけ未来にした検証を「同センサーの独立検証」と呼ばない。
