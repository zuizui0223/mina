# Breeding-space contraction recurs across declining Adélie and chinstrap penguins

**Ecology Report candidate v0.3**

## Abstract

Population decline can alter spatial organization as well as abundance. We tested whether declining colonial penguin populations thin proportionally across breeding components or contract onto fewer effective components. In three Adélie penguin (*Pygoscelis adeliae*) populations near Palmer Station, effective breeding-component number declined by 19–83% and more rapidly than expected when each observed abundance trajectory was imposed on a fixed breeding composition with Poisson or Gamma–Poisson count error. We then froze the same endpoint in independent Signy Island data before computing the effects. Signy Adélie declined from 3.08 to 1.94 effective components (−37%); a separately frozen chinstrap penguin (*P. antarcticus*) test declined from 4.44 to 2.19 (−51%). Both exceeded the most severe 20%-CV fixed-composition null (p ≤ 0.00002). Post-hoc description showed different internal routes: initially dominant components disappeared in all three Palmer populations, whereas the initially dominant component increased its share in both Signy species. Thus abundance decline repeatedly compressed breeding effort into fewer effective components, but not through a universal large-colony refuge. Population totals and spatial contraction therefore describe distinct dimensions of decline.

**Keywords:** abundance–occupancy; Antarctica; colonial breeding; population decline; spatial contraction; Adélie penguin; chinstrap penguin; subcolonies

## Introduction

Population decline has a spatial form as well as a magnitude. The same loss of individuals can produce little change in occupancy if decline is concentrated in densely populated parts of a distribution, or rapid spatial contraction if losses occur disproportionately elsewhere [@rodriguez2002]. Total abundance therefore does not uniquely determine how a population disappears from space.

Colonial breeders provide a nested, within-population version of this problem. Individuals are distributed among nests, aggregations, subcolonies and larger breeding sites. A declining colony could thin approximately in proportion across these components, preserving their relative representation, or breeding effort could become concentrated into a smaller effective subset. These alternatives imply different spatial states even when total abundance is identical.

Penguins offer an unusually clear system in which to ask this question. Breeding occurs in discrete terrestrial components while foraging resources are acquired at sea. Within breeding sites, local geometry and habitat are biologically important: Adélie reproductive performance varies with subcolony-scale habitat and configuration [@schmidt2021], and mechanistic theory predicts that declining abundance can fragment nest aggregations through site fidelity, self-organization and edge-biased predation [@mcdowall2019]. Long-term mapping at Torgersen Island has independently documented loss of historical Adélie subcolonies associated with snow and terrain [@cimino2025].

Yet neither colony disappearance nor preferential loss of small groups demonstrates non-proportional spatial contraction. As total abundance falls, small components can reach zero sooner even if all components retain constant expected shares. The relevant null is therefore not “no colonies disappear,” but **proportional thinning**: the observed total-abundance trajectory occurs while the latent relative breeding distribution remains fixed.

We first developed this test in long-term Adélie counts from the Palmer Archipelago. We then used Signy Island to ask two stronger questions with endpoints frozen before effect computation: does the pattern replicate in an independent Adélie system, and does it recur in declining chinstrap penguins? Finally, after all primary outcomes were known, we described whether concentration reflected persistence of initially dominant breeding components or turnover in which component dominated. Our central prediction was that decline would reduce effective breeding-component number more rapidly than proportional thinning plus frozen count-error models could generate.

## Methods

### Palmer discovery system

We used the Palmer Station Antarctica Long Term Ecological Research Adélie breeding-pair census (1991–2017; DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e). Counts are reported for nominal colony-code components within breeding islands. To prevent changes in census-unit identity from manufacturing concentration trends, the primary analysis required an unchanged reported roster. Cormorant, Humble and Litchfield islands met this criterion. Litchfield was analysed through its final positive census in 2006.

For each population-year, if n_j is the number of breeding pairs in component j and p_j is its share of the population total, we calculated the inverse-Simpson effective number of breeding components,

N_eff = 1 / Σ p_j².

N_eff is expressed in “equally represented component” units: it declines when a larger fraction of breeders is carried by fewer census components. It is not genetic effective population size and does not measure physical land area.

The observed statistic was the ordinary-least-squares slope of annual N_eff against year.

