# Antarctic island biogeography: source-capacity retention and neighbour rescue — pre-outcome gate v1

**Date:** 2026-10-08
**Status:** hypothesis + prior-art + data-identifiability audit; **NOT a preregistered or confirmed ecological result**.
**Scope:** new, separately evaluated island-biogeography programme. Do not alter the frozen PR #189 Ecology scientific package or reuse the outcome-exposed Palmer/Signy series as a prospective confirmation.

## The research question is about islands, not penguin breeding biology

> Can growth in usable breeding habitat on a marine-subsidised source island reduce the supply of dispersers to nearby islands, thereby weakening rescue or recolonisation even as the source population prospers?

MacArthur–Wilson area/isolation predictions concern immigration and extinction of island populations. They **do not** themselves assert that an increase in donor-island area must raise donor emigration. Do not advertise a logical contradiction of the original theory.

Antarctica allows a sharper hypothesis because:
1. Penguins generally acquire food at sea, so terrestrial island area proxies breeding opportunities much better than local trophic production;
2. usable ice-free terrain is dynamic even when physical island shoreline distances remain fixed;
3. the biological network is nested (subcolony → colony → physical island → marine-connected archipelago), and natal/breeding-site fidelity can sever physical proximity from realized immigrant supply;
4. ice, snowfall, topography, and access to open water independently vary.

Define an **effective source island** by usable habitat, juvenile recruitment and realized emigrant flux, not geometric area alone. Treat mainland coastal ice-free patches and offshore islands under the same concept where data permit; do not automatically treat the penguin colony as equivalent to a GIS landmass.

## Prior-art veto: why a simple capacity-or-fidelity claim is not novel

