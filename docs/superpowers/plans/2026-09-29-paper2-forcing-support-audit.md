# Paper 2 Gate 2C Forcing-Support Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine, without opening demographic count magnitudes, the finest geographic scale at which each Pygoscelis species can support an identifiable shared demographic forcing factor.

**Architecture:** Add one outcome-blind audit script with pure support/selection helpers, synthetic unit tests, a frozen JSON contract, and a GitHub Actions workflow against the pinned mapppdr commit. The audit reconstructs the already-frozen 107 breeding-season units, evaluates APBP-region, CCAMLR, and species-wide support in that order, and chooses the first level that covers every retained unit with a qualifying forcing group.

**Tech Stack:** Python 3.12, pandas, pyreadr, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-paper2-environmental-coupling-design.md`

## Global Constraints

- MAPPPD source remains pinned to `88c73a507e0921b2541c218c71eaf16721bc6502`.
- Primary time field remains `season`.
- Primary window remains 1980–2025.
- Frozen bridged cohort must reproduce exactly 107 site x species units.
- No count magnitude may be summarized, compared, transformed, modeled, or written to an output.
- Grouping hierarchy is APBP region x species -> CCAMLR x species -> species-wide.
- A forcing group qualifies only with >=5 units, >=15 seasons with observations from >=3 units, >=10 seasons with temporal coverage from >=50% of units, and >=3 units spanning both first and last thirds of 1980–2025.
- A geographic level is selectable for a species only when every bridged unit of that species belongs to a qualifying group at that level. Otherwise fall back one level. This conservative completion rule prevents outcome-blind deletion of sparse geographic groups.
- Do not change the 107-unit cohort to rescue a finer forcing scale.

## Review Focus

- Missing APBP or CCAMLR labels must make that level fail for affected units rather than silently invent a group.
- A group with 4 units must fail even if temporal overlap is otherwise excellent.
- The >=50% temporal-coverage threshold must use `ceil(0.5 * n_units)`, including odd group sizes.
- Temporal coverage is inclusive from each unit's first through last observed season; it does not imply an observed count in intermediate seasons.
- Species-wide fallback must still fail closed if the species itself does not satisfy all four support criteria.

---

### Task 1: Pure support and selection logic

**Files:**
- Create: `scripts/audit_paper2_forcing_support.py`
- Create: `tests/test_paper2_forcing_support.py`

**Interfaces:**
- Produces: `evaluate_group(unit_seasons: dict[str, list[int]], start: int, end: int) -> dict`
- Produces: `select_level(level_summaries: dict[str, dict], unit_ids: set[str]) -> str | None`

- [ ] **Step 1: Write failing synthetic tests**

Tests pin:
- 5 well-overlapped units qualify;
- 4 units fail;
- odd-size 50% coverage uses ceiling;
- missing geography prevents complete level coverage;
- selection chooses APBP first, then CCAMLR, then species-wide;
- species-wide can fail closed.

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m unittest tests.test_paper2_forcing_support -v`  
Expected: FAIL because audit module/functions do not yet exist.

- [ ] **Step 3: Implement pure helpers**

Implement the exact signatures above plus small internal helpers for first/last thirds and level completeness.

- [ ] **Step 4: Run tests**

Run: `python -m unittest tests.test_paper2_forcing_support -v`  
Expected: all tests PASS.

### Task 2: Outcome-blind Gate 2C audit

**Files:**
- Modify: `scripts/audit_paper2_forcing_support.py`
- Create: `contracts/PAPER2_FORCING_SUPPORT_AUDIT_V1.json`
- Create: `.github/workflows/paper2-forcing-support-audit.yml`

**Interfaces:**
- Consumes: Task 1 helpers.
- Produces: `build_frozen_cohort(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]`
- Produces: `audit(root: Path) -> dict`
- Produces result artifact: `PAPER2_FORCING_SUPPORT_AUDIT_RESULT_V1.json`
- Produces unit artifact: `PAPER2_FORCING_SUPPORT_UNITS_V1.csv`

- [ ] **Step 1: Add failing cohort/audit tests using synthetic frames**

Pin that:
- Gate 0 and 107-unit drift checks fail closed;
- audit outputs contain no `count` field or count magnitude;
- APBP/CCAMLR missing labels are represented explicitly and cannot qualify;
- selected level is deterministic from support metadata only.

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m unittest tests.test_paper2_forcing_support -v`  
Expected: FAIL on unimplemented cohort/audit paths.

- [ ] **Step 3: Implement Gate 2C audit**

Reconstruct the frozen cohort using only count non-missingness as record eligibility, then discard count before all summaries. Join `sites.rda` for region and CCAMLR labels. Report every candidate group's four support statistics and species-level selected fallback.

- [ ] **Step 4: Add frozen contract and workflow**

Workflow installs only pandas/pyreadr, checks out the pinned mapppdr commit, runs the unit tests first, then the audit, then uploads JSON/CSV artifacts.

- [ ] **Step 5: Run branch CI**

Expected: unit tests and audit workflow PASS.

### Task 3: Freeze and interpret the receipt

**Files:**
- Create: `results/PAPER2_FORCING_SUPPORT_AUDIT_RESULT_V1.json`
- Modify: `docs/superpowers/specs/2026-09-29-paper2-environmental-coupling-design.md` only if Gate 2C forces a narrower, outcome-blind interpretation of the predeclared hierarchy.

**Interfaces:**
- Consumes: successful workflow artifact from Task 2.
- Produces: frozen species-specific forcing scale choices used by the later demographic-response contract.

- [ ] **Step 1: Download and inspect workflow artifact**

Verify pinned commit, 107-unit cohort, no count magnitudes, and deterministic selected scale per species.

- [ ] **Step 2: Freeze result receipt**

Commit the workflow-produced JSON verbatim except for an execution provenance wrapper if needed.

- [ ] **Step 3: Re-run CI on frozen receipt**

Expected: all relevant workflows PASS.

- [ ] **Step 4: Report ecological consequence**

State which species can support APBP-region, CCAMLR, or only species-wide shared forcing, and whether the hypothesized island-filter test remains identifiable before any abundance outcome is opened.
