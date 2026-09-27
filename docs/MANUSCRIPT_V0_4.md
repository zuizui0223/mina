# Regional decline, local collapse across Antarctic penguin breeding islands

**Manuscript v0.4 — post-diagnostic ecological revision; JAE submission remains on hold**

## Abstract

Spatial synchrony is scale-dependent: geographically separated populations can share slow directional change while differing substantially in short-term dynamics, and synchrony alone does not identify its cause [@liebhold2004; @sheppard2019]. We used a complete 1991–2017 census of five neighboring Adélie penguin (*Pygoscelis adeliae*) breeding islands near Palmer Station, West Antarctic Peninsula, to separate regional demographic structure from local breeding-patch state in a marine central-place forager whose principal food resources lie outside the terrestrial breeding patch.

All five populations declined strongly. A first principal component explained **96.4%** of standardized log-abundance variation, a descriptive summary of the common long-term decline, whereas median pairwise correlation of annual growth was **0.373** and Litchfield reached local extinction while four neighboring islands persisted. Prospectively bounded tests did not support the predicted positive effects of annual or 3–7-year sea-ice duration, nor a predicted negative interaction between October snowfall and published snow-prone habitat.

Effective colony number, (N_{\mathrm{eff}}=1/\sum p_j^2), had a positive conditional coefficient (**+0.1168**) for next-year growth after accounting for island identity, current abundance and secular time. However, its small held-out MSE improvement (0.07311 to 0.07208) was not unusual in a 20,000-replicate year-block permutation (**p=0.262**; 73.8th percentile). The coefficient itself was unusual under the same permutation (**p≈0.00010**) and remained unusual under predeclared Poisson and 10%/20% Gamma–Poisson mechanical-coupling simulations (coupled-null one-sided probabilities 0.00080, 0.00060 and 0.00640). We therefore retain (N_{\mathrm{eff}}) only as a conditional same-census association, not as robust out-of-year predictive evidence.

Independent Torgersen mapping shows a real spatial counterpart: 23 historic active subcolony footprints were reduced to five by 2022, with habitat-structured attrition, although no one-to-one public crosswalk links those polygons to LTER colony codes. The Palmer system therefore provides a bounded example of regional demographic decline coexisting with patch-specific collapse in an externally subsidized breeding system. Its strongest inference is not a new synchrony mechanism or a predictive colony metric, but the separation of regional trajectory, local demographic state and independent breeding-patch attrition.

## Introduction

Spatial synchrony is widespread in population ecology and can arise through dispersal, shared environmental forcing (the Moran effect), or synchronous trophic interactions [@liebhold2004]. Its magnitude and apparent drivers can also depend strongly on timescale: long-period population variation may be highly coherent even when shorter-period fluctuations are only weakly synchronized [@sheppard2019]. Consequently, a common long-term trajectory is not itself evidence for a particular regional driver, and contrasts between slow and fast synchrony are not by themselves surprising. The harder ecological problem is to identify which processes account for the shared component and which state variables distinguish local vulnerability.

Seabird breeding islands offer an unusually clear setting for that problem. Seabirds acquire most trophic resources from marine food webs but concentrate reproduction on discrete terrestrial patches, creating strong land–sea coupling [@mulder2011; @grant2022]. Much seabird-island research has emphasized marine nutrient transport and ecosystem engineering on recipient islands. The reciprocal demographic constraint is equally important: a highly mobile marine consumer can range widely for food while remaining dependent on a finite, physically structured breeding surface. We use **externally subsidized breeding islands** to describe this geometry. The term does not imply that terrestrial biotic interactions are absent; it separates the location of the main food resource from the location where reproduction is spatially constrained.

The Palmer Archipelago provides long-term replication within one regional marine setting. Adélie penguins near Palmer Station have undergone major population declines while gentoo penguins have expanded at some breeding sites [@pickett2018; @checastaldo2023]. Neighboring islands differ in snow accumulation and geomorphology, and those physical differences are associated with breeding phenology and long-term subcolony persistence [@fraser2013; @cimino2019; @cimino2025]. Thus the system contains a shared regional demographic background together with terrestrial heterogeneity at distances small enough that treating each island as a separate climatic region would be implausible.

