# V8 Antarctic ecosystems × co-censused penguin pairs — result and ecological decision

**Observed 2026-10-19, source-backed** [GitHub Actions #39219124577](https://github.com/zuizui0223/mina/actions/runs/39219124577) SUCCESS, [original machine-readable result](../results/APBP_ANTARCTIC_ICEFREE_COEXISTENCE_V8.json). Frozen first effect protocol: [V8](../contracts/APBP_ICEFREE_ECOSYSTEM_COEXISTENCE_V8.md). **No change to the frozen Ecology manuscript PR189 or the negative V6 result.**

## Biological question, exact response and non-circular environment

Does the abiotic environmental mosaic surrounding an already known, jointly surveyed penguin breeding locality predict how **equally original Adélie / chinstrap / gentoo nest counts are distributed between co-recorded species**?

- Original event-matched observations: APBP DwC-A v2.3 (DOI 10.48361/zftxkr), source SHA256 `afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf`, with eMoF original occurrenceID matching and original nest unit checks. An `Event` is a census event that may cover a colony site, **not proof the species nest in the exact same square meter**. Missing species have no inferred zeros.
- Independent terrestrial cover: Tóth et al. 2025 *Antarctic Ecosystem Inventory*, source DOI **10.5281/zenodo.11629115** (56,185,140-byte 100m TIFF SHA256 `7d6c93613f47924f491b74005aa6dda6503ea48abf43dc38d2028d29b8b2f87c`; VAT 103,681 bytes SHA256 `f4de71a32ec735096bf0898adb78eea8cb120c2e452ef7f14502dd8b586955aa`; source published MD5s matched). Original Tier1 labels: E1,E2,E3,E4,E5,G1,G2,G3,L. The original **E1B8 “Penguin colonies”** Tier2 and every penguin-labelled source Tier3 were **excluded before fitting** to reduce tautological MAPPPD response contamination. Even remaining general Tier1 geography is not a direct independent nest-substrate survey.
- Pairwise response `balance=2*min(N_A,N_B)/(N_A+N_B)`, per original simultaneous census Event, summarized as the **median across source Events per site×species pair**. Thus 0 = one species dominates / the other is an original observed zero; 1 = equal nest counts. Conditional on TWO species being recorded at an established site, not island-wide coexistence probability.

## Original sample and quantitative comparison

The original **350 co-recording Event IDs, 62 census site IDs** yield **348 admissible original Events, 472 pair-level source Event contrasts, 82 site×species-pair panels over 60 sites** after strict duplicated taxa/zero-total restrictions. After requiring at least 30 *non-penguin-source-derived* 100m environmental pixels in the 5km fixed radius: **61 site-pair rows over 42 sites**. After requiring at least 3 distinct surveyed sites per geographic 250km holdout block: **55 site-pair rows, 40 source sites and 5 spatial blocks** entered the model. Mainland assignment: 6 of 40 model sites, 31 provisional islands, 3 still geounmatched; hence this is **not** an identifiable mainland–island effect test.

| 5km main predictor | 5-region equal-block MSE | Original 55-row weighted MSE |
| --- | ---: | ---: |
| B0 species-pair, latitude/longitude, original pair total nests, source census accuracy and replicated event count | **0.076740511** | 0.075126246 |
| B1 B0 + Tier1 Shannon environmental diversity + mapped *non-rookery* ecological fraction | 0.071352392 | 0.069765730 |

- B1 nominally improves the equal-block MSE by **0.005388119**, but **only 2 of 5 regional blocks** improved (prespecified support gate needed >=4/5).
- Full-sample normalized Tier1 entropy coefficient **−0.034274**, excluding dominant region **−0.048029**. A stable sign by itself is insufficient if most regions worsen and source position is imprecise.
- In the prespecified **2km sensitivity**, the B1 MSE **0.079536021 is worse** than the same B0 **0.076740511**. Only 1/5 regions improved and entropy coefficient sign changes **+0.056516 → −0.029990** when the largest region is left out.
- Only **10 unique original source sites** in the primary cohort have source positional uncertainty <=1km; predeclared precision-coefficient subset lacks the required sampling support and was therefore **not estimated**. No imputed high-precision effect.
- Every biological effect is observational and exploratory: **`scientific_decision=NOT_SUPPORTED_OR_UNIDENTIFIABLE`**, **`passed_full_descriptive_macro_support_gates=false`**, **`novel_island_mechanism_demonstrated=false`**.

## One descriptive ecological pattern, not a new causal mechanism

**Post-outcome descriptive summary** from the same 55 source site×species pair rows (full source in V8 Actions artifact, no null test): the **median pairwise balance was 0.15547**, implying that among co-recorded taxa one species held approximately **92.23%** of their combined recorded nests at the median site×pair. **30/55 (54.5%)** of rows had >=90% of recorded nests assigned to the locally dominant member. Aggregated first to 40 distinct original census sites, the median *within-site median dominant share* was **92.02%**; 21/40 sites had within-site median dominant share >=90%. This is a descriptive **strongly asymmetric recorded abundance split in jointly sampled taxa**—not proof of local physical exclusion, true competition, reproductive success or temporal species displacement. It can arise from within-site colony delineation choices, sampling effort and species-specific nesting counts. It is neither a general all-Antarctic prevalence estimate nor unique to islands.

Species-pair panel counts in the 55 selected source site×pair rows: Adélie–chinstrap 10, Adélie–gentoo 18, chinstrap–gentoo 27. Their pair balance medians were approximately 0.1183, 0.2560 and 0.1357, respectively; no independent phylogeny or statistical difference test was performed.

## Research decision: distinguish a useful database from genuinely identifiable ecological novelty

A more complex environmental predictor has now **failed robustness requirements** in both separate V6 (marine ice × island rock) and V8 (abiotic terrain mosaic × species nest balance). It is scientifically inappropriate to search for a positive regression by changing the buffer scale after observing these results.

The current original count panel also cannot reliably test local interspecific competition/synchrony: among 350 original multi-species co-recording Events, only **181 have an unambiguous December/January/February timestamp**. Applying strict one-record-per-source-site×pair×season uniqueness leaves **25 exactly consecutive co-census pairs from 9 distinct locations**, too little geographically independent replication for a pan-Antarctic annual species-rank turnover law. This is *metadata-only feasibility*, not a fitted co-response effect; not a basis for 350 independent longitudinal comparisons.

A next causally informative data type is independently repeated observations of **suitable, explicitly surveyed but unoccupied substrate, new colony founding or abandonment, snow/landfast-ice interruption and tagged breeder status**, preferably at multi-island scale. This will distinguish resource selection versus breeding nonparticipation and priority effects. Both seabird colony distributions and Palmer snow/landscape-driven colony extinction have established prior art (e.g. *Landscape Ecology*, 2025, DOI 10.1007/s10980-025-02088-y). The 2026 emperor remote-sensing persistence study (DOI 10.1002/rse2.70064) likewise already shows historical colony use. Do not rediscover these patterns with only existing published figures.

**Stop here on V8.** The future island ecology manuscript requires qualitatively better observations (site-specific habitat and actual nesting establishment), not more threshold tuning of an already insufficient APBP×AEI cohort.
