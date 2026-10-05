# BTO SMP academic data-request content v2

**Status:** draft content only; not submitted.  
**Purpose:** obtain a record-level extract that can support a preregistered test of spatial recovery after local breeding-site abandonment.

## Project type

Academic (non-commercial)

## Title of project / question

Spatial recovery after local seabird colony loss: are abandonment and recolonization thresholds symmetric?

## Details of research

I am testing a specific island-ecology hypothesis in colonial seabirds:

> when a breeding Site has been abandoned, does that same Site require a higher surrounding population state to be recolonized than the population state at which it was lost?

The hypothesis was generated independently from long-term Antarctic penguin analyses, where breeding distributions became concentrated during decline and did not necessarily re-expand during numerical increase. The SMP would provide an independent multi-species test based on repeated abandonment and later recolonization of the **same physical SiteID**.

The analysis is deliberately staged.

### Stage A — structure and SiteID history only

Before using count magnitudes, I will identify candidate species × MasterSite panels using only:

- SiteID and MasterSite hierarchy;
- observation years and missingness;
- count unit and method;
- Whole Colony versus plot/partial/merged status;
- SiteID history, including renames, merges, splits, replacements and boundary changes.

A SiteID can enter the focal test only if its physical identity is stable across the retained interval and it is a mutually exclusive child Site within its MasterSite.

### Stage B — occupancy state only

After the physical SiteID roster is frozen, count values will be reduced only to:

- positive;
- explicit zero;
- missing/unusable.

A missing SiteID × year record will never be interpreted as zero.

Completed vacancy spells will be defined prospectively as calendar-consecutive sequences of the form:

occupied -> explicit zero -> ... -> explicit zero -> occupied.

No abundance magnitudes will be used to choose these spells.

### Stage C — paired population threshold

Only after the exact completed-spell roster is frozen will abundance magnitudes be opened.

For each focal SiteID, the surrounding population is defined as the MasterSite total **excluding that focal SiteID**, preventing the Site's own loss/reappearance from mechanically generating the predictor.

The preregistered comparison asks whether the surrounding population state at recolonization is higher than at abandonment.

## Details of data required

Please provide the raw Seabird Monitoring Programme **Whole Colony / Colony Count** extract for 1986–2024 for non-sensitive species across Britain and Ireland, preferably in CSV, TSV or Excel format.

For every record, if available, please include:

- Species
- Country and County
- SiteID
- Site name
- MasterSite and MasterSite identifier
- Plot / spatial-level indicator
- StartGrid and EndGrid
- Site category / Site type / Site habitat
- survey date or year
- Method
- Unit
- Count
- Accuracy
- Estimate / estimate type
- Comments
- verification / review status
- any explicit nil-return / zero flag
- any surveyed/not-surveyed flag
- any parent/aggregate/merged-site flag

### Site-history metadata are essential

Because the focal test pairs abandonment and later recolonization at the **same physical breeding Site**, I would also be grateful for any provider-supplied crosswalk, change log or metadata that can identify:

- SiteID renames;
- retired/replacement SiteIDs;
- merged or split Sites;
- changes in mapped/site boundaries;
- parent Sites that overlap child Sites;
- child Sites that overlap one another;
- dates when any of those changes took effect.

If a stable physical SiteID history cannot be resolved, that Site will be excluded before occupancy states or count magnitudes are analysed.

### Zero versus missing is also essential

Please confirm, if possible:

1. whether a row with `Count = 0` represents an explicit surveyed nil return;
2. whether absence of a SiteID × year row means not surveyed / no submitted record rather than zero abundance;
3. whether explicit nil returns are encoded separately in any field.

The primary analysis will use only direct observed counts. Imputed or estimated annual counts will not be substituted for missing observations.

## Data format

Electronic, preferably CSV/TSV; Excel is also acceptable.

A separate SiteID/MasterSite history table is entirely acceptable if that information is not embedded in the count extract.

## Additional information

During an earlier public structural audit, Kittiwake records for Flamborough and Filey Coast SPA were inspected to verify the MasterSite > Site hierarchy. That species × MasterSite combination is prospectively excluded from confirmatory analysis because count magnitudes were already visible.

The support thresholds, vacancy-spell definition, SiteID identity requirements and paired threshold estimand were frozen before receipt of the bulk extract and will not be relaxed after ecological outcomes are inspected.

I will follow the SMP Data Access and Use Policy and required acknowledgement wording in any publication using these data.