Our aim was not to rediscover scale-dependent synchrony. Instead, we used the synchronized island series as a scaffold for a finite sequence of questions. First, how much of the long-term trajectory is common and how much annual demographic variation remains local? Second, do simple, prospectively specified marine and terrestrial environmental formulations transfer to held-out years in their predicted directions? Third, after accounting for island identity, current abundance and secular time, is the internal distribution of breeders among census subcolonies associated with subsequent demographic change? Because predictor and response are derived from the same census program, we explicitly quantified uncertainty in that third result with a year-block permutation and a separate mechanical-coupling simulation. Finally, we compared the census-derived pattern with independently mapped Torgersen breeding-patch attrition while keeping the unresolved colony-code-to-polygon crosswalk as a hard inferential boundary.

We expected the five islands to share a strong low-frequency decline, but treated that as descriptive rather than novel. Environmental mechanisms were considered supported only if they improved held-out prediction in their predeclared directions. For effective colony number, the original prospective rule required a positive coefficient and lower leave-one-year-out error; after observing a small gain, we added a frozen post-positive uncertainty diagnostic rather than treating the raw gain as sufficient evidence. This distinction between association and transfer is central to the final interpretation.

## Methods

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

### Within-island colony organization and post-positive diagnostics

The LTER census contains nominal island-specific colony codes. For each island-year, let (p_j) be the share of positive breeding pairs in colony code (j). We defined effective colony number as
[
N_{\mathrm{eff}}=\frac{1}{\sum_j p_j^2}.
]
This quantity increases when breeders are distributed more evenly among multiple reported groups.

For annual transitions whose starting island abundance was positive, the baseline model contained island fixed effects, standardized current (log(1+N)), and standardized census year. The full model added standardized (log(1+N_{\mathrm{eff}})). Validation withheld all island transitions ending in the same calendar year together. The originally frozen support rule required a positive coefficient and lower leave-one-year-out MSE. Active positive-colony count and an externally fixed >50-pair group definition were specificity checks; no alternative topology metric or size threshold was searched.

Because the observed held-out improvement was small, we subsequently froze a post-positive year-block permutation diagnostic. The response, current abundance, island, years and LOYO folds were held fixed. Only (N_{\mathrm{eff}}) was reassigned using synchronized donor-year blocks, always from the same island. The mapping preserved within-year cross-island topology covariance and was stratified by the set of eligible islands, separating 1991–2006 five-island years from 2007–2016 four-island years after Litchfield extinction. We repeated the exact LOYO pipeline for 20,000 permutations (seed 20260927) and used the one-sided proportion of permuted MSE gains at least as large as observed as the primary uncertainty statistic. We also recorded the corresponding full-data coefficient null distribution.

We then tested a distinct concern: mechanical coupling caused by deriving both (N_{\mathrm{eff},t}) and the growth denominator (N_t) from the same census. Under a topology-null model, target island-year totals were retained but colony shares were supplied by the same year-block permutation used above. We generated 10,000 simulated census data sets under each of three predeclared count-error models: independent Poisson colony counts, and Gamma–Poisson colony counts with independent multiplicative colony-level CVs of 10% and 20%. Within each replicate we compared a **coupled** fit, where (N_{\mathrm{eff},t}) and (N_t) used the same simulated current-year count vector, with a **decoupled** fit, where (N_{\mathrm{eff},t}) and current abundance used independent simulated draws. These are stylized sensitivity analyses, not calibrated estimates of Palmer observer error.

### External spatial triangulation

The census colony codes are nominal and are not accompanied by a public one-to-one mapping to independently reconstructed GIS subcolony polygons. We therefore did not claim colony-ID-level spatial validation. Instead, we used the 2025 Torgersen reconstruction as process-level triangulation [@cimino2025]. That study used historic maps, drone imagery, GPS, digital surface models and satellite snow mapping to reconstruct historic and current subcolony footprints and their physical habitat.

