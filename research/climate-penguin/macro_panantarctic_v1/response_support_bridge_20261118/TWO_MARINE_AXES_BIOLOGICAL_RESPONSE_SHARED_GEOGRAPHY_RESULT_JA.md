# 南極ペンギンの二海洋環境軸と異なる生物応答：真の共通地理・年・地点での転写検証

**2026-11-18 JST | mina Draft PR #214, 既存main・凍結済みv0.5/Ecology Report/Paper2に非介入。** ユーザーの意図に合わせ、塩分×δ¹⁵Nの肯定結果を取り下げず、温度–海氷と塩分の二軸が「同じペンギンの異なる生物応答」に対応するという仮説を、同じ観測支持域へ転写できるか原資料だけで検証。

## 要約：肯定結果は維持。ただし多応答間の生態機構は地理・年でまだつながらない

1. **物理環境の確かな二次元性**：元595 siteに対するsource wet-cell gateで実海洋588地点×1993–2020の16,464 site-year／18報告地域（実wet grid378セル）、source-only PCAの暖・低海氷PC1＝60.3654%、塩分PC2＝33.3773%。地理的・時系列的に両者を別々に考える必要がある。PCAの直交性は因果的独立ではない。
2. **塩分–同位体の正の肯定結果**：Youngflesh original isotope optical proxy 860原source site×繁殖季節（88 original site, 82 wet grid cells, 13 region）では、同一site、原地域×season、撮影日、11〜翌2月のNSIDC V4海氷150km、GLORYS thetaoで調整しても、GLORYS塩分係数 **β=+0.8341458422 ‰/salinity unit**、条件付き残差partial R² **2.88018%**、82 wet-cell cluster CI **[+0.3886,+1.2797]**。元13地域クラスタの保守的CIは[−0.0159,+1.6842]と0を含み、大陸普遍の同一効果ではない。
3. **種間同年共調査は異なる地理**：元MAPPPD 2456 method-consistent実巣数レコードから、同年・同siteで2種とも巣数がある真正記録は**351 pair-rows**（ADPE/GEPE 98、CHPE/GEPE165、ADPE/CHPE88）。元物理18地域全体のうち、共調査があるのは7 region区分、その中で同位体sourceにも実観測があるのは4 region。
4. **新たに確認した地理転写の限界**：生物結果に依存せず共調査原観測地域を事前に選択して同じ同位体モデルを再計算すると、**227 isotope site×season（23 site、22 wetcell、4 region）でβ_salt=+0.0798953、wetcell CI [−0.3433,+0.5031]、partial R²=0.00043177（0.04318%）**。全13地域の効果はこの共通4地域にそのまま転写できない。**効果が有意に異なるという独立の検定ではなく、地域組成が違うsource集団の感度解析**。この4地域のうちC-West Antarctic PeninsulaとSouth Shetlandsの同位体系列はそれぞれ**1 site×seasonのみ**で、強い推定情報はNE/SW Antarctic Peninsulaに偏る。
5. **直接の同時複数応答が0**：元860 isotope site×seasonと元351二種共調査pair-rowの**厳密な同一site ID×same breeding-season一致は0**。同一site ID自体はHERO・DALR・PLATの3箇所で両sourceにあるが、共通観測年は0。source地域×seasonを同一視すれば共通は**7組のみ**で、該当する同位体38行と共調査24行は**別地点の観測**（年だけ近いものをペアとして共回帰しない）。

### 物理・生物の原資料支持を段階的に落とした結果

| パネルと比較 | original source件数・地点・独立性 |
|---|---|
| 元3変数海洋SIC+水温+塩分（8–11月） | 16,464 site×year、588 original site、378 distinct marine wet cells、18 region |
| 元δ¹⁵N光学proxy+同季節海氷/水温/塩分（11–翌2月） | 860 site×season、88 site、82 wetcells、13 region |
| 元同site・同年の2種巣数pair-row（8–11月気候で対応） | 351 pair-row、3 pair-combinations、6〜7 report regions（元source distinct totalは7） |
| 両者の観測地域unionではなく **intersection** | 4 region、δ¹⁵N **227** rows；co-census側の共通region行 **327** （全351から不共通regionを除く） |
| 両者の **region×season intersection** | 7 region×season group、**δ¹⁵N 38** rows と co-census **24** rows。互いにsite ID×seasonでは0 |
| 両者の **同一site ID×season** | **0** |
| δ¹⁵Nと同じoriginal ADPE巣数を実測した同一site×season（別比較） | **70** records、49 site、10 region。うち複数年に渡って同じsiteで両方あるのは**29 records/8 sites/4 region**。真の成長・prey比変化のパネルにはさらに不足 |
| 全3種実巣数とδ¹⁵Nの原同site×season一致 | 72 census records（70 ADPE＋他2種）、72 distinct site×season |

