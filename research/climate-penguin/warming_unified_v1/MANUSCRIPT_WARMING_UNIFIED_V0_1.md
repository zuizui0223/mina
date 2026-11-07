# Breeding-community change and marine–temporal niche separation are differently associated with Antarctic sea ice

**Integrated warming-first manuscript v0.1 — 7 November 2026**

**Research status:** One proposed climate-centered empirical paper. Original source analyses, cohort definitions, original census data and historical climate values are unchanged. This is an openly post-result synthesis plus a new same-year source join, **not external preregistration**. The paper does not identify causal warming effects or project future penguin breeding numbers.

## Abstract

Antarctic warming alters the physical context in which penguins breed, but different components of their ecological niches may not change in concert. We synthesized site-matched breeding counts, observed satellite sea ice, original stomach-content records, breeding phenology and future physical climate projections for Adélie, gentoo and chinstrap penguins, keeping geographical and temporal observational units distinct. In six repeatedly monitored sites in two regions where Adélie and gentoo penguins bred throughout shared observation years, Adélie nest counts declined and gentoo counts increased at all six sites. Nearshore August–November sea ice declined during the full 1991–2020 series at all six sites, whereas September sea ice estimated only for the actual breeding-census years increased at four sites. At Signy Island, we joined nine identical breeding seasons (2001–2009) from independently archived diet and hatching sources to the same nearshore August–November ice series. Across 422 original Adélie and gentoo stomach samples, their mean seasonal fish-fraction contrast was positively associated with ice concentration (r = 0.781; leave-one-year range 0.685–0.883), whereas the chinstrap–Adélie mean hatching-date offset was weakly associated with that same ice series (r = −0.066; leave-one-year range −0.355 to +0.152); the two indices were also weakly correlated (r = −0.052). The earlier full three-species stomach analysis (772 stomachs, nine climate seasons) and the published longer hatching series support the distinct observational context, not independent replication. For the six breeding-composition sites, CMIP6 SSP5-8.5 late-century physical forcing indicated mean surface-air warming of +4.35°C across all six sites and mean sea-ice change of −23.94 percentage points across four strictly marine-supported sites. We interpret these observations as **unequal coupling of breeding-community composition, marine diet and temporal partitioning to the measured ice environment at different temporal and spatial grains**. The datasets do not establish that ice loss caused species replacement, that changed diets altered competition, or that future climate can yet forecast colony numbers.

## Introduction

One of the central ecological challenges of Antarctic warming is determining which biological responses are connected to a changing physical environment and at what temporal scale. Regional temperature rise, shrinking sea-ice habitat, marine food-web change and changing terrestrial nesting opportunities can co-occur, but their ecological mechanisms and sampling scales differ. Treating all of these processes as one synchronous penguin response can produce misleading attribution.

Adélie penguins are commonly associated with sea-ice habitats, while gentoo and chinstrap penguins often differ in foraging habitat use and breeding geography. These are ecological tendencies, not a categorical ranking of which species benefits from every low-ice year. Longitudinal colony counts directly address breeding-community change but may not identify its proximate drivers. Diet samples reflect a later and narrower part of the marine feeding niche, and breeding phenology concerns seasonal timing rather than abundance.

Previous work already demonstrated that the Adélie–chinstrap seasonal gap at Signy Island is substantial and that temperature responses can move their dates together while retaining asynchronous breeding (Clewlow et al. 2019, DOI 10.1111/1365-2656.12919). Long-term satellite-derived Adélie diet changes have also been linked to sea ice and population change (Youngflesh et al. 2026, DOI 10.1016/j.cub.2026.06.028). We do not re-label either relationship as a new discovery. The present study adds a source-audited comparison of **where apparently reciprocal breeding-community change occurs, which historical ice time window it accompanies, and whether marine and temporal niche differences co-vary with one identical ice series in the same nine Signy breeding seasons**.

The guiding question is therefore: **Are the ecological signatures of a warming Antarctic sea-ice environment aligned across long-term breeding-community composition, seasonal diet separation and phenological separation?** We evaluate this observationally, distinguishing existing positive measurements from unsupported future biological transfers and unmeasured land-vegetation mechanisms.

## Methods

### Evidence grains, original data and non-independence

The analysis preserves three observational grains rather than pooling them as replicated climatic experiments: (i) six original MAPPPD nesting sites monitored over shared years in two Antarctic Peninsula/South Shetland regions; (ii) one Signy Island marine-diet time series with nine common breeding seasons; and (iii) annual mean hatching-day records at Signy from another source with 17 original seasons, subset to the nine exact matching diet years for the integrated comparison. Six sites are not six independent regional climate treatments, and 422 original stomachs do not provide 422 independent ice-year observations. Where sites share an original marine climate grid cell, that dependence is retained in coverage reporting.

