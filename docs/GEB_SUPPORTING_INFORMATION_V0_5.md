# Supporting Information — Integrated v0.5 GEB

**Manuscript:** *Dynamic colony history reveals limits of static island architecture for predicting Antarctic penguin demography*

This Supporting Information preserves implementation and inferential details compressed from the main text. It does not introduce additional paper-level claims. Machine-readable contracts, source checksums, simulation receipts and complete result objects are archived in the accompanying reproducibility repository.

## S1. Inferential-status map

| Analysis | Biological role | Status | Paper-level use |
| --- | --- | --- | --- |
| Palmer five-island common decline | demographic background | descriptive | establishes shared regional decline |
| Palmer effective-colony-number concentration | spatial reorganization | frozen simulation null | evidence that decline is not proportional thinning alone |
| Palmer lag-1 colony state | immediate association | fixed specification, mechanically coupled | reported but not mechanistically interpreted |
| Palmer lag-2 colony state | primary bias-resistant local-state endpoint | fixed-specification validation after documented provenance repair | principal Palmer information result |
| Palmer lags 3–5 | temporal profile | frozen with lag analysis | constrains duration; not separate positive discoveries |
| 4–5-year recruitment-echo contrast | delayed local recruitment hypothesis | predeclared within lag contract | unsupported |
| Palmer state-memory rho1 | persistence diagnostic | frozen mechanism diagnostic | weak one-year measured-state persistence |
| Palmer state-memory rho2, rho3 | longer persistence diagnostics | frozen mechanism diagnostic | non-confirmatory |
| Palmer bridge delta_past | history diagnostic after measured next-year state | non-causal mechanism diagnostic | mechanism diagnostic only |
| Independent REPRO mean chicks-to-crèche/nest | independent biological validation | frozen primary endpoint | non-replication; narrows state interpretation |
| REPRO binary any-crèche sensitivity | alternate nest endpoint | prespecified sensitivity | cannot rescue failed REPRO primary |
| Common-panel REPRO vs colony-state comparison | metric-alignment diagnostic | post-result diagnostic | explains metric mismatch; not independent evidence |
| HUMPOP arrival timing | adult-return process candidate | prospective gate | stopped for insufficient information; no coefficient fit |
| Antarctic 2-km area × heterogeneity | paper-level transferability hypothesis | preregistered 9,999-permutation test | directionally concordant but non-confirmatory |
| A-only breeding-space buffering | simpler static-landscape hypothesis | prespecified secondary | unsupported |
| Image/direct calibration refits | observation robustness | prespecified sensitivity | direction preserved |
| 1/2/5-km spatial support | spatial-support sensitivity | secondary + joint interpretation gate | no established biological scale dependence |
| Retrospective operating characteristic | detectability context | post-inference diagnostic | constrains interpretation of non-rejection |
| Ross Island individual settlement | future mechanism test | outcome-blind design only; real data locked | not current manuscript evidence |

## S2. Palmer census and concentration analysis

Annual Adélie breeding-pair counts came from the Palmer Station Antarctica LTER area-wide census. The synchronized island panel comprised Christine, Cormorant, Humble, Litchfield and Torgersen from 1991–2017. Island trajectories were analysed on the log(1 + N) scale.

For island-year t, the fraction of breeders in colony code j was p_j,t, and effective colony number was

\[
N_{\mathrm{eff},t}=\frac{1}{\sum_j p_{j,t}^{2}}.
\]

The inferential concentration analysis was restricted to Cormorant, Humble and Litchfield because their reported colony-code rosters were unchanged through the synchronized period. The observed statistic for each island was the OLS slope of N_eff against centred calendar year.

The fixed-composition null retained the observed annual island total but removed temporal change in the latent colony composition. Expected colony counts were generated from one time-invariant composition estimated from cumulative counts. We then applied three prespecified observation/count models: Poisson sampling and Gamma–Poisson sampling with 10% and 20% multiplicative CV. Each null used 100,000 realizations. Island-specific one-sided probabilities measured the fraction of simulated slopes at least as negative as observed; the joint statistic required all three slopes to be simultaneously at least as negative as their observed values.

The null therefore asks whether the observed concentration can be explained by decline plus fixed composition and independent count error. It does not test a specific behavioural mechanism and does not imply that colony codes are one-to-one mapped nesting polygons.

## S3. Late-season colony-state construction and lag model

Adult breeding-pair counts and chick counts were joined using island, raw colony code and breeding season. Chick season was assigned from the PALYYZZ study identifier under an earlier outcome-blind season-key contract. Within each eligible island-season,

\[
E_{i,t}=C_t\frac{N_{i,t}}{N_t},
\]

where C_t is the island total chick count, N_i,t the focal colony breeding-pair count and N_t the island total breeding-pair count. We computed

