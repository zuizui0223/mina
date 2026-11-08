# Frozen analysis design v1 — Antarctic penguin climatic legacy (10–20 years)

**Frozen:** 2026-11-08 JST. **Repository lane:** mina, derived from PR #206 branch only. **Status:** outcome-aware hypothesis generation has already occurred; this is a prospective freeze for the *specific untested 11–20-year versus 1–10-year contrast*, NOT independent preregistration of the overall penguin/climate programme. No new 1979–1990 site-specific SIC exposure or lag model scores were examined when writing this document.

## Ecological question and falsifiable hypotheses

**Question:** Does historical Antarctic sea ice carry additional out-of-time information about Adélie penguin breeding-count change after accounting for more recent sea ice, site history, and time trend?

- **H1 (primary, predictive):** For the same eligible annual transitions and equal-length exposure windows, sea ice from 11–20 years before the count-transition start predicts next-season log nest-count change better out of time than sea ice from 1–10 years before that start.
- **H2 (secondary, unique history):** Adding the 11–20-year window to the recent-window model improves out-of-time prediction. This is a stricter test against mere geographic sorting or high climate autocorrelation.
- **Alternative (biologically motivated):** 3–7-year antecedent conditions are sufficient, consistent with recruitment delays already reported in Adélie penguins; an apparent decade-scale relationship may instead reflect shared time trends, site fidelity, prey/food-web persistence, or sampling.

These are hypotheses about *predictive climatic legacy*, **not direct tests of penguin movement, philopatry, colonization, mortality, or climate debt**. A failure of annual current-SIC forecasts does not imply a long-lag effect; a retrospective long-lag association does not establish its causal mechanism.

## Source cohort and outcome — fixed before lag testing

- Source: research/climate-penguin/outputs/long_count_seaice_v1/intervals.csv, Git blob **6d5982d6f241879de9a2da0232f0f05ec227d3a7** on codex/climate-penguin-progress.
- Select ADPE, gap = 1, positive_positive, same_known_method = True, use recorded site_id, region, start, end, n_start, n_end and log_growth unchanged.
- Fixed primary response is y(i,t) = log(n_end/n_start), for consecutive census-year transition t -> t+1. No log1p substitution, per-site long-term slope substitution, smoothing of the response, or imputation of a missing zero.
- Original supported cohort: **301 annual transitions, 33 site IDs, 6 regions, start years 1991–2018**. The separate **39-site** long-term trend summary is not 39 independent annual response series: 25 have positive and 14 negative fitted slopes. Do not mix breeding-unit patch counts with macro MAPPPD site counts.
- Counts at sites with observed zero and inter-site colonization cannot be addressed by this positive-to-positive subset; site-count changes cannot distinguish death, missed breeding, recruitment, or emigration.

## Predictor timing and source extension

Let SIC(i,y) be August–November 0–100-km nearshore monthly sea-ice concentration at the original matched site geography, using a single consistently processed satellite product and fixed extraction definition.

- **Recent R(i,t):** mean SIC(i,y) for y = t−10, ..., t−1 (10 complete antecedent years).
- **Legacy L(i,t):** mean SIC(i,y) for y = t−20, ..., t−11 (the preceding, non-overlapping 10 years).
- Both means have exactly 10 annual values, with the same four fixed months and identical weights. No outcome-year or future-year SIC enters either predictor. No search across seasons, distance buffers, 5/10/15/20-year peaks, or sea-ice thresholds.
- **Secondary recruitment window:** 5-year mean for y = t−7, ..., t−3. Distinct window duration and overlapping support are clearly labelled secondary; it is not a replacement for the equal-width primary contrast.
- Existing source-matched satellite extraction covers **1991–2020**; for primary legacy support starting 1999, reconstruct **1979–2020** using one product version and harmonized ocean masks, e.g. documented NSIDC-0051 passive-microwave sea-ice concentration. Do NOT splice different product algorithms without cross-calibration. Archive version, grid, land/ocean mask, site geolocations, month weights, and source hash before analysis.
- In early SMMR years the nominal sensor acquisition cadence differs from later daily SSM/I series. Check coverage against *expected sensor acquisitions*, not calendar-day completeness, and apply a single predefined monthly ≥80% acquisition-coverage and marine-pixel ≥80% validity rule. Require all four months and all 10 years for each window. Never fill missing sea ice as zero; record exclusions before fitting.
- Run a source-only comparability audit against existing 1991–2020 series at all site-years; report differences, sensor-transition discontinuities, nearshore mask failures, and duplicate/shared climate pixels. If nearshore comparability fails, do not proceed to an interpretable biological lag test; offshore 100–500 km can be a separately labelled sensitivity, not a rescue primary.

## Feasibility/support gate (computed from existing count years only; NOT lag results)

| Support | Count-only upper bound before 1979–1990 SIC acquisition |
| --- | ---: |
| Original ADPE same-method positive annual changes | 301 transitions / 33 sites / 6 regions |
| 11–20-year window using only currently archived 1991–2020 SIC | 76 transitions / 20 sites / 4 regions (t≥2011) |
| 11–20-year window after one-source 1979 extension | 208 transitions / 32 sites / 6 regions (t≥1999) |
| Initial train starts 1999–2005 | 87 transitions / 22 sites / 6 regions |
| Rolling-year test 2006–2018, site observed in an earlier training year | 111 predictions / 17 sites / 4 regions / 13 years |
| Same rolling-year potential predictions with both count months known after September | 83 predictions |
| Fixed initial-site-only (1999–2005) test subset 2006–2018 | 106 predictions / 13 sites / 4 regions / 13 years |

