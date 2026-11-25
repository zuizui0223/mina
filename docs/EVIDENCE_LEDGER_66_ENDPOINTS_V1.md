# Evidence ledger for the 66 frozen main-branch result endpoints v1

**Source snapshot:** `main@7764523c5f1e536b86084de8583cdd6262ee8fa7`  
**Population rule:** every JSON file in `results/` at that snapshot; exactly **66 files**.  
**Classification date:** 2026-10-04.

## Why this ledger exists

The repository contains a long sequence of exploratory analyses, prospectively frozen tests, failed gates, robustness checks and technical audits. Counting them as 66 independent pieces of ecological evidence would be wrong. This ledger assigns each result file an inferential role **before manuscript selection**, so the final story is constrained by the full analysis history rather than assembled from favorable results.

The central rule is: **only class A can independently confirm a positive biological claim.** Class B can discover, triangulate or strengthen a claim but cannot create an independent replication vote. Class C narrows or falsifies candidate explanations. Classes D and E carry no ecological vote.

## Evidence classes

| Class | Meaning | n | Manuscript use |
|---|---|---:|---|
| **A — Confirmatory replication** | Outcome frozen before effect inspection and used as an independent geographic or cross-species replication | 2 | Can support the headline positive claim |
| **B — Bounded robust / exploratory** | Discovery, closed post-hoc description, structured-null robustness, or independent process-level triangulation | 21 | Supporting evidence; never counted as an extra independent replication |
| **C — Scope-limiting negative** | A candidate mechanism, prediction, transfer rule or robustness claim failed or received a quantitative upper bound | 14 | Narrows the claim; negative results stay visible |
| **D — Data / identifiability gate** | Outcome was not opened, not recoverable, or the required data were unavailable | 21 | Records unanswered questions and prevents post-hoc substitution |
| **E — Technical / quality / provenance** | Schema, timing, quality or reproducibility audit without independent ecological content | 8 | Supports trustworthiness but adds no biological vote |

## Evidence strength by ecological layer

| Ecological layer | A confirmatory | B bounded/robust | C limiting negative | D data/gate | E audit | Total |
|---|---:|---:|---:|---:|---:|---:|
| Regional direction | 0 | 2 | 3 | 0 | 0 | 5 |
| Static place / transferable trait | 0 | 2 | 5 | 16 | 5 | 28 |
| Species / phenotype | 0 | 2 | 0 | 0 | 0 | 2 |
| Within-system breeding configuration | **2** | 8 | 1 | 0 | 1 | 12 |
| Mechanistic trace | 0 | 7 | 5 | 0 | 0 | 12 |
| Data limit | 0 | 0 | 0 | 5 | 0 | 5 |
| Technical / provenance | 0 | 0 | 0 | 0 | 2 | 2 |
| **Total** | **2** | **21** | **14** | **21** | **8** | **66** |

The concentration of class-A evidence in one row is the key result of the ledger. It does **not** mean that within-system configuration was tested only twice; it means that after discovery, robustness checks, null tests and failed mechanism transfers are prevented from being counted as independent votes, the only positive ecological endpoint that reaches prospective replication is breeding-space concentration.

The large number of static-place files should not be mistaken for strong evidence for static traits. Most are outcome-blind support/recoverability gates (D) or audits (E), and the real-data inferential endpoints are negative or scope-limiting (C).

## Publication-facing synthesis

The 66-file history reduces to a much smaller evidence structure:

1. **Regional direction is real context, not the explanation.** Palmer’s five Adélie island populations share a dominant long-term decline component, while frozen annual and low-frequency sea-ice and snowfall formulations fail to explain island-year growth.
2. **Static place does not yield a transferable rule.** The macro trait program accumulated many outcome-blind gates and recoverability checks, then its real-data permutation inference failed; radius and metric sensitivities further bound any scale-independent area/habitat rule.
3. **Apparent island phenotype is mostly compositional and temporally unstable.** Palmer phenotype analyses place most assemblage-level island signal in species composition; within Adélie, fixed island effects and cross-year transfer are weak.
4. **Within-system breeding configuration is the only positive endpoint that reaches prospective replication.** Palmer supplies the discovery; Signy Adélie and Signy chinstrap are the two class-A replication files. A strict Signy roster result is retained as nested robustness, not a third vote.
5. **Mechanism traces remain secondary.** N_eff has a robust contemporaneous/conditional association after several structured nulls, but its held-out predictive gain fails permutation. Performance-linked redistribution is nonconfirmatory in Palmer and fails prospective transfer to Signy. A general reproductive Allee-like collapse and a specific win-stay/lose-switch mechanism are not supported.
6. **Individual-level process remains unobserved.** The public mark-resight gate did not yield a colony-scale movement table, so dispersal, prospecting and public-information behavior remain hypotheses rather than demonstrated mechanisms.

