# Beyond proportional thinning: widespread but geographically uneven breeding-site concentration in monitored seabirds

**Full integrated manuscript draft v0.1 — 7 November 2026.** Exploratory, not externally preregistered and not ready for submission. All findings refer to source-matched monitored components and are not evidence of a universal island or causal warming mechanism.

## Abstract

Population decline can alter the relative allocation of breeders among sites rather than simply thinning all sites proportionally. We harmonized historical two-epoch comparisons across 20 seabird taxa from 396 geographical networks, retaining 675 source-compatible network-by-species rows and 378 pairwise species-overlap rows. A ten-year-scaled change in inverse-Simpson breeding-site concentration was contrasted against a finite-count, fixed-share multinomial benchmark conditional on observed totals. Among 663 British–Irish records representing 17 seabird taxa, 436 (65.8%) had positive excess concentration and 15 of 17 taxa had positive network means. Among 479 networks with declining recorded totals, 327 (68.3%) exceeded the fixed-share count-only expectation. Results were geographically uneven; Scotland contributed 497 of 663 eligible records. Twelve Antarctic regional comparisons were less consistent (five positive). The original JNCC source workbook reproduced all 663 rows' original years, Site.ID rosters, count units and adjusted count totals. Original start-point coordinates or site names were duplicated in 12 panels, but 427 of the 651 remaining panels (65.6%) still showed positive excess concentration. Excluding 90 observations from two gull taxa whose national trend comparability JNCC flags left 374/573 (65.3%) positive. However, site boundary histories and survey-effort errors could not be calibrated. Network-block analyses found no four-test-Holm-supported association between historical sea-surface temperature (SST) change and concentration (H3 adjusted p = 0.940), average population decline and two-species spatial overlap (H4D adjusted p = 1.000), or SST change and overlap (H4W adjusted p = 1.000). Strictly comparable adult site-fidelity estimates were unavailable for all taxa. Redistribution beyond a count-only benchmark is frequent in these British–Irish source data, but its causal mechanisms and general physical-island relevance remain unestablished.

**Keywords:** colonial seabirds; spatial redistribution; population decline; source comparability; inverse-Simpson concentration; climate association.

## Introduction

Populations have spatial compositions as well as total abundances. If two breeding-site networks lose the same total number of birds, the remaining birds need not be similarly distributed among monitored breeding components. One network may retain approximately constant relative site shares, whereas another may become concentrated into fewer effective components. This issue is related to established abundance–occupancy and abundance–area relationships. For example, Thorson et al. (2016) contrasted proportional-density and basin models of occupied area across marine fishes. Thus the existence of population-related spatial contraction is not itself new.

At the scale of colonial breeding-site organization, an important methodological distinction remains. Even if latent site shares are unchanged, finite counts at smaller total abundances can make small breeding components appear to disappear or lose relative importance. The relevant comparison is therefore not simply raw abundance decline versus raw spatial concentration: it is a common fixed-component index conditional on the observed total counts. At the same time, matching numerical site identifiers across repeated censuses is not equivalent to proving that physical nesting polygons and survey effort are unchanged.

The British and Irish Seabirds Count (2015–2021) and Seabird 2000 (usually 1998–2002) provide repeated count estimates across many named source sites and taxa. The JNCC released a corrected comparison workbook in July 2024. A separate Antarctic penguin database offers repeated nest-count records, albeit at coarser network scales and much lower replication. The geographically broad comparison creates an opportunity to ask whether changes beyond a proportional count-only benchmark occur across taxa and systems, while avoiding a false assumption that JNCC administrative Master sites, Antarctic regions and within-island census components are ecologically interchangeable.

We addressed four planned directions: H2 predicted stronger excess concentration among species with higher adult fidelity to the same breeding site; H3 predicted stronger concentration where SST rose more; H4D predicted greater overlap in the relative site allocations of two sympatric species where their average decline was stronger; and H4W predicted greater overlap where SST rose more. Historical concentration patterns had already been inspected before these hypotheses were fixed. New SST associations followed a saved prefit analysis contract, but they are not externally preregistered or independent confirmation.

## Materials and methods

### Census sources and fixed cohorts

