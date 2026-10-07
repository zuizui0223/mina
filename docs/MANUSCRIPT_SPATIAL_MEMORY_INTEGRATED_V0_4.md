# Population change can suppress, erode or redirect breeding-space organization

**Integrated manuscript draft v0.4**  
**Date:** 2026-10-07  
**Status:** synthesis of already-opened endpoints; no new effect search.  
**Classification contract:** `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`  
**Claim ledger:** `results/SPATIAL_MEMORY_CLAIM_EVIDENCE_LEDGER_V1.json`

## Abstract

Breeding censuses record where reproduction is expressed, not all living adults or their latent site affiliations. A decline can therefore arise from temporary nonbreeding, demographic loss, or changing breeding capacity—processes that need not leave the same spatial trace. We synthesized already-opened penguin datasets using process classes assigned from natural-history evidence rather than spatial outcomes. A documented mega-iceberg disturbance on Ross Island reduced Adélie penguin breeding abundance by 54.3%, yet the next census restored 97.0% of the aggregate loss and closely retraced its six-component spatial footprint (cosine 0.997; inverse-path mismatch 9.41%). In contrast, persistent Adélie declines at Palmer and Signy concentrated breeders among fewer effective breeding components beyond proportional-thinning nulls. At Beaufort Island, increased nesting capacity coincided with disproportionate growth of a small/new breeding unit and reduced movement toward nearby Ross Island colonies. Independent Gentoo, King, and emperor-penguin cases further showed that aggregate direction did not determine spatial direction. These heterogeneous cases are not a common-effect test. They show that severe census loss can coexist with recoverable spatial organization, whereas attrition and capacity change can alter the demographic pool or breeding landscape from which future spatial structure is expressed.

**Keywords:** Adélie penguin; breeding-site fidelity; colonial breeding; demographic attrition; island ecology; metapopulation; population recovery; spatial reorganization

## Introduction

Population change is usually summarized by a scalar: abundance rose, declined, or recovered. For colonial breeders, that scalar compresses two different things. A breeding census records how many individuals are expressing reproduction at each colony or nesting unit, whereas the population also contains living adults, prior site affiliations, and breeding opportunities that may not be visible in that year's census. Two populations with the same total breeding abundance can therefore occupy very different spatial states, and a dramatic census decline need not imply equivalent destruction of the spatial organization that could be expressed later.

None of the component ideas is new. Ecological-memory theory emphasizes biological legacies that survive disturbance [@johnstone2016], spatial-recovery theory shows that dispersal, local dynamics, network structure, and disturbance geometry alter recovery [@zelnik2019; @wilson2023], and capture–recapture models explicitly separate mortality from breeding propensity or temporary emigration [@souchay2014]. Community and metapopulation studies also show that aggregate or functional recovery can mask persistent compositional or patch-level loss [@hillebrand2020; @wilson2023]. Site-faithful animals can return rapidly after extreme disturbance [@kreling2021], while colonial birds alter breeding fidelity and dispersal as colony conditions change [@brown2017; @spendelow2016]. These literatures emphasize a familiar warning: recovered totals need not imply recovered structure. We ask the converse population-level question: **can a severe breeding-census collapse conceal a multi-site spatial organization that remains recoverable?**

The distinction matters because the same observed decline can arise through different biological routes. A temporary breeding-state or access shock can reduce breeding expression while leaving many adults and their prior site affiliations intact. Persistent demographic attrition can instead change the relative contribution of breeding units through unequal survival, recruitment, movement, reproductive output, or local extinction. A change in breeding capacity modifies the set of places that can receive breeders. These alternatives predict different spatial consequences even when total abundance changes in the same direction.

We use a deliberately schematic decomposition to keep those routes separate. Let \(S_{i,t}\) represent the latent pool of living individuals for whom breeding unit \(i\) remains a plausible established destination, \(q_{i,t}\) the expression of breeding at that unit, and \(K_{i,t}\) available breeding capacity. Observed breeding abundance \(n_{i,t}\) can then be thought of as constrained by both \(S_{i,t}q_{i,t}\) and \(K_{i,t}\). We do not estimate these latent quantities. The decomposition is only a bookkeeping device for asking whether change acts mainly on breeding expression, on the site-affiliated demographic pool, or on the breeding landscape itself.

