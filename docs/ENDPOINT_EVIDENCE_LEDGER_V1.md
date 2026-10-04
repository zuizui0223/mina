# 66 endpoint evidence ledger v1

**Frozen source:** `main@7764523c5f1e536b86084de8583cdd6262ee8fa7`, `results/` = **66 files**.  
**Purpose:** 結果を物語に合わせて選別するのではなく、66件を先に証拠強度で分類し、その後に階層ストーリーへ写像する。

## 証拠段階

- **E1 確証:** 事前凍結された独立系・別種の再現。主張の土台。
- **E2 頑健な探索:** discovery、bounded post-hoc、頑健性を伴う探索的関連。解釈・仮説生成には使うが、単独で一般化しない。
- **E3 範囲を限定した否定:** 事前仮説の失敗、独立再現失敗、感度解析による一般性の否定。近接する主張とセットで本文に出す。
- **E4 データで停止:** 問いに必要なデータ構造がなく、効果を開けない。
- **A0 補助監査:** schema、coverage、recoverability、source sensitivity、reproducibility等。重要だが生態学的な独立証拠として数えない。

**Counts:** E1 **3**, E2 **17**, E3 **14**, E4 **1**, A0 **31**.  
E1の3ファイルのうちSigny Adélie 2件は同じデータ/主張線なので、独立した確証線は **Signy Adélie（地理的再現）** と **Signy chinstrap（別種再現）** の2本。

## 66件の台帳

