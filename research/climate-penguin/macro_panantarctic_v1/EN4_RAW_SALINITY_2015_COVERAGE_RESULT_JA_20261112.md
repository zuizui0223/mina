# EN4現場塩分観測による南極18地域の同期性検証：2015年のデータカバレッジ監査

**2026-11-12 JST｜実際に原本を取得・QCした結果｜Draft PR #214｜判定: 18地域の生の現場観測による塩分同期検証 NO-GO**

## 中心結果

以前の Copernicus GLORYS12V1再解析では、南極18報告地域・588繁殖地、1993–2020年の海洋PC2（ほぼ塩分）の共通年次変動成分が**52.14%**であり、各地域の直線的な28年トレンドを除いても**50.61%**だった。海氷・水温のPC1はそれぞれ19.71%、19.84%。これは同じ再解析に基づく物理的な記述的同期であり、現場で独立に確認されたという意味ではない。

**今回初めて、別の品質管理済み現場観測プロダクトEN4.2.2の原NetCDFプロファイル（補間されたEN4解析格子ではない）を読み込んで、2015年8–11月の観測支持を原地点別に監査した。**

真の元595サイトのうちGLORYSソース地理25km以内で認識できる**588 site・18地域**を照合対象とした。観測プロファイルは最寄りの元site一つのみに割り当て、測器と元QCを明示した。

**原繁殖地100km以内、実測0–10m、元位置・塩分プロファイル・レベル品質フラグすべて1に合格した実測塩分プロファイルは385件、5地域のみ。うち371件（96.4%）がSouth Shetland Islandsに集中。測器識別子を確認すると、385件はたった12種類の原観測プラットフォームに対応し、単独の最多プラットフォームで176プロファイルだった。**

したがって、**2015年の真正近岸現場塩分だけでは、全18地域での同期や1993–2020年の28年変化を照合することはできない**。これは観測データのcoverage NO-GOであり、GLORYSの塩分同期が実在しないという科学的な反証ではない。

## 実際の観測数

| 原プロファイル | 8月 | 9月 | 10月 | 11月 | 合計 |
|---|---:|---:|---:|---:|---:|
| EN4.2.2全球rawプロファイル | 44,080 | 43,324 | 43,438 | 39,559 | **170,401** |
| 原588サイトの250km以内、QC前位置 | 333 | 167 | 82 | 75 | **657** |
| 250km以内、0–10mの品質管理済み塩分 | 259 | 122 | 22 | 11 | **414** |
| 100km以内、0–10mの品質管理済み塩分 | **250** | **114** | **18** | **3** | **385** |

QCは原POSITION_QC・PROFILE_PSAL_QC・PSAL_CORRECTED_QCが各1で、実測DEPH_CORRECTEDが0–10m、PSAL_CORRECTEDが28–38の範囲内の値のみ。最浅い真正合格レベルを抽出。測定していない表層塩分0mは作らない。真の位置を楕円体WGS84で計算、近接プロファイルが複数の繁殖siteに複製されないよう、最寄りsite一つに割り当てた。250kmは存在の感度で、先行研究の100km海氷バッファと同じ海域ではない。

### 地域・プラットフォームの独立性

| 100km以内、0–10m | 実QCプロファイル数 | 原データ識別プラットフォーム |
|---|---:|---:|
| South Shetland Islands | **371** | 7 |
| Wilkes Land | 10 | 2 |
| Victoria Land | 2 | 1 |
| Elephant Island | 1 | 1 |
| South Orkney Islands | 1 | 1 |
| 残り13地域 | **0** | 0 |
| **合計** | **385** | **12** |

うち真のプロファイル元sourceは**WOD系382、GTSPP系2、ARGO系1**。12はsource識別プラットフォームの数であり、12独立の長期気候反復ではない。0–10m・100kmで3プラットフォーム以上ある地域は1地域のみ。2015年の四か月すべてに本当に少なくとも一つの元表層塩分がある地域も1地域のみ。

深度/空間感度でも、0–20m・100kmは**424 profiles / 5地域 / 12識別プラットフォーム**、0–10m・250kmは**414 / 8地域 / 21プラットフォーム**、0–20m・250kmは**530 / 10地域 / 24プラットフォーム**。より深い・遠い観測を選択的に混ぜても、18地域同期を確定できるわけではない。

