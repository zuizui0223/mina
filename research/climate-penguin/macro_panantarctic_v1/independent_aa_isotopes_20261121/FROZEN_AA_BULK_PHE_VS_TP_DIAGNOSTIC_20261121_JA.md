# 凍結：USAP602094真正個体羽毛のbulk δ15NはPhe由来基線とTPのどちらに対応するか

**2026-11-21 JST、元の同位体応答値を集計・モデルfitする前に固定。** 正式原CSV DOI 10.15784/602094, source MD5 `f9a91c9d9bf3dba9607bf0767df8c206`, upload ZIP SHA256 `185dca693aa9cef96019e379308fa999d6985e010f9ddd9358e706c69ff9b1ce`. 原著 Michelson et al 2026 *Marine Ecology Progress Series*, DOI **10.3354/meps15233**（USAP-DC機械メタの末尾に余分な1がある表記とは区別）。source proper native `Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv`.

## 位置づけ

旧Youngfleshの光学δ15N対冬100kmポリニヤの負関連は2004–2010年439地点季節の**探索的発見**。本源は別研究、別個体・別組織・広い歴史年代であって、**ポリニヤとの独立追試ではない**。既存凍結契約 [`FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md`](FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md) は9地点×採集年/2 regions/羽毛合成年不明でno-goのまま。新結果に合わせて変更しない。

新たな**測定解釈の別問い**：同じ羽毛で測られた bulk `d15N` に、minimally fractionating source-AA `Phe_d15N`（基線の指標）が関連するのか、relative `Trophic_position`（`Glu_d15N`−`Phe_d15N`等から元著者が推定）が関連するのかを比較する。後者は**Pheを含む式から算出された派生測定**で、二者の独立性を仮定しない。Pheは現地硝酸塩/一次生産同位体基線の直接採水測定ではない。

## 実際のmetadataによる支持

- 108元個体・45 source列、全Adélieのbreast feather、1841–2016年。元源`Sample_ID`重複なし。
- `d15N,Phe_d15N,Glu_d15N,Trophic_position`の4値全てが揃う元個体**65**。元`Region×時代`（historical <=1995; modern >=2000）に分類し、元`Site×Year_collected`で個体を平均→主解析の**55 site×collection year**、35異なる元Site、2 source regions。4層のsite×yearは Antarctic Peninsula historical 23 (17 sites), modern 6 (4 sites)、Ross Sea historical 21 (14 sites), modern 5 (2 sites)。同一site×collection-yearの10件の重複個体分を独立生態反復にしない。
- 同一Siteに2以上の年があるのは12 Sites・32 site-year。原historical vs modernでAA完全標本がある共通siteはCape CrozierとRoss Islandのみ。年代差や領域比較は**サンプリング場所・試料タイプの違い**と交絡し得る。

## 凍結する主比較（符号を見てから変更禁止）

1. 55個のsite×collection-yearの原bulk `d15N` をYとする。元Site×年内のそれぞれ元individual4指標を算術平均（既知の測定精度の重みはない）。4層の**Region×historical/modern固定効果**を全モデルで共通に入れた上で、`Phe_d15N`のみのbaseline-proxyモデルB、`Trophic_position`のみのtrophicモデルT、両方のBT、層だけのnull 0を比較。標本の元Siteの名称と4層をsourceから決める。欠測値で代入・変数追加・検証前サブサンプリングしない。
2. **一次判定**は元Site単位で丸ごと除いたLOSO prediction, 各source Siteの残差MSEを一地点一票で平均したRMSE。主要対比は`MSE(B)−MSE(T)`：負ならPhe指標の方が新しいSiteのbulk δ15Nを予測する精度が高い。4層ごとの学習切片はその層の他siteから推定し、未識別層はLOSO NOT_ESTIMABLE（過去元Siteの一つで現代Ross Sea等の識別不能が起こる場合はその折を除かず判定不能を返す）。B,T,BT,0の生MSE/RMSEも保存。TよりBが勝っても因果的「大部分は基線による」とは言わない。BとTの学習相関は併記。
3. 同じ事前固定された35 Siteについて、LOSOのpaired per-site MSE差を4,999回Site bootstrap（seed 20261121）で再標本化。95% percentile, 各Siteの予測差、上限<0なら **BASELINE_PROXY_OUT_OF_SITE_PREDICTIVE_DOMINANCE_SUPPORTED**。0を含めば inconclusive; 正側なら T優位。これは**同源データ内のcross-validated予測性能**、独立なポリニヤ機構・新時代転写ではない。Region数は2しかなく、全南極推論へのクラスタCIではない。
4. 二次：55行のgroup固定効果を除く共通標本OLS/加法モデルB,T,BTで、within-4-group conditional R² と Phe追加・TP追加のincremental residual R²を報告。Phe/TPを55行で標準化した場合のBT係数（単位はPhe 1SD=‰、TP1SD=栄養段階、応答bulk‰）を示す。標準化後の係数比較は原因の寄与率ではない。目立つ相関と多重共線性を隠さず、二者を直交独立な機構としない。
5. 事前に定めた**サイト内の変動**の感度：Site固定効果に置き換え、同じ55 siteyearのうち複数年の12サイト・32 siteyearでB,T,BTの残差化係数とrankを算出。データ数やrank不足で推定不能ならそのままNO_GO。年が一意のsiteの数値を増やすことはしない。これは厳密な同じ羽毛個体の経時追跡ではない。
6. 記述的層間歴史対現代のbulk/Phe/TPの平均と中央値は原55 site-yearでのみ報告し、異なる採集点/試料タイプの相違を明記。**historical−modernの因果傾きやポリニヤ依存を主効果にしない**。新しい時期の任意区分、外れ値カット、別帯域/AAの総当たりはしない。

## 科学的限界

- 元のAA-TPはPheを使い計算されているためPheとTPを互いに完全独立の説明変数とは言えず、同時の2係数を因果分解に使えない。bulk δ15NとPheの対応は同一個体の化学測定同士の照合であり、海域基線の外部介入測定ではない。
- 羽毛の成長/換羽時期、実採餌位置、海洋一次生産基線、糞の夏季窒素同位体との直接一致は未知。positiveでもYoungflesh439と独立時期の「ポリニヤによるオキアミ採食変化」が証明されるわけではない。主題は「bulkを単純に餌生物・栄養段階へ変換するリスク」の具体的測定検証。
- 元2026年Michelson論文自身が歴史的栄養段階の安定性を既に報告している。原著の発見をあらためて独創的な発見として主張しない。重複研究であり、元文献を必ず明示する。

**実施順**：このfreezeをgit commit→Python source/MD5→55 site-year構築→フィット&LOSO/4,999 site bootstrap→不都合な結果も含めレシート→原稿の主線と補助へ判断。変更はPR #214のみ、main・凍結論文には手をつけない。
