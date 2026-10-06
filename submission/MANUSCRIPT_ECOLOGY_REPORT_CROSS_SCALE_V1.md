# Breeding-space contraction recurs across spatial scales in Antarctic penguins

**Ecology Report candidate — cross-scale v1**

## Abstract

Population decline can reduce site occupancy mechanically because small local counts increasingly reach zero. We asked whether colonial breeders show additional spatial reorganization after conditioning on that effect. We quantified effective breeding-component number, (E=1/\sum p_j^2), and compared observed change with fixed-composition nulls that preserve the observed abundance trajectory. In three Adélie penguin (*Pygoscelis adeliae*) populations near Palmer Station, (E) declined by 19–83% beyond frozen count-error expectations. Prospectively frozen Signy Island tests independently supported the same endpoint in Adélie penguins (−37%) and chinstrap penguins (*P. antarcticus*; −51%). We then moved one spatial level upward using a frozen MAPPPD archive: among four estimable declining species × regional monitoring networks, all had positive observation-error-calibrated abundance–concentration effects, with individual support in South Shetland Adélie and chinstrap networks. Thus decline did not merely scale down a fixed breeding distribution. Breeding effort repeatedly became concentrated into fewer effective monitored components, and that direction persisted across spatial levels even though effect magnitude and the components that persisted were not universal.

## Introduction

Population decline has a spatial form as well as a magnitude. Positive abundance–occupancy relationships are widespread: as populations lose individuals, occupied sites often disappear [@gaston2000]. Yet the same pattern can arise in two fundamentally different ways. If relative spatial composition remains fixed, low-abundance components will reach zero increasingly often simply because fewer individuals remain. Alternatively, the relative distribution itself can change, concentrating the remnant population into a smaller subset of space. Equal abundance losses can therefore produce very different range contractions depending on where decline occurs [@rodriguez2002], and density-dependent distribution models similarly distinguish proportional thinning from abundance-linked spatial contraction [@thorson2016].

Colonial breeders provide a discrete, hierarchical version of this problem. Breeders occupy nests nested within aggregations, colony units, breeding sites and larger regional networks. A declining colony can therefore lose abundance without changing its expected allocation among components, or it can undergo **breeding-space contraction**: a decline in the effective number of monitored components carrying reproduction. We use that term operationally for relative allocation among repeated monitoring units; it does not imply direct measurement of occupied physical area.

Penguins are useful for testing this distinction because reproduction is concentrated on discrete terrestrial breeding patches while foraging occurs at sea. Within Adélie colonies, reproductive performance varies with subcolony-scale habitat and configuration [@schmidt2021], mechanistic models predict changing nest geometry during decline [@mcdowall2019], and long-term mapping at Torgersen Island documents non-random loss of historical breeding footprints [@cimino2025]. These studies show that breeding geometry matters, but they do not establish whether longitudinal loss of monitored components exceeds the mechanical consequence of declining abundance.

We therefore conditioned explicitly on abundance. Under our fixed-composition null, each observed annual population total defines the abundance trajectory while expected relative shares among breeding components remain constant. Simulated counts include finite-count and frozen observation-error effects. A stronger observed reduction in effective component number therefore identifies directional redistribution beyond proportional thinning.

The evidence was assembled in three stages. Palmer Adélie populations provided the discovery system. We then froze the same endpoint before testing independent Signy Adélie data and, separately, Signy chinstrap data. Finally, after the local pattern had been established, we froze a bounded scale-transfer analysis using an already-pinned Antarctic Penguin Biogeography Project (APBP/MAPPPD) archive [@checastaldo2023], redefining components as breeding sites within published regional monitoring networks. The regional test asks whether the **direction** of abundance-conditioned concentration persists one level higher in the spatial hierarchy; it is not a test of a universal exponent or common cross-scale effect size.

## Methods

### Effective monitored breeding components

For season (t), let (n_{jt}) be the breeding-pair count in component (j), (N_t=\sum_j n_{jt}), and (p_{jt}=n_{jt}/N_t). We calculated

[
E_t = \frac{1}{\sum_j p_{jt}^2}.
]

(E) is the inverse-Simpson effective number of monitored breeding components: it falls as reproduction becomes concentrated into fewer components. It is not occupied area, genetic effective population size, or a count of equal-area habitat patches.

Component definitions differed by spatial level. Palmer components were stable colony-code census units within island breeding systems; Signy components were frozen monitored breeding colonies or canonical monitoring units; MAPPPD regional components were repeatedly monitored breeding sites. Cross-scale inference therefore concerns **directional redistribution beyond fixed composition**, not numerical equality of (E), slopes or elasticities among scales.

### Palmer discovery system

