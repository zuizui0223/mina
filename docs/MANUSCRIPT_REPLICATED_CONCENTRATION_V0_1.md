# Breeding-space contraction accompanies Adélie penguin population decline across two Antarctic systems

**Manuscript v0.1 — replicated concentration paper**

## Abstract

Population decline is usually summarized as loss of abundance, but colonial breeders can also change how the remaining population is distributed among breeding components. Distinguishing simple proportional thinning from spatial reorganization matters because both trajectories can produce the same total population decline. We tested this distinction in long-term Adélie penguin (*Pygoscelis adeliae*) breeding records from two Antarctic monitoring systems. In the Palmer Archipelago, West Antarctic Peninsula, we analysed the complete 1991–2017 colony-level census and restricted the primary spatial test to Cormorant, Humble and Litchfield islands, whose reported colony-code rosters remained unchanged. Effective colony number, N_eff = 1/sum(p_j^2), declined by 19%, 51% and 83%, respectively. A fixed-composition null preserved each observed island-total trajectory while holding the relative distribution among colony units constant and adding Poisson or Gamma–Poisson counting error. The observed concentration trends remained more negative than expected under every frozen error model, including a 20% multiplicative-CV sensitivity. We then froze the same endpoint in an independent Signy Island, South Orkney Islands, data set before computing its N_eff trajectory. Across a fixed-roster 1998–2009 epoch, breeding pairs declined from 2,688 to 901 while N_eff declined from 3.61 to 2.54 (−29.7%; slope −0.111 yr−1); the slope remained unusual under Poisson (p = 0.000010), 10% CV (p = 0.000010) and 20% CV (p = 0.000130) nulls. Independent Torgersen Island mapping provides physical-scale triangulation by documenting loss of historical subcolony footprints during decline. These results provide replicated longitudinal evidence that Adélie decline can involve coarse-scale contraction of breeding-space organization rather than proportional loss alone. The census data do not identify the responsible behavioural or habitat mechanism, and coarse-scale loss of breeding components can coexist with finer-scale fragmentation within retained components.

**Keywords:** Adélie penguin; colonial breeding; population decline; spatial reorganization; subcolonies; long-term monitoring; breeding-space contraction; Antarctica

## Introduction

Population decline has a spatial form as well as a magnitude. Two populations can lose the same fraction of individuals while following very different spatial trajectories. If all local breeding components decline proportionally, relative occupancy is preserved and the population simply becomes thinner. Alternatively, some components can lose breeders faster than others, concentrating the remaining population into a smaller effective set of breeding locations. These trajectories are ecologically distinct even when conventional population totals are identical.

Colonial breeders make this distinction especially important because population processes emerge from nested spatial organization. Individuals occupy nests, nests form aggregations, aggregations occur within subcolonies or colony units, and multiple breeding components can coexist within a larger breeding site. Spatial geometry can influence reproductive performance through edge effects, predation exposure, snow accumulation, drainage and access to breeding habitat. In Adélie penguins, subcolony-scale habitat and configuration are associated with reproductive success [@schmidt2021], and theoretical work predicts that declining abundance can generate fine-scale fragmentation of nest aggregations through the interaction of site fidelity, self-organization and edge-biased predation [@mcdowall2019]. Long-term spatial reconstruction at Torgersen Island additionally shows that historical Adélie subcolonies have disappeared non-randomly with respect to landscape and snow conditions [@cimino2025].

These studies establish that spatial organization is biologically consequential, but they leave a separate longitudinal question unresolved: **as a breeding population declines, is breeding effort across established colony components lost approximately in proportion, or does the relative distribution itself reorganize?** This is not equivalent to asking whether small colonies disappear first. Under declining total abundance, small components can reach zero earlier even when their expected proportional share never changes. Demonstrating spatial reorganization therefore requires a null model that preserves the observed total-abundance trajectory while holding the latent composition fixed.