Islands make this distinction particularly visible. Colonial seabirds obtain most trophic resources at sea but must express reproduction on discrete terrestrial patches. Their breeding islands are therefore dynamic boundary conditions on a spatial population: local snow, terrain, sea-ice access, and nesting capacity filter shared regional forcing, while island boundaries constrain whether redistribution is expressed within a colony, elsewhere on the same island, or between islands [@fraser2013; @cimino2019; @schmidt2021].

Adélie penguins provide three process-anchored contrasts. On Ross Island, giant icebergs altered sea-ice and colony access and caused widespread breeding disruption around the 2001 census trough [@lyver2014; @dugger2014]. Long-term mark–recapture work independently shows that established breeders move among Ross Island colonies very rarely, while breeder-to-nonbreeder transitions are common [@dugger2026]. Palmer and Signy provide persistent-decline systems in which we can ask whether spatial composition was merely thinned or changed disproportionately [@cimino2025; @dunn2016]. Beaufort Island provides a capacity-change case in which usable nesting habitat expanded and movement toward nearby Ross Island colonies changed as local habitat became available [@larue2013].

We therefore test a hierarchy of claims using a common proportional-counterfactual logic. Existing theory already establishes that aggregate recovery can coexist with structural non-recovery; we use the boundary cases only to confirm that simple abundance-direction rules fail here as well. The focal empirical question is the converse: whether a severe observed breeding collapse can be followed by recovery of nearly the same multi-node allocation. We then contrast that temporary-disturbance case with persistent attrition and capacity change by asking, in each system, whether local change follows the spatially neutral proportional expectation. The cases are not exchangeable replicates of one effect size, and the process classes were formalized after their spatial outcomes were known. Our goal is therefore not to claim a universal three-process law, but to establish a narrower distinction: **loss of an observed breeding distribution and loss of the spatial organization that can later be re-expressed are not necessarily the same biological event.**

## Materials and Methods

### Evidence design and process classification

All spatial endpoints used here had already been opened in the mina research program before the present synthesis. The purpose of this manuscript is therefore integration, not preregistration of a new cross-system effect.

To reduce outcome-driven narrative assignment, we defined process classes using source-side ecological evidence and prohibited use of the spatial response itself during classification. The complete rules are frozen in `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`.

We distinguished three primary classes.

**Temporary breeding-state or access shock.** Assignment required an independently documented acute disturbance, a breeding-pair or occupied-nest response rather than total adult abundance, evidence that failed, abandoned, skipped, or access-limited breeding contributed to the event, and persistence of the pre-existing breeding geography sufficient to make return biologically plausible.

**Persistent demographic attrition.** Assignment required multi-year population decline plus independent evidence of durable demographic change such as persistent colony loss, mortality or recruitment limitation, emigration, or long-term local extinction. Long duration by itself was not sufficient.

**Breeding-capacity change.** Assignment required independent evidence that usable nesting habitat or breeding capacity changed and that this change plausibly altered settlement opportunities or movement.

Cases lacking sufficient source-side evidence for one of these classes were retained only as boundary cases. We did not use effective breeding-unit number, dominance, inverse-path mismatch, or any other spatial outcome to assign process class.

### Common proportional counterfactual

The process-specific analyses use different response metrics but share one counterfactual principle: **what spatial pattern would be expected if the observed aggregate change occurred without additional reallocation among breeding units?**

For a single transition from state 0 to state 1, the fixed-composition expectation is

\[
n_{i,1}^{*}=G\,n_{i,0},
\qquad
G=\frac{N_1}{N_0}.
\]

Under this null, every breeding unit changes by the same multiplicative factor and relative composition is preserved:

\[
p_{i,1}^{*}=p_{i,0}.
\]

This is the proportional-thinning null for decline and the proportional-growth null for expansion. Palmer and Signy implement this idea with their frozen trajectory/count-error procedures; the Beaufort endpoint comparison uses the same fixed-starting-composition logic.

A rebound after an identified preceding loss requires a path-specific version of the same principle. Let

\[
L_i=n_{i,0}-n_{i,1}
\]

be the prior local loss and \(R=\sum_i(n_{i,2}-n_{i,1})\) the observed aggregate rebound. Exact proportional reversal allocates the rebound according to the spatial footprint of loss,

\[
R_i^{*}=R\frac{L_i}{\sum_j L_j}.
\]

Equivalently,

\[
n_{i,2}^{*}=n_{i,1}+r(n_{i,0}-n_{i,1}),
\qquad
r=\frac{R}{\sum_j L_j}.
\]

