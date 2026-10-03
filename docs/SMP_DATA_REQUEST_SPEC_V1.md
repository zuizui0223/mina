# SMP research extract specification v1

## Purpose

Request a non-sensitive research extract sufficient to determine whether the Seabird Monitoring Programme can support a multi-species analysis of spatial redistribution within breeding populations.

The scientific question is whether, during population change, breeding abundance changes only in total or also changes in its relative distribution among repeatedly monitored components.

## Requested records

Colony-count records from 1986 through the latest fully verified year for all regularly monitored seabird species, preferably including explicit zero / nil-return records.

For the initial feasibility audit, coordinates of sensitive colonies are not required.

## Requested fields

Please include, where available:

- master-site stable ID and name
- child-site stable ID and name
- plot stable ID and name
- survey year and exact date
- species
- count
- count unit
- method
- accuracy / estimate category
- explicit nil-return / zero indicator
- verification status
- comments or flags indicating merged sites, reconstructed totals, extrapolated totals or legacy imports
- source survey/census
- date of site/plot creation or retirement
- any versioned site-boundary identifier
- site/plot rename, merge, split or replacement crosswalks

## Clarification questions

1. Are child-site IDs intended to represent the same count area through time?
2. When a site's count boundary changes materially, is a new site ID normally created?
3. Are historical merges/splits/renames available as a crosswalk or change log?
4. Does the database retain individual named-plot counts, or are some legacy plot series stored only as totals across several study plots?
5. Can explicit nil returns be distinguished from unsurveyed/missing site-years in the extract?
6. Are method/count-unit changes flagged consistently enough to screen for longitudinal comparability?
7. Can records labelled as merged-site totals or reconstructed totals be identified programmatically?
8. Are there restrictions on using stable IDs and non-sensitive site names in a reproducible academic analysis?

## Preferred format

CSV or equivalent tabular extract plus a data dictionary and any site/plot identity crosswalk.

## Analysis boundary

Panel eligibility will be determined from identifiers, coverage, methods and units **before** any abundance/concentration outcomes are computed. No request is made for BTO to perform the analysis.
