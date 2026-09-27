# Common decline, divergent collapse: breeding-colony organization indexes local vulnerability across Antarctic penguin islands

**JAE submission draft v0.3 — Research Article main text; anonymized scientific content from the frozen mina result family**

## Abstract

1. Seabird breeding islands couple marine food webs to discrete terrestrial reproductive patches, creating a useful system for separating shared regional demographic change from local breeding-patch vulnerability.

2. We analysed a complete 1991–2017 annual census of five neighbouring Adélie penguin (*Pygoscelis adeliae*) islands near Palmer Station, West Antarctic Peninsula. A first principal component explained **96.4%** of standardized log-abundance variation, whereas median pairwise correlation of annual growth was only **0.373**; Litchfield reached local extinction while four neighbouring islands persisted at low abundance.

3. Prospectively bounded tests did not support the predicted positive effects of annual or 3–7-year sea-ice duration, nor the predicted negative interaction between October snowfall and published snow-prone island habitat. These failures apply to the tested formulations and do not imply that sea ice or terrestrial habitat are ecologically unimportant.

4. In contrast, effective colony number, (1/\sum p_j^2), had a positive conditional coefficient (**+0.1168**) and reduced held-out-year mean squared error from 0.07311 to 0.07208 after accounting for island identity, current abundance and secular time, a modest **1.4% relative error reduction**. Active-colony count did not improve transfer, and an externally fixed >50-pair group threshold improved prediction only with the opposite coefficient direction to its historical hypothesis.

5. Independently reconstructed Torgersen Island maps show real habitat-structured subcolony attrition: 23 historic active footprints were reduced to five active footprints by 2022. Because a public one-to-one crosswalk between LTER colony codes and mapped GIS polygons remains unresolved, this is phenomenon-level spatial triangulation rather than identifier-level validation of the effective-colony metric.

6. The Palmer system therefore shows a scale separation in animal ecology: neighbouring islands can share a regional demographic direction while the pathway to local collapse remains strongly patch-specific. Within-island colony organization provides a modest state indicator of local vulnerability, not a demonstrated causal fragmentation mechanism.

**Keywords:** Adélie penguin; breeding-colony structure; central-place foraging; island ecology; long-term monitoring; Palmer Archipelago; population synchrony; seabird islands

## Introduction

Island ecology asks why populations and communities diverge among habitat patches embedded within a broader regional setting. Seabird islands are a particularly strong form of land–sea coupling: birds acquire resources in marine food webs, return to land to reproduce, and transport marine-derived materials that can restructure terrestrial soils and communities [@mulder2011; @grant2022]. Most seabird-island work has therefore emphasized what seabirds do to islands. Here we ask the reciprocal demographic question: **how does the internal state of a terrestrial breeding patch condition the fate of a marine-foraging population?**

In many terrestrial systems, the patch contains both breeding habitat and much of the trophic resource base, making local resource availability, competitors, predators and physical habitat difficult to separate. Antarctic penguin breeding islands differ in a useful way. Pygoscelis penguins forage at sea but reproduce on discrete terrestrial patches, so the food environment is largely external to the breeding island while nesting habitat remains spatially localized. We refer to these as **externally subsidized breeding islands**: marine conditions can impose shared regional forcing, while snow, topography, drainage, access and the spatial organization of nest sites can generate local filters. The phrase describes the demographic geometry of the breeding system; it does not imply that terrestrial biotic interactions are absent.

The Palmer Archipelago is well suited to resolving these scales. Adélie penguins near Palmer Station have experienced major long-term population declines, while gentoo penguins have expanded and some breeding sites have undergone species replacement [@pickett2018; @checastaldo2023]. At the same time, neighboring islands differ in breeding habitat and snow accumulation. Long-term work on Torgersen and Humble islands shows that regional environmental conditions interact with island geomorphology to produce local variation in breeding phenology [@cimino2019]. Earlier work proposed that breeding-habitat quality, shaped by geomorphology and snow deposition, contributes substantially to differences among local Adélie populations [@fraser2013]. More recent spatial reconstruction on Torgersen independently mapped strong subcolony loss and showed that persistence was non-random with respect to terrain and snow-related habitat features [@cimino2025].

These observations raise a scale problem. A strong common decline across islands does not necessarily imply synchronous annual demographic responses, and a regional climate correlate does not necessarily explain why one island reaches extinction while another persists. Conversely, local colony structure can be associated with vulnerability without identifying the external driver of the regional decline. Separating these levels is important because otherwise a single correlation can be asked to explain both the regional direction and local collapse.

