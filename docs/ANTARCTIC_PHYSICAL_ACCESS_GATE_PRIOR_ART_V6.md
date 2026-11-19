# Antarctic breeding opportunities: area is not the same as passability — prior-art and causal feasibility audit v6

**2026-10-08 | PR #192 exploratory follow-up; NO new biological outcome accessed or fitted.**  
**Purpose:** evaluate an independently documented mechanism that competes with "more island nesting area suppresses emigration." A **passable route** may turn a pre-existing breeding site from practically unusable to usable with no meaningful change in total mapped area. The two components of access, **ocean-foraging access** and **nest-site/ice-shelf entry passability**, can point in opposite directions. This is not a new discovery: specific prior literature already documents both.

## 1. Independent biological observations — do not rebrand as our findings

### Atka Bay emperor penguins (ice shelf and sea ice, not an offshore rocky island)

- Zitterbart et al. (2014, Antarctic Science, doi:10.1017/S0954102014000285) documented a **stable-sea-ice** 2013 event: between **12 and 26 August 2013**, about **2,000 birds (~70% of the colony)** climbed from sea ice to the adjacent ice shelf, an extraordinary change relative to the regularly observed location since 1981. The shelf edge was **~15 m high** and usually impassable. An unusual accumulation of snow in April–June 2013 created accessible ramps (approximately 15% slope); a high frequency of strong persistent easterly winds in July–August plausibly pushed the colony towards the new route. **Snow ramp and wind are both candidate causes** and were already explicitly identified by the authors. Nor can it be claimed that simply poor sea-ice stability forced the event: sea ice was stable.
- Richter et al. (2018, Methods in Ecology and Evolution, doi:10.1111/2041-210X.12971) recorded Atka Bay colony motion and meteorology in April–July 2013 and demonstrated wind-related colony movements. The open SPOT data are deposited under Dryad doi:10.5061/dryad.19ph7 (Zenodo public record 4936490); the **colony-location/wind ZIP is ~19.8 MB**. This directly vetoes the unqualified claim "wind causes collective penguin displacement" as novel.
- Macdonald et al. (2026, Communications Earth & Environment, doi:10.1038/s43247-026-03906-0) tracked **three emperor colony locations**, Atka Bay, Coulman Island and Cape Washington, through **2017–2024** using Sentinel-1 SAR and optical imagery. Atka Bay colonies moved from fast ice onto the ice shelf in **7 of 8 breeding seasons**, often **months before** fast-ice breakup and **despite apparently stable fast ice**. In winter 2024 the Atka Bay colony was observed in **two small embayments**. Summer groups at all three colonies sometimes **moved away from open-water/ice-edge access**, rather than monotonically minimizing travel distance to sea. Authors explicitly discuss wind as a leading candidate and call for high-resolution local meteorology to distinguish drivers.
- Fretwell et al. (2026, Communications Biology, doi:10.1038/s42003-026-10961-y) already documented **five** emperor colonies that relocated or newly appeared, including two likely relocations after ice-shelf calving. Dynamic ice-associated colony relocation and distinction from genuine new founding are therefore prior art, not our claimed general mechanism.

**Necessary substrate caution:** an emperor colony on mobile fast ice/ice shelf can translate over kilometres while the breeding group persists. This is categorically different from a newly occupied Adélie nesting unit on immobile rock or an observed first-breeding migration across a physical island boundary. Do not mix these as identical immigration events.

## 2. A precise causal distinction

For a candidate site i and season t distinguish:

- **Material nesting space** K_it: rock or ice area meeting geomorphic nesting prerequisites, mapped without contemporary guano/occupancy.
- **Entry passability** Q_it: an independently observed snow ramp, accessible slope, corridor or tide-crack pathway by which birds can reach that space *at the actual reproductive stage*. This may change at a **threshold** even when K stays fixed.
- **Ocean-resource access** A_it: feasible path from colony to open water or foraging, potentially harmed by the same ice/snow that improves Q.
- **Occupancy/settlement** B_it: documented nesting or active breeding in that site, not assumed to be identical to birds seen visiting.
- **Weather** W_t: high-frequency directional wind, snowfall and exposure.
- **Age/stage** S_t: incubation versus chick rearing versus post-fledging (not interchangeable).

In Atka 2013 the hypothesized positive change was Q, not a demonstrated increase in K. Extra snow can simultaneously increase Q to a high shelf and impede A to ocean in other geometries. Thus "more snow is good/bad" has **no unambiguous predicted sign** unless its placement relative to routes is specified.

The biologically stronger cross-system question is whether **environmental variation shifts the *identity of the limiting boundary*** rather than simply adding/subtracting habitat area:

> Does threshold accessibility to a pre-existing nesting option alter where breeding is expressed, independent of usable area, sea-ice stability and wind? If access changes without new capacity, colony layout can reorganize without new settlement across islands.

This is a proposed comparison, not yet a cross-taxon law.

## 3. Data pairing found, and what remains unidentifiable

Potentially compatible, independently monitored sources:

