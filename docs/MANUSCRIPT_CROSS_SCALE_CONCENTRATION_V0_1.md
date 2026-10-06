# Breeding-component concentration recurs across spatial scales in Antarctic penguins

**Manuscript v0.1 — cross-scale concentration synthesis; not yet journal-formatted**

## Abstract

Population decline has a spatial form as well as a magnitude, but loss of occupied breeding space can arise mechanically when fewer individuals are distributed among fixed sites. We asked a stricter question in Antarctic colonial penguins: does breeding effort become concentrated into fewer effective monitored components than expected from proportional thinning, and does that direction persist across spatial levels? We quantified effective breeding-component number as \(E=1/\sum_j p_j^2\), where \(p_j\) is the share of breeding pairs in component \(j\), and compared observed changes with fixed-composition nulls conditioned on the observed abundance trajectory. Within the Palmer discovery system, three island-based Adélie sample-colony monitoring networks declined in effective component number by 19–83%; all exceeded frozen count-error null expectations. Prospectively frozen external tests at Signy Island independently supported the same outcome in Adélie penguins (−37%) and chinstrap penguins (*P. antarcticus*; −51%). We then moved one level up the spatial hierarchy using the already-pinned Antarctic Penguin Biogeography Project archive, treating monitored breeding sites within published regions as components. Seven species × region networks were structurally estimable; four were declining. All four had positive observation-error-calibrated abundance–concentration effects, although only the South Shetland Adélie and chinstrap networks were individually supported (p = 0.0148 and 0.0152). The direction of contraction therefore transferred more consistently than its magnitude. Component-level routes also differed: Palmer sample-colony networks lost their initially dominant monitored components, whereas Signy panels retained and strengthened them. Declining monitored abundance in Antarctic *Pygoscelis* is thus repeatedly accompanied by non-proportional breeding-component concentration across spatial levels, while the strength and internal route of contraction remain geographically contingent.

**Keywords:** abundance–occupancy; Antarctica; colonial breeding; effective number; penguins; population decline; spatial contraction; spatial scale

## Introduction

Population decline is usually summarized by how many individuals remain. Yet a declining population also has a spatial state: the remaining individuals may continue to occupy the same places in roughly the same proportions, or reproduction may become increasingly concentrated into a smaller subset of locations. These possibilities are not equivalent. Equal losses of abundance can produce very different spatial contractions depending on where losses occur within a distribution [@rodriguez2002], and positive abundance–occupancy relationships do not by themselves distinguish a change in spatial organization from the mechanical disappearance of low-count sites as abundance falls [@gaston2000].

This distinction has a direct analogue in density-dependent distribution theory. For marine fishes, proportional-density models and basin-type models differ in whether the spatial distribution remains proportionally stable or contracts with abundance; effective area occupied can therefore contain information not recoverable from abundance alone [@thorson2016]. Colonial breeders provide a discrete and strongly hierarchical version of the same problem. Individuals occupy nests, nests form aggregations, aggregations occur within subcolonies or census units, and multiple breeding sites form larger regional networks. A decline can therefore reorganize breeding space at more than one level.

Penguins are especially useful for separating the spatial organization of reproduction from total abundance. *Pygoscelis* penguins forage at sea but reproduce on discrete terrestrial breeding patches. Within those patches, nesting configuration and habitat matter: Adélie reproductive performance varies with subcolony-scale conditions [@schmidt2021], mechanistic models predict fragmentation of nesting aggregations during decline [@mcdowall2019], and long-term reconstruction at Torgersen Island shows non-random loss of historical subcolonies associated with terrain and snow [@cimino2025]. At broader scales, the Antarctic Penguin Biogeography Project (APBP/MAPPPD) compiles long-term abundance observations across the Antarctic breeding ranges of Adélie, chinstrap and gentoo penguins [@checastaldo2023].

The inferential difficulty is that spatial contraction can appear even when the latent composition is unchanged. If a population with fixed relative allocation among components becomes small, finite counts alone increase the probability that low-share components reach zero. Measurement error can further exaggerate apparent redistribution. A test for ecological reorganization must therefore condition on the abundance trajectory and ask whether changes in relative composition exceed those expected under a fixed spatial allocation.

