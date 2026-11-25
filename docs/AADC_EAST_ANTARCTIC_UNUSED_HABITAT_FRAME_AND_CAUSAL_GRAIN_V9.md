# V9 — East Antarctic never-used habitat and the observation-grain trap

**2026-10-10; source-data archaeology and novel-mechanism stop, not a new causal result.** This updates experimental feasibility in `mina` PR193 only. The scientifically frozen Ecology paper PR189 and auth-gated mark-resight PR142 remain unchanged.

## A missing control class turns out to exist at a DIFFERENT spatial grain

The Australian Antarctic Data Centre's older source collections make a geographic-site risk set conceptually possible.

| Official AADC source | What it actually contains | Spatial/biological limitations |
|---|---|---|
| [Potential habitat for Adélies](https://doi.org/10.4225/15/5758F4EC91665), `AAS_4088_Adelie_Potential_Habitats` | A defined list/map of ice-free **islands within 100 km of shore and coastal continental exposed-rock outcrops within 1 km of shore**, from 37–160°E | An *island/outcrop* is NOT a measured 3–10 m patch suitable for a particular nest; absence is not documented by membership alone |
| [Historical site occupancy](https://doi.org/10.4225/15/57590498D301C), `AAS_4088_Adelie_Occupancy` | Breeding-site name and shared site codes, historical presence and absence observations by breeding season (1950s–2012) | Not a guaranteed full annual census, no failed nest/chick success or guaranteed detection |
| [2025 8-species explicit search/non-reporting](https://doi.org/10.26179/5n29-r073), `AAS_4518_Seabird_Breeding_Occupancy` | 1910–2020 records by season/geographic site/species, including **presence, explicit absence, and mere non-reporting despite a site search** | Older missing/unknown visits remain unknown; reporting-state distinction already published by Southwell et al 2025; no matched nest-scale stage-specific fitness |
| [Original Cox 2024 Cape Crozier source](https://github.com/pointblue/solo_nests/tree/PolarBiol-submission/data) | **50** actual historical GPS nest IDs with egg/chick observation and next-year local follow-up | All sites were sampled BECAUSE an original solitary nesting site was recognized; **zero** independently sampled never-used suitable 3–10 m sites, 13 `breeder=0` are not confirmed egg failures |

**Key causal point:** AADC *island-scale* known negative cannot be artificially inserted as a control observation in Cox's *3–10m nest-scale* cohort at a different Antarctic region and generation. That would manufacture a false matched comparison even if geographic coordinates and seasons could be made to look compatible.

## What actual source access reached

The NASA Earthdata CMR collection mirror in `opengeos/NASA-CMR-STAC` lists the AADC-authorized historical `file_id=4598` and `/eds/4345/download` endpoints. The exact official source-only [GitHub Actions #38011152997](https://github.com/zuizui0223/mina/actions/runs/38011152997) **completed success** as a provenance audit with *scientifically negative access results*:

- Potential habitat old `download_file.cfm?file_id=4598` endpoint **downgrades HTTPS to HTTP** on the AADC host. This source gate blocks the insecure redirect rather than trusting a modified/unauthenticated binary. No map/table downloaded.
- Historical occupancy `/eds/4345/download` served a 1211-byte **JavaScript application shell**, not an official occupancy CSV, spreadsheet or complete ZIP. No breeding states or site counts were read.
- A second [official-redirection diagnostic #38011213531](https://github.com/zuizui0223/mina/actions/runs/38011213531) confirmed the downgrade target was only `http://data.aad.gov.au` (no URL path or query details logged).
- Therefore: **0 original site/season occupancy records** and **0 official never-used sites** have been empirically joined. The AADC's metadata and its potential habitat frame exist, but actual usable archived biological rows and a matched nest-level crosswalk are **unverified**.

A new source-bound audited contract and script/CI protect this distinction: `contracts/AADC_4088_POTENTIAL_SITES_VS_OCCUPANCY_SOURCE_GATE_V1.json`; `scripts/probe_aadc_4088_potential_vs_occupancy_source_v1.py`; `.github/workflows/aadc-4088-potential-occupancy-official-source-v1.yml`; `contracts/PENGUIN_ISLAND_VS_NEST_PATCH_OCCUPANCY_SOURCE_HIERARCHY_V1.json`.

## The novelty is narrower than we hoped

- **Southwell et al. 2017**, DOI [10.1642/AUK-16-125.1](https://doi.org/10.1642/AUK-16-125.1), already used historical direct observations to reject **all 16** putative new colonization/extinction events in East Antarctica, emphasizing spatial/site-label errors, season mismatch and failed satellite detection of small colonies.
- **Southwell & Emmerson 2020**, DOI [10.1002/ece3.6037](https://doi.org/10.1002/ece3.6037), already connected habitat occupancy, density dependence, land availability and selection of steeper terrain (including 50m plot-level occupied/unoccupied mapping) across multiple regional populations.
- **Southwell et al. 2025**, DOI [10.1111/ddi.70066](https://doi.org/10.1111/ddi.70066), already generalized **present / absent / unknown and non-reporting** across eight seabird species, 1910–2020, explicitly finding extensive geographic and seasonal observation gaps.

Thus neither simply building a potential site roster, nor finding unoccupied islands, nor pointing out bias/false colonizations, nor showing density-dependent occupation of rocky sites is novel.

## Falsifiable difference that would actually matter in island ecology

Only a *new independent* panel that observes (1) physically usable formerly **never-used** breeding micro-patches, (2) **genuinely failed** nests (verified egg attempt/fate) and **successful** nests, (3) exact same next-season patch-ring new settlement and first breeder identities, (4) before/after physical mound/guano changes and climatic/predator access, and (5) replicate **independent islands/colonies** can separate:

- **Failed-pioneer ecosystem engineering:** prior failed nest site causes a durable increase in effective reproductive opportunity, independent of successful chicks or arriving marked family members;
- **Successful nest public information:** preferential next-year first settlement only following prior success;
- **Static habitat sorting:** all three prior-history classes disappear as independent predictors when pre-arrival microterrain, accessibility and detection are made comparable.

The **causal intervention** (or independently timed environmental event) is not an extra covariate; it is needed to distinguish physical change *caused by the pioneer* from original substrate quality that attracted both the pioneer and later arrivals. Previous literature already described stones, guano mounds, nest cue attraction and young-breeder dispersal.

**Decision:** Hold this mechanism in PR193 rather than analyzing Cox's original 36 nests or the unrelated AADC site-scale frame to manufacture a positive result. The next field/dataset priority is a **matched, season-dated 3–10m patch sampling frame including verified empty plots and fledging outcomes**, not another broad ice/area regression. This is currently **prospective design only**; no new causal Antarctic penguin or island law established.
