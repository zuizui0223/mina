# Local demographic reorganization does not scale into a transferable island-resilience rule in Antarctic penguins

**Integrated manuscript draft v0.3**

## Abstract

Island populations can differ strongly in how decline unfolds, but local demographic structure and transferable cross-island predictors are not the same thing. We tested that distinction in Antarctic penguins at two nested scales. First, a complete 1991–2017 census of five neighbouring Adélie penguin (*Pygoscelis adeliae*) breeding islands near Palmer Station showed a highly coherent regional decline (PC1 = 96.4%) accompanied by pronounced within-island concentration. Effective colony number declined by 19–83% in the three islands with stable colony-code rosters, and fixed-composition count-error nulls did not reproduce the observed concentration trends. A secondary Palmer analysis suggested short-lived performance-linked redistribution, but a prospectively frozen Signy replication did not support the analogous lag-2 association. We then asked whether static breeding-island architecture predicted demographic coupling to shared forcing across three *Pygoscelis* species and 104 predictor-complete site × species units from 1980–2025. At the prespecified 2 km scale, area × habitat-complex interactions were negative in all three species, but the preregistered cross-species permutation test was non-confirmatory (median gamma_AH = -0.318; 9,999 permutations; one-sided p = 0.0947). A simpler breeding-space buffering hypothesis was also unsupported. Retrospective operating-characteristic analysis showed that the study had little sensitivity to common effects near the observed magnitude but about 80% detection for |gamma_AH| ≈ 0.50 and 90% near 0.54. The apparent 2-to-5 km sign reversal also failed a joint multi-radius null (p = 0.0810), so it was treated as radius sensitivity rather than ecological scale dependence. Together, these results reveal a sharp cross-scale asymmetry: decline can have a strong internal spatial-demographic architecture within islands while static island structure still fails to provide a confirmed, transferable rule for population response across Antarctica. The key issue is therefore not whether islands matter, but which level of island information transfers across space.

**Keywords:** Adélie penguin; Antarctic Peninsula; breeding islands; demographic coupling; habitat heterogeneity; island ecology; population decline; scale; spatial concentration

## Introduction

A central promise of island ecology is that local geography can make biological outcomes predictable. Island area, isolation and environmental heterogeneity have long been used to explain variation in species richness and extinction, and theory explicitly links heterogeneity to the amount of effective habitat available within finite space [@kadmon2007; @allouche2012]. Yet the ecological meaning of an island changes when the focal population obtains its principal resources outside the island. Seabirds and penguins are extreme examples: they forage in marine food webs but reproduce on terrestrial patches. In such systems, an island may constrain reproduction without containing the dominant trophic resource field.

This geometry motivates a distinction between an island as a **resource container** and an island as a **demographic response filter**. Marine subsidies can alter classical island-biogeographic relationships [@obrist2020], and seabirds themselves transport large quantities of marine-derived materials to terrestrial systems [@mulder2011; @grant2022]. The reciprocal demographic problem is less often isolated: when broad marine or regional forcing is shared across populations, can the spatial structure of a breeding island explain why local populations respond differently?

Two scales must be separated to answer that question. At a local scale, decline can be internally reorganized. A population can thin approximately proportionally across all occupied breeding components, or breeders can become increasingly concentrated into a smaller subset of components as abundance falls. Those outcomes imply different spatial-demographic trajectories even when island-total decline is similar. At a broader scale, however, the existence of local reorganization does not guarantee that static island properties will predict the strength of population response across sites. Local organization may depend on occupancy history, behaviour, fine-scale snow or terrain, density dependence, or other state variables that do not transfer through coarse landscape metrics.

The Palmer Archipelago provides a strong discovery system for the first scale. Adélie populations near Palmer Station have undergone major long-term declines, while neighbouring islands share regional environmental context but differ in snow accumulation, breeding habitat and demographic endpoint [@fraser2013; @pickett2018; @cimino2019; @cimino2025]. Independent work shows that subcolony persistence can be strongly structured by terrain and long-term snow conditions [@cimino2025], and that reproductive success varies at subcolony scale [@schmidt2021]. These observations suggest that decline should be analysed not only as loss of abundance but also as reorganization of breeders within islands.