Input original source files, source-relevant report files, fixed source Git object hashes and the new paired comparison rules are documented in the analysis contract under the warming_unified_v1 folder. The original UK/Ireland JNCC two-epoch concentration study uses different monitoring units and is **not included as climate evidence** in this paper.

### Long-term community change and distinct sea-ice observation windows

We used the previously defined strict cohort of six original sites where Adélie and gentoo penguins both had positive recorded nest counts at every common census year. Source comparisons required the same source Site.ID, known method, five or more common years and a span of at least ten calendar years. Both species' original census count totals were used as measured; missingness was not converted to zero or imputed. Site identifiers were ARDL, BISC, LION, LLAN, PCHA and PETE, representing two original regions. Their actual common years, rather than all calendar years, defined the biological observation window.

For each site, we retained the already computed sign of the slope of log(gentoo/Adélie) recorded nests per decade, and the direction of the absolute nest-count trajectories in the same shared-year cohort. To separate climate time scales, we compared the nearshore September sea-ice concentration trend evaluated at the actual shared census years with the August–November SIC trend over all 30 years from 1991 through 2020 at the same fixed source locations. The results are ecological and environmental co-observations; the difference between a sampled-year trend and a full-period trend does not identify a temperature-caused population shift.

### Nine-season same-island, same-climate diet/phenology join

The source-controlled annual stomach table stored with the prior detailed diet analysis contains Adélie and gentoo records for 2001–2009, with 349 and 73 stomach samples, respectively. We joined one species-year mean fish fraction per species to the independently archived 17-season Signy mean hatching-date record on the literal breeding-season start year. The source temperature/ice supports were independently verified to refer to the same Signy GOPT August–November sea-ice series, including an existing factor-of-ten encoding difference. All nine years were required; no season was chosen by correlation magnitude.

We defined the annual marine contrast as mean gentoo fish/(fish+crustaceans) fraction minus the corresponding Adélie fraction. This new two-species common-year contrast is **not identical** to the original three-species diet statistic, gentoo minus the average of Adélie and chinstrap. The original separate three-species analysis comprised 772 stomachs across the same nine climate years and found r approximately +0.784 with August–November SIC; it remains supporting context, without any invented annual chinstrap fractions in the new joined table.

We defined the temporal contrast as the mean chinstrap hatching day minus the mean Adélie hatching day in the same season. Importantly, this temporal pair uses chinstrap and Adélie whereas the diet pair uses gentoo and Adélie; neither is a complete three-species phenology–diet interaction. We calculated descriptive Pearson correlations between each contrast and the same observed annual SIC, between the two contrasts, and between each species' absolute mean hatching day and SIC, all on **n = 9 climate years**. We also checked the range of each correlation when one climate year was omitted. No new confirmatory p value, causal path model or differential correlation test was selected post hoc. The Adélie hatching colony changed from A41 to A39 in 2003, so historical timing estimates also contain a site-method comparability caution.

### Future physical climate support and unobserved land mechanisms

At the original six composition sites, we audited the existing CMIP6 physical source for three climate models under SSP2-4.5 and SSP5-8.5, each for 2041–2060 and 2081–2100 relative to the source model's 1995–2014 baseline. Surface air temperature was supported at all six sites. **Two source sites (PCHA and PETE) failed the original marine-grid-within-50-km criterion**, so sea-ice concentration and sea-surface salinity were averaged only among four verified marine locations. We used site-equal rather than count-weighted means; ocean grid fingerprints were tracked so repeated values were not treated as independent marine projections. Differences in salinity remain in original CMIP6 source units.

No climate-to-breeding response coefficients were transferred from the historical community or Signy models into future counts or fish fractions. Prior 39-site Adélie historical SIC–nest trend associations improved some geographic prediction comparisons but did not transport reliably into the observed two-period within-site response, and the 216 annual growth intervals with three oceanic covariates did not improve temporal/geographic holdouts over simple baselines. These are explicit forecasting constraints.

Existing ice-free area, mapped vegetation and NDVI data do not currently establish synchronized, source-quality-controlled changes to the nesting polygons at these six sites. We therefore treat terrestrial vegetation and nesting opportunity as missing mechanistic support, not as an observed zero effect or as a proven warming-to-greening-to-colony sequence.

