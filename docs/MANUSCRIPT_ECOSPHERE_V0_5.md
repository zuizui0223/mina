# Common decline, divergent endpoints: multiscale demography across Antarctic penguin breeding islands

**Ecosphere-oriented manuscript v0.5 — revised after serial-structure-preserving N_eff diagnostics; core ecological endpoints closed**

## Abstract

Seabird breeding islands separate a marine trophic environment from a discrete terrestrial reproductive patch, creating a useful setting for asking how common regional change is translated into local population outcomes. We analysed a complete 1991–2017 annual census of five neighbouring Adélie penguin (*Pygoscelis adeliae*) islands near Palmer Station, West Antarctic Peninsula, together with broader regional breeding-site records and independent spatial reconstruction from Torgersen Island. The five populations shared a strong long-term decline (PC1 of standardized log abundance = **96.4%**), while annual growth was only moderately synchronized (median pairwise *r* = **0.373**); this contrast is treated as expected timescale-dependent synchrony rather than a novel synchrony phenomenon. Local endpoints nevertheless diverged: Litchfield reached extinction, several islands persisted at very low abundance, and the nearby non-island Biscoe Point benchmark underwent strong Adélie-to-gentoo replacement. Prospectively bounded annual and low-frequency sea-ice-duration models and an October snowfall × snow-prone-habitat model did not satisfy their directional and held-out validation rules. Within islands, effective colony number had a positive conditional coefficient (**+0.1168**) with next-year growth, but its small held-out MSE gain (**+0.00103**) was not unusual under 20,000 synchronized year-block permutations (*p* = 0.262), so the predictive claim remains withdrawn. The coefficient itself remained extreme under 100,000 island-wise circular shifts that preserve each island's temporal ordering (*p* < 0.00001) and under an exact 416-member joint-shift sensitivity preserving cross-island covariance among the four persistent islands (*p* = 0.0024). Circular-shift Poisson/Gamma–Poisson coupling simulations also rarely generated an observed-scale coefficient (largest *p* = 0.0078), supporting retention of N_eff only as a structured-null-robust conditional association. Independent Torgersen mapping documented habitat-structured attrition from 23 historic active subcolonies to five active footprints by 2022. Together, the results show that a common regional demographic direction can terminate in different local ecological states within an externally subsidized island system, while the mechanisms of local collapse remain patch-specific and only partly resolved.

**Keywords:** Adélie penguin; breeding patches; central-place foraging; island ecology; long-term monitoring; population dynamics; seabird islands; spatial synchrony

## Introduction

Island ecology asks why populations and communities diverge among habitat patches embedded within a broader regional setting. Seabird islands are a particularly strong form of land–sea coupling: birds acquire resources in marine food webs, return to land to reproduce, and transport marine-derived materials that can restructure terrestrial soils and communities [@mulder2011; @grant2022]. Most seabird-island work has therefore emphasized what seabirds do to islands. Here we ask the reciprocal demographic question: **how does the internal state of a terrestrial breeding patch condition the fate of a marine-foraging population?**

In many terrestrial systems, the patch contains both breeding habitat and much of the trophic resource base, making local resource availability, competitors, predators and physical habitat difficult to separate. Antarctic penguin breeding islands differ in a useful way. Pygoscelis penguins forage at sea but reproduce on discrete terrestrial patches, so the food environment is largely external to the breeding island while nesting habitat remains spatially localized. We refer to these as **externally subsidized breeding islands**: marine conditions can impose shared regional forcing, while snow, topography, drainage, access and the spatial organization of nest sites can generate local filters. The phrase describes the demographic geometry of the breeding system; it does not imply that terrestrial biotic interactions are absent.

The Palmer Archipelago is well suited to resolving these scales. Adélie penguins near Palmer Station have experienced major long-term population declines, while gentoo penguins have expanded and some breeding sites have undergone species replacement [@pickett2018; @checastaldo2023]. At the same time, neighboring islands differ in breeding habitat and snow accumulation. Long-term work on Torgersen and Humble islands shows that regional environmental conditions interact with island geomorphology to produce local variation in breeding phenology [@cimino2019]. Earlier work proposed that breeding-habitat quality, shaped by geomorphology and snow deposition, contributes substantially to differences among local Adélie populations [@fraser2013]. More recent spatial reconstruction on Torgersen independently mapped strong subcolony loss and showed that persistence was non-random with respect to terrain and snow-related habitat features [@cimino2025].