Our analyses developed in three stages with different degrees of prospective independence. First, the Palmer Archipelago provided a discovery system: three island-based Adélie sample-colony monitoring networks with stable colony-code rosters showed strong within-network concentration beyond fixed-composition count-error nulls. Second, the same effective-component endpoint and null logic were frozen before testing independent Signy Island data, first in Adélie penguins and then in a separately frozen chinstrap analysis. Those tests established geographic and cross-species replication within *Pygoscelis*. Third, after the local contraction pattern and its candidate abundance scaling had been identified, we asked whether the **direction** of the pattern survived a change in spatial level. Using only an already-pinned MAPPPD snapshot and already-frozen observation handling, we defined species × published APBP region as monitored networks and individual breeding sites as components, froze a coverage-only eligibility rule, and then opened the regional concentration outcomes.

The resulting design distinguishes three questions. First, does decline produce concentration beyond proportional thinning within breeding systems? Second, does the same outcome recur in an external region and species? Third, when breeding components are redefined one level higher—from within-site census units to breeding sites within regional networks—does the abundance–concentration direction persist? The regional extension was frozen to test transfer of **direction**; a universal quantitative exponent or component-level mechanism was not a prespecified regional target.

## Materials and Methods

### Effective breeding-component number

At every spatial level we described relative breeding allocation using the inverse-Simpson effective number,

\[
E_t = \frac{1}{\sum_j p_{jt}^2},
\]

where \(p_{jt}=n_{jt}/\sum_j n_{jt}\) and \(n_{jt}\) is the breeding-pair count for component \(j\) in season \(t\). \(E\) equals the number of equally represented components that would generate the observed concentration. It therefore falls when a larger share of reproduction is carried by fewer components.

We use the generic term **effective breeding-component number** because the physical meaning of a component differs among data sets. Palmer components are long-term colony-code units from a fixed sample-colony monitoring panel within focal islands; Signy components are monitored breeding colonies or colony units; MAPPPD regional components are repeatedly monitored breeding sites. We do not interpret these units as equal-area habitat polygons.

### Palmer discovery system

The Palmer analysis used the public Palmer Station Antarctica Long Term Ecological Research Adélie breeding-pair table archived at DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e (EDI revision knb-lter-pal.87.7), spanning 1991–2017. Source-provenance checks identify the reported colony codes as the historical fixed sample-colony monitoring panel rather than an exhaustive enumeration of all physical subcolonies: in 1993 the frozen table contains 54 positive monitored colony codes, matching contemporary documentation of 54 sample colonies [@fraser1994amlr]. We therefore treat yearly sums as summed monitored-component abundance, not island-wide population totals. Primary concentration inference was restricted to Cormorant, Humble and Litchfield because those monitoring networks retained unchanged reported colony-code rosters over their eligible intervals. Litchfield contributed through its final positive monitored-panel census.

For each island-year we calculated \(E\). The observed concentration statistic was the OLS slope of \(E\) against calendar year. We estimated one time-invariant component-share vector from cumulative counts within each island and imposed the observed summed monitored-component abundance trajectory on that fixed composition. Counts were then simulated under Poisson, Gamma–Poisson 10% multiplicative-CV and Gamma–Poisson 20% multiplicative-CV observation models. Each frozen model used 100,000 simulations. Support required a negative observed \(E\) slope and a one-sided Monte Carlo probability \(\le 0.05\) under every frozen error model.

Palmer is the discovery system. Its concentration analysis is not represented as prospectively generated evidence.

### Signy external and cross-species replications

The external Adélie test used the NERC EDS UK Polar Data Centre data set *Population size and breeding success of Adelie penguins on Signy Island from 1978 to 2020* (DOI: 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d). Before the relevant \(E\) outcome was calculated, an outcome-blind support audit froze the eligible monitoring units and seasons. The primary panel contained five canonical units across 22 complete seasons from 1996–2019, excluding incomplete 1997 and 2010 records. A later strict literal-roster analysis over 1998–2009 was retained as robustness rather than replacing the earlier endpoint.

