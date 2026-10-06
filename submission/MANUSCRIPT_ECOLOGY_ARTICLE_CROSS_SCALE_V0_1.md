# Breeding-component concentration recurs across spatial scales in Antarctic penguins

**Ecology Article candidate v0.1 — cross-scale concentration synthesis**

## Abstract

Population change has a spatial form as well as a magnitude, but concentration into fewer breeding components can arise mechanically when abundance changes. We asked whether breeding effort in Antarctic colonial penguins becomes concentrated beyond fixed-composition expectations and whether that concentration is specific to population decline. We quantified effective breeding-component number as \(E=1/\sum_j p_j^2\), where \(p_j\) is the share of breeding pairs in component \(j\), and compared observed changes with nulls conditioned on the empirical abundance trajectory. Within the Palmer discovery system, three island-based Adélie penguin (*Pygoscelis adeliae*) sample-colony monitoring networks declined in \(E\) by 19–83%; all exceeded frozen count-error null expectations. Prospectively frozen external tests at Signy Island independently supported the same outcome in Adélie penguins (−37%) and chinstrap penguins (*P. antarcticus*; −51%). We then moved one level up the spatial hierarchy using the pinned Antarctic Penguin Biogeography Project archive. Seven species × region networks were structurally estimable. Among four declining networks, all had positive observation-error-calibrated abundance–concentration effects, although only South Shetland Adélie and chinstrap networks were individually supported (p = 0.0148 and 0.0152). Crucially, all three increasing regional networks also ended with lower \(E\); in Victoria Land Adélie and Central-west Antarctic Peninsula gentoo, \(E\) declined while abundance increased, yielding negative abundance–concentration elasticities. Thus the strong within-system evidence establishes non-proportional concentration during decline, but the regional extension does not support interpreting concentration as decline-specific. Instead, it suggests that breeding-component organization can change partly independently of abundance trend. Because the increasing regional panels were sparse and no trend-asymmetry test was frozen, this does not establish hysteresis or a ratchet.

**Keywords:** abundance–occupancy; Antarctica; colonial breeding; effective number; penguins; population decline; spatial contraction; spatial scale

## Introduction

Population decline is usually summarized by how many individuals remain. Yet a declining population also has a spatial state: the remaining individuals may continue to occupy the same places in roughly the same proportions, or reproduction may become increasingly concentrated into a smaller subset of locations. These possibilities are not equivalent. Equal losses of abundance can produce very different spatial contractions depending on where losses occur within a distribution [@rodriguez2002], and positive abundance–occupancy relationships do not by themselves distinguish a change in spatial organization from the mechanical disappearance of low-count sites as abundance falls [@gaston2000].

This distinction has a direct analogue in density-dependent distribution and habitat-selection theory. For marine fishes, proportional-density and basin-type models differ in whether spatial use remains proportionally stable or contracts with abundance; effective occupied area can therefore contain information not recoverable from abundance alone [@thorson2016]. In the classical ideal-free framework, individuals distribute among habitat patches according to patch payoffs and density-dependent competition [@fretwell1970]. A simple reversible basin-like interpretation therefore predicts that contraction during decline should reverse as abundance recovers and secondary breeding components are reoccupied.

Low-density habitat-selection theory provides a contrasting possibility. If fitness initially increases with local density, or if settlement costs decline in the presence of conspecifics, patch choice can remain aggregative even before crowding becomes important [@greene2001]. Conspecific attraction can reduce the fraction of occupied patches in metapopulation models [@ray1991], and colonial seabirds can use the breeding performance of conspecifics as information when selecting breeding habitat [@danchin1998]. These processes make a distinct qualitative prediction: breeding-component concentration need not reverse immediately when summed monitored abundance increases. We use this contrast only as an interpretive framework. The present census data do not measure individual settlement decisions or fitness-density curves.

Colonial breeders provide a discrete and strongly hierarchical version of this problem. Individuals occupy nests, nests form aggregations, aggregations occur within subcolonies or census units, and multiple breeding sites form larger regional networks. Population change can therefore reorganize breeding allocation among monitored components at more than one level.