These observations raise a scale problem, but not a new synchrony paradox. Spatial population synchrony is expected to depend on temporal scale because dispersal and spatially correlated environmental variation can act differently across frequencies, and multiple Moran-type drivers can interact rather than map one-to-one onto observed synchrony [@abbott2007; @desharnais2018; @anderson2019; @sheppard2019; @reuman2025]. We therefore treat the coexistence of a common multi-decadal decline and weaker annual synchrony as established dynamical context. The ecological question here is what that regional direction becomes locally: persistence, extinction, species replacement, or contraction of the internal breeding network.

We combined three levels of evidence without treating any one scale as a complete mechanism. First, we quantified shared and island-specific structure in the synchronized 27-year Adélie census. Second, we used the broader APBP/MAPPPD record to distinguish local assembly endpoints across nearby breeding sites. Third, we prospectively bounded simple regional sea-ice and terrestrial snowfall formulations and evaluated within-island colony organization, followed by explicit uncertainty and count-error diagnostics and independent Torgersen spatial triangulation.

We used the synchronized decline as descriptive context rather than as a novelty test. For the bounded mechanism analyses, support required the predeclared coefficient direction and improved held-out performance. For colony organization, the original positive coefficient and held-out gain were subsequently subjected to a frozen synchronized year-block permutation diagnostic and to fixed count-error simulations; these post-positive diagnostics determine the final interpretation reported here.

## Materials and Methods

### Study system and data roles

The primary demographic analysis used five Adélie breeding islands monitored by the Palmer Station Antarctica Long Term Ecological Research program: Christine (CHR), Cormorant (COR), Humble (HUM), Litchfield (LIT) and Torgersen (TOR). We used the public colony-level breeding-pair census, aggregated annually within island. The synchronized panel spans 1991–2017 without missing island-years and contains 27 census seasons. The source table and its checksum are frozen in the mina reproducibility receipts (Palmer LTER data DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e).

We used the Antarctic Penguin Biogeography Project (APBP/MAPPPD) as a broader assembly context rather than as the synchronized primary time series [@checastaldo2023]. An outcome-blind local inventory within 20 km of Palmer Station identified six true-island breeding sites—Torgersen, Litchfield, Humble, Christine, Cormorant and Dream—and retained Biscoe Point on Anvers Island as a non-island benchmark. This distinction matters because Biscoe Point shows strong Adélie-to-gentoo replacement, whereas several true islands show decline or vacancy without equivalent gentoo replacement.


### Five-island scale separation

Colony-level breeding-pair counts were summed to island-year totals. For each island, we transformed abundance as \(\log(1+N)\). To quantify the common long-term component, we standardized each island's 1991–2017 log-abundance trajectory and performed principal component analysis across islands. We also calculated annual log growth,
\[
g_{i,t}=\log(1+N_{i,t})-\log(1+N_{i,t-1}),
\]
and Pearson correlations for all ten island pairs.

We decomposed total log-abundance variation using additive ordinary least squares models containing island and year factors. We report the fractions uniquely attributable to year and island and the residual fraction. These are descriptive scale partitions; the year term is not interpreted as a causal climate effect.

### Prospective regional and terrestrial mechanism tests

Mechanism tests were frozen before the corresponding predictor values were inspected or joined to the response.

For the annual marine test, the response was island annual growth and the primary regional predictor was Palmer DSR Grid sea-ice season duration for the completed sea-ice season preceding the breeding census. The baseline model contained island fixed effects; the regional model added standardized sea-ice duration. Validation withheld all five island observations from one calendar year at a time. Support required lower held-out mean squared error and a positive full-data coefficient.

After this annual formulation was not supported, a separate fixed-window test asked whether low-frequency sea-ice duration at a predeclared five-year scale improved prediction beyond a temporal baseline. Three- and seven-year windows were fixed robustness checks rather than tuned alternatives. Overlapping windows were purged from training during validation.

For the terrestrial weather test, annual island growth was converted to a local deviation by subtracting the mean growth of the other eligible islands in the same interval. The predictor was the number of October days with numeric positive snowfall at Palmer Station, and the island modifier was the published fraction of snow-prone/suboptimal breeding habitat from Fraser et al. [@fraser2013]. Post-extinction Litchfield zero-to-zero intervals were excluded. The predeclared prediction was a negative snowfall-by-habitat interaction and improved leave-one-year-out prediction.

