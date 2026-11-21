# AADC 16 A→P observational reports × Landsat source scenes — complete event inventory (2026-11-21)

**Current state:** Both austral summer scene metadata queries have been completed for **all 16 original expert-supported AADC absence-report→breeding-presence observation transitions**, spanning 14 original geographic site IDs. This is an **event-only, source-only reconnaissance** of candidate Landsat imagery. It is **not a census of actual bare-rock exposure, true new colonizations, or independent physical islands**.

### Original science and provenance

- AADC 2025 8-species origin: expert supported, original absence grade 4, exactly **16** observed annual A→P records at **14** geographic site IDs. [Source QA workflow #44530909415](https://github.com/zuizui0223/mina/actions/runs/44530909415).
- Publisher original latitude/longitude: original AADC geog-site XLSX SHA256 `ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294`; **source point centroids are not mapped nests**.
- Imagery provider: [Element84 Earth Search STAC](https://earth-search.aws.element84.com/v1/), collection `landsat-c2-l2`. Original command `scripts/audit_aadc_landsat_scene_source.py --max-events 16`; [full original scene metadata run #44850629480](https://github.com/zuizui0223/mina/actions/runs/44850629480) artifact **14684739302**. Exact original source files/season window constraints retained.

### Original scene metadata outcomes

| Cohort | Immutable event count |
| --- | ---: |
| Original reported A→P transitions | 16 |
| Both A and P austral seasons return ≥1 Landsat scene | **8** |
| Only P-season images returned | 4 |
| Neither season returned or both outside catalog era | 4 |
| Source query errors | 0 |

Both-season scenes at **8 distinct source site IDs**: `IS_70749`, `R_223`, `IS_70714`, `IS_70731`, `IS_70715`, `IS_70729`, `IS_121`, `IS_105` (A-observation austral season starts 2008 through 2017). These span **DUM (6) and LUT (2)** broad geographic areas; the land-source classification is 7 island and 1 continental source point, **not 8 comparable physical landmasses**.

Across 32 event-season queries: **20** queries returned at least one scene; **349** scene items were returned on the *first available page* summed across event windows, all **349** with a `qa_pixel`/QA asset listed. They are **not 349 distinct independent images** because several nearby site-buffers and years overlap. All 20 positive queries also report a STAC `next` link (pagination may apply), hence **first-page scene counts are lower bounds or preliminary, not complete image inventories**. The source script correctly marked zero season pairs as complete unpaginated counts and eight as *nonzero scene metadata on both sides*.

### Exact source-only stop

STAC `eo:cloud_cover` is a **scene-level** fraction. It cannot tell whether the specific 30 m pixel near an AADC nest patch was actually visible, nor whether visible land is ice-covered. Landsat 7 imagery since 2003 may include SLC-off unfilled pixels. For Landsat 4–7, USGS notes that the QA_PIXEL Clear bit (6) alone is unreliable in some conditions and direct cloud/dilated-cloud/filled bits should be checked instead ([USGS](https://www.usgs.gov/landsat-missions/landsat-collection-2-known-issues)). The next feasible **technical** gate is read-only site-buffer `QA_PIXEL` on two independently located candidate events, not a hypothesis-driven glacier/colonization model.

An ice-covered→new bare-rock conclusion would require separately validated original image footprint dates, cloud/shadow/snow/water QA, actual rock/ice classification at an independently mapped **nest patch** and a parallel survey of unoccupied possible patches. The 16 events are observational state changes rather than confirmed new settlement. Source-only infrastructure remains separate from frozen Paper1/Paper2 and earlier AADC PR180 threshold.

Machine-readable receipt: `results/AADC_16_EVENT_LANDSAT_STAC_SOURCE_QA_20261121.json`. Original full source metadata JSON is the pinned workflow artifact; preserve it for any future pixel-QA work. No inferential p-value was calculated.
