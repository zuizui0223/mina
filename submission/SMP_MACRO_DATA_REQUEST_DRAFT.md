# SMP data request draft — macroecology feasibility

Dear Seabird Monitoring Programme team,

I am assessing whether the SMP database can support a comparative study of how breeding birds are redistributed among component sites during long-term population increase and decline.

Before analysing any focal ecological outcome, I would like to audit the longitudinal structure of the database. I am therefore requesting a record-level **Whole Colony Count** extract covering **1986–2024** for the non-sensitive species that can be released for research use.

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
- Estimate
- Comments
- explicit nil-return / zero information, if encoded separately from Count = 0

For this project, it is especially important to distinguish repeated component Sites within a MasterSite from aggregate records that overlap or merge those Sites. If available, I would also be grateful for any metadata or crosswalk describing:

- SiteIDs that were retired, renamed, merged, split, or had their boundaries redefined;
- parent/aggregate Sites versus mutually exclusive component Sites;
- the meaning of comments such as “Total count after merging sites”;
- whether absence of a SiteID × year record always means “not surveyed” rather than zero abundance.

I also noticed that the public SMP browser contains some repeated non-whole-colony **Plot** records. If plot-level abundance data and stable Plot identifiers can be provided separately, could you let me know whether there is any plot-boundary history or documentation of plot additions/removals over time?

The intended first step is a data-structure audit only. Species, sites and time series will be selected using fixed support criteria before abundance magnitudes are used. If that gate passes, a second preregistered gate will inspect only total abundance trends to ensure adequate representation of both increasing and declining systems. Component-level concentration will remain unopened until both stages are complete.

I will follow the SMP Data Access and Use Policy and the required acknowledgement wording in any publication using the data.

Many thanks for your help.