When \(r=1\), the counterfactual returns exactly to the pre-disturbance vector. When \(0<r<1\), it lies on the straight path between trough and baseline.

These proportional counterfactuals are not claimed as novel mathematics. Their role is to provide a common biological baseline: aggregate change alone, without extra spatial reallocation. The system-specific analyses then ask how observed change departs from that baseline.

### Expressed breeding abundance and latent spatial organization

We use a conceptual decomposition to clarify what breeding censuses can and cannot observe. It is not fitted as a latent-state model.

Let \(S_{i,t}\) denote the latent pool of living individuals for whom breeding unit \(i\) remains a plausible established destination at time \(t\), \(q_{i,t}\) the fraction of that pool expressed in the breeding census, and \(K_{i,t}\) available breeding capacity. We use only the schematic constraints

\[
n_{i,t} \propto S_{i,t}q_{i,t},
\qquad
n_{i,t} \le K_{i,t}.
\]

The decomposition separates three routes to an observed change in breeding abundance.

- A **breeding-state/access shock** acts primarily on \(q_{i,t}\): breeders temporarily fail, skip, abandon, or cannot access nesting space while much of the site-affiliated demographic pool and breeding geography remain.
- **Persistent demographic attrition** changes \(S_{i,t}\) through unequal survival, recruitment, movement, reproductive contribution, or local extinction.
- **Capacity change** alters \(K_{i,t}\), changing which parts of the breeding landscape can receive expressed abundance and potentially changing movement among units.

The available colony counts do not separately estimate \(S\), \(q\), and \(K\). Their purpose here is interpretive: identical changes in observed \(n_i\) can imply different prospects for later spatial recovery depending on which underlying component changed.

### Spatial state

For a census containing local breeding units \(i=1,\ldots,k\), with breeding abundance \(n_i\), total abundance was

\[
N=\sum_i n_i.
\]

Relative representation was

\[
p_i=\frac{n_i}{N}.
\]

We summarized spatial redundancy with the effective number of breeding units,

\[
E=\frac{1}{\sum_i p_i^2}.
\]

This is the inverse Simpson concentration of breeding abundance: \(E\) is high when abundance is distributed more evenly among units and low when a small subset dominates. Because the biological identity and spatial scale of census units differ among datasets, \(E\) is interpreted within each system rather than compared as an absolute cross-system diversity value.

### Ross Island acute disturbance

The Ross analysis used the frozen six-component aerial census series for Cape Royds, Cape Bird South, Middle, and North, and Cape Crozier West and East. The source census estimates breeding pairs or occupied nesting territories near incubation, not total living adults [@lyver2014].

The focal natural experiment was defined post-result using independent natural-history evidence for the mega-iceberg disturbance:

\[
1999 \rightarrow 2001 \rightarrow 2002.
\]

For each component we calculated shock loss,

\[
L_i=n_{i,1999}-n_{i,2001},
\]

and rebound gain,

\[
R_i=n_{i,2002}-n_{i,2001}.
\]

Aggregate restoration was

\[
A=\frac{\sum_i R_i}{\sum_i L_i}.
\]

Directional alignment of spatial loss and rebound was quantified with cosine similarity,

\[
C=\frac{L\cdot R}{\lVert L\rVert\,\lVert R\rVert}.
\]

To measure departure from an exact inverse path while holding the observed rebound total fixed, expected rebound was allocated in proportion to shock loss:

\[
R_i^{*}=
\left(\sum_j R_j\right)
\frac{L_i}{\sum_j L_j}.
\]

The half-\(L_1\) mismatch was

\[
M=\frac{1}{2}\sum_i |R_i-R_i^{*}|,
\]

reported as a fraction of total rebound. These are descriptive effect sizes because validated component-specific count errors are unavailable for the focal years.

### Persistent attrition at Palmer and Signy

The Palmer analysis used annual breeding-pair censuses from five Adélie breeding islands near Palmer Station for 1991–2017. The concentration test was restricted to Cormorant, Humble, and Litchfield, whose reported colony-code rosters remained unchanged through the analysis period. For each island, the observed slope of effective colony number through time was compared with a fixed-composition proportional-thinning null that retained the observed island-total trajectory. Independent Poisson and Gamma-Poisson count-error families were applied exactly as frozen in the original analysis.

