# SMP provider-confirmation templates v1

These templates are frozen before the SMP bulk extract is analyzed.

## Zero semantics

File:
`submission/SMP_PROVIDER_ZERO_CONFIRMATION_TEMPLATE_V1.json`

Fill only from:
- BTO/SMP provider correspondence;
- official data dictionary;
- official provider documentation.

Do not infer any Boolean from the observed ecological pattern.

Required before Stage B:
- direct Count=0 row is confirmed as a surveyed nil return;
- absent SiteID×year row is confirmed not to mean biological zero;
- estimated/imputed zeroes can be excluded;
- source and compatible data era are documented.

## Site identity

File:
`submission/SMP_PROVIDER_SITE_IDENTITY_TEMPLATE_V1.csv`

One row per candidate species × MasterSite × SiteID from Stage A.

Provider/metadata resolution must determine:
- one physical `master_site_key`;
- whether MasterSite identity is confirmed;
- stable SiteID identity over the retained interval;
- mutual exclusivity from siblings;
- overlap with parent/aggregate records;
- boundary change;
- retirement/replacement;
- canonical count Unit when multiple structurally eligible Units exist.

Ambiguous SiteIDs or MasterSites are excluded; they are never repaired using occupancy or abundance outcomes.

## Freeze rule

The completed provider-confirmation files are hashed and frozen before positive/zero occupancy histories are scanned.