| # | Result | 段階 | 階層 | 役割 | 現在許される読み方 |
|---:|---|---|---|---|---|
| 1 | `AEI_VAT_SCHEMA_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | audit | AEI/VAT schema integrity audit only; no ecological outcome. |
| 2 | `ANTARCTIC_BREEDING_OPTIONS_ATLAS_GATE1_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_gate | 2-km breeding-option atlas coverage/variation gate passed; demographic outcomes remained closed. |
| 3 | `ANTARCTIC_BREEDING_OPTIONS_HIERARCHY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_gate | Habitat-complex richness frozen as primary heterogeneity trait; no demographic outcome opened. |
| 4 | `ANTARCTIC_TERRAIN_ATLAS_GATE1D_A_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_gate | Terrain coverage passed and relief selected over redundant elevation SD; no outcome opened. |
| 5 | `CONCENTRATION_DOMINANCE_DESCRIPTIVE_SUMMARY_V1.json` | E2 頑健な探索 | 島内/系内の配置 | posthoc_description | Same contraction endpoint arose via Palmer dominance turnover and Signy core retention; descriptive only. |
| 6 | `CONTRACTION_SCALING_LAW_SYNTHESIS_V1.json` | E2 頑健な探索 | 島内/系内の配置 | bounded_posthoc | Five local trajectories all had positive abundance–E scaling; common descriptive kappa about 0.25; search closed. |
| 7 | `CONTRACTION_SCALING_RULES_EXPLORATION_SUMMARY_V1.json` | E2 頑健な探索 | 島内/系内の配置 | bounded_posthoc | No universal threshold, instantaneous law, predictor of kappa, or universal quarter-power constant; bounded exploratory synthesis. |
| 8 | `EXPLORATORY_RESULT_V1.json` | E2 頑健な探索 | 種・表現型 | exploratory | Apparent island phenotype largely reflects species composition; within Adelie island signal is weak and non-transferable across years. |
| 9 | `MAPPPD_MACRO_GEOGRAPHY_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | audit | Macro sample broad but geographically uneven; species and geography partly confounded; no outcomes modeled. |
| 10 | `MAPPPD_MACRO_INVENTORY_RESULT_V1.json` | A0 補助監査 | データ範囲 | inventory_gate | Pygoscelis macro trend lane viable; emperor/king/macaroni not viable in same lane; no outcome opened. |
| 11 | `MAPPPD_OBSERVATION_METHOD_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | audit | Observation-method heterogeneity audit; methodological support only. |
| 12 | `PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | E2 頑健な探索 | 島内/系内の配置 | discovery | Palmer discovery: all three stable-roster islands concentrate beyond proportional thinning under the full frozen count-error family. |
| 13 | `PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json` | E2 頑健な探索 | 機構の痕跡 | exploratory_association | N_eff carried a small positive next-year growth association beyond abundance/time; later permutation removed the predictive claim but not the conditional association. |
| 14 | `PALMER_EXTERNAL_SPATIAL_TRIANGULATION_RESULT_V1.json` | E2 頑健な探索 | 島内/系内の配置 | external_triangulation | Independent Torgersen mapping shows non-random spatial attrition consistent with local contraction; identifier crosswalk and causality remain unresolved. |
| 15 | `PALMER_HIERARCHICAL_VARIABILITY_RESULT_V1.json` | E2 頑健な探索 | 島内/系内の配置 | exploratory_hierarchy | Observed temporal variability is reduced mainly within islands rather than among islands; full error robustness is limited by later CV20 null. |
| 16 | `PALMER_HIERARCHY_COMPONENT_COUNT_AUDIT_RESULT_V1.json` | A0 補助監査 | 島内/系内の配置 | posthoc_audit | Component-count diagnostic argues hierarchy is not only a unit-count artifact; not confirmatory. |
| 17 | `PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json` | E3 範囲を限定した否定 | 島内/系内の配置 | scope_limit | Raw hierarchy is unusual under Poisson/CV10 but compatible with CV20; centered signals cannot rescue full robustness. |
| 18 | `PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json` | E3 範囲を限定した否定 | 機構の痕跡 | falsification | Externally fixed >50-pair group metrics improve prediction error but coefficients have the wrong sign; directional hypothesis rejected. |
| 19 | `PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json` | E2 頑健な探索 | 地域・方向 | exploratory_context | Five neighboring Adelie islands share a dominant multi-decadal decline component while annual synchrony and local endpoints remain heterogeneous. |
| 20 | `PALMER_MANUSCRIPT_FIGURE_PACKAGE_RESULT_V1.json` | A0 補助監査 | 再現性 | packaging_audit | Reproducible figure package receipt; no ecological evidence. |
| 21 | `PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json` | E4 データで停止 | 個体過程の境界 | data_stopped | Public sources lack the band-to-later-breeding-site resight bridge needed for retention/dispersal inference; direct individual-movement lane closed. |
| 22 | `PALMER_NEFF_CIRCULAR_COUPLING_RESULT_V1.json` | E2 頑健な探索 | 機構の痕跡 | robustness | N_eff coefficient remains unusual under serial-structure-preserving coupled count-error nulls; no predictive claim restored. |
| 23 | `PALMER_NEFF_CIRCULAR_SHIFT_RESULT_V1.json` | E2 頑健な探索 | 機構の痕跡 | robustness | N_eff coefficient survives independent and joint circular-shift structured nulls; held-out prediction remains unsupported. |
| 24 | `PALMER_NEFF_DEMOGRAPHIC_MOMENTUM_RESULT_V1.json` | E2 頑健な探索 | 機構の痕跡 | robustness | Conditional N_eff association persists after one- and two-year demographic momentum controls; incremental predictive gain remains tiny. |
| 25 | `PALMER_NEFF_MECHANICAL_COUPLING_RESULT_V1.json` | E2 頑健な探索 | 機構の痕跡 | robustness | Shared census-error mechanics do not generate an observed-scale positive N_eff coefficient under frozen sensitivities; association only. |
| 26 | `PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json` | E3 範囲を限定した否定 | 機構の痕跡 | scope_limit | Held-out N_eff predictive gain is null-compatible (p=0.262); full-data coefficient remains unusual, so prediction is demoted to conditional association. |
| 27 | `PALMER_NETWORK_STAGE2_RESULT_V1.json` | E2 頑健な探索 | 地域・方向 | exploratory_context | Adelie decline recurs across local islands and endpoints differ (extinction/replacement/persistence); multi-island composition reassembly itself is not estimable. |
| 28 | `PALMER_PERFORMANCE_MEMORY_RESULT_V1.json` | E2 頑健な探索 | 機構の痕跡 | exploratory_mechanism | Reproductive performance shows weak short memory and past performance adds information beyond current state; persistent habitat and biological memory remain entangled. |
| 29 | `PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json` | E2 頑健な探索 | 機構の痕跡 | postexposure_validation | Lag-2/3 performance-linked redistribution is positive under fixed specification, but provenance repair followed exposure; delayed 4–5-year recruitment echo is rejected. |
| 30 | `PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json` | E2 頑健な探索 | 種・表現型 | bounded_exploration | Species sorting explains much island differentiation; within Adelie fixed island morphology is weak and cross-year island identity nearly disappears. |
| 31 | `PALMER_REPRODUCTIVE_DENOMINATOR_AUDIT_RESULT_V1.json` | E3 範囲を限定した否定 | 機構の痕跡 | scope_limit | Positive colony-size/chick count pattern is island-dependent and denominator semantics are unstable; no Palmer-wide Allee-like or pre-extinction reproductive collapse mechanism. |
| 32 | `PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json` | E3 範囲を限定した否定 | 地域・方向 | prospective_falsification | Predeclared positive annual sea-ice-duration mechanism and habitat moderation are not supported. |
| 33 | `PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json` | E3 範囲を限定した否定 | 地域・方向 | prospective_falsification | Predeclared 3/5/7-year low-frequency sea-ice-duration rescue fails; common decline is not recovered by smoothing the same index. |
| 34 | `PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json` | E3 範囲を限定した否定 | 地域・方向 | prospective_falsification | October snowfall-by-snow-prone-habitat interaction is opposite the predicted sign and worsens held-out prediction. |
| 35 | `PALMER_WIN_STAY_LOSE_SWITCH_RESULT_V1.json` | E3 範囲を限定した否定 | 機構の痕跡 | mechanism_falsification | Specific win-stay/lose-switch mechanism is not supported; only a broader within-island redistribution class remains compatible. |
| 36 | `PAPER2_A_BUFFERING_SECONDARY_RESULT_V1.json` | E3 範囲を限定した否定 | 静的な場所 | scope_limit | Simple breeding-space amount buffering is not supported after preregistered species-specific permutation/Holm inference. |
| 37 | `PAPER2_BREEDING_SEASON_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | Season chosen over calendar year before outcome modeling; no count magnitudes opened. |
| 38 | `PAPER2_CROSS_SPECIES_GENERALITY_V4_RESULT_V1.json` | A0 補助監査 | 静的な場所 | recovery_audit | Synthetic recovery shows cross-species median estimand can be recovered; no real outcomes opened. |
| 39 | `PAPER2_DETECTABLE_EFFECT_RESULT_V1.json` | E3 範囲を限定した否定 | 静的な場所 | scope_limit | Non-confirmatory macro result is informative against very large common effects (~/0.5/+), but not against effects around /0.3/; not an equivalence test. |
| 40 | `PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | descriptive_component | First real V3 point estimates are negative across species but were explicitly non-inferential pending permutation; primary inference lives in V3 permutation result. |
| 41 | `PAPER2_FORCING_SCALE_SENSITIVITY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | Forcing-scale sensitivity and fallback rules frozen before demographic outcomes. |
| 42 | `PAPER2_FORCING_SUPPORT_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | Forcing support and coverage audited before counts; no ecological outcome. |
| 43 | `PAPER2_H_MAIN_RECOVERY_V5_RESULT_V1.json` | A0 補助監査 | 静的な場所 | recovery_audit | Synthetic recovery shows H main effect estimable; no real outcomes opened. |
| 44 | `PAPER2_INTEGRATED_HIERARCHICAL_RECOVERY_RESULT_V2.json` | A0 補助監査 | 静的な場所 | recovery_audit | Hierarchical estimator recoverable species-wide, not at all regional scales; pre-outcome method gate. |
| 45 | `PAPER2_INTEGRATED_RECOVERY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | failed_method_gate | Initial integrated estimator failed pre-outcome recovery and counts stayed locked; triggered redesign rather than ecological interpretation. |
| 46 | `PAPER2_INTEGRATED_SENSITIVITY_SUPPORT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | Outcome-blind source-sensitivity coverage audit; ground-only Adelie lane coverage-limited. |
| 47 | `PAPER2_LATENT_FACTOR_RECOVERY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | recovery_audit | Latent-factor recovery selected species/region scales before real outcomes; observation layer not yet validated. |
| 48 | `PAPER2_OBSERVATION_OVERLAP_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | Direct/image overlap and accuracy precision structure audited before count magnitudes. |
| 49 | `PAPER2_OBSERVATION_RECOVERY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | recovery_audit | Synthetic observation nuisance layer recoverable; not ecological evidence. |
| 50 | `PAPER2_OBSERVATION_TIMING_SENSITIVITY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | sensitivity_support | Exact-date and <=14-day calibration leave focal direction essentially unchanged; does not alter non-confirmatory primary inference. |
| 51 | `PAPER2_PREDICTOR_IDENTIFIABILITY_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | A×H design is structurally identifiable with frozen group adjustment; no outcome claim. |
| 52 | `PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json` | E3 範囲を限定した否定 | 静的な場所 | scope_limit | 2-km negative to 5-km positive sign switch is not unusual under the frozen null; ecological scale-dependence language is not allowed. |
| 53 | `PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json` | E3 範囲を限定した否定 | 静的な場所 | scope_limit | A×H interaction is not invariant across radius or heterogeneity metric; cannot be a general island-architecture law. |
| 54 | `PAPER2_SPATIAL_ADJUSTED_V3_RESULT_V1.json` | A0 補助監査 | 静的な場所 | recovery_audit | Species-wide forcing plus spatial loading adjustment passes synthetic recovery; real outcomes still locked at that gate. |
| 55 | `PAPER2_TEMPORAL_OVERLAP_AUDIT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | 1980–2025 common window and complete-case support frozen before demographic values. |
| 56 | `PAPER2_V2_SENSITIVITY_SUPPORT_RESULT_V1.json` | A0 補助監査 | 静的な場所 | preoutcome_audit | V2 source-sensitivity testability audit; no real outcomes opened. |
| 57 | `PAPER2_V2_SOURCE_SENSITIVITY_RECOVERY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | failed_method_gate | V2 source-sensitivity recovery missed one frozen threshold; counts remained locked and estimator was not rescued. |
| 58 | `PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json` | E3 範囲を限定した否定 | 静的な場所 | confirmatory_null | Primary cross-species A×H permutation test is non-significant (p=0.0947); no species survives Holm adjustment, so only a suggestive tendency remains. |
| 59 | `PAPER2_V3_SOURCE_SENSITIVITY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | failed_method_gate | V3 source robustness misses Adelie exclude-unknown recovery threshold; no threshold relaxation. |
| 60 | `PAPER2_V4_SOURCE_GENERALITY_RESULT_V1.json` | A0 補助監査 | 静的な場所 | recovery_audit | Paper-level source-robustness estimand recoverable after exclusion sensitivity; methodological support, not ecological outcome. |
| 61 | `SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | E1 確証 | 島内/系内の配置 | prospective_replication | Independent Signy Adelie replication was predeclared after Palmer discovery and supports concentration beyond proportional thinning. |
| 62 | `SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | E1 確証 | 島内/系内の配置 | prospective_cross_species_replication | Separately frozen Signy chinstrap test supports the same concentration endpoint across species. |
| 63 | `SIGNY_CONCENTRATION_QUALITY_AUDIT_V1.json` | A0 補助監査 | 島内/系内の配置 | postresult_quality_audit | Quality audit retains frozen primary concentration result and forbids post-outcome season-exclusion rescue. |
| 64 | `SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json` | E1 確証 | 島内/系内の配置 | prospective_replication_same_dataset | Strict-roster 1998–2009 Signy Adelie replication is supported under all frozen error models; same dataset/claim line as the other Signy Adelie result, not an independent third geography. |
| 65 | `SIGNY_PERFORMANCE_REDISTRIBUTION_REPLICATION_RESULT_V1.json` | E3 範囲を限定した否定 | 機構の痕跡 | failed_independent_replication | Palmer lag-2 performance-linked redistribution does not replicate under the frozen Signy primary design; mechanism is locally plausible, not transferable. |
| 66 | `SIGNY_REPLICATION_SUPPORT_AUDIT_RESULT_V1.json` | A0 補助監査 | 機構の痕跡 | preoutcome_support_audit | Signy lag-2 replication support gate passed before effect computation; no effect in this audit. |

## 階層ストーリーへの写像

### 1. 地域は「方向」を持つが、単純な年次機構は残らない

E2の `PALMER_LTER_FIVE_ISLAND_SYNCHRONY` と `PALMER_NETWORK_STAGE2` は、近隣Adélie個体群が共通の長期減少方向を持つ一方、局所endpointが分岐することを示す。E3の年次sea-ice、3/5/7年平滑化sea-ice、October snowfall × habitatはいずれも事前仮説を満たさない。したがって言えるのは「地域要因がない」ではなく、**観測した単純な時間応答では共通方向を説明できない**まで。

### 2. 静的な場所の特徴は、移せる共通規則にならない

Paper 2のreal fitは方向を示したが、E3のprimary permutationは `p=0.0947`、species-specific Holm rejectionは0。さらにradius sign-switch nullとscale/trait sensitivityが一般性を削る。Detectable-effect解析からは「|effect|≈0.5以上の大きな共通効果なら多くの場合検出できた」が、|0.3|程度の効果不在は言えない。

### 3. 見かけの島の表現型情報は主に種組成にある

E2のPalmer phenotype analysesでは、full assemblageの島差はspecies sortingに強く依存し、Adélie内の固定島効果は小さい。pairwise sign reversalが頻発し、cross-year transferはほぼchance。したがって**場所固有の固定phenotype**より**種構成＋年ごとの再構成**が整合的。

### 4. 島内の繁殖個体配置だけが、発見から事前凍結再現まで残る

Palmer concentrationはE2のdiscovery。E1のSigny Adélie地理再現とSigny chinstrap別種再現が、比例的間引きを超えるeffective breeding-component contractionを確証する。E2のdominance/scalingは、その形が**経路は違うが方向は共通**で、universal thresholdやuniversal kappaではないことを示す。

### 5. 機構の痕跡は複数あるが、どれもE1には上がらない

N_eff conditional associationはserial null・mechanical coupling・momentum controlsを通るE2だが、E3 year-block permutationでheld-out predictionは失敗。Performance→redistribution lag2/3もE2だがpost-exposure validationで、E3のSigny replicationは失敗。>50-pair threshold、general reproductive/Allee interpretation、win-stay/lose-switchはいずれもE3。したがって**配置変化は確証、個体過程は未同定**が正しい。

### 6. 個体レベルへ降りるところでデータが切れる

66 resultファイル内の純粋なE4はmark-resight auditで、band IDから後年の繁殖場所へつなぐpublic bridgeがない。これが「配置の確証」から「個体の移動・保持・prospecting」へ進めない直接の境界。

## 本文での使用規則

1. **主張はE1からのみ立てる。** 現在の中心確証はbreeding-space contractionのSigny再現。
2. **Palmerはdiscoveryとして明記する。** E2の強さをE1へ格上げしない。
3. **E3は近接主張と対で出す。** 例: N_eff associationを書くなら predictive permutation failure も同時に書く。
4. **A0を「31件の追加証拠」と数えない。** これは解析の信用性を支える台座。
5. **E4はDiscussion末尾の次のデータ需要へ直結させる。** 個体標識/繁殖地resightが最優先。
6. **同一データの感度解析を独立replicateとして数えない。** とくにSigny Adélie 2 result filesとPalmer N_eff robustness family。

## 一文の統合

> 地域は長期的な減少方向を共有させるが、その単純な年次環境応答や静的な場所特性は移せる規則にならない。再現に耐えた情報は、減少する個体群の内部で繁殖個体がどの構成単位へ配分されるかにあり、その配置は個体数の比例的減少が要求する以上に集中する。しかし、その再配置を生む個体レベル過程は現在の公開データでは識別できない。

## Snapshot boundary

この台帳は**mainの66 result filesだけ**を対象にする。後のbranch-only cross-scale MAPPPD concentration、SMP contracts、またresults外の停止ルートは別の更新で扱う。