## Source integrity とデバッグ記録

公式EN.4.2.2 g10生プロファイル元ZIP 2015年版は**727,111,596 byte**で、直リンク4個の月次 .nc.gz は404だった。初回の年間ZIP一括取得は本研究の設定600MB転送上限で停止。その後英国気象庁サーバーのHTTP206 byte-range が真に利用可能だとGitHub Actions [#43127855730](https://github.com/zuizui0223/mina/actions/runs/43127855730)で実証し、ZIP内から2015年8〜11月**だけ**遠隔バイト範囲で復元した。原ZIPに記録されたCRC32を完全に検算して月別NetCDF SHA256を個別に保存。**年間全727MBのSHA256は計算していない**ので原本全体のSHAが完全一致したとは言わない。

またnetCDF4のPOSITION_QC等の1文字flagは、0次元numpy masked character arrayとして返り、初回実装は真のQC値1を表示文字列 b'1' として誤判定していた。これを原因特定・修正し、元位置QC、プロファイルQC、レベルQCのヒストグラムを追加して再検証。**修正後の385件/12平台source診断のみを主結果として採用**し、修正前に誤って算出された0件は科学的な結果として用いない。

公開するのは source URL/各月NetCDF SHA/元ZIP CRC/ソース距離・深度・月・地域・プラットフォームの集計とQC情報だけで、非商用政府ライセンスの元ZIPや個別raw塩分観測値をrepository/artifactへ再配布しない。

## 結論の境界

- **Yes:** 現場塩分観測の地理的、季節的、深度的、観測プラットフォーム上の非一様性を原ソースで検証。2015年8–11月0–10m・100km以内の真の現場塩分は南極18地域の時系列一括検証には不十分。
- **No:** 元のGLORYS再解析塩分PC2の52%同期を現場観測で独立に再現した、または否定した、とは言わない。EN4 rawは観測sourceだがGLORYSが同じ元Argo/CTDなどを同化している可能性もあるため、元観測を広く集めても完全に独立した実験とはならない。
- **No:** 塩分がペンギンの繁殖巣数や群集転換を支配すること、塩分変化が海氷融解由来であること、28年間の植生・繁殖応答に塩分の因果ラグがあること。真のペンギン2種同年観測351 source recordsのPC2との応答は弱く地域除外で符号反転した。
- **Next independent measurement gate:** 年を変えたraw Argo+CTDの品質管理済みプロファイルを、機器数・実月別coverageを明示して追跡するか、EN4の**観測重みと解析誤差付き1°格子分析**を別PRODUCT感度として比較する。後者は観測空白域への内挿であり、独立in-situ検証とは決して言わない。

## Reproducibility

- [**Original EN4 raw 2015 in-situ 0–10m QC and 12-platform source run #43129617403 — SUCCESS**](https://github.com/zuizui0223/mina/actions/runs/43129617403), artifact **13904608166** (source month-level CRC/SHA, QC, region, platform counts; no original raw profile redistribution).
- Code: pilot_EN4_2015_raw_profile_salinity_coverage.py, unit_test_EN4_2015_raw_profile_gate.py; workflow .github/workflows/penguin-original-EN4-2015-raw-salinity-profile-coverage.yml.
- Original source licence/format: UK Met Office Hadley Centre EN4.2.2 https://hadleyserver.metoffice.gov.uk/hadobs/en4/ and https://www.metoffice.gov.uk/hadobs/en4/en4-0-2-profile-file-format.html. Cite Good, Martin and Rayner 2013, JGR Oceans, DOI **10.1002/2013JC009067**.
- Previous GLORYS source result [REGIONAL_MARINE_SYNCHRONY_RESULT_JA_20261112.md](REGIONAL_MARINE_SYNCHRONY_RESULT_JA_20261112.md), [Actions #43049546362](https://github.com/zuizui0223/mina/actions/runs/43049546362).
- This remains one exploratory Antarctic macroecology manuscript in Draft PR #214. Frozen Paper 1/2, main, warming v0.6, previous climate PR #206 and separate bright/dark PR #215 unchanged.
