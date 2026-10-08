# A reported colony is not necessarily a newly founded colony: published site-history crosswalk

**2026-10-08 | Retrospective biological observations, Fretwell (2024), DOI:10.1017/S0954102023000329**  
**Status:** a genuine published site×year support audit, not a new satellite extraction, dispersal/colonization causal test or novel published effect. No new Dryad/BAS biological rows opened. The prospective PR #195 ecological outcome contract remains unchanged.

## Actual records extracted from the primary published observations

Fretwell (2024) reported **four previously unreported emperor breeding locations**. Reading the site's described original Sentinel-2/VHR year rather than the year it entered the known-colony inventory produces a strikingly different interpretation:

| Reported in 2024 | First independently cited positive year | Other directly supported years | Negative survey before first positive? | Biological interpretation |
|---|---|---|---|---|
| **Lazarev North** | 2018 | 2019, 2020, 2021, 2022 (at least one positive image/year) | Not established | Repeated northern-site presence; a relocation from old Lazarev is *plausible* not origin-tagged |
| **Verleger Point** | 2018 | 2019–2022, present in each annual Sentinel-2 survey | Not established | Previously existing colony newly reported in inventory |
| **Vanhoeffen** | 2018 | 2019–2022, present in each annual Sentinel-2 survey | Not established | Previously overlooked offshore colony (30–40 km from ice edge); 2022 count estimate ~5,000 but provisional |
| **Gipps Ice Rise** | **2016** | Specific all-year sequence not verified from this paper | Not established | Existing ~200-pair site from October 2016 VHR; 2021 calving destroyed its sheltered ice creek, shifting visibility/physical location |

**Mechanical cross-study facts**: **4/4** newly reported sites already had published original imagery prior to the *2024 report date*; **3/4** have expressly documented positive sightings in *each year from 2018 through 2022*; across these four *literal supported observations* at least **16 site–years** are explicitly supported (5 + 5 + 5 + 1). **0/4** have, in the reviewed publication, a pre-first-positive sequence of independent, repeated, high-coverage biological *surveyed zero* observations establishing *new formation*. These zero supports are a statement about evidence **reported in the paper**, not zero true ecological colonizations or an estimate of their rate. The sample was selected by the 2024 article, not randomly.

### Missingness and the biological clock

- Lazarev old site: original nesting site was last seen by **2014** and absent from subsequent surveyed imagery in the author narrative; first Lazarev North positive **2018**, and north site repeatedly confirmed through 2022. **No banded animals** link the two. It cannot be interpreted as an island-origin/migration event or a true previously vacant destination proven in 2017.
- Umbeashi: had been labeled '**no longer extant**' in the 2019 catalogue, but was newly seen in **2021 and 2022**. This shows *catalogue extinction status was reversible*, but no verified whole-colony all-season absence in 2019 or 2020 is provided. **Nonextant in a catalogue ≠ complete biological extinction.** Umbeashi is not one of the four new sites.
- Gipps: the existence of ~200 penguin pairs **five years before the 2021 calving** directly rules out the narrative that the calving *founded* this colony. The disturbance altered location/visibility, which can create a false time-of-first-colonization if one uses newly visible guano as the first biological event. This inference of visibility and movement **is already in the 2024 paper**.

## Why this matters to PR #195

The initial route hypothesized that *physically suitable unoccupied* fast-ice patches might become occupied after catastrophic 2022–2023 sea-ice failure. Its feasibility depends on three independent state labels in each original satellite scene:
1. **Occupied**: a colony/subgroup is positively detected, but attendance is not reproductive success.
2. **True surveyed empty**: relevant habitat is imaged at the right reproductive dates, suitable for detection, with a documented negative and sufficient repeated coverage.
3. **Unknown**: not inspected, cloudy, unsuitable season/resolution, changing ice/site polygon, or a paper merely states 'not extant'.

None of the four 2024 reported sites satisfies **2** before its first positive observation based on what the paper reports. **Counting them as four demonstrated de novo post-shock colonizations would be wrong.**

This is *not* an argument that emperors cannot create new colonies. Fretwell et al. (2026, `10.1038/s42003-026-10961-y`) report **two recently formed colonies**, notably Case Island region and NW Stancomb–Wills, potentially associated with breakup or immigrant supply. That result itself is prior art. However, accessible passages do not yet establish how many earlier annual negative scenes were searched at those exact georeferenced new patches, or whether those sites were newly founded rather than newly observed/expanded. Their stronger "recently formed" interpretation cannot be validated as a prospectively new causal endpoint by assuming missing history is an observed zero.

## Precise outcome and causal stop rules

- **A newly discovered site can be old, and a locally extinct catalogue site can later reappear.** Published examples exist; we documented their exact years without creating new effects.
- **An effect of a 2021 or 2022 fast-ice shock on settlement is not identified** by first detection of a previously unseen guano stain. Need independent pre-event presence history and contemporaneous physically traversable site options.
- Distinguish previously **occupied receiving colony** (Dawson–Lambton) from previously **truly surveyed unoccupied option** (none yet verified here).
- Do not assign immigration origin or offspring production from guano/pixel area. Two or more years of visible guano are **repeated apparent occupancy**, not an individual recruitment success estimate.
- A 2026 paper calling two sites 'recently formed' is evidence of **published author classification**, not a pass on our strict repeated-zero + reproductive-establishment gate until underlying image chronology is checked.
- Never treat **2019 reported nonextant** as a formally verified whole-season extinction for Umbeashi.

**Decision:** prospective mechanism route remains **HOLD** for newly available vacant refuge, despite positive published evidence of repeated colony occupation, reappearance and post-iceberg exposure. The potentially new causal contrast remains *truly surveyed vacant sites vs already-occupied receiving colonies* after external shocks, using independently measured before-move access and certified breeding outcomes.

## Reproduce

`python scripts/audit_emperor_discovery_vs_formation_v1.py`

`python -m pytest -q tests/test_emperor_discovery_vs_formation_v1.py`

The source-coded evidence file `external/EMPEROR_FRETWELL_2024_SITE_DETECTION_EVIDENCE_V1.json` quotes only dated presence/absence classifications in the **published article**, not a new digital-image inspection. Its summary result is in `results/EMPEROR_DISCOVERY_VS_FORMATION_AUDIT_V1.json`.

## Primary source

- Fretwell P (2024). *Four unreported emperor penguin colonies discovered by satellite.* *Antarctic Science* 36:277–279. https://doi.org/10.1017/S0954102023000329
- Fretwell PT et al. (2026). *Dynamic emperor penguin colonies.* *Communications Biology*. https://doi.org/10.1038/s42003-026-10961-y