The primary unit was the source family, original geographical network, species, original count unit, fixed constituent site roster and two corresponding survey epochs. In the JNCC source, a network meant Country × Master site and the components were original Site.ID records. An eligible main panel required at least three matched component IDs, exact agreement of early census years among all components, exact agreement of late census years, nonnegative integer adjusted counts and the same source count unit in the two epochs. Literal missingness was not converted to zero. Parent aggregate records with potential overlapping child entries and duplicated identity keys were conservatively excluded using previously documented metadata rules. Original count units were AON, AOS, AOT, AOB or IND and were never summed across types.

The original publisher workbook was byte-matched to SHA-256 9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4. From 1,483 guarded JNCC candidate parents, 663 were eligible for the fixed two-epoch count benchmark, spanning 17 species and 389 source geographical networks. The dedicated comparable Atlantic Puffin worksheet was used where appropriate, without duplicating entries from the more general worksheet. Source labels such as Razorbil were preserved as computational identities.

Antarctic regional candidates used original MAPPPD region and Site.ID keys. For each region × focal species, the earliest year-pair with at least three common sites measured by compatible original methods was selected, taking the latest possible ending year at the earliest eligible beginning year. The site roster and year pair were frozen without inspecting the biological outcome or climate. Twelve MAPPPD regional species rows from Adélie, chinstrap and gentoo penguins met the count-benchmark requirements. Separately, locally resolved Palmer, Signy and Ross censuses and emperor penguin model summaries were kept for scale comparison, not added as independent macroregional observations where counts might be reused.

The fixed registry included 1,529 candidate network × species records, 680 rows with a computable fixed-share count benchmark, and 675 independent macroprimary records (JNCC 663 and MAPPPD 12). There were also 732 potential species-pair records, of which 378 had a compatible computed count-only comparison. Original terminal zeros and missing records remained explicitly represented.

### Concentration and the null benchmark

Let n(j,t) be the source-adjusted count at constituent site j at epoch t and N(t) the total across the fixed site roster. The recorded share was p(j,t)=n(j,t)/N(t) for N(t)>0. The inverse-Simpson effective component number was D2(t)=1/sum_j p(j,t)^2. We defined the per-decade raw concentration change as Y_raw = (10/dt) log[sum_j p(j,1)^2 / sum_j p(j,0)^2]. A positive value represents stronger concentration of recorded breeding components; it does not measure physical breeding area, an occupied site count or genetic effective population size.

For each eligible row, the finite-count fixed-share benchmark pooled the two observed site vectors to form q(j)=[n(j,0)+n(j,1)]/[N(0)+N(1)]. It simulated 20,000 independent multinomial allocations in each epoch using q(j) and the two original observed totals, and calculated the same concentration statistic. Our main descriptive response was Y_excess = Y_raw − mean(Y_null). Under this particular benchmark, positive values denote stronger observed concentration than the count-only expectation. This is not a calibrated model of changed observation effort, detection or adjusted-count error. The null's simulated quantiles do not provide sampling uncertainty intervals for ecological redistribution.

The associated recorded abundance change was G=(10/dt)log[N(1)/N(0)] where defined. If an endpoint had zero total, its raw status was retained without a pseudocount, and finite-log-change responses were not invented.

### Species overlap

Two-species comparisons used original site identities and exactly the same two census years for both taxa. Each pair had its own matched constituent-site roster and counts recomputed on that common support; totals from distinct main cohorts were not recycled. Spatial overlap was O(t)=sum_j min[p(a,j,t),p(b,j,t)], ranging from zero to one. A comparable two-epoch fixed-share multinomial benchmark for both species yielded excess per-decade overlap change, Z_excess. Pair decline D_pair=−[G(a)+G(b)]/2 was positive when the mean recorded log-growth of the pair was negative. Overlap describes use of the same relative source-site distribution, not direct interspecific competition.

### Ocean temperature and the association plan

Historical SST was linked from the same NOAA OISST v2.1 product, sampling March–May for the northern hemisphere and September–November for the Antarctic. The originally matched site coordinates were assigned the same available marine grid cell within 50 km at both epochs, requiring all six monthly values. Network means gave equal weight to the fixed original sites. W=(10/dt)[mean SST(late)−mean SST(early)] in °C per decade. Available source-verified SST covered 662/675 macroprimary rows and 376/378 species-pair rows. These are endpoint-year seasonal environmental covariates, not proven exposure histories for the complete demographic intervals. NOAA OISST version-processing differences, including updates from 2016 onward, must be acknowledged.

