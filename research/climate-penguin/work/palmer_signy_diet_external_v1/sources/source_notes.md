# Pickett et al. (2018) Palmer食性データの一次出典と利用上の注記

取得・照合日: 2026-11-06。対象は **Table 1の公表集計値、2種×6繁殖季（2009/10–2014/15）**。個体別胃内容物重量を取得したものではない。Palmer周辺の外部地域比較に使用できるが、同島・同コロニーでの再現検証とは扱わない。

## 1. 一次出典・公開条件・保存ファイル

Pickett EP, Fraser WR, Patterson-Fraser DL, Cimino MA, Torres LG, Friedlaender AS. 2018. Spatial niche partitioning may promote coexistence of *Pygoscelis* penguins as climate-induced sympatry occurs. *Ecology and Evolution* 8:9764–9778. DOI: [10.1002/ece3.4445](https://doi.org/10.1002/ece3.4445).

- 出版社全文: https://onlinelibrary.wiley.com/doi/10.1002/ece3.4445
- PMC全文: https://pmc.ncbi.nlm.nih.gov/articles/PMC6202752/
- 実際にHTTP 200で取得したJATS XML: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6202752/fullTextXML
- 対象テーブルのXML ID: `ece34445-tbl-0001`。
- ライセンス: **[Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**。原XMLの`article-meta/permissions/license`に、適切な原著引用を条件として使用・配布・複製を認める旨が明記されている。原著の著作権表示は©2018 The Authors。本パッケージは上記原著Table 1からの抽出・変換であり、餌群別の表を種×繁殖季の機械可読CSVへ変換し、出典・季ラベル・表示精度と丸め区間・不一致フラグを追加した。原表の数値は変更していない。抽出表と原文資料は原著引用および本ライセンス表示とともに提供する。
- `pickett2018_europepmc.xml`は実取得した全文XMLの原バイト。出版社HTMLの直接取得はHTTP 403だったので、HTMLと偽って保存していない。
- `web_wiley_table1_excerpt.txt`は[出版社全文](https://onlinelibrary.wiley.com/doi/10.1002/ece3.4445)を別経路で読み取ったテキスト抜粋。Table 1は保存抜粋のL262–288に対応する。これらは保存した読み取り結果の行ラベルであり、出版社HTMLの固定行番号ではない。元HTMLではない。
- `primary_source_excerpts.txt`は保存XMLから抽出した関連方法・結果・公開条件の本文。
- 本文のDATA ACCESSIBILITYは原データとメタデータを出版から1年以内にLTER Network Data Portalで公開する予定とする。これは個体別CSVの存在・現時点でのダウンロード成功の証明ではない。本作業では個体別データを取得していない。Table 1そのものの公開・再利用条件とは区別する。

### 機械可読ファイル

| ファイル | 内容 |
| --- | --- |
| `pickett2018_palmer_diet_species_season.csv` | 主入力。12行、1行=1種×1繁殖季。全4餌カテゴリーの平均・SD・出現頻度・原表示、n、表の行番号、平均の丸め区間。 |
| `pickett2018_table1_long.csv` | 48行、1行=1種×1季×1餌カテゴリー。カテゴリー別n、平均・SD・出現頻度それぞれの表示精度と丸め区間を保持。 |
| `extraction_verification.json` | 入力ハッシュ、照合件数、nの合計、不一致、組成和などの機械可読記録。 |
| `extract_pickett2018.py` | 保存済みXMLの抽出と出版社web reader版との照合を再実行するスクリプト。ネット接続不要。 |

両CSVともUTF-8、カンマ区切り、ヘッダー1行。百分率列は0–100の数値で、0–1比率ではない。`sd_pct`は平均と同じ百分率単位の標準偏差で、SEやCIではない。`raw_cell`には原表の表示文字列を保存した。

## 2. 原表の行と抽出の検証

Table 1のデータ行は、ヘッダーを除き1から数える。rowspanの餌名を継承して抽出し、4カテゴリー×6季×2種を欠落なく保存した。

| データ行番号 | 出版社reader行 | 原表の餌カテゴリー | 年ラベル |
| --- | --- | --- | --- |
| 1–6 | L265–270 | *Euphausia superba* (%) | 2009–2014 |
| 7–12 | L271–276 | *Thysanoessa macrura* (%) | 2009–2014 |
| 13–18 | L277–282 | Unidentified fish (%) | 2009–2014 |
| 19–24 | L283–288 | Other prey items (%) | 2009–2014 |

独立した2つの取得表現（Europe PMC JATS XMLと出版社ページのweb reader表）を別のパーサーで読み、48セルについてmean・SD・occurrence・nの**192値を全数比較し一致**した。これは転記・抽出の照合であり、原著内の誤植が存在しないという検証ではない。原表の各種×各季では4カテゴリーのnが一致している。

丸めた4カテゴリー平均の和は、アデリー2009=100.0、2010=99.9、2011=100.0、2012=99.9、2013=100.0、2014=100.0%。ジェンツーは全6季100.0%。元の値は100%へ再正規化していない。

## 3. 採集時期と海氷年の結合

一次根拠: Methods “Study site and species”、XML `ece34445-sec-0003`。本文は、繁殖のchick-rearing phaseについて、**12月末から2月中旬、2009（2009–10 field season）から2014（2014–15 field season）**に野外調査を行ったとする。

したがってTable 1の年`y`は繁殖季開始年として保存した。

| 原表のYear | CSVのseason_label | 採集窓の表現 |
| --- | --- | --- |
| 2009 | 2009/10 | 2009年12月末–2010年2月中旬の調査期 |
| 2010 | 2010/11 | 2010年12月末–2011年2月中旬の調査期 |
| 2011 | 2011/12 | 2011年12月末–2012年2月中旬の調査期 |
| 2012 | 2012/13 | 2012年12月末–2013年2月中旬の調査期 |
| 2013 | 2013/14 | 2013年12月末–2014年2月中旬の調査期 |
| 2014 | 2014/15 | 2014年12月末–2015年2月中旬の調査期 |

本文が示すのは調査期の一般窓で、各胃標本の具体的な日付ではない。CSVには推測した日付を入れていない。海氷はまず`season_start_year`を明示した結合とし、冬・春の先行窓、繁殖期窓、1年遅れ等を区別する。2010というラベルを無条件に2010年1–2月の採集と扱うと1年ずれる。

Methods “Dietary analysis”、XML `ece34445-sec-0004`では、天候によるがほぼ5日間隔、1採集日につき各種5個体、巣に戻るように見える推定繁殖成鳥からwater off-loadingで胃内容物を得たとする。試料数は年単位の独立な海氷曝露の数ではない。種間差を各季に作った場合、外部検証の時間方向の観測数は**6季**である。

## 4. 地理: 同地域・異なる主要コロニー

一次根拠: Methods “Study site and species”、XML `ece34445-sec-0003`。Discussionは種効果とコロニー効果を分離できない設計と明記する。

- Biscoe Point: 64°48′S, 63°46′W。アデリーとジェンツーが主に別コロニーで営巣。ジェンツーの主要調査コロニー。
- Humble Island: 64°45′S, 64°05′W。アデリーの調査コロニー。
- Torgersen Island: 64°46′S, 64°04′W。後期のアデリー調査コロニー。
- Humble/TorgersenはBiscoe Pointのおよそ15 km西で、アデリーのみが占有すると本文に記載。

Table 1は各胃標本の島・コロニーIDや季ごとのコロニー切替日を収録していない。Biscoe Pointに両種が営巣していることだけから、Table 1の両種試料をBiscoe Point同所採集とみなさない。CSVの地理単位は`same_region_different_primary_study_colonies`。広域海氷への共通曝露を用いる外部地域比較であり、Signyと同じ同島設計の再現検証には数えない。

## 5. 統計単位、分母、変換の限界

一次根拠: Methods “Dietary analysis”、XML `ece34445-sec-0004`、Table 1 caption。排水・選別・秤量した餌のwet mass %を計算し、Table 1は**percent diet compositionのmean ± SD**と、別指標として括弧内に**frequency of occurrence (%)**を示す。個々の胃試料組成の平均として扱う。絶対湿重量や胃試料ごとの組成は表からは復元できない。

### 取得できた値

- `e_superba_mean_pct`、`t_macrura_mean_pct`、`fish_mean_pct`、`other_mean_pct`: 公表された平均湿重量構成比。
- `*_sd_pct`: その標準偏差。
- `*_occurrence_pct`: その餌が検出された胃試料の割合。湿重量構成比とは交換不可。
- `sample_n`またはlong表の`n`: Table 1の標本数。

### Fish/(Fish+krill)を作る場合

Table 1から直接計算できるのは、次の**平均組成比から作った比**である。

`R = mean_fish_pct / (mean_fish_pct + mean_e_superba_pct + mean_t_macrura_pct)`

これは一般には、個々の胃で魚とオキアミだけに分母を限定してから平均した`mean[F_i / (F_i + E_i + T_i)]`とは一致しない。胃内容物の絶対重量を全個体でプールした`sum(fish_mass_i) / sum(fish_mass_i + E_mass_i + T_mass_i)`とも一致しない。各標本の重量、共分散、個体内分母がないため、これらの統計量間の厳密変換やRの正確な標準誤差は得られない。

`R`を使う場合は`ratio_of_reported_mean_compositions`など、集計方法を結果に明記する。丸められた平均の非線形変換である点も保持する。Signyの統計量と集約単位が異なれば、測定方法の感度分析または外部の方向性確認として位置づける。

*E. superba*だけをkrill分母に入れると、2010/11季のアデリーに36.0%、ジェンツーに6.6%含まれる*T. macrura*を落とす。同季のアデリー*E. superba*63.6%という値を魚への置換として読まない。Table 1の魚は同季アデリー0.2%、ジェンツー0.3%である。

Results “Dietary overlap”、XML `ece34445-sec-0008`はOtherにamphipods、isopods、mysid speciesを含むとする。いずれも甲殻類だが、この文の“included”だけではOtherがそれらだけから成る完全な分類辞書は得られない。`F/(F+E+T)`は「魚対2種のオキアミ」の指標。これを「魚対全甲殻類」と同一視するにはOtherの分類を別途確認するか、Otherを含む/除く感度分析を行う。

## 6. nの不一致を保持する

| 種 | Table 1の各季n（2009–2014） | 表の合計 | Methods本文の合計 |
| --- | --- | ---: | ---: |
| Adélie | 23, 25, 15, 25, 21, 27 | 136 | 136（77雄、59雌） |
| Gentoo | 10, 15, 36, 20, 18, 30 | 129 | 128（64雄、64雌） |

ジェンツーの不一致は未解決。表内では4餌カテゴリーすべて同じ季別nを示す。本文の合計に合わせて36を35へ変えるなどの修正は行っていない。原表の平均・SD・出現率もそのまま保持し、ジェンツーの全行に`table_total129_vs_methods128`を付した。

この不一致のため、nによる精密な分散重み付けや推定個体データの復元は優先しない。各季を1観測とする6季の比較ではnを説明情報として残し、原データまたは訂正が得られるまで表/本文のどちらが正しいかを断定しない。

## 7. 表示精度と丸め区間

- meanとSDは全48セルで小数第1位までの表示。表示値`x`について、近接丸めを仮定した保守的な閉包区間`[max(0, x−0.05), x+0.05]`を保存した。構成比の上端は100で切る。境界での丸め規則は論文に記載がないため、両端を含む保守的なenvelopeとして扱う。
- 出現率は原表示が`100`や`0`のセルと、`0.0`等の小数第1位のセルが混在する。long表の`occurrence_display_quantum_pp`と丸め区間は**表示された桁数**から作った。全例100%という本文もあるが、表示桁を勝手に細かくしていない。
- これらは**表示丸めに関する区間であって、信頼区間でも標本誤差でもない**。通常の近接丸めという条件が必要で、論文は丸め処理自体を明示していない。
- `0.0 ± 0.0`であっても出現率が正のセルがある。例えば2014/15季Otherはアデリー3.7%、ジェンツー6.7%。したがって表示0.0を「生態的に完全な不在」や「絶対にゼロ」と置き換えない。
- 原表示は`raw_cell`に残した。構成比和99.9%を埋めるなどの補正も、tracesや欠測値への再符号化もしていない。

## 8. 再実行

リポジトリルートから実行する。Python標準ライブラリのみを使用する。

```bash
python research/climate-penguin/work/palmer_signy_diet_external_v1/sources/extract_pickett2018.py
```

同ディレクトリの保存済みXMLとweb reader抜粋からCSV2点、関連本文抽出、照合JSONを再作成する。海氷の取得・結合・統計計算はこの抽出スクリプトの担当外。既存図の転載は行っていない。