\[
Q_{i,t}=
\frac{C_{i,t}-E_{i,t}}
{\sqrt{\max[E_{i,t}(1-N_{i,t}/N_t),10^{-12}]}}
\]

and standardized Q_i,t within island-season to obtain S_i,t.

For adjacent adult censuses,

\[
G_{i,u}=\log(1+N_{i,u+1})-\log(1+N_{i,u}),
\]

and relative growth R_i,u was obtained by subtracting the mean G among eligible colonies in the same island-transition. Prior size was z[log(1 + N_i,u)] within that transition.

Each lag was fit separately as

\[
R_{i,u}=\beta_k S_{i,t}+\gamma z\log(1+N_{i,u})
+\alpha_{\mathrm{island:colony}}+\epsilon,
\]

where u = t + k − 1. Inference permuted S_i,t among eligible colonies within each predictor island-season while holding the outcome, missingness and controls fixed. The primary p-value was the one-sided upper-tail Monte Carlo probability with +1 correction over 100,000 draws.

Lag 1 is mechanically coupled because S_i,t and the t → t+1 growth interval both contain N_i,t. The lag-2 endpoint instead relates S_i,t to growth from t+1 → t+2, so the predictor construction does not share the adult count used as the growth denominator.

### S3.1 Provenance repair

The first lag implementation used calendar date to assign chick season. An earlier outcome-blind contract had already established PALYYZZ as canonical because the archive contains date inconsistencies. Once the conflict was discovered, only the season key was repaired; the state metric, lags, controls, permutation scheme, sensitivities and decision thresholds remained unchanged. Observed lag coefficients had been seen before the repair. Consequently, the repaired result is labelled **fixed-specification validation after provenance repair**, not fully outcome-blind preregistration.

### S3.2 Lag-profile diagnostic

The predeclared delayed-recruitment contrast was

\[
C_{\mathrm{recruit}}
=\frac{\beta_4+\beta_5}{2}
-\frac{\beta_2+\beta_3}{2}.
\]

The directional prediction was C_recruit > 0, motivated by a possible 4–5-year local cohort/recruitment echo. This contrast was explicitly not treated as a unique signature of public-information use.

## S4. State persistence, bridge diagnostic and REPRO validation

Measured state persistence was estimated for h = 1, 2, 3:

\[
S_{i,t+h}=\rho_hS_{i,t}+\alpha_i+\epsilon.
\]

Predictor state was permuted within the predictor island-season under the frozen eligible-colony null. The bridge diagnostic for the lag-2 redistribution interval included S_i,t, measured S_i,t+1, prior size and colony fixed effects. Because S_i,t+1 is post-t, delta_past is not interpreted as causal mediation.

For the independent REPRO validation, a monitored nest received 0–2 successful crèche events according to the number of positive chick crèche dates. Historical files encode non-events as numeric zero; later files use blank nullable values. Before fitting any REPRO performance-growth coefficient we froze the semantic rule that only positive numeric crèche dates count as success. The colony-season endpoint was mean chicks reaching crèche per monitored nest, requiring at least five monitored nests.

The primary REPRO model used next-year relative redistribution, standardized prior colony size and colony fixed effects, with 100,000 within-island-season permutations. A binary indicator of whether a nest produced at least one chick reaching crèche was prespecified as sensitivity-only. Because the mean-chicks endpoint failed its frozen primary test, the binary sensitivity cannot be promoted to a replacement primary result.

The common-panel comparison between REPRO and the colony-wide chick state was defined only after the REPRO result. It is therefore labelled post-result diagnostic and is used to assess metric alignment, not to add confirmatory evidence.

## S5. HUMPOP arrival gate

The Palmer breeding-adult arrival archive (HUMPOP) passed an outcome-blind schema gate: official PAL-LTER transformation code showed that the raw LOC field is retained as colony and repeated dates with adult counts are available. The frozen primary endpoint was the date at which a colony-season first crossed 50% of its observed seasonal maximum. The design required at least 100 matched colony-seasons. Only 69 remained after the frozen eligibility rules, so the analysis stopped before fitting an arrival coefficient or computing a p-value. The result is therefore **non-estimable under the prespecified gate**, not a null arrival effect.

## S6. Antarctic-wide analysis frame and observation model

The Antarctic-wide analysis used a fixed MAPPPD/APBP snapshot. An outcome-blind inventory identified 152 candidate Pygoscelis site × species units. A common 1980–2025 time window and frozen temporal-coverage criteria produced 107 bridged units and 2,100 nest-count records. Joining the predeclared site predictors yielded 104 complete units: 41 Adélie, 34 chinstrap and 29 gentoo.

Primary 2-km site predictors were

\[
A=z[\log(1+\mathrm{ice\text{-}free\ area})]
\]