This is the evidential basis for the manuscript sentence:

> **The direction of decline is regional, but the reproducible spatial signal lies in how breeders are redistributed locally: breeding-space concentration persists beyond proportional thinning, whereas static place traits, simple environmental mechanisms and individual-level behavioral explanations do not achieve the same evidential status.**

## Full 66-endpoint ledger


### A confirmatory replication

| # | Result file | Story layer | Outcome | Core claim unit | Current evidential reading |
|---:|---|---|---|---|---|
| 61 | `SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | Within-system breeding configuration | supported | replication | Prospectively frozen independent-system Adelie replication supports non-proportional concentration. |
| 62 | `SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | Within-system breeding configuration | supported | replication | Prospectively frozen cross-species chinstrap replication supports non-proportional concentration. |

### B bounded robust or exploratory

| # | Result file | Story layer | Outcome | Core claim unit | Current evidential reading |
|---:|---|---|---|---|---|
| 5 | `CONCENTRATION_DOMINANCE_DESCRIPTIVE_SUMMARY_V1.json` | Within-system breeding configuration | descriptive | none | Same concentration endpoint assembled by different dominance routes; no inferential p-values. |
| 6 | `CONTRACTION_SCALING_LAW_SYNTHESIS_V1.json` | Within-system breeding configuration | mixed | none | Bounded post-hoc scaling: smooth abundance–E relation; threshold and formal ratchet rules not supported. |
| 7 | `CONTRACTION_SCALING_RULES_EXPLORATION_SUMMARY_V1.json` | Within-system breeding configuration | mixed | none | Closed candidate-rule search rejects universal quarter-power and common collapse threshold; kappa remains descriptive. |
| 8 | `EXPLORATORY_RESULT_V1.json` | Species / phenotype | supported boundary | none | Assemblage island morphology is mainly compositional; within-Adelie fixed island phenotype is weak and cross-year transfer is approximately chance. |
| 12 | `PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` | Within-system breeding configuration | supported | discovery | Discovery: all three stable-roster Palmer islands concentrate beyond fixed-composition thinning under all frozen error models. |
| 13 | `PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json` | Mechanistic trace | superseded positive | none | N_eff gave a small positive LOYO gain and coefficient, but the predictive interpretation was later removed by year-block permutation. |
| 14 | `PALMER_EXTERNAL_SPATIAL_TRIANGULATION_RESULT_V1.json` | Within-system breeding configuration | supported boundary | none | Independent Torgersen mapping converges on spatial attrition; no colony-code crosswalk or causal validation. |
| 15 | `PALMER_HIERARCHICAL_VARIABILITY_RESULT_V1.json` | Within-system breeding configuration | supported boundary | none | Observed variability reduction is larger within islands than among islands, but later count-error audit limits robustness. |
| 16 | `PALMER_HIERARCHY_COMPONENT_COUNT_AUDIT_RESULT_V1.json` | Within-system breeding configuration | robustness | none | Post-hoc component-count normalization retains the hierarchy; diagnostic only. |
| 19 | `PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json` | Regional direction | supported context | none | Five islands share a dominant long-term decline component (PC1 about 96.4%) while annual growth synchrony is only moderate. |
| 22 | `PALMER_NEFF_CIRCULAR_COUPLING_RESULT_V1.json` | Mechanistic trace | robustness | none | Positive N_eff coefficient remains unusual under coupled circular structured nulls; not a predictive claim. |
| 23 | `PALMER_NEFF_CIRCULAR_SHIFT_RESULT_V1.json` | Mechanistic trace | robustness | none | N_eff association retained against independent and joint circular-shift nulls. |
| 24 | `PALMER_NEFF_DEMOGRAPHIC_MOMENTUM_RESULT_V1.json` | Mechanistic trace | robustness | none | Positive N_eff association persists after lagged-growth controls; no robust out-of-year prediction or causality. |
| 25 | `PALMER_NEFF_MECHANICAL_COUPLING_RESULT_V1.json` | Mechanistic trace | robustness | none | Observed coefficient is unusual under same-census mechanical-coupling nulls, while predictive gain remains failed. |
| 27 | `PALMER_NETWORK_STAGE2_RESULT_V1.json` | Regional direction | supported boundary | none | Adelie decline recurs across Palmer islands but local community endpoints differ; no uniform gentoo replacement. |
| 28 | `PALMER_PERFORMANCE_MEMORY_RESULT_V1.json` | Mechanistic trace | mixed | none | Short-term performance state persists and past performance adds information, but persistent environment and individual information use remain unresolved. |
| 29 | `PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json` | Mechanistic trace | supported nonconfirmatory | none | Bias-resistant lag-2 performance-to-redistribution association survives fixed specification, but provenance repair occurred after coefficient exposure. |
| 30 | `PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json` | Species / phenotype | supported boundary | none | Within Adelie, fixed island morphology is weak and temporal reassembly dominates; no persistent island ecotype claim. |
| 40 | `PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json` | Static place / transferable trait | descriptive only | none | All three A-by-H point estimates are negative, but this file contains point estimates only; frozen permutation inference is required. |
| 50 | `PAPER2_OBSERVATION_TIMING_SENSITIVITY_RESULT_V1.json` | Static place / transferable trait | robustness | none | Timing sensitivity does not reverse the focal interaction direction/crossover classification; no new inferential p-values. |
| 64 | `SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json` | Within-system breeding configuration | nested robustness | none | Strict Signy Adelie roster/window concentration result passes all frozen error models; not an independent extra replication beyond the Signy family. |