Adult breeding-site fidelity was defined as a conditional annual proportion returning to the *same breeding site* at the next breeding opportunity. Data on natal philopatry, apparent return to a broader study area, survival or qualitative attachment were not converted into exact comparable species-level probabilities. No focal taxon had a source-verified fidelity estimate meeting this common denominator. H2 was therefore not estimable.

The prefit analytical contract for the three remaining associations replaced an earlier random-effects draft with species fixed effects and network-block inference. The change was documented before the SST association coefficients were fitted, because the UK and Antarctic species were completely source-nested and shared original counts across species pairs demanded explicit within-network dependence handling. The H3 equal-weight model conditioned Y_excess on W, G, log(K), log(network spatial diameter), elapsed years and species fixed effects. The joint H4 equal-weight model conditioned Z_excess on D_pair, W, log(K_pair), log(spatial diameter), elapsed years and common species-membership fixed effects for both members. Inference used network-cluster CR1 intervals and 9,999 null-restricted Rademacher wild-bootstrap replicates per coefficient, with a single sign shared by all records from the same network. H2, H3, H4D and H4W retained a four-hypothesis Holm correction family, with unestimated H2 internally assigned p=1 only to preserve multiplicity. Predicted positive coefficients were considered supported only with Holm-adjusted two-sided p below 0.05.

The Scotland-excluded regressions were specified separately as a geographical descriptive sensitivity, not an alternative main hypothesis test. A second matrix implementation independently recomputed every original and sensitivity coefficient and CR1 uncertainty to numerical precision.

### Original source quality and physical climate context

Post-result measurement QA reconstructed the original JNCC source record for every one of the 663 eligible panels. Site.ID, source census year, count unit, numerical adjusted-count totals, fixed roster size and publisher SHA were required to agree exactly. Repeated original source-point coordinates and names among different Site.IDs were flagged, without assuming that the same point meant a double-counted biological colony. Original 2024 publisher comparison sheets include years, site codes, start/end grid codes, coordinates, adjusted counts and publisher-calculated percentages, but no independent per-site observer effort, detection probability or historical nest polygon crosswalk. The source-only QA was descriptive and was never used to refit the frozen associations.

Existing CMIP6 outputs were attached only to geographically identical original Antarctic monitoring sites. Full-network means required every fixed MAPPPD constituent site to match its original source coordinate within 500 m; stringent marine summaries also required all three models' marine cells within 50 km. Coverage of fixed later monitoring counts was recorded rather than treated as a globally representative population fraction. We did not propagate unsupported H3/H4 associations into forecasts of colony abundance or concentration.

## Results

### Widespread excess concentration and uneven source coverage

In the JNCC 663 eligible panels, 436 (65.8%) had positive Y_excess. The median excess was +0.0722 per decade, and the mean of the 17 taxa's separate network means was +0.1269 per decade. Fifteen of 17 taxa had positive network means. Among the 479 with lower later recorded totals, 327 (68.3%) had positive excess concentration. The Antarctic regional comparisons were less uniform: five of twelve were positive. Local Palmer and Signy breeding-component changes remained an independent, finer-resolution evidence source and cannot be pooled as equivalent macroregional observations.

Different source count units all included positive concentration examples. AON: 251/343 (73.2%); AOS: 76/121 (62.8%); AOT: 25/47 (53.2%); AOB: 6/7 (85.7%); IND: 78/145 (53.8%). Their apparent differences do not prove ecological count-unit effects: AOS and AOB each represented just one species, and every unit was confounded with its own taxonomic composition.

### Geography matters

Scotland contributed 497/663 eligible JNCC rows (75.0%), with 333 positive. The Republic of Ireland contributed 70 rows and 39 positive, but its species-equal average was negative (−0.0745 per decade), whereas Scotland's was +0.1381. Omitting Scotland left 103/166 (62.0%) positive, 10 of 14 contributing species with positive means and a species-equal mean of +0.0630. The broad descriptive positive direction therefore did not vanish, but its strength and the represented species varied considerably across countries. The dataset cannot establish a region-independent universal island rule.

