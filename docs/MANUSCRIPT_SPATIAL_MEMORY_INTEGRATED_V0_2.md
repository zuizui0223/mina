# Population change can hide or rewrite spatial organization in colonial breeders

**Integrated manuscript draft v0.2**  
**Date:** 2026-10-07  
**Status:** synthesis of already-opened endpoints; no new effect search.  
**Classification contract:** `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`  
**Claim ledger:** `results/SPATIAL_MEMORY_CLAIM_EVIDENCE_LEDGER_V1.json`

## Abstract

Ecological recovery depends partly on biological legacies that survive disturbance, but in mobile colonial animals an important legacy can be latent: surviving individuals may retain affiliations to breeding sites even when they do not breed there in a given year. Population recovery is therefore not only about how much abundance returns. Colonial populations also have an expressed spatial state: breeders are distributed among persistent colonies, subcolonies, or nesting areas. We asked what kinds of population change temporarily suppress that spatial organization and what kinds rewrite it. We synthesized already-opened long-term penguin datasets using process classes assigned from natural-history evidence rather than from spatial outcomes. A documented mega-iceberg disturbance on Ross Island reduced Adélie penguin breeding abundance by 54.3%, yet the next census restored 97.0% of the aggregate loss and the six-component rebound closely retraced the spatial footprint of decline (cosine similarity 0.997; 9.41% inverse-path allocation mismatch). In contrast, persistent Adélie declines at Palmer and Signy were accompanied by concentration among fewer effective breeding components beyond proportional-thinning nulls. A third pattern occurred at Beaufort Island, where increased nesting capacity coincided with disproportionate growth of a small/new breeding unit and declining movement toward nearby Ross Island colonies. Independent Bird Island, Heard Island, and emperor-penguin cases showed that the sign of aggregate abundance change alone did not specify the direction of spatial reallocation. These contrasts do not establish a universal causal law, but they support a process-dependent spatial-memory hypothesis: breeding-site fidelity can preserve a recoverable spatial template when disturbance suppresses breeding expression, whereas demographic attrition and changing capacity can alter the template future breeding expresses. For colonial breeders, numerical recovery and spatial recovery are therefore distinct ecological outcomes.

**Keywords:** Adélie penguin; breeding-site fidelity; colonial breeding; demographic turnover; island ecology; metapopulation; population recovery; spatial reorganization

## Introduction

Population change is usually summarized by a scalar: abundance rose, declined, or returned toward a previous level. That scalar is indispensable, but it discards another population state. Colonial breeders occupy persistent spatial networks of nesting areas, colonies, and subcolonies, and two populations with the same total abundance can distribute reproductive effort very differently across that network. A population can therefore recover numerically without restoring its former spatial organization, or suffer a dramatic temporary breeding decline while retaining much of the spatial information required to reconstruct that organization.

The broad ideas of ecological memory and spatial recovery are not new. Ecological-memory theory emphasizes biological legacies that survive disturbance and shape subsequent recovery, while spatial-recovery and metapopulation theory show that dispersal, network structure, local dynamics, and the spatial footprint of disturbance can alter aggregate recovery [@johnstone2016; @zelnik2019; @wilson2023]. Our question is narrower: **where can a spatial legacy reside in a mobile colonial population when the animals themselves can temporarily disappear from the breeding census?**

This distinction matters especially on islands. Classical island ecology emphasizes area, isolation, colonization, and extinction, while metapopulation theory emphasizes occupancy and exchange among patches. Colonial seabirds add an unusual geometry: they acquire most trophic resources at sea but reproduce in spatially discrete terrestrial patches. Their breeding islands are therefore neither simple resource containers nor passive points on a map. Islands filter shared regional forcing through local snow, terrain, access, and nesting capacity, while strong breeding-site fidelity can preserve links between individuals and particular parts of the breeding network [@fraser2013; @cimino2019; @schmidt2021; @dugger2026]. In this setting, the observed breeding distribution can change much faster than the underlying site affiliations of surviving adults.

This combination creates a simple but underused question: **what must change biologically for the spatial organization of a breeding population to change?** A temporary breeding-participation or access shock can remove birds from a breeding census without necessarily removing the adults, their site attachments, or the breeding locations themselves. If conditions improve, the previous spatial allocation may therefore be re-expressed. Persistent demographic decline is different. Unequal survival, recruitment, breeding propensity, dispersal, or reproductive output can change the relative demographic contribution of local breeding units, so the former allocation need not be recovered even if total abundance later rises. A change in nesting capacity is different again: it modifies the set of locations that can receive breeders and may redirect movement among nested spatial scales.