We used the public Palmer Station Antarctica Long Term Ecological Research Adélie breeding-pair census (1991–2017; DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e). Primary concentration inference was restricted to Cormorant, Humble and Litchfield islands because their reported colony-code rosters were unchanged over eligible intervals. Litchfield was analyzed through its final positive census in 2006. Palmer units are treated conservatively as monitored census components because a versioned spatial-boundary history is not available for every colony code.

For each population-year we calculated (E), and the observed statistic was the ordinary-least-squares slope of (E) against year. Palmer is the discovery system rather than prospective evidence.

### Prospectively frozen Signy replications

The independent-system test used the public Signy Adélie data set (DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d). Before the relevant (E) outcome was calculated, an outcome-blind support audit froze five canonical breeding units across 22 complete seasons from 1996–2019. The source changed from separate A1/A60 reporting to pooled forms, so those labels were harmonized to A1+A60 under a rule fixed before effect inspection.

The cross-species test used the corresponding Signy chinstrap data set (DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9). A separate outcome-blind audit froze nine literal colony units across the same 22 complete seasons. A predeclared gate required stable-roster abundance to decline before the concentration prediction could be interpreted.

### Fixed-composition null for local systems

For each Palmer or Signy population, we estimated a time-invariant component-share vector from cumulative counts across its frozen panel. Those shares were combined with each observed annual population total to define latent expected component counts. We simulated 100,000 trajectories under each of three frozen error families: independent Poisson sampling and Gamma–Poisson sampling with 10% or 20% multiplicative CV. The 20% model is a severe sensitivity, not an estimate of true observer error.

Support required a negative observed (E) slope and a one-sided plus-one Monte Carlo probability (\le 0.05) under all three error models. No alternative metric, threshold, time window or error CV could rescue a failed test.

### MAPPPD regional scale transfer

The broader test used the pinned `CCheCastaldo/mapppdr` snapshot at commit `88c73a507e0921b2541c218c71eaf16721bc6502`. We reused an earlier frozen 1980–2025 observation cohort and calibration rather than constructing a new method filter after seeing concentration outcomes. Same-season repeated records were corrected for the previously estimated direct-versus-image offset on the (log(1+\mathrm{count})) scale and precision-collapsed using frozen accuracy-dependent variances.

The parent unit was species × published APBP region and the components were site IDs. These are monitored geographic networks, not assumed closed demographic populations. Eligibility was determined before regional concentration outcomes from observation structure only: at least three retained sites, at least five seasons observed at every retained site, and at least 10 calendar years between first and last complete seasons. When necessary, a deterministic rule removed the site with the fewest observed seasons until the first qualifying roster was reached; count magnitude did not enter selection.

For each eligible network we calculated annual (N_t) and (E_t). Network abundance direction was the slope of (log N_t) against year. For regional scale transfer, the observed statistic was the abundance–concentration elasticity

[
\log E_t = \alpha + \kappa_{obs}\log N_t.
]

The fixed-composition null pooled adjusted site counts across retained complete seasons to estimate time-invariant shares (q_j), then drew site counts at each empirical total from a multinomial distribution. A second null added the previously frozen observation-error variance on the (log(1+n)) scale. Both used 20,000 simulations. We summarized excess concentration as

[
\Delta\kappa = \kappa_{obs}-\mathrm{median}(\kappa_{null}).
]

A regional panel was individually supported only when (\Delta\kappa>0) and one-sided (p\le0.05) under both nulls. These are panel-level calls; no family-wide regional rejection criterion or pooled cross-scale p-value was prespecified.

### Reproducibility and computational assistance

All analyses were executed from version-controlled code, and numerical outputs were checked against frozen result receipts and source-data checksums. OpenAI ChatGPT (GPT-5.6 Sol) assisted with code drafting and review, literature searching, statistical sensitivity-analysis scripting and editorial drafting. The authors verified all analyses, sources, interpretations and text.

## Results

### Five within-system populations concentrated beyond proportional thinning

Effective breeding-component number declined in all three eligible Palmer Adélie populations. Cormorant fell from 3.54 to 2.86 (−19%; slope −0.031 yr⁻¹), Humble from 4.62 to 2.28 (−51%; −0.086 yr⁻¹), and Litchfield from 5.78 to 1.00 before local extinction (−83%; −0.368 yr⁻¹). Under the severe Gamma–Poisson 20%-CV model, one-sided probabilities were 0.0380, 0.000010 and 0.000010, respectively; no one of 100,000 joint simulations was simultaneously as negative as all three observed slopes.

Signy independently replicated the endpoint. Adélie breeding pairs declined from 2,342 to 1,217 while (E) declined from 3.08 to 1.94 (−37%; slope −0.044 yr⁻¹); none of 100,000 20%-CV null trajectories was as negative (plus-one p = 0.000010). The separately frozen chinstrap panel declined from 1,642 to 581 pairs while (E) fell from 4.44 to 2.19 (−51%; slope −0.072 yr⁻¹); one of 100,000 20%-CV null slopes was as negative (p = 0.000020). Thus the within-system endpoint transferred across geography and species with prospectively frozen tests.