The independent Signy replication used the 1998 and 2009 Adélie censuses for eight stable named breeding units. The same conceptual null was used: if total decline simply scaled a fixed within-island allocation, the observed fall in (E) should be reproducible by proportional thinning plus the predeclared count-error family.

The present manuscript does not pool Palmer and Signy p-values or treat their census units as physically equivalent. Their common role is narrower: each asks whether persistent decline preserved a fixed relative allocation of breeding abundance.

### Beaufort Island capacity release

The Beaufort synthesis combined two independent evidence streams.

First, LaRue et al. documented long-term change in available nesting habitat, breeding population size, and movement of banded Beaufort-born birds toward Ross Island colonies [@larue2013].

Second, the public Ross Sea aerial census contains an established Beaufort breeding unit and a disjunct unit first reported as Beaufort Island New. For 2004–2010 we compared observed gain of the new unit with the gain expected if island-total growth were distributed in proportion to 2004 composition. The ratio of observed to proportional-expected gain measures whether the small/new unit gained representation rather than merely increasing because the whole island increased.

This decomposition does not identify movement of individuals between Beaufort units. The inter-island movement inference comes independently from the band/resighting study.

### Boundary cases

Three cases were retained to test the weaker proposition that aggregate direction is not a reliable proxy for spatial direction.

At Bird Island, six Gentoo breeding units had prospectively frozen 1981 and 2024 endpoints, followed by a preallowed audit of all 42 adjacent complete transitions. At Heard Island, historical counts of two King penguin breeding sectors provide post-result literature triangulation only. For emperor penguins, a prospectively frozen 50-colony comparison used published posterior-median abundance indices for 2009 and 2018, with predeclared regional sensitivity analyses.

These cases were not assigned to one of the three process classes because the full intervals did not have sufficiently specific source-side process identification.

### Inferential hierarchy

We separate three levels of claim.

1. **Direct cross-system result:** aggregate abundance direction does not uniquely determine spatial direction.
2. **Process-specific empirical signatures:** the source-identified Ross, Palmer/Signy, and Beaufort cases show different forms of spatial change.
3. **Recoverable-spatial-organization hypothesis:** the biological route of change may influence whether an old multi-node breeding allocation remains recoverable.

Only levels 1 and 2 are empirical conclusions of the present synthesis. Level 3 is a mechanistic hypothesis motivated by those results and independent natural-history evidence.

## Evidence map

The three process-anchored cases are not exchangeable estimates of one common response. Ross has a three-state inverse-path design, Palmer and Signy test persistent concentration against proportional thinning, and Beaufort combines a capacity-release census contrast with independent movement evidence. Table 1 preserves those different estimands rather than forcing them into a common omnibus score.

| Evidence role | System | Process | Main spatial result | Inferential boundary |
|---|---|---|---|---|
| Memory-preserving natural experiment | Ross Island Adélie, 1999→2001→2002 | Acute breeding-state/access disturbance | 96.97% of aggregate loss restored; cosine 0.99695; inverse-path mismatch 9.41% | Post-result spatial decomposition; no individual identity |
| Replicated attrition signature | Palmer Adélie, 1991→2017 | Persistent demographic attrition | Effective breeding-component number declined 19.1%, 50.6%, 82.7% beyond frozen proportional-thinning nulls | Census codes not mapped polygons; vital-rate mechanism unidentified |
| Independent attrition replication | Signy Adélie, 1998→2009 | Persistent demographic attrition | N 2,688→901; E −29.7%; frozen replication supported | No separate survival/recruitment/movement decomposition |
| Capacity-change contrast | Beaufort Adélie, 2004→2010 | Increased nesting capacity | Small/new unit gain 3.15× proportional expectation; share 0.95%→1.48%; independent inter-island export declined | Census and movement are independent evidence streams, not mediation |
| Boundary evidence | Bird Gentoo; global emperor; Heard King | Not assigned to A/B/C | Aggregate direction and spatial direction occupy multiple combinations | Used only against sign-locking; not process-class replicates |

## Results

### An acute breeding disturbance largely re-expressed the previous Ross Island spatial template

Ross Island breeding abundance fell from 207,411 pairs in 1999 to 94,798 in 2001, a loss of 112,613 pairs or 54.3%. All six monitored components declined.

By 2002, breeding abundance had risen to 203,996 pairs. The gain of 109,198 pairs restored 96.97% of the aggregate shock loss in the next available census.