The Palmer Archipelago provides a strong discovery system for this question. Five neighbouring Adélie breeding islands experienced a highly coherent multi-decadal decline, while independent work documents strong local variation in snow, geomorphology and subcolony persistence [@cimino2019; @cimino2025]. In previous analysis of the Palmer LTER census, the three islands with unchanged colony-code rosters—Cormorant, Humble and Litchfield—showed progressive declines in effective colony number that were not reproduced by fixed-composition count-error nulls. That result established a repeatable within-Palmer pattern but left open whether it was a peculiarity of one regional monitoring system.

We therefore sought an external system in which the same biological endpoint could be tested without changing the statistic or null logic. Signy Island in the South Orkney Islands has a long-running ground-count program in predetermined Adélie breeding colonies. Earlier work established the long-term Signy population decline and disappearance of several monitored colonies [@dunn2016], but did not test whether changes in the relative distribution of breeding pairs exceeded those expected from proportional thinning. The underlying public colony-level data therefore permit a direct replication of the Palmer concentration question [@dunn2021signyadelie].

We ask one primary question: **does Adélie population decline repeatedly concentrate breeding effort among fewer effective breeding components?** We quantify the distribution of breeding pairs using effective colony number and test observed temporal trends against a fixed-composition null that preserves the empirical total-population trajectory. Palmer supplies three discovery populations; Signy supplies a separately frozen external endpoint. Independent mapped subcolony loss at Torgersen is retained as physical spatial triangulation. We deliberately do not use the resulting patterns to infer individual dispersal, public information, an Allee effect or a unique habitat mechanism.

## Materials and Methods

### Study systems

#### Palmer Archipelago

The Palmer analysis used the public Palmer Station Antarctica Long Term Ecological Research Adélie penguin breeding-pair census (DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e). The complete synchronized island panel covers 1991–2017 for Christine, Cormorant, Humble, Litchfield and Torgersen islands. Counts are reported at nominal island-specific colony codes.

Because changing the set of census units can create artificial changes in diversity or concentration, the primary within-island analysis required an unchanged reported colony-code roster through the analysis interval. Cormorant, Humble and Litchfield satisfied that gate. Litchfield contributed through its final positive island census; later zero-abundance years were not used to define an effective distribution.

#### Signy Island

The replication used the British Antarctic Survey/NERC Polar Data Centre data set *Population size and breeding success of Adelie penguins on Signy Island from 1978 to 2020* [@dunn2021signyadelie]. Signy monitoring consists of repeated ground counts in predetermined breeding colonies and has followed CCAMLR Ecosystem Monitoring Programme standards since the mid-1990s. The long-term decline of the Signy Adélie population and selected study colonies has previously been described [@dunn2016].

The concentration endpoint was frozen before any Signy effective-colony-number values or slope were computed. The initial contract specified 1998–2010, but execution stopped at the data-availability gate because no 2010 breeding-pair season is present in the public source. Before any endpoint or null distribution was calculated, the end year was repaired to 2009, producing the maximal contiguous available interval beginning in 1998 and ending before the structurally absent 2010 season and the addition of monitored colony A39 in 2011. No further window repair was permitted.

The resulting primary epoch contains 12 seasons (1998–2009) and eight literal published colony units: A1 + A60, A2, A3, A4, A41, A62, A63 and A64. The pooled A1 + A60 label was retained exactly as published and was not retrospectively split. A source-quality audit confirmed that the 2008 comment flag used in an earlier breeding-success analysis concerns the timing and reliability of chick/fledgling counts, not the breeding-pair endpoint used here.

### Effective colony number

For each site and year, let n_j be the number of breeding pairs in colony component j, N = sum_j n_j, and p_j = n_j/N. We measured the effective number of occupied breeding components as

N_eff = 1 / sum_j p_j^2.

This is the inverse Simpson concentration expressed in effective-number units. N_eff is high when breeding pairs are distributed relatively evenly among multiple components and declines when breeding effort becomes concentrated in a smaller subset. The statistic does not require that census units be equal in area and is not interpreted as a count of physical habitat patches.

For each eligible population, the observed concentration statistic was the ordinary least-squares slope of annual N_eff against calendar year. A negative slope indicates increasing concentration over time.

