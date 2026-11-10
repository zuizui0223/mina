# Geographic scale constrains sea-ice, terrestrial habitat and breeding-niche associations in Antarctic penguins

**Working manuscript v0.1 | 10 November 2026 | exploratory macroecology / draft, not submitted**

> **Scope.** This document is a single-paper synthesis of the source-verified 595-site MAPPPD and 1991–2020 OSI SAF ice datasets, not an assertion that annual Antarctic warming causes vegetation expansion or penguin colony relocation. Results from different subcohorts are kept distinct. All model and uncertainty values are descriptive and post-exploratory unless stated.

## Abstract

Environmental change in Antarctica has reshaped coastal sea-ice regimes and may alter both terrestrial breeding opportunities and the marine niches of penguins. However, geographic covariation among climate, terrestrial environments and breeding populations cannot automatically be interpreted as a uniform response of colonies to warming. We assembled original observed breeding-nest records for three pygoscelid penguins at **595 colonies in 18 Antarctic regions** (2,456 method-consistent species–site–season counts, 1892–2025) and reconstructed nearshore sea-ice concentration (SIC) at all locations from **120 original monthly fields spanning 1991–2020** (71,400 site–months). We contrasted (i) SIC and colony abundance trends over identical observed census years for **100 species–site time series at 77 colonies in seven regions**, (ii) historical SIC with contemporary mapped terrestrial vegetation and observed colony size at **173 vegetation-detected colonies across eight regions**, and (iii) SIC associations with **three pairs of species jointly censused in the same years**. Adélie and chinstrap colony trends showed differently signed within-region descriptive SIC associations (region-demeaned *r* = 0.666 and −0.513; gentoo *r* = 0.017), yet all 250-km spatial-block intervals crossed zero. Across 173 vegetation-detected sites, SIC and log mapped-vegetation area correlated negatively (*r* = −0.384), but this association nearly disappeared within regions (*r* = 0.097; block interval −0.154 to 0.236). Region means accounted for 89.1% of between-site SIC variance. Observed sympatric species nest ratios also lacked robust region-conditioned SIC relationships across all three pairs. These results identify **strongly scale-dependent environmental associations** within the observed Antarctic breeding-colony network, while showing that broad geographic environmental gradients do not alone establish local warming responses, vegetation-mediated demographic change or universal species-specific breeding-niche rules.

**Keywords:** Antarctic penguins; biogeography; sea ice; terrestrial vegetation; colony breeding counts; environmental niche; spatial scale; geographic confounding; macroecology.

## Introduction

Antarctic penguins encounter environmental heterogeneity at several scales. The marine domain varies with seasonal sea ice, prey availability and climate, whereas terrestrial breeding habitat is constrained by ice-free ground, nesting substrate and near-colony land conditions. These axes are often discussed together under climate change, yet they are rarely observed at the same spatial and temporal grain. A positive association between a species and a sea-ice environment across distant Antarctic regions may reflect geographic sorting, while a temporal decline in sea ice at one colony might imply a different demographic association.

The challenge is compounded by survey structure. Antarctic penguin counts are concentrated at known breeding locations, collected with different effort and methods across regions and decades. Absence of a species record is not necessarily absence of the species, and repeated colony observations or colonies exposed to the same ocean cells are not independent climatic experiments. Similarly, a mapped terrestrial vegetation layer compiled across several years is a spatial habitat descriptor, not a time series of annual greening.

Here we separate **three estimands** instead of combining incomparable outcomes into a single warming-to-demography causal chain: (1) within-colony long-term breeding-nest trends versus marine ice trends over the same observed years; (2) between-colony environmental covariation and contemporary observed nest abundance; and (3) marine ice versus the relative nesting balance of species directly co-censused in the same colony-year. The three analyses share a pan-Antarctic source inventory and a common original gridded SIC product. They differ, explicitly, in available biological observations and temporal coverage.

We ask: **At which geographic scales are Antarctic coastal sea-ice, terrestrial habitat and penguin breeding-niche associations expressed, and do associations estimated across regions persist within regions or repeated colonies?** We test the observational limits of generalization rather than presupposing that warming necessarily affects all species in the same direction.