Spatial restoration was also strong. The six-component shock-loss and rebound-gain vectors had a cosine similarity of 0.99695. Relative to an exact inverse path scaled to the observed rebound total, 10,270.6 breeding pairs would need to be reallocated among components, corresponding to 9.41% of the rebound. The balancing positive residual was concentrated at Cape Crozier West.

The magnitude of the 9.41% mismatch was not exceptional within the Ross series: two other complete six-component down-then-up episodes had mismatch fractions of 9.12% and 10.63%. The focal event is therefore informative because it combines a documented external disturbance with near-complete aggregate restoration, not because its residual mismatch is unusually large.

Independent demographic evidence makes a memory-preserving interpretation plausible but not identified. In the 1996–2020 Ross mark-recapture study, movement among colonies was highest for pre-breeders and below 0.20% for established breeders, whereas transitions from breeding to non-breeding states were common [@dugger2026]. The census result itself, however, does not identify individual birds.

### Persistent decline concentrated breeding abundance at Palmer and Signy

At Palmer, the five island populations shared a strongly coherent long-term decline, but within-island spatial change exceeded proportional thinning on the three stable-roster islands.

Effective colony number changed from 3.54 to 2.86 on Cormorant (-19.1%), from 4.62 to 2.28 on Humble (-50.6%), and from 5.78 to 1.00 on Litchfield before local extinction (-82.7%). Under the frozen 20% multiplicative-CV Gamma-Poisson sensitivity, the observed negative concentration slope remained unusual on Cormorant ((p=0.0380)) and was not reached in 100,000 simulations on either Humble or Litchfield (plus-one (p=0.000010) each); no simulation produced slopes as negative on all three islands simultaneously.

Signy independently reproduced the same qualitative departure from proportional thinning. Between 1998 and 2009, total Adélie breeding pairs declined from 2,688 to 901 while effective breeding-unit number fell from 3.610 to 2.539 (-29.7%). The observed slope was more negative than the frozen Poisson and 10% multiplicative-CV null distributions (plus-one (p=0.000010) for each) and remained supported under the 20% multiplicative-CV sensitivity ((p=0.000130)).

Thus persistent decline in both systems altered relative breeding composition rather than simply scaling down a fixed allocation. The data identify unequal local attrition; they do not identify which combination of survival, recruitment, movement, breeding propensity, or reproductive success generated it.

### Increasing breeding capacity redirected growth within and between islands at Beaufort

At Beaufort, usable nesting habitat at the main colony increased strongly as ice retreated, and independent band/resighting data showed that visitation or emigration of Beaufort-born birds to Ross Island colonies peaked near 3% in 2005 and then declined as local habitat became more available [@larue2013].

Within Beaufort, the aerial census also showed a compositional change. From 2004 to 2010, the established main unit increased from 47,725 to 63,760 breeding pairs (+33.6%), while the small/new unit increased from 460 to 957 (+108.0%). Island-total breeding abundance increased by 34.3%.

Because the new unit contained only 0.95% of Beaufort breeders in 2004, proportional allocation of island-wide growth predicts a gain of only 157.8 pairs there. The observed gain was 497 pairs, 3.15 times the proportional expectation. Its share increased to 1.48%, and the effective number of the two census units increased slightly from 1.019 to 1.030.

The conjunction is spatially important: during the same broad capacity-release period, a small/new within-island unit gained disproportionate share while movement toward other islands declined. The result is consistent with local breeding capacity changing the spatial scale at which redistribution was expressed.

### Aggregate abundance direction did not specify spatial direction

The boundary cases rejected a simple rule in which growth necessarily spreads breeders or decline necessarily concentrates them.

At Bird Island, Gentoo breeding abundance increased from 3,331 pairs in 1981 to 4,470 in 2024 (+34.2%) while effective six-unit number also increased from 3.569 to 4.128 (+15.7%). Yet the complete annual record was strongly non-monotonic: among 42 adjacent transitions, 12 had both (N) and (E) increase, nine had (N) increase while (E) decreased, eight had (N) decrease while (E) increased, and 13 had both decrease.

At Heard Island, total King penguin abundance increased in every observed interval from 1963 to 1988 and both monitored sectors increased at every interval, yet effective unit number was non-monotonic and sector dominance reversed.

