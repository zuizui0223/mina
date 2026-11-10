# Ross Sea Adélie penguin band-resight original-data discovery gate (2026-11-08)

**Branch:** `codex/penguin-ross-band-resight-source-audit-20261108` (separate from Circuitscape PR #211 and the warming PR #206). Original dataset discovery precedes opening any individual-level resight records. **This document fixes source acceptance criteria, not a preregistered biological hypothesis.**

## Critical new original sources

A direct **individual-level** dataset, not a paper re-analysis, is publicly cataloged at the U.S. Antarctic Program Data Center:
- Ballard, G. (2021), **Adelie penguin resighting data 1997–2021**, DOI **10.15784/601444**, `band_resighting_1997-2021.csv`, advertised original size **25.1 MB**, original MD5 `aaae6ddad6d12081b5a68466794438a2` (record DOI https://doi.org/10.15784/601444).
- Ballard, G. (2021), **Adelie penguin banding data 1994–2021**, DOI **10.15784/601443**, `band_inv_1994-2021.csv`, advertised MD5 `3da33defa4decc82b6e317c7fa9f9044` (DOI https://doi.org/10.15784/601443).
- The official project also exposes a [public PenguinScience raw-data repository](https://data.pointblue.org/apps/penguin_science/) via Point Blue Conservation Science, with a public `AllData/` landing page; a mirror there may or may not contain equivalent exact source files.

These catalogs identify **Ross / Beaufort Island research**, whereas the prior unsuccessful `results/PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json` examined **Palmer/Humble** and found no qualifying public later-resight crosswalk. This is **not a reversal of that Palmer source verdict**. An original band-resight table could enable a previously blocked real movement response in a **different region**, if it contains the necessary columns.

### Minimum evidence required before proclaiming an actual dispersal test

1. Download only through **provider-authorized, public data services and links**. If USAP-DC requires a browser reCAPTCHA for download, do **not** bypass it; stop at `SOURCE_ACCESS_HOLD` and preserve the official landing links. A documented alternate provider mirror is acceptable only if licensing and origin are verifiable. Do not scrape user-specific or hidden endpoints.
2. Verify *original file content* with the publisher-listed MD5. Record SHA256, bytes, and exact source URL, but **do not commit raw band IDs or person records to Git**. Programmatic summarization may be archived as aggregate QA; raw data remain at publisher or authorized user-provided location.
3. Independently examine original CSV header and readme. For `band_inv_1994-2021.csv`, require at least a stable **penguin individual band ID**, original **banding season/year** and a documented **banding place/colony**. For resight CSV, require the same **individual band ID**, later **season/date**, actual **resight site**, and (to call it *breeding dispersal*) a **breeding/occupancy status** that discriminates a breeder from visiting/nonbreeding individuals. If any field is missing/ambiguous, mark `SCHEMA_INCOMPLETE`; do not substitute another field silently.
4. Verify stable individual ID typing (leading zero band numbers remain strings); site code semantics and site lookup may distinguish Cape Crozier, Cape Bird, Cape Royds and Beaufort Island; confirm rather than assume from project description. If all observations occur at one site or identity-to-site cannot be joined, no between-site transition estimate.
5. Before biological outcomes, profile only **coverage and quality**: distinct source years, site codes, band IDs, duplicates and missingness, repeated individuals across years, simultaneous different-site resights, and whether breeding status codes are documented. No post hoc choice of convenient subset or automatic assumption that no resight means no return.
6. Only if valid: freeze within-individual **first documented breeding location** and later independently documented breeding location, distinguish natal (hatched at banded colony) vs adult previous breeding fidelity, same-year travel vs between-year breeding moves, and reconstruct empirically observed **origin → destination** flows. Use a multi-state capture–recapture or detection-adjusted model only with observation effort, observation process and individual statuses sufficient to identify it. Raw transition frequencies on seen individuals alone **do not** equal migration probabilities or climate causality.
7. If the source has true between-site breeding records, compare their observed moves to alternative marine **resistance functions**, but do not use the same movers to choose β and claim its independent validation. Season of the movement is unknown between breeding sightings; comparing a particular ice date as the true path is a model assumption and needs careful censoring.

## Target biological question and novelty boundary

> **Is the ecological 'penguins can travel but populations stay' premise correct at the *individual breeding-site* level, and do observed changes between Cape Royds / Bird / Crozier / Beaufort follow distance, coastline, sea ice or colony-specific breeding-history constraints?**

A public project page notes some birds banded at Cape Royds were observed nesting at Cape Bird, while other colony visitors did not nest; this suggests the hard premise 'they never relocate' is itself likely false. **Source counts and breeding status must be verified before reusing this illustration as new evidence.** The possible distinctive question is when *breeding* location switching does or does not happen, not whether penguins are physically capable of swimming.

This is a separately motivated data-source and hypothesis project for Ross Sea Adélie, **not independent replication** of the six western Antarctic Peninsula Adélie/Gentoo community-count series, nor a validated future population forecast. No change to `main`, Paper1/2 or warming manuscript v0.6 until a true source eligibility and novel biological test exists.

## Concrete status gate
- `SOURCE_METADATA_CONFIRMED`: official DOI, file listing and MD5 documented; **no contents yet**.
- `SOURCE_ACCESS_HOLD`: only CAPTCHA-authenticated data download exists in permitted current execution, no source bytes.
- `SOURCE_HASH_VERIFIED_SCHEMA_PASS`: original files obtained legally with matching MD5 and essential movement fields, before any outcome test.
- `SCHEMA_INCOMPLETE`: bytes available but insufficient individual/year/site/status fields.
- `FIRST_TRUE_RECRUITMENT_OR_BREEDING_MOVE_RESULT`: **only** after original observed band-ID-based transition calculation and method QC.

Deliver a source receipt and exact next operator dependency; avoid claiming rates from catalog text.
