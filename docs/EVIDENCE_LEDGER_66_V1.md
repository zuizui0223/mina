# Evidence ledger for all 66 main-branch result records — v1

**Source universe:** all 66 JSON files in `results/` at main SHA `7764523c5f1e536b86084de8583cdd6262ee8fa7`. No result record is omitted.

## Evidence classes

- **A — confirmatory:** prospectively frozen independent or cross-species replication that directly supports the focal ecological claim.
- **B — robust exploratory/fixed-specification:** ecological signal or triangulation that is useful but not independent confirmatory evidence.
- **C — informative negative / scope limiter:** a failed frozen test, failed replication, directional reversal, sensitivity failure, or quantitative bound that removes or narrows a claim.
- **D — stopped before inference:** the ecological question could not be answered because a data, estimability, or recovery gate failed.
- **N — non-evidential infrastructure:** audits, predictor construction, synthetic recovery, intermediate fits, and reproducibility records. N is not a fifth evidence strength; it means the record should not be counted as ecological evidence.

## Counts

| Class | Records |
|---|---:|
| A | 3 |
| B | 18 |
| C | 15 |
| D | 4 |
| N | 26 |
| **Total** | **66** |

The record count is deliberately not the evidence count. Re-analyses and robustness checks sharing one data/hypothesis family are linked by `independence_group`; they do not receive independent “votes.” In particular, records 61 and 64 are both Signy Adélie concentration records and count as one independent replication family.

## Complete 66-record ledger

