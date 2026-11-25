# V17 — Evidence synthesis: spatial co-location is not established site takeover

**Date:** 2026-10-13. Independent exploratory Zavodovski research PR #196. This document is an interpretation of already-opened outcomes, **not a preregistered new biological test**. Frozen Ecology PR189 is untouched.

## Prior art; what cannot be claimed as new

Ratcliffe et al. (2026, *Current Biology*, DOI 10.1016/j.cub.2026.09.010) already established rapidly declining chinstraps and increasing macaronis on Zavodovski and considered krill availability under regional warming a more plausible primary decline driver than island nesting competition, fisheries, volcanic eruption, or whales. The broad opposite-species population trend, ecological attribution, and 'competition is not main cause' are not novel PR196 findings.

The independent January 2011 colony mapping of Lynch et al. (2016, *Polar Biology* 39:1615–1625, https://doi.org/10.7282/T3N58PHR) is also published prior art; its survey and satellite basis are documented in BAS database GB/NERC/BAS/PDC/02263. It is a **different interpretation of the same image**, not an independent year or a replicated population response.

## Source-validated analysis hierarchy

| Evidence | V10 / first digitization | Historic / alternate map | Supported meaning |
| --- | ---: | ---: | --- |
| M-gain area overlapping C-loss, 2011→2016, all direct-image cloud-free support (E) | 66.96% | not comparable without mixed-class masking | descriptive spatial overlap, **not** colonization |
| M-gain area overlapping C-loss, 2016→2025, pair-specific cloud-free support (E) | 67.82% | no historic 2016 replicate | descriptive |
| C-loss area overlapping M-gain, 2011→2016 (F) | 7.97% | not comparable until same support | most loss is **not** mapped as a M gain |
| C-loss area overlapping M-gain, 2016→2025 (F) | 5.73% | no alternate-year map | same |
| V16 E 2011→2016 **after masking MIXED and historic pure-polygon overlaps on identical support** | **62.64%** | **32.56%** | same-scene redigitization shifts E by 30.08 percentage points |
| V16 F on identical unambiguous support | **7.40%** | **4.70%** | F remains small in the two interpretations |
| V16 Jan 2011 same-scene Jaccard, species-specific clean support | C = **0.540747**, M = **0.512006** | two source maps | major cartographic disagreement |
| V15 direct mapped M-gain in 2011 historic MIXED patches | **13.21%** of mapped gain | MIXED independent label | prior mixed colony co-occurrence explains some, not all of apparent gains |
| V15 M-gain∩C-loss overlapping historic MIXED | **18.79%** | MIXED independent label | some apparent 'takeover' had prior mixed occupancy |
| V11 shifting mapped C-loss by 10m | median E **30.05%** (2011→2016), **37.86%** (2016→2025) | fabricated shifts | strong sensitivity to geometry, **not** measured image registration error |

Relevant original audited artifacts on PR #196:
- `results/ZAVODOVSKI_DIRECT_IMAGE_OVERLAP_V10.json`
- `results/ZAVODOVSKI_POST_OUTCOME_GEOMETRY_DIAGNOSTIC_V11.json`
- `results/ZAVODOVSKI_HISTORIC_MIXED_PATCH_OVERLAY_V15.json`
- `results/ZAVODOVSKI_2011_ALTERNATE_DIGITIZER_V16.json`
- Original source dictionary: `sources/bas_zavodovski_layer_descriptions_v1.csv`

## The ecology, separated from measurement

**1. Positive descriptive finding, conditional on mapped boundaries:** Macaroni mapped gain preferentially spatially co-locates with some places where chinstrap mapped boundaries contract. But 'preferentially' here is **not** a habitat-availability-controlled statistical preference; use 'co-locates' only.

**2. Robust asymmetry in *area*, not individuals:** The converse fraction remains small (V10 5.7–8.0%; V16 4.7–7.4% on fixed nonmixed support), so the vast majority of mapped chinstrap loss is not replaced by mapped *new* macaroni breeding area. A 63% or other species-population trend from the main paper cannot be converted into bird-to-bird spatial takeover.

**3. Critical veto on a novel mechanism:** V16 map redraw nearly halves E and Jaccard ~0.5. Exact patch succession, founder settlement, guano legacy, competitor suppression and density facilitation are **not identified**, even without the cloud-year problem. The 2011 sample's historic MIXED polygons further imply that a loss/gain overlay need not represent absence→arrival at the same nest site.

**4. Existing prior art narrows novelty:** Ratcliffe et al. already favored oceanic krill effects over terrestrial nesting competition. PR196 currently adds a valuable evidence audit and finer-grain spatial measurement sensitivity; it does **not** independently discover a new causal island-biogeography mechanism.

## Decision for manuscript program

- **Do not fold PR196 into the frozen Ross/Palmer Ecology manuscript**. Do not headline E≈67% as interspecific takeover.
- Keep PR196 as descriptive measurement audit / methods-informed discovery. It may become a short supporting technical note only if a proper independent validation or mechanism emerges; it is not yet a stand-alone mechanistic ecology paper.
- A true mechanism test requires at minimum independent within-colony occupancy lineage (actual C and M presence at the same physical site), georeferenced fixed-substrate habitat and opportunity mask, separately measured between-year positional error, and sufficiently frequent observations to establish ordering of occupancy change. Original-year cloud masking alone is insufficient.
- Candidate broader ecological question: can cross-species population substitution occur while *most* formerly occupied nesting substrate is **not reclaimed**, and is that true across independent island systems after controlling for colony-map uncertainty? This is a **hypothesis**; the single-island satellite maps do not establish it as a general law.

Status: V16 observed; V13 intentionally held as source-label mismatch; V16 is an exploratory post-outcome alternative-map test. No p-value/claim of causal competition.
