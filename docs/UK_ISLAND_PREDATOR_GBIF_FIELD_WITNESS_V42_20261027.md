# V42 source validation STOP — independent mammal sightings vs strict UK island atlas

**Executed on 2026-10-27; Draft PR #201.** This is an audit of **independent mammal observation support**, not a fitted ecological-occupancy model and not an ecological negative finding.

## Existing UK mammal source-probability result (V40/V41 preserved)

The original Stanbury 2017 invasive mammal status × RSPB 2014 island table yielded probabilistic classifiers for P(published 1/2 status | source island covariates) on 506 islands >10ha low-tide area, 4 taxa. Original archipelago-block Brier gain: American mink −0.01655, brown rat +0.05846, house mouse +0.11429, feral cat +0.11783. **These are calibrated only against the original assessed source labels whose 0 class combines assumed and known absences**, not verified mammal occupancy. No changes to V40/V41 scores, maps or coefficients are made in V42.

## Distinct independently published public animal sources

- Mammal Mapper dataset GBIF UUID \`8898e990-9d39-4871-9e6e-d1031c19e24b\`, DOI \`10.15468/mjw32e\`, Mammal Society/NBN, CC BY 4.0.
- National Mammal Atlas Project online UUID \`67e2335c-4303-4ee3-9bfe-ecfe65662629\`, DOI \`10.15468/i2eosa\`, Mammal Society/NBN, CC BY-NC 4.0. These share verification/distribution partners (not independent survey designs). **No anonymous raw Atlas records copied or redistributed.**
- Both obtained via permitted public GET \`api.gbif.org/v1\`; taxon resolution in original GBIF species API: American mink \`Neovison/ Mustela vison\` key 5218823; brown rat 2439261; house mouse 7429082; Felis catus 2435035. \`Neogale vison\` name failed strict GBIF name match and was never misinterpreted as absence.
- Predeclared 2022–2026 (≤2026-10-27) window with recorded uncertainty ≤250m; strict single original GSHHG 2.3.7 **full-resolution** land polygon with exactly ONE original RSPB reference point and physical-island area class small; only source RSPB original 506 islands >10ha low-tide area; additional minimum 250m distance inland of mapped coastline. No nearest-neighbor snapping or interpolated source-island membership.

## Empirical source-only retrieval, bounded by predeclared 5,000 records / source / species

| Taxon | Mammal Mapper public records | National Mammal Atlas public records | Fully retrieved both sources? |
| --- | ---: | ---: | --- |
| American mink | 184 | 858 | YES |
| Brown rat | 803 | **7,073 indexed; NOT retrieved** (exceeds 5,000 source cap) | **NO** |
| House mouse | 54 | 378 | YES |
| Cat sightings (NOT necessarily feral) | 575 | 1,485 | YES |

**4,337** individual GBIF source occurrence rows downloaded over the seven full taxon×dataset requests; the 7,073 registered Atlas rat source rows were not counted as retrieved and were not partially sampled. All 4,337 are recorded mammal POSITIVES: no surveyed non-detections or observer GPS effort histories were obtained.

### Strict actual physical-island intersection

From the 4,337 downloaded UK mammal georeferenced source rows:
- 4,319 are strictly inside a unique original GSHHG land polygon; 13 are coastal snap candidates (excluded), 4 unresolved and 1 ambiguous.
- 4,317 of 4,319 are **not** strictly inside a physical island polygon represented by exactly one of the original RSPB lowid points and also belonging to the V40 506-island domain. This is largely an island-reference and mainland source-coverage issue; do NOT claim these mammal records are geospatially invalid or evidence of true absence.
- Exactly **two** source sightings match strict V40 island identities with coordinate-source quality; both are **Felis catus** from National Mammal Atlas, each on a distinct physical island and source island group, and **none is independently verified feral**. Publishing coordinates or original occurrence identities is not needed for the audit and not done.
- **0** strictly qualified recent American mink, **0** brown rat (one source incompletely retrieved), **0** house mouse positive sighting witnesses on the 506 source islands.
- Frozen source-only positivity gate (≥10 genuinely independently observed events, ≥5 strict source islands, ≥2 source groups, no cat ferality inference) **FAILS for every species**. It is a failure of independent-validation coverage, NOT biological evidence of predator absence.

## What this settles and what it does NOT

**It definitively tests one data source path:** two abundant publicly available UK mammal occurrence datasets have inadequate strict physical-island coverage to validate actual invasive-mammal occupancy predictions for the UK 506-island model. Combined with V36's just 3 verified mixed-island JNCC parent networks, the project has two independent **sample-identifiability** problems. No swapping coast buffers or pretending unknown presences are zeros to rescue a causal predator effect.

**It does NOT establish:** true occupancy calibration, sensitivity/specificity, a predator-free island list, rat/mink absence, recent eradication success, actual 1998–2021 JNCC predator status or actual seabird demographic predation effects. Original 2014/2017 status and 2022–2026 opportunistic sightings cannot be treated as coincident survey windows.

## Correct next input: field **surveillance deployment with audited negative checks**

The publicly available Scotland **Scottish Island Biosecurity Programme Plan (NatureScot 2026)** explicitly documents a national biosecurity surveillance database and an ArcGIS Survey123 app for submitting rodent/mink/camera/chew/tracking-tunnel observations. It also states that surveillance check frequency varies among islands, with some remote islands not checked. This is the correct *type* of original effort-indexed source from which a genuine detection-corrected island occupancy model might become identifiable, if accessible with appropriate data permissions.

The *Hebridean Mink Project* (2007–2014) separately has real documented individual trapping/capture histories analysed in NatureScot Commissioned Report 522, but a publicly downloadable machine-readable individual-island observation/effort file was **not verified** by this audit.

- New provider access gate, not yet completed: island ID/physical polygon; site/station ID; start/end deployment; method; explicit detection/non-detection; species identity; effort days/trap nights; survey year/date; operator/survey coverage; absence criteria; eradication/re-invasion date and method; shareable licence and source provenance.
- If obtained, first reclassify true observations separately from Stanbury historical source categorical labels, estimate effort-corrected \`Pr(z_island,species,year=1)\` with repeated visits and island-group-heldout Brier/calibration. Before new seabird H2, a separate physical island/within-network cross-landmass sample still must pass V36 threshold; **do not reopen V36 H2 without new island/polygon data**.
- Do NOT request private raw protected data, contact the provider, send email, export from authentication-protected Survey123, or bypass access settings without user authorization and provider terms.

## Reproducible evidence

- Contract: \`contracts/JNCC_GBIF_INDEPENDENT_PREDATOR_ISLAND_WITNESS_V42.md\`
- Source script and tests: \`scripts/audit_jncc_gbif_independent_predator_positive_v42.py\`, \`tests/test_jncc_gbif_independent_predator_positive_v42.py\`
- Pinned aggregate counts and source checksums: \`results/JNCC_GBIF_INDEPENDENT_PREDATOR_WITNESS_V42_SOURCE_RESULT.json\`
- Actual successful bounded live API + full GSHHG job: https://github.com/zuizui0223/mina/actions/runs/40468578519
- Scientific monitoring source: https://www.nature.scot/doc/scottish-island-biosecurity-programme-plan
- Other original trapping-source description: https://www.nature.scot/doc/naturescot-commissioned-report-522-analysis-and-future-application-hebridean-mink-project-data
