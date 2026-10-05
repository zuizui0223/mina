# SMP data request draft — spatial recovery hysteresis

Dear Seabird Monitoring Programme team,

I am contacting you via the current SMP/BTO data-request route for a research extract; the SMP public guidance indicates that larger data requests can be handled through the BTO Data Request system or the SMP organiser.

I am assessing whether the SMP database can support a comparative study of whether local breeding-site loss and recovery are spatially reversible across colonial seabirds.

The specific test compares **the same repeated SiteID** at two moments: when it changes from occupied to an explicit zero count, and when that same SiteID is later recolonized. The hypothesis is that recolonization may require a higher surrounding MasterSite population state than the state at which the SiteID was abandoned.

Before analysing any count magnitude, I would first run a structural and occupancy-state audit. I am therefore requesting a record-level **Whole Colony / Colony Count** extract covering **1986–2024** for non-sensitive species that can be released for research use.

If available, could the extract include:

- Species
- Country / County
- SiteID
- Site
- MasterSite
- stable unique MasterSite identifier/key, if available
- StartGrid / EndGrid
- Site category / Site type / Site habitat
- survey date or year
- Method
- Unit
- Count
- Accuracy
- Estimate / estimate type
- Comments
- verification status
- explicit nil-return / zero information, if encoded separately from Count = 0
- Plot / spatial-level indicator distinguishing whole-colony Site records from partial/study plots

I note that the current SMP guidance describes zero/nil returns as essential for distinguishing true absence from an unsurveyed site. Because the requested extract spans historical record eras, I would nevertheless be grateful if you could confirm the scope/era for which that interpretation is valid in the supplied data.

For this project, three metadata issues are especially important:

1. **Zero versus missing.** Could you confirm whether an absent SiteID × year record means “not surveyed” rather than zero abundance, and whether explicit nil returns are identifiable?
2. **Site identity through time.** Is there a crosswalk or history for SiteIDs that were renamed, merged, split, retired, replaced, or had their boundaries changed?
3. **Mutual exclusivity.** Can parent/aggregate Site or MasterSite totals be distinguished from the component SiteIDs they summarize, so that overlapping records are not double-counted?

If plot-level records exist separately, they are not required for the primary analysis unless their identifiers and boundaries are stable and documented through time.

The analysis is prospectively staged. Panel and SiteID eligibility will be frozen from identifiers, sampling support and provider/site-history metadata before occupancy states or count magnitudes are opened. Provider confirmation of zero semantics is required before any Count=0 row can be treated as vacancy. The next gate will use only positive/explicit-zero/missing states to identify completed, calendar-consecutive abandonment-to-recolonization spells and their frozen contiguous complete-year blocks. Only if that support gate passes will abundance magnitudes be used for the paired threshold test and the predeclared common-phase temporal-alignment null.

I will follow the SMP Data Access and Use Policy and required acknowledgement wording in any publication using the data.

Many thanks for your help.


The provider metadata will be frozen into an identity-resolution table and a zero-semantics confirmation record before any abandonment/recolonization sequence is extracted.