The broader Antarctic system provides a test of whether that local logic generalizes. The Antarctic Penguin Biogeography Project compiles long-term abundance records across the breeding ranges of Adélie, chinstrap and gentoo penguins [@checastaldo2023]. We used this archive to ask whether static breeding-space amount and habitat-option heterogeneity predict site-specific coupling to demographic variation shared within each species. The focal prediction was an area-dependent heterogeneity effect. When terrestrial breeding space is scarce, increasing habitat complexity could subdivide limited effective breeding area; when breeding space is ample, heterogeneity could instead provide alternative breeding conditions. This idea is related to the area–heterogeneity tradeoff in island and community theory [@kadmon2007; @allouche2012], but here the response is not species richness. It is the coupling of a single breeding population to shared demographic forcing.

We therefore treated the study as a test of **cross-scale transferability of island information**. **Part I** asks whether a coherent regional decline acquires a reproducible internal spatial organization within islands. **Part II** then asks whether that local organization can be compressed into static island traits that predict demographic coupling across Antarctica. The two parts are inferentially independent: a strong Palmer result cannot rescue a null Antarctic-wide result, and no p-values are pooled across scales. The falsifiable proposition is deliberately asymmetric. Islands may contain real and repeatable local demographic structure while still failing to yield a transferable macroecological rule.

## Materials and Methods

### Part I: Palmer discovery system

#### Demographic census

The Palmer analysis used annual breeding-pair censuses from five Adélie breeding islands monitored by the Palmer Station Antarctica Long Term Ecological Research program: Christine, Cormorant, Humble, Litchfield and Torgersen. The synchronized panel spans 1991–2017 with 27 complete island-year observations. Colony-level counts were summed to island totals, and abundance was analysed as log(1 + N). Data provenance and checksums are frozen in the project receipts (Palmer LTER census DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e).

We standardized each island's log-abundance trajectory and used principal component analysis to quantify the common temporal component. Annual log growth was

$
g_{i,t}=\log(1+N_{i,t})-\log(1+N_{i,t-1}).
$

Year and island factors were also used descriptively to partition shared temporal and persistent island-level variation. These terms are descriptive and are not interpreted as identified environmental mechanisms.

#### Within-island concentration

For island-year (t), let (p_j) be the fraction of breeding pairs assigned to colony code (j). We defined effective colony number as

$
N_{\mathrm{eff}}=\frac{1}{\sum_j p_j^2}.
$

The concentration analysis was restricted to Cormorant, Humble and Litchfield, the three islands whose reported colony-code rosters remained unchanged across the synchronized period. For Litchfield, only positive-abundance years were retained.

For each island, the observed statistic was the ordinary least-squares slope of annual (N_{mathrm{eff}}) against centered calendar year. We tested whether that slope could arise from proportional thinning under a fixed-composition null. A time-invariant colony-code composition was estimated from cumulative counts, multiplied each year by the observed island total, and subjected to prespecified independent count-error models: Poisson sampling plus Gamma–Poisson sensitivities with 10% and 20% multiplicative CV. We generated 100,000 realizations per model. The one-sided island-specific probability was the fraction of simulated slopes at least as negative as observed; a joint probability required all three island slopes to be simultaneously at least as negative as observed.

This null preserves the empirical decline in island total while removing temporal change in latent colony composition. Rejection therefore establishes demographic redistribution beyond proportional thinning plus independent count error. It does not identify physical nesting polygons or a causal mechanism.

#### Independent spatial triangulation

We used published Torgersen mapping as phenomenon-level spatial triangulation rather than as a merged response dataset [@cimino2025]. That work reconstructs historic active subcolonies and links persistence/extinction to snow- and terrain-related landscape conditions. Agreement with the colony-code analysis is interpreted as independent evidence that concentration reflects a real spatial-demographic process, not proof that nominal colony codes correspond one-to-one with mapped footprints.

### Secondary local-dynamics follow-up and independent replication