Our spatial criterion was deliberately qualitative and bounded: mapped subcolony contraction and non-random habitat-associated attrition could converge with the internal colony-organization interpretation, but unresolved identifier correspondence prevents a causal test linking the exact LTER effective-colony metric to mapped topography.

### Reproducibility and frozen result family

All data extraction, endpoint contracts, result receipts, figure-data exports and figure rendering are versioned in the `mina` repository. Figure-data generation fails if the primary census no longer reproduces the frozen PC1 variance fraction, median annual-growth correlation or conditional effective-colony coefficient. The manuscript figure package uses the same frozen source fingerprint as the primary analysis.

## Results

### Long-term decline was common, while annual dynamics remained only moderately synchronized

All five island populations declined strongly between 1991 and 2017. Christine fell from 1,410 to 27 breeding pairs (1.9% remaining), Cormorant from 681 to 23 (3.4%), Humble from 1,085 to 68 (6.3%), Litchfield from 497 to zero, and Torgersen from 3,016 to 22 (0.7%). Litchfield reached zero breeding pairs in 2007 and remained locally extinct through the end of the synchronized series.

All five standardized long-term trajectories were dominated by the same declining direction. PC1 explained **96.4%** of five-island log-abundance variation and had similar same-sign loadings across islands. Given the strongly monotonic decline in all five series, we treat this high PC1 as a descriptive low-frequency summary rather than an unexpected synchrony result. At the annual-growth scale, median pairwise correlation was **0.373**, with pairwise correlations ranging from negative to >0.7, consistent with the general expectation that synchrony depends on timescale [@liebhold2004; @sheppard2019].

The additive decomposition similarly separated scales. Year uniquely accounted for **53.5%** of total log-abundance variance, island identity for **33.0%**, and residual variation for **13.5%**. Thus, the dominant long-term decline was regional in direction, but substantial persistent island differences and year-specific local deviations remained.

### Simple sea-ice-duration and snowfall formulations did not explain the scale mismatch

Adding preceding sea-ice duration to the annual island baseline yielded only a small held-out mean squared error improvement (0.07704 to 0.07591), while the full-data coefficient was **−0.050**, opposite the predeclared positive direction. A year-cluster bootstrap interval included zero. Adding the published static habitat interaction worsened held-out prediction.

The fixed low-frequency rescue also failed. At the primary five-year scale, adding trailing sea-ice duration worsened purged out-of-window mean squared error from 0.00373 to 0.00501 and produced a negative sea-ice coefficient (−0.016). Fixed three- and seven-year checks showed the same qualitative outcome. We therefore closed the sea-ice-duration window family rather than searching additional smoothing scales.

The terrestrial annual interaction was also unsupported. October snowfall days plus their interaction with published snow-prone habitat modestly increased in-sample \(R^2\) from 0.252 to 0.287, but leave-one-year-out RMSE worsened from 0.308 to 0.325. The interaction coefficient was **+0.073**, opposite the predeclared negative direction. These results reject the tested formulations, not the ecological importance of sea ice or breeding habitat.

### Colony organization showed a conditional association but not a robust held-out predictive gain

The original full-data model gave effective colony number a positive standardized coefficient of **+0.1168** after conditioning on island identity, current abundance and secular time. The full model's leave-one-year-out MSE was 0.07208 compared with 0.07311 for the baseline, a raw gain of +0.00103 (about 1.4% relative error reduction).

That gain did not survive the frozen uncertainty diagnostic. In 20,000 synchronized year-block permutations, the observed gain lay at the **73.8th percentile** of the null distribution; 5,244 permutations had gains at least as large, giving a one-sided **p=0.262**. The null 95th percentile (+0.00442) was more than four times the observed gain. We therefore do not interpret the original error reduction as robust out-of-year predictive evidence.

The conditional coefficient behaved differently. Only one of 20,000 year-block permutations produced a coefficient at least as large as observed (one-sided **p≈0.00010**). The coefficient also remained unusual in the predeclared same-census mechanical-coupling simulations: the probability of a coupled-null coefficient at least +0.1168 was **0.00080** under Poisson counts, **0.00060** with 10% Gamma–Poisson multiplicative variation, and **0.00640** with 20% variation. Median paired coupling bias (coupled minus decoupled) represented −2.3%, +0.8%, and +8.8% of the observed beta, respectively. These stylized simulations therefore did not reproduce an observed-scale positive coefficient through shared current-year count error alone.