### Within-island colony organization

The LTER census contains nominal island-specific colony codes. For each island-year, let \(p_j\) be the share of breeding pairs in colony code \(j\). We defined effective colony number as
\[
N_{\mathrm{eff}}=\frac{1}{\sum_j p_j^2}.
\]
This quantity is high when breeders are distributed more evenly among multiple colony codes and low when breeding pairs are concentrated in fewer groups.

The primary next-year model used annual transitions for which current island abundance was positive. The baseline contained island fixed effects, standardized current \(\log(1+N)\), and standardized census year. The full model added standardized \(\log(1+N_{\mathrm{eff}})\). Validation withheld all island transitions ending in one calendar year together. Support required a positive coefficient and lower held-out-year mean squared error.

Two specificity checks were fixed in advance. First, we replaced effective colony number with the number of active positive-count colony codes. Second, we evaluated an externally defined historical threshold of >50 breeding pairs per group rather than searching thresholds on the present outcome. The >50-pair analysis was treated as a directional validation: predictive improvement alone was insufficient if the coefficient had the opposite sign to the historical positive-retention hypothesis.

### Post-positive uncertainty and count-error diagnostics

Because the original effective-colony analysis produced only a small held-out error reduction, we froze an uncertainty diagnostic before using the result as a manuscript pillar. We kept next-year growth, current abundance, island identity and year fixed and permuted only effective colony number as synchronized start-year blocks. Donor values came from the same island in another year, with a common donor-year mapping across islands; years were stratified mechanically by island availability so the five-island pre-extinction phase was not mixed with the four-island post-Litchfield phase. We repeated the exact leave-one-end-year-out C0/C1 pipeline for 20,000 permutations. The primary statistic was \(\Delta\mathrm{MSE}=\mathrm{MSE}(C0)-\mathrm{MSE}(C1)\).

We next corrected the coefficient null for serial structure. For each island, we circularly shifted the complete ordered sequence of \(\log(1+N_{\mathrm{eff}})\) across its eligible transition years while keeping response, abundance, island identity and calendar year fixed. This preserves the island-specific marginal distribution, cyclic ordering, circular autocovariance and Fourier power spectrum while breaking calendar alignment with future growth. The primary structured null used 100,000 independent island-wise shifts. A fixed sensitivity applied one common lag to Christine, Cormorant, Humble and Torgersen while shifting Litchfield independently, allowing all 26 × 16 = 416 lag combinations to be enumerated exactly; this preserves cross-island N_eff covariance among the four persistent islands.

We then repeated the same-census mechanical-coupling diagnostic using circularly shifted, rather than year-block-permuted, latent colony composition. Target-year total abundance remained fixed, but colony-share vectors came from the same island at a circularly shifted donor year. Colony counts were simulated under independent Poisson sampling and fixed Gamma–Poisson sensitivities with 10% and 20% multiplicative overdispersion. Coupled simulations derived effective colony number and current abundance from the same simulated count vector; decoupled simulations used an independent current-total draw. These are stylized sensitivity models rather than empirical estimates of Palmer observer error.

### External spatial triangulation

The census colony codes are nominal and are not accompanied by a public one-to-one mapping to independently reconstructed GIS subcolony polygons. We therefore did not claim colony-ID-level spatial validation. Instead, we used the 2025 Torgersen reconstruction as process-level triangulation [@cimino2025]. That study used historic maps, drone imagery, GPS, digital surface models and satellite snow mapping to reconstruct historic and current subcolony footprints and their physical habitat.

Our spatial criterion was deliberately qualitative and bounded: mapped subcolony contraction and non-random habitat-associated attrition could converge with the internal colony-organization interpretation, but unresolved identifier correspondence prevents a causal test linking the exact LTER effective-colony metric to mapped topography.

### Reproducibility and frozen result family

All data extraction, endpoint contracts, result receipts, figure-data exports and figure rendering are versioned in the `mina` repository. Figure-data generation fails if the primary census no longer reproduces the frozen PC1 variance fraction, median annual-growth correlation or conditional effective-colony coefficient. The manuscript figure package uses the same frozen source fingerprint as the primary analysis.

## Results