### Source comparability and measurement ambiguity

The publisher-recovered source reproduced all 663 JNCC analysis panels, covering 4,217 child site records counted across network × species panels (not unique physical sites). Ten panels included duplicate original point coordinates among distinct Site.IDs and two had duplicate original site labels. When those 12 metadata-flagged panels were separated descriptively, 427/651 remaining panels (65.6%) still had positive excess concentration and 15/17 taxa retained positive network means. The mean of species means was +0.1256 per decade compared with +0.1269 in the complete JNCC set.

The publisher flags low national population-trend comparability for Herring Gull and Lesser Black-backed Gull owing to changes in methods or coverage. When their 90 panels were separated in an explicitly post-result descriptive sensitivity, 374/573 (65.3%) of the other panels remained positive; 14/15 taxa had positive means and the species-equal mean was +0.1416. This publisher warning is not evidence that every local matched source record in those gull taxa is erroneous. Remaining uncertainties include the validity of Site.ID as a stable historical polygon, census-date differences within a year and heterogeneous observer effort and adjusted-count error.

### Predeclared SST and overlap associations were not supported

The frozen network-block analysis covered 662 main rows (387 networks; 20 taxa) for H3 and 376 pair rows (90 networks; 18 taxa) for H4D and H4W. None of the positive directional predictions achieved significance under the four-test family Holm criterion.

| Hypothesis | Coefficient | CR1 95% interval | Raw two-sided wild p | Holm p | Result |
|---|---:|---:|---:|---:|---|
| H3: W to Y_excess | +0.03316 | −0.02138 to +0.08770 | 0.2350 | 0.9400 | Unsupported |
| H4D: D_pair to Z_excess | +0.00616 | −0.03182 to +0.04414 | 0.7576 | 1.0000 | Unsupported |
| H4W: W to Z_excess | −0.01522 | −0.04981 to +0.01938 | 0.4212 | 1.0000 | Unsupported |

Scotland-excluded sensitivity coefficients were H3 +0.04146 (CI −0.04948 to +0.13241), H4D −0.00715 (−0.05985 to +0.04555) and H4W −0.09189 (−0.14771 to −0.03607). The last, more-negative regional coefficient is descriptive sensitivity, not a newly supported primary test. Independent matrix recomputation matched coefficients and CR1 errors to numerical precision. H2 remained not estimable for all 20 species.

### The physical future-exposure overlap is incomplete

Twelve fixed Antarctic macroregional network × species comparisons contained 61 source-component memberships. Thirteen component memberships were matched to the existing CMIP6 atlas by site code and original coordinates. Only 3/12 networks were completely covered for air temperature and 2/12 under the stricter marine-cell requirement. Coordinate-matched sites represented 30.2% of the combined later source counts, and strictly marine-matched sites 17.6%. Those recorded counts do not refer to the same global year. The JNCC networks did not have original location-matched CMIP6 inputs in this analysis. We therefore treated future projections only as a limited physical-exposure audit, not predicted nesting area, colony numbers or extinction risk.

## Discussion

The main descriptive finding is that proportional thinning is an insufficient *count-only* explanation for many British–Irish networks' observed allocation across monitored breeding components. The pattern persists after two transparent source-metadata restrictions. This adds a common, directly reproducible discrete component-composition benchmark to an established broader literature on abundance–occupancy and effective occupied area. It is not the first demonstration of spatial contraction when populations decline, nor is it evidence of a single universal life-history response.

A growing source network can also become more concentrated, and a declining network can become more even. Neither the identity of the initially largest component nor its later status is determined by total decline or the Simpson index alone. Existing JNCC work on site-leader switching uses the same original counts and a different analysis contract; those results provide context but are not independent tests of the present concentration result.

Uniform SST change was not a supported macro predictor, nor were average decline and temperature change supported explanations of increased between-species spatial overlap. This does not establish that climate or competition is ecologically irrelevant. A two-epoch SST contrast may fail to capture local food supply, prey access, exposure during critical breeding weeks, spatially heterogeneous habitat opportunity or colony-level memory. The regional contrast and Scotland-excluded H4W sensitivity suggest that a single pooled coefficient is inadequate as a causal or universal description. Importantly, those observations do not authorize post-result threshold or variable selection to recover a positive hypothesis.