### C scope limiting negative

| # | Result file | Story layer | Outcome | Core claim unit | Current evidential reading |
|---:|---|---|---|---|---|
| 17 | `PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json` | Within-system breeding configuration | scope limited | none | Raw hierarchy is unusual under Poisson/CV10 but not CV20; full error-family robustness is not supported. |
| 18 | `PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json` | Mechanistic trace | not supported | none | Externally fixed >50-pair group metric fails the predicted positive direction despite held-out information. |
| 26 | `PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json` | Mechanistic trace | not supported | none | Held-out predictive gain is null-compatible; forecasting/predictive pillar is removed although coefficient remains unusual. |
| 31 | `PALMER_REPRODUCTIVE_DENOMINATOR_AUDIT_RESULT_V1.json` | Mechanistic trace | not supported | none | No Palmer-wide positive density-dependence law, no general Allee-like reproductive mechanism, and no pre-extinction breeding collapse. |
| 32 | `PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json` | Regional direction | not supported | none | Frozen annual sea-ice and sea-ice-by-habitat mechanisms do not explain island growth. |
| 33 | `PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json` | Regional direction | not supported | none | Frozen 3/5/7-year low-frequency sea-ice rescue fails; long-term decline is not explained by this simple sea-ice formulation. |
| 34 | `PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json` | Regional direction | not supported | none | Predeclared snowfall-by-snow-prone-habitat mechanism fails and worsens held-out prediction. |
| 35 | `PALMER_WIN_STAY_LOSE_SWITCH_RESULT_V1.json` | Mechanistic trace | not supported | none | Redistribution is compatible with within-island switching, but the specific win-stay/lose-switch asymmetry is not supported. |
| 36 | `PAPER2_A_BUFFERING_SECONDARY_RESULT_V1.json` | Static place / transferable trait | not supported | none | Simple area buffering is not supported in any species after frozen permutation/Holm inference. |
| 39 | `PAPER2_DETECTABLE_EFFECT_RESULT_V1.json` | Static place / transferable trait | scope limited | none | Retrospective bound: common effects around absolute 0.5 should have been detectable; absolute 0.3 need not be. No equivalence claim. |
| 52 | `PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json` | Static place / transferable trait | not supported | none | Observed radius sign-switch plus contrast has null probability 0.081; ecological scale-dependence language is not allowed. |
| 53 | `PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json` | Static place / transferable trait | scope limited | none | A-by-H interaction direction is not invariant to spatial scale or trait metric; primary result is not a transferable rule. |
| 58 | `PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json` | Static place / transferable trait | not supported | none | Frozen primary permutation test does not reject; no species Holm rejection and no process-variance claim. |
| 65 | `SIGNY_PERFORMANCE_REDISTRIBUTION_REPLICATION_RESULT_V1.json` | Mechanistic trace | not supported | none | Prospective Signy lag-2 redistribution replication and lose-switch hinge both fail; mechanism transferability is not established. |

### D data or identifiability gate