After establishing the Palmer concentration phenomenon, we tested whether
relative reproductive performance carried short-lived information about later
within-island redistribution. Performance was defined as colony chick output
relative to a size-proportional within-island expectation and standardized
within island-season. The bias-resistant Palmer endpoint related performance in
season t to relative adult redistribution during t+1 -> t+2 while controlling
outcome-interval colony size and persistent colony identity. Because the Palmer
season-key provenance rule was repaired after coefficients had already been
exposed, this analysis is treated as fixed-specification validation rather than
independent confirmation.

We then froze an independent Signy replication before fitting any Signy
effect. Using the BAS/NERC Adélie breeding-success series for the standardized
1996/97–2019/20 window, we applied the same lag-2 performance-to-redistribution
endpoint and within-season permutation logic. Literal published colony labels
were retained, including the pooled label `A1 + A60`; exclusion of non-atomic
labels and exclusion of comment-flagged nonstandard seasons were mandatory
sensitivities. The primary Signy test used 100,000 within-season permutations
and was not allowed to be replaced by a favorable sensitivity.

### Part II: Antarctic-wide transferability test

#### Outcome-blind analysis frame

The broad-scale analysis used MAPPPD/APBP abundance data pinned to a fixed source commit. Gate 0 contained 152 Pygoscelis site × species units. A common 1980–2025 breeding-season window and predeclared temporal-coverage rules yielded 107 bridged units and 2,100 nest-count records. After joining the prespecified terrestrial predictors and preserving missingness at unsupported sites, the final predictor-complete frames contained 41 Adélie, 34 chinstrap and 29 gentoo site × species units.

Predictor construction was completed without demographic outcome magnitudes. At the primary 2 km radius, breeding-space amount was

$
A=z\left\{\log\left[1+\mathrm{ice\text{-}free\ area}\right]\right\}.
$

and breeding-option heterogeneity was

$
H=z\left\{\mathrm{Tier\ 2\ Habitat\ Complex\ richness}\right\}.
$

The focal interaction was \(A \times H\). Terrain relief was frozen as a separate predictor but was not used to rescue the primary interaction.

#### Observation model and recovery gates

Direct counts were the reference observation method. Image-based counts received one shared mean offset, supported by repeated direct/image observations within the same site × species × season. Observation precision was represented by two frozen accuracy groups: class 1 versus pooled classes 2–5. Unknown-vantage records were retained in the primary cohort but excluded from method-offset calibration.

Before real count magnitudes were opened, we required the complete estimation pipeline to recover prespecified null, simple-buffering and interaction scenarios on the real temporal and observation schedules. Candidate forcing partitions and estimators that failed these gates were rejected rather than retuned. The retained model used one species-wide latent annual forcing per species, while geography entered only as a loading-adjustment stratum (CCAMLR blocks for Adélie; APBP regions for chinstrap and gentoo). Full gate history and failed candidate estimators are reported in the Supplement and reproducibility receipts.

Within each species, site coupling was modelled conceptually as

$
\lambda_i =
1+\alpha_{b(i)}
+\gamma_A A_i
+\gamma_H H_i
+\gamma_{AH}A_iH_i
+b_i.
$

where \(\alpha_{b(i)}\) is the frozen spatial-block effect and \(b_i\) is a residual site loading deviation. Site-trait terms were centered within the frozen spatial block. The latent annual forcing had mean zero and site loadings were identified to a species-wide mean of one.

The process model used log1p abundance and propagated endpoint observation variance into interval likelihoods. Pre-outcome synthetic recovery required the estimator to recover null, simple-buffering and crossover scenarios under the real observation schedule. Species-wide forcing, the focal interaction and the cross-species median estimand all passed the frozen recovery rules before real outcomes were opened.

#### Primary hypothesis and inference

The primary paper-level statistic was the median \(\gamma_{AH}\) across the three species. The directional alternative was more negative. We used 9,999 permutations. Within each species and frozen spatial block, the complete site-trait tuple \((A,H,A\times H)\) was permuted among site time series, singleton blocks were fixed, and the complete V3 model—including forcing, drift, process variance, block intercepts and residual loadings—was re-estimated.

The paper-level p-value was