Data gate before biological lag scoring: require at least 150 complete eligible annual transitions; ≥20 usable sites in ≥4 regions; ≥80 rolling-origin test predictions across ≥10 sites, ≥3 regions and ≥10 distinct test years; and a documented primary source consistency check. These are feasibility thresholds, not ecological significance cutoffs. If they fail, report NOT TESTABLE rather than modifying windows after outcomes are seen.

## Locked models and chronological evaluation

Use the same eligible count transitions for every model at each test origin. For test year t ∈ 2006..2018, fit on **eligible transitions with start < t only**, predict only sites observed in that training set, and record all dropped/unseen sites. Recompute all standardization and site means from training years only; do not use held-out responses for tuning. Keep existing fixed ridge penalties: site = 3, linear time trend = 3, climate = 8. All climate models have the same site and time backbone. No penalty optimization on test outcomes.

- **M0:** zero change yhat = 0 (unchanged nest count).
- **Mbase:** site intercept + linear calendar trend, ridge penalties fixed above.
- **Mrecent:** Mbase + train-standardized R(i,t), represented as within-site anomaly relative to its training-site mean.
- **Mlegacy:** Mbase + train-standardized L(i,t), represented identically, same number of parameters as Mrecent.
- **Mboth:** Mbase + R and L; report incremental predictive gain over Mrecent only. Do not interpret partial coefficients causally when collinear.
- **Mrecruit (secondary):** Mbase + the prespecified t−7..t−3 recruitment SIC window.

**Primary score:** paired difference Δ = MAE(Mrecent) − MAE(Mlegacy) on same out-of-time predictions (Δ > 0 favors long legacy). Also report MAE against M0 and Mbase, and the Mrecent-to-Mboth change. Present (a) pooled transition-weighted MAE, (b) year-equal MAE over 13 test years, (c) site-equal MAE over held-out sites; also region-specific and Victoria-Land-omitted diagnostics. The terminal 2014–2018 subset is a predeclared robustness readout of the same rolling predictions, *not an independent holdout*. No dependence-blind n=111 inferential p-value.

**Dependence/identifiability:** report correlations of R and L before and after removing training-fit site and linear-year terms. If absolute residualized correlation exceeds 0.95, label distinct lag coefficients non-identifiable even if scoring proceeds. Repeat the comparison on all after-September timing-confirmed transitions, and by broad region. Two-way site/year block resampling of paired prediction differences (2,000 draws, fixed seed 20261108) is sensitivity only; with four test regions and shared sea-ice grids, the uncertainty intervals are approximate and should not be described as independent environmental replication.

## Decision rule — do not reinterpret after opening long-lag scores

- **Legacy prediction supported (bounded claim)** only if Mlegacy beats Mrecent, Mbase and M0 on both year-equal and site-equal holdout MAE, the pooled comparison has the same sign, the improvement does not reverse on removing Victoria Land, and the two-way resampled Δ interval excludes zero on the positive side. Report effect size and dependence limitations; no claims of dispersal mechanism.
- **Weak signal / inconclusive** if Mlegacy only beats Mrecent but not M0, if signs differ across aggregations, if effect relies on one region, or if R/L are not distinguishable. Do not reframe failure of recent SIC as proof of legacy.
- **Legacy prediction not supported** if Mlegacy fails to outperform recent SIC and conservative baselines with adequate support. This does not mean sea ice has no delayed demographic effect.
- **Not testable** if product harmonization or support gate fails. No rescue by tuning lag 8/12/15/25 years, selecting only declining sites, changing months, or switching outcome to 39 whole-period slopes.

## Relation to current unified manuscript and prior literature

- The validated 5-year count-forecast v3 in Draft PR #206 did not outperform the zero-change benchmark; the present long-lag hypothesis is a separate post-hoc motivated, before-new-test frozen design.
- Prior exploratory 1- and 3-year antecedent-SIC annual tests also did not exceed the unchanged-count benchmark (antecedent_ice_forward_gate_v3/REPORT_JA.md). Do not count those failed tests as positive evidence for a 10–20-year delay.
- Devictor et al. (2012), Nature Climate Change, described climate debt by comparing climate and community thermal response trajectories. Here, no equilibrium breeding distribution and no inter-colony movement flow have been estimated, so **"climatic legacy"** is defensible if predictions replicate; **"climate debt"** requires further evidence.
- Ross Sea banding work has documented increased Adélie breeding dispersal under severe local environmental perturbation (e.g. DOI 10.1073/pnas.1000623107 / mark-recapture study); colony count change is NOT proof penguins are immobile.
- Published East Antarctic Adélie work already links population trends to about five-year-lagged physical change; distinguish multi-decadal memory from known recruitment timing effects rather than claiming all demographic lag is novel.

## Required outputs only when data gate passes

1. Unmodified source identification manifest with 1979–2020 SIC checksum, site/grid ID and full annual coverage table.
2. Outcome-blind cohort support/collinearity report and strict-model specification.
3. Predicted 2006–2018 site×year log-growth table for every model, full predeclared error table, paired uncertainty, region and timing sensitivity.
4. Plain-language outcome classification: supported / weak / unsupported / not testable; never turn a descriptive climate association into a 2050/2100 breeding count forecast.

**Protected scope:** Do not modify main, frozen Paper 1/Paper 2, or add BTO. This is a separate proposal branch targeting the current climate-penguin draft lane.