The cross-species test used the corresponding Signy chinstrap data set (DOI: 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9). Nine literal colony units were frozen before the chinstrap concentration effect was computed, using the same 22 complete primary seasons. The summed abundance trajectory first had to pass a frozen decline gate. Conditional on that gate, support required a negative \(E\) trend more extreme than all prespecified fixed-composition count-error nulls.

The Signy tests used the same \(E\) definition and the same Poisson/Gamma–Poisson error family as the Palmer interpretation.

### Bounded abundance-scaling description

After the five within-system concentration results were established, a bounded post-hoc analysis described the relationship between total breeding abundance \(N\) and effective breeding-component number \(E\):

\[
\log E_t = \alpha_i + \kappa_i \log N_t.
\]

This search was explicitly closed after evaluating a finite set of scaling, threshold, slow-state and transition-asymmetry candidates. It generated a hypothesis about directional abundance–space coupling but does not contribute prospective evidence to the Palmer or Signy concentration decisions. We use it here only to compare whether effect **direction** and **magnitude** transfer to the regional analysis.

### MAPPPD regional scale-transfer analysis

For the broader spatial test we used the pinned CCheCastaldo/mapppdr snapshot at commit 88c73a507e0921b2541c218c71eaf16721bc6502. The snapshot contains long-term nest-count observations for Adélie, chinstrap and gentoo penguins across Antarctica. Previous outcome-blind audits identified 152 candidate site × species units with at least five nest-count years spanning at least 10 years across 122 distinct sites and 10 APBP regions. Observation methods were heterogeneous, including ground, aerial, photographic and remote-imagery records.

We did not create a new observation-selection rule for the concentration analysis. Instead, we reused the frozen Paper 2 1980–2025 bridged cohort and observation-calibration code. This cohort retains site × species series meeting the earlier coverage rule and uses same-season repeated observations to estimate a direct-versus-image observation offset and accuracy-dependent variances. In the regional analysis, repeated same-season observations were method-corrected on the \(\log(1+n)\) scale and precision-collapsed before calculating site-level states.

The regional parent unit was **species × published APBP region** and the components were site IDs. These parent units are monitored geographic networks, not assumed closed demographic populations.

#### Coverage-only support gate

Before regional concentration outcomes were computed, we froze a deterministic structural gate. A network required at least three retained sites, at least five seasons observed at every retained site, and at least 10 calendar years between the first and last complete seasons.

Within each species × region group, the roster algorithm began with all sites in the already-frozen cohort. If the complete-season requirement failed, the site with the fewest observed seasons was removed; ties were broken by removing the lexicographically greatest site ID. The algorithm stopped at the first qualifying roster and failed if fewer than three sites remained. Count magnitude did not enter roster selection.

#### Regional concentration statistic and nulls

For each eligible regional network, adjusted site counts were used to calculate annual \(N_t\) and \(E_t\). Network direction was defined by the OLS slope of \(\log N_t\) against calendar year.

The observed abundance–concentration elasticity was

\[
\log E_t = \alpha + \kappa_{obs}\log N_t.
\]

Positive \(\kappa_{obs}\) means that lower abundance is associated with fewer effective breeding sites.

The fixed-composition null pooled adjusted site counts across retained complete seasons to estimate time-invariant site shares \(q_j\). At each empirical total \(N_t\), site counts were drawn from a multinomial distribution with probabilities \(q_j\), thereby preserving the observed abundance trajectory while allowing the finite-count loss of low-share sites.

A second sensitivity added independent normal observation error on the \(\log(1+n)\) scale using the previously frozen variance assigned to each collapsed site-season observation. Both nulls used 20,000 simulations and seed 20261003. The focal calibrated effect, \(\Delta\kappa\), was the observed \(\kappa\) minus the median of the simulated null \(\kappa\) distribution.

