# V20 — Béchervaise Island RFID entrance events versus tagged nest-resight histories

2026-10-10. Source discovery and identifiability gate only, not a new biological result.

## Two linked-by-programme but NOT YET linked-by-animal datasets

[AAS_4086 weighbridge, 2006–2018](https://doi.org/10.26179/1205-2s58) was installed in the path between the sea and selected Béchervaise Island Adélie subcolonies. It captures time, direction, weight and embedded RFID identity for tagged passing birds, not an exhaustive census of all island visitors.

[AAS_4518 Mac. Robertson Land penguin demographic archive, 1991–2019](https://doi.org/10.26179/s2qa-s344) describes same-island seasonal files of tag IDs and dates read with handheld devices when tagged birds were observed on nests. The published data also contain chick survival/productivity, occupied nest counts, mass and marine climate metrics. The shared observation interval is 2006–2018. A probable same-island ID system is a useful hypothesis, not a verified exact join. RFID passage records may be repeated within one animal's feeding trips; scanning a bird on a nest need not verify its egg without recorded egg status, and failure to observe it on a nest does not prove its nonbreeding, emigration or mortality.

The old AADC indicator mentions tagged adults being searched from 2000/01 on Welch, Verner, Petersen and Klung islands near Béchervaise. However, that older indicator is explicitly obsolete and does not validate a current multi-island person-level data source. Until original data confirm sampling effort, tag code, detection and movements, this is still primarily a within-island opportunity.

## Prior art narrows new claims

[Emmerson and Southwell (2022), Global Change Biology, DOI 10.1111/gcb.16437](https://doi.org/10.1111/gcb.16437) already established the broad Mac. Robertson Land cascade: near-shore sea ice drove poor breeding success, the regional metapopulation lost approximately 154,000 breeding birds, and low cohort size was associated with inverse density-dependent fledgling survival. A new paper must not sell those published feedbacks as our discovery.

The still-unproven narrower claim is whether an independently recorded tagged *prospector's* admission to a colony is followed by that SAME individual's subsequent nest and first egg attempt, and whether this admission-to-breeding conditional probability changes under environmental or social contexts. This requires tag-based exact join, time/date ordering and real no-egg observation/detection.

## What the source inspection actually did

[GitHub Actions V20 #38045283533](https://github.com/zuizui0223/mina/actions/runs/38045283533) passed a bounded HTTPS source availability probe and its synthetic tests, but **both requested original AADC routes returned JavaScript HTML despite HTTP 206 status**:

- [AAS_4518 advertised source package /eds/5516/download](https://data.aad.gov.au/eds/5516/download): no genuine original nest resight XLS/ZIP validated.
- [AAS_4086 technical guide /eds/5228/download](https://data.aad.gov.au/eds/5228/download): no genuine guide binary validated. This is ONLY a guide route, not the as-yet unverified actual gate-crossing file download.

Zero penguin IDs, gate passages or original resight records read. The Australian publisher cautions that weighbridge data are **unprocessed, may not be directly interpretable**, and asks users to consult data custodian Louise Emmerson regarding its meaning. The original technical guide and source files are prerequisites to analyzing the events.

Artifacts: contracts/BECHERVAISE_RFID_GATE_TO_NEST_SAME_ID_SOURCE_V20.json; scripts/probe_bechervaise_original_rfid_vs_nest_resights_v20.py; tests/test_bechervaise_original_rfid_vs_nest_resights_v20.py; .github/workflows/bechervaise-rfid-nest-sameid-source-v20.yml.

## Decision

SOURCE AND ID-LINK HOLD. We found the first plausible original Antarctic evidence pair whose collection process can potentially observe tagged individuals at a colony entry BEFORE detecting a nest, but it remains **metadata-only**. If authentic originals can be obtained, require documented RFID tag compatibility, coverage and live entrance dates, source nest location/egg status and detection-effort models. Even then it would not by itself prove an inter-island colonization effect.

Do not manufacture a link, classify missed nest scans as failed breeding, infer immigration from multiple passes, claim a new demographic Allee effect or change frozen Ecology PR189, USAP PR142 and emperor PR195.