### A common long-term decline provides the regional background to divergent local endpoints

All five island populations declined strongly between 1991 and 2017. Christine fell from 1,410 to 27 breeding pairs (1.9% remaining), Cormorant from 681 to 23 (3.4%), Humble from 1,085 to 68 (6.3%), Litchfield from 497 to zero, and Torgersen from 3,016 to 22 (0.7%). Litchfield reached zero breeding pairs in 2007 and remained locally extinct through the end of the synchronized series.

Despite these different endpoints, the standardized long-term trajectories were highly coherent. PC1 explained **96.4%** of five-island log-abundance variation and had similar same-sign loadings across islands. Annual dynamics were less synchronous: the median pairwise annual-growth correlation was **0.373**, with pairwise correlations ranging from negative to >0.7. Because synchrony is known to be timescale-dependent, we use this contrast to define the regional and local scales of the analysis rather than as a stand-alone discovery.

The additive decomposition similarly separated scales. Year uniquely accounted for **53.5%** of total log-abundance variance, island identity for **33.0%**, and residual variation for **13.5%**. Thus, the dominant long-term decline was regional in direction, but substantial persistent island differences and year-specific local deviations remained.

### Simple sea-ice-duration and snowfall formulations did not explain the scale mismatch

Adding preceding sea-ice duration to the annual island baseline yielded only a small held-out mean squared error improvement (0.07704 to 0.07591), while the full-data coefficient was **−0.050**, opposite the predeclared positive direction. A year-cluster bootstrap interval included zero. Adding the published static habitat interaction worsened held-out prediction.

The fixed low-frequency rescue also failed. At the primary five-year scale, adding trailing sea-ice duration worsened purged out-of-window mean squared error from 0.00373 to 0.00501 and produced a negative sea-ice coefficient (−0.016). Fixed three- and seven-year checks showed the same qualitative outcome. We therefore closed the sea-ice-duration window family rather than searching additional smoothing scales.

The terrestrial annual interaction was also unsupported. October snowfall days plus their interaction with published snow-prone habitat modestly increased in-sample \(R^2\) from 0.252 to 0.287, but leave-one-year-out RMSE worsened from 0.308 to 0.325. The interaction coefficient was **+0.073**, opposite the predeclared negative direction. These results reject the tested formulations, not the ecological importance of sea ice or breeding habitat.

### Colony organization was associated with next-year growth but did not show robust out-of-year prediction

Effective colony number had a positive standardized conditional coefficient (**+0.1168**) after island identity, current abundance and secular time were included. The original leave-one-end-year-out MSE decreased from 0.07311 to 0.07208, a gain of **+0.0010288**.

That gain did not survive the frozen uncertainty diagnostic. Under 20,000 synchronized year-block permutations, the null mean gain was −0.000202 (SD 0.00236), the 95th percentile was +0.00442, and **5,244/20,000** permutations produced a gain at least as large as observed. The one-sided permutation probability was **0.262**, placing the observed gain at the 73.8th percentile of the null distribution. We therefore withdraw the claim that effective colony number provides robust held-out-year predictive information.

The coefficient itself behaved differently. Under 100,000 independent island-wise circular shifts, no surrogate coefficient reached the observed +0.1168 (Monte Carlo one-sided *p* < 0.00001; null 97.5th percentile = 0.0628). In the exact joint-shift sensitivity, which preserved cross-island N_eff covariance among Christine, Cormorant, Humble and Torgersen, the identity alignment was the only one of 416 combinations reaching the observed coefficient (exact *p* = 1/416 = **0.0024**).

The count-error result also persisted after replacing the latent year-block null with circularly shifted colony composition. An observed-scale coupled coefficient was rare under Poisson (*p* = **0.00030**), Gamma–Poisson CV10% (*p* = **0.00150**) and Gamma–Poisson CV20% (*p* = **0.00780**) simulations. Median paired coupling bias was −1.7%, +0.5% and +6.6% of the observed coefficient, respectively. Thus, neither serial structure nor simple shared census-count error under the fixed sensitivity models reproduced the positive coefficient. The circular-shift surrogate has a wrap-around boundary and the count-error models are not empirically calibrated observer-error distributions, so this remains evidence for a bounded conditional association rather than causal identification.