The present study developed from an audit of the Palmer Penguins data set, in which apparent morphology-to-island predictability was largely attributable to species identity rather than a stable within-species island phenotype [@gorman2014]. That result motivated the shift from asking whether an island can be classified from penguin phenotype to asking which ecological level—regional forcing, island state, species turnover or within-island breeding organization—actually carries persistent information. We therefore shifted from treating island identity as a classification target to treating the Palmer system as an island-assembly problem. The analysis proceeded in finite stages. First, we quantified shared and island-specific structure in a synchronized 27-year Adélie census. Second, we prospectively tested simple regional sea-ice and terrestrial snowfall formulations. Third, after those formulations failed, we tested one predeclared internal colony-state hypothesis: whether a more distributed breeding population among subcolonies predicts better next-year demographic performance beyond current abundance, island identity and secular time. Finally, we compared the interpretation with independently constructed Torgersen spatial records.

We expected three broad outcomes. If the long-term decline is regionally coherent, standardized island trajectories should share a dominant common component. If simple annual or low-frequency environmental proxies directly govern annual demographic response, their addition should improve held-out-year prediction in the predeclared direction. If within-island breeding organization indexes local vulnerability, effective colony number should add positive next-year predictive information beyond abundance and time. We treat the last prediction as a state-indicator test, not a causal fragmentation test.

## Materials and Methods

### Study system and data roles

The primary demographic analysis used five Adélie breeding islands monitored by the Palmer Station Antarctica Long Term Ecological Research program: Christine (CHR), Cormorant (COR), Humble (HUM), Litchfield (LIT) and Torgersen (TOR). We used the public colony-level breeding-pair census, aggregated annually within island. The synchronized panel spans 1991–2017 without missing island-years and contains 27 census seasons. The source table and its checksum are frozen in the mina reproducibility receipts (Palmer LTER data DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e).

We used the Antarctic Penguin Biogeography Project (APBP/MAPPPD) as a broader assembly context rather than as the synchronized primary time series [@checastaldo2023]. An outcome-blind local inventory within 20 km of Palmer Station identified six true-island breeding sites—Torgersen, Litchfield, Humble, Christine, Cormorant and Dream—and retained Biscoe Point on Anvers Island as a non-island benchmark. This distinction matters because Biscoe Point shows strong Adélie-to-gentoo replacement, whereas several true islands show decline or vacancy without equivalent gentoo replacement.

The Palmer Penguins morphology and isotope data were used only as exploratory motivation [@gorman2014]. They are not used to estimate the primary long-term colony-network effect.

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

### External spatial triangulation

The census colony codes are nominal and are not accompanied by a public one-to-one mapping to independently reconstructed GIS subcolony polygons. We therefore did not claim colony-ID-level spatial validation. Instead, we used the 2025 Torgersen reconstruction as process-level triangulation [@cimino2025]. That study used historic maps, drone imagery, GPS, digital surface models and satellite snow mapping to reconstruct historic and current subcolony footprints and their physical habitat.

Our spatial criterion was deliberately qualitative and bounded: mapped subcolony contraction and non-random habitat-associated attrition could converge with the internal colony-organization interpretation, but unresolved identifier correspondence prevents a causal test linking the exact LTER effective-colony metric to mapped topography.

### Reproducibility and frozen result family

All data extraction, endpoint contracts, result receipts, figure-data exports and figure rendering are versioned in the `mina` repository. Figure-data generation fails if the primary census no longer reproduces the frozen PC1 variance fraction, median annual-growth correlation or conditional effective-colony coefficient. The manuscript figure package uses the same frozen source fingerprint as the primary analysis.

## Results

### A nearly common long-term decline coexists with divergent annual dynamics

All five island populations declined strongly between 1991 and 2017. Christine fell from 1,410 to 27 breeding pairs (1.9% remaining), Cormorant from 681 to 23 (3.4%), Humble from 1,085 to 68 (6.3%), Litchfield from 497 to zero, and Torgersen from 3,016 to 22 (0.7%). Litchfield reached zero breeding pairs in 2007 and remained locally extinct through the end of the synchronized series.

Despite these different endpoints, the standardized long-term trajectories were highly coherent. PC1 explained **96.4%** of five-island log-abundance variation and had similar same-sign loadings across islands. This common long-term direction did not translate into tightly synchronized annual dynamics: the median pairwise annual-growth correlation was **0.373**, with pairwise correlations ranging from negative to >0.7.

The additive decomposition similarly separated scales. Year uniquely accounted for **53.5%** of total log-abundance variance, island identity for **33.0%**, and residual variation for **13.5%**. Thus, the dominant long-term decline was regional in direction, but substantial persistent island differences and year-specific local deviations remained.

### Simple sea-ice-duration and snowfall formulations did not explain the scale mismatch

