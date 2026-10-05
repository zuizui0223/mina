# SMP provider evidence ledger v1

**Date:** 2026-10-05  
**Status:** public-source evidence collected before SMP outcome opening.

## Purpose

Separate what is already established by official BTO/SMP documentation from what still requires provider confirmation before the spatial-recovery hysteresis analysis may proceed.

No SMP ecological outcome is opened by this document.

## Official public evidence already available

### A. Explicit zero / nil returns are biologically meaningful

Official BTO SMP guidance states that zero counts are essential because they distinguish a species no longer being present from a species simply not being surveyed. It also states that local disappearance is recorded as a **nil return**.

Source:
- BTO, “Taking part in SMP”
- https://www.bto.org/get-involved/volunteer/projects/seabird-monitoring-programme/taking-part

Implication:

- it is legitimate in principle to distinguish a recorded zero/nil return from non-survey;
- the analysis must still verify how that distinction is encoded in the supplied bulk extract.

### B. Whole-colony counts are an official SMP record family

The SMP public database and data-access policy state that whole-colony counts can be browsed/downloaded online and are also available by request.

Sources:
- https://app.bto.org/seabirds/public/data.jsp
- https://www.bto.org/sites/default/files/seabird_monitoring_programme_data_access_and_use_policy.pdf

Implication:

- the requested primary record family exists as an official SMP data product;
- large/raw longitudinal extracts may still require a BTO request.

### C. The bulk Whole Colony Count schema contains the fields needed for the frozen filters

The 2022 SMP Data Request Guidance lists, among other fields:

- Species;
- SiteID;
- Site;
- MasterSite;
- StartGrid / EndGrid;
- site category/type/habitat;
- dates/times;
- Method;
- Unit;
- Count;
- Accuracy;
- Estimate;
- Comments.

It defines Accuracy code C as a count and E as an estimate.

Source:
- https://www.bto.org/sites/default/files/smp_data_request_guide_aug22.pdf

Implication:

- the Stage-A/Stage-C direct-count and count-unit filters are aligned with the documented extract schema;
- estimated records can prospectively be excluded rather than mixed with direct counts.

## Still unresolved and requiring provider confirmation

### 1. Missing-row semantics in the delivered extract

Need explicit confirmation that, for the supplied record family/era:

> absence of a SiteID × species × year row is not itself a biological zero and must be treated as missing/not surveyed unless an explicit nil/zero record is present.

The public guidance clearly distinguishes zero from non-survey conceptually, but the exact semantics of an absent row in a bulk extract must be confirmed.

### 2. Physical SiteID continuity

Need provider/site-history evidence for candidate SiteIDs:

- stable physical identity through the retained interval;
- rename history;
- merge/split history;
- boundary changes;
- retirement/replacement;
- whether the SiteID is a mutually exclusive child rather than an aggregate/overlapping unit.

A literal unchanged identifier is not accepted as proof of unchanged physical support.

### 3. Physical MasterSite identity

Need one provider-resolved physical \`master_site_key\` for every retained panel.

If one displayed MasterSite label maps to multiple physical entities, the candidate panel is excluded rather than split after outcomes are seen.

### 4. Canonical Count Unit when multiple Units survive structural filtering

If more than one otherwise-valid Count Unit exists for one species × MasterSite, BTO must identify the canonical primary Unit before occupancy states open.

No unit conversion or outcome-driven selection is permitted.

### 5. Zero-semantics scope

Need the compatible:

- start year;
- end year;
- record family/era;

for which the provider statements above are valid.

If semantics changed through time, Stage B is restricted to the confirmed era.

## Gate consequence

Stage B is authorized only after:

1. the official public evidence above is archived;
2. the provider-specific unresolved items are frozen;
3. the identity-resolved structural roster passes;
4. the zero-semantics JSON passes all runtime checks.

## Boundary

Official documentation reduces ambiguity but does not license assumptions about undocumented row absence, SiteID continuity, or boundary stability.

Those unresolved items remain hard stop conditions.