Specificity checks did not restore a predictive interpretation. Active-colony count worsened held-out prediction. The externally fixed >50-pair group count and breeder fraction improved prediction but had negative coefficients, opposite their historical positive-direction hypothesis. We therefore retain effective colony number only as a conditional same-census association whose biological interpretation requires independent spatial validation.

### Independent Torgersen mapping showed real spatial contraction

The independent spatial record on Torgersen provides a physical counterpart to the internal colony-state signal [@cimino2025]. Of 23 historic active subcolony footprints, only five were active in 2022, an active-footprint fraction of 21.7%. All ten historic south-aspect subcolonies were extinct, compared with eight of 13 north-aspect subcolonies. Larger historic subcolonies tended to disappear later (reported \(R=0.75\), \(p=0.0009\)).

This evidence provides independent phenomenon-level support that real breeding-patch attrition on Torgersen is spatially structured rather than a purely nominal property of census coding. It does **not** validate the exact census-derived effective-colony metric against polygon topography, because a public machine-readable crosswalk between LTER colony codes and the independently mapped polygons has not been resolved.

### Broader local assembly endpoints were heterogeneous

The APBP context showed that local decline does not imply a single replacement pathway. Litchfield reached observed local Adélie extinction without focal-species replacement in the strict panel. In contrast, at the non-island Biscoe Point benchmark, Adélie declined from 3,020 breeding pairs in 1971 to 408 in 2025 while gentoo increased from an explicit zero in 1984 to 5,405 in 2025. Dream Island was consistent with a different Adélie-decline/chinstrap-increase pathway, although synchronized composition coverage was insufficient for a confirmatory community trajectory. These endpoints motivate treating regional decline and local assembly outcome as distinct ecological dimensions.

## Discussion

### Scale-dependent synchrony is context; divergent local endpoints are the ecological result

Long-term coherence with weaker short-term synchrony is not itself surprising. Population synchrony commonly depends on timescale, and correlated environmental drivers can generate different synchrony signatures across frequencies [@desharnais2018; @anderson2019; @sheppard2019; @reuman2025]. In the Palmer system, that established framework is useful because it prevents the 96.4% PC1 from being overinterpreted as a novel mechanism. The ecological result is instead the divergence of local outcomes within the same regional decline: persistence at low abundance, local extinction, alternative species-reassembly pathways and spatial contraction of breeding footprints.

This distinction matters for inference. A common PC1 does not identify the environmental mechanism, and a local extinction does not imply a unique local driver. Our prospective tests deliberately asked whether simple, biologically motivated proxies could bridge the two scales. They did not. The annual sea-ice coefficient was opposite its predeclared direction; smoothing the same duration index at 3–7 years did not rescue it; and annual snowfall did not interact with static snow-prone habitat in the expected direction. Continuing to search additional windows or months after these failures would turn mechanism testing into tuning.

These negative tests should not be read as evidence that sea ice, prey fields or snow are unimportant to Adélie ecology. Sea ice is closely linked to Pygoscelis trophic ecology [@gorman2014], and local geomorphology and snow conditions affect breeding phenology and subcolony persistence [@cimino2019; @cimino2025]. Rather, the tests show that the dominant 1991–2017 population trajectory and its island-to-island deviations are not captured by the specific linear duration and snowfall formulations we froze.

### Colony organization is a state indicator, not yet a causal mechanism

The effective-colony result should no longer be described as predictive. Its +0.00103 held-out MSE gain was compatible with synchronized year-block permutation noise (*p* = 0.262). The positive conditional coefficient, however, survived both serial-structure-preserving circular-shift nulls and all three circular-shift count-error coupling sensitivities. The defensible interpretation is therefore narrower but stronger than a raw same-census correlation: breeder distribution among colony codes is conditionally associated with next-year demographic performance after abundance, island and time are controlled, and that association is not readily reproduced by preserved temporal structure or the fixed shared-count-error models. A simple count of occupied colony codes did not transfer, while an externally fixed >50-pair threshold had the opposite coefficient direction to its historical hypothesis.

One possible interpretation is that effective colony number indexes the amount or diversity of usable breeding space still represented across an island, but the present data cannot distinguish that explanation from other biological sources of colony redistribution. If deteriorating snow or terrain conditions remove parts of the breeding landscape, breeder distributions may become increasingly concentrated before complete island-level collapse. The external Torgersen reconstruction is compatible with, but does not directly validate, this interpretation: the number of mapped active footprints collapsed, extinction was non-random across aspect, and larger historic footprints tended to persist longer [@cimino2025]. Yet this remains triangulation, not causal identification. The census codes are not currently crosswalked one-to-one to the mapped polygons, and colony organization could also reflect unmeasured demography or behavioral redistribution.