### Prospective Signy replications

For the independent-system replication we used the public Signy Adélie data set (DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d). Before any Signy concentration endpoint was calculated, an outcome-blind support audit froze five canonical breeding units (A1+A60, A2, A3, A4 and A64) in 22 numerically complete seasons from 1996–2019; incomplete 1997 and 2010 seasons were excluded. The source changed from separate A1/A60 reporting to a pooled label, so A1, A60 and pooled forms were harmonized into A1+A60 under a rule frozen before effect inspection.

The cross-species test used the corresponding Signy chinstrap data set (DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9). A separate outcome-blind audit froze nine literal breeding units (C15, C16, C17, C18, C46, C47, C79, C80 and C81) in the same 22 complete seasons. A predeclared eligibility gate required the summed abundance of these units to decline through time before the concentration prediction could be interpreted.

### Proportional-thinning null

For each population, we estimated a single time-invariant vector of component shares from cumulative counts across its frozen panel. Those fixed shares were multiplied by each year's observed population total. The null therefore preserved the empirical abundance trajectory while eliminating directional redistribution among breeding components.

We generated observed counts under three frozen error families: independent Poisson sampling, Gamma–Poisson sampling with 10% multiplicative CV and Gamma–Poisson sampling with 20% multiplicative CV. The 20% model is a deliberately severe sensitivity, not an estimate of true observer error. We simulated 100,000 fixed-composition trajectories per error model and recalculated the N_eff slope.

A population supported breeding-space contraction when its observed slope was negative and the one-sided plus-one Monte Carlo probability of a null slope at least as negative was ≤0.05 under all three error models. Palmer additionally required all three stable-roster islands to pass individually; we also calculated the probability that all three null slopes were simultaneously as negative as observed. No alternative concentration metric, threshold, time window or error CV could rescue a failed test.

### Post-hoc pathway description and physical triangulation

After the five primary concentration outcomes were known, we froze a descriptive decomposition with no p-values. For each population we recorded the initially dominant component, its first- and final-season shares, the final dominant component and its initial rank. We also calculated, within each population, the descriptive Spearman correlation between initial share and the temporal slope of log1p component abundance. These summaries cannot alter the primary inference.

We used published Torgersen spatial reconstruction [@cimino2025] only as physical triangulation. Palmer colony codes have not been crosswalked one-to-one to those mapped polygons, so the external mapping is not treated as validation of individual census-unit identities.

### Computational assistance and reproducibility

OpenAI ChatGPT (GPT-5.6 Sol) assisted with code drafting and review, literature searching, statistical sensitivity-analysis scripting and editorial drafting. All analyses were executed from version-controlled code; numerical outputs were checked against frozen result receipts and public source-data checksums; cited literature was independently verified; and the authors remain responsible for all analyses, interpretations and text.

## Results

### Three Palmer populations contracted beyond proportional thinning

Effective breeding-component number declined on all three eligible Palmer islands. Cormorant fell from 3.54 to 2.86 (−19%; slope −0.031 yr⁻¹), Humble from 4.62 to 2.28 (−51%; −0.086 yr⁻¹), and Litchfield from 5.78 to 1.00 by its final positive census (−83%; −0.368 yr⁻¹).

All three trends remained more negative than expected under the complete frozen error family. Under the most severe Gamma–Poisson CV20% model, p = 0.038 for Cormorant and p = 0.000010 for Humble and Litchfield; no one of 100,000 simulated realizations produced slopes simultaneously as negative as all three observed populations (joint plus-one p = 0.000010).

### Signy replicated the endpoint across region and species

In the prospectively frozen Signy Adélie panel, breeding pairs declined from 2,342 to 1,217. N_eff declined from 3.08 to 1.94 (−37%; slope −0.044 yr⁻¹). None of 100,000 CV20% null trajectories was as negative (plus-one p = 0.000010). A later strict-literal-roster analysis using a different frozen panel also supported concentration, showing that the result did not depend on the canonical A1+A60 construction.

The separately frozen chinstrap panel passed its decline gate: breeding pairs fell from 1,642 to 581 (−65%). Effective breeding-component number fell from 4.44 to 2.19 (−51%; slope −0.072 yr⁻¹). Under CV20%, only one of 100,000 null slopes was as negative, giving p = 0.000020; Poisson and CV10% probabilities were p = 0.000010.