## Results

### Reciprocal breeding counts and climate time-window mismatch

All six strict shared-year Adélie–gentoo site comparisons had declining absolute Adélie counts and increasing absolute gentoo counts; the corresponding true log(gentoo/Adélie) nest ratio slopes were positive at all six sites. This observation improves upon the older shorthand that 13 out of 13 available source pairs showed rising log(1 + count) contrasts, because some earlier pairs included one species unobserved or zero in several years. The strict cohort comprised two geographical regions and had 67 matched site-years and 45 actually consecutive-year intervals; those intervals are neither independent population experiments nor independent ocean-climate series.

Across the complete 1991–2020 August–November satellite SIC record, all six original sites had negative sea-ice concentration slopes. At the *actual breeding count years* September SIC had positive slopes at four of the six sites. August–November SIC at just those census years had positive slopes at only two of six. Thus the community trajectory had a consistent observed direction while the environmental direction depended on month and whether all years or only count-observed years were considered. The result rules out a simplistic claim that every site experienced a monotonic low-ice sequence in the exact years in which the breeding counts were measured. It does not rule out climate mechanisms operating through long-term means, prey resources or lagged conditions.

### Paired seasonal marine and temporal niche signatures

For the nine identical Signy climate years 2001–2009, 422 stomachs contributed to the source-level mean Adélie and gentoo fish fractions. The annual gentoo-minus-Adélie fish fraction contrast averaged **0.3614** and was positively correlated with GOPT August–November SIC (**r = +0.7814**). The correlation remained positive in all leave-one-season comparisons (range **+0.6849 to +0.8827**).

In the same nine years, the chinstrap–Adélie hatching offset averaged **29.22 days**, and its correlation with that identical SIC series was **r = −0.0661**. Deleting one year gave correlations from **−0.3552 to +0.1520**. The marine contrast and hatching-day offset were nearly uncorrelated (**r = −0.0518**). Both species' absolute mean hatching dates were positively correlated with this nine-year ice series (Adélie **r = +0.4160**; chinstrap **r = +0.4389**), but these values do not establish statistically equivalent climate slopes.

The signs and magnitudes are compatible with differences between sea and seasonal-time niche descriptors. However, different species pairs underlie the two contrasts, and a difference between two descriptive Pearson correlations is not by itself proof that climate affects one niche axis more than the other. The original 17-year hatching analysis showed that both absolute dates shifted in relation to SIC while the interspecies timing offset was comparatively stable (17-year gap–SIC r = +0.0782); published work has already demonstrated substantial allochrony and its climatic relationship. The previous full three-species 772-stomach diet series gave a related but nonidentical marine statistic (r = +0.7839), without furnishing an independent nine-year replication.

### The verified future physical environment is changing; the biological future remains uncalibrated

| CMIP6 scenario | Period | Mean air Δ°C, all six sites | Mean SIC Δpercentage points, four verified marine sites | Mean sos change, native units |
| --- | --- | ---: | ---: | ---: |
| SSP2-4.5 | 2041–2060 | +1.66 | −11.27 | +0.004 |
| SSP2-4.5 | 2081–2100 | +2.51 | −19.96 | −0.102 |
| SSP5-8.5 | 2041–2060 | +1.92 | −13.96 | −0.011 |
| SSP5-8.5 | 2081–2100 | +4.35 | −23.94 | −0.203 |

All six sites were projected to warm in all three model members for every condition, and all **four marine-supported** sites showed model-consensus SIC decreases. This is a comparison of future physical conditions at the *same sites used for the historical nesting result*, with source-verified missingness. It is not a population projection; no support exists for converting a specified increase in tas or decrease in SIC to an exact future number of nests or date of species replacement.

## Discussion

### Which response is most coherent across a warming system?

The integrated pattern is that apparently reciprocal long-term breeding-community change co-occurs with falling multidecadal marine ice cover at the six strictly monitored sites, while short-window sea-ice conditions do not uniformly carry the same directional trend in the exact census years. A separate nine-year Signy comparison indicates that the measured fish-fraction niche contrast and hatching-season gap need not exhibit the same association with a shared annual sea-ice series. Consequently, the response of Antarctic penguins should be represented as a set of connected but **not equivalent** ecological trajectories rather than one temperature-to-population coefficient.