These alternatives are more biological than a simple distinction between short- and long-term change. Duration alone is not sufficient. A one-year event can permanently remove habitat, while a decades-long series can fluctuate around a stable spatial composition. What matters is whether the perturbation primarily suppresses the expression of an existing breeding network, changes the demographic composition of that network, or changes the network's capacity.

Adélie penguins provide a useful system for separating these processes. On Ross Island, giant icebergs altered sea-ice and colony access and caused widespread breeding disruption, producing an exceptional breeding-abundance trough around 2001 [@lyver2014; @dugger2014]. Long-term mark-recapture work shows that once Adélie penguins have entered the breeder state they move among Ross Island colonies very rarely, while transitions between breeding and non-breeding states remain common [@dugger2026]. This creates a natural expectation of spatial memory: a census shock caused partly by temporary non-breeding can be much larger than the loss of the underlying breeding network.

Elsewhere, long-term decline has a different spatial signature. Near Palmer Station, neighbouring Adélie island populations declined coherently at the regional scale, but within islands breeders became progressively concentrated among a smaller effective set of census breeding components [@cimino2025]. At Signy Island, a separate long-term Adélie decline included colony disappearance and strong reduction in total breeding pairs [@dunn2016]. These systems allow a test of whether persistent decline behaves like proportional thinning or instead rewrites relative local composition.

Finally, Beaufort Island provides an independent capacity-change case. Retreating ice increased usable nesting habitat, population size increased, and movements of Beaufort-born birds toward nearby Ross Island colonies declined after local habitat became more available [@larue2013]. The case therefore links changing island capacity to both within-island allocation and between-island exchange.

We synthesize these already-opened datasets under an explicit evidence hierarchy. Our strongest general test is deliberately modest: aggregate abundance change should not be assumed to specify spatial change. We then ask whether three source-identified processes show distinct spatial signatures in the available systems: temporary breeding-state/access disturbance, persistent demographic attrition, and breeding-capacity change. We do not treat these cases as exchangeable replicates of one effect size, and we do not claim a prospective test of a universal three-process law. Instead, we use them to develop and bound a process-dependent spatial-memory hypothesis: **spatial recovery should depend on what population change removes, preserves, or makes newly available.**

## Materials and Methods

### Evidence design and process classification

All spatial endpoints used here had already been opened in the mina research program before the present synthesis. The purpose of this manuscript is therefore integration, not preregistration of a new cross-system effect.

To reduce outcome-driven narrative assignment, we defined process classes using source-side ecological evidence and prohibited use of the spatial response itself during classification. The complete rules are frozen in `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`.

We distinguished three primary classes.

**Temporary breeding-state or access shock.** Assignment required an independently documented acute disturbance, a breeding-pair or occupied-nest response rather than total adult abundance, evidence that failed, abandoned, skipped, or access-limited breeding contributed to the event, and persistence of the pre-existing breeding geography sufficient to make return biologically plausible.

**Persistent demographic attrition.** Assignment required multi-year population decline plus independent evidence of durable demographic change such as persistent colony loss, mortality or recruitment limitation, emigration, or long-term local extinction. Long duration by itself was not sufficient.

**Breeding-capacity change.** Assignment required independent evidence that usable nesting habitat or breeding capacity changed and that this change plausibly altered settlement opportunities or movement.

Cases lacking sufficient source-side evidence for one of these classes were retained only as boundary cases. We did not use effective breeding-unit number, dominance, inverse-path mismatch, or any other spatial outcome to assign process class.

### Latent site affiliation and expressed breeding state

We use a simple conceptual decomposition to clarify what the breeding census can and cannot observe. It is not fitted as a statistical model.

Let (S_{i,t}) denote the latent pool of living individuals whose established breeding affiliation makes unit (i) a plausible breeding destination at time (t), and let (q_{i,t}) denote the fraction of that pool expressed in the breeding census. Then, schematically,

[
n_{i,t} \approx S_{i,t} q_{i,t},
]

subject to available breeding capacity (K_{i,t}).

The decomposition separates three ways an observed breeding distribution can change.

- A **breeding-state/access shock** acts primarily on (q_{i,t}): breeders temporarily fail, skip, abandon, or cannot access nesting space while much of (S_{i,t}) and the set of breeding units remain.
- **Persistent demographic attrition** changes (S_{i,t}) through unequal survival, recruitment, movement, reproductive contribution, or local extinction.
- **Capacity change** alters (K_{i,t}), changing which parts of the breeding landscape can receive expressed abundance and potentially changing movement among units.

This is an interpretation scaffold, not an identified decomposition. The available colony counts do not separately estimate (S), (q), and (K). Its purpose is to make explicit why the same observed change in (n_i) can carry different implications for future spatial recovery.

