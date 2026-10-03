# SMP bulk-data request specification v1

## Research purpose

We are assessing whether the Seabird Monitoring Programme can support an outcome-blind, multispecies analysis of how breeding abundance is distributed among persistent spatial monitoring units within larger breeding populations.

At the first stage we will **not inspect or analyse count magnitudes**. We will use only metadata needed to determine whether sufficiently long and internally complete MasterSite × species panels exist.

## Preferred spatial hierarchy

- parent population: `SMP_MasterSite × Species`
- component: `SMP_SiteCode`
- primary records: Whole Colony colony-count records at the Site level

Plot-level colony counts, if supplied, will be audited separately and will not be mixed with the MasterSite > Site analysis.

## Requested fields

Structural fields required for the outcome-blind gate:

- SMP_RecordID
- Species
- SMP_Country
- SMP_County
- SMP_MasterSite
- SMP_SiteCode
- SMP_SiteName
- SMP_PlotName
- StartDate or count year
- Method
- Count_unit
- Accuracy / CountAccuracy
- EstimateType
- Comments
- site start/end grid references if available
- any field identifying whole-colony versus partial count
- any field or separate crosswalk documenting SiteCode rename, split, merge, retirement or reassignment among MasterSites

The eventual scientific analysis also requires the count magnitude, but the structural audit will suppress that field until the eligibility gate and analysis protocol are frozen.

## Questions for SMP/BTO if not encoded in the export

1. Is `SMP_SiteCode` intended to identify the same spatial monitoring section through time unless a documented site-definition change is made?
2. Is there a versioned history or crosswalk for SiteCode renames, splits, merges, retirement or MasterSite reassignment?
3. Does the standard export distinguish Whole Colony and partial Site counts unambiguously?
4. Are `Total count after merging sites` records identifiable by a dedicated flag or only by comments?
5. Are colony-count study-plot records available in the database/export, or are plot-level records principally breeding-success records?
6. For historical records predating the current online system, were current SiteCodes back-crosswalked to legacy colony/section identities?

## Planned eligibility rule already frozen

A MasterSite × species panel is primary-eligible only if it contains:

- at least 3 persistent SMP SiteCode components,
- at least 10 seasons in which all frozen components have eligible counts,
- at least 12 calendar years from first to last complete season,
- one compatible census unit through time,
- one compatible method family through time.

The macro route proceeds only if at least 20 panels, 5 species and 15 MasterSites pass. This criterion was frozen before SMP count magnitudes were opened.