Source quality remains the principal barrier to a stronger claim. The original comparative workbook lets us confirm numerical and structural reproducibility, including matched years and count units, but not a calibrated observation process. Matching original Site.IDs is weaker than verifying fixed nesting polygons; equal original start-point coordinates for different IDs create a visible caution in a small number of panels, yet their scarcity does not prove the remaining polygons were stable. Adjusted counts and an idealized multinomial null cannot exclude heterogeneous survey effort or detection error. The central conclusion must therefore say 'excess concentration of monitored adjusted counts relative to a count-only benchmark', not 'confirmed ecological concentration beyond measured census error'.

For island ecology, the distinction is especially consequential. A JNCC Country × Master site is often an administrative cluster of coastal sites and is not a direct physical-island unit. The Antarctic regional dataset has few networks and a very different sampling hierarchy. Without source-independent historical island polygons, regional species-specific observation uncertainty, or measurements of predator and nesting opportunity, neither physical isolation nor island–mainland differences can be assigned a causal role. The separately frozen within-island Palmer/Signy results are informative at another grain, but combining them numerically as independent evidence would create pseudoreplication.

The general inference is therefore conditional but usable: across the eligible JNCC data, restructuring in the relative abundance of matched monitored breeding components is frequently stronger than expected under fixed site probabilities and finite count allocation alone. Its geographical variation and lack of a uniformly supported SST/decline predictor identify where new independent site-quality, observation-effort and nesting-boundary information would be needed. Future ocean and land climate scenarios are only physical context until a biologically transferable response is demonstrated.

## Proposed figures and supplement

**Figure 1.** Geography and hierarchy of JNCC Country × Master sites and MAPPPD regional networks. Clearly distinguish administrative monitoring networks, physical islands and within-island census codes; do not infer one from the other.

**Figure 2.** Distribution of Y_excess by species, with original network counts and country strata; highlight source-data skew and avoid treating null-simulation bands as observational confidence intervals. Supplement count-unit and source-quality subsets.

**Figure 3.** H3/H4D/H4W coefficients and CR1 intervals on original units, Holm-adjusted p, H2 as not estimable. Scotland-excluded coefficients are a separately labelled supplementary sensitivity.

**Supplementary source audit:** Original survey years, fixed Site.ID counts, matched count units, 4,217 original site records summed across JNCC analysis panels, 12 collision-flagged parent rows and 90 publisher-warning gull rows.

**Supplementary physical exposure:** CMIP6 four scenarios with strict source-site coverage for air temperature, sea ice and salinity; explicitly do not present predicted future birds.

## Verified reference anchors (complete manuscript bibliography before submission)

- Joint Nature Conservation Committee, *Seabirds Count: the fourth breeding seabird census*. Publisher summary and methods/coverage limitations: https://jncc.gov.uk/our-work/seabirds-count/
- JNCC, *Seabirds Count Datasets*, revised 11 July 2024. Original comparison workbook: https://jncc.gov.uk/resources/63f0ea40-485d-46dd-b967-150df90a7b2b
- Thorson, J. T., Rindorf, A., Gao, J., Hanselman, D. H. & Winker, H. (2016). Density-dependent changes in effective area occupied for sea-bottom-associated marine fishes. *Proceedings of the Royal Society B*, 283, 20161853. https://doi.org/10.1098/rspb.2016.1853
- NOAA NCEI, *Optimum Interpolation Sea Surface Temperature v2.1*. https://www.ncei.noaa.gov/products/optimum-interpolation-sst
- Coulson, J. C. (2016). A review of philopatry in seabirds and comparisons with other waterbird species. *Waterbirds*, 39, 229–240. https://doi.org/10.1675/063.039.0302
- Original MAPPPD and Palmer/Signy census provenance: the frozen source manifests and existing Ecology Report references in the mina repository. Complete full-format author citation verification before external submission.

## Editorial hold before submission

This manuscript is an evidence-led working draft rather than an approved publication. It requires figure generation and inspection, final citation and permissions review, scientific review of original count-adjustment/effort comparability, and coauthor approval. Do not replace the original H3/H4 tests or treat post-result source-quality subsets as preregistered positive findings. No central island-specific mechanism, causal warming result or numerical 2050–2100 breeding forecast has been established.
