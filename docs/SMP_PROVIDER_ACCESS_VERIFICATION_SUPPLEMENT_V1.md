# SMP provider-access verification supplement v1

**Date checked:** 2026-10-05  
**Status:** operational/provider-evidence supplement only.  
**Scientific design:** unchanged from `SMP_SPATIAL_RECOVERY_HYSTERESIS_PREREGISTRATION_RECEIPT_V3.json`.

## Official access route verified

Current BTO guidance states that raw survey data can be requested using the BTO Data Request Form.

Current form:
https://app.bto.org/data-request/new-data-request.jsp

The public SMP data page additionally states that large amounts of SMP data should be obtained through a Data Request form and gives `smp@bto.org` as the SMP contact.

Sources checked:
- https://www.bto.org/data
- https://app.bto.org/seabirds/public/data.jsp
- https://www.bto.org/get-involved/volunteer/projects/seabird-monitoring-programme/taking-part
- https://www.jncc.gov.uk/our-work/seabird-monitoring-programme/

## Zero semantics — public evidence

BTO's current SMP guidance explicitly says that zero counts are essential because they distinguish a species no longer being present from a species simply not being surveyed.

The same page describes site extinction as a recorded **nil return**.

This publicly supports the preregistered distinction:

- observed explicit zero / nil return ≠ unvisited or missing year.

## Still unresolved and still requires provider confirmation

The public guidance does **not** fully establish the database-level semantics needed for the frozen analysis.

The following remain mandatory provider-confirmation fields:

1. whether every direct `Count=0` row in the requested record family is a surveyed nil return;
2. whether absence of a `SiteID × species × year` row always means missing/not surveyed rather than biological zero;
3. how estimated, imputed or inferred zeroes are encoded and can be excluded;
4. which years / record family obey those semantics;
5. physical continuity of SiteIDs through renames, merges, splits, retirements, replacements or boundary changes;
6. provider-resolved physical MasterSite equivalence when multiple species or identifiers refer to one geographic breeding locality;
7. parent/aggregate versus mutually exclusive child-site relationships.

## Execution consequence

Public web documentation alone does **not** authorize Stage B.

Stage B remains locked until the provider confirmation template and physical-identity gate are completed under the frozen contracts.

## Data-availability caveat

BTO notes that bespoke data requests may require staff processing and may be chargeable in some cases. Sensitive records may also be restricted or spatially blurred.

The frozen design already excludes sensitive species from the requested confirmatory pool.

## Boundary

This supplement records operational facts only.

It does not:
- change zero semantics;
- infer missing rows as zero;
- change support thresholds;
- add/remove species;
- change SiteID or MasterSite identity rules;
- authorize biological outcome opening.
