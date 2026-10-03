# SMP macroecology feasibility audit v1

**Status:** outcome-blind source-structure audit. No SMP abundance outcome has been used to select species, MasterSites, Sites, years, thresholds, or models.

## Question

Can the British/Irish Seabird Monitoring Programme (SMP) provide repeated, internally component-resolved breeding-abundance panels suitable for an independent test of breeding-space concentration beyond proportional thinning?

## Evidence inspected

Official/public sources inspected before opening any macroecological outcome:

1. BTO/JNCC SMP public data browser:
   https://app.bto.org/seabirds/public/data.jsp
2. BTO SMP Taking Part / data-access page:
   https://www.bto.org/get-involved/volunteer/projects/seabird-monitoring-programme/taking-part
3. SMP Data Request Guidance (August 2022):
   https://www.bto.org/sites/default/files/smp_data_request_guide_aug22.pdf
4. Seabird Monitoring Handbook for Britain and Ireland:
   https://www.bto.org/sites/default/files/seabird-monitoring-handbook.pdf
5. SMP Data Access and Use Policy:
   https://www.bto.org/sites/default/files/seabird_monitoring_programme_data_access_and_use_policy.pdf

## Structural findings

### 1. A nested abundance hierarchy exists

The SMP Data Request Guidance defines abundance counts at specified **Sites**, which may be colonies or parts of colonies. The whole-colony-count extract contains:

- `SiteID`
- `Site`
- `MasterSite`

and explicitly states that a **MasterSite may contain multiple Sites**.

This makes the natural macroecological hierarchy:

> **species × MasterSite = focal breeding population/system**  
> **SiteID = component within that system**

rather than using the `Plot` field as the primary component.

### 2. Individual plot records also exist

A live public-browser audit of Black-legged Kittiwake at Flamborough Head and Bempton Cliffs (2009–2024) showed both:

- Plot `4`: repeated study-plot records from 2009–2019;
- Plot `(Whole Colony)`: separate aggregate colony records in some years.

Thus the database can retain sub-colony plot information in at least some systems.

However, the large-data Whole Colony Count extract schema in the official Data Request Guidance is organized primarily around SiteID / Site / MasterSite. Plot data therefore remain a secondary opportunity, not the assumed primary macro unit.

### 3. Population-monitoring plots are intended to be comparable, but boundaries can change over long spans

The Handbook states that cliff study-plots used for population monitoring should use the same plots and boundaries for consecutive-year comparisons. It also states that the number or boundaries of plots can be changed gradually over longer periods, provided consecutive comparisons use matching plots.

Therefore a repeated Plot name alone is insufficient proof of immutable geometry across decades.

For the macro analysis, long-term identity continuity must be treated as a data-quality gate rather than assumed.

### 4. Missing rows are not zeros

Current SMP guidance explicitly emphasizes that zero counts / nil returns are important and should be recorded because they distinguish true absence from a site not being surveyed.

Therefore:

> **no record = missing survey**, never zero.

Only explicit zero / nil returns may be treated as zero abundance.

### 5. Count units and methods vary among species

Official guidance includes species-specific count units such as AON, AOS, AOB, AOT, and IND. Some species allow more than one abundance unit or method.

A component panel is therefore comparable only if all retained component-year observations use the same frozen abundance unit and a compatible method family.

### 6. Counts can be estimates or aggregates

The official extract includes `Accuracy` and `Estimate` fields, and the public browser displays records marked as estimates. Public-browser comments can also identify records such as “Total count after merging sites”.

These records cannot be silently mixed with mutually exclusive component counts. Aggregate-over-child records must be excluded from component composition.

### 7. The SMP has enough temporal depth in principle

SMP annual monitoring began in 1986 and the database also contains census records from major national surveys. The public SMP report currently documents trends through 2024.

The macro analysis should use verified historical seasons only; the current eligibility contract fixes the outer window at 1986–2024.

## Primary feasibility conclusion

**SMP is structurally promising enough to justify a formal data request and an outcome-blind panel audit.**

The strongest route is not “all plots in SMP”. It is:

> repeated **SiteID** components nested within the same **MasterSite**, for a single species and a single comparable count unit/method.

This directly matches the penguin question at a broader taxonomic scale while avoiding dependence on plot-level geometry being permanently fixed.

## Main unresolved risk

The critical unresolved issue is whether the large extract preserves enough information to identify:

1. mutually exclusive child Sites within a MasterSite;
2. retired / merged / redefined SiteIDs;
3. years in which a child Site was genuinely unvisited versus visited with zero birds;
4. parent aggregate records that overlap the child Site counts.

A usable macro panel requires a reliable way to exclude overlapping parent/merged records and to freeze a stable component roster.

## Decision gate

The macroecology extension proceeds only if the requested SMP extract yields at least:

- **10 structurally eligible species × MasterSite panels**,
- from **at least 5 seabird species**,
- with each panel containing **at least 3 mutually exclusive SiteID components**,
- **at least 10 complete or explicitly zero-coded seasons**,
- a span of **at least 12 calendar years**,
- and one comparable abundance unit/method family throughout the retained panel.

These are support criteria only. They are evaluated before computing concentration, kappa, decline depth, or any focal effect.

If this gate fails, the frozen Ecology Report remains the primary paper and the SMP macro extension is closed without outcome fishing.

## Data request needed

Request a record-level Whole Colony Count extract for 1986–2024 including, where available:

- Species
- Country / County
- SiteID
- Site
- MasterSite
- StartGrid / EndGrid
- site category / type / habitat
- date / year
- Method
- Unit
- Count
- Accuracy
- Estimate
- Comments
- explicit nil-return / zero indicator if distinct from Count=0
- any site status / retired / merged identifier
- any parent-child / Site-to-MasterSite crosswalk
- any SiteID history / replacement / merge / split table

Also ask whether Plot identifiers and plot-boundary history can be included in a separate extract, because those could support a second, finer-scale analysis.

## Freeze boundary

No SMP concentration metric, decline effect, kappa, species ranking, trait association, threshold, or direction of effect may be computed until the structural eligibility audit has run on the requested extract and emitted a frozen eligible-panel list.
