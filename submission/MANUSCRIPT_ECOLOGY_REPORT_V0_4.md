# Breeding-space contraction recurs across declining Adélie and chinstrap penguins

**Ecology Report candidate v0.4**

## Abstract

Population decline can alter spatial organization as well as abundance. We tested whether declining colonial penguin populations thin proportionally across monitored breeding components or contract onto fewer effective components. In three Adélie penguin (*Pygoscelis adeliae*) populations near Palmer Station, effective breeding-component number declined by 19–83% more rapidly than expected when each observed abundance trajectory was imposed on a fixed composition with Poisson or Gamma–Poisson count error. We then froze the same endpoint before effect computation in independent Signy Island data. Signy Adélie declined from 3.08 to 1.94 effective components (−37%), and a separately frozen chinstrap penguin (*P. antarcticus*) test declined from 4.44 to 2.19 (−51%); both exceeded the most severe 20%-CV fixed-composition null (p ≤ 0.00002). Thus, across two Antarctic systems and two *Pygoscelis* species, population decline repeatedly compressed breeding effort into fewer effective monitored components. Abundance loss and breeding-space contraction therefore describe distinct dimensions of colonial population decline.

**Keywords:** abundance–occupancy; Adélie penguin; Antarctica; chinstrap penguin; colonial breeding; population decline; spatial contraction; subcolonies

## Introduction

Population decline has a spatial form as well as a magnitude. The same loss of individuals can produce little change in occupancy if decline is concentrated in densely populated parts of a distribution, or rapid spatial contraction if losses occur disproportionately elsewhere [@rodriguez2002]. Total abundance therefore does not uniquely determine how a population disappears from space.

Colonial breeders provide a nested, within-population version of this problem. Individuals are distributed among nests, aggregations, subcolonies and larger breeding sites. A declining colony could thin approximately in proportion across these components, preserving their relative representation, or breeding effort could become concentrated into a smaller effective subset. These alternatives imply different spatial states even when total abundance is identical.

Penguins offer a useful system in which to ask this question. Within breeding sites, local geometry and habitat are biologically important: Adélie reproductive performance varies with subcolony-scale habitat and configuration [@schmidt2021], mechanistic theory predicts that declining abundance can fragment nest aggregations [@mcdowall2019], and long-term mapping at Torgersen Island has documented loss of historical Adélie subcolonies associated with snow and terrain [@cimino2025].

Yet neither colony disappearance nor preferential loss of small groups demonstrates non-proportional spatial contraction. As total abundance falls, small components can reach zero sooner even if all components retain constant expected shares. The relevant null is therefore **proportional thinning**: the observed total-abundance trajectory occurs while the latent relative distribution among monitored breeding components remains fixed.

We first developed this test in long-term Adélie counts from the Palmer Archipelago. We then used Signy Island to ask two stronger questions with endpoints frozen before effect computation: does the pattern replicate in an independent Adélie system, and does it recur in declining chinstrap penguins? Our prediction was that decline would reduce effective breeding-component number more rapidly than proportional thinning plus frozen count-error models could generate.

## Methods

### Palmer discovery system

We used the Palmer Station Antarctica Long Term Ecological Research Adélie breeding-pair census (1991–2017; DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e). Official metadata define colony_code as an island-specific identifier for an ecosystem colony, and historical Palmer methods describe colony-level censuses following standardized CEMP procedures. To prevent obvious changes in census-unit rosters from manufacturing concentration trends, the primary analysis was restricted to Cormorant, Humble and Litchfield islands, whose published code sets were unchanged over their eligible intervals. Litchfield was analysed through its final positive census in 2006.

The public archive does not include a versioned spatial-boundary history for every Palmer colony code. We therefore interpret Palmer units as **monitored census colonies/components**, not as verified fixed GIS polygons, and treat Palmer as the discovery system rather than the confirmatory basis of the manuscript.

For each population-year, if n_j is the number of breeding pairs in component j and p_j is its share of the population total, we calculated the inverse-Simpson effective number of breeding components,

N_eff = 1 / Σ p_j².

N_eff is expressed in equally represented component units: it declines when a larger fraction of breeders is carried by fewer monitored components. It is not genetic effective population size and does not measure physical land area.

The observed statistic was the ordinary-least-squares slope of annual N_eff against year.

### Prospectively frozen Signy replications

For the independent-system replication we used the public Signy Adélie data set (DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d). Before any Signy concentration endpoint was calculated, an outcome-blind support audit froze five canonical breeding units (A1+A60, A2, A3, A4 and A64) in 22 numerically complete seasons from 1996–2019; incomplete 1997 and 2010 seasons were excluded. The source changed from separate A1/A60 reporting to a pooled label, so A1, A60 and pooled forms were harmonized into A1+A60 under a rule frozen before effect inspection.

The cross-species test used the corresponding Signy chinstrap data set (DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9). A separate outcome-blind audit froze nine literal breeding units (C15, C16, C17, C18, C46, C47, C79, C80 and C81) in the same 22 complete seasons. A predeclared eligibility gate required the summed abundance of these units to decline through time before the concentration prediction could be interpreted.

### Proportional-thinning null

For each population, we estimated a single time-invariant vector of component shares from cumulative counts across its frozen panel. Those fixed shares were multiplied by each year's observed population total. The null therefore retained the empirical abundance trajectory while eliminating directional redistribution among components.

We generated counts under three frozen error families: independent Poisson sampling, Gamma–Poisson sampling with 10% multiplicative CV and Gamma–Poisson sampling with 20% multiplicative CV. The 20% model is a deliberately severe sensitivity, not an estimate of true observer error. We simulated 100,000 fixed-composition trajectories per error model and recalculated the N_eff slope.