Adding preceding sea-ice duration to the annual island baseline yielded only a small held-out mean squared error improvement (0.07704 to 0.07591), while the full-data coefficient was **−0.050**, opposite the predeclared positive direction. A year-cluster bootstrap interval included zero. Adding the published static habitat interaction worsened held-out prediction.

The fixed low-frequency rescue also failed. At the primary five-year scale, adding trailing sea-ice duration worsened purged out-of-window mean squared error from 0.00373 to 0.00501 and produced a negative sea-ice coefficient (−0.016). Fixed three- and seven-year checks showed the same qualitative outcome. We therefore closed the sea-ice-duration window family rather than searching additional smoothing scales.

The terrestrial annual interaction was also unsupported. October snowfall days plus their interaction with published snow-prone habitat modestly increased in-sample \(R^2\) from 0.252 to 0.287, but leave-one-year-out RMSE worsened from 0.308 to 0.325. The interaction coefficient was **+0.073**, opposite the predeclared negative direction. These results reject the tested formulations, not the ecological importance of sea ice or breeding habitat.

### Distributed colony organization carried modest next-year information

Effective colony number added a small but reproducible increment beyond island identity, current abundance and secular time. Its full-data standardized coefficient was **+0.1168**. Held-out-year mean squared error declined from 0.07311 in the baseline to 0.07208 in the topology model, a relative reduction of about 1.4%.

The effect was not equivalent to simply counting occupied colony codes. Active-colony count had a positive coefficient but worsened held-out prediction. Nor was the signal equivalent to retaining more large breeding groups. With the externally fixed >50-pair threshold, group count improved held-out prediction, but its coefficient was negative (**−0.221**), opposite the historical positive-direction prediction. The corresponding >50-pair breeder fraction showed the same sign reversal.

The supported result is therefore narrow: after conditioning on island, abundance and time, a population distributed more evenly across its reported breeding groups carried slightly more positive information about next-year demographic performance. We do not interpret the size of this gain as explaining the dominant regional decline.

### Independent Torgersen mapping showed real spatial contraction

The independent spatial record on Torgersen provides a physical counterpart to the internal colony-state signal [@cimino2025]. Of 23 historic active subcolony footprints, only five were active in 2022, an active-footprint fraction of 21.7%. All ten historic south-aspect subcolonies were extinct, compared with eight of 13 north-aspect subcolonies. Larger historic subcolonies tended to disappear later (reported \(R=0.75\), \(p=0.0009\)).

This evidence provides independent phenomenon-level support that real breeding-patch attrition on Torgersen is spatially structured rather than a purely nominal property of census coding. It does **not** validate the exact census-derived effective-colony metric against polygon topography, because a public machine-readable crosswalk between LTER colony codes and the independently mapped polygons has not been resolved.

### Broader local assembly endpoints were heterogeneous

The APBP context showed that local decline does not imply a single replacement pathway. Litchfield reached observed local Adélie extinction without focal-species replacement in the strict panel. In contrast, at the non-island Biscoe Point benchmark, Adélie declined from 3,020 breeding pairs in 1971 to 408 in 2025 while gentoo increased from an explicit zero in 1984 to 5,405 in 2025. Dream Island was consistent with a different Adélie-decline/chinstrap-increase pathway, although synchronized composition coverage was insufficient for a confirmatory community trajectory. These endpoints motivate treating regional decline and local assembly outcome as distinct ecological dimensions.

## Discussion

### Regional direction and local collapse are different ecological scales

The central result is the coexistence of two apparently contradictory patterns: an almost common long-term Adélie decline across neighboring islands and only moderate synchrony in annual growth. The contradiction disappears when the scales are separated. The islands share the direction of long-term change, but not the detailed path through demographic space. A regional forcing can therefore be important without yielding interchangeable local trajectories.

This distinction matters for inference. A common PC1 does not identify the environmental mechanism, and a local extinction does not imply a unique local driver. Our prospective tests deliberately asked whether simple, biologically motivated proxies could bridge the two scales. They did not. The annual sea-ice coefficient was opposite its predeclared direction; smoothing the same duration index at 3–7 years did not rescue it; and annual snowfall did not interact with static snow-prone habitat in the expected direction. Continuing to search additional windows or months after these failures would turn mechanism testing into tuning.

These negative tests should not be read as evidence that sea ice, prey fields or snow are unimportant to Adélie ecology. Sea ice is closely linked to Pygoscelis trophic ecology [@gorman2014], and local geomorphology and snow conditions affect breeding phenology and subcolony persistence [@cimino2019; @cimino2025]. Rather, the tests show that the dominant 1991–2017 population trajectory and its island-to-island deviations are not captured by the specific linear duration and snowfall formulations we froze.

### Colony organization is a state indicator, not yet a causal mechanism