### Fixed-composition proportional-thinning null

The ecological null was proportional thinning of a time-invariant breeding distribution. For each population, we estimated one fixed vector of colony shares from cumulative breeding-pair counts across its complete eligible interval. In each year, the fixed shares were multiplied by that year's observed total number of breeding pairs. Thus, the null preserved the empirical magnitude and temporal trajectory of population decline while removing directional change in relative colony composition.

We then generated observed counts from three frozen error models: independent Poisson counts, Gamma–Poisson counts with 10% multiplicative coefficient of variation, and Gamma–Poisson counts with 20% multiplicative coefficient of variation. The latter is deliberately severe and is used as a sensitivity rather than an empirically calibrated observer-error estimate. For observed-positive years, simulated vectors with a zero total were redrawn.

For each population and error model, we generated 100,000 null realizations and recomputed the N_eff slope. The one-sided probability was calculated with a plus-one correction as (1 + number of null slopes at least as negative as observed) / 100001.

A population was considered to show concentration beyond proportional thinning if its observed slope was negative and p <= 0.05. The Palmer analysis additionally required the same criterion on all three stable-roster islands and evaluated the probability of slopes simultaneously at least as negative as observed on all three.

The Palmer and Signy implementations used the same biological statistic and fixed-composition logic. Count-error parameters, alternative concentration metrics, pair-count thresholds and tuned time windows were not searched after seeing the replication result.

### Independent physical spatial evidence

We used the published Torgersen Island reconstruction of Cimino et al. [@cimino2025] as an independent spatial evidence layer. That study combined historical records and modern spatial data to reconstruct persistence and extinction of mapped subcolony footprints. We use its reported loss of historic active subcolonies and habitat-structured persistence only to establish that real physical breeding-space attrition occurs in the Palmer system.

The public Palmer census colony codes have not been mapped one-to-one to those GIS polygons. Torgersen therefore provides phenomenon-level spatial triangulation rather than identifier-level validation of N_eff.

## Results

### Palmer decline was accompanied by progressive concentration on all three stable-roster islands

Effective colony number declined throughout the Palmer record on each island eligible for the fixed-roster analysis. Cormorant declined from 3.535 to 2.859, a 19.1% reduction, with a slope of −0.03098 yr−1. Humble declined from 4.625 to 2.285 (−50.6%; slope −0.08550 yr−1). Litchfield declined from 5.783 to 1.000 by its final positive census in 2006 (−82.7%; slope −0.36808 yr−1).

These trends exceeded the concentration expected from falling abundance alone. Under the most permissive frozen sensitivity, Gamma–Poisson error with 20% multiplicative CV, one-sided probabilities were p = 0.0380 for Cormorant and p = 0.000010 for both Humble and Litchfield. None of 100,000 simulated realizations generated slopes simultaneously as negative as the three observed slopes (plus-one joint p = 0.000010). Poisson and 10% CV models produced the same qualitative decision.

Thus the Palmer result is not explained by a fixed relative breeding distribution becoming noisier as total abundance falls. The relative distribution itself changed directionally toward a smaller effective set of census breeding components.

### The same concentration pattern independently replicated at Signy

The frozen Signy fixed-roster epoch contained 12 seasons and eight published breeding components. Total breeding pairs declined from 2,688 in 1998 to 901 in 2009. Over the same interval, N_eff declined from 3.610 to 2.539, a 29.7% reduction, with an observed slope of −0.11148 yr−1.

The fixed-composition null did not reproduce this trend. Under Poisson sampling, none of 100,000 simulated slopes was as negative as observed (plus-one p = 0.000010); the 95% null interval was approximately −0.0151 to 0.0150 yr−1. Under the 10% multiplicative-CV Gamma–Poisson sensitivity, none of 100,000 simulations reached the observed slope (p = 0.000010; 95% interval −0.0326 to 0.0326). Even under 20% multiplicative CV, only 12 of 100,000 simulations were at least as negative as observed (p = 0.000130; 95% interval −0.0585 to 0.0583).