| Data source | Years / geography | Actual information | What it cannot identify alone |
|---|---|---|---|
| Macdonald et al. 2026 / NERC UK Polar Data Centre doi:10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9 | 3 emperor sites × 2017–2024 | geolocated subgroup positions over winter-to-summer, reportedly available as tracking shapefiles | individual band identities, successful immigration, independently measured ice-shelf ramp geometry |
| AWI Neumayer III PANGAEA doi:10.1594/PANGAEA.962313 | station c. **8 km** from Atka; 1-min weather instrument since 1998, source series from 1982 | measured **wind direction DD10, wind speed FF10** and meteorology. Example November 2017 doi:10.1594/PANGAEA.887751 and May 2018 doi:10.1594/PANGAEA.900773 | colony-site wind exposure at sub-km scale; local ramp creation or pack-ice path |
| Richter et al. 2018 SPOT archived imagery/wind, Dryad doi:10.5061/dryad.19ph7 | 2013 Atka, video/image + meteorology | historical joint measurement that can verify processing and wind-direction sign conventions | *new* 2017–2024 outcome or independent replication |
| Macdonald et al. remotely sensed fast-ice context; local topographic/snow surveys required | 2017–2024 | some sea-ice state and ice-shelf position information | yearly ramp passability **Q_it**, without on-location imaging/DEM and effort |

**Current access issue:** public UK Polar Data Centre discovery endpoint for doi:10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9 currently returns the explicit notice **"This service is temporarily unavailable"**. We have **not obtained its shapefile rows**, so no paired colony displacement × wind fit can honestly be reported. PANGAEA provides a published weather *series* and directly accessible 2017–18 monthly metadata, but the full 2017–2024 month-level weather coverage and exact matched clocks still require a frozen structural inventory.

**Critical scientific identification gate:** 8-km-away station wind is stronger than coarse ERA5 but is **not a local ice-ramp measurement**. Even a highly significant wind-displacement slope would distinguish weather forcing from random movement, **not** prove that ramp passability Q caused crossing. To test passability independently, build time-stamped snow-ramp geometry **before** location change (e.g., validated SPOT/VHR records). **Do not infer ramp existence from the penguins crossing it**, which would make the test circular.

## 4. Falsifiable alternatives with explicit outcome distinction

**H-Q: access-threshold switching**: first ice-shelf entry is likely when externally mapped, stage-feasible ramps connect existing ice to the shelf, controlling for wind direction and fast-ice stability. If suitable ramps exist in many well-observed seasons with no shelf entry, or entry occurs without a ramp, the strong deterministic version fails.

**H-W: wind-driven collective response**: subgroup displacement direction aligns with the *toward* vector of short-term measured wind (meteorological DD10 is a **from-direction**), with fast changes after reversals. Wind is known prior art from 2013; only a new **stage-matched, independently held-out 2017–2024** effect would extend temporal generality.

**H-I: ice-risk relocation**: site switching follows changes in physical ice stability or breakout risk, not mere wind/stage. Atka 2013 and repeated 2017–2024 movement **during apparently stable fast ice** contradict the *universal* deterministic claim that instability is necessary, without excluding variable risk perception.

**H-S: stage-dependent social/reproductive geometry**: motion depends on chick age, aggregation and safety/thermoregulation more than marine access. Requires stage-aligned repeated movement and independent stage/colony data, not just a fixed October/November threshold fitted post-result.

**H-Ocean: always minimize distance to the sea**: **already contradicted as a universal rule** by documented late-season outward-from-edge motions in Macdonald et al. 2026. Do not relabel this as a newly tested null.

## 5. Relevance to island ecology and explicit STOP

The strongest usable insight for PR #192 is **effective island isolation is state-dependent**: access is shaped by slope, temporary snow bridges, sea ice, and reproductive timing, rather than a static land polygon or inter-island distance alone. **But Atka Bay is NOT a test of Beaufort north-to-Ross first-breeding settlement or neighbour rescue**. The already-known effects should be used only to prevent incorrectly attributing Beaufort movement patterns to gross island area.

To go further, demand before any new outcome analysis:

1. Full 2017–2024 location files with calendar dates and group-coordinate precision (currently retrieval-blocked at PDC).
2. Reliable matched wind stations at the correct resolution, with declared local-vs-station extrapolation and missingness.
3. **Independent observed ramp/accessibility Q** if claiming the *cause* is crossing geometry. Without Q, only wind vs broad ice state can be evaluated, not the new access threshold.
4. Within-season group identity and image continuity so temporal changes aren't treated as new independent colonies.
5. Multiple truly independent events/colonies for any general island-boundary claim. Three emperor colonies of differing physical substrate are not independent island pairs sharing a first-breeding estimand.

**Decision:** STOP causal access-threshold claims in PR #192 at present. Favor a distinct follow-up if full trajectory + local ramp imagery become available. Keep frozen Ecology PR #189 and locked individual choice PR #142 unchanged.

## Links / prior art
- Zitterbart et al. 2014: https://doi.org/10.1017/S0954102014000285
- Richter et al. 2018 / Dryad: https://doi.org/10.1111/2041-210X.12971 / https://doi.org/10.5061/dryad.19ph7
- Macdonald et al. 2026: https://doi.org/10.1038/s43247-026-03906-0
- Tracking data: https://doi.org/10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9
- AWI station data: https://doi.org/10.1594/PANGAEA.962313
- Fretwell et al. 2026: https://doi.org/10.1038/s42003-026-10961-y
