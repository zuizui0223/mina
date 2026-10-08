# Source-capacity versus emigrant export: Beaufort–Ross **structural falsification audit v2**

**Date:** 2026-10-08  
**Evidence status:** previously published observations and previously frozen Ross census only. **NO new individual resight records read, NO inferential effect, NO confirmation of source-mediated rescue.**  
**Related:** PR #192 (this branch); PR #189 (scientifically frozen; untouched); PR #142 / Issue #141 (separate untouched resight-choice protocol, official USAP-DC API-key dependency).

## Decision first

**The Ross–Beaufort system cannot test the proposed receiver-colony reoccupation/rescue endpoint at the existing three-colony or six-census-component grain.** In the frozen 1985–2012 Ross panel, all 3 colony counts are positive in each of 26 observed years (78/78 occupied, zero 0→positive reoccupation transitions). All six census components are likewise positive in those years (156/156 positive). This is an *eligibility failure for an observed reoccupation endpoint*, not a finding of absent immigrant demographic contributions and not a statement about unobserved fine-scale nest patches.

The 2013 Beaufort **emigration rate** is a ratio of Beaufort-chick-banded individuals **seen visiting** Royds/Bird/Crozier over modeled Beaufort-band cohort members potentially alive; this is not confirmed first-breeding settlement, total adult emigration, or absolute exported settlers. **P2 and P3 remain not identified.**

## Published Beaufort audit (LaRue et al. 2013, DOI 10.1371/journal.pone.0060568)

From published Table 1, **main Beaufort colony only**, *not the newly founded north-shore subcolony or the entire island*:

| Year | Published guano-envelope-minus-snow 'available area' (m²) | Main-colony occupied breeding territories/pairs | Implied density (pairs/m²) |
|---|---:|---:|---:|
| 1958 | 75,670.3 | NA | NA |
| 1983 | 107,571.2 | 34,588 | 0.3215 |
| 1993 | 104,637.3 | NA | NA |
| 2005 | 127,603.4 | 52,335 | 0.4101 |
| 2010 | 129,029.5 | 63,760 | 0.4942 |

Arithmetic derived from **published** numbers:
- main published area 1983→2005: **+18.6223%**;
- main published area 2005→2010: **+1.1176%**, an absolute **1,426.1 m²**;
- main breeding count 2005→2010: **+21.8305%**;
- mean breeding pairs per published main-area unit 2005→2010: **+20.4840%**, rather than decreasing.

Thus a simple claim that **contemporaneously falling mean crowding** caused post-2005 Beaufort-to-Ross visit-rate decline is contradicted by the *published mean density proxy*. This is NOT a test of individual nest spacing, territory quality, available unused microhabitats, or true competition: an independent new north-shore subcolony was also founded in 2004 and grew 460→957 pairs by 2010.

The 2013 paper reports 71% long-term increase in *main* mapped area (1958→2010) and 543 m glacier-front retreat (1983→2010). These longer-term transformations cannot be relabeled **2005→2010 contemporaneous exposure**. A mechanistic analysis must separately measure cumulative/recently exposed bare ground, snow cover and ability to occupy the north-shore patch.

## Two measurement errors that prevent a naïve causal claim

### A. The published habitat index is partially an **outcome**, not a purely exogenous capacity variable

LaRue et al. mapped current-season guano-stain envelope minus local snow/ice, rather than all physically suitable but unoccupied flat/ice-free terrain. By construction, colony expansion affects the mapped 'available area'. A regression of visit rate on this index alone therefore mixes physical ice retreat, snow exposure, **realized occupation**, and perhaps changes in observation.

Needed alternative exposure `K_geo`: a fixed-buffer geomorphic candidate nest substrate (slope/rock/ice-free state) measured without using contemporary penguin-guano occupancy. Treat north-shore and main-colony footprints separately. The glacier-front 543m long-term retreat is independent physical evidence but not a temporally dense annual capacity covariate.

**Causal adjustment caution:** current density = breeding pair count / measured habitat index is downstream of capacity *and* population responses. Controlling for it mechanically can block mediation or introduce conditioning bias. Define total capacity effect first; use **pre-change** crowding to stratify or a separately identified controlled-direct-effect design if necessary.

### B. The published 'emigration' index is **seen visiting Ross**, not settling there

For year t, a schematic accounting is

`q_visit(t) = D_Ross(t) / sum_c M_Beaufort(c) × S_hat(c,t)`

where D is a count of Beaufort-origin unique visitors seen at Ross, M is age-cohort marking, and S_hat is transferred age-specific survival. This is a study-specific observed-visit quantity. The paper did not estimate robust Beaufort-native capture/resighting probabilities, owing to limited access. Original marked cohorts included ~400 Beaufort chicks per year 1999–2010 **except 2005 and 2008**. Missing birth cohorts alter the age composition in subsequent observation years. An age-standardized first-breeding study must account for these design gaps.

A person can be seen as a prebreeder at another island and later first breed at Beaufort; **visitor ≠ emigrant breeder**. Conversely, non-observation at Ross cannot distinguish Beaufort residence, survival, temporary nonbreeding, or emigration elsewhere. Even a resighted Ross breeder does not by itself give its total-population source expansion factor without a known source sampling fraction.