The resulting inference is narrower than the original prospective decision rule. Effective colony number retains a conditional association with next-year growth that survives the fixed diagnostics, but it does **not** provide demonstrably robust held-out-year predictive improvement. Active-colony count still failed to improve transfer, and the externally fixed >50-pair measures improved raw prediction only with coefficients opposite their historical positive-direction hypothesis.

### Independent Torgersen mapping showed real spatial contraction

The independent spatial record on Torgersen provides a physical counterpart to the internal colony-state signal [@cimino2025]. Of 23 historic active subcolony footprints, only five were active in 2022, an active-footprint fraction of 21.7%. All ten historic south-aspect subcolonies were extinct, compared with eight of 13 north-aspect subcolonies. Larger historic subcolonies tended to disappear later (reported \(R=0.75\), \(p=0.0009\)).

This evidence provides independent phenomenon-level support that real breeding-patch attrition on Torgersen is spatially structured rather than a purely nominal property of census coding. It does **not** validate the exact census-derived effective-colony metric against polygon topography, because a public machine-readable crosswalk between LTER colony codes and the independently mapped polygons has not been resolved.

### Broader local assembly endpoints were heterogeneous

The APBP context showed that local decline does not imply a single replacement pathway. Litchfield reached observed local Adélie extinction without focal-species replacement in the strict panel. In contrast, at the non-island Biscoe Point benchmark, Adélie declined from 3,020 breeding pairs in 1971 to 408 in 2025 while gentoo increased from an explicit zero in 1984 to 5,405 in 2025. Dream Island was consistent with a different Adélie-decline/chinstrap-increase pathway, although synchronized composition coverage was insufficient for a confirmatory community trajectory. These endpoints motivate treating regional decline and local assembly outcome as distinct ecological dimensions.

## Discussion

### The synchrony result is context, not the novelty claim

The five Palmer islands provide a clear example of a well-established property of spatial population dynamics: synchrony depends on timescale [@liebhold2004; @sheppard2019]. Their near-common long-term decline and only moderate annual-growth correlation should therefore not be presented as a paradox requiring a new explanation. Nor does the 96.4% PC1 identify a mechanism; with five strongly declining standardized series, a dominant first component is expected.

What the synchronized panel contributes is a controlled regional background against which local outcomes can be compared. Litchfield reaches extinction while neighboring islands persist at low abundance, and year-specific island deviations remain substantial. This makes it possible to ask whether simple candidate drivers or internal breeding-patch states account for the local component without relabeling the common decline itself as a mechanistic discovery.

The prospective environmental tests provide one useful boundary. The tested annual sea-ice duration, fixed 3–7-year duration summaries and October snowfall-by-habitat formulation did not transfer in their predicted directions. These results do not show that sea ice, prey fields or snow are unimportant to Adélie ecology. They show that the particular linear formulations we froze do not bridge the regional and local demographic scales in this data set. That distinction is important because causes of spatial synchrony are generally difficult to identify from synchronized abundance alone [@liebhold2004].

### Colony organization is associated with local demographic state, but does not yet predict it robustly

The effective-colony result is now best understood as an association with a hard uncertainty boundary. Its positive conditional beta is difficult to reproduce by year-block reassignment and remains extreme under the three predeclared stylized count-error simulations. This argues against two simple explanations: arbitrary year alignment and an observed-scale positive coefficient generated solely by sharing current-year census error between (N_{\mathrm{eff}}) and population growth.

The held-out prediction result, however, is much weaker. A +0.00103 MSE improvement falls comfortably inside the year-block null (p=0.262). We therefore withdraw the earlier interpretation of effective colony number as a robust predictive state indicator. At most, breeder distribution among reported subcolonies is a candidate state correlate whose generality and forecasting value require genuinely independent data.