### An externally subsidized island system exposes breeding-patch filtering

The Palmer system provides a demographic complement to the more familiar ecosystem-engineering view of seabird islands. Seabirds are well known to move marine-derived nutrients onto land and alter recipient island ecosystems [@mulder2011; @grant2022]. Our analysis focuses on the reciprocal constraint: the breeding population itself remains tied to discrete terrestrial patches even when its principal food resources are external. These penguins acquire food in the ocean but concentrate reproduction on discrete terrestrial patches. This externalization of trophic resources reduces—but does not eliminate—the overlap between “island food supply” and “island breeding habitat.” Marine niche partitioning can also permit closely related species to coexist despite dietary overlap [@pickett2018]. As a result, terrestrial breeding-patch structure can emerge as a distinct axis of local vulnerability.

This perspective also clarifies why regional and local processes need not compete as explanations. Regional marine change may set the broad demographic direction, while terrestrial patch quality, colony history and the geometry of remaining nest habitat determine how that direction is realized locally. Biscoe Point further shows that local outcomes can include species replacement rather than simple vacancy. The appropriate island-ecology object is therefore not only species presence or total abundance, but the coupled state of regional marine forcing, breeding-patch occupancy and within-patch colony organization.

### Limitations and next tests

The primary synchronized analysis contains five nearby islands in one regional marine system. That is a strength for detecting scale separation under shared forcing but a limitation for generalization to other Antarctic archipelagos. The effective-colony metric is based on nominal census colony codes rather than mapped connectivity. Its coefficient survives the predeclared circular-shift nulls, but its held-out predictive gain is not stronger than the synchronized year-block permutation null. We also intentionally stopped after a finite set of failed environmental formulations, so untested pathways—including prey availability, sea-ice phenology other than duration, snow persistence at each island, and age-structured recruitment—remain plausible.

The highest-value next step is not another tuning pass over the same census. It is an external spatial crosswalk. Matching LTER colony codes to independently mapped historic and current polygons would allow direct tests of whether effective colony number tracks loss of snow-free habitat area, aspect, elevation or physical separation. Replicating the colony-organization result in another monitored archipelago would provide a stronger test of generality. Multi-species time series could then ask whether externally subsidized island systems tend toward vacancy, persistence or replacement depending on the identity and habitat requirements of potential colonists.

## Conclusion

Five neighbouring Adélie breeding islands underwent a strongly coherent multi-decadal decline, but the shared regional direction terminated in different local ecological states. The contrast between long-term coherence and weaker annual synchrony is consistent with established scale-dependent synchrony theory and should not be treated as the novelty by itself. Instead, the Palmer system shows how an externally subsidized island population can share a regional demographic regime while local breeding patches diverge toward persistence, extinction, replacement or spatial contraction. The tested sea-ice-duration and snowfall formulations did not identify the mechanisms responsible for that divergence. Effective colony number retained a positive conditional association with next-year growth that survived serial-structure-preserving circular shifts and circular-shift count-error sensitivities, but its small held-out predictive gain was compatible with synchronized year-block permutation noise and is not a positive predictive result. Independent Torgersen mapping demonstrates real habitat-structured subcolony attrition, while the unresolved census-code-to-GIS crosswalk prevents causal attribution. The strongest inference is therefore multiscale and bounded: regional decline and local ecological fate are distinct dimensions of Antarctic island demography.

## Data availability

The primary Palmer LTER Adélie penguin census is publicly archived at DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e. The sea-ice and Palmer Station weather sources used in the bounded mechanism tests are publicly archived at DOI 10.6073/pasta/4207e529832840db2282498d9f4f4f05 and DOI 10.6073/pasta/3eefb45dbfb784c3cabe3690ea46fe9e, respectively. Broader penguin assembly data are available through APBP/MAPPPD [@checastaldo2023]. Analysis code, frozen endpoint contracts, result receipts and figure-building scripts will be supplied as an anonymized repository snapshot for peer review and archived with a permanent DOI on acceptance.

## References

See `docs/REFERENCES_V3.bib`.