### Regional site networks retained the same direction

Thirteen species × APBP-region groups occurred in the frozen MAPPPD cohort; seven passed the coverage-only gate across three *Pygoscelis* species and three regions. Four eligible networks were declining.

All four declining networks had positive observation-error-calibrated (\Delta\kappa). Adélie in the Central-west Antarctic Peninsula had (\Delta\kappa=+0.073) (p = 0.108) and South Shetland Adélie had (+0.115) (p = 0.0148). Chinstrap in the Central-west Antarctic Peninsula had (+0.017) (p = 0.432) and South Shetland chinstrap had (+0.434) (p = 0.0152). Thus two panels were individually supported under both frozen regional nulls, while all four pointed in the same direction. Because two species occur within each declining region, the four panels are not four independent geographic replicates; their 4/4 sign agreement is descriptive.

The Central-west Antarctic Peninsula rosters include Biscoe Point in the broader Palmer-area APBP context, although the Palmer discovery populations are Cormorant, Humble and Litchfield. We therefore treat MAPPPD as a scale-transfer test rather than an additional independent geographic replication; Signy supplies the independent geographic replication.

## Discussion

Declining abundance did not merely scale down a fixed breeding distribution. Across three Palmer discovery populations and two prospectively frozen Signy tests, effective breeding-component number declined more strongly than expected from fixed relative composition subjected to the observed abundance trajectory and frozen count-error models. A bounded regional extension then showed the same abundance–concentration direction in every estimable declining MAPPPD network, with individual support in both South Shetland species panels.

The general contribution is a decomposition of abundance loss from spatial reorganization. Abundance–occupancy relationships and range contraction are established ecological patterns [@gaston2000; @rodriguez2002], and density-dependent changes in effective occupied area have been quantified in other systems [@thorson2016]. Our analysis asks a narrower question that those patterns do not resolve: after conditioning on the abundance trajectory itself, does **relative spatial composition** still change? The answer was repeatedly yes within the strongest local systems and remained directionally positive when monitored sites within regional networks became the components.

That does not imply a universal numerical scaling law. The local and regional analyses use different scale-appropriate statistics, and component definitions differ physically. We therefore do not pool effect sizes or p-values across scales. What transfers is ordinal: declining systems repeatedly move toward fewer effective monitored breeding components beyond fixed-composition expectations. The rate of that movement can vary with component definition, geography, habitat, history and demography.

Nor does contraction identify a universal refuge mechanism. In a bounded post-hoc description, all three Palmer populations lost the component that was largest initially, whereas the initially dominant component remained dominant and increased its share in both Signy species. The same population-level endpoint can therefore emerge through contrasting component histories. Fine-scale fragmentation and coarse component loss are also not contradictory: Torgersen mapping shows loss of historical breeding footprints alongside fragmentation within some retained footprints [@cimino2025], consistent with spatial organization changing differently at different grains.

The regional extension remains deliberately limited. Only Adélie and chinstrap penguins contribute declining regional networks, the two individually supported regional effects share the South Shetland region, and some eligible networks contain only five complete seasons. MAPPPD sampling is geographically and methodologically uneven, and APBP regions are monitoring networks rather than closed populations. These constraints prevent a seabird-wide or Antarctic-wide law.

The monitoring implication is simpler. Population totals cannot reconstruct how reproduction is distributed once component-resolved counts are aggregated away. Preserving repeated component-level counts allows population decline to be separated into numerical loss and reorganization of breeding space. For colonial species, those are distinct ecological state variables.

## Acknowledgments

We acknowledge the Palmer Station Antarctica Long Term Ecological Research program, the British Antarctic Survey/NERC UK Polar Data Centre, and the Antarctic Penguin Biogeography Project contributors for making the long-term monitoring data publicly available. OpenAI ChatGPT (GPT-5.6 Sol) was used for code drafting and review, literature searching, statistical sensitivity-analysis scripting and editorial drafting; all generated material was checked by the authors, who retain responsibility for the analysis and manuscript.

## Author Contributions

[Complete before submission.]

## Conflict of Interest Statement

[Complete before submission.]

## Data Availability

The Palmer LTER Adélie census is available at DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e. Signy Adélie data are available at DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d and Signy chinstrap data at DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9. The MAPPPD analysis uses the public CCheCastaldo/mapppdr repository pinned at commit 88c73a507e0921b2541c218c71eaf16721bc6502. Frozen contracts, result receipts, analysis code and figure scripts are available in the mina repository. The exact submitted code release and derived outputs should be permanently archived before acceptance.

## References

See `docs/REFERENCES_V6.bib`.