That narrower interpretation also clarifies the specificity checks. Active-colony count does not transfer, and the externally fixed >50-pair hypothesis reverses its expected sign. The relevant census association is therefore not reducible to “more colonies” or “more large colonies.” One possible biological interpretation is that (N_{\mathrm{eff}}) summarizes how breeding pairs occupy the remaining breeding surface, but census codes are not an independent habitat measurement and this interpretation cannot be established from the time series alone.

Independent Torgersen mapping is useful precisely because it is external to the census-derived index. The reconstruction documents strong spatial contraction, aspect-structured extinction and persistence of larger historic footprints [@cimino2025]. That evidence demonstrates that real breeding-patch attrition occurred, but it remains **phenomenon-level triangulation**: without a one-to-one LTER colony-code/GIS-polygon crosswalk, it cannot validate the exact (N_{\mathrm{eff}}) coefficient or establish habitat fragmentation as its cause.

### An externally subsidized island system exposes breeding-patch filtering

The Palmer system complements the familiar ecosystem-engineering view of seabird islands. Seabirds move marine-derived nutrients onto land and alter recipient ecosystems [@mulder2011; @grant2022], but their own reproduction remains spatially constrained to terrestrial patches even when their principal food resources are external. In Pygoscelis penguins, marine niche partitioning can permit closely related species to coexist despite dietary overlap [@pickett2018]. The demographic consequence is that regional marine conditions and local breeding-surface state can operate on different ecological axes rather than being competing explanations.

This perspective also clarifies why regional and local processes need not compete as explanations. Regional marine change may set the broad demographic direction, while terrestrial patch quality, colony history and the geometry of remaining nest habitat determine how that direction is realized locally. Biscoe Point further shows that local outcomes can include species replacement rather than simple vacancy. The appropriate island-ecology object is therefore not only species presence or total abundance, but the coupled state of regional marine forcing, breeding-patch occupancy and within-patch colony organization.

### Limitations and next tests

The primary synchronized analysis contains five nearby islands in one regional marine system. That is a strength for detecting scale separation under shared forcing but a limitation for generalization to other Antarctic archipelagos. The effective-colony metric is based on nominal census colony codes rather than mapped connectivity. Its conditional coefficient survives the fixed permutation and stylized count-error diagnostics, but its held-out predictive gain does not (year-block p=0.262). We also intentionally stopped after a finite set of failed environmental formulations, so untested pathways—including prey availability, sea-ice phenology other than duration, snow persistence at each island, and age-structured recruitment—remain plausible.

The highest-value next step is not another tuning pass over the same census. It is an external spatial crosswalk. Matching LTER colony codes to independently mapped historic and current polygons would allow direct tests of whether effective colony number tracks loss of snow-free habitat area, aspect, elevation or physical separation. Replicating the colony-organization association in another monitored archipelago, or resolving the Palmer colony-code/GIS crosswalk, would provide the first genuinely independent test of generality. Multi-species time series could then ask whether externally subsidized island systems tend toward vacancy, persistence or replacement depending on the identity and habitat requirements of potential colonists.

## Conclusion

Five neighboring Adélie penguin islands share a strong long-term decline while annual dynamics and extinction endpoints remain local. That scale dependence is consistent with established spatial-synchrony theory and is treated here as ecological context rather than a novel synchrony mechanism. Prospectively bounded annual and low-frequency sea-ice-duration models and an annual snowfall-by-habitat model failed their directional validation tests.

Effective colony number is positively associated with next-year growth after island, abundance and time are controlled, and the coefficient remains unusual under frozen year-block and stylized mechanical-coupling diagnostics. Its small leave-one-year-out improvement, however, is not unusual under year-block permutation (p=0.262), so we do not claim robust predictive value. Independent Torgersen mapping establishes that breeding-patch attrition is real and habitat structured, but the unresolved colony-code-to-GIS crosswalk prevents identifier-level or causal validation.

The resulting contribution is deliberately bounded: in an externally subsidized breeding system, a common regional trajectory can coexist with patch-specific collapse, and internal breeding organization can covary with local demographic state without providing reliable out-of-year prediction. The next decisive test requires independent spatial mapping or replication, not further tuning of the same census.