| # | Result record | Information level | Tier | Record type | What the record actually says |
|---:|---|---|:---:|---|---|
| 1 | `AEI_VAT_SCHEMA_AUDIT_RESULT_V1.json` | infrastructure | **N** | audit | AEI/VAT predictor schema audit; no ecological outcome inference. |
| 2 | `ANTARCTIC_BREEDING_OPTIONS_ATLAS_GATE1_RESULT_V1.json` | static_place | **N** | data_gate | 2-km breeding-option atlas passed coverage and variation gate before demographic outcomes. |
| 3 | `ANTARCTIC_BREEDING_OPTIONS_HIERARCHY_RESULT_V1.json` | static_place | **N** | predictor_selection | Tier-2 richness retained as primary heterogeneity trait; redundant alternatives demoted before outcomes. |
| 4 | `ANTARCTIC_TERRAIN_ATLAS_GATE1D_A_RESULT_V1.json` | static_place | **N** | data_gate | Terrain atlas passed coverage; relief retained, absolute elevation kept contextual. |
| 5 | `CONCENTRATION_DOMINANCE_DESCRIPTIVE_SUMMARY_V1.json` | within_island_configuration | **B** | exploratory_descriptor | Palmer concentration occurred by dominance turnover whereas Signy retained and strengthened its initial core. |
| 6 | `CONTRACTION_SCALING_LAW_SYNTHESIS_V1.json` | within_island_configuration | **B** | exploratory_descriptor | Five local trajectories all had positive abundance–E scaling; common descriptive kappa about 0.25. |
| 7 | `CONTRACTION_SCALING_RULES_EXPLORATION_SUMMARY_V1.json` | within_island_configuration | **B** | bounded_exploration | Smooth scaling beat fixed hinges, annual first-difference coupling was weak, and no simple predictor explained kappa. |
| 8 | `EXPLORATORY_RESULT_V1.json` | species_composition | **B** | exploratory_ecology | Apparent island morphology was largely compositional; within-Adelie island phenotype was weak and temporally reassembled. |
| 9 | `MAPPPD_MACRO_GEOGRAPHY_AUDIT_RESULT_V1.json` | static_place | **N** | audit | Macro sample was broad but geographically uneven; species and geography partly confounded. |
| 10 | `MAPPPD_MACRO_INVENTORY_RESULT_V1.json` | static_place | **N** | data_gate | MAPPPD contained 152 Pygoscelis candidate site×species trend units and 92 stricter units. |
| 11 | `MAPPPD_OBSERVATION_METHOD_AUDIT_RESULT_V1.json` | static_place | **N** | audit | Observation vantage/accuracy heterogeneity audited before demographic modeling. |
| 12 | `PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | within_island_configuration | **B** | discovery_robustness | All three stable-roster Palmer populations concentrated beyond proportional thinning under the full frozen count-error family. |
| 13 | `PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json` | mechanism_trace | **B** | exploratory_association | Effective colony number showed a small positive next-year growth association beyond abundance and time; predictive framing was later downgraded. |
| 14 | `PALMER_EXTERNAL_SPATIAL_TRIANGULATION_RESULT_V1.json` | within_island_configuration | **B** | independent_triangulation | Independent Torgersen mapping showed strong habitat-structured footprint loss, converging at phenomenon level but not identifier level. |
| 15 | `PALMER_HIERARCHICAL_VARIABILITY_RESULT_V1.json` | within_island_configuration | **B** | exploratory_hierarchy | Most observed variability reduction occurred within islands rather than among islands, but biological buffering was not yet identified. |
| 16 | `PALMER_HIERARCHY_COMPONENT_COUNT_AUDIT_RESULT_V1.json` | within_island_configuration | **B** | robustness_audit | Post-hoc diagnostics showed the hierarchy was not explained solely by comparing more lower-level units. |
| 17 | `PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json` | within_island_configuration | **C** | informative_negative | Raw hierarchy exceeded Poisson/CV10 expectations but was compatible with the uncalibrated CV20 sensitivity; strong buffering claim fails. |
| 18 | `PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json` | mechanism_trace | **C** | informative_negative | Fixed >50-pair group metrics improved prediction but coefficients reversed the preregistered protective direction. |
| 19 | `PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json` | regional_direction | **B** | frozen_context | Five Palmer islands shared a dominant long-term decline component (PC1 96.4%) while annual growth synchrony was only moderate. |
| 20 | `PALMER_MANUSCRIPT_FIGURE_PACKAGE_RESULT_V1.json` | infrastructure | **N** | reproducibility | Manuscript figure package reproduced frozen numerical results. |
| 21 | `PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json` | individual_process_limit | **D** | data_gate_stop | Public mark/resight sources lacked the band-to-later-breeding-site bridge required for direct retention/dispersal inference. |
| 22 | `PALMER_NEFF_CIRCULAR_COUPLING_RESULT_V1.json` | mechanism_trace | **B** | robustness | N_eff coefficient remained unusual under coupled circular-shift/count-error nulls; prediction remained unsupported. |
| 23 | `PALMER_NEFF_CIRCULAR_SHIFT_RESULT_V1.json` | mechanism_trace | **B** | robustness | Positive N_eff coefficient survived serial-structure-preserving circular-shift nulls, including exact covariance-preserving shifts. |
| 24 | `PALMER_NEFF_DEMOGRAPHIC_MOMENTUM_RESULT_V1.json` | mechanism_trace | **B** | robustness | N_eff association persisted after one- and two-year prior-growth controls, but incremental prediction became tiny. |
| 25 | `PALMER_NEFF_MECHANICAL_COUPLING_RESULT_V1.json` | mechanism_trace | **B** | robustness | Shared current-year count error did not generate an observed-scale positive N_eff coefficient under frozen sensitivities. |
| 26 | `PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json` | mechanism_trace | **C** | informative_negative | Held-out predictive gain was null-compatible (p=0.262) although the conditional coefficient remained unusual; prediction claim rejected. |
| 27 | `PALMER_NETWORK_STAGE2_RESULT_V1.json` | regional_direction | **B** | mixed_outcome_gate | Multi-island Adelie decline was estimable and replicated; synchronized multi-island composition reassembly was not estimable. |
| 28 | `PALMER_PERFORMANCE_MEMORY_RESULT_V1.json` | mechanism_trace | **B** | exploratory_mechanism | Reproductive performance showed weak 1–2 year memory and added information beyond current state, consistent with layered local dynamics. |
| 29 | `PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json` | mechanism_trace | **B** | fixed_spec_validation | Bias-resistant lag-2 performance→redistribution association survived fixed specification after provenance repair; not fully preregistered. |
| 30 | `PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json` | species_composition | **B** | exploratory_ecology | Species sorting plus year-specific within-species structure explained apparent island phenotype better than persistent island ecotypes. |
| 31 | `PALMER_REPRODUCTIVE_DENOMINATOR_AUDIT_RESULT_V1.json` | mechanism_trace | **C** | informative_negative | Pooled colony-size/chick association was island-dependent; Palmer-wide Allee-like reproduction and pre-extinction collapse were not supported. |
| 32 | `PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json` | regional_direction | **C** | frozen_negative | Preceding-year sea-ice duration and its habitat moderation failed the preregistered positive annual-growth mechanism. |
| 33 | `PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json` | regional_direction | **C** | frozen_negative | Predeclared 3/5/7-year sea-ice-duration rescue failed; simple low-frequency duration did not explain the shared decline. |
| 34 | `PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json` | regional_direction | **C** | frozen_negative | October snowfall×habitat interaction was opposite the preregistered direction and worsened held-out prediction. |
| 35 | `PALMER_WIN_STAY_LOSE_SWITCH_RESULT_V1.json` | mechanism_trace | **C** | frozen_negative | Specific win-stay/lose-switch asymmetry failed; redistribution remained compatible with several broader dynamic processes. |
| 36 | `PAPER2_A_BUFFERING_SECONDARY_RESULT_V1.json` | static_place | **C** | frozen_negative | All three simple area effects were negative but none survived preregistered species-specific Holm inference; buffering hypothesis unsupported. |
| 37 | `PAPER2_BREEDING_SEASON_AUDIT_RESULT_V1.json` | static_place | **N** | audit | Season field and 1980–2025 window fixed before count magnitudes were opened. |
| 38 | `PAPER2_CROSS_SPECIES_GENERALITY_V4_RESULT_V1.json` | static_place | **N** | recovery_gate | Synthetic recovery showed the cross-species median interaction estimand was recoverable before outcomes. |
| 39 | `PAPER2_DETECTABLE_EFFECT_RESULT_V1.json` | static_place | **C** | scope_limiting_negative | Observed non-confirmatory interaction does not exclude moderate effects, but common effects around |0.50–0.55| would usually have been detected. |
| 40 | `PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json` | static_place | **N** | intermediate_outcome | First real-count V3 point estimates were explicitly non-inferential pending frozen permutation testing. |
| 41 | `PAPER2_FORCING_SCALE_SENSITIVITY_RESULT_V1.json` | static_place | **N** | design_gate | Regional versus species-wide forcing sensitivity was fixed before outcomes. |
| 42 | `PAPER2_FORCING_SUPPORT_AUDIT_RESULT_V1.json` | static_place | **N** | data_gate | Forcing support/coverage passed outcome-blind eligibility rules for all three species. |
| 43 | `PAPER2_H_MAIN_RECOVERY_V5_RESULT_V1.json` | static_place | **N** | recovery_gate | Synthetic H-main recovery passed before real outcomes; terrain-R inference remained unopened. |
| 44 | `PAPER2_INTEGRATED_HIERARCHICAL_RECOVERY_RESULT_V2.json` | static_place | **N** | recovery_gate | Hierarchical estimator passed only under species-wide forcing; regional recovery failure constrained the final estimator before outcomes. |
| 45 | `PAPER2_INTEGRATED_RECOVERY_RESULT_V1.json` | static_place | **D** | preoutcome_gate_stop | Initial integrated estimator failed synthetic recovery before any real demographic magnitude was opened; triggered redesign rather than threshold relaxation. |
| 46 | `PAPER2_INTEGRATED_SENSITIVITY_SUPPORT_RESULT_V1.json` | static_place | **N** | audit | Exclude-unknown remained testable for all species; ground-only was coverage-limited for Adelie before outcomes. |
| 47 | `PAPER2_LATENT_FACTOR_RECOVERY_RESULT_V1.json` | static_place | **N** | recovery_gate | Latent-factor scale recovery selected species-specific forcing scales before outcome access; observation layer still unopened. |
| 48 | `PAPER2_OBSERVATION_OVERLAP_AUDIT_RESULT_V1.json` | static_place | **N** | audit | Direct/image overlap and accuracy structure were audited outcome-blind to define the observation model. |
| 49 | `PAPER2_OBSERVATION_RECOVERY_RESULT_V1.json` | static_place | **N** | recovery_gate | Synthetic observation layer recovered the shared image offset and frozen accuracy structure before real outcomes. |
| 50 | `PAPER2_OBSERVATION_TIMING_SENSITIVITY_RESULT_V1.json` | static_place | **C** | robustness_of_negative | Exact-date/≤14-day calibration changed offsets modestly but not the interaction direction; primary permutation result remained non-confirmatory. |
| 51 | `PAPER2_PREDICTOR_IDENTIFIABILITY_AUDIT_RESULT_V1.json` | static_place | **N** | audit | A×H crossover design was full-rank/identifiable in all species before demographic outcomes. |
| 52 | `PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json` | static_place | **C** | informative_negative | Observed 2→5 km sign reversal was compatible with the joint radius null (p=0.081); biological scale-dependence claim prohibited. |
| 53 | `PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json` | static_place | **C** | informative_negative | A×H interaction was not invariant to radius or diversity metric; primary pattern cannot be a general island-architecture law. |
| 54 | `PAPER2_SPATIAL_ADJUSTED_V3_RESULT_V1.json` | static_place | **N** | recovery_gate | Spatially adjusted species-wide V3 estimator passed all frozen synthetic recovery checks before real outcomes. |
| 55 | `PAPER2_TEMPORAL_OVERLAP_AUDIT_RESULT_V1.json` | static_place | **N** | audit | Common 1980–2025 trend endpoint availability was established without opening demographic values. |
| 56 | `PAPER2_V2_SENSITIVITY_SUPPORT_RESULT_V1.json` | static_place | **N** | audit | Outcome-blind source-sensitivity support rules identified testable lanes; Adelie ground-only was coverage-limited but nonblocking. |
| 57 | `PAPER2_V2_SOURCE_SENSITIVITY_RECOVERY_RESULT_V1.json` | static_place | **D** | preoutcome_gate_stop | V2 exclude-unknown recovery missed the frozen 90/100 rule (88/100); no threshold relaxation and outcomes remained locked. |
| 58 | `PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json` | static_place | **C** | confirmatory_negative | All three interaction estimates were negative, but the preregistered cross-species permutation test failed (p=0.0947); no Holm species rejection. |
| 59 | `PAPER2_V3_SOURCE_SENSITIVITY_RESULT_V1.json` | static_place | **D** | preoutcome_gate_stop | V3 source-robustness gate failed Adelie exclude-unknown recovery (86/100); no threshold was relaxed and outcomes stayed locked. |
| 60 | `PAPER2_V4_SOURCE_GENERALITY_RESULT_V1.json` | static_place | **N** | recovery_gate | Paper-level cross-species source robustness passed before outcome unlock while Adelie-specific limitation remained explicit. |
| 61 | `SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | within_island_configuration | **A** | prospective_replication | Prospectively frozen independent-system Adelie test replicated non-proportional concentration. |
| 62 | `SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | within_island_configuration | **A** | prospective_cross_species_replication | Separately frozen chinstrap test replicated concentration across species. |
| 63 | `SIGNY_CONCENTRATION_QUALITY_AUDIT_V1.json` | within_island_configuration | **N** | quality_audit | Post-result quality audit retained the frozen primary concentration result unchanged and forbade rescue exclusions. |
| 64 | `SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json` | within_island_configuration | **A** | prospective_replication_robustness | Earlier/strict Signy Adelie concentration replication passed all frozen error models; same independence group as the later Signy Adelie record. |
| 65 | `SIGNY_PERFORMANCE_REDISTRIBUTION_REPLICATION_RESULT_V1.json` | mechanism_trace | **C** | failed_replication | Palmer lag-2 performance-linked redistribution did not replicate under the frozen Signy primary design; transferability not established. |
| 66 | `SIGNY_REPLICATION_SUPPORT_AUDIT_RESULT_V1.json` | mechanism_trace | **N** | data_gate | Outcome-blind Signy support audit passed feasibility for the later redistribution replication; effect not yet computed in this record. |

## Claim discipline

The paper-level claim should be erected only from **A** evidence. **B** records explain why the claim is biologically plausible and robust without being allowed to upgrade it. **C** records are part of the story rather than failures to hide: they eliminate simple regional forcing, static-place universality, predictive overclaim, and specific movement mechanisms. **D** records show exactly where the available data stop. **N** records make the exploration auditable but are not presented as ecological tests.