## Materials and methods

### Antarctic colony observations

We reconstructed source-identified, unambiguous MAPPPD species–colony–season records for Adélie (*Pygoscelis adeliae*, ADPE), chinstrap (*P. antarcticus*, CHPE), and gentoo (*P. papua*, GEPE) penguins. The original focal-species dataset included 2,861 rows. We required a known single census method and a non-negative original nest count; within each species–colony series we retained the most frequently used method (lexical tie-breaking without considering outcomes), preserving observed zero counts. This yielded **2,456 observations at 595 source colony identifiers in 18 regions**. Unrecorded species and unobserved years were not assigned zero counts. The coverage does not represent exhaustive surveys of available Antarctic nesting habitat.

We georeferenced source colony identifiers in polar stereographic coordinates and recorded 100- and 250-km spatial grid memberships, used for dependence assessment rather than as invented ecological islands. For analysis of temporal associations, we restricted records to 1991–2020 and fixed an eligibility criterion of at least five different census years spanning at least ten calendar years for a given colony and species. The resulting 100 time series came from **77 colonies across seven regions** (37 Adélie, 27 chinstrap, 36 gentoo).

### Sea-ice reconstruction

We obtained **120 original EUMETSAT OSI SAF OSI-450-a1 v3.1 monthly Southern EASE2 25-km NetCDF fields**, August–November 1991–2020. At each original colony coordinate, we defined a frozen set of valid original ocean pixels within 100 km using the September 1993 marine-status mask and original WGS84 distance; all months were evaluated against the same native membership. The 71,400 possible colony–month values passed the fixed marine coverage gate. Cross-comparison with the previous 40-colony daily-derived SIC product (4,800 same colony–months) showed near-identical values (*r* = 0.99996; median absolute difference 0.057 percentage points). Each species–colony trend used **only the census years actually observed for that series**, and the SIC trend used those identical years.

### Terrestrial environment and contemporary abundance

We used one source-mapped terrestrial vegetation/lichen area within 2 km of each colony from the **2017–2023 Plantarctica composite**. This layer contains mapped positive detections, not independently verified botanical cover at a standardized survey year. The environmental subpanel comprised **173 source sites in eight regions and 14 polar 250-km grid blocks**, with 197 site–species median count records. SIC was the original **1991–2020 mean** at each site. These variables are not synchronous observations of annual ice, vegetation and breeding count changes.

For the land–marine environmental analysis, we calculated Pearson correlations with one observation per site and after subtraction of region-specific site means. We decomposed total site-equal covariance into between-region and within-region components and used 2,000 250-km spatial-block bootstrap resamples to describe uncertainty. A single fixed conditional model related `log1p(observed median nests)` to species, original source region, `log1p(number of observed seasons)`, mean SIC/10 percentage points, and `log1p(mapped vegetation area)`. We did not construct pseudoabsences or select alternative covariates according to their p-values.

### Long-term breeding trends and co-censused composition

For each of the 100 eligible species–colony series, we calculated an ordinary least-squares slope of `log1p(observed nests)` per decade against actual census years, and a corresponding slope of August–November mean SIC (percentage points per decade) over **the same years**. We report the original colony-equal correlation of the two slopes, the region-demeaned correlation, 250-km block-bootstrap uncertainty and geographic omission sensitivity. These slope pairs are observations, not experiments or mechanistic survival estimates.

Separately, we used strictly same-colony, same-year original records in which **both focal species of a pair were actually counted**. The three fixed contrasts were ADPE/GEPE (100 colony-years at 25 sites), ADPE/CHPE (89 at 24 sites) and CHPE/GEPE (168 at 33 sites), in 1991–2020. Each response was `log1p(nests of first species) − log1p(nests of second species)`; the predictor was the exact same site-year's August–November SIC. We kept pooled colony-year descriptors separate from **site-equal average geography** and from within-colony temporal slopes. Site-level slopes required at least three co-censused years spanning at least five years, and species-pair results were evaluated as one fixed three-pair descriptive family. No naive independent colony-year p-values were interpreted.

## Results