| # | Result file | Story layer | Outcome | Core claim unit | Current evidential reading |
|---:|---|---|---|---|---|
| 2 | `ANTARCTIC_BREEDING_OPTIONS_ATLAS_GATE1_RESULT_V1.json` | Static place / transferable trait | gate pass | none | Ice-free/habitat proxy coverage passed; demographic outcomes remained unopened. |
| 3 | `ANTARCTIC_BREEDING_OPTIONS_HIERARCHY_RESULT_V1.json` | Static place / transferable trait | gate pass | none | Tier-2 habitat-complex richness and mapped ice-free area chosen outcome-blind; no demographic outcome. |
| 4 | `ANTARCTIC_TERRAIN_ATLAS_GATE1D_A_RESULT_V1.json` | Static place / transferable trait | gate pass | none | Terrain relief proxy chosen outcome-blind; no demographic outcome. |
| 9 | `MAPPPD_MACRO_GEOGRAPHY_AUDIT_RESULT_V1.json` | Static place / transferable trait | gate pass | none | Broad geography exists but is unbalanced; no outcome model opened. |
| 10 | `MAPPPD_MACRO_INVENTORY_RESULT_V1.json` | Static place / transferable trait | gate pass | none | Pygoscelis macro trend lane feasible; other penguin taxa fail support; no outcome model. |
| 21 | `PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json` | Data limit | partial gate | none | No qualifying public colony-scale Palmer resight table located; individual movement remains unidentified. |
| 38 | `PAPER2_CROSS_SPECIES_GENERALITY_V4_RESULT_V1.json` | Static place / transferable trait | recoverability gate | none | Cross-species generality estimand is recoverable synthetically; real counts remain unopened at this gate. |
| 41 | `PAPER2_FORCING_SCALE_SENSITIVITY_RESULT_V1.json` | Static place / transferable trait | design gate | none | Forcing-scale sensitivity design frozen; no demographic outcomes opened. |
| 42 | `PAPER2_FORCING_SUPPORT_AUDIT_RESULT_V1.json` | Static place / transferable trait | identifiability gate | none | All species have identifiable forcing support under frozen coverage rules; no ecological effect yet. |
| 43 | `PAPER2_H_MAIN_RECOVERY_V5_RESULT_V1.json` | Static place / transferable trait | recoverability gate | none | Main H effect recoverable in simulation; real counts remain unopened. |
| 44 | `PAPER2_INTEGRATED_HIERARCHICAL_RECOVERY_RESULT_V2.json` | Static place / transferable trait | recoverability gate | none | Hierarchical core recoverable only after species-wide forcing selection; primary regional hierarchical gate fails. |
| 45 | `PAPER2_INTEGRATED_RECOVERY_RESULT_V1.json` | Data limit | failed gate | none | Integrated synthetic recovery fails pre-outcome; counts correctly remain unopened. |
| 46 | `PAPER2_INTEGRATED_SENSITIVITY_SUPPORT_RESULT_V1.json` | Static place / transferable trait | support gate | none | Exclude-unknown sensitivity is testable across species; ground-only Adelie is coverage-limited; no real outcomes. |
| 47 | `PAPER2_LATENT_FACTOR_RECOVERY_RESULT_V1.json` | Static place / transferable trait | recoverability gate | none | Latent forcing scale is recoverable by species, with gentoo regional factor rejected before outcomes; observation layer still pending. |
| 49 | `PAPER2_OBSERVATION_RECOVERY_RESULT_V1.json` | Static place / transferable trait | recoverability gate | none | Observation layer recoverable synthetically; no real demographic magnitudes opened. |
| 54 | `PAPER2_SPATIAL_ADJUSTED_V3_RESULT_V1.json` | Static place / transferable trait | recoverability gate | none | Spatially adjusted core passes synthetic recovery; real counts remain unopened at this gate. |
| 56 | `PAPER2_V2_SENSITIVITY_SUPPORT_RESULT_V1.json` | Static place / transferable trait | support gate | none | Source sensitivities are structurally testable except ground-only Adelie; no real outcomes. |
| 57 | `PAPER2_V2_SOURCE_SENSITIVITY_RECOVERY_RESULT_V1.json` | Data limit | failed gate | none | Exclude-unknown recovery fails; observation-source sensitivity gate remains incomplete and counts stay closed. |
| 59 | `PAPER2_V3_SOURCE_SENSITIVITY_RESULT_V1.json` | Data limit | failed gate | none | Full source-sensitivity recovery fails pre-outcome; counts stay closed. |
| 60 | `PAPER2_V4_SOURCE_GENERALITY_RESULT_V1.json` | Static place / transferable trait | support gate | none | Paper-level source robustness is synthetically recoverable despite Adelie exclude-unknown limitation; no real magnitudes opened. |
| 66 | `SIGNY_REPLICATION_SUPPORT_AUDIT_RESULT_V1.json` | Data limit | gate pass | none | Outcome-blind support audit says Signy replication is feasible; effect was still unopened at this stage. |

