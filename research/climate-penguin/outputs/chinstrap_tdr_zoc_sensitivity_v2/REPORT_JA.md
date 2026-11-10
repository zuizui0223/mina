# BAS Chinstrap TDR: pressure zero-offset sensitivity before ecological scale-up

2026-10-31. The original BAS Chinstrap TDR v2 source has **317 original TDR CSV files, three header-only files and 314 usable raw pressure series**. Matched native GPS/TDR v2 source supports **300 nonempty deployments**. The four original ID-frozen per-island pilot LIC001, PI001/PIC001, MIC001, SIC004 has now actually decoded full native pressure at 1-second cadence and applied provisional q1 per-hour 60min ZOC + fixed 5 dbar and ≥10sec dive candidates. Source verified pilot: Laurie 1,481 events, GPS bracket901; Powell 4,786 / 2,117; Monroe 1,369 / 876; Signy 51 / 24. Original TDR time series overlaps GPS periods 96.7–99.3%. Thus TDR coupling is feasible, but **the majority of candidate dives at Powell and Signy are not geolocated under strict source timestamp criteria**, and the selected fractions may differ systematically.

**Critical sensor QC:** Per-hour 1%-quantile pressure offset range is Laurie0.30, Powell0.60, Monroe**7.7525**, Signy0.41 dbar. The unusually large Monroe drift and strong threshold sensitivity (at ≥2/5/10dbar: 2388/1369/532 candidate events) make it unsafe to interpret uncorrected or one-choice dives across islands as biological depth or search-effort differences.

This second independent workflow tests all **four calibration specifications** without choosing outcomes: fixed 60min q1 (previous primary), fixed 30min q1, 60min q5, and global q1 constant comparator. Cross with fixed 2/5/10dbar and 10s, original GPS bracketing conditions unchanged => **48 tag×offset×threshold rows**. The constant global offset is a diagnostic, NOT a recommended ZOC. No raw pressure timeseries published in artifacts, only per-tag summary.

**Scientific release gate:** If counts/GPS geolocation vary strongly with offset and time, report inability to compare; do not pick convenient correction. Even if local ZOC stable, require external/visual review of sensor surface periods and pressure-to-depth calibration before full 300 source tags or 'foraging patch quality'. 2021 Movement Ecology already analyzed the same underlying Chinstrap GPS/TDR data with a pressure zero-offset method and reported distance-varying foraging patch quality; rerunning source-derived diving cannot be claimed as first discovery. Our intended incremental role is connecting real dive-associated movement to a later-published modelled marine resource map with strict multi-island source accounting, not a novel independent prey observation.

Methods/results remain source-based and exploratory, **no causality or 2050/2100 future breeding forecasts**.


## 2026-10-31 実行済みの4手法×3閾値感度（原TDR再取得・4テスト成功）

[GitHub Actions #41165153690](https://github.com/zuizui0223/mina/actions/runs/41165153690) で、元BAS TDR・GPSを再取得し、固定4追跡の4補正方式×2/5/10dbar＝**48条件すべて**を実際に計算。q1/60minの元pilot数値を独立した固定receiptに照合し、原タグ源を保持した出力CSVを成果物へ保存した。

| 原追跡 | q1/60minでの5dbar潜水候補 | 4補正方式による候補範囲 | q1/60min GPS時刻対応 | 4補正方式のGPS対応範囲 | 時間変動ゼロ点幅 |
|---|---:|---:|---:|---:|---:|
| Laurie LIC001 | 1,481 | **1,476–1,481** | 901 | **897–901** | 0.30 dbar |
| Powell PI001/PIC001 | 4,786 | **4,771–4,825** | 2,117 | **2,113–2,132** | 0.60 dbar |
| Monroe MIC001 | 1,369 | **1,254–1,456** | 876 | **846–1,012** | **7.7525 dbar** |
| Signy SIC004 | 51 | **51–52** | 24 | **24–24** | 0.41 dbar |

3タグでは5dbar候補数が補正方式によって小幅にしか動かず、Monroeは最小～最大の幅202件（主解析1,369の約14.8%）で、GPS時刻対応数の幅166件（主876の約18.9%）。単一のゼロ点補正アルゴリズムに固定して「Monroeは潜水が少ない/長い」と結論するには不十分な品質状態。

**ここでの判定：原圧力/GPS接続は動作するが、島間で同じ潜水生態を推定するには計器固有のゼロ点挙動に対するQAが必須。** 初期の4追跡は事前固定の動作検査であり、ランダムな島の代表群ではない。ゼロ点補正は真の水深を保証せず、単独のTDR潜水をオキアミ捕食成功と解釈しない。圧力センサの原メーカー仕様・表層でのゼロ基準・潜水/陸上位相を外部照合するまで、潜水深さとモデル上のkrill値の新しい関連係数は使用しない。