A population supported breeding-space contraction when its observed slope was negative and the one-sided plus-one Monte Carlo probability of a null slope at least as negative was ≤0.05 under all three error models. No alternative concentration metric, threshold, time window or error CV could rescue a failed test.

### Secondary spatial interpretation

Published Torgersen spatial reconstruction [@cimino2025] was used only as physical triangulation. Palmer colony codes have not been crosswalked one-to-one to those mapped polygons, so this evidence supports the occurrence of real breeding-space loss near Palmer but does not validate individual census-code boundaries.

After all primary outcomes were known, we also described trajectories of initially and finally dominant census units. Because longitudinal boundary histories are not publicly documented for every Palmer code, these identity-level summaries are retained only as supplementary **nominal census-unit trajectories** and carry no inferential weight.

### Computational assistance and reproducibility

OpenAI ChatGPT (GPT-5.6 Sol) assisted with code drafting and review, literature searching, statistical sensitivity-analysis scripting and editorial drafting. All analyses were executed from version-controlled code; numerical outputs were checked against frozen result receipts and public source-data checksums; cited literature was independently verified; and the authors remain responsible for all analyses, interpretations and text.

## Results

### Palmer discovery: concentration exceeded proportional thinning

Effective breeding-component number declined on all three eligible Palmer islands. Cormorant fell from 3.54 to 2.86 (−19%; slope −0.031 yr⁻¹), Humble from 4.62 to 2.28 (−51%; −0.086 yr⁻¹), and Litchfield from 5.78 to 1.00 by its final positive census (−83%; −0.368 yr⁻¹).

All three trends remained more negative than expected under the frozen error family. Under the most severe Gamma–Poisson CV20% model, p = 0.038 for Cormorant and p = 0.000010 for Humble and Litchfield; no one of 100,000 simulated realizations produced slopes simultaneously as negative as all three observed populations (joint plus-one p = 0.000010).

### Signy prospectively replicated the endpoint across region and species

In the frozen Signy Adélie panel, breeding pairs declined from 2,342 to 1,217. N_eff declined from 3.08 to 1.94 (−37%; slope −0.044 yr⁻¹). None of 100,000 CV20% null trajectories was as negative (plus-one p = 0.000010). A later strict-literal-roster robustness analysis using a different frozen panel also supported concentration, showing that the conclusion did not depend on the canonical A1+A60 construction.

The separately frozen chinstrap panel passed its decline gate: breeding pairs fell from 1,642 to 581 (−65%). Effective breeding-component number fell from 4.44 to 2.19 (−51%; slope −0.072 yr⁻¹). Under CV20%, only one of 100,000 null slopes was as negative, giving p = 0.000020; Poisson and CV10% probabilities were p = 0.000010.

Thus the same population-level endpoint occurred in five declining population units across two Antarctic systems and two *Pygoscelis* species, with the two Signy tests providing the prospectively frozen replications.

## Discussion

Across five declining penguin populations, abundance loss was accompanied by a second change: reproduction became concentrated into fewer effective monitored breeding components. The Palmer pattern was first detected in an exploratory discovery system, but the same endpoint subsequently replicated under frozen analysis contracts in an independent Adélie data set and then in chinstrap penguins.

The result extends a general point from range-contraction ecology to the internal organization of colonial populations. Equal losses of abundance need not produce equal spatial changes because decline can be concentrated in different parts of a distribution [@rodriguez2002]. Here the spatial units are breeding components within populations rather than geographic range cells. The empirical implication is the same: **population totals do not determine the spatial trajectory of decline**.

This interpretation does not require every monitoring unit to be a permanent physical polygon. At Palmer, historical work mapped discrete breeding colonies and the public metadata identify colony-specific codes, but we found no public versioned boundary crosswalk covering the complete 1991–2017 series. We therefore avoid treating post-hoc changes in Palmer code dominance as proof that fixed physical subcolonies exchanged demographic importance. That uncertainty is one reason the prospectively frozen Signy replications carry the confirmatory weight of the paper.

Independent Torgersen mapping nevertheless shows that real coarse-scale breeding-space loss occurs in the Palmer system. Of 23 historical active subcolony footprints, only five were active by 2022, and persistence was structured by snow and terrain [@cimino2025]. Some retained historical footprints also fragmented internally. These observations resolve an apparent tension with models predicting fragmentation during Adélie decline [@mcdowall2019]: a population can lose whole breeding components at a coarse scale while fragmenting within the components that remain.

Our inference stops at the population-level outcome. Aggregate counts cannot determine whether contraction arose through mortality, nonbreeding, recruitment, within-site movement or habitat-specific demographic performance. A separate Palmer analysis linked relative reproductive performance to later redistribution, but its frozen Signy replication was unsupported; we therefore do not use public information or breeding dispersal as a general explanation.

The study also has clear limits. Three Palmer populations share one regional environment, and the two Signy species share one island. Monitoring components are operational census units rather than standardized equal-area habitat patches, and the error distributions are sensitivity models rather than empirically calibrated observer-error estimates. Generalization should therefore be to a **candidate spatial form of colonial population decline**, not to all penguins.

Even with those boundaries, the ecological message is simple. A population with the same number of breeders can occupy its breeding system very differently depending on how those breeders are distributed among monitored components. Component-resolved monitoring preserves this second dimension of decline; aggregate totals cannot reconstruct it after the fact. Future work can combine versioned breeding polygons and individual histories to ask which ecological processes determine the route to contraction.

## Data availability

Palmer LTER Adélie census: DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e.

Signy Adélie: DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d.

Signy chinstrap: DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9.

Frozen endpoint contracts, outcome-blind support audits, result receipts and reproducible figure/data scripts are maintained in the public mina repository.

## References

See docs/REFERENCES_V6.bib.
