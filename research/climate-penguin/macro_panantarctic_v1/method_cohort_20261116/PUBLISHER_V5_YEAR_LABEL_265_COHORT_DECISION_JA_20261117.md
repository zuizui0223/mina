# MAPPPD v5.0原本のシーズン年／暦年照合と265系列再現性

2026-11-17 JST｜mina Draft PR #214、元原本追跡と探索的PC1感度。主論文には未昇格。

## 原本の検証結果

MAPPPD v5.0（2026-10-21）の原出版社API 4 payloadを既存のsource SHA256で再取得した。729 site、5,487 original observations、そのうち対象3種の数値付き巣数観測は3,885件。元の派生2,999行から採択したseason/vantage既知268 site×speciesと、今回のoriginal 5,487行から独立に作った268 site×speciesは**元site×species IDが完全一致（268/268）**。したがって268の版・出所・サイトIDに矛盾はない。観測されない場所・種・年を0巣にしない。

| 1980–2000 と 2005–2025 に実際の記録があるsource条件 | 全種 | ADPE | CHPE | GEPE |
|---|---:|---:|---:|---:|
| seasonごとの一意な巣数 | 283 | 110 | 122 | 51 |
| seasonごとの既知・単一vantage | **268** | **103** | **114** | **51** |
| 暦年ごとの既知・単一vantage | **269** | **101** | **115** | **53** |
| season/暦年のどちらでも採択されるIDの共通集合 | **265** | **101** | **113** | **51** |
| seasonの前後期で少なくとも一つ共通vantage | 161 | 64 | 51 | 46 |
| seasonの前後期で唯一・同一vantageのみ | 96 | 31 | 34 | 31 |
| seasonの前後期で一つ以上共通する非空citekeyとvantageの組 | 82 | 41 | 17 | 24 |
| 旧scriptの通期最多vantage固定 | 159 | 64 | 51 | 44 |

原3種巣数3,885行で**暦年−season年=0は2,796件、+1は1,089件、それ以外0**。南極繁殖シーズンの年またぎと整合的で、誤入力とは断定しない。両ロスターの共通265 ID以外には、seasonのみ3 ID（ADPE2/CHPE1）、calendarのみ4 ID（CHPE2/GEPE2）がある。

以前の報告265系列は **ADPE102 / CHPE116 / GEPE47**。今回の「両ロスターに入った265系列」の **101/113/51** とは異なる。したがって**265という数だけが一致した別の集合**であり、以前の265系列を再現できたとは判断しない。元265の観測IDと生成コードが必要。元の熱–海氷効果−0.55、アデリー−0.80は再現済みではない。

## 偶然の265共通集合の環境PC1感度（探索のみ）

原シーズン年の前後期巣数中央値を使い、元報告地域×種で中心化したOLSを、以前と同じ海洋地点平均PC1・前期巣数・前後期実観測年数で実施。calendar年ロスターは共通集合の eligibility 判定にだけ使用した。共通265のうちPC1値のある **259系列**で、

**β_PC1 = −0.1815621、250km固定空間ブロック2,000回の条件付き2.5–97.5%点 [−0.9544426, +0.0454543]**。

元268（PC1対応262；β−0.1821488、区間[−0.9654043,+0.0464072]）とほぼ同じで、どちらもゼロをまたぐ。これらは地域が少ない条件付き再標本化感度であって母集団の信頼区間ではない。地点平均PC1は温暖化の局所的時間変化ではなく、年次の気候因果を示さない。過去の265係数と実際の標本・説明変数・回帰仕様が違い、係数を直接比較して再現性検定と呼べない。

原MAPPPDのvantageは元の観測位置／手段ラベルであって、調査手段間の測定誤差校正ではない。citekey+vantageが共通の82系列も、すべての元記録が同じcitekey/vantageで計数されたことを保証しない。重複で巣数が矛盾するsite×species×yearの数値を平均しない。原APIには暦年とdate/month/day列があるが、観測日と8–11月環境曝露の先行性は別途実確認が必要。

## 再現証拠と判定

- 元原出版社APIのsource version/dateと各原payload SHA：既存のsource-gated derive_MAPPPD5_original_macro_source_v1.pyで再検証。
- 元観測ID、calendar/season採択、vantage/citekey比較：reconcile_publisher_v5_longterm_lineage.py。
- 元267/268等の誤った標本数昇格を防ぎ、偶然の265共通集合を検証：explore_climate_pc1_method_sensitivity.mjsのcalendar-rosterオプション。
- 完了したGitHub Actions： https://github.com/zuizui0223/mina/actions/runs/43896717970 （SUCCESS）。原観測IDロスター・照合receipt・PC1感度JSONをartifactに保存。
- 固定Git blob sourceはderived2999 = fc134e364cf38699fa7611d7dee5fbbbcb370c0a、marine PC1 588 = 9b382f84e06f25317c801eb1b611563d8929e71f。

**総合：原本268系列の元ID/原API完全照合PASS。偶然の265が以前の265であるという解釈STOP。以前の気候βと2050/2100巣数への移植NO-GO。** 595既知地点のCMIP6物理曝露と271地点の原実数重みは別の再現済み記述結果として保持。単一主原稿v0.5／親PR #206／凍結Ecology Report／mainに今回の新しい生物学的有意効果を付加しない。
