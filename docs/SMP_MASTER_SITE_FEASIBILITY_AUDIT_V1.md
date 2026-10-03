# SMP master-site feasibility audit v1

**Status:** outcome-blind structural audit for a possible macroecological extension.  
**Date:** 2026-10-03  
**Frozen Ecology Report:** unchanged.

## Question

Can the UK/Ireland Seabird Monitoring Programme (SMP) supply repeated, component-resolved abundance panels suitable for testing whether breeding abundance becomes disproportionately concentrated during decline across many seabird species and monitoring systems?

## Structural findings from official SMP documentation

### 1. SMP has an explicit spatial hierarchy

The current SMP Online guidance distinguishes:

- **MasterSite** — a grouping that may contain multiple Sites;
- **Site** — a defined count area with a unique SiteID;
- **Plot** — an optional subdivision within a Site.

The 2022 SMP data-request guidance states that Whole Colony Count extracts include `SiteID`, `Site`, and `MasterSite`, with MasterSite explicitly allowed to contain multiple Sites.

The current SMP Online application guide states that:

- pre-existing plots remain available under the site;
- plot names should be kept consistent so future observers can count the same plots;
- site-boundary changes are accepted only when they reflect the area that has always been counted;
- expansion into a new area requires creation of a new Site.

This is materially stronger longitudinal identity support than was available for the Palmer colony-code archive.

### 2. Plot Colony Counts are real but too sparse for the main macro route

BTO Research Report 754 reports Plot Colony Counts for only six species:
Fulmar, Kittiwake, Shag, Guillemot, Razorbill, and Puffin.

Across species, the number of plots per site ranges from one to five and most sites have only one plot. In 2019 only six species × site combinations monitored at least five Plot Colony Counts.

Therefore **Plot is not the primary macroecological component level**.

### 3. MasterSite > Site is the promising scale

The public SMP browser can select a MasterSite and return its child Sites separately.

Structural pilot:
- MasterSite: Flamborough and Filey Coast SPA
- Species: Kittiwake
- child Sites visible simultaneously included Cayton Bay 2, Filey 1, Filey 2, Filey 3, and Flamborough Head and Bempton Cliffs.
- multiple child Sites were observed in the same years.
- child Site rows retained separate counts rather than being collapsed to a MasterSite total.

This establishes that **child Sites can function as repeated spatial components within a MasterSite**.

### 4. Pilot exposure boundary

During the structural audit, Kittiwake counts for Flamborough and Filey Coast SPA were viewed.

Therefore the combination:

> Kittiwake × Flamborough and Filey Coast SPA

is **outcome-exposed** and must be excluded from any prospective confirmatory SMP analysis.

The pilot may be retained only as a data-structure example.

## Data-quality issues that must be handled before outcome analysis

### Missing years

SMP annual data are sparse at many sites. The current SMP trend workflow uses imputation for missing colony counts, but imputation is inappropriate for the present composition endpoint because it could manufacture or suppress relative redistribution among components.

**Decision:** no imputed counts in the primary macroecological analysis.

### Zero versus missing

Current SMP guidance explicitly states that zero counts / nil returns are important and distinguish true absence from non-survey.

**Decision:** recorded zero is an observed ecological state; absent record is missing.

### Count scale

Primary macro panels will use **Site-level / Whole Colony Count records only**. Plot Colony Count records are excluded from the primary route.

### Estimates and merged totals

The public browser can flag estimates (e.g. EST-MID) and comments such as “Total count after merging sites”.

**Decision:** primary eligibility uses direct/non-estimated Site-level records and excludes records explicitly identified as merged totals. Estimate-inclusive analyses, if later needed, must be frozen as sensitivity analyses before their outcomes are computed.

### Unit consistency

Counts can use different biological units among species (AON, AOS, IND, etc.).

**Decision:** within a species × MasterSite panel, all retained components must be measured in one common count unit. No conversion between units is allowed.

### Method consistency

Different methods with the same unit may still have different observation properties.

**Decision:** a retained child Site may not switch among non-missing method codes across the primary panel. Different Sites may use different but temporally stable methods, because a time-invariant Site-specific multiplicative bias is compatible with the fixed-composition null; temporal method drift is not.

## Proposed outcome-blind panel construction

For each species × MasterSite × count-unit combination:

1. keep Site-level Whole Colony Count rows only;
2. exclude outcome-exposed pilot combinations;
3. exclude sensitive-species records if exact location release is restricted;
4. treat recorded zero as observed and absent record as missing;
5. exclude records flagged as estimates or merged totals in the primary route;
6. collapse only exact duplicate rows that are byte-identical; otherwise a Site × year with multiple competing counts is marked ambiguous and unavailable;
7. retain child Sites with at least **10 observed annual counts**;
8. if at least three child Sites remain, define the fixed roster by the deterministic missingness-only algorithm in the eligibility contract;
9. require at least **10 complete years** in which every retained Site is observed;
10. require those complete years to span at least **10 calendar years**;
11. do not inspect count magnitudes, abundance trends, N_eff, or any response statistic before the support gate is frozen and passed.

## Current verdict

**SMP is feasible enough to justify a formal data request.**

The original Plot-level plan is too sparse for a many-species macroecological test. The MasterSite > child Site hierarchy is substantially more promising and is supported by both official field/data guidance and the live public browser.

The next gate is purely quantitative support:

> How many species × MasterSite panels survive the frozen `>=3 Sites × >=10 complete years` criterion?

That number must be established before opening any abundance outcome.
