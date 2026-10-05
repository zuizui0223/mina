# BTO SMP academic data-request content v1

**Status:** draft content only; not submitted.  
**Purpose:** obtain a raw structural extract for an outcome-blind support gate before any macroecological response analysis.

## Project type

Academic (non-commercial)

## Title of project / question

Spatial redistribution of breeding seabirds during population increase and decline

## Details of research

We are testing whether long-term population change is accompanied by systematic changes in how breeding birds are distributed among repeated spatial monitoring units, and whether spatial concentration behaves differently during population increase and decline.

Initial Antarctic penguin analyses generated a prospective hypothesis that breeding-space organization may change partly independently of the sign of population trend: concentration can accompany decline, but numerical increase need not necessarily restore a previous spatial distribution. The SMP provides an independent system in which this symmetry can be tested across multiple seabird species.

Before testing any ecological outcome in the SMP data, we will run an outcome-blind structural audit using only sampling structure, identifiers and missingness. Count magnitudes will not be used to select species, MasterSites, SiteIDs, years or thresholds. The design treats mutually exclusive child Sites within a MasterSite as repeated spatial components and distinguishes recorded zeroes from missing observations.

If the structural gate passes, we will next inspect only total MasterSite-level abundance trajectories to confirm that enough increasing and declining panels are represented. Component-level spatial concentration will remain unopened until that balance gate is passed. The concentration estimand and inferential rules have been frozen in advance of receiving the bulk extract.

Planned outputs are a peer-reviewed macroecological study and fully reproducible analysis code. The Antarctic results remain a hypothesis-generating source and are not pooled with the SMP test.

## Details of proposed collaboration

[AUTHOR TO COMPLETE: list supervisors/collaborators, or state that no formal external collaboration is currently proposed.]

## Details of data required

Please provide the raw Seabird Monitoring Programme **Colony Count** extract for 1986–2024 for non-sensitive species across Britain and Ireland, preferably in CSV, TSV or Excel format.

We need the most disaggregated Site-level records available, including where possible:

- Species
- Country and County
- SiteID
- Site
- MasterSite and MasterSite identifier
- Plot / Site-level indicator (to distinguish Whole Colony Counts from Plot Colony Counts)
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
- any field identifying merged-site totals, nil returns, or historical site-boundary changes

The initial support gate will use identifiers, metadata and missingness only. After the eligible species × MasterSite roster is frozen, a second gate will use only summed annual MasterSite totals to verify that both increasing and declining trajectories are adequately represented. Component-level proportions and concentration metrics will remain unopened until both gates pass. We intend to use only observed raw counts in the primary analysis, not imputed annual values.

Please also advise whether current bulk exports preserve Plot identifiers and whether any SiteID or MasterSite crosswalk/change-log exists for historical merges, splits or boundary changes.

## Data format

Electronic, preferably CSV/TSV; Excel is also acceptable.

## Additional information

During a public structural audit we inspected Kittiwake records for Flamborough and Filey Coast SPA to confirm the MasterSite > Site hierarchy. That species × MasterSite combination will be excluded from any prospective confirmatory analysis because count magnitudes were already visible.

The planned outcome-blind eligibility gate requires at least three retained child Sites and at least ten complete observed years spanning at least twelve calendar years, together with a macro-scale support requirement across multiple species and MasterSites. These thresholds were frozen before receipt of the bulk extract and will not be relaxed after abundance or concentration outcomes are inspected.