A network was classified as individually supported only when \(\Delta\kappa>0\) and the one-sided Monte Carlo probability was \(\le0.05\) under both the fixed-composition and observation-error nulls.

The regional contract prohibited alternate geographic radii, hand-built clusters, alternate completeness thresholds, alternate abundance transformations, lags, hinges or trait searches in response to the result.

Because the local and regional records differ in temporal design, the regional extension was not treated as a second estimate of the local time-slope statistic. Local inference asks whether effective component number declines through time more strongly than expected under fixed composition and count error; regional inference asks whether effective component number covaries positively with abundance after panel-specific fixed-composition calibration. The shared estimand is therefore **directional redistribution beyond fixed composition**, not equality of test statistics or effect sizes. We do not pool local and regional p-values or estimate a common cross-scale \(\kappa\).

### Reproducibility and computational assistance

All analyses were executed from version-controlled code, and numerical outputs were checked against frozen result receipts and source-data checksums. OpenAI ChatGPT (GPT-5.6 Sol) was used during analysis and manuscript development to assist with code drafting and review, literature searching, statistical sensitivity-analysis scripting, and editorial drafting. It was not treated as an author or an independent source of scientific authority. All generated code, citations, numerical outputs, interpretations, and manuscript text were checked by the authors, who retain responsibility for the work.

### Descriptive internal pathways

After the five within-system concentration results were known, a bounded non-inferential decomposition recorded whether the initially dominant component remained dominant and how its share changed. These summaries have no p-values and cannot alter the primary concentration classifications.

The three increasing MAPPPD regional networks are likewise used only as descriptive context. No formal regional ratchet or hysteresis test was frozen before their outcomes were computed.

## Results

### Within-system concentration replicated across regions and species

Effective breeding-component number fell in all three eligible Palmer Adélie sample-colony monitoring networks. Cormorant declined from 3.535 to 2.859 (−19.1%), Humble from 4.625 to 2.285 (−50.6%), and Litchfield from 5.783 to 1.000 before all retained monitored components reached zero (−82.7%). Under the most severe frozen Gamma–Poisson 20%-CV model, one-sided probabilities were 0.0380, 0.000010 and 0.000010, respectively; no one of 100,000 joint simulations produced slopes simultaneously as negative as observed on all three islands.

Signy independently reproduced the outcome. In the prospectively frozen Adélie panel, breeding pairs declined from 2,342 to 1,217 while \(E\) fell from 3.081 to 1.936 (−37.2%). None of 100,000 simulations under the severe 20%-CV null was as negative as the observed \(E\) slope (plus-one p = 0.000010). The later strict literal-roster robustness analysis over 1998–2009 reached the same qualitative conclusion.

The separately frozen chinstrap test also passed. Breeding pairs declined from 1,642 to 581 and \(E\) declined from 4.438 to 2.191 (−50.6%). Under the severe 20%-CV null, one of 100,000 simulations was at least as negative as observed (plus-one p = 0.000020).

Thus the within-system result transferred from the Palmer discovery system to an independent Antarctic region and from Adélie to chinstrap penguins.

### The local scaling direction was consistent but not a universal exponent

Across the five Palmer/Signy monitoring trajectories, post-hoc annual log–log elasticities were positive in every trajectory: 0.069, 0.203, 0.465, 0.289 and 0.366. A population-fixed-effect model gave a common descriptive \(\kappa=0.250\), with leave-one-population-out estimates ranging from 0.139 to 0.354.

The relation was much stronger over long trajectories than from one year to the next: the common level model had \(R^2=0.585\), whereas first differences gave \(\kappa=0.120\) and \(R^2=0.071\). A fixed set of hinge models at 50%, 25% and 10% abundance remaining did not improve held-out prediction over the single log-linear relation. The bounded exploration therefore suggested slow, sublinear structural change rather than a common abrupt collapse threshold.

### Regional breeding-site networks retained the same concentration direction

Thirteen species × APBP-region groups occurred in the frozen MAPPPD cohort. Seven passed the coverage-only fixed-roster gate, spanning all three *Pygoscelis* species and three published regions: the Central-west Antarctic Peninsula, South Shetland Islands and Victoria Land.