$
p=\frac{1+\#\{T_{\mathrm{perm}}\leq T_{\mathrm{obs}}\}}{9{,}999+1}.
$

Species-specific interaction p-values used the same one-sided rule and were Holm-adjusted across the three species.

A full point-estimate option–fragmentation crossover required

$
\gamma_{AH}<0,
$

$
\gamma_H-\gamma_{AH}\geq 0
$

at \(A=-1\) SD, and

$
\gamma_H+\gamma_{AH}<0
$

at \(A=+1\) SD.

#### Prespecified secondary and robustness analyses

The simple breeding-space buffering hypothesis was evaluated with A-only versions of the same spatially adjusted model. Species-specific one-sided permutation p-values were Holm-adjusted.

Observation robustness re-estimated the shared image/direct offset using exact-date direct/image pairs and pairs separated by no more than 14 days, then refit the unchanged V3 process model.

Spatial-support sensitivity used 1 km and 5 km area/richness predictors and 2 km Shannon diversity. These variants were descriptive only; none could replace the frozen 2 km richness analysis.

Because the raw interaction changed sign across radii, we performed a post-inference interpretation diagnostic. The entire 1/2/5 km trait tuple for each site was permuted jointly within species × spatial block, preserving cross-radius covariance. Across 9,999 permutations we recorded the probability of reproducing both the observed negative 2 km / positive 5 km sign switch and a 5 km minus 2 km contrast at least as large as observed. Ecological scale-dependence language was allowed only if this joint probability was (leq 0.05).

Finally, we quantified the information content of a non-rejected primary result using a retrospective operating-characteristic analysis. The unchanged V3 simulation/model and real observation layout were used to generate common three-species interaction magnitudes from -0.20 to -0.60. Each synthetic paper-level statistic was evaluated against the realized frozen 9,999-permutation null. We report raw detection fractions plus interpolated 80% and 90% detectable-effect thresholds. This analysis is not an equivalence test or confidence interval.

## Results

### Part I: coherent decline, divergent local organization

The five Palmer island populations shared a dominant long-term decline. The first principal component of standardized log abundance explained **96.4%** of total trajectory variation. Despite that shared temporal component, island endpoints differed, including persistence, strong decline and local extinction.

Within-island organization changed systematically during decline. Effective colony number fell from **3.54 to 2.86** on Cormorant, from **4.62 to 2.28** on Humble and from **5.78 to 1.00** on Litchfield before local extinction. These changes correspond to declines of approximately **19%**, **51%** and **83%**, respectively.

The concentration trends were not reproduced by fixed-composition nulls. Under the most severe prespecified 20% multiplicative-CV error model, Cormorant remained unusual (**p = 0.038**). In 100,000 simulations, no realization reached the observed negative slope on Humble or Litchfield (plus-one **p = 0.000010** for each), and no simulation produced slopes simultaneously as negative as all three islands (joint plus-one **p = 0.000010**).

Independent Torgersen mapping showed a parallel physical contraction from 23 historic active subcolonies to five active footprints and spatially structured extinction [@cimino2025]. The strongest inference from Part I is therefore that decline involved redistribution toward a smaller effective set of within-island breeding components, not proportional thinning alone.

[**Figure 1–2 near here**]

### Secondary local-dynamics follow-up did not transfer cleanly to Signy

At Palmer, relative reproductive performance carried short-lived information
about later within-island redistribution under the fixed specification. The
bias-resistant lag-2 coefficient was **0.0409** (one-sided permutation
**p = 0.00327**) and lag 3 remained positive (**0.0511**, **p = 0.00136**),
whereas the association faded by lags 4–5. Measured performance state itself
showed weak one- and two-year persistence, and past performance retained
incremental information about lag-2 redistribution after contemporaneous
performance, current group size and persistent colony identity were included
(bridge coefficient **0.0296**, **p = 0.00726**).

These follow-ups did not identify a simple win-stay/lose-switch mechanism.
A poor-performance-share test was compatible with redistribution or
replacement rather than a prespecified meaningful island-total loss, the
island-level performance/growth endpoint was inconclusive, and the frozen
lose-switch asymmetry was unsupported (delta = **−0.0126**, **p = 0.579**).

The independently frozen Signy test did not replicate the Palmer lag-2
association. The primary coefficient was **0.0213** (**p = 0.279**).
Excluding the pooled non-atomic label retained a positive but unsupported
coefficient (**0.0634**, **p = 0.0603**). Excluding two comment-flagged
nonstandard seasons produced **0.0727** (**p = 0.0207**), but this sensitivity
cannot replace the null primary replication. The Signy lose-switch hinge was
also unsupported. We therefore treat the Palmer performance-linked signal as a
locally plausible dynamic correlate rather than a demonstrated transferable
Antarctic mechanism.

### Part II: local island organization did not yield a confirmed Antarctic-wide rule

At the frozen 2 km richness scale, fitted area × heterogeneity interactions were negative in all three species:

- Adélie: (gamma_{AH}=-0.304);
- chinstrap: (gamma_{AH}=-1.184);
- gentoo: (gamma_{AH}=-0.318).

The preregistered paper-level statistic, the median across species, was **-0.318**. The frozen one-sided block-permutation test did not reject the null (**p = 0.0947**). Species-specific raw p-values were 0.2162, 0.0661 and 0.0563 for Adélie, chinstrap and gentoo, respectively; no species-specific interaction survived Holm adjustment.

The point-estimate geometry nevertheless differed among species. Chinstrap and gentoo satisfied the full crossover sign pattern. For chinstrap, the fitted low-area and high-area heterogeneity slopes were +1.901 and -0.467; for gentoo they were +0.427 and -0.209. Adélie had a negative interaction but the high-area heterogeneity slope remained slightly positive (+0.045), indicating attenuation rather than a sign-reversing crossover.

The primary result is therefore **directionally concordant but non-confirmatory**. We do not interpret the chinstrap/gentoo subset as a rescued positive result.

[**Figure 3 near here**]

### Simple breeding-space buffering was also unsupported

A-only estimates were negative in all three species:

- Adélie: (gamma_A=-0.280);
- chinstrap: (gamma_A=-0.200);
- gentoo: (gamma_A=-0.071).

However, raw one-sided permutation p-values were 0.1426, 0.4225 and 0.3067, and Holm-adjusted values were 0.4278, 0.6134 and 0.6134. Thus the simpler prediction that greater breeding-space amount consistently weakens coupling to shared forcing was also unsupported.

### Observation calibration did not explain the interaction direction

The primary image/direct multiplicative offset was approximately **1.040**. Exact-date matching estimated a factor of **1.069**, and matching within 14 days estimated **1.058**. Refit cross-species median interactions were -0.326 and -0.323, respectively. All three species retained negative interaction estimates under both calibrations, and chinstrap and gentoo retained the full point-estimate crossover classification. Thus the direction of the primary interaction was not an artifact of the broad same-season image calibration.

### Radius sensitivity did not establish biological scale dependence

Raw cross-species median interaction estimates varied across spatial support:

- 1 km: **-0.058**;
- 2 km, primary: **-0.318**;
- 5 km: **+0.107**.

At 2 km, replacing richness with Shannon diversity produced a median interaction of **-0.163** and retained the chinstrap/gentoo crossover classification but not the Adélie negative interaction.

The apparent radius reversal was not sufficiently unusual under the joint multi-radius null. A negative 2 km and positive 5 km sign switch occurred in **24.78%** of null permutations. A 5 km minus 2 km contrast at least as large as the observed **0.425** occurred with plus-one probability **0.0971**. The preregistered joint event—sign switch plus an observed-size contrast—occurred 809 times, giving plus-one probability **0.0810**. The total 1/2/5 km range was at least as large as observed in **26.45%** of null permutations.

Accordingly, we treat the radius result as **sensitivity to spatial support**, not as evidence for biological scale dependence.

[**Figure 4 near here**]

### The non-confirmatory result constrains very large, but not moderate, common effects

The 5% lower tail of the realized paper-level permutation null was approximately **-0.424**. In retrospective simulations, a common true interaction of -0.20 was never detected in 300 replicates; -0.30 was detected in **4.7%**, -0.35 in **11.7%**, -0.40 in **38.0%**, -0.45 in **59.7%**, -0.50 in **81.0%**, -0.55 in **92.7%**, and -0.60 in **96.7%**.

Interpolated detectable-effect thresholds were **|gamma_AH| = 0.498** for 80% detection and **0.539** for 90% detection. The observed absolute cross-species median, 0.318, was only about 64% of the 80% threshold.

The primary non-rejection therefore does not establish absence of an interaction around the observed magnitude. It does, however, make a very large and consistently expressed three-species interaction less plausible: common effects around 0.50–0.55 would usually have crossed the frozen rejection rule.

## Discussion

### Strong local organization did not become transferable cross-island information

The central result is a cross-scale asymmetry. At Palmer, a coherent regional decline acquired a clear internal spatial-demographic architecture: breeders became concentrated into fewer effective breeding components, and the pattern was too strong to be explained by proportional thinning plus prespecified count error. Across Antarctica, however, static breeding-island area and habitat complexity did not provide a confirmed general predictor of how strongly populations coupled to shared demographic forcing.

This is more informative than a simple contrast between a “positive” local analysis and a “negative” broad-scale analysis. It identifies a boundary on transferability. Island identity and within-island organization can contain real ecological information without that information being compressible into a small set of static island descriptors that travels successfully among populations. The inferential shortcut to avoid is therefore not merely assuming that islands matter, but assuming that the **same island information matters at every hierarchical scale**.

### Why local island effects need not transfer

Several mechanisms could generate strong local reorganization without a transferable broad-scale landscape rule. First, the relevant state variable may be occupancy history rather than potential habitat. A mapped habitat complex can exist without being used, and use can depend on colony density, social attraction, historical nesting footprints or access routes. Second, fine-scale snow, melt and drainage processes can matter within islands even when coarse landscape summaries are similar. Palmer work already shows interactions between geomorphology, snow conditions and breeding timing or persistence [@fraser2013; @cimino2019; @cimino2025]. Third, local movement among breeding components can reorganize a declining population without producing a stable relationship between static island area and demographic sensitivity.

These possibilities are mechanisms to test, not explanations identified by the present models. The species-wide latent forcing used in Part II is also a statistical device selected by pre-outcome recovery. It must not be interpreted as proof of a single species-wide climatic driver.

### Externally subsidized breeding islands are not simple resource islands

The result also clarifies how penguin breeding sites fit within island theory. Classical and extended island-biogeographic models show that area, isolation and habitat heterogeneity can interact because finite area constrains the effective amount of each habitat [@kadmon2007; @allouche2012]. Marine subsidies can further alter area and diversity relationships [@obrist2020]. Penguins add a different configuration: the island is essential for reproduction but most trophic acquisition occurs at sea.

This decoupling weakens the expectation that terrestrial area or heterogeneity should map directly onto demographic stability. Breeding-space amount can matter strongly at particular colonies without functioning as a general proxy for energetic carrying capacity. Habitat heterogeneity can create alternatives, barriers, snow traps or locally persistent nesting opportunities depending on scale and history. The weak transferability observed here is therefore compatible with the idea that terrestrial architecture acts as one component of population response rather than as a dominant, scale-invariant filter.

### The area × heterogeneity pattern remains suggestive, not established

All three primary 2 km interaction estimates were negative, and chinstrap and gentoo displayed the complete point-estimate crossover geometry. That concordance is ecologically interesting, but the preregistered paper-level permutation test did not cross the frozen rejection threshold. The appropriate conclusion is not that a hidden positive result was missed, nor that the effect is zero.

The retrospective operating-characteristic analysis helps place the non-rejection. A common interaction around the observed magnitude had poor detection probability under the actual observation layout and frozen test. Effects near 0.50–0.55 in magnitude, however, would usually have been detected. Thus the data constrain a **very large general effect** more strongly than a moderate one. The distinction is important: failure to confirm a general rule is not equivalent to demonstrating that island architecture is irrelevant.

### Radius variation is a robustness problem, not a new ecological finding

The raw interaction changed markedly between 1, 2 and 5 km, including a sign reversal between the primary 2 km scale and 5 km. It would be tempting to interpret this as biological scale dependence. The joint multi-radius null argues against doing so. When the complete 1/2/5 km trait tuple was permuted together within the frozen spatial blocks, a sign reversal plus an observed-size contrast occurred with probability 0.081. The variation therefore does not satisfy the prespecified criterion for a scale-dependent ecological discovery.

This diagnostic changes the wording of the manuscript. We retain the raw radius sensitivity because it is important evidence about transferability, but we do not treat the 5 km reversal as a mechanism. It reinforces a narrower point: conclusions based on coarse static breeding-landscape summaries are sensitive to analytical support and should not be treated as scale-free properties of islands.

### A dynamic local signal also failed a direct transfer test

The transferability limit was not confined to static island descriptors.
Palmer reproductive performance contained short-lived information about later
within-island redistribution, but the corresponding primary lag-2 test did not
replicate at Signy under a prospectively frozen comparable design. Directional
agreement in the Signy sensitivities is worth reporting, but it does not
override the null primary test.

This distinction matters because a locally informative state variable can be
ecologically real without being portable. The Palmer result may reflect local
retention, breeding participation, redistribution, immigration/emigration or
persistent habitat state, and colony counts cannot distinguish those
mechanisms. The independent Signy result therefore argues against treating the
Palmer association as a general performance-cued movement rule. In the language
of this manuscript, **dynamic local information can fail transfer just as
static island architecture can fail transfer**.

### A hierarchy of island information

The Palmer and Antarctic analyses can be understood as a hierarchy of information. Species identity, regional context, island identity and within-island organization all carry ecological information, but information at one level does not automatically transfer to another. At Palmer, the within-island distribution of breeders carries information that island totals alone miss. Across Antarctica, however, static island area and habitat-complex diversity do not provide a confirmed rule for how strongly populations track shared forcing.

This perspective links the present work to a broader methodological problem: **apparent island information can be real at one hierarchical level while failing as transferable information at another**. The practical implication is that island ecology should distinguish local explanatory structure from cross-island predictive structure rather than treating them as interchangeable.

### Implications and limitations

The strongest positive result is local: decline can involve systematic spatial concentration within breeding islands. The strongest broad-scale result is a limit: static breeding-island architecture did not yield a confirmed general response-filter rule across Pygoscelis populations.

Several limitations remain. The Antarctic-wide habitat metrics describe potential breeding landscapes around sites, not occupied nesting polygons. The final species-wide forcing factors are latent demographic summaries rather than identified environmental drivers. The primary cross-species interaction was only weakly detectable at the observed magnitude, so moderate general effects remain unresolved. The radius sensitivity further shows that habitat summaries depend on spatial support. Finally, the process-variance parameter repeatedly approached its frozen lower profile bound in recovery and real fits, so we do not interpret residual process variance ecologically.

These constraints also define the next experiments. Mapped occupied breeding footprints, local snow persistence, colony-density history and movement among subcolonies are more direct candidates for explaining local response differences than additional searches over coarse landscape radii.

## Conclusion

A shared decline can generate sharply different internal demographic trajectories among neighbouring islands. At Palmer, Adélie populations became progressively concentrated into fewer breeding components as they contracted, showing that island population decline has a spatial organization that total abundance alone misses. Yet the Antarctic-wide test did not confirm a simple static rule linking breeding-space amount and habitat heterogeneity to population coupling across three *Pygoscelis* species. The study had little sensitivity to moderate common interactions near the observed magnitude, but would usually have detected a very large shared effect; the apparent cross-radius reversal was also compatible with the multiradius permutation null.

The resulting conclusion is a boundary on generalization. The same boundary also appeared in the secondary dynamic analysis: a Palmer performance-linked redistribution signal did not independently replicate at Signy.

> **local demographic organization can be strong and repeatable without becoming transferable information in static island traits or local dynamic correlates at broader scales.**

For island ecology, the central question is therefore not simply whether islands matter, but **which level of island information can be carried across space, species and scale**.

## Data and code availability

All analyses are tracked in the `mina` reproducibility repository with frozen source commits, pre-outcome contracts, simulation-recovery receipts, primary and secondary permutation receipts, and manuscript claim boundaries. Public source datasets retain their original data-provider licences and citations. A submission-ready archival release will freeze the exact code and derived non-restricted outputs used for the manuscript.

## Acknowledgements

[Author-controlled text to be completed.]

## Author contributions

[Author-controlled text to be completed.]

## Conflict of interest statement

[Author-controlled text to be completed.]