At the global emperor-penguin scale, the frozen 50-colony posterior-median index declined by 12.4% from 2009 to 2018 and effective colony number declined by 12.8%, but 20 of 50 colonies increased. Across the eight predeclared ice regions, all four combinations of (N)-increase/decrease and (E)-increase/decrease occurred.

Thus the sign of aggregate breeding change did not uniquely specify the direction of spatial reallocation.

## Discussion

### The converse of hidden collapse

Recovery ecology has repeatedly shown that totals can look healthy while structure remains altered. Community abundance or function may recover before multivariate composition [@hillebrand2020], and spatial metapopulation models explicitly produce "hidden collapses" in which total abundance recovers while local patches remain collapsed [@wilson2023]. Our Ross result exposes the opposite interpretive risk.

That site-faithful animals return after disturbance is not new. Individuals can return to familiar home ranges after extreme events [@kreling2021], and colonial birds can retain or alter breeding-site fidelity as colonies are disturbed, restored, or recolonized [@brown2017; @spendelow2016]. Ross therefore should not be sold as evidence that penguins "remember where to breed."

The informative result is the population scale of re-expression. More than half of observed Ross breeding abundance disappeared between 1999 and 2001, yet the next census restored 96.97% of the aggregate loss and the six-component rebound vector was almost collinear with the loss vector. Only 9.41% of rebound abundance would need to be reassigned to produce exact proportional reversal. The mismatch itself is ordinary within the Ross series; the informative conjunction is a severe externally documented disturbance, near-complete numerical restoration, and recovery of almost the same multi-node allocation.

Thus, just as aggregate recovery can hide structural collapse, **aggregate collapse can overstate structural loss when the biological carriers of a previous spatial allocation remain available to re-express it.**

### Breeding censuses observe expression, not all spatial structure

Capture–recapture theory already distinguishes death from temporary absence or nonbreeding [@souchay2014], and high breeding-site fidelity can coexist with high temporary emigration [@safine2020]. Ross adds an aggregate spatial observation to that individual-level logic. The aerial census measures breeding pairs, while later mark–recapture work shows very low movement among colonies for established breeders and common breeder-to-nonbreeder transitions [@dugger2026].

Those data do not identify the individual birds that disappeared from the 2001 census and returned in 2002. We therefore cannot estimate a latent spatial state directly. But they make a specific interpretation plausible: a shock acting heavily on breeding expression can make the observed spatial field collapse faster than the site-affiliated demographic structure that produced it.

This also explains why "spatial memory" should not be equated with resilience. Familiarity and fidelity can restore a previous configuration when the old configuration remains viable, but the same attachment can constrain reorganization after habitat changes. The useful distinction is not memory versus no memory; it is whether the disturbance leaves the old spatial template biologically relevant.

### Persistent attrition erodes allocation through unequal loss

Palmer and Signy show a different arithmetic. Their declines were not reproduced by proportional thinning of a fixed local composition. Effective breeding-unit number fell substantially, and the decline in spatial redundancy exceeded the frozen count-error nulls.

No active aggregation is required. If local breeding units differ in integrated demographic multipliers, some shrink or disappear faster than others and the surviving units gain relative weight. Persistent attrition can therefore rewrite spatial composition simply by removing its carriers unequally.

The data do not identify one causal vital rate. Survival, recruitment, breeding propensity, reproductive performance, and movement can vary among nearby colonies in different ways [@dugger2026]. Treating the census trajectory as the integrated demographic outcome is therefore more defensible than assigning concentration to a single local-quality mechanism.

### Capacity change redirects the map of possible redistribution

Beaufort illustrates a third route: the breeding landscape itself changed. As usable nesting habitat increased, the small/new within-island breeding unit gained 3.15 times the abundance expected under proportional allocation of island-wide growth, while independent band/resighting evidence showed declining movement of Beaufort-born birds toward Ross Island as local habitat became more available [@larue2013].

The two evidence streams do not establish mediation. They do show that within-island spreading and between-island retention can occur together when local capacity changes.

This makes the island ecologically active in a more specific sense than "area matters." For mobile marine foragers, an island is a **dynamic boundary condition on a breeding network**. Capacity can alter whether demographic change is expressed within a breeding unit, among units on the same island, or as movement among islands. Classical area and isolation remain relevant, but they do not by themselves describe this nested redistribution.

### Aggregate direction is a poor proxy for spatial direction