Penguins are especially useful for separating the spatial organization of reproduction from total abundance. *Pygoscelis* penguins forage at sea but reproduce on discrete terrestrial breeding patches. Within those patches, nesting configuration and habitat matter: Adélie reproductive performance varies with subcolony-scale conditions [@schmidt2021], mechanistic models predict fragmentation of nesting aggregations during decline [@mcdowall2019], and long-term reconstruction at Torgersen Island shows non-random loss of historical subcolonies associated with terrain and snow [@cimino2025]. At broader scales, the Antarctic Penguin Biogeography Project (APBP/MAPPPD) compiles long-term abundance observations across the Antarctic breeding ranges of Adélie, chinstrap and gentoo penguins [@checastaldo2023].

The inferential difficulty is that spatial contraction can appear even when the latent composition is unchanged. If a population with fixed relative allocation among components becomes small, finite counts alone increase the probability that low-share components reach zero. Measurement error can further exaggerate apparent redistribution. A test for ecological reorganization must therefore condition on the abundance trajectory and ask whether changes in relative composition exceed those expected under a fixed spatial allocation.

Our analyses developed in three stages with different degrees of prospective independence. First, the Palmer Archipelago provided a discovery system: three island-based Adélie sample-colony monitoring networks with stable colony-code rosters showed strong within-network concentration beyond fixed-composition count-error nulls. Second, the same effective-component endpoint and null logic were frozen before testing independent Signy Island data, first in Adélie penguins and then in a separately frozen chinstrap analysis. Those tests established geographic and cross-species replication within *Pygoscelis*. Third, after the local contraction pattern and its candidate abundance scaling had been identified, we asked whether the **direction** of the pattern survived a change in spatial level. Using only an already-pinned MAPPPD snapshot and already-frozen observation handling, we defined species × published APBP region as monitored networks and individual breeding sites as components, froze a coverage-only eligibility rule, and then opened the regional concentration outcomes.

The resulting design distinguishes three questions. First, does decline produce concentration beyond proportional thinning within breeding systems? Second, does the same outcome recur in an external region and species? Third, when breeding components are redefined one level higher—from within-site census units to breeding sites within regional networks—does abundance-linked concentration recur among declining networks, and what boundary do the eligible increasing networks place on a decline-specific interpretation? The regional contract was frozen to test abundance–concentration direction rather than a formal decline-versus-increase asymmetry, so increasing panels are used to constrain interpretation rather than to claim a preregistered ratchet or hysteresis test.

## Materials and Methods

### Effective breeding-component number

At every spatial level we described relative breeding allocation using the inverse-Simpson effective number,

\[
E_t = \frac{1}{\sum_j p_{jt}^2},
\]

where \(p_{jt}=n_{jt}/\sum_j n_{jt}\) and \(n_{jt}\) is the breeding-pair count for component \(j\) in season \(t\). \(E\) equals the number of equally represented components that would generate the observed concentration. It therefore falls when a larger share of reproduction is carried by fewer components.

We use the generic term **effective breeding-component number** because the physical meaning of a component differs among data sets. Palmer components are long-term colony-code census units within island breeding systems; Signy components are monitored breeding colonies or colony units; MAPPPD regional components are repeatedly monitored breeding sites. We do not interpret these units as equal-area habitat polygons.

### Palmer discovery system

The Palmer analysis used the public Palmer Station Antarctica Long Term Ecological Research Adélie breeding-pair table archived at DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e (EDI revision knb-lter-pal.87.7), spanning 1991–2017. Source-provenance checks show that its colony-code rows correspond to the historical fixed sample-colony monitoring panel rather than an exhaustive enumeration of all physical subcolonies on each island: in 1993 the frozen table contains 54 positive monitored colony codes, closely matching contemporary program documentation of 54 sample colonies. We therefore treat yearly sums as **summed monitored-component abundance**, not island-wide population totals. Primary concentration inference was restricted to Cormorant, Humble and Litchfield because those island-based monitoring networks retained unchanged reported colony-code rosters over their eligible intervals. Litchfield contributed through its final positive monitored-panel census.

For each island-year we calculated \(E\). The observed concentration statistic was the OLS slope of \(E\) against calendar year. We estimated one time-invariant component-share vector from cumulative counts within each island and imposed the observed summed monitored-component abundance trajectory on that fixed composition. Counts were then simulated under Poisson, Gamma–Poisson 10% multiplicative-CV and Gamma–Poisson 20% multiplicative-CV observation models. Each frozen model used 100,000 simulations. Support required a negative observed \(E\) slope and a one-sided Monte Carlo probability \(\le 0.05\) under every frozen error model.