The independent Signy endpoint therefore met the complete frozen replication rule. Its magnitude fell within the range of the Palmer responses: the 29.7% decline in effective colony number exceeded the Cormorant reduction but was smaller than those on Humble and Litchfield.

### Physical mapping at Torgersen shows that coarse breeding-space loss is real

Independent spatial reconstruction at Torgersen documented 23 historically active subcolony footprints and only five active footprints by 2022 [@cimino2025]. Persistence was associated with long-term landscape and snow conditions: all historical south-aspect subcolonies were extinct, while some north-aspect subcolonies remained.

The mapped study also reported that some retained historical footprints had fragmented internally into smaller active pieces. Thus physical evidence from Torgersen illustrates an important scale distinction: whole historical breeding components can disappear at a coarse scale even while the breeding aggregation remaining inside an occupied component becomes fragmented at a finer scale.

## Discussion

### Population decline repeatedly compressed the distribution of breeding effort

Across two geographically separated Antarctic monitoring systems, declining Adélie populations did more than lose breeders. The remaining breeding effort became increasingly concentrated among fewer effective colony components. Three Palmer islands showed the pattern independently within a common regional decline, and a separately frozen Signy endpoint replicated it under the same statistic and null logic.

The strongest result is not that small colonies disappeared or that colony counts fell. Both can occur mechanically as abundance decreases. Rather, the observed changes were substantially more directional than expected when each empirical total-abundance trajectory was imposed on a fixed relative breeding distribution. This comparison separates **loss of population size** from **change in population spatial organization**.

The Signy result changes the scope of the inference. Long-term declines and disappearance of monitored colonies at Signy were already known [@dunn2016]. What the replication adds is evidence that the redistribution of breeding effort among the surviving and disappearing components cannot be reduced to proportional thinning plus the frozen count-error family. The Palmer pattern is therefore not only a local feature of one census program.

### Coarse concentration and fine fragmentation are compatible

At first glance, concentration among fewer colony components may appear to conflict with theoretical work predicting fragmentation during Adélie population decline [@mcdowall2019]. The apparent contradiction disappears once spatial level is made explicit.

The present N_eff metric operates across established census colony or subcolony units. A decline in N_eff means that breeding effort is being lost disproportionately from some of those units, leaving a larger share of the population in a smaller effective subset. McDowall and Lynch [@mcdowall2019] address the arrangement of nests and aggregations at a finer spatial scale: as abundance falls, site fidelity and local interactions can leave the remaining nest distribution divided into fragments with high edge exposure.

Both processes can occur simultaneously. Torgersen provides an empirical example: many historical subcolony footprints have vanished, but some of the footprints that remain active contain smaller internal fragments [@cimino2025]. Decline can therefore simplify breeding-space occupancy at one level while fragmenting it at another. This hierarchical reorganization is a more useful interpretation than forcing all spatial change into a single aggregation-versus-fragmentation axis.

### Several mechanisms can generate the same spatial-demographic outcome

The replicated concentration pattern does not by itself identify why particular breeding components lose breeders faster than others. Long-term snow accumulation, wind redistribution, topography and drainage can make some breeding areas less persistent [@cimino2019; @cimino2025]. Subcolony geometry can alter edge exposure and reproductive success [@schmidt2021]. High nest-site fidelity and incomplete information can slow spatial adjustment after environmental change [@mcdowall2019]. Changes in breeding participation, survival, recruitment or movement could also change the distribution of active breeding pairs without direct transfer among adjacent components.

These mechanisms are not mutually exclusive, and the present census data cannot discriminate among them. In particular, a decline in a census component does not demonstrate that its former breeders moved into a component that increased in relative share. Public Palmer data also lack an individual mark–resight table linking identity to later breeding subcolony, so individual dispersal or public-information use should not be inferred from aggregate counts.

The contribution here is therefore at the level of population organization: regardless of the mixture of individual mechanisms, the decline repeatedly changes the spatial distribution in which reproduction occurs.

### Total abundance misses a second dimension of population contraction