Four eligible networks had declining abundance over their retained complete seasons. All four had positive observation-error-calibrated \(\Delta\kappa\).

Adélie penguins in the Central-west Antarctic Peninsula retained three sites across five complete seasons and had \(\kappa_{obs}=0.080\), \(\Delta\kappa=+0.073\), and observation-error p = 0.108. South Shetland Adélie retained four sites across seven seasons and had \(\kappa_{obs}=0.088\), \(\Delta\kappa=+0.115\), and p = 0.0148.

Chinstrap penguins in the Central-west Antarctic Peninsula retained three sites across 10 seasons and had \(\kappa_{obs}=0.022\), \(\Delta\kappa=+0.017\), and p = 0.432. South Shetland chinstrap retained six sites across eight seasons and had \(\kappa_{obs}=0.445\), \(\Delta\kappa=+0.434\), and p = 0.0152.

Thus two of four declining networks were individually supported under both regional nulls, but the direction was positive in all four. Their median observation-error-calibrated effect was +0.094. These are panel-level support calls defined by the frozen regional contract, not a family-wide rejection across four panels; no multiplicity-adjusted regional generality test was prespecified. The exact 4/4 positive sign count has a nominal one-sided sign probability of 0.0625, but species × region panels within the same region are not independent geographic replicates, so we treat that probability as descriptive only.

The geographic split was clear: both South Shetland networks survived the observation-error sensitivity, whereas the Central-west Antarctic Peninsula networks pointed in the same direction but did not.

### Direction transferred more consistently than magnitude

The four declining regional networks had raw \(\kappa\) values of 0.080, 0.088, 0.022 and 0.445, with a median of 0.084. This range overlaps the five within-system values but does not cluster around the descriptive local common estimate of 0.250.

The existing data therefore support a shared **sign** of abundance-linked breeding-space contraction more strongly than a common exponent. The value near one quarter that emerged from the five local trajectories is not treated as a universal scaling constant.

### Increasing abundance did not necessarily rebuild effective breeding-site number

Three eligible regional networks increased in abundance. Adélie penguins in Victoria Land increased from approximately 387,917 to 516,140 adjusted breeding pairs (+33.1%), while \(E\) declined from 4.85 to 3.56 (−26.6%). Gentoo penguins in the Central-west Antarctic Peninsula increased from approximately 19,084 to 23,253 (+21.8%), while \(E\) declined from 4.93 to 4.13 (−16.3%). South Shetland gentoo increased from approximately 11,910 to 19,544 (+64.1%), while \(E\) changed little but still ended lower, from 3.90 to 3.86 (−1.1%).

These patterns are qualitatively consistent with the earlier slow-state description, in which annual abundance rebounds seldom coincided with immediate recovery of effective component number. They do not constitute a confirmatory regional hysteresis result because no such test was frozen for the increasing MAPPPD panels.

### The internal route to concentration was not conserved

The five supported within-system populations reached concentration through different component-level trajectories.

At Palmer, the monitored colony-code component that was largest initially had zero breeding pairs by the final eligible census in all three sample-colony monitoring networks. Dominance shifted to a different component on Cormorant, Humble and Litchfield.

At Signy, the opposite occurred. The initially dominant Adélie component remained dominant and increased from 47.5% to 69.4% of the retained population. The initially dominant chinstrap component likewise remained dominant and increased from 40.0% to 65.6%.

The replicated endpoint therefore does not require preferential survival of the historically largest breeding unit. What transfers is concentration of breeding effort, not the identity or rank of the component that carries the remnant population.

## Discussion

### Decline has a reproducible spatial trajectory beyond abundance loss

Across the strongest within-system evidence, five declining monitored breeding-system trajectories in two Antarctic monitoring systems and two *Pygoscelis* species lost effective breeding components beyond expectations from proportional thinning and prespecified count-error models. The Signy analyses were frozen before their concentration effects were computed, so the result is not confined to the Palmer discovery system.

