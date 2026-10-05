# BTO SMP academic data-request content v2

**Status:** draft content only; not submitted.  
**Purpose:** obtain a raw structural extract for a prospectively frozen test of spatial recovery hysteresis.  
**Current access route checked 2026-10-05:** BTO/JNCC state that large SMP requests should use the BTO Data Request route or contact the SMP organiser at smp@bto.org.

## Project type

Academic (non-commercial)

## Title of project / question

Spatial recovery after local breeding-site abandonment in colonial seabirds

## Details of research

We are testing whether local breeding-site loss and recovery are spatially reversible in colonial seabirds.

The focal hypothesis is that, for the **same repeated breeding SiteID**, later recolonization may require a higher surrounding population state than the population state at which that SiteID was abandoned. In other words, population recovery may not simply retrace the spatial pathway of population decline.

The study was motivated by independent Antarctic penguin analyses in which breeding distributions became concentrated during decline and regional effective breeding-site number was not necessarily restored during numerical increase. Those penguin results are hypothesis-generating only and will not be pooled with the SMP test.

The SMP analysis is staged prospectively.

### Stage A — structure only

We will first use only identifiers, sampling years, missingness, method/unit metadata, and provider-supplied SiteID history to freeze stable species × MasterSite panels and mutually exclusive retained SiteIDs. Count magnitudes will not be used to select panels, SiteIDs, species, years or thresholds.

### Stage B — occupancy state only

For the frozen roster, counts will be reduced to:
- positive;
- explicit zero;
- missing/unusable.

Missing records will never be treated as zero.

We will identify only completed, calendar-consecutive vacancy spells of the form:

positive -> zero -> ... -> zero -> positive.

The exact SiteIDs and years entering the threshold comparison will therefore be frozen before abundance magnitudes are opened.

### Stage C — paired threshold test

Only if the predeclared support gate passes will count magnitudes be opened.

For each frozen vacancy spell, we will compare the surrounding MasterSite population state at:
- the occupied -> zero transition; and
- the later zero -> occupied transition.

The focal SiteID itself will be excluded from the surrounding population total.

A same-SiteID paired design is used so that fixed site identity/quality is controlled directly. A second frozen structured null will apply one **non-circular common integer-year shift** to every frozen abandonment/recolonization spell within the same physical MasterSite phase block. Only shifts that keep all shifted event years inside the same observed consecutive block are allowed. This preserves the observed multivariate abundance trajectory, local covariance, vacancy duration and relative event geometry while avoiding circular end-to-start wrapping.

Planned outputs are a peer-reviewed ecological study and fully reproducible analysis code.

## Details of proposed collaboration

[AUTHOR TO COMPLETE: list supervisors/collaborators, or state that no formal external collaboration is currently proposed.]

## Details of data required

Please provide the raw Seabird Monitoring Programme **Colony Count / Whole Colony Count** extract for 1986–2024 for non-sensitive species across Britain and Ireland, preferably in CSV, TSV or Excel format.

We need the most disaggregated repeated Site-level records available, including where possible:

- Species
- Country and County
- SiteID
- Site
- MasterSite and a stable unique MasterSite identifier/key
- Plot / Site-level indicator
- StartGrid and EndGrid
- Site category, Site type and Site habitat
- Start date and End date
- survey time fields if available
- Method
- Unit
- Count
- Accuracy
- Estimate / estimate type
- Comments
- verification / review status if available
- explicit nil-return / zero information, if encoded separately from Count = 0
- any field identifying merged-site totals, parent/aggregate sites, or historical site-boundary changes

The current BTO SMP guidance explicitly states that zero/nil returns are important because they distinguish true absence from a species simply not being surveyed. For the requested bulk extract, we still need the applicable record-era semantics confirmed rather than assuming that every historical record family encodes zero identically.

For this project, it is particularly important to distinguish:

1. **explicit zero / nil returns** from years in which a SiteID was not surveyed;
2. a stable physical MasterSite identifier/key from display-name labels, and persistent SiteIDs from SiteIDs that were renamed, merged, split, retired, replaced, or had boundaries redefined;
3. mutually exclusive child Sites within a MasterSite from aggregate MasterSite or merged-site totals.

If available, could you also provide or describe any SiteID/MasterSite crosswalk or change-log that records historical merges, splits, replacements, renames, or boundary changes?

## Data format

Electronic, preferably CSV/TSV; Excel is also acceptable.

## Additional information

During an earlier public structural audit, Kittiwake records for Flamborough and Filey Coast SPA were inspected to confirm the MasterSite > Site hierarchy. That species × MasterSite combination is excluded from prospective confirmatory analyses because count magnitudes were already visible.

The structural, SiteID-identity, zero-semantics, vacancy-spell, paired-effect, and V2 non-circular common-shift null rules were frozen before receipt of the requested bulk extract. If the data do not contain enough stable completed abandonment-to-recolonization cycles, the hypothesis test will stop rather than lower the support thresholds after seeing count magnitudes.


## Frozen analysis templates

Provider responses will be transcribed before occupancy-state analysis into:

- `submission/SMP_SPATIAL_RECOVERY_IDENTITY_RESOLUTION_TEMPLATE.csv`
- `submission/SMP_SPATIAL_RECOVERY_ZERO_SEMANTICS_CONFIRMATION_TEMPLATE.json`

No positive/zero spell scan is authorized until these metadata gates are complete.