The boundary cases prevent a return to another simple rule. Bird Island Gentoo abundance increased while spatial evenness increased overall, but annual transitions occupied all four combinations of abundance and redundancy change. Global emperor abundance declined overall while 20 of 50 colonies increased, and predeclared regions occupied all four abundance/redundancy quadrants. Heard Island King penguins increased in both monitored sectors while dominance reversed.

Thus "decline concentrates" and "recovery spreads" are both too simple. Aggregate direction is a summary of net change, not a description of how local breeding units contributed to that change.

### The synthesis is unified by a counterfactual, not a common effect size

The three process-anchored contrasts do not share one response statistic, but they do share a counterfactual: aggregate change with no additional spatial reallocation.

For Palmer and Signy, the spatially neutral expectation is proportional thinning of the starting composition. For Beaufort, it is proportional growth of the starting composition. For Ross, where the biological question is recovery from a known preceding shock, it is proportional reversal of the loss vector. In each case the observed local pattern is compared with the spatial allocation expected if aggregate change alone determined local change.

This is why a single omnibus effect size is neither necessary nor desirable. The common inferential object is the **proportional spatial counterfactual**, while the biologically appropriate deviation measure differs with the process and data structure.

### What the present synthesis does—and does not—test

The three process-anchored contrasts still do not share one estimand. Ross has a baseline–trough–rebound inverse-path design. Palmer and Signy test persistent concentration across decline trajectories. Beaufort combines a capacity-release endpoint contrast with independent movement evidence. Treating their deviations from proportional expectation as exchangeable replicates would create a cleaner statistic but a weaker biological study.

The strongest empirical conclusion is therefore comparative, not causal: **source-identified kinds of population change are associated with distinct spatial signatures in the available cases.** The stronger hypothesis is that later spatial recovery depends on whether change primarily suppresses breeding expression, erodes the site-affiliated demographic pool, or changes breeding capacity.

A decisive test would classify disturbance process before opening spatial outcomes and would replicate baseline–perturbation–recovery designs across independent systems. The present archive has only one clean temporary-shock case of that form. That is the main ceiling on any claim of a general law.

### Conservation implications

A recovered headcount is not necessarily a recovered breeding network, but a collapsed breeding census is not necessarily a destroyed one either.

Monitoring programs should therefore distinguish:
1. total breeding abundance;
2. occupancy and relative abundance among breeding units;
3. whether the process causing change is expected to preserve site-affiliated adults and breeding opportunities.

This distinction matters for island-nesting seabirds because the same census signal can call for opposite interpretations. A temporary participation shock may warrant caution against declaring structural collapse, whereas persistent attrition or habitat-capacity change may require monitoring redistribution even if total abundance stabilizes or increases.

## Conclusion

Population change can suppress, erode, or redirect breeding-space organization. In the available penguin systems, an acute breeding-state disturbance removed more than half of observed breeding abundance yet was followed by near-complete numerical and spatial re-expression; persistent decline concentrated breeders through unequal attrition; and increased breeding capacity redirected growth within an island while between-island movement declined. Independent boundary cases showed that aggregate abundance direction alone cannot specify the spatial path.

The broader implication is narrower than a universal law but more informative than a recovery-versus-decline dichotomy: **what disappears from a breeding census is not always what disappears from the breeding network.** Spatial recovery depends on what population change leaves available to be expressed again.

## Transparency and claim boundary

The present manuscript is an integrated synthesis of analyses developed sequentially in one research program.

- The focal Ross 1999–2001–2002 inverse-path decomposition was developed after an earlier frozen 2001–2012 recovery-deconcentration prediction failed.
- The Palmer concentration analysis and Signy replication retain their original frozen nulls.
- The Beaufort within-island decomposition was corrected after recognizing that absolute share of net gain must be compared with a proportional-growth baseline.
- Bird Island and emperor endpoints were frozen before their magnitudes were opened; Heard Island is post-result literature triangulation.
- The A/B/C process classification was formalized after the spatial outcomes were known and is therefore not described as blinded or preregistered.
- No common three-class effect size or omnibus test is claimed.
- The latent variables (S), (q), and (K) are conceptual and are not separately estimated from aggregate colony counts.
- No individual identity is inferred from aggregate colony counts.
- No new covariate, lag, species, or favorable subset was opened to create this synthesis.

The strongest licensed empirical statement is that source-identified kinds of population change are associated with distinct spatial signatures in the available cases. The stronger proposition that process class causally determines spatial memory remains a hypothesis for prospective testing.
