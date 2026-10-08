# Ross–Beaufort island dispersal: prior-art, movement-stage and access-confounding audit v5

**2026-10-08 — published-data evidence audit for PR #192.** Independent prior literature is *not* an untouched test. No USAP-DC rows opened; no new confirmatory ecology endpoint; frozen Ecology PR #189 and prospecting protocol PR #142 unchanged.

## What has become observationally stronger

Dugger et al. (2010, PNAS, doi:10.1073/pnas.1000623107) analyzed 2,681 individual **previously observed breeders** on Ross Island during 1996–2007, incorporating observation/detection models for the three Ross study colonies. Their published **Table 3** directly lists the former breeding location and later **Beaufort resighting**:

| Prior breeding site | Individuals previously observed breeding | Subsequently detected on Beaufort |
|---|---:|---:|
| Cape Royds | 475 | **3** |
| Cape Bird | 970 | **1** |
| Cape Crozier | 1,236 | **1** |
| **Total** | **2,681** | **5** |

The publication itself says that 3/475 formerly breeding Royds birds emigrated to Beaufort versus ~0.1% at each of Bird and Crozier, and warns the true movement numbers may be higher because Beaufort was searched **infrequently**. These are *minimum documented cross-island adult movement observations*, not an unbiased population-level emigration rate. The table's outcome is **subsequently resighted at another location**, *not first breeding on Beaufort*, and it does not distinguish **Beaufort north shore vs Cadwalader southwest**. In this analysis adults were included after they had bred at least once at their original Ross colony; they cannot be repurposed as a cohort of first-time breeders from Ross on Beaufort.

> **An asymmetric, real prior-breeder Ross → Beaufort movement pathway exists in the literature**. It was already established in 2010, not a discovery from the present audit.

## Cross-island versus colony-level movement: prebreeder and breeder are different estimands

Shepherd et al. (2005, PNAS, doi:10.1073/pnas.0502281102) already describe an **external, exogenous travel-route perturbation**: giant B-15A/C-16 icebergs changed the spring approach to colonies. In published 2000/01 pre-iceberg vs 2001/02 with-iceberg descriptions:

- Bird-banded young penguins **seen** in the study: 348 vs 160; *among those seen*, visitors to Crozier: **2** vs **at least 7**.
- These observations show a change in **documented prebreeder visitation** during a known route obstruction. The paper itself interpreted this as route diversion and noted uncertainty over some other movement contrasts.
- None of these visits identifies confirmed destination breeding, natal dispersal probability or individual sea-crossing path. They also concern **Ross-to-Ross movements**, not Beaufort's north shore.

Dugger et al. (2010) subsequently fitted a multistate model to Ross **adult breeders**, finding the best movement model (84% QAICc weight) included colony and iceberg presence; the published abstract reports movement increasing particularly from small Cape Royds in adverse conditions, up to ~3.5%, whereas movement in less disturbed years was generally <1%.

**Consequent hard veto:** the published post-2005 Beaufort-chick-banded **Ross visitation ratio** decrease (LaRue et al. 2013) cannot be attributed to source-island nest-option expansion without addressing changing regional sea-ice/iceberg movement routes, *age/cohort composition* and unequal Beaufort vs Ross search effort.

### Do not combine incompatible denominators

| Directional evidence | Source marks/stage | Event recorded | Denominator | Main limit |
|---|---|---|---|---|
| Ross → Beaufort (Dugger 2010) | previously observed Ross **breeders** | later detected Beaufort, n=5 | 2,681 former Ross breeders *across 1996–2007* | Beaufort effort sparse; no north-beach destination or first Beaufort breeding |
| Beaufort → Ross (LaRue 2013) | Beaufort **chick-banded cohorts** | annual visiting any Ross colony | estimated still-alive Beaufort marked cohort by age and year | visits not first breeding; depends on borrowed survival & observing windows |
| Ross Bird → Ross Crozier (Shepherd 2005) | young Bird-banded birds | visits among observed prebreeders before/after iceberg | within-year n of re-encountered Bird banded birds | conditional on who was seen; stage differs |

**It is invalid to compare 5/2681 with LaRue's ~3% as if they were opposing contemporaneous directional transition probabilities**. Doing so would create a spurious “reversal of migration direction” story even if both numbers were measured perfectly.

## Quantitative identification bottleneck in the habitat exposure