Long-term seabird monitoring commonly emphasizes total breeding-pair abundance because totals provide the most direct measure of population trajectory and are often the only quantity available consistently across sites. Our results show why internal distribution can add distinct information.

A population with 1,000 breeding pairs spread relatively evenly across several established components is not spatially equivalent to a population with 1,000 pairs concentrated overwhelmingly in one or two. Those states differ in occupied breeding space, edge geometry, exposure to local conditions and the number of spatial components available to absorb local disturbance. We do not show that higher N_eff causes resilience, but we do show that N_eff can collapse during decline even after the effect of total abundance on count stochasticity is explicitly removed.

This distinction is relevant to remote sensing and colony monitoring. Colony-area or guano-footprint methods are increasingly important for Antarctic population assessment, but spatial rearrangement can change the relationship between abundance and occupied geometry. Monitoring programs that retain subcolony or component-level information therefore preserve an ecological dimension that aggregate counts alone cannot reconstruct.

### Limitations

Four population units support the primary inference: three neighbouring Palmer islands and one Signy Island monitoring series. The Palmer units share regional environmental forcing and are not independent Antarctic regions; Signy provides the critical external replication but remains a single additional system. Generalization beyond Adélie penguins therefore requires further replicated colony-level records.

The census units are also operational monitoring components rather than standardized equal-area habitat patches. Palmer colony codes lack a public one-to-one spatial crosswalk, and Signy includes the literal pooled unit A1 + A60. Effective colony number should consequently be interpreted as the effective number of monitored breeding components, not as a direct measurement of occupied land area.

Finally, the count-error models are stylized sensitivities rather than empirical observer-error distributions. Their strength is that the same frozen family was used to ask whether plausible abundance-dependent noise could manufacture the observed temporal trend. The Signy data are based on repeated standardized ground counts, but no analysis here estimates a true observation CV for every colony and year. The supported conclusion is therefore that the pattern exceeds proportional thinning under the specified error family, not that all measurement uncertainty has been eliminated.

### A testable next step

The next mechanistic test should use explicitly spatial colony polygons or individual movement data rather than another concentration index. At the polygon level, one can ask whether coarse loss of breeding components preferentially removes snow-prone, edge-dominated or topographically constrained habitat while retained components fragment internally. At the individual level, mark–resight data could separate mortality, nonbreeding, within-island relocation and between-site dispersal.

Those tests would explain how the replicated pattern is produced. They are not necessary to establish the present descriptive ecological result: decline repeatedly changes where breeding effort remains.

## Conclusion

Adélie penguin population decline has a reproducible spatial-demographic form. On Cormorant, Humble and Litchfield islands near Palmer Station, breeding pairs became progressively concentrated among a smaller effective set of colony-code components, beyond the concentration expected from the observed total-population decline and independent count error. A separately frozen analysis of Signy Island reproduced the same pattern: effective colony number fell by 29.7% during a 1998–2009 decline, and the observed slope remained extreme even under a 20% multiplicative-CV count-error sensitivity.

Together with independent mapped subcolony loss at Torgersen, these results show that declining Adélie populations can undergo **breeding-space contraction**, not merely proportional thinning. At finer scales, retained breeding components may simultaneously fragment, making the spatial response to decline hierarchical rather than one-dimensional. Population totals capture how many breeders remain; the distribution among breeding components captures an additional feature of decline—where reproduction is disappearing from first.

## Data availability

The Palmer LTER Adélie penguin census is publicly archived at DOI 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e. The Signy Adélie population and breeding-success data are publicly archived by the NERC EDS UK Polar Data Centre at DOI 10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d [@dunn2021signyadelie].

Analysis code, frozen endpoint contracts, provenance repairs, result receipts and manuscript source are maintained in the mina repository. The Signy concentration analysis is documented by contracts/SIGNY_CONCENTRATION_REPLICATION_V2.json, results/SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json and results/SIGNY_CONCENTRATION_QUALITY_AUDIT_V1.json.

## References

See docs/REFERENCES_V6.bib.