Palmer is the discovery system. Its concentration analysis is not represented as prospectively generated evidence.

### Signy external and cross-species replications

The external Adélie test used the NERC EDS UK Polar Data Centre data set *Population size and breeding success of Adelie penguins on Signy Island from 1978 to 2020* (DOI: 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d). Before the relevant \(E\) outcome was calculated, an outcome-blind support audit froze the eligible monitoring units and seasons. The primary panel contained five canonical units across 22 complete seasons from 1996–2019, excluding incomplete 1997 and 2010 records. A later strict literal-roster analysis over 1998–2009 was retained as robustness rather than replacing the earlier endpoint.

The cross-species test used the corresponding Signy chinstrap data set (DOI: 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9). Nine literal colony units were frozen before the chinstrap concentration effect was computed, using the same 22 complete primary seasons. The summed abundance trajectory first had to pass a frozen decline gate. Conditional on that gate, support required a negative \(E\) trend more extreme than all prespecified fixed-composition count-error nulls.

The Signy tests used the same \(E\) definition and the same Poisson/Gamma–Poisson error family as the Palmer interpretation.

### Bounded abundance-scaling description

After the five within-system concentration results were established, a bounded post-hoc analysis described the relationship between summed monitored breeding abundance \(N\) and effective breeding-component number \(E\):

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

The regional contract prohibited alternate geographic radii, hand-built clusters, alternate completeness thresholds, alternate abundance transformations, lags, hinges or trait searches in response to the result. Complete evidence provenance and the full eligible regional panel table are provided in Appendix S1: Sections S1 and S7 and Table S4.

Because the local and regional records differ in temporal design, the regional extension was not treated as a second estimate of the local time-slope statistic. Local inference asks whether effective component number declines through time more strongly than expected under fixed composition and count error; regional inference asks whether effective component number covaries positively with abundance after panel-specific fixed-composition calibration. The shared estimand is therefore **directional redistribution beyond fixed composition**, not equality of test statistics or effect sizes. We do not pool local and regional p-values or estimate a common cross-scale \(\kappa\).

### Reproducibility and computational assistance

All analyses were executed from version-controlled code, and numerical outputs were checked against frozen result receipts and source-data checksums. OpenAI ChatGPT (GPT-5.6 Sol) was used during analysis and manuscript development to assist with code drafting and review, literature searching, statistical sensitivity-analysis scripting, and editorial drafting. It was not treated as an author or an independent source of scientific authority. All generated code, citations, numerical outputs, interpretations, and manuscript text were checked by the authors, who retain responsibility for the work.

### Descriptive internal pathways

After the five within-system concentration results were known, a bounded non-inferential decomposition recorded whether the initially dominant component remained dominant and how its share changed. These summaries have no p-values and cannot alter the primary concentration classifications.

The three increasing MAPPPD regional networks are likewise used only as descriptive context. No formal regional ratchet or hysteresis test was frozen before their outcomes were computed. Their complete endpoint summary is provided in Appendix S1: Table S5, and component-route context is provided in Appendix S1: Section S9 and Figure S1.

## Results

### Within-system concentration replicated across regions and species

Effective breeding-component number fell in all three eligible Palmer Adélie sample-colony monitoring networks. Cormorant declined from 3.535 to 2.859 (−19.1%), Humble from 4.625 to 2.285 (−50.6%), and Litchfield from 5.783 to 1.000 before all retained monitored components reached zero (−82.7%). Under the most severe frozen Gamma–Poisson 20%-CV model, one-sided probabilities were 0.0380, 0.000010 and 0.000010, respectively; no one of 100,000 joint simulations produced slopes simultaneously as negative as observed on all three islands.

Signy independently reproduced the outcome. In the prospectively frozen Adélie panel, breeding pairs declined from 2,342 to 1,217 while \(E\) fell from 3.081 to 1.936 (−37.2%). None of 100,000 simulations under the severe 20%-CV null was as negative as the observed \(E\) slope (plus-one p = 0.000010). The later strict literal-roster robustness analysis over 1998–2009 reached the same qualitative conclusion.