**原生物観測の地域極端性**：共調査351行のうちSouth Shetlands194行・Central-west Antarctic Peninsula113行、計 **307/351（87.5%）** を占める。一方、δ¹⁵Nのこの両地域の厳格sourceは**合計2/860**行しかない。逆に、δ¹⁵NのVictoria Land197行とWilkes Land146行、計 **343/860（39.9%）** には同site・同年の二種共調査行が0。生物の応答チャネルごとの見かけの地域特性を、直ちに生理・食性選好の差と解釈するのは誤り。

### 同じ地域×年まで絞った場合

同じ7 region×yearグループに由来するδ¹⁵N 38件だけに同じ元回帰式を条件付き再適合すると、β_salt=+1.5394、湿潤格子クラスタ95%区間 **[−0.2497,+3.3286]** と幅が非常に大きい。partial R²=22.0%は39行未満・多数singletonsからsite×region/year FEを削った**source選別の狭い残差におけるin-sample分母**であり、全域2.88%との予測/モデル改善比較禁止。こちらも二種巣数の個々の行とは同時観測ではない。

### 既存二軸–種間巣数応答との統合

元の[二海洋軸×3種共調査のSource監査](../DUAL_MARINE_AXIS_PENGUIN_RESPONSE_RESULT_JA_20261111.md)では、二種巣数比は3組とも共通のPC1/PC2方向を示さず、ヒゲ対ジェンツーPC2の弱い負方向は一原地域の除外で符号反転した。今回の解析では、島嶼・生態的機構が存在しないことを示したのではなく、**同じ環境軸で測っても、生物応答2系列の地理・年代・サイト支持が一致しないため「海氷は個体数、塩分は食性」という普遍的なチャネル分業を同時検証できない**と判定した。

### 論文上の優先順位

- **mainの肯定結果として維持**：温度–海氷PC1と塩分PC2という物理二軸、観測既知繁殖地間の実巣数配分変化、特定地点でのジェンツー/アデリー比の変化、source cohortでの将来の海氷物理曝露。島間・種内の機構は出典/調査単位を同じにする。
- **塩分×δ¹⁵Nの明確な肯定結果も消さない**：元860 sourceでの条件付き正相関をv0.6候補の生物結果として明記。ただし今回のsource地域限定0.080と元13地域clusterのCIゼロ横断、翌年塩分の時間負対照、観測POM基準値不足を同時記載。
- **禁止する過大解釈**：「海氷軸は繁殖だけ、塩分軸は食性だけ」「一方の相関を別生物応答に転写」「同じ13地域を3種共通生態実験と呼ぶ」「δ¹⁵Nを直接魚食割合と呼ぶ」「1970〜2100ペンギン動的巣数予報」。真の共通同一site×seasonの複数応答がない。
- **次の研究に必要**：同じ繁殖地域・観測季節・site固定に実δ¹⁵N/餌・共調査巣数・同一海氷/塩分観測が反復して存在する複数独立regionの前向き/原記録パネル。

## 再現

Source-fixed Python [`audit_response_channel_transfer.py`](audit_response_channel_transfer.py)、[GitHub Actions #44222977506 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44222977506)、artifact **14390778853**。Inputs: 元Youngflesh原source δ¹⁵N+海氷/GLORYS matched860 artifact 14328755565；元595/2456 true source counts artifact 13669533413；元588×28物理+351共調査 artifact 13828472111。全3 ZIPをGitHub原source artifactから取得し、元標本境界、ゼロ/欠測、site×season重複、全860先行βの正確な再現、4地域sourceへの制約下β、0同site同年、7同region-yearを別stepsで独立検算。出力JSON/地域表/3組別表/7年地域表/70 ADPE生同時記録をarchiveへ保存。mainと凍結v0.5は未変更。

**確定判定**：全源sourceの塩分–同位体の肯定相関あり。同時に地理制約でその効果は不安定なため、他の生物応答へ一律の「塩分が効く」機構を移せない。これは生物応答が異なる可能性への情報であり、チャネルごとの独立した機構を立証した結果ではない。

## 追加検証：共通地域で塩分の物理的変動が消えていただけか？

**否。** 同じ固定生物/物理ソースと同じ調整変数で、塩分を site FE、original region×season FE、撮影日・DOY²、Nov–FebのGLORYS水温、NSIDC海氷から残差化した塩分原物理コントラストを別に算出。source全860行では塩分残差SD **0.1889633**、共調査4地域に絞った227行では**0.2245062**と、狭めた側の方が大きい。site/region-season FEだけを抜いた段階でもそれぞれ**0.2230196**対**0.2634045**。

したがって、salinity β=+0.834→+0.080の地理条件付き減衰は**塩分残差変動が数学的に消滅したためではない**。あくまで別地域・別観測site・別原気候環境という母集団変更であり、個体食性機構の差やβ差の仮説検定ではない。

[原固定sourceの全860と狭域227、残差SDを追加したCI #44224044031 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44224044031)、artifact **14392141706**。コード・レポートのsourceキーとcrosswalk分母に変更無し。前のoriginal #44222977506も独立保存。
