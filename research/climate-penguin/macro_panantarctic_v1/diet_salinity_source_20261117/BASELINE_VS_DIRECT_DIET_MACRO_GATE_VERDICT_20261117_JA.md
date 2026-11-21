# 南極ペンギンの食性×塩分機構：POM基準値とSCAR直接食性を独立原資料で検証した結果

**2026-11-17 JST | mina PR #214の補助ソース監査 | データ入手と原本の厳密な母集団照合は完了、統一機構はNO-GO。** 凍結済みEcology Report/Paper 2、主論文v0.5、旧βや元の4図を変更しない。

## 最も重要な結論

これまで南極広域で「塩分→魚／オキアミ利用→繁殖の変化」を明確に推定できなかった理由は、δ15Nと食物網基準値を原理的に区別する観測が十分ないことに加え、実際の餌種を測るデータの厳格な同年・同地点支持が、データベースの全行数から大きく縮小するため。

### A. 実POM δ15N基準値の照合

- 原POM: St John Glew et al. 2021, *Global Biogeochemical Cycles*, DOI https://doi.org/10.1029/2020GB006901 / https://github.com/KatieSJG/SO_isoscape 原Appendix A.csv、blob SHA1 e44eb37cd772781b986e1a1776cf104eaaddd716。
- 元3,360行中δ15N有効POM2,718件、元の860アデリーLandsat δ15N proxyと繁殖開始年1996–2012の11〜翌2月で重なる実POM802件。ただし距離を真WGS84測地距離で合わせると **100km以内20/860 (2.33%)、250km以内37/860 (4.30%)**。100km以内に異なるPOM stationが3個以上あるのは**8地点×season、1地域・1season**。
- 100kmの20地点×seasonは20の別site、250kmの37地点×seasonは37の別siteで**同じsiteの複数季節POM観測が0**。250km内の371二者対応も元POMの実ステーション59個・3source StudyIDs・4季節であり371独立反復ではない。
- 記述的な元δ15N proxy×塩分係数は β=+0.834‰/salinity unit（860 site×seasons、82 wetcells、13地域、同じ11〜翌2月、siteとregion×season FE、海氷、水温、DOY調整）。GLORYS塩分のsite+region-season残差SD0.223に対応する予測同位体差は**約0.186‰**。その程度の未測定のδ15N baseline共変動だけでも解釈は変わり得るが、**その実測baseline係数を今回推定したわけではない**。
- 2021年の公開「年平均・4季節isoscape」は地理的・季節的なclimatologyであり、source 860 site×各年の時間変動を測る観測ではない。時系列の欠測基準値として使用しない。

詳細 [元POMの厳格観測ゲート](ORIGINAL_POM_BASELINE_IDENTIFICATION_GATE_20261117_JA.md)、[CI #44091101888 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44091101888)、artifact 14331772347。

### B. δ15Nと独立した実餌種の公開ソース：SCAR

- 公開元: SCAR Southern Ocean Diet and Energetics Database https://diet.apps.aq/、出版社Zenodo DOI https://doi.org/10.5281/zenodo.20047874。ZIP 9,543,574 bytes、元MD5 **5e098c268ce0028704bc4b06300cb0ef**と一致。原scar_diet.csvの全分類群食性行41,010、source registryは434 source IDs（すべて食性の独立研究とは限らない）。
- 真の捕食者名がPygoscelis adeliae、P. antarcticus/antarctica、P. papuaである餌行**1,180件 / 31原source IDs**（アデリー309・ヒゲ53・ジェンツー818行）。有効な0–1の重量組成値は683行。原値の**−999は欠測コード**として集計対象から除外（前記738 numeric non-NAと混同しない）。測定方法はstomach flushingが主、gizzard/scat等も含み、単純に足して同じ観測精度にしない。
- 年日付が実際に同一Nov–翌Febの繁殖季節に入り、開始〜終了が≤122日、元緯度≤−55°、元地理bbox対角が≤25km：**400 prey rows（date条件）→241 prey rows（地理も合格）→73 study+location+date-window+method groups**。
- MAPPPD固定595登録地点のうちどれかから≤25kmにあるsource locality/date groupsは**40**、**5つの真正調査地名、5元source研究、3 source reporting regions、17開始季節**。同一研究×場所×種×季節で再集約すると**30研究・場所・種・季節行**（アデリー21、ヒゲ7、ジェンツー2）。
- 最も厳しい「25km以内の原殖民地site IDが一つだけ」という条件は**0合格**。これは餌データが0という意味ではない。Cape Shirreff、Gourlay Peninsula、Petrel Island、Point Martin、Stranger Pointに複数の元MAPPPD site IDが近接しており、**海域・source locality と個別MAPPPD siteとを1対1で対応できない**ため。上記40は**locality**単位に限定して利用可能、人口・巣数の特定サイトと自動結合不可。
- 5地点・3地域でのlocalityレベル解析は、温度・海氷・餌の局所記述には使い得るが、3種の独立・南極大陸規模の反復として扱うには支持が足りない。特にヒゲとジェンツーのsource観測反復が少ない。

詳細 [original SCAR source-gated code](audit_scar_pygoscelis_diet_panel.py)、[original-source Actions #44093550198 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44093550198)、artifact 14331759490。前段 [Zenodo original source/ZIP MD5確認 #44092322294](https://github.com/zuizui0223/mina/actions/runs/44092322294)。

## 何が現在確定し、何を止めるか

**肯定的に成立:** 既報を外から引き直した独立な海洋同位体baseline実標本と、直接の胃内容物・魚/オキアミ食性sourceを両方原本検算・源ID・時期・距離で対応させられた。これにより、長年の探索で「観測数が多いはずなのに統一生態機構が弱い」原因を、具体的な観測単位と分母の縮退として数値化できた。

**今は不可能:** 860の光学δ15N proxyをPOMに基づいて年別補正して食性と呼ぶこと、SCARの1,180 prey rowsを1,180独立採餌実験と呼ぶこと、地域×年の餌構成・海氷・塩分・巣数を単一の南極全域の環境機構へ昇格すること。大陸規模の塩分因果係数、魚/オキアミ食性変化、CMIP6からの巣数予報は宣言しない。

**研究判断:** 元の塩分関連は exploratory isotope–marine association として補助報告に固定。大規模なメイン論文は既存の「海洋温度–海氷二軸性、同じ既知繁殖地間の巣数再配分、同所の種構成変化、実測繁殖地の将来物理曝露」という**実際に観測が一致する複数階層**を中心に保ち、機構を未同定として正直に扱う。次に生物的機構へ挑むなら、独立複数地域の同一実採餌時間・海域の直接prey量と同位体baseline/近岸アクセスを持つ前向きデータが必要。p値を改善するための別ラグ・半径探索はしない。

## ソースと作業履歴

- Main original penguin isotope/GLORYS/NSIDC: GitHub Actions #44083346932
- Spatial exchange and following-year negative control: Actions #44088674449
- Independent POM source real same-year sampling gate: Actions #44091101888
- Original SCAR dietary-source ZIP validated MD5 + workbook/table schema: Actions #44092322294 and #44092570278
- Source-species/time/locality original target: Actions #44093060873, corrected locality identity #44093550198
- Original published studies and dataset DOI remain attributed to their authors; neither original raw published sources nor unauthorized third-party content is copied into repository output.