### E technical quality provenance

| # | Result file | Story layer | Outcome | Core claim unit | Current evidential reading |
|---:|---|---|---|---|---|
| 1 | `AEI_VAT_SCHEMA_AUDIT_RESULT_V1.json` | Technical / provenance | audit | none | AEI/VAT schema and hierarchy verified; no demographic outcome. |
| 11 | `MAPPPD_OBSERVATION_METHOD_AUDIT_RESULT_V1.json` | Static place / transferable trait | audit | none | Observation-method structure audited outcome-blind; no demographic inference. |
| 20 | `PALMER_MANUSCRIPT_FIGURE_PACKAGE_RESULT_V1.json` | Technical / provenance | reproducibility | none | Figure-data/package reproducibility receipt; no new ecological evidence. |
| 37 | `PAPER2_BREEDING_SEASON_AUDIT_RESULT_V1.json` | Static place / transferable trait | audit | none | Season field/window selected outcome-blind; no counts opened. |
| 48 | `PAPER2_OBSERVATION_OVERLAP_AUDIT_RESULT_V1.json` | Static place / transferable trait | audit | none | Observation method and accuracy overlap audited and primary calibration structure frozen. |
| 51 | `PAPER2_PREDICTOR_IDENTIFIABILITY_AUDIT_RESULT_V1.json` | Static place / transferable trait | audit | none | Predictor identifiability and primary crossover model structure frozen before real inference. |
| 55 | `PAPER2_TEMPORAL_OVERLAP_AUDIT_RESULT_V1.json` | Static place / transferable trait | audit | none | Common 1980-2025 trend window is structurally available; no demographic values opened. |
| 63 | `SIGNY_CONCENTRATION_QUALITY_AUDIT_V1.json` | Within-system breeding configuration | quality audit | none | Post-result quality audit retains the frozen Signy result unchanged; no outcome-dependent exclusion. |

## Anti-double-counting rules

- `PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` is the **discovery**, not confirmatory evidence.
- `SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` and `SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json` are the only two positive **class-A replication units**.
- `SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json` is nested robustness of the Signy Adélie concentration family and must not be counted as another independent replication.
- The N_eff growth files form one robustness chain. The initial LOYO gain cannot be cited without the later year-block permutation result that removed the predictive claim.
- Paper 2 synthetic recovery, observation and support gates demonstrate estimability only. They are not biological evidence about area, habitat or terrain.
- Real Paper 2 point estimates cannot be treated as inferential support because the frozen permutation endpoint did not reject.
- Technical/quality audits and manuscript figure receipts never increase ecological evidence counts.

## Mapping to the six-level story

| Story node | What survives the ledger | What does not survive |
|---|---|---|
| **1. Region — direction** | Strong common long-term Palmer decline; heterogeneous annual growth | Simple annual or smoothed sea-ice rescue; snowfall×habitat mechanism |
| **2. Static place — transferable rule** | Detectability bounds and explicit scope limits | Confirmatory area buffering; robust scale-invariant area×habitat rule |
| **3. Species / phenotype** | Assemblage island signal is largely species composition; within-Adelie phenotype reassembles through time | Persistent island ecotypes / strong cross-year morphological identity |
| **4. Within-system configuration** | Palmer discovery + prospective Signy Adélie + prospective Signy chinstrap concentration | Universal κ, common threshold, universal dominant-colony refuge |
| **5. Mechanistic traces** | Robust N_eff association; nonconfirmatory Palmer lag-2 performance signal | Robust forecasting, general Allee-like reproductive collapse, transferable lag-2 mechanism, win-stay/lose-switch |
| **6. Individual process / data limit** | Explicitly unresolved | Colony-scale movement, prospecting, public-information use |

## Manuscript rule

The headline claim must be written from **class A plus its single class-B discovery family**. Class B may explain shape and robustness; class C must appear as claim boundaries; class D explains why the next mechanistic question remains open; class E belongs in Methods/SI provenance. No manuscript sentence should convert the number of files into an apparent replication count.