The separately frozen chinstrap test also passed. Breeding pairs declined from 1,642 to 581 and \(E\) declined from 4.438 to 2.191 (−50.6%). Under the severe 20%-CV null, one of 100,000 simulations was at least as negative as observed (plus-one p = 0.000020).

Thus the within-system result transferred from the Palmer discovery system to an independent Antarctic region and from Adélie to chinstrap penguins. The five normalized abundance and effective-component trajectories are shown in Figure 1.

### The local scaling direction was consistent but not a universal exponent

Across the five Palmer/Signy trajectories, post-hoc annual log–log elasticities were positive in every population: 0.069, 0.203, 0.465, 0.289 and 0.366. A population-fixed-effect model gave a common descriptive \(\kappa=0.250\), with leave-one-population-out estimates ranging from 0.139 to 0.354.

The relation was much stronger over long trajectories than from one year to the next: the common level model had \(R^2=0.585\), whereas first differences gave \(\kappa=0.120\) and \(R^2=0.071\). A fixed set of hinge models at 50%, 25% and 10% abundance remaining did not improve held-out prediction over the single log-linear relation. The bounded exploration therefore suggested slow, sublinear structural change rather than a common abrupt collapse threshold.

### Regional concentration was not unique to declining networks

Thirteen species × APBP-region groups occurred in the frozen MAPPPD cohort. Seven passed the coverage-only fixed-roster gate, spanning all three *Pygoscelis* species and three published regions: the Central-west Antarctic Peninsula, South Shetland Islands and Victoria Land.

Four eligible networks had declining abundance over their retained complete seasons. All four had positive observation-error-calibrated \(\Delta\kappa\), meaning that lower abundance was associated with fewer effective breeding sites more strongly than expected under the fixed-composition null.

Adélie penguins in the Central-west Antarctic Peninsula retained three sites across five complete seasons and had \(\kappa_{obs}=0.080\), \(\Delta\kappa=+0.073\), and observation-error p = 0.108. South Shetland Adélie retained four sites across seven seasons and had \(\kappa_{obs}=0.088\), \(\Delta\kappa=+0.115\), and p = 0.0148. Chinstrap penguins in the Central-west Antarctic Peninsula retained three sites across 10 seasons and had \(\kappa_{obs}=0.022\), \(\Delta\kappa=+0.017\), and p = 0.432. South Shetland chinstrap retained six sites across eight seasons and had \(\kappa_{obs}=0.445\), \(\Delta\kappa=+0.434\), and p = 0.0152.

Thus two of four declining networks were individually supported under both regional nulls, while the calibrated direction was positive in all four. Their median observation-error-calibrated effect was +0.094. These are panel-level support calls defined by the frozen regional contract, not a family-wide rejection across four panels; no multiplicity-adjusted regional generality test was prespecified. The exact 4/4 positive sign count has a nominal one-sided sign probability of 0.0625, but species × region panels within the same region are not independent geographic replicates, so we treat that probability as descriptive only (Figure 2).

The three increasing networks, however, change the interpretation of the regional extension. Victoria Land Adélie increased from approximately 387,917 to 516,140 adjusted breeding pairs (+33.1%), while \(E\) declined from 4.85 to 3.56 (−26.6%), giving \(\kappa_{obs}=-0.358\) and observation-error-calibrated \(\Delta\kappa=-0.355\). Central-west Antarctic Peninsula gentoo increased from approximately 19,084 to 23,253 (+21.8%), while \(E\) declined from 4.93 to 4.13 (−16.3%), with \(\kappa_{obs}=-0.238\) and \(\Delta\kappa=-0.228\). South Shetland gentoo increased from approximately 11,910 to 19,544 (+64.1%); \(E\) changed little but still ended lower, from 3.90 to 3.86 (−1.1%), with \(\Delta\kappa=+0.020\).

All three increasing networks therefore ended with lower effective breeding-site number than they began with, even though their abundance trajectories had the opposite sign from the declining networks. The regional analysis does not establish a common trend-independent concentration law: panels contain only 3–11 sites and 5–10 complete seasons, panels within regions are not independent, and no formal decline-versus-increase asymmetry test was frozen. It does, however, rule out a simple interpretation in which regional concentration is only a consequence of population decline (Figure 3).

### Abundance-linked scaling transferred only within the declining subset