Absolute `F_settler = R_eligible × p_first_breeding_at_receiver` is a DIFFERENT estimand from D_Ross and its published fraction. The data currently reported do not identify R_eligible or p_first_breeding_at_receiver.

**Illustrative algebra only (NOT an estimate of actual emigrants):** if the source eligible cohort had increased by exactly the *breeding-pair count* ratio 63,760/52,335=1.2183, then absolute exports would fall only if the true destination-settlement probability ratio were **below 0.8208**, i.e., a decline exceeding **17.92%**. Because source cohort and main-colony count are not equivalent, 0.8208 is a pedagogic threshold, not an inferred ecological threshold.

## Recipient support result — **hard STOP for P3 reoccupation in this panel**

Frozen Ross 1985–2012 six-component aerial count CSV from PR #189, independently assembled from Lyver et al. 2014:

- **26 observation years**; 3 named physical colonies (Royds, Bird, Crozier) × 26 = **78 occupied colony-years, zero absent years**.
- Corresponding six monitored components × 26 = **156 positive component-years**, no observed local zero.
- Min among these years: Royds **1,367**, Bird **22,816**, Crozier **67,114** breeding pairs.

Therefore a `zero→positive` recipient-colony event cannot occur in this panel. Nor can a regression on these outcomes establish prevention of a **counterfactual** extinction absent immigrants. A separate properly surveyed set of smaller, extinction-prone receiving sites and exposure to **identified origin-specific settlers** would be needed.

Do not merge the fine-scale Palmer/Signy extinction spells with Beaufort/Ross individual origins: those are different metapopulation networks and lack matching origin data.

## Alternative mechanism that needs serious treatment

The **end of the B-15A/C-16 iceberg period around winter 2005** (Lyver et al. 2014), also matches the approximate calendar point of maximum Beaufort-origin Ross sightings. This could alter the *physical corridor/access* or dispersal/search behavior separately from glacier retreat. Frozen tests must condition on external sea-ice/iceberg state and cohort age/effort before attributing the decline to source nesting capacity.

The **within-island alternative** is testable only if Beaufort individual histories distinguish (1) first breeding main colony, (2) first breeding new north-shore subcolony, (3) first breeding Ross, and document effort in all three. The public header currently known in PR #142 uses `BEAU` as a colony; it does not yet demonstrate within-Beaufort subcolony resolution, and Beaufort search effort is known to be sparse.

### Prior-art veto: recipient immigration itself is already known

Herman & Lynch (2022, Ornithological Applications, DOI 10.1093/ornithapp/duac014) inferred substantial, sustained immigration as necessary to reproduce the growth of **four newly founded gentoo colonies** using age-structured ABC and published counts. This is valuable independent recipient-side evidence, but neither banded **donor origin** nor changing donor habitat capacity is identified. It **cannot** validate a donor-capacity → recipient rescue causal pathway. Do not sell "immigration matters for new colonies" as a discovery.

## Revised claims ladder

1. **Existing replicated/published observation:** physical nesting habitat has expanded on Beaufort, and a *Beaufort-origin marked-cohort Ross visitation ratio* declined after 2005. Both published already.
2. **New testable H1:** independent, exogenous source nesting-option changes alter *age-standardized first-breeding destination* among known-natal individuals, not merely visit counts. **Blocked on support, detection and mapped option dates.**
3. **New testable H2:** decreases in probability overwhelm changes in actual recruit production so **absolute settled emigrant flux falls**. **Not identifiable with current published aggregates**.
4. **New testable H3:** an **independent** receiving-island system with verified, repeated absences and identified donor origins shows reduced reoccupation/demographic rescue after donor-option release. **STRUCTURAL FAIL in Ross three-colony/six-component 1985–2012 panel**, no other eligible receiving system yet established.

## Feasibility gate / single next action

Preserve PR #142's official USAP-DC first-breeding-choice execution lock. Do not access resight rows using another workflow or alternate preview. A separate **header-only source support audit** (not a reuse of PR #142's preregistration) must resolve:

- whether Beaufort `Eggs/Chicks` breeder status and **first breeding season** are distinguishable at Ross and Beaufort;
- whether Beaufort annual search effort and colony-specific detection can support relative probabilities;
- whether Beaufort main/new spatial subcolony labels exist;
- whether mark cohorts/source sampling fractions and age/year structure support annual absolute export;
- whether an independently reconstructed capacity option polygon has **dates before each settlement season**;
- whether an independent receiver network has explicitly surveyed 0→positive events and known-origin immigrants.

**If not:** terminate the source-capacity-causes-rescue claim, retain only the published Beaufort vignette, and prioritize a standalone island-colonization study on independent recipient systems **without inventing donor origins**.

## References / canonical sources

- LaRue et al. 2013: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0060568
- Lyver et al. 2014: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0091188
- Herman & Lynch 2022: https://doi.org/10.1093/ornithapp/duac014
- USAP-DC resights and banding: https://www.usap-dc.org/view/dataset/601444 ; https://www.usap-dc.org/view/dataset/601443
- Existing PR #189 frozen counts: `external/ross_island_v2_frozen_counts.csv` at `analysis/ross-sea-expansion-intensification-support-v1`.
