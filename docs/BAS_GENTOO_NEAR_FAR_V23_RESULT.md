# V23 — Verified BAS original gentoo near-vs-far annual nest-growth gradient

**Date: 2026-10-21.** Executed on the original BAS Bird Island, Maiviken and Signy CSV sources after prospectively freezing the FAR-region outcome comparison in [V23 contract](../contracts/BAS_GENTOO_NEAR_FAR_REGION_V23.md). The observed V22 near result was already known before designing V23, so this is an exploratory directional test, not an independently preregistered discovery. [Original-source GitHub Actions #39447683037](https://github.com/zuizui0223/mina/actions/runs/39447683037) completed successfully with five invented-fixture tests. Source hashes and V22's full 10-window result were reproduced exactly before any V23 far correlation.

## 1. What was compared

**One species, three separately located BAS monitoring systems**, all gentoo penguins. The original response is the *within-source annual log(1+nest count)* change; Bird Island is the equal-weighted mean of seven original colony-specific changes, Maiviken is the original incubating-nest change on the larger South Georgia main island, and Signy is the original TOTAL_NUMBER_OF_PAIRS annual change from ten colonies. These count stages and monitored colony extents remain different. No absolute population totals were pooled.

The fixed V22 cohort included 10 consecutive windows over 2009–2018. The source-pinned Signy CSV had 43 original records and 10 usable numeric original pair-count seasons in the V22 2009–19 period, leaving **8** *common three-site* consecutive annual-change windows (**2011–2018**). The first two V22 windows are excluded only because a Signy source count was not numerically usable. All three r coefficients use precisely the same eight windows; the observed V22 full-cohort r=0.5621534427494942 remains preserved, not replaced by the restricted-cohort estimate.

## 2. Genuine numerical result

| Exact same 8 start-year windows 2011–2018 | Pearson r annual growth | Same-direction windows |
|---|---:|---:|
| **Bird Island – Maiviken** (same South Georgia subregion) | **+0.5143600** | **6/8** |
| Bird Island – Signy (distant, same provider) | **−0.3342093** | 3/8 |
| Maiviken – Signy (distant, same provider) | **−0.6680307** | 3/8 |

**Predeclared contrast**: r(Bird,Maiviken) − ½[r(Bird,Signy) + r(Maiviken,Signy)] = **+1.0154800**. Leave-one-annual-window-out contrast remains positive, range **+0.7089716 to +1.2963925**. These are correlations, NOT estimated unitless causal coefficients and NOT independent hypothesis tests across 3 geographical pairs. Eight adjacent change windows share consecutive seasonal observations and may be autocorrelated.

The narrow predeclared descriptive question is answered **YES** for these original monitoring series: *same-region breeding changes are more aligned than distant within-provider changes, despite a physical island boundary between Bird and Maiviken*. Crucially, all three datasets are obtained from BAS, so a simple “NOAA versus BAS publisher difference” cannot alone explain the observed near-versus-far pattern.

## 3. Critical interpretation

- This is a **within-BAS descriptive regional gradient**, not a proven effect of ocean-water barriers, static island area, breeding substrate or any specific marine resource. Geography remains coupled with oceanic regime, climate exposure, local observer/protocol, census extent and breeding phenology.
- Maiviken is on **South Georgia main island**, NOT on the Antarctic mainland. Bird Island is a separate offshore island; Signy is another independent physical island. Seven Bird Island colony counts are nested, not independent islands.
- The Signy measure is breeding pairs, Bird Island uses nests and Maiviken incubating nests. Within-site changes reduce fixed counting-scale differences; variation in reproductive stage/effort does not cancel. The data cannot prove that changes in actual breeding attempts are equivalently measured.
- The near result was seen before V23 was specified, and the sample has only **3 physical landmasses and 8 annual windows**, so neither a statistically general island-distance law nor a new causal ecological mechanism is established. Known regional penguin dynamics and breeding trends are prior art.
- Independent next-mechanism evidence would need species-matched simultaneous regional **wind/sea-ice/marine-access anomalies**, validated at colony and seasonal scales, and several geographically replicated island–mainland pairs. Do not regress 3 islands on post-selected variables to manufacture a climatic cause.

## 4. Provenance and stop rules

The [V23 machine-readable result](../results/BAS_GENTOO_NEAR_VS_FAR_V23.json) records original SHA256 for Bird Island **b1abc3c3adacee3f277d481217aabe4206c7b592a81f1f0eb1a0ec20a64450d3**, Maiviken **8eef8ba06b0f1e666041be38415cfcc70d16cdb07e72ca6db805d8b70631dc85**, and Signy **53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b**. Original V22 source cohort/hash and exact full r check passed. One malformed old Signy season remains excluded, no missing report is recoded zero, no significance test or retrospective threshold re-optimization was done. The frozen Ecology PR189 and failed V14–V17 gates remain unchanged.

**Scientific disposition: DESCRIPTIVE_WITHIN_BAS_NEAR_GREATER_THAN_FAR_CAUSAL_HOLD.**