Within the four declining regional networks, raw \(\kappa\) values were 0.080, 0.088, 0.022 and 0.445, with a median of 0.084. This shared positive sign is consistent with the five declining Palmer/Signy trajectories, but the increasing regional panels show that the sign of \(\kappa\) is not a general property of concentration itself: when abundance increased while \(E\) declined, \(\kappa\) became negative.

The regional data therefore separate two ideas that should not be conflated. First, among declining networks, lower abundance can be associated with excess concentration beyond fixed composition. Second, effective breeding-site number can also decline while abundance increases. The former is an abundance-conditioned scaling result; the latter is a temporal concentration pattern that the present contract was not designed to test formally.

The value near one quarter that emerged from the five local trajectories is therefore not treated as a universal scaling constant, and no single \(\kappa\) sign is claimed across increasing and declining regional networks.

### Increasing abundance did not necessarily rebuild effective breeding-site number

The three increasing MAPPPD networks provide descriptive evidence that numerical growth need not reconstruct a previous spatial distribution. This is consistent with the earlier bounded slow-state exploration, in which effective-component number increased during only 8 of 31 annual abundance rebounds. However, the local frozen ratchet criterion failed because the fitted rebound elasticity was negative, and no formal regional ratchet or hysteresis test was preregistered.

The increasing networks therefore serve as a boundary on the decline-specific interpretation and as a prospectively testable hypothesis for independent data: concentration may be only weakly reversible, or may reflect a directional reorganization that is partly independent of abundance trend. The present regional data cannot distinguish those possibilities.

### The internal route to concentration was not conserved

The five supported within-system populations reached concentration through different component-level trajectories.

At Palmer, the breeding component that was largest initially had zero breeding pairs by the final eligible census in all three populations. Dominance shifted to a different component on Cormorant, Humble and Litchfield.

At Signy, the opposite occurred. The initially dominant Adélie component remained dominant and increased from 47.5% to 69.4% of the retained population. The initially dominant chinstrap component likewise remained dominant and increased from 40.0% to 65.6%.

The replicated endpoint therefore does not require preferential survival of the historically largest breeding unit. What transfers is concentration of breeding effort, not the identity or rank of the component that carries the remnant population. The contrasting nominal component trajectories are shown in Appendix S1: Figure S1.

## Discussion

### Concentration during decline is strongly replicated within breeding systems

Across the strongest within-system evidence, five declining monitored breeding-system trajectories in two Antarctic monitoring systems and two *Pygoscelis* species lost effective breeding components beyond expectations from proportional thinning and prespecified count-error models. The Signy analyses were frozen before their concentration effects were computed, so this result is not confined to the Palmer discovery system.

That inference should remain narrow and strong: **within the observed declining monitoring systems, lower monitored breeding abundance was accompanied by non-proportional concentration of reproduction into fewer effective monitored components**. None of the Palmer or Signy panels provides a comparable sustained increase phase, so these data alone cannot determine whether concentration is specific to decline or whether the same spatial state can persist during numerical recovery.

### The regional extension is a boundary condition, not a simple replication of decline-specific contraction

The MAPPPD analysis moved the component definition one spatial level higher, from within-system census units to monitored breeding sites within published Antarctic regions. Among the four declining regional networks, all four had positive null-calibrated abundance–concentration effects and two South Shetland networks were individually supported. Taken alone, that subset would appear to extend the local decline-associated direction upward in scale.

The three increasing networks prevent that interpretation from being generalized to regional concentration as a whole. Every increasing network ended with lower \(E\) than it began with. In Victoria Land Adélie and Central-west Antarctic Peninsula gentoo, abundance increased while \(E\) declined substantially, so the abundance–concentration elasticity reversed sign. The third increasing network, South Shetland gentoo, changed little in \(E\) but also ended lower.

The regional result therefore contains two distinct statements. **Within declining networks**, the abundance-conditioned concentration direction recurred. **Across all eligible regional networks**, concentration was not uniquely tied to negative abundance trend. Because the increasing panels are sparse and non-independent and no trend-asymmetry test was frozen, we do not infer a trend-independent regional law. But the same evidence is sufficient to reject the stronger narrative that regional concentration is simply a spatial consequence of population decline.

This distinction changes the cross-scale synthesis. The local Palmer/Signy result is a replicated phenomenon of concentration during decline. The regional result is not a second-scale confirmation of a decline-specific mechanism; it shows that the regional spatial state can continue to concentrate under the opposite abundance trajectory.

