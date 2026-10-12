# V23 — A shared RFID gateway is not an observation of the nest micro-patch a bird chose

Date: 2026-10-11. This is a **source measurement-grain audit**, NOT a new quantitative biological finding. The source repository owner remains the Australian Antarctic Division and no wildlife individual IDs or events have been accessed.

## Existing evidence we must not claim as a new mechanism

The original [AAS_4086 weighbridge DOI 10.26179/1205-2s58](https://doi.org/10.26179/1205-2s58) describes a gateway crossing the passage shared by **multiple breeding subcolonies** on Béchervaise Island. The device records the ID, date/time, direction and weight of tagged birds **at the shared entrance**. It does **not** identify which nest, pebble mound, 3–10 m patch or subset of prospecting nests a bird actually inspected after passing.

The [AAS_4518 demographic and resight archive DOI 10.26179/s2qa-s344](https://doi.org/10.26179/s2qa-s344) describes birds identified via handheld tag readers **while seen ON nests**, scan dates and the derived measure **Age first.nesting.all.6.years**, and age of first natal return or recruitment. These reproductive timing and recruitment-related outcomes have already been studied in the published [Emmerson & Southwell (2022)](https://doi.org/10.1111/gcb.16437) study; their original field-level age/nesting methods are prior art. The nest scan metadata does NOT independently confirm that every tag read was the bird's first **own egg** or first lifetime reproduction, nor does it directly supply a previous-season prospecting patch that same bird had chosen.

Furthermore, [Emmerson, Walsh & Southwell (2019)](https://doi.org/10.1002/ece3.5067) already cross-linked individual gateway records to breeder/nonbreeder *same-season* state and found the bulk of nonbreeder passages occurred **after hatch**. [Penney (1970)](https://doi.org/10.1016/0003-3472(70)90048-5) already documented prebreeders prospecting near subsequent nests (58% first breeders had been seen in future nest vicinity) and [Acker et al (2022)](https://doi.org/10.1111/1365-2656.13676) already analyzed high-quality nest competition shaping breeding participation in colonial birds. Neither late prebreeder attendance, prebreeding nest-area proximity nor social competition is new by itself.

## Four questions that must remain separate

| Distinct prospective estimand | Can the **published gate + on-nest scan measurement design** answer it? | Missing element / novel-cause caution |
|---|---|---|
| E1. Tagged gate visitor in season t observed ON a nest in t+1 | **Potentially**, if both original archives and tag formats can be linked | Real source data, stable ID coding, which birds were at risk and year-specific detection/uptime. One tag at nest is not proof of an independently documented egg or newly colonizing individual. |
| E2. Tagged **never-breeder** in season t lays her/his **first verified egg** in t+1 | **Undetermined**; raw on-nest resight alone insufficient | Direct same-adult egg confirmation, lifetime known-age breeding history, early failure vs skip, adequate negative observations. Generic first nesting age is already studied. |
| E3. Prebreeder later first nests in the **same specific micro-patch visited** last season | **NO from a shared gateway alone** | Previous-year visited nest-patch GPS/unique site event is fundamentally absent from gateway data, regardless of the number of tag crossings. Need independent prebreeding per-patch sighting or tracking. |
| E4. **Causal inter-island** colony rescue or social/physical memory effect | **NO from these two same-island archives** | A separate source–recipient island tagged panel, live access/cue exposure contrast and both arrival/own-egg processes must be established. No random/exogenous variation here. |

The strongest possible source-link result without extra egg data would be a conditional probability of a **future nest-tag scan among previously gate-detected birds**, NOT a probability of own egg laying, first-ever reproduction, choice of an exact previously prospected patch, immigration or an island-boundary effect. It would also be necessary to account for repeated feeding passes and the gate covering only some subcolonies on one physical island.

## Actual completed scientific data-source gates

- [V20 official-source probe](https://github.com/zuizui0223/mina/actions/runs/38045283533) retrieved **HTML**, not authentic original bird-tag files, from AADC advertised downloadable URLs. A technical-guide link must not be misinterpreted as a raw gate-data link.
- [V21 prior-art and stage coding QA](https://github.com/zuizui0223/mina/actions/runs/38056704745) verified synthetic source-level logic, **not** the original 2019 raw tags. Original same-ID linking is attested by published 2019 paper.
- [V22 time-stage mock-data workflow](https://github.com/zuizui0223/mina/actions/runs/38058074727) verified same-day egg/hatch date ambiguity and why late nonbreeder visits do not make a homogeneous prelay risk set.
- **V23 static source-grain contract**, script and tests: `contracts/BECHERVAISE_INDIVIDUAL_VS_PATCH_GEOMETRY_V23.json`, `scripts/audit_bechervaise_individual_vs_patch_estimand_v23.py`, `tests/test_bechervaise_individual_vs_patch_estimand_v23.py`, `.github/workflows/bechervaise-individual-vs-patch-identifiability-v23.yml`. V23 checks only what source fields would license, never opens wildlife tag records. The workflow may pass technically without producing a new ecology result.

This correction addresses a conceptual overclaim in V21–22: we should not suggest that finding stable tag IDs alone would permit tests of **returning to a previously visited nesting patch**, because that requires a *site-specific previous visit event* not captured by the weighbridge's shared entrance.

## Decision and next action

**STOP hunting for a positive model in metadata-only source pairs.** To proceed with E1, the earliest data-access question is to obtain the authentic AAS_4086 RFID gate files and AAS_4518 season-tag nest resights from the [AADC](https://data.aad.gov.au/metadata/records/AAS_4086_Weighbridge), with Louise Emmerson's input, including tag encoding and effort coverage. For E2 require **individual egg records and natal histories** before computing transitions; for E3 require prebreeder **per-nest/per-subcolony visits** independently measured; for E4 require a **second island** with a comparable detection frame and a dated natural experiment.

Even those data would first answer one island's *descriptive conditional recruitment behavior*. The original observations could be from existing papers, so archival independence/novelty checks are necessary. Do not count multiple capes or subcolonies of the same island as independent islands.

No new causal Antarctic ecology mechanism has been established by V23. Ecology manuscript PR189, source-authentication PR142 and emperor georeference audit PR195 are unchanged.
