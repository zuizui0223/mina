# Signy component scenarios implementation plan

> For agentic workers: use `superpowers:executing-plans` for the primary implementation and independent subagents for source reconstruction and final numerical review.

**Goal:** Connect the existing Signy meal-component association to the pinned future mean sea-ice conditions.

**Architecture:** Read the pinned inputs, reconstruct climate conditions, fit three separate seasonal response functions, and export model-specific conditional contrasts. Independent scripts own only the `independent/` subdirectories.

**Tech stack:** Existing Python environment; numpy, pandas, scipy, statsmodels, matplotlib.

**Spec:** [DESIGN.md](DESIGN.md).

## Constraints and decisions

Use the same 9 seasons, 73 stomachs, three climate models and 12 conditions. Never multiply fitted p and c to construct fitted m, use stomach counts as climate replicates, clip unsupported outcomes, or treat model spread as a probability interval. The user has explicitly opted for autonomous continuation; keep the existing draft branch and its authorized publication workflow. The clean checkout and exclusive file ownership provide isolation for this extension.

## Tasks and checks

- [x] **1. Climate and response calculations.** Created `analyze.py` and `tests/test_signy_component_scenarios_v1.py`. Interfaces: `annual_ice(frame, years)`, `support_info(values, limits)`, `fit_response(x, y)`, `fit_components(frame)`, `change_interval(slope_interval, delta_sic)`, and `predict_response(fit, reference_sic, target_sic, limits)`. Observed RED then GREEN for eight cases covering equal month weights, missing/duplicate months, wrong units, support of means versus years, signed intervals, unsupported responses, and separate m prediction.
- [x] **2. Full calculations and independent checks.** Ran `analyze.py`: 12 climate conditions, 36 response rows, 33 finite future response rows. Independently reconstructed monthly climate inputs and OLS/HC3/fractional-logit outcomes; compared with floating-point tolerances, never rounded display text.
- [x] **3. Figure and interpretation.** Created `plot.py`, `REPORT_JA.md`, `README.md` and updated the existing manuscript, supplement and two evidence ledgers. Checked source labels, scenario support, p/c/m distinction and visual layout. An independent reviewer found no material issue in the new analysis and scientific claims.
- [x] **4. Verify and prepare delivery.** Ran the eight new tests, `work/diet_niche_manuscript_v1/verify_assets.py`, and the full repository suite. Recorded the known baseline failures without changing unrelated frozen inputs. The final verification record accompanies this plan. Publication follows the prepared work: commit once, update PR206 with an expected-head lease, then verify identical remote/local trees.

## Progress ledger

- Base: `fcf369b6aaf1e3824e1ae48e6009e6c3b591e7a5`.
- Design reviewed independently before new future diet outcomes were computed; no blocking methodological issue.
- Pre-flight: climate output supplies target SIC and support to the three response fits; all use percentage-point SIC and equal-season weights.
- Calculation checks: 335 climate rows matched; 300 annual diet-support flags and 300 physical-range flags matched. All 33 supported response rows and the three withheld response rows matched the independent implementation.
- Figure and scientific review: four panels, units, reference lines, support labels, missing outcomes and caveats inspected; no material findings. The full manuscript retains the previous three-species result, Palmer transfer limits and original reference list.
- Tests: 8 added tests passed; final repository suite 642 passed, 39 skipped, 3 known baseline failures. An initial 7 additional failures were caused by the missing local `pyshp` package; installing version 3.1.6 resolved all seven without repository changes.
- Manuscript assets: 11 original source hashes, 9 years, 772 stomachs, 12 climate conditions, 64 local links and 9 references verified. New component-scenario artifacts are covered separately in `VALIDATION.json`.
- Publication state: the lease and remote-tree check are performed after this record is committed; this file does not claim an already completed remote update.