### A socially structured habitat-selection hypothesis

The increasing regional networks sharpen the ecological interpretation because they distinguish a simple reversible abundance–space model from a broader class of socially structured habitat-selection processes. Under a reversible basin-like model, numerical recovery should progressively repopulate secondary breeding components, increasing (E) as abundance rises. That did not occur in the two clearest increasing regional panels: Victoria Land Adélie and Central-west Antarctic Peninsula gentoo gained abundance while (E) declined.

One mechanism capable of producing that pattern is positive social feedback at low density. Habitat-selection models with Allee-type fitness or density-dependent settlement costs can generate aggregation even among patches of similar intrinsic quality [@greene2001], and conspecific attraction can reduce equilibrium patch occupancy [@ray1991]. Colonial seabirds also provide empirical precedent for breeding decisions informed by the performance of conspecifics [@danchin1998]. In Adélie penguins, larger breeding aggregations can also differ in geometry and edge exposure, with consequences for reproductive performance and predation risk [@schmidt2021].

These observations make socially structured habitat selection a plausible hypothesis, but they do not identify it as the mechanism in our data. Aggregate colony counts do not reveal whether breeders moved among components, whether recruits copied conspecifics, whether local fitness increased with density, or whether persistent unmeasured habitat differences generated the same spatial pattern. The regional increasing panels were not covered by a frozen asymmetry test. We therefore use the social-feedback framework to generate a discriminating prediction for independent data: **if concentration is maintained by positive social feedback below saturation, excess concentration should also occur in increasing systems; if the pattern is a reversible response to habitat quality and crowding, increasing systems should instead re-expand across components.**

### Breeding-space organization may be a slow or weakly reversible state

The bounded local scaling analysis already suggested a timescale separation. Long-term abundance and \(E\) were moderately coupled, whereas year-to-year abundance changes explained little annual change in \(E\). Effective-component number increased during only 8 of 31 annual abundance rebounds. The frozen ratchet criterion nevertheless failed, because the rebound elasticity was negative rather than the prespecified weakly positive form.

The increasing MAPPPD panels are qualitatively consistent with weak spatial recovery: numerical growth did not restore effective site number over their retained intervals. They add a broader-scale observation in the same direction, but they do not convert the failed local ratchet test into evidence for hysteresis. A true ratchet hypothesis requires an independent design in which increasing and declining systems are both represented and the asymmetry statistic is frozen before outcomes are inspected.

The most useful hypothesis generated here is therefore not “decline causes concentration,” but a stricter one: **breeding-space concentration may be partly path-dependent or directionally persistent, such that numerical increase does not necessarily reverse prior spatial concentration**. That is a hypothesis for independent macroecological testing, not a conclusion from the present regional panels.

### A common \(\kappa\) is not the transferable quantity

A tempting interpretation of the five local trajectories was a common quarter-power-like contraction rule because their descriptive fixed-effect estimate was \(\kappa\approx0.25\). The regional results argue even more strongly against elevating that number into a general law. Declining regional networks span \(\kappa=0.022\) to 0.445, whereas two increasing networks with falling \(E\) have negative \(\kappa\).

Thus \(\kappa\) describes the direction of abundance–space coupling within a given abundance trajectory; it is not a universal measure of concentration independent of trend direction. What transfers among the declining panels is only the positive abundance-conditioned direction. The broader regional concentration pattern is better described directly with \(E\) through time than with a single shared elasticity.

### The same endpoint can emerge through different local mechanisms

Palmer and Signy provide a strong warning against treating concentration as evidence for one component-level mechanism. At Signy, the initially dominant breeding unit behaved like a persistent core. At Palmer, every initially dominant monitored colony-code component reached zero and another unit inherited dominance.

That divergence means the result cannot be summarized as “large colonies survive.” Persistent habitat quality may matter in some systems, but historical size alone is insufficient. Torgersen mapping reaches a similar conclusion from physical subcolonies: larger historical subcolonies often persisted longer, yet terrain and snow altered those relationships and some retained footprints fragmented internally [@cimino2025].

Concentration should therefore be interpreted as a population-organization endpoint. Differential habitat quality, breeding-site fidelity, survival, recruitment, movement, breeding participation and social processes can all change the allocation of reproduction among components. Aggregate counts do not identify which mechanism operated in a given population.

