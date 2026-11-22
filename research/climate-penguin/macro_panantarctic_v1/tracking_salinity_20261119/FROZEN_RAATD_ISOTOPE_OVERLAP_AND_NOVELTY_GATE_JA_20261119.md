# RAATDアデリー追跡 × 塩分：新データ取得の事前支持ゲート（2026-11-19）

**場所：** `mina` draft PR #214の新データA案、既存main肯定結果5件・凍結原稿を変更しない。個体追跡の元測定を開く前に、この照合基準で生物・海洋の原資料一致を確認する。偽の独立個体数、未観測年の0、元GUANO画像と追跡個体の同一性を仮定しない。

## 原本と権限

1. **RAATD filtered original**：SCAR Retrospective Analysis of Antarctic Tracking Data（Zenodo 2020, https://zenodo.org/records/3722948）。公開`SCAR_EGBAMM_RAATD-filtered-noTMB.zip`元MD5`168e5b9b5c4ed20bb84dd00145acb0a5`を検算。原年分布1991〜2016、Adélie filtered **520個体・90,202 state-space estimated positions**（Ropert-Coudert et al. 2020, *Scientific Data*, https://doi.org/10.1038/s41597-020-0406-x）。GPS/PTT/GLSは精度が異なる；**GLS位置をGPS級の局所採餌選択として使用しない**。
2. **元アデリー光学δ¹⁵N cohort**：source 860 original site×breeding season（88site、82 GLORYS wetcells、13 source reporting regions、season 1996 and 1999–2012）。成功GitHub Actions #44083346932、artifact 14328755565、ZIP SHA256`dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`。
3. **元繁殖地座標**：MAPPPD source 595 IDs、18 regions、artifact 13669533413、ZIP SHA256`add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a`。リンクは元`site_id`とWGS84測地線距離。
4. **BirdLife STDB**：メタデータは閲覧可能だが追跡座標の使用は所持者から申請・承認が必要（https://www.seabirdtracking.org/instructions/ および https://www.seabirdtracking.org/terms-of-use/）。未承認データを「公開取得した」と表示しない。

## 原sourceの照合定義

- 対象は **ADPE = *Pygoscelis adeliae*** の真metadata個体IDに結合できる、元RAATD filtered 位置記録。RAATD元個体・装置・追跡日（UTC）を保持した派生集計。device型の条件をGPUで勝手に変えない。
- **11〜翌2月の同一breeding season**。追跡timestampが11/12月なら同年season、翌1/2月なら前年season。デプロイ年だけでは照合しない。
- 元RAATDの`deployment_decimal_latitude/longitude`を、最も近い88の元isotope観測MAPPPD siteとのWGS84楕円体距離で照合。半径を**5、25、100kmの全3条件**で記録。特定siteに**一意**に対応するには、次に近いisotope siteが同半径外であること。25kmが主コロニーマッチ（RAATD deployment座標はサイト固有に精密に記録されたとは限らず、**確実な同一繁殖集団とは呼ばない**）。100kmは広域の地理重複の上限感度であり個体のコロニーID・採餌半径を意味しない。
- 対応siteには実際に**同一breeding seasonの元source δ¹⁵N画像レコードが存在**すること（sourceで存在したことのないsite×yearは空欄、0にしない）。派生メタデータ表は個体IDs・電子メール・追跡軌跡の生座標を含めず、元`site_id×season`で個体数やフィルタ位置数を集計する。

## 次段解析の開始ゲート（結果閲覧前固定）

**今ターンはRAATD元個体・位置・元88site×seasonの重複数だけを監査する。** RAATDの元個体GPS/PTT≥3が実際に追跡されたsite×seasonが**12以上**、異なるsource reporting regionが**3以上**、少なくとも**3つの異なる繁殖季節**に分布しているときにのみ、第二段階の`used-available`・個体ランダム効果による近岸塩分選択解析を検討する。これは科学的有意差を意味しない最低観測機会であり、結果に応じて緩和しない。少なくとも3独立地域でのout-of-region予測移用を主張するには別の判定基準を要する。

第二段階では海流/渦、海水温、海氷、距離、季節と航海/採餌ステージを調整し、同じ個体・同じ時間にアクセス可能な環境`availability`を比較する。追跡点は採餌成功・捕獲餌・食性組成を測定しない。**塩分×位置選択が出ても「塩分が魚食率を変える」と直結しない。** 地点別海洋`sos`粗格子に多数のGPS点を重ねても海洋独立replicate数は増えない。

## 重要な先行研究と発見の余地

- Ropert-Coudert et al. 2020 `Scientific Data`、Hindell et al. 2020 `Nature`：RAATDを用いた南大洋捕食者採餌分布と保全地図。
- 2019 `Scientific Reports` DOI https://doi.org/10.1038/s41598-018-35901-7：Palmerのアデリー・ジェンツーは海洋表層の収束域を選択。低塩分・高塩分の水塊との関係は2019–2021のPalmer海洋研究に存在。
- 2026 `Global and Planetary Change` DOI https://doi.org/10.1016/j.gloplacha.2026.105518：南極半島アデリーの追跡×海洋再解析×将来の採餌生息地適性。
- 2026 `Progress in Oceanography` DOI https://doi.org/10.1016/j.pocean.2026.103798：**5ペンギン種・3,189個体・59コロニーの追跡**を用いて中規模渦・ARSの場所選択を検証。RAATD由来追跡を多数再利用するため、追跡データ単体で新規性を主張しない。

**最終評価条件：** 直接採餌率ではなく、元物理海水塩分の**個体内used-available環境選択の追加説明力／地域間転写性**を独立に確認してはじめてA案の生態学的増分。今回はデータ重複の可否だけを先に固定し、可能性のない追跡×isotope媒介解析を続けない。