This distinction is a scientific contribution only within strict limitations. A spatial count pattern and a seasonal foraging sample do not establish a causal pathway linking climate to population replacement. Long-term trends can arise through regional demography, prey and habitat change, changing colony identities or observation practices. Hatching-gap dynamics can be constrained by nesting substrate exposure and the species' breeding schedules, while stomach fractions reflect different foraging seasons and sampling protocols. We did not model all three axes in the same individuals or physical colonies, and therefore cannot infer direct interspecies competition or causal niche-mediated demographic replacement.

### Distinguish our evidence from established work

Clewlow et al. (2019) identified resilient Adélie–chinstrap breeding asynchrony and associated stage-specific foraging distribution, so we do not claim discovery of an approximately 29-day gap. The Signy hatching time series is a source-exact temporal context for the new same-year pairing. Youngflesh et al. (2026) linked Adélie dietary proxies to Antarctic sea ice and demographic history; our stomach-based Gentoo/Adélie comparison targets a different, two-species seasonal contrast, not the first evidence that penguin diets respond to sea ice.

The novel synthesis is the explicit coexistence of three source-grounded observations at their correct grain: reciprocal nest-count changes in a strict same-site cohort, seasonal trophic partitioning corresponding to contemporaneous nearshore SIC, and an apparently maintained interspecies hatching offset under the same years' sea-ice variation. The ecological inference is **axis- and timescale-conditional**, not an experimentally supported warming mechanism.

### Why not issue 2050/2100 colony forecasts?

Physical CMIP6 forcing is clear for the supported sites but historical biological transfer has not been calibrated. An earlier 39-site Adélie spatial relationship between mean historical SIC and long-term nest trends was positive (r = +0.622), yet the corresponding 23-site early/late temporal comparison had a weaker association (r approximately +0.269). Annual ocean SIC, temperature and salinity regressions failed to produce stable time/space holdout improvements. The existing four-variable conditional breeding-time scenarios reversed sign under model specification changes. Therefore a climate projection does not license a projection of future absolute nest counts, replacement rate, diet partition or hatching-day shifts. Any numerical future biological forecast would require independent chronological and geographic validation and explicit species-specific life-history, observation and mechanistic constraints.

### Land habitat and physical island structure

Land-based nesting substrate, snow, ice-free exposure and vegetation may influence where penguins can breed, but existing vegetation sources are insufficiently aligned to nesting polygons and source field dates. In particular, NDVI is not interchangeable with biological greening, and penguin guano or snow changes could affect reflectance. We do not claim that penguins left specific sites and plants subsequently colonized them. Earlier Palmer and Signy within-colony concentration studies remain genuine spatial-demographic observations but are not directly attributable to temperature or ice from these combined data, and the UK/Ireland seabird concentration macro study is a separate research output.

## Figures to generate from verified source data

**Figure 1 (primary).** Six strict same-site reciprocal community changes, with paired Adélie and Gentoo endpoints and a second aligned panel contrasting observed-census-year September SIC trends against full 1991–2020 August–November SIC trends; explicitly show two source regions.

**Figure 2 (primary).** Nine exact shared Signy climate years: (a) Gentoo–Adélie annual fish-fraction contrast versus source SIC; (b) chinstrap–Adélie mean hatching offset versus same SIC. Show each climate year once, with no stomach-level pseudoreplication. State the compared species are different in the two panels.

**Figure 3.** Four CMIP6 future climate conditions at six source sites (tas), with ocean SIC and sos only for the four sites having verified marine cells. Display that PCHA and PETE do not qualify for a 50-km ocean value, not a zero change.

**Supplementary evidence.** Original strict 6-site source and source-year slopes; previously examined full three-species Signy 772-stomach contrast and its non-independent overlap with two-species data; 17-year hatching series and Clewlow provenance; temporal-transfer tests; annual historical ocean forecast failures; annual NDVI source support limits; earlier colony concentration at different scales.

## Submission and claim boundary

**Current state: empirical one-paper working draft, not ready to submit.** New common-year numbers are source-joined after prior outcomes were inspected; original temperature, ice, stomach and nesting source records have been preserved. A final paper requires fully referenced observational provenance, spatial/temporal independence assessment, reviewer-friendly source units and figure verification. No part of this text converts historical association into a proven warming effect or a calibrated future breeding prediction.

**Reference anchors:** JNCC is intentionally not used as warming evidence. Ratcliffe et al./Clewlow et al. (2019), J Anim Ecol DOI 10.1111/1365-2656.12919; Youngflesh et al. (2026), Current Biology DOI 10.1016/j.cub.2026.06.028; original MAPPPD source and Antarctic site count manifest and BAS original Signy stomach/hatching source manifests in the connected mina project.