- Matthiopoulos et al. (2005), *J Anim Ecol*, DOI 10.1111/j.1365-2656.2005.00970.x: strong breeding-site fidelity can leave potential colony habitat unoccupied and delay recolonisation. The general site-fidelity explanation is prior art.
- LaRue et al. (2013), *PLOS ONE*, DOI 10.1371/journal.pone.0060568: on Beaufort, glacial retreat exposed usable habitat and visitation/emigration of Beaufort-chick-banded penguins to Ross Island colonies subsequently fell. The sign of local area gain versus outward movement was **already reported**.
- Bergstrom et al. (2022), *Global Change Biology*, DOI 10.1111/gcb.16331: Antarctic ice-free patch connectivity need not translate into establishment. The connectivity-versus-establishment distinction is prior art.
- Santora et al. (2020), *Global Ecol Biogeogr*, DOI 10.1111/geb.13144: penguin geographic structuring, neighbouring colony size and polynyas/canyons already analysed. Do not reinvent a generic distance/competition model.
- Recent focused access case: Coulman Island, 2026, DOI 10.1038/s43247-026-03764-w. Iceberg disruption of breeding–foraging access is documented; the existence of access barriers is not itself novel.
- Relevant existing mina work: `contracts/ROSS_SEA_ISLAND_MEDIATED_COMPETITION_V2.md` (PR #189) already proposes redistribution-scale switching. The genuinely untested extension is **receiver-side consequences**, not a relabeling of Beaufort.

**Novelty can survive only if** source capacity is independently measured and its change predicts **absolute outgoing cohort flux and recipient-side demographic rescue**, independently of total source output, spatial distance, access and observation effort. Source-side per-capita visitation alone is not sufficient.

## Non-trivial prediction ladder: three non-equivalent questions

For source island i and receiver island j at time t, define:
- `K_it`: independently mapped *usable* breeding habitat (not total island area and not merely guano-stain area);
- `R_it`: estimated annual cohort of potential first-breeding recruits at source i (not the count of breeding pairs);
- `p_ijt`: age-/stage-specific probability that an individual from i settles to breed on j (not just prospecting or sighting);
- `F_ijt = R_it * p_ijt`: estimated **absolute** source-to-recipient settler flux;
- `C_j,t+h`: receiver occupancy/reoccupation or demographic rescue outcome, subject to verified full-site coverage and detection modeling.

**P1 — retention:** after source density, cohort age, foraging/access covariates and effort are accounted for, an increase in independent K is associated with lower `p_out`. This alone would not be new at Beaufort.

**P2 — source-to-recipient flux reversal:** the fall in settlement probability exceeds any rise in the eligible source cohort, yielding **lower absolute export** from the growing source:
`Delta log(F) = Delta log(R) + Delta log(p) < 0`.
This is *not implied* by a falling percentage of visitors.

**P3 — negative source spillover:** surveyed neighbouring receiving sites exhibit fewer new settlers / reduced verified reoccupation conditional on their habitat, marine forcing and observation effort, with a predeclared lag and distance/connectivity kernel. This is the necessary evidence for a regional rescue consequence.

Failure of P1, P2, or P3 must be reported separately; do not collapse them into one qualitative 'paradox'. A positive P1 does not license P2 or P3.

## Distinguishing rival mechanisms

1. **Ordinary habitat / dispersal null:** receiver colonisation follows independently assessed recipient quality, donor output, distance and sea conditions. Source K adds no information once these are controlled.
2. **Constant philopatry:** between-island breeding movement is simply rare in all years, without capacity-induced change.
3. **Shared marine forcing:** changes in prey, sea ice or access jointly alter source counts, movements and receiver occupancy; there is no identifiable donor-induced spillover.
4. **Density-dependent emigration:** any observed migration is explained by occupancy/crowding, rather than changes in spare breeding options at a given density.
5. **Survey/cohort artifact:** Beaufort 'movement' is prospecting by chick-banded individuals, and non-observation is neither death nor nonbreeding. Detection effort and age composition can create spurious fluctuations.

A distinct nested-boundary hypothesis may be tested only if the same individual histories resolve **within-island versus between-island** settlement at matched distances and habitats. Component-count redistribution is not observed movement.

## Beaufort is a motivation, not a new identification

Published Table 1 (LaRue 2013) gives available nesting habitat of about:
- 1983: 107,571 m²; 34,588 pairs;
- 2005: 127,603 m²; 52,335 pairs;
- 2010: 129,029 m²; 63,760 pairs.

The **2005–2010 mapped-area increase is only about 1.1%**, whereas measured breeding-pair growth is around 22%. The drop in banded-bird outward visits after 2005 cannot be attributed to a contemporaneous large expansion of K without further evidence. A slow accumulated or threshold capacity effect remains possible, but is unproven.

The new small Beaufort subcolony's disproportionate growth during 2004–2010 (frozen PR #189 calculations, roughly 3.15× its proportional-growth share) can motivate a **within-island allocation** contrast. It is not a measurement of individual dispersal.

## Current dataset gate: not yet passed

**Existing `mina` sources:**
- MAPPPD/APBP frozen inventory: 729 breeding sites, 5,487 observations, 4,032 nest-count records; 152 trend-candidate Pygoscelis site × species units; 104 final predictor-complete units in the prior macro fit.
- The previous static breeding-landscape macro test was non-confirmatory (preregistered median interaction `gamma_AH=-0.318`, `p=0.0947`), and the association was sensitive to 1/2/5 km spatial support. Do not treat it as positive backing for the new theory.
- The Palmer/Signy network-loss feedback screen (PR #184) does not improve leave-one-population-out loss prediction beyond local size. A social rescue cascade is **not** already established.
- APBP breeding-site counts and static AEI-derived traits cannot identify `R`, `p_ij`, or absolute movement `F`.
- PR #142 / Issue #141 hold a separate USAP-DC first-breeding-choice route. The official API-key/schema/effort barrier must be cleared before accessing new individual outcomes. PR #190 documents focal-cohort gaps; chick-banded cohorts cannot automatically explain pre-2002 adult returns.

**Gate A — literature:** passed, with the strong novelty restrictions above.

**Gate B — *header-only* source/receiver data support:** pending. Before individual outcome access verify independently dated donor `K` series, cohort/band-origin identifier, age/stage, first confirmed breeding destination, resighting effort, at least one actual **between-island** movement opportunity, and receiver whole-site surveyed zero/positive histories. Distinguish “not surveyed” from “surveyed and absent”.

**Gate C — genuine replication:** require independently observable donor–receiver relations spanning multiple island systems / physical changes. Ross plus Beaufort, when treated as one connected archipelago, do not count as two independent networks. If only Beaufort is available, this remains a case study.

**Gate D — prospective execution:** select outcomes, lags, within/between-island hierarchy, age strata, distance kernel, region-year blocks and negative controls **before** opening focal transition magnitudes. Use untouched donors/receiver networks where possible. Do not salvage failed gates by threshold searching.

**STOP:** if individual settled recruitment and effort are unavailable, one may report a descriptive count/occupancy comparison but **must not** call it source-mediated demographic isolation or a new island-biogeography law.

## Ecological framing and intended result

Do not claim “more habitat increases isolation” based on local percentage movement. The potentially meaningful island-biogeographic result is:

> In a marine-subsidised archipelago, increases in one island's reproductive capacity can reduce the supply of colonists to other islands, making local habitat gains and regional rescue potential move in opposite directions.

This is a **testable candidate**, not yet an empirical conclusion.

If P1 is true but P2/P3 fail, the outcome is local retention without established connectivity costs. If P2 and P3 both hold across independent systems, the result extends island biogeography from static area/isolation into dynamic **source-capacity-mediated immigration**.

Potential species extension: rock/ice-free-terrain nesters (Adélie, chinstrap, gentoo) in a common terrestrial-patch framework; emperor penguins on changing landfast sea ice require a separate outcome and observation source, not a pooled 'fourth replicate' of the same estimator.

## Relation to active work

- PR #189 frozen *Ecology* Article remains unchanged.
- PR #190 is a distinct individual re-entry audit and cannot substitute for source-to-recipient settlement.
- This document does not assert that a new significance test ran, that a receiver-side dataset was accessed, or that the universal hypothesis passed.