Thus the same population-level endpoint occurred in five declining population units, across two Antarctic systems and two *Pygoscelis* species.

### Convergent contraction followed different internal routes

The descriptive decomposition did not support a universal “large colonies persist” narrative.

At Palmer, the initially dominant component had zero breeding pairs by the final eligible census in all three populations. Cormorant's initial dominant fell from 45% of pairs to zero, while an initially fourth-ranked component became dominant. Humble's initial dominant fell from 34% to zero and an initially second-ranked component ended at 59%. At Litchfield, the initial dominant fell from 26% to zero while the initially second-ranked component contained all four pairs in the final positive census. Descriptive initial-share versus component-slope correlations were negative in all three populations (rho = −0.64, −0.30 and −0.62).

Signy showed the opposite route. The Adélie A1+A60 component remained dominant and increased from 47% to 69% of breeders (rho = +0.90). Chinstrap C80 remained dominant and increased from 40% to 66% (rho = +0.38). The replicated population-level contraction therefore arose through dominance turnover at Palmer but dominant-core retention at Signy.

## Discussion

Across five declining penguin populations, abundance loss was accompanied by a second change: reproduction became concentrated into fewer effective breeding components. This pattern was stronger than expected when each observed abundance trajectory was imposed on a fixed latent breeding distribution, and it survived the same deliberately severe count-error sensitivity in every population. More importantly, the Palmer discovery transferred prospectively to a second Adélie monitoring system and then to a second penguin species.

The result extends a general point from range-contraction ecology to the internal organization of colonial populations. Equal losses of abundance need not produce equal spatial changes because decline can be concentrated in different parts of a distribution [@rodriguez2002]. Here the spatial units are not geographic range cells but breeding components within populations. The empirical implication is the same: **population totals do not determine the spatial trajectory of decline**.

The post-hoc decomposition sharpens this conclusion by ruling out an overly simple mechanism. At Signy, contraction resembled retention of an established core: the initially dominant component remained dominant in both species and carried an increasing fraction of the remnant population. At Palmer, concentration occurred despite loss of the initially dominant component in every population. Which component persisted was therefore contingent even though the population-level contraction endpoint recurred.

Independent Torgersen mapping is consistent with this contingency. Of 23 historical active subcolony footprints, only five were active by 2022, and persistence was structured by snow and terrain [@cimino2025]. Larger historical subcolonies generally disappeared later, but size did not guarantee persistence; habitat orientation modified decline. Some retained historical footprints also fragmented internally. These observations resolve an apparent tension with models predicting fragmentation during Adélie decline [@mcdowall2019]: a population can lose whole breeding components at a coarse scale while fragmenting within the components that remain.

Our inference stops at that population-level outcome. Aggregate counts cannot determine whether contraction arose through mortality, nonbreeding, recruitment, within-site movement or habitat-specific demographic performance. A separate Palmer analysis linked relative reproductive performance to later redistribution, but its frozen Signy replication was unsupported; we therefore do not use public information or breeding dispersal as a general explanation. Direct mechanism tests require spatially explicit habitat polygons or individual mark–resight histories.

The study also has clear limits. Three Palmer populations share one regional environment, and the two Signy species share one island. Monitoring components are operational census units, not equal-area habitat patches, and the error distributions are sensitivity models rather than empirically calibrated observer-error estimates. Generalization should therefore be to a **candidate spatial form of colonial population decline**, not to all penguins.

Even with those boundaries, the practical ecological message is simple. A population with the same number of breeders can occupy its breeding system very differently depending on how those breeders are distributed among components. Component-resolved monitoring preserves this second dimension of decline; aggregate totals cannot reconstruct it after the fact. Future work can ask when contraction proceeds through core retention, when it proceeds through dominance turnover, and whether those routes predict subsequent persistence.

## Data availability

Palmer LTER Adélie census: DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e.

Signy Adélie: DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d.

Signy chinstrap: DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9.

Frozen endpoint contracts, outcome-blind support audits, result receipts and reproducible figure/data scripts are maintained in the public mina repository.

## References

See `docs/REFERENCES_V6.bib`.
