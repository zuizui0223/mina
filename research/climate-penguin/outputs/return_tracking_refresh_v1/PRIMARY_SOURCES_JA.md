# 繁殖前帰路の公開追跡データ再探索

確認日: 2026-10-30。対象は個体ID・日時・位置・繁殖地を持ち、9–11月の帰路と海氷流動を結合できる追加資料。既取得Hinke2019、NOAA冬季Adélie、Ross GLS、AAD認証案件は再取得しなかった。論文記載、公開ファイル確認、解析可能性を分ける。

## 結論

今回の追加探索では、**海氷域の繁殖前帰路について新たに解析可能と確認できた個体軌跡は0**。これは全世界に資料がないという意味ではない。アクセスできた新規ファイルのうち、Adélie資料は期間集計、個体位置資料は非海氷域のマゼランペンギンだった。したがって、海氷輸送対障壁の区別やマクロな繁殖地間反復が増えたとは判定しない。

## ファイル内部を確認できた資料

### Adélieの年間潜水行動：期間集計のみ

[Point Blue公式リポジトリ](https://github.com/pointblue/ADPE_longitudinal_foraging) と [CSV原本](https://raw.githubusercontent.com/pointblue/ADPE_longitudinal_foraging/main/by_period_dive_data.csv) を取得し、メモリ上で列・集計数を確認した。全239行中、`Returning migration` は45行、18個体、繁殖地コードCROZ・ROYD。開始日は2017・2018・2019年の8月16日、終了日は10月26–31日。`season` は2016–2018であり暦年とずれる。

列は個体、繁殖地、性、年齢群、期間、潜水回数・深度・時間など。**緯度経度も日単位位置もない**。期間の開始・終了を個体の出発・到着イベントと同一視できない。期間間の潜水努力比較には使えるが、流氷方向と移動方向の一致や帰着遅延の直接分析には使えない。

一次論文: [High-resolution recording of foraging behaviour over multiple annual cycles shows decline in old Adélie penguins' performance](https://pmc.ncbi.nlm.nih.gov/articles/PMC10072935/)。PMC本文は今回ブラウザ確認画面になったため、数量は論文検索断片でなく公開CSV実査に基づく。

### Martillo島マゼランペンギン：小さな公開原データ、要QC

[Dodino et al. 2021](https://doi.org/10.1371/journal.pone.0256339) のS1 Datasetは [Figshare v3](https://doi.org/10.6084/m9.figshare.14388233.v3) を指す。[公開API](https://api.figshare.com/v2/articles/14388233/versions/3) でCC BY 4.0、`GLS raw data.xlsx`、308,814 bytesを確認。[ファイル](https://ndownloader.figshare.com/files/27491777) をメモリ上で開き、9シート（個体番号3482, 3488, 3494, 3497, 3499, 3503, 3509, 3510, 3514）、日時、日出入、緯度経度、SST、WetDryChange、最大水圧列を確認した。

単純な緯度±90度・経度±180度の範囲判定では各シート188座標行（2017-02-22–10-02）、うち9–11月に各14行。ただしこれは**品質確認済み位置数・帰路点数ではない**。原座標には著しい飛びがあり、緯度経度列は論文のProbGLS補正軌跡とみなせない。シート間の日時・座標列が全て同一ではないことも確認した。

論文はMartillo島1繁殖地・2017年・雌5雄4個体の冬季追跡を扱い、帰着は9月中旬–10月初め。GLSの位置誤差と春分期の欠測・推定に注意が必要。**非海氷域の移動比較候補**として次に原データQCと位置再構成を進められるが、海氷依存種の反復を増やさず、温暖化や海氷輸送を検証する本命資料にはならない。[解析コード](https://github.com/nlois/SpatialAnalysis_MagellanicPenguins) は公開されているが、この調査では位置再構成の再現性を未検証。

## 一次資料の所在まで確認、データ利用は未確認

| 資料 | 確認結果 | 今回の判定 |
|---|---|---|
| [BAS Bird Island PTT 01218](https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01218) | Macaroni・Gentoo、1998年以降、主に夏季、一部冬季と公式メタデータに明記。アクセス欄は参考論文のみ、保管先Oracle DB | 公開カタログ。個体・月別件数やダウンロードを未確認。解析可能数へ加えない |
| [Mattern et al. 2025 Tawaki](https://doi.org/10.7717/peerj.19695) | 論文では2019年2月23日–9月11日、3地点14個体、完全冬季旅程5個体。データ所在地は [Movebank study 691598094](https://www.movebank.org/cms/webapp?gwt_fragment=page=studies,path=study691598094) | Movebankページをツールで取得できず、匿名ダウンロードや実ファイルは未確認。主に亜南極海域・帰路季節も異なるため即時代替にしない |
| [Macdonald et al. 2026 emperor colony movement](https://doi.org/10.1038/s43247-026-03906-0) | Atka Bay・Coulman Island・Cape Washington、2017–2024、SAR/光学画像による群れ位置。shapefileの [UK PDC DOI](https://doi.org/10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9) を明記 | [PDC 02155](https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/02155) はメンテナンス表示。実ファイル未確認。群れの繁殖期移動であり個体の繁殖前帰路ではない |

## 次の判断

最も具体的に着手可能なのはMartillo公開GLSの品質監査。ただし**非海氷対照の方法検討**と明示し、既存の海氷帰路仮説を救済したと扱わない。海氷域の本命分析は、既存候補で個体ID・帰路日時・海氷流動の有効観測が同時に揃うまで機構検証を保留する。皇帝ペンギンの新規SAR研究はリモセンによる繁殖地移動の別問いには有望だが、3繁殖地への縮小や繁殖季節・観測単位の変更を黙って行わない。

問い合わせ、ログイン・CAPTCHAの迂回、大容量取得は実施していない。外部ファイルは確認用にメモリ内で読み、ここには一次資料へのリンクと監査結果のみ保存した。