### Geographic extent and variation in environmental regimes

The colony network spans **595 source sites** and 18 reporting regions; 2,456 species–site–year original nest counts remain after within-site method consistency screening. Marine SIC for 1991–2020 was successfully reconstructed at all 595 sites. Across the 173 sites with mapped positive terrestrial vegetation, the original SIC–mapped land-area correlation was **−0.3836**. However, its region-demeaned value was only **+0.0969** (250-km block 95% interval −0.154 to +0.236).

Between-region differences explained **89.13% of the observed across-site SIC variance** and 36.28% of across-site log mapped vegetation area variance. The total site-equal SIC–plant-area covariance (−18.669 in the original variable units) separated into **−19.910 between regions and +1.241 within regions**. The within-region contribution thus partly offset rather than replicated the large-scale negative association. These are geographic covariance identities, not causal region effects.

### Species-specific long-term colony trends

For 100 species–colony series at 77 sites, descriptive region-demeaned SIC-trend versus log-nest-trend correlations differed: Adélie **+0.6661** (37 series), chinstrap **−0.5126** (27), and gentoo **+0.0167** (36). Yet the 250-km block 95% intervals were respectively **−0.129 to +0.825**, **−0.903 to +0.640**, and **−0.261 to +0.724**. Geographic replication within species comprised only 9, 5 and 6 blocks, and the chinstrap association changed sign upon exclusion of the South Shetland Islands. Across species, the species-centered pooled trend correlation was approximately +0.018. The data therefore do not establish a universal direction of nest change in response to SIC trends.

### Conditional contemporary breeding-size associations

In the 197 contemporary positive-vegetation site–species records, the fixed conditional model estimated a **+0.1277** coefficient for `log1p(mapped vegetation area)` (250-km block interval **−0.0685 to +0.2848**) and **−0.0861** for 10-percentage-point mean SIC (interval **−0.3609 to +1.5598**). Both geographic block intervals included zero. Model *R*² = 0.2726 reflected all species and geographic terms together and is not the incremental explanatory contribution of climate or vegetation.

### Co-censused species' relative nesting balances

The same-year source data supported exactly 100 ADPE–GEPE, 89 ADPE–CHPE and 168 CHPE–GEPE observations. Pooling site-years yielded weakly negative SIC versus log nesting-balance correlations of −0.169, −0.126 and −0.031, whereas using one average observation per site changed the first two geographic correlations to **+0.181** and **+0.201**. After region demeaning, they became **+0.285**, **−0.069** and **+0.016** (three 250-km block intervals all crossing zero). Within-site temporal slope analyses comprised only **8, 7 and 19 sites**, with the first two pairwise comparisons concentrated in **two** spatial blocks each. Thus repeatedly sampled colonies materially influence the direction of pooled associations, and the subpanel cannot support a continent-wide sympatric ice-response rule.

## Discussion

### Broad environmental association is not a local ecological response

The clearest continent-scale result is a **separation of geographic environmental structure from within-region variation**. Sea ice and mapped terrestrial vegetation covary across distant Antarctic regions, yet this pattern greatly weakens within regions. Consequently, an apparent continental gradient in occupied breeding habitat cannot by itself show that local ice retreat generates terrestrial vegetation expansion, changes recruitment or shifts colony composition. This distinction matters for macroecology because climate, geographic accessibility, nesting substrates, prey habitats and survey placement are jointly spatially structured.

### Different ecological outcomes have different transfer limits

Our longitudinal population subpanel and co-censused community-ratio subpanel use directly observed biological outcomes, unlike analyses restricted to physical habitat. Their signs are not constant across species or across geographic and temporal estimands, and their apparent effects are sensitive to region and spatial block replication. These results do not refute climate-related biological change; rather, they show that **a simple, universal sea-ice–breeding abundance coefficient is not identified by the present uneven colony records**. Cross-site substitution, annual within-colony change and species-composition balance should not be interchanged.

### Marine, terrestrial and temporal niches are not a single measured mediation chain