and

\[
H=z(\mathrm{Tier\ 2\ Habitat\ Complex\ richness}),
\]

with focal interaction A × H. Predictor construction and collinearity decisions were frozen before demographic outcome magnitudes were opened.

Direct counts were the observation reference. Image counts received one shared offset estimated from repeated direct/image comparisons, and observation precision was represented by frozen accuracy groups. Candidate forcing partitions and estimators had to recover null, simple-buffering and interaction scenarios under the real observation schedule before outcome values were opened. Failed candidate estimators were retained in the audit history rather than retuned after outcomes.

The retained site-loading model was

\[
\lambda_i=
1+\alpha_{b(i)}
+\gamma_AA_i
+\gamma_HH_i
+\gamma_{AH}A_iH_i+b_i,
\]

where alpha_b(i) is the frozen spatial-block adjustment and b_i a residual site loading. Adélie used CCAMLR blocks; chinstrap and gentoo used APBP regions. Site traits were centred within block. The process model used log(1 + N) and propagated endpoint observation variance into interval likelihoods.

## S7. Antarctic-wide primary permutation test

The paper-level estimand was the median gamma_AH across the three species. The one-sided alternative was more negative. Within each species and spatial block, complete (A, H, A × H) tuples were permuted among site time series; singleton blocks remained fixed. The complete V3 model was re-estimated for each of 9,999 permutations. The paper-level p-value used +1 correction. Species-specific interaction tests used the same directional rule and Holm correction across species.

A full point-estimate option–fragmentation crossover required gamma_AH < 0, a non-negative heterogeneity slope at A = −1 SD and a negative heterogeneity slope at A = +1 SD. Crossover classifications are descriptive geometry unless supported by the frozen inferential test.

## S8. Secondary Antarctic-wide analyses

### S8.1 Simple breeding-space buffering

A-only models used the same observation/process framework. Species-specific one-sided permutation p-values were Holm-adjusted. This hypothesis was frozen as secondary and cannot replace the primary area × heterogeneity test.

### S8.2 Observation calibration

The primary image/direct offset used the frozen calibration scheme. Robustness refits re-estimated the offset using exact-date direct/image pairs and pairs within 14 days, then refit the unchanged demographic model.

### S8.3 Spatial support

Area and habitat richness were rebuilt at 1 km and 5 km; 2 km Shannon diversity was an additional sensitivity. None could replace the 2-km richness primary analysis. After the raw estimates changed sign across radius, a joint interpretation diagnostic permuted the entire 1/2/5-km trait tuple within species × block to preserve cross-radius covariance. The prespecified interpretation event required both the observed 2-km negative/5-km positive sign switch and a contrast at least as large as observed. Biological scale-dependence language required p ≤ 0.05.

### S8.4 Detectability

Retrospective simulations used the unchanged real observation layout, estimator and realized 9,999-permutation rejection threshold. Common interaction magnitudes from −0.20 to −0.60 were evaluated to estimate empirical detection probability and interpolated 80% and 90% minimum detectable effects. This exercise contextualizes non-rejection; it is neither an equivalence test nor a confidence interval.

## S9. Claim boundaries carried into the GEB main text

1. The Palmer lag-2 result is not described as fully preregistered.
2. The positive lag-1 association is not the novelty and is not mechanistically interpreted.
3. The independent REPRO failure is reported as a primary biological constraint.
4. HUMPOP is reported as stopped, not as a negative effect.
5. Static habitat remains biologically relevant; state does not replace place.
6. The Antarctic-wide result remains non-confirmatory at the frozen primary scale.
7. Radius variation remains sensitivity rather than established scale dependence.
8. Parts I and II are not compared by effect size, explained variance or predictive superiority.
9. Published public-information and Ross Island movement studies are precedent/motivation, not discoveries of this manuscript.
10. No unpublished Ross individual-level behavioral result enters the evidentiary chain.

## S10. Reproducibility objects

The repository contains machine-readable contracts and receipts for all primary tests, repairs, stopped analyses and post-result diagnostics. Key objects include:

- PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_V2
- PALMER_PERFORMANCE_MEMORY_V1
- PALMER_REPRO_REDISTRIBUTION_V1
- PALMER_REPRO_SAME_PANEL_METRIC_DIAGNOSTIC_V1
- PALMER_HUMPOP_ARRIVAL_SCHEMA_GATE_V1
- PAPER2_OUTCOME_BLIND_PREDICTOR_SET_V1
- PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1
- INTEGRATED_PALMER_ANTARCTIC_MANUSCRIPT_V0_4
- INTEGRATED_V0_5_GEB_SUBMISSION_V1

These objects preserve source commits/checksums, exact decision rules and validation history beyond the concise journal-facing description.
