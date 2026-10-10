# Data-custodian inquiry draft — Béchervaise Island RFID and reproductive status

**Status:** READY TO REVIEW AND SEND MANUALLY; **NOT SENT**. 2026-10-10. The researcher may revise affiliation, name, research role, collaboration/author-credit expectations, and use/data access permissions before sending. This template intentionally contains no actual penguin tag values, credentials, AADC access tokens or inferred outcomes.

**Intended recipient:** Dr Louise Emmerson, Australian Antarctic Division — current contact information should be confirmed via the [original 2022 paper](https://doi.org/10.1111/gcb.16437) or [AADC 2024 weighbridge catalogue](https://doi.org/10.26179/1205-2s58).

**Subject:** Béchervaise Island: RFID weighbridge and nest resight data linkage / potential collaboration

Dear Dr Emmerson,

I am investigating how the different stages of colony recolonisation and population recovery can be distinguished in Antarctic Adélie penguins, particularly whether tagged adults that visit a breeding colony without nesting subsequently initiate their first breeding attempt.

I have read your 2019 *Ecology and Evolution* paper on body-mass patterns in breeders and nonbreeders (DOI 10.1002/ece3.5067), and the 2022 *Global Change Biology* study of regional population decline and demographic feedback (DOI 10.1111/gcb.16437). I understand that same-individual RFID records from the Béchervaise Island weighbridge were already linked to breeder status using on-nest tag resightings, and that the demographic decline/cohort-survival feedback has already been studied.

I identified two relevant AADC catalogues: the raw 2006–2018 weighbridge crossings (DOI 10.26179/1205-2s58) and the 1991–2019 population and nest-resighting data (DOI 10.26179/s2qa-s344). Before doing any individual-level analyses, I would appreciate your guidance on the following:

1. **Actual source access and processing:** What is the preferred authorized route to obtain the original 2006–2018 gate events and corresponding seasonal nest resighting files, and is there a processed weighbridge release or a technical codebook? The advertised AADC download pages present an interactive email/S3 process in my current workflow.
2. **Stable tag identity and year overlap:** Are PIT/RFID numbers consistently encoded across automatic gateway files and handheld on-nest tag scans in 2006–2018? Are there known tag reuses, format changes, reader failures or partial years that must be addressed?
3. **Direct nesting outcome:** For each same-tag adult and year, are *first observed arrival/passage*, on-nest status, independently verified clutch/egg laying, and chick production available? I understand that a nest tag read is not necessarily direct egg confirmation, and no scan is not evidence of confirmed nonbreeding.
4. **Breeding-state history:** Can known-aged prospective first breeders be separated from previously breeding adults that skipped a year or failed their nests early? Are visit-to-*next-year first egg* transitions already included in past published analyses or ongoing unpublished work?
5. **Coverage and interpretation:** What subcolonies were funnelled through the gateway each year, how complete were nest tag reader surveys, and how should late-season (often post-hatch) visits by nonbreeders be distinguished from early-season prospecting?
6. **Scientific use and collaboration:** If a well-defined new analysis is feasible, what data-use, authorship, custodian consultation, and attribution arrangements would you recommend? I would be pleased to discuss the question and avoid duplicating your ongoing research.

My intention is to establish data provenance and observational identifiability first, rather than infer individual breeding decisions or inter-island migration from colony-pair counts or unlinked datasets.

Thank you for your time and for building this remarkable long-term monitoring programme.

Kind regards,

[Your name]
[Your institution and department]
[Your contact details]

---

## Minimal analysis prerequisites once originals are provided

| Item requested privately | Why it is essential | Without it |
|---|---|---|
| Original PID/PIT codebook and stable encoding, season and reader firmware changes | Unique same-animal identity across gate and nest | HOLD_ANY_ID_JOIN |
| Raw crossing timestamp, direction and processing QC / uptime | Distinguish entering, returning from feeding, repeated passes | HOLD_FIRST_GATE_AS_TRUE_ARRIVAL |
| Nest scan date, tag and site/egg code with field scan effort | Identify own attempted reproduction and surveillance probability | HOLD_P_EGG_GIVEN_GATE |
| Genuine first breeding history or cohort of known-age tagged chicks | Separate first breeders, skippers and early failed breeders | HOLD_FIRST_BREEDING_TRANSITION |
| Colony-specific first observed egg/hatch dates and uncertainty | Distinguish conventional pre-laying from late-season nonbreeding visits | HOLD_STAGE_TEMPERATURE_AND_SITE_TIMING |
| Dated physical access, at least a second independently monitored island | Move from a single-island descriptive stage transition to island-biogeographic causality | HOLD_ISLAND_LEVEL_CAUSAL_GENERALIZATION |

**Never commit to GitHub:** private copy of raw tag-level events, any email link containing credentials, S3 secret keys, personal details not approved by the data custodian. Publish only approved aggregate diagnostics and code when licensing/attribution is resolved.
