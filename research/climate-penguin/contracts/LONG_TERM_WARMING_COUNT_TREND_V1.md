# Climate–penguin long-term trend comparison v1 (exploratory design)

Date: 2026-10-29. This design is **post-exploration**, frozen *before opening the new long-term cross-site coefficient*. Previous colony counts and first-stage ERA5 weather/count results were already examined. No claim of prospective confirmation or human-caused climate attribution follows.

## Motivation / distinct estimands

The existing delta-temperature/delta-log-count model measures short-term **year-on-year weather covariation**, not the biological impact of 30-year climate warming. This new outcome is a **within-site log nest-count trend per decade**, compared with the **coincident site-specific ERA5 temperature trend per decade**. It asks whether locations experiencing faster local atmospheric change also exhibit different monitored population trajectories. This is observational, not a causal warming effect. It does not borrow any previously reported exploratory p-value.

## Fixed source and eligibility

- Count series: the already-pinned `historical_count_season_timing.csv` 1991–2020 MAPPPD Adélie nest counts, exactly one interpretable count/method per site×season; no missing-as-zero or pseudo-absence. Exclude unknown and mixed/count-method labels. Fix a method-specific longitudinal series at each site using *source support only*.
- Primary window: both observation conditions before/after chronology check `all_after_september == True`; September 2m ERA5 temperature (not the full year's post-census future temperature).
- Secondary window: `all_after_november == True`, August–November ERA5 mean. Different sample eligibility is **not** evidence of differing ecological effects.
- A site qualifies if one known method has **at least eight positive count seasons** spanning **at least 12 years**. If multiple known methods qualify, choose the one with greater observation support (more years, then longer span, then lexical method), never by decline/increase or strength of climate association. Count zeros/excluded counts do not become zeros in log models. These threshold choices were informed by a structure/eligibility inspection, not pre-data randomization.
- Climate: original SHA-pinned 40-site ERA5 monthly artifact from GitHub Actions run 40856645581, not a mixed-source weather product. Compute temperature slope across the **calendar span of the eligible count series**, using every complete monthly climatic year inside that span, not only years with counts. Require at least 12 climate years and at least 80% availability. Count and temperature trends have units log nest count/decade and °C/decade.
- Preserve original returned 0.25° ERA5 grid coordinates; multiple colony sites sharing the same grid are not independent exposure replicates. Note that 40 sites have only 30 ERA5 grid locations.
- Output both source site-level slopes and aggregate descriptive effects. The between-site unweighted Pearson correlation and least-squares slope (count trend per °C/decade) are descriptive. Also calculate region-centered correlation, equal-grid-collapsed correlation, and leave-one-grid-out range. All are **post-hoc sensitivity diagnostics**, not formal confidence intervals or significance tests. No bootstrap p-values.
- No post-result adjustment of minimum years/span, seasons, geographic rosters, count unit, region weights or climatic predictors to restore a favorable sign.

## Identifiability / stop gate

Before reading the new result, the count **metadata-only** eligibility check showed **16 qualifying sites across 2 regions** for the September primary (14 Victoria Land, 2 Central-west Antarctic Peninsula); November secondary **15 sites across 2 regions** (14 Victoria Land, 1 Peninsula). This cannot establish a general Antarctic-wide cross-region effect.

Macro-generality promotion requires **≥3 represented source regions**, **≥5 qualifying sites outside Victoria Land**, and **≥10 unique ERA5 grid exposures**. If any criterion fails, restrict interpretation to a predominantly Victoria Land descriptive association; no Antarctic-wide mechanism claim, even if a slope looks compelling. A result can be reported as a local observation or as no useful relationship, not only if it has a favorable sign.

The field method and response unit may conceal observer differences, count coverage and population exchanges. An atmospheric warming trend may correlate with other unmeasured factors and cannot by itself distinguish colony abandonment, breeding success, sea-ice transport, food supply, ice-free rock access or anthropogenic warming. Cross-site correlations do not identify individual movement, climate-driven losses or new island habitat. Paper 1 PR189 and Paper 2 PR199 are unchanged.