The LaRue et al. (2013) main-colony habitat/breeding-pair relationship used **n=3 overlapping image/count dates**, from which a positive area–count association was reported. This is **not three independent island-capacity shocks**; the mapped guano-envelope minus snow is also partly an outcome of penguin occupation. For the contemporaneous 2005→2010 comparison the measured main-colony area grew only **1.12%** while its nest counts grew **21.83%**; the earlier multi-decade ~71% habitat change cannot be assigned wholly to that period. The **northern beach** settlement-choice habitat was not independently measured within those main-colony polygons. Accordingly, neither three paired exposure dates nor the 2005 onward visit-rate series provides a defensible temporal mediation fit of `K_north -> first breeding destination`.

An **access-only rival** has stronger already-published observational support than the proposed new capacity effect because the 2010 multistate movement models compared distinct iceberg-present versus iceberg-absent years with explicitly estimated Ross colony resighting rates. Nevertheless, even those fitted *Ross-to-Ross breeder* movements are **not** direct identification of the Beaufort north-beach founding mechanism.

## The strongest rival causal explanations, now with stronger evidence hierarchy

**H_A, path-access forcing.** Variation in iceberg and sea-ice geometry shifts foraging/migration connectivity and intercolony visit/settlement probabilities, even at constant usable nesting area. **Published observational support exists** for stage-specific change at Ross; not a new claim.

**H_K, island nest-option capture.** Independent increase/activation in Beaufort north-beach *nesting options* changes the odds that a locally available prebreeder establishes on the same island rather than crosses to Ross, conditional on exposure to H_A and cohort demography. **Hypothesis only**, no independent annual north-option series or destination-linked first-breeding data.

**H_C, cohort / detectability mixture.** Apparent rate changes arise from the marked-at-risk denominator, unbanded years, juvenile age mix and uneven north/beaufort searches. **Plausible observation-process rival; not fitted**.

**H_F, social/natal fidelity and settlement opportunity.** Recruits preferentially use established habitat, responding to social availability rather than geometric nesting capacity, with possible direction changes after founding. Known site-fidelity/colonial settlement theory is prior art; **not observed specifically for north-beach first-breeders**.

A published short-term iceberg perturbation is especially damaging to causal attribution from a **single** ice-retreat-versus-visit-rate time series, because access and nesting context change over similar years without an independent instrument or adequate matched unexposed networks.

## Testing hierarchy and decisive support requirements

- Existing **Ross island three-colony** time series: 78/78 positive occupancy years; cannot test receiver *reoccupation*. Can test demographic changes in established colonies only if origin-specific confirmed recruits/detection available.
- Existing **Beaufort subcolony** series: 1994/95 2 pairs → 2005/06 525 pairs → 2013/14 989 pairs; cannot infer source origins or settlement choice.
- **First genuine causal contrast** would estimate a confirmed first-breeding destination `D_{individual, season}` among Beaufort main, Beaufort north, and Ross colonies, together with independent pre-decision date north habitat options, source cohort, arrival/access geometry, and site-year detection. 
- Compare prospectors of similar age/natal source/year who actually had both alternatives available, and include known variations in iceberg corridors independently of north beach capacity. Avoid conditioning away the *mediated* capacity effect by using descendant/current density as a routine "control".
- Dataset 601444 currently has public metadata for destination colonies (CROZ/ROYD/BIRD/BEAU), not a verified north/south split at BEAU; the separate real-row access route remains gated by USAP-DC official API key in PR #142.
- Because 2005 and 2008 Beaufort chick-banding cohorts are missing and the island was rarely searched, failed destination support **ends** the first-breeding counterfactual; it is not rescued by classifying nonobservations as nonbreeding or using sighting visits as settlers.

## Scientific decision

**Novelty gate:** past breeder dispersal, iceberg-mediated travel diversion, age-dependent prospecting, and first colonization requiring immigrant input are all *prior art*. A Ross–Beaufort linkage cannot be promoted merely by recovering these historic movements.

**Causal data gate:** no new positive source-option → altered cross-boundary first-breeding *effect*. No one-way source/sink assignment justified. PR #192 remains a pre-outcome feasibility and prior-art program. An original ecology result requires a truly independent successful first-breeding choice panel or a different instrumented archipelago system.

## Key sources

- Dugger et al. 2010 original Table 3 / methods: https://penguinscience.com/reprints/Dugger_Ainley_2010_survival.pdf
- Shepherd et al. 2005: https://doi.org/10.1073/pnas.0502281102
- LaRue et al. 2013: https://doi.org/10.1371/journal.pone.0060568
- Dugger et al. 2026: https://doi.org/10.3389/fevo.2026.1868960
- USAP resighting: https://doi.org/10.15784/601444
- Banding: https://doi.org/10.15784/601443
- ASPA 105 management plan: https://www.ats.aq/devAS/Meetings/Measure/715