The MAPPPD extension moves the question one spatial level higher. Here components are not subcolonies or colony-code units within an island; they are monitored breeding sites within published Antarctic regions. All four estimable declining networks had positive null-calibrated abundance–concentration effects, although only two were individually supported after observation-error sensitivity.

The appropriate synthesis is therefore neither “five local examples” nor “a universal Antarctic law.” It is **cross-scale directional recurrence within Antarctic *Pygoscelis***. When abundance declines, reproduction tends to become disproportionately concentrated into fewer effective monitored breeding components, and that direction can persist when the spatial grain of a component is enlarged.

This extends established abundance–space theory without claiming that the abundance–occupancy relationship itself is new. Range-contraction studies show that equal abundance losses can yield different spatial outcomes [@rodriguez2002], and effective-area work in marine fishes demonstrates density-dependent redistribution at geographic scales [@thorson2016]. Our contribution is to isolate an analogous process in discrete colonial-breeding units by explicitly conditioning on the observed abundance trajectory and asking whether **relative breeding composition changes beyond proportional thinning**.

### Direction is more portable than a scaling constant

A tempting interpretation of the five local trajectories was a common quarter-power-like contraction rule because their descriptive fixed-effect estimate was \(\kappa\approx0.25\). The regional results argue against elevating that number into a general law. Regional declining networks spanned \(\kappa=0.022\) to 0.445 and had a much lower median.

This distinction matters. A scaling exponent combines multiple biological and observational properties: the number and size distribution of available components, environmental heterogeneity, site fidelity, recruitment, movement, local extinction and the spatial scale at which components are defined. There is little reason to expect all of these to remain invariant when moving from within-island census units to regional breeding-site networks.

The more stable quantity in the present data is the **sign**: decreasing abundance was associated with decreasing effective breeding-space representation in every eligible declining regional network and every one of the five local trajectories. Generality therefore appears ordinal before it is metric. The system repeatedly moves in the same direction, while the rate of that movement remains contingent.

### Breeding-space organization may be a slower state than abundance

The bounded local scaling analysis showed a marked timescale separation. Long-term abundance and \(E\) were moderately coupled, but year-to-year changes in abundance explained little annual change in \(E\). The best simple held-out descriptor of normalized contraction was calendar time, and short-term abundance rebounds seldom coincided with recovery of effective component number.

The increasing MAPPPD networks provide independent descriptive context for that interpretation. All three ended with lower \(E\) despite higher abundance, including a roughly one-third abundance increase in Victoria Land Adélie and a roughly one-fifth increase in Central-west Antarctic Peninsula gentoo.

This is compatible with breeding-space organization behaving as a relatively slow ecological state. Once particular breeding components are lost or become weakly represented, numerical recovery need not immediately reconstruct the previous spatial distribution. Site fidelity, persistent habitat differences, recruitment into established groups and delayed colonization could all generate such inertia [@mcdowall2019]. However, the present data do not establish hysteresis: the local frozen ratchet criterion failed, and no formal regional ratchet test was preregistered.

### The same endpoint can emerge through different local mechanisms

Palmer and Signy provide a strong warning against treating concentration as evidence for one component-level mechanism. At Signy, the initially dominant breeding unit behaved like a persistent core. At Palmer, every initially dominant monitored colony-code component reached zero and another unit inherited dominance.

That divergence means the result cannot be summarized as “large colonies survive.” Persistent habitat quality may matter in some systems, but historical size alone is insufficient. Torgersen mapping reaches a similar conclusion from physical subcolonies: larger historical subcolonies often persisted longer, yet terrain and snow altered those relationships and some retained footprints fragmented internally [@cimino2025].

Concentration should therefore be interpreted as a population-organization endpoint. Differential habitat quality, breeding-site fidelity, survival, recruitment, movement, breeding participation and social processes can all change the allocation of reproduction among components. Aggregate counts do not identify which mechanism operated in a given population.

### Contraction and fragmentation can occur simultaneously at different spatial levels

