# Climate, sea ice and penguin breeding: exploratory progress

Research checkpoint, 2026-10-30. This directory is a draft research lane. It does not replace the frozen Paper 1 / Paper 2 analyses or establish publication readiness.

## 2026-11-10 追加：3種の同年共調査ニッチも元データから検証済み

**[元同年3種ペアの地理・地域内・同地点時系列の完全比較](macro_panantarctic_v1/COCENSUS_NICHE_RESULT_JA_20261110.md)**を追加。1991–2020年・近岸海氷に同年照合できた元3種ペアはアデリー/ジェンツー**100地点年／25地点**、アデリー/ヒゲ**89／24**、ヒゲ/ジェンツー**168／33**。地域平均を除いた地点等重み相関rは**+0.285／−0.069／+0.016**で、すべて250km空間ブロック区間は0を含む。見かけの地点年プールrでは3組とも微小な負方向だが、サイトを一票にすると一部の符号が反転する。**同一地域で3種が共通の海氷巣数応答を示すという結論は支持されない**。ただし元595地点は主分析の大陸規模の母体で、同年共調査の地点群は南極半島周辺の地域限定サブパネルであることを明示する。[元観測・元OSIからの2実装検算成功CI #42768561120](https://github.com/zuizui0223/mina/actions/runs/42768561120)。GPS Circuitscapeや特定地点の画像QAを再び論文の中心に増やさない。

## 2026-11-10 マクロ解析の統合結果を更新

**[最新の大陸規模マクロ結果・論文用の中心問い](macro_panantarctic_v1/MAIN_MACRO_INFERENCE_20261110_JA.md)**。南極595地点の元繁殖データ＋1991〜2020年の71,400地点月の原海氷が完成。**アデリー37・ヒゲ27・ジェンツー36の長期系列（77地点）**では、地域内海氷×巣数傾向の方向が種で異なる一方、250kmブロック95%区間は3種とも0を含む。

陸・海を同じ大陸規模で比較した**173植生陽性地点（8地域・14ブロック）**の解析も完了：海氷×静的植生の全地点r=−0.3836、地域平均除去後r=+0.0969（ブロック区間−0.154〜+0.236）。海氷の地点間分散の**89.13%**は地域ごとの平均の差。元197地点×種の静的植生・海氷×巣数中央値の2環境係数もブロック区間に0を含む。**環境の地域間勾配と地域内生物応答を混同しない**というマクロ生態学のスケールの発見・限界として扱う。

[両分析を元ソースから照合したCI SUCCESS #42766156914](https://github.com/zuizui0223/mina/actions/runs/42766156914)。過去の25地点の衛星画像取得は補足的な品質確認に留め、主線を中断して新たなGAMのp値探索へ戻らない。原因機構・未来の巣数・緑化による媒介効果は未実証。

## 現在の主線（2026-11-09更新）— 南極全域のマクロ生態学

**ユーザー希望により小規模の衛星QA・食性だけの論文化から主線を修正した。** 今は[元MAPPPDの595地点・18地域・3種のマクロ観測台帳](macro_panantarctic_v1/RESULT_JA_20261109.md)が出発点。2,456件の調査法を固定した元巣数、303地点×年の複数種同年記録、87の100km固定空間格子を元ハッシュで独立再構築済み（[CI SUCCESS](https://github.com/zuizui0223/mina/actions/runs/42610664607)）。

**海氷レイヤーの小規模40地点制約も解消**：元OSI SAF海氷の1991〜2020年8〜11月を595地点全てで抽出、**71,400地点×月／120原NetCDF**を全件取得（[CI SUCCESS](https://github.com/zuizui0223/mina/actions/runs/42612067836)）。元40地点の既存資料と4,800件照合してr=0.99996。これは**海氷の実測原データの大陸的な拡張**であり、温暖化によるペンギンの巣数変化を証明したわけではない。

**次の唯一の生物検定**は[1991–2020年の長期同一方法の3種100地点×種系列／77地点／7地域を固定した海氷×巣数トレンド比較](macro_panantarctic_v1/THREE_SPECIES_100_TREND_TEST_CONTRACT_20261109.md)。地点×種で巣数と海氷を**同じ計数年**だけで評価し、地域平均・250km空間ブロックによる脆弱性を監査する（[実行ジョブ](https://github.com/zuizui0223/mina/actions/runs/42613076334)）。海氷・植生・ニッチの大陸的関係を一つずつ識別するのが目的で、単独のpを救うモデル変更や未調査地点の擬似不在は行わない。

**植生はまだ別レイヤー**：Plantarcticaの2017–2023年静的地図が元222/595地点と一致する。静的植生を1991〜2020年の年次緑化と見なさず、陸側の環境ニッチの空間勾配として扱う。かつての「25地点の年次NDVIとGAMのpを追う」路線（Draft PR #213）は検証資料として保管するが、大陸規模の主論文の分母にしない。

## 現在の主線（2026-11-07）— 温暖化を一本化したペンギン論文

**新しい唯一の主論文は [warming_unified_v1](warming_unified_v1/README.md)。** 以前の海鳥JNCC繁殖集中の共通帰無は別の研究成果として保存し、温暖化影響の直接証拠に加算しない。繁殖群集6地点・Signy同年9季節の海と時間のニッチ・同地点CMIP6 4条件の出典照合を実行した。[英語全文初稿](warming_unified_v1/MANUSCRIPT_WARMING_UNIFIED_V0_1.md)。温暖化の物理曝露と将来の実巣数予報は分ける。BTOの追加データ待ちやメール送信を主線へ入れない。

以下は旧作業・原本監査の索引であり、肯定結果も限界も保存する。

## Start here

- **[2026-11-05・BAS3種GPS×TDR全78元タグと孵化前後の空間再分配](outputs/signy_three_tdr_gps_alltags_v2/REPORT_JA.md)** — 原圧力候補133,525、元GPS結合100,293、共通時計693時間。2015年の厳格2tag同時刻×各7日ではChinstrap孵化前+13.83km→後−29.98km（元GPS-only同じ時間も+3.86→−27.37km）。Clewlow2019既報leapfrogのsource検証。


- **[2026-11-05・Signy 3種のGPS×TDR原個体ID監査](outputs/signy_three_species_TDR_GPS_source_v1/REPORT_JA.md)** — BAS新取得のAdélie/Gentoo元TDRと既存Chinstrap v2原TDR、GPS各3ZIPのソース照合。潜水解析の前のスキーマ・原ID支持ゲート。
- **[2026-11-05・Signy 3種の潜水候補×GPS同時刻再解析](outputs/signy_three_tdr_gps_pilot_v1/REPORT_JA.md)** — 2013・2015年の源GPS標本のみでタグを固定し、元TDRのセンサ補正、GPSブランケット、同じ暦日・同時計で種間の位置差を監査。解析結果はCI検証前に主張しない。


- **[2026-11-04・Signy元胃37種ペア×年は同日採取ゼロ：育雛段階と暦日の比較可能性](outputs/signy_calendar_sample_overlap_v1/REPORT_JA.md)** — 1,364元胃、孵化日がある14年で胃採取中央値は孵化時期差29日にほぼ追従。同暦日±7日で選ぶと逆に雛齢段階が25日ずれる。
- **[2026-11-04・Signy元GPSの2種同日65日・共通1時間1,121枠と年別の空間配置](outputs/signy_calendar_GPS_spatial_v1/REPORT_JA.md)** — 元168タグのSHA固定。2タグ以上の2013年24日（距離差+50km）と2015年16日（−6km）、孵化日差・地域平均海氷が近くても距離配置が変わる探索的証拠。捕食・競争機構ではない。


- **[2026-11-03・BAS元平均孵化日17年×海氷](outputs/signy_original_hatching_source_v1/REPORT_JA.md)** — 公開DOIの34種×年を取得。海氷増加時に両種孵化日は遅い方向（r+0.576/+0.622）、時期差は平均29.3日、海氷とのr+0.078。
- **[2026-11-03・実孵化日と食性・原雛数14年の3軸同年結合](outputs/signy_hatching_diet_chick_v1/REPORT_JA.md)** — 元BAS7ZIP・1,001胃と同年照合。胃試料採取時期は両種とも平均孵化後約31〜32日、元監視コロニーが繁殖計数と一致するのは4年だけ。


- **[2026-11-03・Signyヒゲ到着調査17年の観測開始日偏りと13年3軸同年照合](outputs/signy_chinstrap_arrival_multiaxis_v1/REPORT_JA.md)** — 公式168原行・17暦年、13年の魚利用・雛計数・SIC同年接続。観測された到着数中央値は初回調査日に依存（r=0.726）。実カメラの二種定着差とは区別。


- **[2026-11-03・Signy 2016〜19海×時間×陸の同年4繁殖季・原日付順序検証](outputs/signy_three_axis_same_season_v1/REPORT_JA.md)** — 同実カメラSIGNc×原BAS242胃×原繁殖巣区画を2種×4季節で照合。胃採取は全8種×年で早期雛数計数後・後段階計数前。4!相関は非確証的。


- **[2026-11-03・Signy原BASの海氷×食性×早期雛数／後段階巣立ち雛数の差](outputs/signy_trophic_productivity_ice_v1/REPORT_JA.md)** — 原6ZIPを照合した9繁殖季で記録段階によって海氷との相関が変化。固定コロニー（5/8）、後段階が前段階を上回る元16/158、12比較9!極端率0.176を記録。


- **[2026-11-02・Signyの３種食性差はGentoo魚割合が主に寄与](outputs/signy_species_trophic_forward_v1/REPORT_JA.md)** — 元９年の食性差×先行SICは数学的にGentoo共変動が約99.8%を担う。４季節時系列外MAE 0.3114→0.1680（同島・事後探索）。
- **[2026-11-02・SCAR外部データの質量・trace・再現性ゲート](outputs/scar_external_diet_v1/REPORT_JA.md)** — 41,010元餌項目から３種1,180行31出典。Cape Shirreffの２種魚類割合は数値的に１共通繁殖季、Signy再録は独立島ではない。
- **[2026-11-02・Stranger Point別島のAdélie12季節×海氷](outputs/scar_stranger_point_ice_v1/REPORT_JA.md)** — 単独Adélieの微量魚利用が近岸SICと探索的に負相関。重複する海氷参照を別地点反復と数えない。


- **[Signy以外の海ニッチ：Palmer原同位体・3島の海氷観測独立性監査（2026-11-02）](outputs/palmer_original_isotope_niche_v1/REPORT_JA.md)** — 344原記録から324性別既知同位体、6同島・同年種ペアを測定。3島を2海氷環境系列へ厳格照合し、Signy胃内魚率の追試とは区別。


- **[Signy実測食性ニッチ×海氷の正確9年検定・採取日監査（2026-11-02）](outputs/signy_marine_niche_robustness_v2/REPORT_JA.md)** — 3種同年9季節の胃サンプルからGentoo−他2種の魚類比率差を測定し、9!順列・2海氷期間・育雛採取日差を厳格監査。元の各軸肯定結果は維持。


- **[温暖化と時間・海・陸ニッチの統合結果（2026-11-02）](CLIMATE_NICHE_SYNTHESIS_20261102.md)** — 6地点の巣数実変化、Signy胃1,364試料、47種季節・37食性ペア、45同年の食性×雛数と物理CMIP6を統合。すべて因果・未来繁殖数予測とは分離。


- **[海のニッチ：Signy 3種の原胃内容物×先行海氷実測（2026-11-02）](outputs/signy_diet_climate_v1/REPORT_JA.md)** — 元639/653/74試料から魚/甲殻類質量比を個別胃→species×繁殖季へ集約し、先行GOPT海氷との種間差を分析。独立した餌食性資料。


- **[Signy海のニッチ：3種BAS食性・繁殖時期・繁殖成績の原ソースゲート（2026-11-02）](outputs/signy_three_diet_source_gate_v1/REPORT_JA.md)** — 1997–2020年の2種と1998–2010年のジェンツーの胃内容物の原CSVを独立取得してデータ粒度を検査。新しい因果結果は未主張。


- **[新結果：種構成の長期変化と観測年の海氷の不一致（2026-11-02）](outputs/niche_timescale_divergence_v1/REPORT_JA.md)** — 厳格共存6地点・67共通年・45連続年。実巣数比は6/6増、観測年9月SICは4/6増、1991–2020年の8–11月SICは6/6減。


- **[温暖化と時間・陸・海のニッチ：2同一カメラ・計数結合ゲート（2026-11-02）](outputs/temporal_niche_cross_axis_v2/REPORT_JA.md)** — 2組の正確な順列検定と、同年巣数への結合が2地点年だけという同定制約を再現。



- **[3種のMAPPPD長期繁殖数×実測海氷のマクロ解析・CMIP6統合（2026-10-31）](outputs/breeding_count_macro_v1/REPORT_JA.md):** 元729地点・5,487観測から3種の計数を抽出、40地点海氷と一致した725地点×種×季、56地点×種、連続年467区間、長期傾き54地点×種、CMIP6 224地点×種×シナリオを実行。3種の海氷年変化との関連は探索的で補正後有意なし。アデリーの歴史的減少地に将来海氷減少の大きい地域が偏るが、地域内相関は約0。AEI/REMA陸上環境の追加比較も保存。
- **[最優先研究主題 v3：温暖化はペンギンの繁殖をどう変えるか](RESEARCH_GOAL_WARMING_IMPACTS_V3.md)** — 温暖化→繁殖時期・繁殖数・種構成の実測と条件付き2050/2100生物予測。単なる気候曝露地図・繁殖集中の理論を主線にしない。
- **[観測された同地点の種間繁殖構成変化](outputs/warming_species_breeding_v1/REPORT_JA.md)** — 同じ方法・同じ地点・同年の繁殖数比でGentoo/Adélie 7/7、Chinstrap/Adélie 6/6が長期増加方向。8地点のCMIP6未来気温/SICへ同位置で接続（将来種比は未較正）。
- **[39地点アデリー：長期海氷×繁殖成長とCMIP6の条件付き変化](outputs/historical_ice_breeding_transfer_v1/REPORT_JA.md)** — 1991–2020実測の空間相関 r=+0.622。線形移植は世紀末SSP585に成長率傾向の負方向を出すが、二次モデルでは符号が反転しうる。
- **[同地点・過去2時期の生物応答の答え合わせ](outputs/historical_temporal_transfer_v1/REPORT_JA.md)** — 23地点の1991–2005/2006–2020海氷変化と実繁殖数傾向変化はr≈+0.269。空間係数を時間効果へ単純に転写する較正は未成立。


- **[南極40地点・30年の実測海氷：距離別の地域共通変動（2026-10-31）](outputs/sic_spatial_coherence_macro40_v1/REPORT_JA.md):** 40地点の元SICを30年・4月・近傍／沖合に接続し、6,240件の地点ペアの年次海氷相関を再計算。9月の50km未満r中央値=0.991、250–500km=0.315、1000km以上=0.011。広い沖合では250–500kmでもr=0.797。全件の独立照合と地点除外感度を保存。
- **[実測海氷の地域共通性と局所年変動の分解（2026-10-31）](outputs/observed_sic_covariance_scale_v1/REPORT_JA.md):** Palmer周辺から南の6固定地点×1991–2020年×8–11月の0–100km／100–500km衛星海氷を元値から再集計。9月近傍の分散内訳は年共通87.94%、地点固定10.93%、地点×年固有1.137%。海域が重複するため島内区画の独立海氷とは言えない。独立検証・地理座標・全数CSVを保存。
- **[観測された近隣の海氷変動の同期性と局所差（2026-10-31）](outputs/observed_nearby_sic_covariance_v1/REPORT_JA.md):** 2011–2020年の元衛星SIC、沿岸参照5地点×8–11月×2製品バッファ。年変動は共通成分97%以上だが絶対値の局所差も残る。Palmerの真の5島・繁殖区画ポリゴンとの一対一対応ではない。

- **[繁殖集中×局所ショック：階層別N_effの定量化（2026-10-31）](outputs/climate_concentration_leverage_v1/REPORT_JA.md):** Palmer5島の実効島数3.45→3.08と実効センサス区画数31.06→6.15を分離。共通海氷ショックでは島内集中の増幅は数学的に起きない。Palmer/Signyの5系とρ感度、独立原本照合。
- **[局所海氷差の比較可能性ゲート（2026-10-31）](outputs/within_region_pair_support_v1/REPORT_JA.md):** 同種・同地域の全331ペア/将来条件から50厳密比較ペア（11地点、アデリーのみ）を確保。ただし同じモデル海域格子を共有し、ヒゲ・ジェンツーの厳密対照は未成立。


- **[地域構成と将来気候曝露の交絡・気候格子による見かけの分散（2026-10-31）](outputs/exposure_geographic_decomposition_v1/REPORT_JA.md):** 現在のAEI/REMA無氷地・地形46地点と将来のCMIP6海洋変化を照合し、5地域・25海洋格子指紋へ階層分解。地域内/地域間の相関、全3気候モデル、4将来条件、現地巣数の地点単位・モデル格子単位の実効数を比較。**生態学的な避難所選好や将来の巣数予測とは解釈しない。**

- **[Breeding allocation versus future climate exposure (2026-10-31)](outputs/breeding_allocation_exposure_v1/REPORT_JA.md):** Quantified 2017–2023 observed site-median nest allocation across three penguins against physical CMIP6 warming/sea-ice/salinity changes, compared equal-site, nest-weighted and region-conditioned exposures. Original AEI/REMA 122-site source artifacts supply 46 matched site-code land-context traits. The observed geographic allocation is not a forecast of nest survival nor a mapped subcolony refuge test.
- **[Climate–breeding/vegetation spatial crosswalk (2026-10-31)](outputs/land_marine_colocation_v1/REPORT_JA.md):** 58 original site×species rows across 48 site IDs matched to 106 fixed CMIP6 climate coordinates; 188 unmatched source rows preserved. Includes land-mask QA, CSV, GeoJSON and source-level audit.
- **[Matched-colony conditional future direction audit (2026-10-31)](outputs/future_direction_identifiability_v1/REPORT_JA.md):** 19 strict camera-geographic site×species matches, 76 scenario panels, 912 original two/four-environment model predictions. All 76 panels contain both earlier and later conditional predictions; no calibrated breeding forecast.
- **[Spatial CMIP6 exposure atlas (2026-10-31)](outputs/cmip6_exposure_atlas_v1/REPORT_JA.md):** physical air-temperature, sea-ice and salinity change at 106 fixed locations, grouped into 43 repeated three-model marine-grid fingerprints.

- **[Latest integrated findings: correlations and conditional scenarios](outputs/research_synthesis_v1/RESEARCH_STATUS_JA.md)**: updated inference, salinity, annual NDVI, mapped vegetation support, tracking limits and remaining work. Earlier reports below are dated checkpoints.
- [Full correlation atlas](outputs/correlation_atlas_v1/REPORT_JA.md), [salinity sensitivity](outputs/salinity_sensitivity_v1/REPORT_JA.md), and [conditional response decomposition](outputs/scenario_components_v1/REPORT_JA.md).
- [Salinity site-deletion sensitivity](outputs/salinity_site_influence_v1/REPORT_JA.md): 48 fixed specifications and 656 deletion fits. Adelie retains positive direction after each camera deletion; previous year-deletion sensitivity still crosses zero.
- [Matched-period salinity scenario component](outputs/salinity_scenario_component_v1/REPORT_JA.md): 144 conditional salt-only summaries, with coefficient deletion sensitivity and extrapolation flags. Not a complete future response and not additive to the previous two-variable prediction.
- [Surface-temperature projections and period alignment](outputs/surface_temperature_projection_v1/REPORT_JA.md): nine additional public stores, 30,528 September values, same three model members and salinity cells. Widespread future extrapolation and the tos/top-level potential-temperature definition difference remain explicit.
- [Four-environment conditional scenarios](outputs/four_environment_scenarios_v1/REPORT_JA.md): 288 joint air/ice/salinity/water scenarios, component decomposition, coefficient deletion sensitivity and four-dimensional observational support. Model specification can reverse the direction; these are not calibrated breeding-date forecasts.
- [Observed predictor separation and extrapolation scale](outputs/environment_identifiability_v1/REPORT_JA.md): Adelie water-temperature VIF is about 1.1, but future changes are 8–34 times its conditional observed residual SD. Large projected components do not establish strong observed future responses.
- [Observed nonlinear shape sensitivity](outputs/nonlinear_association_v1/REPORT_JA.md): all 48 one-quadratic-term specifications. Adelie water-temperature curvature remains negative in site/year deletions and the overlapping appendix cohort; this questions linear extrapolation but does not identify an ecological optimum or justify quadratic future forecasts.
- [Current versus previous September associations](outputs/previous_september_v1/REPORT_JA.md): 36 paired-cohort comparisons with mutual temporal adjustment and site/year deletions. Previous-year associations are exploratory and do not establish individual carryover mechanisms.
- [ERA5 snow grid support](outputs/snow_grid_support_v1/REPORT_JA.md): original snow-water-equivalent and land-mask snapshots acquired. Only 14 of 106 nearest cells have land fraction at least 0.5; local breeding-ground snow remains unvalidated, not a missing-value-to-zero join.
- [September regional snow series and associations](outputs/september_snow_v1/REPORT_JA.md): 330 daily 00 UTC snapshots, 1,166 complete location-months, and 36 descriptive land-support/species/cohort comparisons. Land-dominated coverage is too sparse to interpret this as a broad local-nest snow effect.
- [Annual NDVI/count comparison](outputs/vegetation_annual_ndvi_v1/REPORT_JA.md), [mapped vegetation overlap](outputs/ndvi_vegetation_overlay_v1/REPORT_JA.md), and [Landsat support](outputs/landsat_vegetation_support_v1/REPORT_JA.md). NDVI differences are not validated vegetation changes.
- [Completed historical count association analysis](outputs/long_count_seaice_v1/REPORT_JA.md) and [timing support](outputs/long_ice_timing_v1/REPORT_JA.md): 1991–2020 sea-ice acquisition and the 301-interval association analysis are now available, superseding the acquisition-in-progress statements in the earlier checkpoints below.

- **[Earlier checkpoint: vegetation, sea ice, salinity and warming scenarios, 2026-10-30](CLIMATE_RELATIONSHIPS_AND_SCENARIOS_20261030.md):** same-cohort relationships on 169 species/site/seasons; vegetation associations on 246 site/species units; actual 3-model CMIP6 extraction at 106 coordinates. Future environmental changes are quantified; biological future responses remain uncalibrated.
- [Current research objective](outputs/climate_penguin/RESEARCH_GOAL_V2.md): correlation-first work across climate, sea ice, drift, ocean conditions and vegetation, leading to conditional future scenarios. Predictive performance and descriptive relationships are distinct questions.
- [September relationships and conditional historical prediction](outputs/relationship_response_v1/REPORT_JA.md): identical complete cases, between/within-site comparisons, and chronological evaluation using realized heldout-year environments at previously observed sites.
- [Vegetation and observed breeding counts](outputs/vegetation_response_v1/VEGETATION_RELATIONSHIPS_RESULTS_JA.md): 2017–2023 map/count period alignment, regional contrasts, detection sensitivity and species comparisons on common observed site/seasons.
- [CMIP6 future environments](outputs/cmip6_projection_v1/REPORT_JA.md): 27 actual store reads, 381,600 monthly point values, 1995–2014 baseline and two future periods under SSP2-4.5/SSP5-8.5. Three models, one member each; native-grid, uncorrected environmental projections.
- [Exploratory significance](outputs/climate_penguin/EXPLORATORY_SIGNIFICANCE_RESULTS_JA.md) and [wild-cluster sensitivity](outputs/climate_penguin/WILD_BOOTSTRAP_RESULTS_JA.md): 216 post-exploration comparisons. The initial approximate tests had 3 BY-adjusted candidates; none retained BH-adjusted significance in either one-way wild-cluster sensitivity. This is not evidence of no ecological relationship.
- [Year alignment](outputs/climate_penguin/ENVIRONMENT_YEAR_ALIGNMENT_JA.md): source October sea-ice covariates support the current season-start-year environmental join; individual camera dates and settlement calendar origin remain unresolved.
- [Offshore association analysis](outputs/climate_penguin/OFFSHORE_ASSOCIATION_RESULTS_JA.md) and [seasonal sea ice](outputs/climate_penguin/SEASONAL_ICE_RESULTS_JA.md).
- [NOAA tracking audit](outputs/climate_penguin/NOAA_TRACKING_AUDIT_JA.md): public raw tracks obtained, but winter coverage ends in August and cannot calibrate September–October return directions.
- [Satellite common support](outputs/climate_penguin/SATELLITE_MULTISCENE_RESULTS_JA.md): 106 coordinates screened; unequal observation opportunities and limited common clear land constrain vegetation comparisons.
- [Original-pixel reflectance validation](outputs/climate_penguin/REFLECTANCE_ORIGINAL_VALIDATION_JA.md): 28 sampled band comparisons resolve the offset convention for the selected 14 images. No vegetation trend has yet been estimated.
- [Matched-pixel NDVI comparison](outputs/climate_penguin/MATCHED_NDVI_RESULTS_JA.md): seven coordinates, identical clear-land pixels, dates matched within five days, and boundary-mask sensitivity. These are two-date spectral differences, not validated vegetation change or warming attribution.
- [Historical count support](outputs/climate_penguin/HISTORICAL_COUNT_SUPPORT_JA.md): the 1991–2020 scope has 301 eligible consecutive-year comparisons at 33 sites across six regions. The historical sea-ice series and count association analysis are now complete within the specified scope; see the updated links above.
- [Historical observation timing](outputs/climate_penguin/HISTORICAL_COUNT_TIMING_JA.md): 203 of the 301 comparisons have both counts confirmed after September, with stronger regional imbalance. The monthly aggregation pipeline reproduces all 3,200 existing 2011–2020 macro-site monthly SIC values; historical acquisition is now complete; see the updated timing and count analyses above.

## Scope and evidence limits

Settlement, nest counts, breeding success and migration behavior are distinct outcomes. Sea-ice concentration retreat is not necessarily physical melting. Directional drift near colonies is not an observed bird trajectory. Vegetation composites are not annual observations. All current environmental associations are exploratory; source-calendar uncertainties, small cluster counts and spatial/temporal dependence constrain inference. There is no validated future breeding-date projection in this checkpoint.

The broader goals remain open: migration-route identification, validated vegetation and breeding-patch measurements, and climate-scenario calibration; full-period count associations and conditional index scenarios have been delivered. No goal completion is claimed by this PR.

## Layout and reproducibility

The original workspace-relative layout is retained inside this directory:

- `work/`: analysis and acquisition scripts authored during this research.
- `outputs/`: reviewable reports, derived tables, source inventories, checks and compressed daily environmental extracts.
- `SNAPSHOT_MANIFEST.json`: the earlier synchronization snapshot, not a manifest of later additions. The latest synthesis inputs are listed in `outputs/research_synthesis_v1/current_evidence_manifest.csv`.

Python scripts usually resolve the analysis root from their file location. Run from this directory when a script uses relative paths. Requirements vary by task; used packages include Python 3.10, numpy, pandas, scipy, statsmodels, rasterio, pyproj, shapely, geopandas, xarray, netCDF4, zarr, fsspec, requests and Pillow. The inference checkpoint used statsmodels 0.14.6. Dependency locking and a single end-to-end runner are not yet provided.

Raw external caches are intentionally not copied: satellite rasters, large NetCDF downloads, downloaded source documents, and some upstream data. The reports/manifests identify sources, versions and hashes where collected. Acquisition scripts cover many, but not all, inputs; a fresh clone cannot yet reproduce every step without restoring or downloading those inputs. Do not interpret a successful syntax/hash check as end-to-end reproduction. Older reports preserve the chronology; the newest reports linked above supersede their earlier unresolved/negative status where explicitly noted. Some image links in archived reports refer to omitted local previews.

External data and derivatives retain their source-specific licenses and attribution requirements; the repository's code license does not relicense external data. See source inventories and cited data DOIs, including Zenodo settlement data, NOAA/NCEI, OSI SAF, Copernicus Marine and Plantarctica.

## Synchronization

This is the rolling progress PR. At meaningful milestones, update the existing branch, manifest and summary rather than opening a new PR for each analysis. Synchronization does not imply merge or publication. No automatic scheduled task or unattended push has been installed.

The original workspace's `work/climate_penguin/sync_progress_snapshot.py --checkout <checkout>` copies the scoped outputs and scripts into this directory without committing or pushing. It is an additive sync: deletions must be reviewed explicitly. Never run it with source and destination set to the same directory.
