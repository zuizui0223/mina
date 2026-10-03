# SMP component-structure audit v1

## Why SMP is promising

The Seabird Monitoring Programme has the spatial hierarchy needed in principle for a macroecological test of breeding-space contraction.

Official SMP application guidance distinguishes **sites** from **plots**. Existing plots are intended to be reused, plot names should remain consistent so later counters can survey the same plots, and a whole-colony count is entered explicitly at site level rather than as a plot. The same guide states that boundary corrections should be accepted only when they represent the area that has always been counted; expansion into a new area should create a new site. These rules are unusually compatible with a longitudinal component-composition analysis.

The older Seabird Monitoring Handbook independently describes repeat study plots, recommends repeated use of the same plots/sections, and distinguishes whole-colony counts from sample-plot monitoring.

## What the public portal exposes

A live inspection of the public colony-count browser for Kittiwake (1986–2024) showed these fields:

- Species
- Date
- County
- Site
- Plot
- Method
- Unit
- Count
- Comments

The visible `Site` field can encode a child site together with a master site, for example forms such as `Horn Head 5 (Horn Head)` or `Loop Head 24 (Loop Head Peninsular)`. The `Plot` field in the inspected rows was `(Whole Colony)`, indicating that those child sites themselves were the census components rather than within-site study plots.

The public records also contain estimate qualifiers and comments such as `Total count after merging sites`. Those records cannot be naively mixed with component-level rows because doing so would double count or change spatial grain.

## Main structural risk

The existence of hierarchical names is **not enough**. The macro route requires repeated, contemporaneous counts of multiple persistent components inside the same parent population.

The critical question is therefore:

> How many master-site × species panels contain at least three longitudinally stable components that are counted with a compatible unit and method in at least ten common seasons spanning at least twelve years?

This must be answered **without reading count magnitudes**.

## Frozen hierarchy for the audit

Primary parent:
- master site × species.

Primary component:
1. explicit persistent plot, when plot-level records exist consistently; otherwise
2. persistent child site/subsite whose own count is labelled whole colony.

Never combine:
- a master-site total with its child components in the same annual composition;
- a merged total with the component rows from which it was constructed;
- different census units (AON/AOS/IND) in the same primary panel;
- undocumented split/merge/relabel events.

## Outcome-blind pass criterion

The macroecological route continues only if the structural audit finds at least:

- **20 eligible parent × species panels**,
- **5 species**, and
- **15 distinct master sites**,

where each panel has:

- ≥3 components,
- ≥10 complete common seasons,
- ≥12 years from first to last eligible season.

These thresholds are frozen before SMP count magnitudes are inspected.

If 8–19 panels survive, SMP is treated as a smaller multispecies validation dataset rather than the backbone of a macroecological paper. Fewer than 8 panels closes the SMP route.

## Data-access implication

The public browser allows filtered viewing and email-key downloads. For a comprehensive structural inventory the bulk/data-request route is preferable, because the audit needs site/master-site/plot identity, unit, method, accuracy and comments across many species and years. The first bulk-data pass must suppress the count-magnitude field from all audit outputs.

## Current verdict

**PROMISING, NOT YET PASSED.**

The official design is compatible with stable spatial components, and the public database demonstrably contains nested site identities. The unresolved issue is coverage: whether enough parent × species panels have repeated complete component rosters over long enough spans.