The positive effective-colony result is modest in predictive magnitude—about a 1.4% relative reduction in held-out-year MSE—but its specificity is useful. A simple count of occupied colony codes did not transfer, and a historically motivated >50-pair threshold changed prediction in the opposite direction to the expected mechanism. The information therefore lies in how breeders are distributed among groups rather than in a generic “more colonies is better” or “more large groups is better” rule.

One interpretation is that effective colony number indexes the amount or diversity of usable breeding space still represented across an island. If deteriorating snow or terrain conditions remove parts of the breeding landscape, breeder distributions may become increasingly concentrated before complete island-level collapse. The external Torgersen reconstruction is compatible with, but does not directly validate, this interpretation: the number of mapped active footprints collapsed, extinction was non-random across aspect, and larger historic footprints tended to persist longer [@cimino2025]. Yet this remains triangulation, not causal identification. The census codes are not currently crosswalked one-to-one to the mapped polygons, and colony organization could also reflect unmeasured demography or behavioral redistribution.

### An externally subsidized island system exposes breeding-patch filtering

The Palmer system suggests a useful island-ecology perspective that complements the more familiar ecosystem-engineering view of seabird islands. Seabirds are well known to move marine-derived nutrients onto land and alter recipient island ecosystems [@mulder2011; @grant2022]. Our analysis focuses on the other side of that coupling: the breeding population itself can remain constrained by the terrestrial patch even when its principal food resources are external.

The Palmer system suggests a useful demographic extension of island ecology. These penguins acquire food in the ocean but concentrate reproduction on discrete terrestrial patches. This externalization of trophic resources reduces—but does not eliminate—the overlap between “island food supply” and “island breeding habitat.” Marine niche partitioning can also permit closely related species to coexist despite dietary overlap [@pickett2018]. As a result, terrestrial breeding-patch structure can emerge as a distinct axis of local vulnerability.

This perspective also clarifies why regional and local processes need not compete as explanations. Regional marine change may set the broad demographic direction, while terrestrial patch quality, colony history and the geometry of remaining nest habitat determine how that direction is realized locally. Biscoe Point further shows that local outcomes can include species replacement rather than simple vacancy. The appropriate island-ecology object is therefore not only species presence or total abundance, but the coupled state of regional marine forcing, breeding-patch occupancy and within-patch colony organization.

### Limitations and next tests

The primary synchronized analysis contains five nearby islands in one regional marine system. That is a strength for detecting scale separation under shared forcing but a limitation for generalization to other Antarctic archipelagos. The effective-colony metric is based on nominal census colony codes rather than mapped connectivity, and its predictive gain is small. We also intentionally stopped after a finite set of failed environmental formulations, so untested pathways—including prey availability, sea-ice phenology other than duration, snow persistence at each island, and age-structured recruitment—remain plausible.

The highest-value next step is not another tuning pass over the same census. It is an external spatial crosswalk. Matching LTER colony codes to independently mapped historic and current polygons would allow direct tests of whether effective colony number tracks loss of snow-free habitat area, aspect, elevation or physical separation. Replicating the colony-organization result in another monitored archipelago would provide a stronger test of generality. Multi-species time series could then ask whether externally subsidized island systems tend toward vacancy, persistence or replacement depending on the identity and habitat requirements of potential colonists.

## Conclusion

Five neighboring Adélie penguin islands underwent an exceptionally coherent long-term decline but not a uniform annual or extinction trajectory. Simple annual and low-frequency sea-ice-duration models and an annual snowfall-by-habitat model failed their predeclared predictive tests. A more distributed breeding population among census subcolonies carried a small positive increment of next-year demographic information, and independent Torgersen mapping confirms that the breeding landscape itself has undergone strong, habitat-structured spatial attrition. The evidence supports a scale-separated view of Antarctic island ecology: broad regional processes set a common direction, while the internal state of terrestrial breeding patches provides modest information about where local collapse is most advanced. The colony-network signal is predictive rather than causal, and resolving its spatial mechanism requires an explicit census-code-to-habitat crosswalk.

## Data availability

The primary Palmer LTER Adélie penguin census is publicly archived at DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e. The sea-ice and Palmer Station weather sources used in the bounded mechanism tests are publicly archived at DOI 10.6073/pasta/4207e529832840db2282498d9f4f4f05 and DOI 10.6073/pasta/3eefb45dbfb784c3cabe3690ea46fe9e, respectively. Broader penguin assembly data are available through APBP/MAPPPD [@checastaldo2023], and the exploratory Palmer Penguins data are publicly archived with the original study [@gorman2014]. Analysis code, frozen endpoint contracts, result receipts and figure-building scripts will be supplied as an anonymized repository snapshot for peer review and archived with a permanent DOI on acceptance.

## References

See `docs/REFERENCES_V2.bib`.
