# SMP component-resolved data-structure audit v1

**Status:** pre-outcome structural audit for a possible macroecological extension. No SMP count magnitudes have been analysed in `mina`.

## Question

Can the Seabird Monitoring Programme (SMP) support repeated, component-resolved breeding-count panels in which a larger colony/site contains multiple persistent monitored subunits that can be followed through time?

This is the minimum requirement for an external test of breeding-space contraction. A site-total time series alone is not sufficient.

## What is verified from official/public SMP material

### Programme scope

- SMP is an annual monitoring programme established in 1986 for 25 seabird species breeding in Britain and Ireland.
- The database contains colony counts and also incorporates historical census material predating the annual programme.
- Public reporting is primarily at species / country / regional population-trend level.

### Public database hierarchy

The public portal exposes separate fields for:

- Country
- Area
- Site
- Count type
- Species
- Year range

Displayed colony-count rows contain:

- Species
- Date
- County
- Site
- Plot
- Method
- Unit
- Count
- Comments

Inspection of public Kittiwake results shows `Site` strings such as:

- `Horn Head 5 (Horn Head)`
- `Loop Head 24 (Loop Head Peninsular)`
- `Cronagarn (Aran Island)`

This demonstrates a visible lower-site / master-site hierarchy in at least part of the database.

### Plot / subsite semantics

Official SMP field forms distinguish:

- Master site
- Site name
- Site code
- Subsite / Plot site name

and instruct recorders to leave the subsite/plot field blank for a whole-colony count.

The SMP field guidance further emphasizes using repeatable site/plot definitions and documenting boundaries so that the same area can be surveyed again.

Therefore SMP has the **data model needed in principle** for component-resolved longitudinal analysis.

### Important public-browser caveat

In the public Kittiwake search inspected for 1986–2024, visible rows showed `Plot = (Whole Colony)`. Some comments indicated `Total count after merging sites`.

Thus the public result table does **not yet establish** that persistent plot-level identifiers are routinely exposed in downloadable historical data. Site naming may itself represent nested subsites, and some historical records may have been merged.

This is the central unresolved point.

### Count semantics

Public rows expose:

- method codes (e.g. 1.1, 1.2);
- biological units (e.g. AON = Apparently Occupied Nests);
- count qualifiers, including estimated values;
- comments.

Any macroecological analysis must harmonize unit and method semantics before reading count magnitudes.

## Data-access structure

The public SMP portal allows browsing and a request-download workflow. For larger data volumes, BTO explicitly directs users to make a formal data request.

A macroecological analysis will therefore require a bulk extract rather than screen-scraping public pages.

## Minimum fields required from a bulk extract

For every colony-count record, request:

1. species identity;
2. observation date / breeding season / year;
3. master-site identifier and master-site name;
4. site identifier / site code and site name;
5. subsite / plot identifier and plot name;
6. a flag distinguishing whole-colony, partial-site, study-plot and merged-site records;
7. count method code plus method description/crosswalk;
8. count unit;
9. count value;
10. lower/upper bounds or estimate qualifier where applicable;
11. count-accuracy class;
12. comments / notes;
13. any record-level validation flag;
14. site-definition metadata or version/change history;
15. parent-child crosswalks for sites that were split, merged, renamed or redefined.

Without stable identifiers or a change-history crosswalk, a component-level analysis would not be confirmatory.

## Structural go/no-go logic

### GO

SMP can support the macroecological test if the bulk extract contains enough species × master-site panels in which:

- at least three component identifiers can be mapped consistently through time;
- the same biological count unit is used within the panel;
- complete component-resolved counts exist for enough seasons to estimate a temporal redistribution trajectory;
- split / merge / rename events can be excluded or reconciled outcome-blind.

### CONDITIONAL

SMP remains usable at a coarser spatial scale if stable **site** identifiers exist under larger master sites even when plot identifiers do not. In that case the component is a site/subsite, not a within-site plot.

### NO-GO for the contraction test

Do not use SMP for the primary macro test if:

- records are predominantly whole-colony totals with no repeated lower-level units;
- component identifiers cannot be followed through time;
- site mergers/splits cannot be separated from biological redistribution;
- count units change incompatibly within panels;
- component coverage is too sparse to form repeated complete rosters.

SMP would still remain useful for ordinary abundance-trend context, but not for testing within-system concentration.

## Current assessment

**Promising but not yet eligible.**

The public schema strongly suggests that hierarchical site/subsite/plot data exist, but the public browser does not prove that a sufficiently large set of long-term persistent component IDs can be extracted. A bulk data request is the correct next gate.

## Scientific role if the gate passes

The penguin work becomes discovery / hypothesis generation.

SMP then provides independent taxonomic and geographic tests in multiple seabird species. The predeclared macro question would be whether declining colonial populations show concentration beyond a proportional-thinning null after unit structure and count semantics are harmonized.

No SMP effect magnitude should be opened until the structural support audit is complete and the analysis contract is frozen.
