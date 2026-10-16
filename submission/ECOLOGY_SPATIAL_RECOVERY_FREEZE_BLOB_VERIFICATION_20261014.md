# Ecology v0.9 — frozen-source SHA verification and clerical correction

**Verified:** 2026-10-14. **Scope:** publication-provenance QA only. No frozen scientific dataset, model, manuscript effect, figure data or null comparison has been modified.

## Verified immutable scientific blobs

The exact eight scientific-file Git blob SHA-1s on the active `analysis/ross-sea-expansion-intensification-support-v1` branch were individually checked against the original immutable scientific freeze commit `3e8882742ca2affc6717d373fd9b6d903b01f4c1`. All eight files have **identical blob hashes to their original scientific freeze versions**.

| Source | Verified Git blob SHA |
| --- | --- |
| `docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_8.md` | `b95ccc5f662b21c77635e5b7273fd400cd51d59f` |
| `docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib` | `09e1e8c6cc7a52cde9d71ebccdb77a26d76b818e` |
| `results/SPATIAL_RECOVERY_CLAIM_EVIDENCE_LEDGER_V4.json` | `e4f5549cbb0b218a0b03fb0bf665459f6ddfcad8` |
| `results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json` | `ee274203b373d38dd8fc2035cbde54103706864f` |
| `results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json` | **`6682dafcf49d0b9d335ce99ce0e6bb8fa6c4e5d0`** |
| `docs/ROSS_LOCAL_RECOVERY_RATIO_DECOMPOSITION_V1.md` | `c48cf9054f3ee7451c756351cd87da0a5ba4579f` |
| `scripts/build_spatial_recovery_path_state_figures.py` | `a458fa5fe7d1fb03261c0e08ba354a5d78302776` |
| `docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_1.md` | `afdd6a6d15dce8e57b8f61858414a87246d830c6` |

## Historical typo, not scientific drift

The original record `submission/SPATIAL_RECOVERY_ECOLOGY_SCIENTIFIC_FREEZE_V1.md` wrote the spatial-grain result SHA as `6682dafcf49d0b9d335ce99ce0e6bb8fa6c4e5` (last **`d0`** omitted). Both the scientific freeze commit and the active branch actually contain the full SHA above, and their *contents match exactly*. The original historical record is retained unmodified; **this document is its addendum correcting a citation of a Git blob, not a replacement freeze or fresh analysis**.

This does not change the canonical scientific manuscript, results, effect sizes or preregistration/inference classification. Production manuscript remains `docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md`, and any final author-complete submission rendering must be separately checked.