### Spatial state

For a census containing local breeding units (i=1,ldots,k), with breeding abundance (n_i), total abundance was

[
N = sum_i n_i.
]

Relative representation was

[
p_i = n_i/N.
]

We summarized spatial redundancy with the effective number of breeding units,

[
E = rac{1}{sum_i p_i^2}.
]

This is the inverse Simpson concentration of breeding abundance: (E) is high when abundance is distributed more evenly among units and low when a small subset dominates. Because the biological identity and spatial scale of census units differ among datasets, (E) is interpreted within each system rather than compared as an absolute cross-system diversity value.

### Ross Island acute disturbance

The Ross analysis used the frozen six-component aerial census series for Cape Royds, Cape Bird South, Middle, and North, and Cape Crozier West and East. The source census estimates breeding pairs or occupied nesting territories near incubation, not total living adults [@lyver2014].

The focal natural experiment was defined post-result using independent natural-history evidence for the mega-iceberg disturbance:

[
1999 ightarrow 2001 ightarrow 2002.
]

For each component we calculated shock loss,

[
L_i=n_{i,1999}-n_{i,2001},
]

and rebound gain,

[
R_i=n_{i,2002}-n_{i,2001}.
]

We quantified aggregate restoration as

[
rac{sum_i R_i}{sum_i L_i}.
]

We quantified directional alignment of spatial loss and rebound with cosine similarity,

[
cos(L,R)=rac{Lcdot R}{|L||R|}.
]

To measure departure from an exact inverse path while holding the observed rebound total fixed, expected rebound was allocated in proportion to shock loss:

[
R_i^{*} =
left(sum_j R_jight)
rac{L_i}{sum_j L_j}.
]

The half-(L_1) mismatch was

[
M=rac{1}{2}sum_i |R_i-R_i^{*}|,
]

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
3. **Process-dependent spatial-memory hypothesis:** the biological nature of change determines whether an old spatial template remains recoverable.

Only levels 1 and 2 are empirical conclusions of the present synthesis. Level 3 is a mechanistic hypothesis motivated by those results and independent natural-history evidence.

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

### Population change has no single spatial inverse

The central result is not that recovery spreads breeders or that decline concentrates them. Both simple rules fail.

Instead, the same scalar change in total breeding abundance can correspond to very different spatial dynamics. Ross Island showed near-complete numerical recovery that largely retraced the spatial footprint of an acute disturbance. Palmer and Signy showed persistent decline that progressively changed relative representation among breeding units. Beaufort showed growth accompanied by increased representation of a small/new unit while inter-island movement declined. Bird, Heard, and emperor penguins showed still other combinations.

This distinction matters because spatial organization is itself a population state. It determines which breeding units carry most reproductive effort, which local hazards can affect a large fraction of breeders, and how much of the breeding network remains occupied or demographically important. A recovered total is therefore not sufficient evidence that the same breeding network has recovered.

### A breeding distribution can disappear faster than its latent spatial template

Ross suggests one biological route by which a previous spatial state can survive a dramatic census shock. The aerial counts measure breeding participation. The mega-iceberg event changed sea-ice access and caused extensive breeding disruption [@lyver2014; @dugger2014]. Independent mark-recapture data show that established Ross breeders almost never move among colonies, while breeding sabbaticals occur frequently enough that annual breeding counts need not equal the number of surviving site-attached adults [@dugger2026].

Together these facts suggest a distinction between **expressed spatial structure** and a **latent spatial template**. The observed breeding vector can collapse because (q_i), the expression of breeding by site-affiliated adults, falls. If many of those adults survive and retain breeding-site affiliations, much of the previous spatial structure may persist without being visible in that year's breeding census. Improved conditions can then reveal a spatial configuration similar to the pre-disturbance one. In that restricted sense, breeding-site fidelity can act as a carrier of population-level spatial memory.

This use of memory is not intended as a new definition of ecological memory. Existing disturbance theory already treats surviving organisms and structures as biological legacies that shape recovery [@johnstone2016]. The additional point here is that, in a mobile colonial animal, part of the relevant legacy can reside in **individual-to-place associations that remain latent when breeding is skipped**. Nor should that interpretation be confused with a claim that fidelity is always stabilizing. Strong fidelity can also slow redistribution when the environment or habitat configuration has changed. Ross subcolony studies show that nesting habitat and colony geometry influence reproductive performance [@schmidt2021], and established site attachment can reduce flexibility after structural change. Spatial memory can therefore restore the past, but it can also preserve a spatial arrangement that is no longer optimal.

This dual role is more informative than treating fidelity as a synonym for resilience.

### Persistent attrition changes the template by changing relative demographic contribution

