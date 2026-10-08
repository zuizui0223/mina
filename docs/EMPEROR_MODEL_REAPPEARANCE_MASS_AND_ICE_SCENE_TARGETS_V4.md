# Emperor penguin apparent recovery: posterior allocation versus verified breeding-site reuse

**2026-10-08 | Previously published observations and outputs only. This is new arithmetic/source triangulation, NOT a new penguin migration or causal rescue discovery.**

## Result 1: How much published model growth comes from 'zero to positive' nodes?

From LaRue et al. 2024, the author-archived frozen **50 colonies × 2009–2018** posterior `N_mean` table, we summed **positive changes within every colony for each of nine consecutive year pairs**, then partitioned whether that colony had *model posterior mean zero* in the preceding year.

| Measure across nine annual transitions | Published-model aggregate |
|---|---:|
| Sum of within-colony positive changes (gross gain) | **129,460.42** |
| Sum of within-colony negative changes (gross loss) | **152,338.79** |
| 'Zero previous mean → positive next mean': 9 episodes | **10,120.61** = **7.8175% of gross gain** |
| Of these, original satellite raw status `no→yes` and next image basic date/area screen passes: 5 episodes | **6,795.00** = **5.2487% of gross gain** |
| Raw `no→yes` but following image OUTSIDE author fit date/area screen: 1 episode (RUPE) | **2,204.00** = **1.7024%** |
| Raw source does NOT document `no→yes`: 3 episodes | **1,121.61** = **0.8664%** |

**Very important denominator:** 129,460 and 10,121 are sums of **published model posterior means' repeated annual increments**. They are *not* numbers of distinct individual penguins, immigrant arrivals, birds saved, or total reproductive output. Multiple increases can affect the same individuals over several years. The 5 basic-screen matches may still have unreviewed original image removal flags, and `bpresent=no` does not distinguish absent birds from absent fast ice. These numbers do **not** estimate false-colonization rate or ecological resilience.

**Event concentration:** in 2010→2011 the 50 model colonies had **16,337.14** total gross positive changes, and **3,865.03** were assigned to `MERT` flipping from model zero to positive: **23.66%** of that year's modeled gross increase. Mertz had a documented **2010 calving** event, so interpreting that increase as arrival of 3,865 novel breeders would be biologically unjustified. Underlying moving ice-front dynamics, sensor coverage, physical platform availability and attendance all need consideration. The calving mechanism itself was previously described in Antarctic research.

**Source-matching finding:** Among the 9 model episodes, **6 raw `no→yes`**, but one (RUPE 2016→2017) was seen only **11 December 2017**, outside the original fitted September–November window. Five have following images inside the basic author date/area conditions; 3 lack an actual raw `no→yes` pair (AMUN 2012→2013 `no→NA`; LAZA 2011→2012 `yes→yes`; LEDD 2014→2015 `no→no` with late November exclusion). **All nine fail** the independent `physically present ice + repeated surveyed negative + new confirmed breeding` required to say a real unused refuge was newly colonized.

This is consistent with the public 2024 JAGS model's year-independent `z_occ[s,t] ~ dbern(prob_occ)` plus observation/temporal abundance uncertainty. Its inferential purpose was a **global abundance index**, not to infer natal dispersal or physically accessible but unoccupied nesting sites. Do not claim model fitting was incorrect.

## Result 2: five named, dated candidates for independent physical-ice and breeding verification

This is the **maximum honest next empirical step** from the original 2009–2018 raw-image evidence. The five direct `no→yes` source pairs that have following basic date/area eligibility are:

| Original colony | Original prior `no` satellite image | Following `yes` satellite image | Author site-centroid latitude, longitude |
|---|---|---|---|
| Amundsen Bay (`AMUN`) | 2010-10-08 | 2011-09-27 | −66.78, 50.55 |
| Ledda Bay (`LEDD`) | 2009-10-27 | 2010-10-08 | −74.228, −130.784 |
| Ledda Bay (`LEDD`) | 2012-10-22 | 2013-11-30 | −74.228, −130.784 |
| Mertz Glacier (`MERT`) | 2010-10-02 | 2011-10-11 | −67.23, 145.516 |
| Umbeashi (`UMBE`) | 2012-09-27 | 2013-10-12 | −68.05, 43.01 |

These are **author-archive colony centroids**, not accurately mapped ice-ramp polygons. Public author `colony_attributes.csv`, pin `b27e18d5746a03279661748cbb427fa76183cd67`, plus original image dates, pin `a964360e2cc9bc6303199e0971a4e7d40f793752`. This short list selects by **previously exposed original source evidence**, so it is **retrospective prioritization**, *not* prospective confirmatory replication.

### Required external observation before a biological classification

For each paired date, independently inspect a sufficiently resolved and temporally preceding sea-ice image at the **actual nest patch**, not merely the rounded colony coordinate:
1. Was nesting-quality landfast ice (or ice shelf) physically present on the prior `no` date? If missing, this is **habitat absence**, not an avoided vacant refuge.
2. Was the whole feasible patch imaged at the right breeding stage, with coverage and bird/guano detection sensitivity sufficient to conclude biological non-occupation? If not, outcome is **unknown**, not zero.
3. Does the following `yes` demonstrate egg/incubation/chick evidence and continued subsequent occupancy, rather than a temporary aggregation/observer effect? If not, it is **detection**, not proven new breeding.
4. Were other colonies/alternative candidate patches surveyed with similar effort? This is indispensable for any social attraction or 'occupied nodes capture migrants' claim.
5. Are contemporaneous wind, calving, path-passability and fast-ice break-up independently observed **before** the decision? Otherwise changing ocean access and local alternative use remain confounded.

No entry on the above list currently passes those gates. **0 qualifying events in this audited source is not evidence that no novel founding occurred anywhere.**

## Position within island biogeography

A real biological discovery would have to show a disperser choosing an already *occupied* breeding colony over a previously *empty, verified suitable and equally reachable* site, or vice versa. Neither this global model, its raw satellite attendance codes nor the 2024 newly reported sites identify that destination choice. The model mass-accounting result just shows that **the apparent state-switch phenomenon contributes a minority of modeled annual increases, and most individual switches cannot be interpreted as true available-site recolonization**.

We should **not** claim a new MacArthur–Wilson exception, competition/social inhibition or natal philopatry explanation from these numbers. The more interesting general mechanism—effective breeding options constrained by physical access **and** occupancy history—still needs data in which both are measured independently.

## Provenance and repeatable execution

- Author 50×10 model CSV: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/output/model_results/3_Colony_Level/colony_summary.csv
- Author original 2009–2018 satellite records: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/empe_satellite_2023-05-25.xlsx
- Original JAGS occupancy model: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/EMPE_model_empirical.jags
- Code: `scripts/audit_larue_2024_reappearance_mass_allocation_v1.py` (pinned source); `tests/test_emperor_larue_reappearance_mass_allocation_v1.py`
- Frozen results: `results/EMPEROR_LARUE_PUBLISHED_REAPPEARANCE_GROSS_GAIN_ALLOCATION_V1.json`
- Next scene target receipt: `results/EMPEROR_LARUE_FIVE_PRE_SHOCK_ICE_SCENE_TARGETS_V1.json`

**All this is retrospective.** The physically available but vacant refuge hypothesis in PR #195 remains **HOLD** without independent ice and breeding observations, and frozen PR #189 is untouched.
