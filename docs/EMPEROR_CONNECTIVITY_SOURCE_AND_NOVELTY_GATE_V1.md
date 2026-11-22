# Emperor colony accessibility × breeding output: independent source-and-novelty audit

Date: **2026-11-22**. State: **source gate completed; direct quantitative hypothesis NOT identifiable; no effect coefficient computed**.

## Stage 0 source retrieval (completed, verified)

- Macdonald et al. 2026, `https://doi.org/10.5281/zenodo.17380979`: official Astrid, Mertz and SANAE Excel catalogues. The three small XLSX checksums are verified. These are **image-date location / surface-substrate observations**; `x` indicates visible colony/guano and `~` is uncertainty. A non-visualization must **not** be converted to breeding failure, a true absence, or zero chicks. Actual distances to the fast-ice edge are distributed separately in a ~2.4-GB shapefile ZIP, not in these Excel files.
- Winterl et al. 2024, `https://github.com/whoi-mars/EmperorPenguinPhenology`: original supplementary Excel S10, S11, S19, S20 and **S21** downloaded. S21 contains actual recorded breeding pair and chick count outcomes: **10 Pointe Géologie colony-years (2012–2021)** and **3 Atka Bay colony-years (2018–2020)**, for **13** direct pairs/chicks observations.
- LaRue et al. 2024 public modelled spring attendance (not chick outcome): 50 colonies × 10 years, 2009–2018. Same official release SHA as the independent DEEP-AA primary analysis.
- Previous DEEP-AA audit: 50 colonies × 2009–2018 with complete Apr–Aug polynya exposures in 9 of 10 years (2012 incomplete).

### Audited join counts (not independent biological tests)

| Join and distinction | Exact joinable units |
|:--|--:|
| Macdonald Astrid/Mertz/SANAE substrate catalogues ↔ LaRue spring attendance 2009–2018 | **30 colony-seasons** |
| Those 30 with complete Apr–Aug DEEP-AA index | **27 colony-seasons** |
| Winterl direct observed chicks/pairs, including 2019–2021 | **13 colony-seasons** |
| Winterl observed chicks/pairs ↔ LaRue 2009–2018 | **8 colony-seasons** |
| Those 8 with complete Apr–Aug DEEP-AA | **7 colony-seasons** |
| **Actual fast-ice-edge route distance × actual chicks/pairs, same colony-year** | **0** |

Macdonald's sites are Astrid, Mertz and SANAE. Winterl's two sites are Pointe Géologie and Atka Bay. The site sets do not intersect. **Do not fit the proposed distance→breeding success regression**, do not backfill a modelled LaRue index as survival, and do not treat 3 repeated sites as 30 spatially independent replicates.

## Novelty and prior work: no old hypothesis recycled

1. **Longer fast-ice-edge distance reduces breeding and fledging success:** Barbraud/colleagues 2021 (39-year Pointe Géologie series, Aug–Nov windows), `https://doi.org/10.1098/rsbl.2021.0097`. Hence the absolute distance→success question is already answered at a long-term single-site scale.
2. **Continent-wide habitat diversity and fast-ice spatial architecture:** `https://doi.org/10.1126/sciadv.adg8340` (2023). Distinct geographic habitat clusters already established; do not claim novel discovery of habitat polymorphism.
3. **East Antarctic 27 colonies and ice-edge distance, relocations and breeding losses, 2018–2023:** Wienecke et al. 2024, `https://doi.org/10.3354/esr01355`. The stability–access tradeoff has been discussed and some colony-level outcomes documented.
4. **Breeding-site relocation:** Macdonald et al. 2026 (`https://doi.org/10.1017/S0954102025100515`) and Fretwell et al. 2026 (`https://doi.org/10.1038/s42003-026-10961-y`).
5. **Physical interruption of access despite habitat:** Park et al. 2026, Coulman iceberg event, 69% drop in chick counts (`https://doi.org/10.1038/s43247-026-03764-w`); not a new mechanism by itself.
6. **Winter polynya area and modelled abundance:** previous independent, outcome frozen null `https://github.com/zuizui0223/mina/actions/runs/45018808042`; none of this data-audit work changes it.

## Forward gate

The only meaningful next independent quantitative test would be a **multi-colony, matched colony-year, pre-fledging habitat stability × functional ocean-accessibility model**, on **breeding outcomes independent of the ice predictor**, extending beyond the one-colony 2021 result and the 2026 iceberg case.

Need to first obtain truly independent annual chick/breeder counts or comparable survival measures for a plurality of Macdonald/Wienecke locations **or** generate validated ice-edge/obstacle route distances at ≥2 original Winterl colonies over enough years. Need check genuine sample size and temporal spread *before* choosing model/predictors, and compare to 2021 and 2024 papers. Do not imply this gate is solved.

## Record scope

This branch is an independent **feasibility/data audit**, not a new paper, not a positive ecological result, and must not delay the frozen Adélie manuscript. No model fits claimed; no hypotheses retuned after the earlier negative polynya result.
