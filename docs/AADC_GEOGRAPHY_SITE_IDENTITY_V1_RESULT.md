# AADC geographic-site identity and expansion — independent original-source result (2026-10-25)

## What was actually executed

A new geography-only program independently downloaded the original AADC 2021 4,884-site spatial reference workbook and the original 2025 7,785-site geographic-reference workbook. Source bytes, SHA256 values and expected original sheet names/record counts were verified. **No animal occurrence, species, population count or survey outcome workbook was downloaded.**

- Original publisher geographic site IDs: **4,884 (2021)** versus **7,785 (2025)**.
- Shared exact original identifiers: **4,862**. All **4,862/4,862** shared IDs had identical numerical original latitude and longitude.
- New-to-2025 original geographic-site IDs: **2,923**.
- IDs present in 2021 but absent in 2025: **22**.
- All 7,785 2025 geography rows have valid Antarctic coordinates; **7,785 unique exact coordinate pairs**, with **zero shared identical coordinate pairs** among different 2025 site IDs.
- 2025 source-defined geographic-site feature classes: **4,478 'island', 3,307 'continent'**. These are **author classes**, NOT 4,478 independent SCAR land polygons or 4,478 penguin populations.

## New substantive geographic inference

The original *geographic survey sampling frame* is both expanded and coordinate-stable for the 4,862 identifiers carried between publisher editions. This supports a reproducible prospectively defined **site-history crosswalk** for macroecological comparison instead of manual matching of colony names. The additional 2,923 reference-site IDs are **geography coverage changes**, not proven biological colonizations; likewise 22 non-retained identifiers are not local extinctions.

## Critical inferential limits

Original coordinate identity across 2021/2025 **does not verify field GPS or breeding-site placement**. Spatial model availability is further restricted by actual searched species, original observation effort, P/A/NR distinctions and valid local habitat-source crosswalks. The prior AADC V14 biological model used **368** strictly eligible geographic sites across eight spatial blocks (not all 7,785), and did not establish an island-area/nesting-guild effect. Therefore this new 7,785-site inventory is **not** a claim to 7,785 independent biological observations or a clean prospective reset of already inspected V14 data.

The next authorized geography stage is an **outcome-blind** crosswalk from the 7,785 coordinate-only reference sites to independent SCAR land/rock polygons. Allow separate records for exact containment, boundary/edition mismatch and unresolved geographic precision. Do not interpret missing site/GIS matches as true unsuitable habitat. Only after the crosswalk can one quantify how many *eligible searched* species/sites remain under spatial held-out support; do not fit a biological response before that gate.

## Reproduce / audit

- Script: `scripts/audit_aadc_geography_editions_v1.py`
- Synthetic tests: `tests/test_aadc_geography_editions_v1.py` (**4 passed** in original CI)
- JSON receipt: `results/AADC_GEOGRAPHY_SITE_EDITIONS_V1.json`
- [Successful GitHub Actions run](https://github.com/zuizui0223/mina/actions/runs/40162883187)
- [Exact original result artifact](https://github.com/zuizui0223/mina/actions/runs/40162883187/artifacts/12587261486)
- SHA original 2021: `2236269e754962f9af082a0853993fc65a4afd20c7489a65fae81bdd1899ffaa`
- SHA original 2025: `ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294`

This result is a new source-derived spatial provenance contribution, not a penguin-ecological effect or an empirical test of double insularity.