A reduction in effective coarse components does not imply that the remaining breeding distribution becomes geometrically compact at every scale. Mechanistic work predicts fine-scale fragmentation during Adélie decline [@mcdowall2019], while Torgersen mapping documents disappearance of whole historical breeding footprints alongside fragmentation within some retained footprints [@cimino2025].

The apparent contradiction is resolved by hierarchy. A population can lose entire breeding components at a coarse scale while the nests within surviving components split into smaller fragments. The MAPPPD result adds another level: a regional monitored network can also become dominated by fewer breeding sites even when within-site configuration is unresolved.

This suggests that “spatial contraction” should always name its observational level. Effective component number is not occupied area, and a fall in \(E\) at one level does not prescribe the sign of fragmentation, clustering or occupancy change at another.

### Limits to macroecological generalization

The regional extension is broader than the original two-system result but remains taxonomically narrow. Only Adélie and chinstrap penguins contribute declining regional networks; eligible gentoo regional networks were increasing. The two individually supported regional declines are both in the South Shetland Islands, so they are not independent geographic replications. MAPPPD coverage is also geographically uneven and methodologically heterogeneous. The Central-west Antarctic Peninsula regional rosters include Biscoe Point, a site in the broader Palmer-area APBP context, although the primary Palmer concentration populations are Cormorant, Humble and Litchfield. The MAPPPD analysis is therefore a **scale-transfer test with different component definitions**, not an additional independent geographic replication of Palmer; the independent geographic replication is Signy.

We therefore do not claim a general seabird or colonial-breeder rule. Nor do we treat published APBP regions as closed demographic populations. The regional analysis concerns redistribution within fixed sets of repeatedly monitored breeding sites.

The correct macroecological advance is more specific: an abundance-conditioned concentration signal first detected within breeding systems remains visible when the spatial unit is changed from local breeding components to regional site networks. Because the local and regional tests use different scale-appropriate statistics, this is an ordinal cross-scale inference about direction, not a meta-analysis of a common effect size. That cross-scale persistence is stronger evidence for a transferable ecological direction than the original five trajectories alone, but further taxonomic generality requires genuinely independent component-resolved data outside *Pygoscelis*.

### Monitoring implications

Population totals and occupied-site counts answer different questions. A population can retain many nominal sites while reproduction becomes heavily concentrated among them, or numerical recovery can occur without restoring an earlier distribution across sites. Effective breeding-component number provides a compact way to track this internal spatial state while retaining abundance as a separate variable.

For monitoring programs, the practical implication is not that \(E\) should replace total abundance. Rather, preserving component-resolved counts can reveal structural change that later aggregation destroys. Once only population totals remain, it is impossible to reconstruct whether decline was proportional across space or concentrated onto a subset of breeding components.

## Conclusion

Population decline in Antarctic *Pygoscelis* repeatedly involved more than numerical loss. Three Palmer Adélie sample-colony monitoring networks, a prospectively tested Signy Adélie panel and a separately frozen Signy chinstrap panel all became concentrated into fewer effective breeding components beyond proportional thinning. A bounded MAPPPD extension then showed the same abundance–concentration direction in all four estimable declining regional breeding-site networks, with robust individual support in South Shetland Adélie and chinstrap penguins.

What generalized was not a universal exponent or a universal refuge. The magnitude of contraction varied widely, and Palmer and Signy reached the same endpoint through opposite changes in component dominance. The strongest current inference is therefore directional and hierarchical: **as Antarctic penguin populations decline, breeding effort can become disproportionately concentrated into fewer effective components across multiple spatial levels, while the rate and local mechanism of that contraction remain contingent.**

## Data availability

Palmer LTER Adélie census: DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e.

Signy Adélie: DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d.

Signy chinstrap: DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9.

The MAPPPD analysis uses the public CCheCastaldo/mapppdr repository pinned at commit 88c73a507e0921b2541c218c71eaf16721bc6502.

Frozen endpoint contracts, outcome-blind support audits, result receipts and analysis scripts are maintained in the mina repository.

## References

See docs/REFERENCES_V6.bib.
