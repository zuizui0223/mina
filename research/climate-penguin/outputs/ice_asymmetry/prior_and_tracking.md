# 往路・復路の海氷非対称性：一次研究・追跡データ監査

確認日2026-10-29。個体数モデルは実行していない。

## 最重要の訂正

往路に有利な海氷流動が復路に不利になりうるという非対称性は、単に今回考えた予測ではない。Jongsomjit et al.2024 Ecology e4196がすでに季節的なice supportをモデル化し、4–5月の北向き移動では支援が大きい一方、9–10月の南向き帰還では予想した支援を得なかったと報告している。Ross Gyreの季節変化と北・東向き漂流のため、帰還時に逆向きとなりうると解釈している。さらに人口学的影響（生存、繁殖成功、加入、繁殖確率）の可能性もDiscussionで明記している。従って「往路復路非対称性を新発見」と主張しない。

残る候補は、既知の個体行動の非対称性が、多地点・長期間の繁殖数の変動を説明するか、しかも海氷濃度・期間だけの説明から区別できるか、という人口学的スケールへの拡張である。今回の検索はその未検証性の完全な証明ではなく、世界初とは断言しない。

## 先行研究が実際に測ったもの

- Cape CrozierとCape Royds、回収年2017–2019。装着は2016–2018繁殖期。解析対象は既知年齢87個体146移動記録。
- 公開モデル表は5611の5日集計行。本文にlocationsという表現があっても、Zenodoの行は生の毎位置ではない。
- 位置推定は光GLSをSGATで補正。真のGPSではない。4月1日～10月31日に限定し、白夜による位置推定制約がある。緯度到達地解析では春秋分付近の不確実な位置をさらに除く。
- 主なモデルは移動距離／ice supportを応答とする。supportモデルは週の二次項等を含む。繁殖集団の翌年増減や生存率を応答にした検定ではない。
- Breeding.fは移動前の繁殖状態であり、翌年の繁殖成功ではない。往路の前年成功と復路の翌年成績を混同しない。
- 装着器は翌年帰還した個体から回収する設計。回収追跡は帰還個体に選択されるため、非帰還確率や漂流による死亡を直接検証できない。
- 東西ルートによる到着日の差は約3日だが有意ではなかった。すでに帰還遅延が実証されたと表現しない。

## 指標の独立性

論文のVpは、観測された個体の対地移動Vtから氷の流れViを差し引いた相対運動。Ice supportはViをVp方向へ射影したもの。つまり個体の実際の移動速度・方向を使って定義される。観測された移動距離と完全に独立の環境指標ではない。この点は論文を否定するものではないが、minaで未知の個体軌跡を持つ全繁殖地へ同じsupport値を機械的に作ることはできない。

マクロ解析では、個体数を見ずに定めた季節別ルート／方向・利用海域に対して海氷ベクトルを投影する、別の「潜在的な輸送方向の適合度」が必要になる。生きた個体の真の輸送支援・移動エネルギーとしては扱わない。春秋で同一の氷ベクトルに逆符号を付けるだけだと指標が代数的に従属する。異なる実際の季節・方向の流動を評価し、統計的な分離可能性を監査する。

## 実取得した公開資料

Zenodo8374474の4ファイルを実ダウンロードし、R4.5.3でRDataを開いた。

- ice_vector_metrics_Ecology.R
- IceSupportDF_envinddatana.RData
- Final_Distance_Model_Ecology.R
- Final_Support_Model_Ecology.R

RDataはenvinddatanaというdata.frame、5611×15。fields: birdyear,dist5day,support5day,drift5day,yearweek,year.f,sic5day,bird_fn,err5day,divesum5,lonAvgBinom180,age,sex.f,Breeding.f,colony。緯度経度や日単位日時はない。週14–43、2017–2019、CROZ/ROYD。CROZの移動数39/36/24、ROYD12/17/18。元の位置を再計算するコードは外部のLocationData.csvを要求し、そのCSVはこのZenodoには入っていない。

別途USAP-DC DOI10.15784/601482に原GLS位置のCSV14.7MBが登録されていることを確認した。公開画面にreCAPTCHAゲートがあるため、この監査では取得していない。メタデータの開始日0201-02-01は明らかに不整合で、本文の2017–2019と原データ確認を優先する。

## Ross海以外へ広げる資料

1. Terre Adelieの2025年Biological Conservation研究は62個体・5年間。Movebank4778411162を示す。Figshare27947100のメタデータを取得し、中身は4つの解析Rコードであり軌跡ではないことを確認。Movebank匿名API要求は401。原軌跡は取得済みとしない。
2. Takahashi et al.2018のEastAntarctica/Syowa研究は2冬、18個体と5個体。3–4月は西、5–8月は北、その後南東へ帰還という移動を報告。Ross海の北向き往路・南向き復路を全南極へそのまま割り当てることへの反例。公開原データのダウンロード先は確定していない。
3. AADのBechervaise winter1996 campaign26に冬季ARGOS追跡のメタデータあり。未取得の候補として記録。
4. Casey/Shirleyの見つかったデータは1995/96夏季であり、冬の校正から除外。NOAA Adelie telemetryについては旧カタログのnon-public表記だけで判断した記述を訂正する。2026-10-29に公開NCEI 0244399 v1.1のCSVを取得・監査した。全12,722行・84個体だが、冬季は2004年3〜8月の254行・3個体のみで、9〜10月の帰還方向校正には使えない。詳細はoutputs/climate_penguin/NOAA_TRACKING_AUDIT_JA.md。

## 広域解析を保つための役割分担

全地点の毎年の個体追跡を要求すれば研究は少数地点へ縮む。追跡を季節・方向・利用海域の外部校正として使い、主解析の反復は広域の繁殖地×年に置く。ただし、追跡がない海域をRoss海のコピーで埋めない。校正可能な海域を確定し、残りは「海氷循環の季節差との関連」という弱い推定対象に分ける。輸送機構と餌場配置の共変動は個体数だけでは完全分離できない。

## 一次資料

- https://doi.org/10.1002/ecy.4196
- https://doi.org/10.5281/zenodo.8374474
- https://doi.org/10.15784/601482
- https://www.sciencedirect.com/science/article/pii/S0006320725005440
- https://api.figshare.com/v2/articles/27947100
- https://nora.nerc.ac.uk/id/eprint/519726/
- https://data.aad.gov.au/aadc/argos/profile_list.cfm?campaign_id=26
- https://data.gov.au/data/dataset/satellite-tracking-of-adelie-penguins-around-casey-station-antarctica
- https://catalog.data.gov/dataset/adelie-penguin-telemetry-data
