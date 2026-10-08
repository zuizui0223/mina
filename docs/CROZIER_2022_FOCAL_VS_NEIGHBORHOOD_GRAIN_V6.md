# V6 — focal site reuse versus neighborhood colonization are different outcomes

2026-10-08; source check of the 2023 release of Cox et al. (2024, Polar Biology, DOI 10.1007/s00300-024-03246-9). All animal source results from already-published observations, post-outcome exploratory; this is not a new causal test. Frozen Ecology PR189 unchanged.

## Why single-nest identity is not enough

The prior paper reports four nascent subcolonies around sites of former solitary nesters, and original actively breeding solo sites reoccupied in 2022. However, **occupation of the exact marked 2021 focal nest** is not identical to **new/continued nesting activity within ~1–3 m of the former nest**.

Using the exact 50 source locations and the existing 136 follow-up event rows, with **2022-10-01 to 2023-03-31 only**, never silently incorporating 27 author-labelled December 2023 observations in the August 2023 release:

- 2021 original nonbreeders: **13** source sites. **3/13** sites (solo10, solo19, solo36) have a positive 2022 numeric adjacent-neighbor count; **zero** has a clearly verified focal-site active/occupied source status in the conservative source screen.
- 2021 original breeders: **37** source sites (includes the study's poorly observed solo27); **7/37** have at least one positive observed adjacent-neighbor count; **20/37** have a plausible focal-site occupation in the conservative screen. These are coarse source status checks, **not comparable to the authors' 20/41 analyzed reoccupancy denominator**.
- One particularly clear biological unit distinction: source **solo36** on 2022-12-05 records the original marked focal nest as **MT (empty)** while reporting a neighbor about **1.5 m** away described as incubating an uncertain egg count (**INC9**). This is positive *adjacent activity with focal vacancy*, not independently verified new founded and successful breeding.
- The other two originally nonbreeding sites are labeled **INC?** (uncertain) at the focal site, with two nests between older solo nest markers at solo10 and five occupied-looking territories near solo19. They do not establish absence or current occupation of the precise focal nest, nor whose penguins are involved.

An adjacent nest count is **not** the site-year first-occupancy of a new island or even an independently uniquely identified neighboring breeding pair; no individual parent/chick identities, newcomer origins, nesting success or independently dated within-colony ice/habitat change are provided. Even the presence of surrounding nests at formerly nonbreeding marks does NOT prove that the earlier unsuccessful or nonbreeding pioneer attracted them. Original terrain suitability, prior guano/pebbles and later geography can cause both measurements.

## New theoretical discriminant, not an established effect

The nested states should be tracked separately:

1. exact previous nest location: reused/not confirmed;
2. neighborhood ring: old local group density, new confirmed nesting pairs and date-specific occupancy;
3. biological individual: breeding attempts and actual survival/offspring at both the original and the ring;
4. across-year origin: previously banded focal adults, tagged chicks or true outside immigrants.

A *spatial legacy without exact-site persistence* is ecologically conceivable: an early unsuccessful pioneer could leave local physical/social cues subsequently exploited by neighbors while the original nest stays vacant. But those cues (guano, rocks, abandoned nest) and independent immigration/social attraction have not been directly tested at these records. The published four nascent subcolonies already make the generic concept prior art.

This is potentially relevant to a stronger island-biogeographic question: when habitat is newly made available, do isolated failures trigger **nearby** subsequent nesting despite **failure of the focal site itself**? A modern independent event panel would require new physical habitat, repeated markable first founders, social cue exposure, adjacent-patch settlement, and stage-specific reproductive success. The current 3 source examples only motivate, and do NOT support as a causal finding, that proposition.

Code and receipt: contracts/CROZIER_FOCAL_SITE_VS_NEIGHBORHOOD_RECRUITMENT_V1.json; scripts/audit_crozier_focal_vs_adjacent_nesting_v1.py; tests/test_crozier_focal_vs_adjacent_nesting_v1.py; .github/workflows/crozier-focal-site-adjacent-2022-v1.yml.

**Decision:** Source nest-vs-neighborhood measurement grain is promising as a *design clarification*, but no new causal or general island law is justified. Ecology PR189 frozen, Ledda coordinate/source audit PR195 separate.
