# Ross海位置アンサンブル：生成方法とフラグの一次資料監査

2026-10-30。位置表の全量監査とは別に、著者公開の処理コードv4.0.2（commit `784760d26795235483305557cad78a27ec36e33a`）と解析コードv1.1（`49e6f210de224d34127a31c84835014a6bff9609`）を読んだ。コードの読解であり、元の光データから全推定を再実行した検証ではない。

## 方法と時間解像度

[Schmidt et al. 2023の方法](https://pmc.ncbi.nlm.nih.gov/articles/PMC10655226/)は光レベルから1日2位置を推定し、SGATの初期経路を薄明時刻・誤差・移動モデル・繁殖地での最終／最初の日時を使うMCMCで更新すると説明する。2,000シミュレーションから最終500経路を用いる。これはGPSによる半日ごとの実測ではない。

著者の[create_molt_locs500.R](https://github.com/pointblue/gdr_molt_sic/blob/v1.1/create_molt_locs500.R)も最終500経路を読むと記載する。公開CSVのrun=500～999が2,000シミュレーションのどの反復に対応するか、選択・再番号付けの工程は今回確認できなかった。500経路を500独立個体としない。行数を500で割れば常に一意時刻数になるとも仮定しない。

## フラグの意味

| 列 | コードで確認した定義 | 解析上の注意 |
|---|---|---|
| inserted | 極昼など実際の薄明のない期間を補うため人工追加した薄明時刻の印。元のtwl$Insertedを出力へ渡す | 実際に観測された光由来の位置と区別する。単に位置の線形補間という定義ではない |
| filterLand | 中央値の推定経路の隣接点を線分化し、Natural Earthの陸地ポリゴンとの交差を検出したindD。最初・最後の5区間はFALSEに変更し、末尾へFALSEを付加 | 個々のMCMC位置が陸上かを判定した列ではない。FALSEが陸上問題なしの保証でもない |

根拠：[前処理の人工薄明追加 L178–190](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/GDR_analysis_SGAT_1617_preprocess.R#L178)、[経路からのフラグ生成 L277–283](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/forwardAnalyses_fullModel_1617.R#L277)、[陸地ポリゴン定義 L79–92](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/functions/setupSession_1617.R#L79)。1718・1819のforwardスクリプトでも同じフラグ生成を確認した。

## 秋分付近の除外と終端拘束

[全非繁殖期の作図コード](https://github.com/pointblue/gdr_molt_sic/blob/v1.1/map_all_nonbreed_locs.R)は年内日86–109と229–269を除く。コメントでは春分・秋分付近の精度が悪い期間への対応とされる。この規則を使うと9月の大半が除外される。残る9月末～10月が帰還期全体の代表とは限らない。時刻列の間隔・極昼による欠測を保持し、一定の12時間間隔へ勝手に補間しない。

特に、[位置推定コード L62–70](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/forwardAnalyses_fullModel_1617.R#L62)は開始以前と終了前1日以降などの位置を繁殖地座標へ固定する。終了時刻の扱いは取得日との差も参照する（同ファイルL27–38）。したがって、出来上がった経路から到着日を算出し、それを独立な帰還日検証と呼ぶことはできない。境界条件から離れた区間の流動対応と、終端付近の見かけの進行・到着を分ける必要がある。

## 海氷・SSTを位置推定へ入れた循環性はあるか

公開v4.0.2の3年分のsetupSessionではSST配列を作る呼出しはコメントアウトされている。実行されるlog.priorは陸域マスクを使い、最終thresholdModelは光・移動パラメータ・陸域prior・固定位置・Insertedの欠測指定を渡す。[setupSession L12–21](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/functions/setupSession_1617.R#L12)、[最終モデル L238–269](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/forwardAnalyses_fullModel_1617.R#L238)。

リポジトリにはSSTを処理する補助関数もあり、[makeSSTarray.R](https://github.com/pointblue/gdr_data_processing/blob/v4.0.2/code/geoloc_code/mask/makeSSTarray.R)は海氷コード−10を−1.8へ置く処理を持つ。しかし、関数が存在することは対象位置推定で使った証拠ではない。確認した実行経路にはSICや海氷流動を直接与える呼出しはなかった。

このため「位置が海氷濃度に合うよう直接推定された」とする根拠は今回見つからなかった。一方、公開CSVまでの実行履歴・全依存パッケージ・入力マスクを再現したわけではなく、「完全に独立な位置推定」とも保証しない。移動prior、既知の繁殖地終端、陸域マスクからの制約と、実際の位置不確実性は流動との比較でも残る。

## 採用判断

### 追加確認：arrived列の生成根拠

[gdr_make_molt_dates_table.R v1.1 L13–15・L54–72](https://github.com/pointblue/gdr_molt_sic/blob/v1.1/gdr_make_molt_dates_table.R#L13)は圧力原データから作られた潜水集計を読み、日別潜水数を計算する。[同L91–109](https://github.com/pointblue/gdr_molt_sic/blob/v1.1/gdr_make_molt_dates_table.R#L91)には、装着後300日超・年内日274超で、当日の潜水数15以下かつ前方5日平均15以下、または機器回収日にstatusをarrivedとする規則がある。これは潜水の停止・減少を用いる判定候補であり、光位置・乾湿センサー・現地の初帰還観察から直接測った日という定義ではない。回収日による代替も混在する。

ただし同スクリプトの[最終出力L194–197](https://github.com/pointblue/gdr_molt_sic/blob/v1.1/gdr_make_molt_dates_table.R#L194)にはarrived列がなく、statusから個体年ごとの到着日をどのように選んで別CSVへ書き出したかは示されていない。公開CSVを実読込すると、`gdr_molt_dates_v2022-02-11.csv`は208行×9列でarrivedなし、別の`gdr_molt_arrival_dates_v2022-02-11.csv`は208行×11列でarrived/retr_lagがあり、arrivedは169行で非欠測だった。前者を読んでarrivedを参照するcreate_molt_locs500.Rとは不一致がある。

従って、公開コードは潜水数に基づく到着判定の候補を支持するが、**別CSVの169日付がすべてこの規則から生成されたことは未再現**。また位置推定の終端固定に使うmTab$end・first_dry_day等との一致も確認できていない。同一の値であるとも、独立な行動観測であるとも断定しない。利用には元の日別潜水集計からの再計算、回収日代替の識別、位置推定境界との照合が必要である。

全量集計ではrunを反復推定として保持し、insertedとfilterLandは別々に報告する。帰還日・帰還完了を推定経路の終端から新しく測定したことにしない。海氷流動との照合は、秋分除外・位置アンサンブル・終端拘束への感度を保持して初めて検討できる。今ある広域定着・繁殖数解析とは標本と観測単位を分ける。

アクセス注記：PMCの直接openはブラウザ確認ページとなり、方法本文は検索サービスが返した当該一次論文本文を参照した。NSF公開PDFは接続タイムアウト。フラグとモデル入力の判断は匿名で実取得した著者GitHubの固定タグのコードに基づく。認証、問い合わせ、元コードの実行、原データの再配布は行っていない。