Palmer and Signy show a different arithmetic. In both systems, persistent population decline was more spatially concentrated than expected under proportional thinning of a fixed local composition.

That pattern does not require breeders to move actively toward large colonies. Concentration can arise when local demographic multipliers differ: some breeding units decline faster, disappear earlier, or recruit fewer breeders than others. In this sense, attrition rewrites spatial composition through unequal loss.

The present data do not identify a single vital rate responsible for this process. That is a strength of the interpretation rather than a deficiency to be hidden. Ross demographic work demonstrates that survival, recruitment, breeding propensity, reproductive success, and movement can vary among nearby colonies in different rank orders [@dugger2026]. A spatial census integrates those components. Persistent change in relative abundance therefore need not map onto one local "quality" variable.

### Capacity can shift the spatial scale of redistribution

Beaufort adds a second way to rewrite the spatial template: change the set of places that can receive breeders.

The usual island-biogeographic description would emphasize a larger amount of usable habitat. The demographic consequence is more specific. As capacity increased, a small/new within-island unit gained disproportionately, while movement of Beaufort-born birds toward Ross Island declined [@larue2013]. Within-island spreading and between-island retention occurred together.

This suggests a nested spatial view:

[
	ext{subcolony} ightarrow 	ext{colony} ightarrow 	ext{same island} ightarrow 	ext{another island}.
]

Capacity can alter where along that hierarchy redistribution is expressed. An island is therefore more than a static unit characterized by area and isolation; for colonial breeders it can act as a **demographic container whose effective capacity changes through time**.

This does not replace classical island theory. It adds a behavioural-demographic layer for organisms that forage outside the island but must return to discrete breeding space.

### Islands are environmental compartments as well as demographic containers

The Ross and Palmer cases also caution against treating "island" as a homogeneous environmental unit. Colonies on different sides of the same island can experience shared regional climate while differing in sea-ice access, snow accumulation, exposure, topography, and nesting substrate [@fraser2013; @cimino2019; @schmidt2021].

Thus island effects operate in two directions.

First, an island is an **environmental compartment**: local geometry filters common regional forcing into different breeding conditions within the same landmass.

Second, an island is a **demographic container**: local capacity and boundaries influence whether breeders are retained, redistributed internally, or expressed as movement among islands.

This nested perspective is closer to the biology of colonial seabirds than a binary choice between "regional forcing" and "island effect."

### A process-dependent hypothesis for expressed and latent spatial structure

The present cases motivate, but do not prospectively test, a broader hypothesis.

> **Spatial recovery depends on whether population change suppresses breeding expression, changes the site-affiliated demographic pool, or changes breeding capacity.**

If disturbance primarily removes breeding expression while leaving site-attached adults and the breeding network available, a previous spatial template can remain recoverable.

If population change instead removes individuals or breeding units unequally, demographic turnover changes the relative contribution of the network's components.

If capacity changes, the set of feasible breeding locations changes and redistribution can occur along a new spatial path.

The hypothesis predicts that the biological process causing abundance change should be more informative about spatial recovery than the sign or duration of abundance change alone.

A decisive future test would classify disturbances from independent natural-history evidence before spatial outcomes are opened and would compare multiple systems with a common baseline-disturbance-recovery design. The present synthesis does not meet that standard, because the three process classes are represented by different natural experiments and different spatial estimands.

### Conservation implications

Population monitoring often treats a return of abundance as recovery. For colonial breeders, that can be misleading in both directions.

A dramatic decline in breeding counts can overstate structural loss if many site-attached adults temporarily skip or fail breeding and later re-express the same network. Conversely, a recovered or increasing headcount can hide concentration, dominance change, loss of peripheral breeding units, or replacement of the previous spatial configuration.

Monitoring programs should therefore distinguish at least three quantities:

1. total breeding abundance;
2. occupancy and relative abundance among breeding units;
3. whether the biological process causing change preserves or alters the population's capacity to re-express its previous spatial organization.

For island-nesting seabirds, this requires treating breeding space as a dynamic demographic state rather than only a geographic backdrop.

## Conclusion

Population change has no single spatial inverse. In the available penguin systems, an acute breeding-state disturbance largely re-expressed a prior spatial template, persistent decline concentrated breeders through unequal attrition, and increased breeding capacity redirected growth within an island while reducing export. Independent boundary cases showed that aggregate abundance direction alone cannot identify the spatial path.

These results motivate a process-dependent hypothesis without yet proving a universal mechanism. Whether a colonial population restores its former spatial organization appears to depend not simply on how much abundance was lost or how long change lasted, but on **whether change altered breeding expression, the site-affiliated demographic pool, or the capacity of breeding space itself**.

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
