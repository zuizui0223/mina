# 公開糞地図と2013年以降Landsat 8の実画素照合

2026年11月20日。原著の画像選別コードに依存しない抽出法を、公開Ardley糞ポリゴンと実際のLandsat 8反射率で試した。新しいポリニヤ–同位体の相関検定には至っていない。

## 実際に進んだ点

原著が提供した過去の画素位置だけを新画像に当てはめる方法に加えて、別研究の撮影日付き糞ポリゴンを新Landsat画像に直接重ねる経路を実装した。30 m画素内の注釈糞面積割合を連続量として使い、80%純度条件は設けなかった。これは以前の幾何的な純画素不足を理由に止まる必要のない方法である。

ただし、実画素の品質・年代外での予測・生態解析の標本数を調べると、Ardleyのアデリーで利用できたのは1地点・2繁殖季・3撮影日の18注釈重複画素だった。注釈被覆率の季節外予測も平均値予測を上回らなかった。元85地点・439地点季節のポリニヤ負相関を再検証する新しい光学応答としては、支持が足りない。

## 公開資料と抽出法

Pfeifer et al.の公開Zenodo 14503437には、Ardleyの22撮影日×アデリー・ジェンツーの44個の糞注釈Shapefileがある。4.11GBのZIPのうち、Guanoメンバーがまとまった2,060,190 byteの範囲を一度取得し、270個の関連メンバーについてZIPのCRC32と展開サイズを照合した。元ZIP全体のMD5は提供元メタデータ値を記録したもので、全4.11GBのダウンロード照合を行ったとは主張しない。[公開資料](https://doi.org/10.5281/zenodo.14503437)

Microsoft Planetary ComputerのUSGS Collection 2 Level-2カタログで当地2013年11月〜2018年2月のLandsat 8を検索すると259シーンがあり、22注釈日から8日以内の候補は69シーンだった。範囲・8日差は対応資料を確保するため今回選んだ実装上の設定で、同日の地上真値と同等とは扱わない。最初に画像全体の雲量で選んだ17シーンを試した後、局所で使える画素を見逃さないよう全69シーンのネイティブQAを点検した。

QA_PIXELのfill、膨張雲、巻雲、雲、影、雪、水面を除き、QA_RADSATの飽和・地形遮蔽も除外した。注釈群の外接矩形を150 m拡張した固定範囲内の有効画素割合に基づき、同日で重なる複数シーンを一つにした。選別にδ¹⁵Nやポリニヤの情報は使っていない。採用された画像はすべてTier 2であり、微小な糞パッチとの位置ずれも誤差要因となる。

各シーンの元CRS・元30 m格子に糞ポリゴンを変換し、交差面積/900 m²を計算した。元blue/green/red/NIR/SWIR1/SWIR2を公開STACのscale・offsetで表面反射率へ変換。2018年1月20日の全域QA有効画像では、画素に分けた注釈面積の和が元ポリゴン面積と一致することを独立に確認した。アデリー448.944 m²、ジェンツー2400.412 m²だった。

## 実画像の結果

69候補すべてのQA読取に成功。局所有効画素があったのは5シーンで、同日重複を除くと4撮影日となった。

|注釈日|L8撮影日|QA有効画素|アデリー注釈重複画素|ジェンツー注釈重複画素|アデリー最大注釈面積割合|
|---|---|---:|---:|---:|---:|
|2014-01-10|2014-01-16|112|7|20|40.4%|
|2015-01-27|2015-01-19|21|0|5|0%|
|2017-11-08|2017-11-08|151|1|2|0.97%|
|2018-01-14|2018-01-20|400|10|46|30.7%|

全684 QA有効画素中、アデリー注釈との重複は18、ジェンツーは73。画素は同じ島・同じ画像内で相関するため、684個の独立生態標本とは数えない。2014年の繁殖季は2013/14、2017年11月と2018年1月は同じ2017/18季なので、アデリー陽性のある生態比較単位は2季だけ。その他の原注釈季が撮影されたというだけで、新しい同位体観測があることにはならない。

## 糞信号の季節外検証

6反射率を標準化したRidge回帰（alpha=1を固定）で注釈面積割合を予測し、繁殖季を丸ごと外した。訓練内の平均注釈割合を全検証画素へ予測する基準とMSEを比較した。アデリーでは2013/14季のMSEが0.0015308対基準0.0015260、2017/18季が0.0059860対0.0001972となり、双方で改善しなかった。2014/15季は有効アデリー注釈重複画素がゼロで、生態的な不在を検証したものではない。ジェンツーも全3季で基準を上回らなかった。

この回帰の目的変数は、著者が注釈した面積の割合。注釈がない場所を真の非糞とは確認できていないため、分類器のprecision/specificityや真の糞純度とは解釈しない。小パッチ、画像・注釈の最大8日のずれ、Tier 2の位置精度、濡れ・雪・岩などの混合、そして実質2季の支持が重なる。Ridgeの失敗からSAM、ACE、混合分解や別地点での分類が不可能とは結論しない。

先行研究ではLandsat 8のSAM/ACEによる糞抽出が実施されている。公開報告はCape Birdなど大きな群落での成功を示す一方、Ardleyのような断片化した群落を難しい対象として扱う。今回のArdleyの結果だけを南極全域の検出限界へ一般化しない。[UBA 2017報告](https://www.umweltbundesamt.de/sites/default/files/medien/1410/publikationen/2017-04-06_texte_30-2017_pinguinmonitoring_eng_0.pdf)

より大きいアデリー群落の候補として、Cape Hallettの2018年UAV・WorldView・Landsat比較論文も確認した。同論文の原資料は責任著者への依頼による提供と記載され、直ちに取得できる新しい地理参照付き検証ラベルは得られなかった。現時点の別地点検証の未達理由は原著のコードだけではなく、同時期の公開ラベルの対応範囲にもある。[Park et al. 2026](https://doi.org/10.1002/jgo2.70027)

## ポリニヤ検証と論文への判断

今回の結果から2013年以降の負相関を再現・否定したとは言えない。L8用の103実糞標本PLSR較正は別実行でRMSE約1.742‰を得ているが、混合地表画素に同じ較正を当てる妥当性は未検証。ここでδ¹⁵Nを生成すると、地表混合や画像品質の変化を餌環境の変化として扱うおそれが実データ上残る。2繁殖季では、海氷・水温・塩分を調整した従来モデルも推定できない。

論文では、旧データの負の条件付き関連と、今回の新年代の観測確保・測定妥当性の結果を併記できる。温暖化との問いは「海氷減少量に加え、冬の沿岸開水面配置が翌夏の食物網関連指標に情報を足すか」。現時点では探索的仮説であり、今回の未成立を負相関の否定に数えない。

本文/補足への英文案 — “We evaluated a public-data route to post-2013 validation by intersecting dated, species-specific guano annotations with native Landsat 8 reflectance and quality masks. Across 22 annotation dates at Ardley Island, the 69 temporally matched candidate scenes yielded Adélie annotation overlap on three acquisition dates in only two breeding seasons. A season-held-out model of annotated cover fraction did not outperform the training-mean baseline. These observations did not provide a validated new isotope time series, leaving the historical polynya association without independent post-2013 confirmation.”

## 再現

Python依存はnumpy、pandas、scipy、scikit-learn、requests、remotezip、rasterio、planetary-computer、pyproj、pyshp、shapely。以下は `diet_salinity_source_20261117/` 内のスクリプト。cacheとoutputに作業用ディレクトリを指定する。

```text
python prepare_ardley_l8_fractional_sources.py --cache CACHE
python scan_ardley_local_qa.py --cache CACHE
python ardley_l8_fractional_pilot.py --cache CACHE --out OUTPUT --local-qa-csv CACHE/all_69_local_qa.csv
```

最終の69候補QA一覧、画素ごとの反射率・注釈割合、季節外予測誤差、シーンID、CRC照合・入力SHAの記録は `diet_salinity_source_20261117/ardley_l8_fractional_results/` に保存。生態応答の有意性を見て画像・日付・半径・判定閾値を選んだ解析ではない。公開注釈の欠損を埋めたり、糞がないことに置き換える処理もしていない。
