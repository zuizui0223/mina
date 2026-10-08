# Edmonson Point — continental (non-island) landscape-change comparator

**2026-10-08 | Post-publication, previously exposed outcomes, descriptive only**  
**Not** a replication of the island-to-island source-retention hypothesis, no movement inferred.

## Purpose and prior-art veto

An archipelago-specific explanation must be distinguished from ordinary **within-breeding-area option switching**. Kim et al. (published 11 February 2026) documented a physical nesting-substrate shock on **Edmonson Point**, a mainland Victoria Land **headland** rather than a physical island. This is a valuable *non-island process comparator* because it shows that coarse aggregate stability, local nest losses, and gains elsewhere can co-occur without invoking movement across an island boundary. The nest-redistribution phenomenon was **already reported in that paper**; do not claim to have discovered it.

Source:
- Kim et al. 2026 (open-access), doi:10.1002/jgo2.70001, https://rsnz.onlinelibrary.wiley.com/doi/full/10.1002/jgo2.70001
- SCAR Antarctic Gazetteer, Edmonson Point: https://data.aad.gov.au/aadc/gaz/scar/display_name.cfm?gaz_id=139782
- The independent 2023 ASPA 165 management plan describes Adélie demographic monitoring and site rearrangement: https://documents.ats.aq/recatt/att749_e.pdf

## Independent exposure

An approximately 1.95-m high-ocean-wave event on 15 February 2019 scoured old guano nesting substrate, left grounded icebergs and changed the 2019/20 colony configuration. The paper compared helicopter photographs taken in late incubation on 4 December 2017 and 12 December 2019. The flood followed the 2018/19 breeding season's chick fledging; the 2019/20 nest pattern is a **lagged substrate response**, not known direct chick mortality during the wave itself.

## Published data and reproducible arithmetic

| Breeding season | Coastal nests | Other higher-ground nests | Total |
|---|---:|---:|---:|
| 2017/18 | 1,971 | 576 | 2,547 |
| 2019/20 | 1,863 | 643 | 2,506 |
| Absolute change | −108 | +67 | −41 |
| Relative change using **2017/18 denominator** | **−5.48%** | **+11.63%** | **−1.61%** |

Kim et al. Table 1 gives **+10.42%** for the higher-ground row, but 67/576 = **11.63194%**, while 67/643 = **10.41991%**. The published figure matches the *final-year* denominator only for that column. The primary 2017/18 denominator is used for **all** three comparable percentage changes in this audit. The paper's raw values and main ecological interpretation remain intact.

More descriptive consequences:
- higher-ground **net gain** = 67 nests, coastal **net loss** = 108, ratio = **62.04%**, but **not** a measurement of bird transfer;
- coastal proportion = **77.385%** → **74.342%**, shifting **−3.04 percentage points**;
- inverse-Simpson effective monitored zone number = **1.53849** → **1.61681** (**+5.09%**) across a *two-bin non-island aggregation*;
- total nest count **−1.61%** while subzone counts change in opposite directions. The spatial structure can change more than total abundance; this is a known resilience point, not a new universal scaling relationship.

## Mechanism versus measurement, and why it is useful as a control

The **published study** maps new/abandoned nest patches and documents habitat loss; its authors name nest relocation, breeding absence, nest loss to inundation and predators, or marine forcing of hillside gains as alternative explanations. It does **not** track individuals from the coastal to higher subcolony. Therefore “62% of coastal birds moved uphill” is forbidden even though 67/108 = 62%.

The lower-level explanation — changing local nesting options can reweight subcolonies in a breeding system **without a true island boundary** — is empirically consistent with this observed habitat shock.

**New hypothesis, not yet observed:** if island boundaries add any *extra* threshold/cost to redistribution, matched movement data should show a difference in settlement odds among equally accessible, ecologically similar nesting alternatives **within an island/contiguous headland** versus **on a separate island**, conditional on natal fidelity, flightless transit/sea route distance, habitat, cohort supply, year and detection. Edmonson alone contains no cross-boundary comparison and cannot estimate such a parameter.

## Hierarchical island-biogeography comparison: what is required

- **Within site:** Edmonson coastal versus high ground, with a known exogenous beach-substrate change; descriptive count contrasts only.
- **Within physical island:** Beaufort main southwest versus north beach; north establishment documented by 1995, but no independent option suitability time series and no origin-specific first breeding.
- **Across islands:** Beaufort versus Ross: bidirectional marked **sightings** occur; origin-specific first breeding/export/rescue are not observed from the reviewed materials.

These are **not** mutually exchangeable study units or three inferential replicates. The nested spatial hypothesis would require direct adult/prebreeder movement or first-breeding choice at all levels, independent capacity, and enough independent island networks.

## Stop rule

Do not retrofit the 2026 Edmonson published effect as prospective confirmation of PR #192. Do not call Edmonson an offshore island, equate apparent nest trade-offs with the same birds moving, or interpret a +5.09% E2 change as increased metapopulation rescue. This contrast documents what local nesting geometry **alone** can plausibly do and narrows the search for an island-boundary-specific effect.

## Reproduce

`python scripts/audit_edmonson_mainland_counterexample.py`

`python -m pytest -q tests/test_edmonson_mainland_counterexample.py`
