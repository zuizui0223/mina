# Paper 2 Latent-Factor Schedule Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax.

**Goal:** Test, before opening real demographic count magnitudes, whether the frozen 1980-2025 observation schedules can recover an unknown shared demographic forcing, site loadings, and the predeclared A x H loading effect.

**Architecture:** Use only the frozen bridged-unit season schedules and frozen A/H site predictors. Generate annual latent log-abundance states from the Paper 2 process, observe those latent states only at the real recorded seasons, and fit shared forcing plus site loadings by deterministic alternating weighted least squares on inter-observation intervals. This Gate deliberately excludes the count observation layer; that becomes Gate 2E-B.

**Tech Stack:** Python 3.12, numpy, pandas, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-paper2-environmental-coupling-design.md`

## Global Constraints

- No real penguin count magnitude may be read, summarized, transformed, or modeled.
- Primary window remains 1980-2025 and primary time field remains breeding season.
- A and H use the corrected frozen 2 km breeding-option artifact; zero AEI-cell sites remain missing.
- Regional candidate forcing scales inherit Gate 2C: ADPE=CCAMLR, CHPE=APBP region, GEPE=APBP region.
- Species-wide forcing is the only allowed fallback.
- Primary crossover regression is group + A + H + A:H; relief is not used in this recovery gate.
- Simulation parameters are fixed before real outcomes: forcing SD=0.08, loading residual SD=0.15, process SD=0.04, site drift mean=-0.01, site drift SD=0.01.
- Recovery scenarios are gamma_AH=0 and gamma_AH=-0.35, with gamma_A=gamma_H=0 for this factor-specific diagnostic.
- 100 deterministic-seed replicates per species, scale and scenario.
- Fit uses exactly 8 alternating least-squares iterations; no post-result tuning.

## Recovery Gates

A candidate forcing scale passes for a species only if all are true:

- every forcing group has median true-vs-estimated forcing correlation >=0.70;
- every forcing group has 5th-percentile forcing correlation >=0.30;
- under gamma_AH=-0.35, absolute median bias <=0.10;
- under gamma_AH=-0.35, at least 90% of replicates recover a negative gamma_AH;
- under gamma_AH=0, absolute median estimate <=0.05;
- under gamma_AH=0, the empirical 5th-95th percentile interval contains zero.

Selection: test the frozen regional scale first; if it fails, test species-wide. If species-wide fails, do not open a shared-forcing loading model for that species.

---

### Task 1: Recovery primitives

**Files:**
- Create: `scripts/simulate_paper2_latent_factor_recovery.py`
- Create: `tests/test_paper2_latent_factor_recovery.py`

**Interfaces:**
- `simulate_latent_schedule(frame, gamma_ah, seed, ...) -> dict`
- `fit_unknown_factor(frame, intervals, iterations=8) -> dict`
- `summarize_replicates(records, truth) -> dict`

- [ ] Write tests for exact noiseless recovery, group-loading normalization, deterministic output, and null summary.
- [ ] Run tests and verify RED because the module does not exist.
- [ ] Implement minimal recovery primitives.
- [ ] Run tests and verify GREEN.

### Task 2: Frozen input frames and scale selection

**Files:**
- Modify: `scripts/simulate_paper2_latent_factor_recovery.py`
- Create: `contracts/PAPER2_LATENT_FACTOR_RECOVERY_V1.json`
- Create: `.github/workflows/paper2-latent-factor-recovery.yml`

**Interfaces:**
- `build_scale_frame(forcing_result, forcing_units, breeding_options, species, scale) -> DataFrame`
- `evaluate_scale(frame, replicates, seed_offset) -> dict`
- `select_recovered_scale(regional_result, specieswide_result) -> str | None`

- [ ] Add tests for corrected missingness, regional grouping, species-wide fallback, and fail-closed selection.
- [ ] Run RED.
- [ ] Implement input-frame and scale-selection logic.
- [ ] Add workflow downloading frozen forcing and corrected breeding-option artifacts.
- [ ] Run workflow.

### Task 3: Freeze recovery receipt

**Files:**
- Create: `results/PAPER2_LATENT_FACTOR_RECOVERY_RESULT_V1.json`
- Modify: `docs/superpowers/specs/2026-09-29-paper2-environmental-coupling-design.md`

- [ ] Freeze the successful workflow artifact with execution provenance.
- [ ] Record species-specific recovered forcing scale.
- [ ] Explicitly state that Gate 2E-A does not validate observation-method/count-likelihood recovery.
- [ ] Run full CI before merging.
