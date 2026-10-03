# SMP data request draft — macroecology feasibility audit

## Purpose

Outcome-blind structural feasibility audit for a comparative study of spatial reorganization during seabird population change.

The immediate objective is **not** to inspect abundance trends or effect directions. We first need to determine whether the SMP database contains enough long-term, internally component-resolved abundance panels with stable identifiers to support a preregistered comparative analysis.

## Requested scope

**Survey:** Seabird Monitoring Programme  
**Record type:** colony/breeding-abundance counts only; exclude breeding-success records  
**Years:** 1986–2024  
**Geography:** all non-sensitive SMP coverage that can be released for Britain and Ireland  
**Species:** all regularly monitored seabird species for which abundance counts are available

We would prefer a record-level extract rather than precomputed trends or summaries.

## Requested fields

For each abundance record, where available:

- species name/code;
- country and county/region;
- MasterSite stable identifier and name;
- SiteID and Site name;
- survey date / season / year;
- count method;
- count unit;
- count value;
- count accuracy;
- estimate/range/qualifier field;
- explicit nil-return / zero-status field if this is distinct from Count = 0;
- comments relevant to coverage, aggregation, site definition or count quality;
- recorder/data-provider fields needed to satisfy acknowledgement requirements.

For site structure and provenance, if available:

- SiteID-to-MasterSite crosswalk;
- site creation/retirement/status fields;
- SiteID replacement, merge or split history;
- records identifying parent/merged totals that overlap component SiteIDs;
- any documented change in site boundaries or definitions.

## Secondary plot-level request

If plot-level abundance data can be supplied separately, we would also be grateful for:

- Plot stable identifier/name;
- Plot-to-SiteID crosswalk;
- plot creation/retirement history;
- boundary-change or replacement history;
- indication of Whole Colony versus sample/study-plot count.

The public SMP browser confirms that repeated non-Whole-Colony plot abundance records exist for at least some sites, but we do not assume that these are available comprehensively.

## Why these fields matter

The planned analysis treats a species × MasterSite as a candidate parent population and persistent SiteIDs as spatial components within it. Before looking at abundance magnitudes, we will apply a frozen structural eligibility gate based only on:

- number of persistent components;
- temporal coverage and missingness;
- consistent count units/methods;
- explicit zeros versus unvisited seasons;
- stable component identities;
- absence of overlapping aggregate/child records.

We will not select sites or species based on whether they decline, whether concentration occurs, or the size/direction of any focal effect.

## Planned use

If sufficient eligible panels exist, the data would be used for a comparative ecological study asking whether breeding abundance becomes more spatially concentrated during population decline beyond the concentration expected from proportional thinning and observation error.

The SMP would be fully acknowledged according to the Data Access and Use Policy, and site-specific recorders/organisations would be acknowledged where required. We would not republish the source records wholesale.

## Feasibility question for the SMP team

Before a bespoke extraction is prepared, we would especially appreciate confirmation of:

1. whether SiteID is intended to be a persistent identifier for the same monitored spatial unit through time;
2. whether a history/crosswalk exists for SiteID mergers, splits, replacements or boundary changes;
3. whether explicit nil returns can be distinguished from years in which a SiteID was not surveyed;
4. whether MasterSite totals or merged-site records can be flagged so they are not double-counted with child SiteIDs;
5. whether plot-level abundance records and plot-history metadata are available in bulk.

