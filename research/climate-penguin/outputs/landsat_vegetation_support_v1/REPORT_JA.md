# Landsat 8で2018年の植生観測を補えるか

8地点について、2018／2019年の1～2月を同じLandsat 8で検索・読み取りした。16地点×年、227地点別シーンのQA_PIXELを取得し、最終的な読み取りエラーは0だった。

## 実際に確認できた支持

既知植生域に画素中心が入る30 m格子で、fill・膨張雲・巻雲・雲・雲影・雪・水域のQAフラグがない画素を候補とした。QAを通ったことは植生の正しい識別や大気補正の妥当性を保証しない。放射飽和・エアロゾル・反射率そのものはまだ調べていない。

- 1月のみ、2月のみでは、両年とも2日以上の観測がある共通植生画素は0。
- 1～2月をまとめる感度比較では、Aitcho（AITC）だけで249共通画素を確認。他の7地点は0。
- 227件すべてTier 2で、Tier 1だけに限定した支持は0。単日支持もpaired_qa_support.csvに全件保存。

1～2月の統合でだけ支持が生じるため、各年の観測日や融雪・生育段階の違いを確認する必要がある。30 mの画素数は以前のSentinel-2の20 m画素数と直接比較しない。画素中心が植生図内でも、画素全体が植生という意味ではない。

## 位置精度が次の制約

USGSはTier 2をTier 1の幾何精度基準を満たさない画像と説明している。今回の地図との重ね合わせは配信座標に基づき、実際の位置合わせを検証していない。従って249画素を「両年で確実に同じ植生を観測した画素」とは呼ばない。[USGSのTier説明](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-1-data)。

これは元の40地点の海氷解析をAitcho一地点へ縮小する判断ではなく、植生の年次比較で現在確保できた支持の限界である。広域の植生効果を推定するには、追加の季節・製品・位置合わせ・年次分類の支持が必要。今回の結果から植生と繁殖数の相関や将来予測は計算していない。

## 配信経路と再現

Earth Searchが参照するAWSアセットはRequester Pays設定で匿名アクセスが403になったため、有料認証を使わず、公開配信のPlanetary Computerへ切り替えた。公式に公開されたトークン取得手順で読み取り、期限付きトークンは成果物に保存していない。取得中のレート制限に対しては、トークンを実行内で共有して再利用し、成功済み画像を再取得せずに残りを取得した。[Planetary Computerの公開アクセス説明](https://planetarycomputer.microsoft.com/docs/)。

QA_PIXELのビットは[USGSの品質情報](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands)と取得メタデータを参照。除外ビットは0,1,2,3,4,5,7。閾値を足し合わせる方法とビットごとの判定が一致することを確認した。

`python research/climate-penguin/work/scenario_support_v1/landsat_vegetation_qa.py --map <PlantarcticaVegetationMap.shp>`

`python research/climate-penguin/work/scenario_support_v1/validate_landsat_qa.py`

landsat_sources.zipにカタログ応答、取得QA配列、シーンURLとTierを保持。16配列のハッシュ、日付・シーン・品質配列の対応を検証し、1月・2月・1～2月、全Tier・Tier 1、最低1日・2日の全96比較を保存した。アーカイブをこのフォルダへ展開すると保存配列から再検証できる。
