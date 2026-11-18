# Signy島3種の原繁殖データ接続：原資料監査 v1

**目的**：海氷を年次巣数へ直接回帰する既存の予測失敗を受け、繁殖過程の別の段階である「繁殖つがい数→記録雛数」を、同じ島のアデリー・ヒゲ・ジェンツー3種について、公開一次データから構築する。

- 原出典：British Antarctic Survey（NERC UK Polar Data Centre）のSigny島公開CSV。Adélie DOI \`10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d\`、Chinstrap DOI \`10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9\`、Gentoo DOI \`10.5285/883c6b40-024e-41e8-9c3e-2668a44b5751\`。
- 原CSVを学術活動で先に固定したAdélie・Chinstrap SHA256と照合。Gentooは新規取得として実測SHAを記録する（確認するまで捏造しない）。
- 1996/97〜2019/20の種×原colony×繁殖季の列を保持。重複source colony-seasonを厳格拒否し、欠測数値を0とせず、繁殖つがい数0で割らない。巣数・雛数の計測日がある場合に限って順序を記録する。
- 主要出力は原colony段階の記録雛数/繁殖つがい数、種×年ごとの観測原colony数、期間・出典・元データのSHA。単純な3種の同一島データであって、全南極の3反復を作らない。
- 重要な境界：このデータの雛数が必ずしも個体追跡による巣立ち・加入を表すわけではなく、年齢・調査位置・方法上の変化を別に確認する。平均の記録比を因果的な繁殖成功や生残率へ置換しない。
- これは**source-firstの原データ接続**。結果を見てから海氷・塩分の係数を選ぶ解析は行わない。雛生産が得られた後、環境が計数に先行するか、Signyの海氷・塩分独立時系列があるか、繁殖空間（Signy既存固定群）の年度と重なるかを別途監査する。

再現: \`python research/climate-penguin/work/climate_penguin/signy_trispecies_stage_source_v1.py --source-dir build/signy_source --out build/signy_stage_derived\`。CIワークフロー \`.github/workflows/climate-penguin-signy-3species-stage-source-v1.yml\` が原publisher ZIPを新規取得する。

原CSVの直接再配布は行わず、取得元・ハッシュ・派生CSV・数値の再現入口をGitHub Actions artifactに保存。凍結PR189、Paper2/PR199、既存216比較の統計補正は変更しない。