### Contraction and fragmentation can occur simultaneously at different spatial levels

A reduction in effective coarse components does not imply that the remaining breeding distribution becomes geometrically compact at every scale. Mechanistic work predicts fine-scale fragmentation during Adélie decline [@mcdowall2019], while Torgersen mapping documents disappearance of whole historical breeding footprints alongside fragmentation within some retained footprints [@cimino2025].

The apparent contradiction is resolved by hierarchy. A population can lose entire breeding components at a coarse scale while the nests within surviving components split into smaller fragments. The MAPPPD result adds another level: a regional monitored network can also become dominated by fewer breeding sites even when within-site configuration is unresolved.

This suggests that “spatial contraction” should always name its observational level. Effective component number is not occupied area, and a fall in \(E\) at one level does not prescribe the sign of fragmentation, clustering or occupancy change at another.

### Limits to macroecological generalization

The regional extension is broader than the original two-system result but remains taxonomically and statistically narrow. Only seven species × region networks passed the frozen structural gate, with 3–11 sites and 5–10 complete seasons. Panels within the same APBP region are not independent geographic replicates, and the two individually supported declining networks are both in the South Shetland Islands. MAPPPD coverage is geographically uneven and methodologically heterogeneous.

The increasing regional panels are especially important for interpretation but not sufficient for a formal trend-asymmetry claim. Their lower final \(E\) values show that regional concentration is not restricted to declining abundance trajectories in these data, but the regional contract did not preregister a time-trend test, a decline-versus-increase contrast, or a ratchet statistic. We therefore use them as a boundary condition and hypothesis generator rather than as confirmatory evidence for irreversible or trend-independent concentration.

The Central-west Antarctic Peninsula regional rosters also include Biscoe Point in the broader Palmer-area APBP context, although the primary Palmer concentration populations are Cormorant, Humble and Litchfield. The MAPPPD analysis is therefore a scale-transfer comparison with different component definitions, not an additional independent geographic replication of Palmer; Signy supplies the independent geographic replication.

We do not claim a general seabird or colonial-breeder law, nor do we treat published APBP regions as closed demographic populations. The strongest current inference has two levels: replicated non-proportional concentration **during decline** within breeding systems, and a broader regional indication that effective breeding-site concentration can occur under both declining and increasing abundance trajectories. Testing whether that second pattern reflects a genuine trend-independent concentration process or a weakly reversible spatial ratchet requires independent component-resolved systems with both positive and negative population trends.

### Monitoring implications

Summed monitored abundance and component-resolved allocation answer different questions. A population can retain many nominal sites while reproduction becomes heavily concentrated among them, or numerical recovery can occur without restoring an earlier distribution across sites. Effective breeding-component number provides a compact way to track this internal spatial state while retaining abundance as a separate variable.

For monitoring programs, the practical implication is not that \(E\) should replace total abundance. Rather, preserving component-resolved counts can reveal structural change that later aggregation destroys. Once only aggregate abundance remains, it is impossible to reconstruct whether change was proportional across monitored components or concentrated onto a subset.

## Conclusion

Population decline in Antarctic *Pygoscelis* repeatedly involved more than numerical loss. Three Palmer Adélie sample-colony monitoring networks, a prospectively tested Signy Adélie panel and a separately frozen Signy chinstrap panel all became concentrated into fewer effective breeding components beyond proportional thinning.

The broader MAPPPD extension changes how that result should be interpreted across scales. Among four declining regional networks, the abundance-conditioned concentration direction was positive in all four and individually supported in two South Shetland networks. But all three increasing regional networks also ended with lower effective breeding-site number, including Victoria Land Adélie and Central-west Antarctic Peninsula gentoo populations in which abundance increased while \(E\) declined.

The strongest current inference is therefore not that decline universally causes spatial contraction. It is that **non-proportional concentration is strongly replicated during decline within breeding systems, while at the regional scale breeding-component organization can become more concentrated under either sign of abundance change**. This makes monitored breeding-component organization a distinct spatial state rather than a simple transform of abundance. Whether that state is genuinely trend-independent, weakly reversible or ratchet-like remains an independent test for future component-resolved data.

## References

See docs/REFERENCES_V6.bib.
