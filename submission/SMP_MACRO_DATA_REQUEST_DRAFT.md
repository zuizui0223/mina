# SMP data request draft — spatial recovery hysteresis

Dear Seabird Monitoring Programme team,

I am assessing whether the SMP database can support a comparative study of **local breeding-site abandonment and later recolonization** across colonial seabirds.

The focal question is whether population recovery simply retraces spatial collapse. Specifically, for a breeding Site that becomes empty and is later reoccupied, I plan to compare the surrounding MasterSite population state at abandonment with the state at later recolonization.

Before analysing any ecological outcome, I will freeze the spatial hierarchy and physical SiteID identities. I am therefore requesting a record-level **Whole Colony / Colony Count** extract covering **1986–2024** for non-sensitive species that can be released for research use.

If available, could the extract include:

- Species
- Country / County
- SiteID
- Site
- MasterSite
- StartGrid / EndGrid
- Site category / Site type / Site habitat
- survey date or year
- Method
- Unit
- Count
- Accuracy
- Estimate / estimate type
- Comments
- explicit nil-return / zero field, if available
- surveyed / not-surveyed field, if available
- parent / aggregate / merged-site field, if available

For this project, two metadata issues are especially important.

## 1. Site identity through time

Could you provide any SiteID / MasterSite change log or crosswalk that documents:

- renamed or retired SiteIDs;
- replacement SiteIDs;
- merged or split Sites;
- Site boundary changes;
- parent Sites overlapping child Sites;
- overlapping child Sites.

The focal abandonment-to-recolonization comparison requires the same physical Site to be identifiable across time. Any Site whose physical identity cannot be resolved prospectively will be excluded.

## 2. Explicit zero versus missing

Could you also confirm:

- whether a submitted row with Count = 0 is an explicit surveyed nil return;
- whether an absent SiteID × year row means unvisited / missing rather than zero;
- whether nil returns or survey completion are represented by a separate field.

Missing years will not be treated as absences, and vacancy spells will not bridge an unobserved year.

The analysis is preregistered in stages: identifiers and Site history first, then only positive/zero occupancy states, and only after the exact abandonment/recolonization spell roster is frozen will count magnitudes be used.

I will follow the SMP Data Access and Use Policy and the required acknowledgement wording in any publication.

Many thanks for your help.
