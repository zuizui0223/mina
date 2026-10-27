# V39 integrated evidence decision — JNCC seabird decline concentration, site-size reversal, and leader switching

**Updated 2026-10-27, PR #201; original independent JNCC 2024 revised counts and official UK/RSPB/Stanbury spatial sources.**

## Current new ecological proposition — counts, not causation

> Across source-matched UK/Ireland seabird monitoring networks, falling aggregate breeding counts often correspond to more concentrated **relative site composition**, yet the monitored breeding components that become numerically dominant need not be those that were initially largest. Thus colony-composition concentration and persistent historical site dominance are distinct processes.

The original evidence here is **two adjusted-count census snapshots separated by about two decades**, not annual, movement, independent nest polygons, or physiological social attraction experiments. The word "island" applies to the ecological research programme but is NOT established as a causal physical boundary for each JNCC monitoring parent.

### V30 source-comparable macro sample (already known before all mechanisms)

- Official publisher JNCC revised XLSX SHA256 \`9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4\`.
- 14,112 matched original site×species records → 1,483 guarded structural source parents → **1,321** source-exact integer-count parents across **17 seabird taxa**, 604 Country×Master monitoring networks → **959** with declining matched-site total.
- **597/959 (62.25%)** have concentration \`E>0\` beyond idealized finite-count proportional allocation \`C0 + (1-C0)/N1\`; species equal 14/17 positive means E. This alone does not predict initial dominant-site persistence and is not a causal metapopulation model.
- Results: \`results/JNCC_COMPONENT_CONCENTRATION_V30.json\`, original source PR #198.

### V37 new, pre-frozen size share-retention score (post-V30 discovery)

- Contract \`contracts/JNCC_SIZE_SHARE_SCORE_V37_FROZEN.md\` fixed α=0.5 baseline smoothed site allocations, size feature log(1+n0), standardized conditional within-parent score S, 1,999 fixed multinomial draws, primary declining cohort and species-equal weighting **before opening NEW V37 size-score results**.
- **955** declining information-bearing parent panels (4 omitted because identical original child sizes), 17 taxa. Species-equal signed size-score **−0.538864**, *16/17 species negative* (only Great Cormorant n=4 positive); conditional fixed-count null 5–95% **[−0.02507, +0.02394]**. The preregistered positive size-retention H1a directional prediction **FAILED**; all-count cohort score −0.53973, 0/17 positive.
- Source-country leave-one-out species-equal S remains negative, including omitting Scotland **−0.57667**. No direct evidence of a social Allee effect or its absence, no independent site quality or measurement-error model.

### V38 post-result concentration/turnover decomposition

**Openly post-result exploratory—not independent confirmatory testing.** Compare E, S, and genuinely unique source Site.ID leader in both epochs using the same JNCC parents.

| Source descriptive endpoint | Source count | Raw eligible fraction | Equal-species observed | Equal-species expected under 1,999 fixed allocation draws |
| --- | --- | --- | --- | --- |
| E>0 among declining | **597/959** | **62.25%** | **62.58%** | **40.41%** |
| E>0 AND S<0 among size-informative declines | **321/955** | **33.61%** | **29.42%** | **3.67%** |
| Dominant child source Site.ID switches (unique early and late leader) | **412/846** | **48.70%** | **47.85%** | **14.20%** |
| E>0 AND dominant child source Site.ID switches | **284/846** | **33.57%** | **30.34%** | **5.32%** |

Source: \`results/JNCC_CONCENTRATION_HIERARCHY_TURNOVER_V38_RESULT.json\`, authentic [Actions run](https://github.com/zuizui0223/mina/actions/runs/40439702295).

- Why apparent leader switching does NOT demonstrate real dispersal: source Site.ID names and nesting polygon stability across old/new censuses have not been independently mapped, a two-period compositional rank change contains no banding/recruitment/immigration evidence, and changes in counts can reflect changes in effort or the true site basis.
- A toy study with **fixed latent original site shares [.55,.30,.15]** but independently drawn invented earlier/later counts (N0=40,N1=25) produced a **−0.0498 average baseline size score** without any biological shift. Hence **regression to the mean from baseline measurement noise** is an actual alternative explanation, not a trivial concern. This toy is NOT calibrated to JNCC original census noise and cannot establish how much of observed S−0.54 it explains.
- V38's large conditional-null deviations are conditional on frozen empirical \`p0*\`, not calibrated multinomial survey errors or a causal demographic baseline. E and S share both source epochs and do NOT supply independent mechanistic causal evidence.

### V39 original metadata exact same-year within parent robustness

This post-result sensitivity excludes original source networks with asynchronously surveyed children within either census epoch, with no change of cutoff after the source gate.

- Among 1,483 guarded parent panels, **762** had exactly the same original earliest census year K among all children AND exactly the same original latest census year N among all children (earlier-only 1,216, later-only 869).
- Restricting to exact-integer source panels yielded 663; of those **479** had lower second-round totals and **475** had informative baseline sizes.
- Across **16 taxa with ≥3 panels** the species-equal size score remained **−0.517590**; **15/16 negative**. Conditional count-allocation null 5–95% **[−0.04010,+0.03905]**. Omission of Scotland retained negative **−0.25268**.
- Concentration remained observed in **303/479 = 63.26%**; concentration with size reversal **150/475 = 31.58%**; maximum component switches **207/409 = 50.61%**, and excess concentration plus switching **142/409 = 34.72%**.
- Source: \`results/JNCC_MATCHED_EPOCH_COHORT_V39_SOURCE_RESULT.json\`, original [Actions run](https://github.com/zuizui0223/mina/actions/runs/40440078980).
- **Resolved risk only:** within each retained panel, children no longer differ in the YEAR of their earlier/later original source survey. Still unresolved: original survey season/day, method, adjusted-count procedure, parent network/site polygon identity, site-specific observation error and habitat quality.

## Physical island and invasive mammals — separate source lane, NOT merged as an inferred explanation

- Original first-party RSPB 2014 spatial point inventory **9,688** source lowid entries and Stanbury 2017 ESM5 original invasive mammal coded table join one-to-one. The publisher's >10 ha island denominator is **low-tide area, 506 islands**, not high-tide area (401 islands). Confirmed/probable source labels among those 506: mink 113 (22.3%), brown rat 106 (20.9%). Code 0 combines **"assumed OR known absent"**, not verified absence.
- A descriptive source-label niche screen in 506 islands finds **brown rat** geography predictability but **mink** nonportability across held-out source geography; source labels are potentially generated using island geography and monitoring assumptions. They are NOT true calibrated ecological predator occupancy estimates.
- Source-only physical crosswalk of original JNCC monitoring components against verified **GSHHG 2.3.7 full** shoreline and RSPB/Stanbury original island IDs yielded only **3** source-complete mixed-physical-island parent networks (Common Tern, European Shag, Herring Gull), 8 island IDs, **zero with source mink label contrast and one with brown-rat contrast**. Frozen within-parent H2 source sample requirement ≥20 networks/5 taxa FAILED. This is **nonidentifiability**, NOT absence of a mammalian predator effect. No favorable coastline buffer/name-based pseudo-island rescue is permitted.
- Relevant receipts: \`results/JNCC_PREDATOR_REPORTED_NICHE_V34_SOURCE_RESULT.json\`; \`results/JNCC_PREDATOR_DOCUMENTED_NICHE_V34_SOURCE_RESULT.json\`; \`results/JNCC_PREDATOR_GSHHG_F_L1_ORIGINAL_GEO_SUPPORT_V36.json\`; [source-only V36 Actions](https://github.com/zuizui0223/mina/actions/runs/40438230884).

## Novelty and honest claim ceiling

**Positive, source-derived and general across many taxa:** spatial concentration among falling monitored networks is often accompanied by reorganization of historical site dominance, and a simple preferential-retention-of-initially-large-sites hypothesis fails under one fixed allocation reference even within matched-year subgroups.

**NOT demonstrated:** social attraction as an identifiable mechanism; predator refuge or physical island causality; habitat capacity effects; absolute occupancy loss, verified physical nest-plot expansion or extinction; individual exchange, first-year nesting effort or actual recruitment; general Antarctic vs UK causal contrast. Meta-analysing these samples as independent islands or claiming a Nature-level island mechanism would be scientifically unjustified.

**Primary next biological data requirement:** independent first-party historical site/nest-polygon boundary lineage, source methods/effort and stage-matched local nest records, repeated measures for measurement-error calibration; then independently verified local nesting habitat/cliff/burrow accessibility or historically dated predator intrusion/eradication. Without those, source-count patterns remain two-epoch descriptive inference.

Existing frozen Penguin Ecology Paper1 PR #189 and independent Antarctic macro PR #197/#199 remain untouched. No new manuscript submitted.