The longitudinal SIC series and modern mapped terrestrial plant layer measure different temporal objects, and the co-censused species sample is concentrated around the Antarctic Peninsula. Local Signy stomach-content records provide an independent functional marine-niche example (three species over nine seasons, fish/crustacean composition distance versus ice *r* = 0.784; within-three-indicator adjusted *p* = 0.0342), but they do not supply a 595-site functional trait response. Likewise, Palmer and Signy breeding-space concentration, phenological gaps and CMIP6 future climate exposures each have different source units. We therefore retain these as bounded contextual evidence, not replicates proving a unified ice→food→vegetation→breeding sequence.

### Coverage and interpretation limits

The 595 source colonies are not a spatially exhaustive sample of all Antarctic coastlines. Observations are preferentially concentrated at known breeding colonies; observation effort, colony boundaries and historical census frequency vary across sites and decades. Records of only one species are not observations that other species are absent. Plantarctica positive map detections omit sites with unverified or unmapped plants, and the 2017–2023 composite is not an annual ecological greening measurement. Much geographic variation in nearshore sea ice is shared among nearby site codes. Spatial block intervals are a sensitivity tool, not independent experimental replication or global false-discovery-rate adjustment. Although the 595-site 30-year marine atlas is geographically extensive, the environmentally comparable population-trend and multi-species subsets are much smaller.

## Conclusion

Within the currently sampled Antarctic penguin colony network, sea-ice and terrestrial vegetation environments show strong broad regional structure, whereas their local relationships with breeding abundance and co-censused species ratios remain uncertain and species-dependent. **Quantifying the geographic scale of an association is itself essential before projecting it in time or extending it to unobserved sites.** Future causal inference requires independent repeated colony censuses with actual nondetection/effort information, temporally matched land vegetation measurements and marine prey or movement observations. The present results provide a source-reproducible macroecological baseline, not a calibrated forecast of warming-driven changes in Antarctic colony abundance.

## Proposed figures (strict evidence boundaries)

- **Figure 1:** Map of all 595 actually recorded breeding sites and their survey-year support (18 regions), with native 1991–2020 SIC context. Overlays of 173 vegetation-detected sites shown separately; never imply complete 595-site land mapping.
- **Figure 2:** Scatter of 173 independent site-mean SIC vs `log1p` static mapped land area by source region, and explicit between-region/within-region covariance decomposition (89.13% of SIC between-site variance among regions).
- **Figure 3:** Species-specific same-census-year SIC-trend versus log nest-count-trend for 100 site–species series, 250-km block interval summary, region support (9/5/6 blocks).
- **Supplement:** Three pairs' directly co-censused species nest ratios and SIC (100/89/168 source site-years), 197 static habitat abundance model coefficients, source uncertainty and optional local Signy trophic evidence. No extrapolated 2050/2100 penguin nesting forecast.

## Internal source/provenance record (remove from the submitted manuscript)

- [Original pan-Antarctic 595-site source roster](RESULT_JA_20261109.md) and [macro full-source reproducible code](build.py).
- [Main 595-site 3-axis scale analysis with source results](MAIN_MACRO_INFERENCE_20261110_JA.md).
- [173 mapped-land source comparison and 250-km block uncertainty](https://github.com/zuizui0223/mina/actions/runs/42765413899).
- [100 species–colony long-term slope source audit](https://github.com/zuizui0223/mina/actions/runs/42613076334).
- [Same-year co-census fixed three-pair source analysis and independent QA](https://github.com/zuizui0223/mina/actions/runs/42768561120), [Japanese results](COCENSUS_NICHE_RESULT_JA_20261110.md).
- [Original 595 site×120 month OSI SAF acquisition](https://github.com/zuizui0223/mina/actions/runs/42612067836) and [source-reconciled macro scale synthesis](https://github.com/zuizui0223/mina/actions/runs/42766156914).

**Editorial STOP:** Do not reopen single-site Landsat QA, new GAM kernels or SIC time windows to obtain smaller p-values. Do not label static plant-area composites as annually observed greening or assume that model p-values represent unmeasured Antarctic habitat absence or future climate demographic outcomes. The next substantial progress should be **final verified figures and external source-supported sensitivity**, not another disconnected ecological hypothesis.
