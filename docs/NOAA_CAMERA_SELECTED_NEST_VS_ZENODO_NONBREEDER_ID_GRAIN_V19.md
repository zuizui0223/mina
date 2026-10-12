# V19 — Why nest cameras and nonbreeder satellite tags do not identify arrival-to-breeding transition

2026-10-10. Public-source feasibility audit, not penguin demographic or causal effect. Canonical original sources:

- [NOAA NCEI Accession 0171619](https://www.fisheries.noaa.gov/inport/item/52182), DOI 10.7289/V5Z036F7, Hinke et al 2018 [Methods in Ecology and Evolution](https://doi.org/10.1111/2041-210X.13015).
- [NOAA original focal camera nest attendance dictionary](https://www.fisheries.noaa.gov/inport/item/52183); [same-source nesting status/egg/chick dictionary](https://www.fisheries.noaa.gov/inport/item/52186); [independently observed validation nests](https://www.fisheries.noaa.gov/inport/item/52187); [historic laying-hatch-crèche interval table](https://www.fisheries.noaa.gov/inport/item/52185).
- [Lowther et al nonbreeding Adélie satellite telemetry, Zenodo record 5036339](https://doi.org/10.5281/zenodo.5036339), 2016–2017 South Shetland/King George Island, 15 known nonbreeding adults tracked from Carlini and 15 from Arktowski research areas; Argos positions, date/time, quality and underwater fraction.

## Concrete variable coverage and selection

| Identifiable event / denominator | NOAA preselected nest cameras | Zenodo 2016/17 nonbreeding 30 tracked adults |
|---|---|---|
| Sampling unit | camera×rookery×subcolony×species×focal **nest**, daily | marked telemetry **adult**, irregular Argos fixes |
| Entry into study | Only nests at which **two adults were already present at an empty nest before laying** | Already designated *nonbreeding* adults captured and tagged |
| Visit to potential colony before deciding whether to nest | **NO unselected at-risk visitors** | **NO verified visit/prospecting state at named alternative nest patch**; geographic fixes are positional data |
| Egg laid after visit by same individually identified adult | Egg status/lay/hatch/creche YES **for selected nest**, **NO adult individual identity linking visitor to eggs** | **NO first-egg/focal nest code or breeding status transition** |
| Post-laying risk period and crèche | YES for focal selected nests | No identified offspring or nest |
| Independent geographic island replication | Camera source has distinct nesting study rookeries in multiple southern islands, but selected nest cohort only | Carlini and Arktowski study areas are both **on King George Island**, not two independent islands |
| Can estimate P(same adult eggs after arriving) | **NO, denominator selected after pairing** | **NO, marked first egg absent** |

Original 2018 method explicitly states focal nests were chosen by observing >=2 adults at an empty nest bowl *before* lay; this is **conditioning on pair association**, not an intake census of arriving adult nonbreeders. [Hinke et al 2018](https://doi.org/10.1111/2041-210X.13015) already validated adult presence trajectory to estimate laying/hatching and direct crèche phenology on up to 455 nests. Any new raw camera success effect might be useful for a *post-establishment* fate/phenology study, but cannot be advertised as the unobserved pre-egg transition.

**Crucial original NOAA integer-code trap:** `maxn=0` means no adult visible at an already **selected focal nest** on that day (not zero colony arrivals), `maxn=1/2` are number of adults, `maxn=4` is a special *crèche marker*, and `maxn=5` is *confirmed nest failure*. Treating all `maxn` as integer counts 0–5 invents 4–5 adult congregations on failed/crèche nests, a serious false social effect. We added an explicit source-code classifier and tests with zero different from missing. There is no numeric code 3 licensed in the NOAA published schema; fail closed on undocumented codes.

The source `repro v1-1.xlsx` *does* record site/camera/nest/date, copulation, direct egg-lay, eggs, hatch, chicks and crèche, and `validation v1-1.xlsx` records 2015/16 independent direct egg/hatch outcomes for the **same selected nests**. The biological stage fields are real, but the person-level visitor denominator and common banded adult identity are not. A source-level nest-key join between attendance and repro could be verified after original data access; a join by site/date alone to 30 telemetry IDs cannot identify the same penguin.

## Actual metadata and provenance check

Source-audit [GitHub Actions #38040617716](https://github.com/zuizui0223/mina/actions/runs/38040617716) completed successfully after correcting a QA bug where `0` was incorrectly treated as a missing attendance value. The official [Zenodo API metadata](https://zenodo.org/api/records/5036339) lists `data.csv`, **5,765,910 bytes**, checksum **MD5 d4ca95fd92096e58ffbffff84250d669**, matching the publicly shown 2021 archive. Our script fetched **metadata only**, inspected **0 actual penguin location rows**. NCEI original camera XLSX bytes also not read in V19; NOAA published field dictionary and 2018 methods were verified externally.

- `contracts/ANTARCTIC_VISITOR_TO_FIRST_EGG_NOAA_ZENODO_SOURCE_GATE_V19.json`
- `scripts/audit_noaa_zenodo_visitor_to_first_egg_source_v19.py`
- `tests/test_noaa_zenodo_visitor_to_first_egg_source_v19.py`
- `.github/workflows/noaa-zenodo-visitor-to-first-egg-v19.yml`

## Mechanism verdict and the only meaningful next dataset

**HOLD — the attractive hypothesis 'Royds received visitors but they chose not to lay' has not been tested or quantified.** This new source discovery shows why combining (i) NOAA **selected nest** egg success and (ii) Zenodo **at-sea nonbreeders** cannot determine P(egg|colony arrival), let alone test Ross Island Royds versus Bird supply. Both are geographically **western Antarctic Peninsula / South Shetlands**, NOT Ross Island, and the known nonbreeder stations are on the *same* King George Island. No direct person ID, site/season, species-specific state-at-risk, or movement join exists across both independent research projects.

To distinguish supply from post-arrival decisions, data must include *all marked or detection-corrected incoming prospective adults* at the exact recipient colony entrance, dates of visits to particular nest patches, and whether **those same individuals** lay eggs and then crèche chicks that season. Missing an adult during camera observations is not proof of their dispersal or mortality. Causal explanation further requires independently measured breeding stage access and predator/social conditions, not only arrival counts.

**Scientific action:** Stop searching in already selected nests for missing nonbreeders and stop calling nearby pair-count ratios immigration. The frozen Ecology manuscript PR189 and independent source-authenticated ID gate PR142 remain unchanged, PR195 emperor source audit unchanged.
