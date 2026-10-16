# Population recovery can retrace local losses without restoring spatial structure

**Integrated manuscript draft v0.7**  
**Date:** 2026-10-07  
**Status:** reinterpretation after path-versus-state audit; no new endpoint search.  
**Primary audit:** \`results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json\`  
**Claim ledger:** \`results/SPATIAL_RECOVERY_CLAIM_EVIDENCE_LEDGER_V1.json\`

## Abstract

Recovery of a spatially structured population can be judged by total abundance, by whether gains occur where losses occurred, or by whether final spatial composition returns to its former state. These criteria need not agree. We used a documented mega-iceberg disturbance of Ross Island Adélie penguins to separate them. Breeding abundance fell 54.3% from 1999 to 2001, and the next census restored 96.97% of that aggregate loss. Yet local restoration ranged from 10.8% to 109.8% of prior losses; the dominant Cape Crozier West component supplied 80.6% of rebound. The rebound strongly retraced the geography of loss (90.59% inverse-path fidelity), but endpoint composition remained far from the exact-inverse expectation. At six-component resolution, only 2.4% of the trough's compositional displacement from baseline was erased; after aggregation to Royds, Bird, and Crozier colonies, 28.3% was erased. Exact inverse reversal would have placed composition ~0.07% total-variation distance from baseline at either grain; observed distances were 4.97% and 3.54%, respectively. Independent Palmer and Signy declines and Beaufort capacity release show complementary ways unequal local losses or gains reweight breeding structure. Near-complete aggregate recovery can therefore be a weighted outcome of differential local recovery rather than restoration of the prior spatial population.

**Keywords:** Adélie penguin; colonial breeding; disturbance; island ecology; metapopulation; population recovery; spatial composition; spatial resilience

## Introduction

Ecological recovery is not a single quantity. A population may regain total abundance, a community may regain function without regaining composition, and a spatially structured metapopulation may regain aggregate abundance while local patches remain depleted [@hillebrand2020; @wilson2023]. Recovery theory likewise distinguishes the magnitude of disturbance, the trajectory of return, and the state ultimately reached [@lamothe2019; @white2022]. Metapopulation models predict that uneven disturbance and heterogeneous local demographic rates can alter regional recovery [@wilson2023], while empirical recolonization studies show that local recovery rates depend on conditions in disturbed and source patches [@mutz2017]. These distinctions and mechanisms are therefore established conceptually. The difficulty is that field monitoring often compresses them into one word: recovery.

For a population distributed among persistent breeding sites, three questions are especially easy to conflate. **Amount recovery** asks how much aggregate abundance returned. **Path reversal** asks whether local gains occurred in the same places, and roughly the same proportions, as preceding local losses. **State restoration** asks whether the final relative distribution among breeding sites returned toward its pre-disturbance composition. A rebound can score highly on the first two criteria without satisfying the third. If a large colony both loses and regains many individuals, the loss and gain vectors can be strongly aligned even when that colony overshoots and the relative hierarchy of sites is reweighted.

That possibility is biologically important for colonial breeders. Breeding sites are persistent components of population structure, yet local demographic rates, breeding propensity, access, and habitat capacity can differ among sites. Monitoring at the aggregate scale can therefore miss changes in how reproductive effort is allocated among colonies or subcolonies. Conversely, observing that abundance returned in the same places that lost it does not guarantee that the old spatial state was restored.

Ross Island Adélie penguins provide an unusually strong natural experiment for separating these recovery criteria. Giant icebergs B-15A and C-16 altered sea-ice and colony access and were associated with a severe breeding-abundance trough around 2001 [@lyver2014; @dugger2014]. The public aerial census resolves six persistent breeding components across Cape Royds, Cape Bird, and Cape Crozier. Thus the system contains a known pre-disturbance state, a documented disturbance trough, and an immediate rebound measured with the same breeding-pair census framework.

Previous analysis of this episode showed an apparently simple result: 96.97% of the aggregate loss returned by 2002, and the six-component loss and rebound vectors were almost collinear. At first glance that looks like strong spatial reversibility. But path reversal and state restoration are geometrically different questions. A small structured residual in the rebound allocation can have a large effect on relative composition, especially when it favors a dominant breeding component.

We therefore reanalyzed the Ross natural experiment under an explicit three-part recovery framework. First, we quantified aggregate restoration. Second, we quantified how closely the rebound followed the inverse spatial footprint of loss. Third, we asked whether the endpoint composition actually returned toward the pre-disturbance state. We then calibrated the same distinction against the other complete Ross down→up episodes. Finally, we used two independent process contrasts—persistent Adélie decline at Palmer and Signy, and nesting-capacity release at Beaufort Island—to show how unequal local losses or gains can reweight a breeding network even when all local changes share the same sign.

Our focal hypothesis is deliberately narrow:

> **recovery in the same places as loss does not necessarily restore the same spatial population state.**

The contribution is empirical rather than a new theory of resilience. Trajectory-versus-state distinctions are established in ecology [@lamothe2019]. What the Ross natural experiment provides is a quantified population-level case in which near-complete aggregate and path recovery coexist with state reorganization.

## Materials and Methods

### Evidence design and transparency

All numerical endpoints used here were previously opened in the mina research program. The present path-versus-state distinction was developed after the Ross inverse-path analysis and is therefore explicitly post-result. No endpoint in this manuscript is relabeled as preregistered.

The focal Ross counts are frozen in \`external/ross_island_v2_frozen_counts.csv\`. The 1999→2001→2002 natural-experiment interpretation is anchored to independent published evidence identifying the 2001 period as an iceberg-associated breeding disturbance [@lyver2014; @dugger2014].

The Palmer and Signy analyses retain their original frozen proportional-thinning nulls. The Beaufort proportional-growth correction and independent movement evidence retain their existing post-result boundaries. No new covariate, species, lag, or favorable subset was opened for the present reinterpretation.

### Spatial population state

For local breeding units \(i=1,\ldots,k\) with breeding abundance \(n_i\),

\[
N=\sum_i n_i
\]

is aggregate breeding abundance and

\[
p_i=\frac{n_i}{N}
\]

is the relative spatial composition.

We summarize concentration with the effective number of breeding units,

\[
E=\frac{1}{\sum_i p_i^2},
\]

and compare complete relative-abundance vectors with total-variation distance,

\[
D_{\mathrm{TV}}(p,q)=\frac{1}{2}\sum_i |p_i-q_i|.
\]

\(D_{\mathrm{TV}}\) is interpreted descriptively as the fraction of relative abundance that would have to be reassigned among units to transform one composition into the other.

### Three dimensions of recovery

Let \(\mathbf n_0\) be the pre-disturbance vector, \(\mathbf n_1\) the disturbance trough, and \(\mathbf n_2\) the rebound vector.

#### 1. Aggregate recovery

Local loss and rebound are

\[
L_i=n_{i,0}-n_{i,1},
\qquad
R_i=n_{i,2}-n_{i,1}.
\]

Aggregate loss restored is

\[
A=\frac{\sum_i R_i}{\sum_i L_i}.
\]

\(A=1\) is complete restoration of total breeding abundance lost during the disturbance.

#### 2. Local restoration and path reversal

For each breeding component we defined the local restoration ratio

\[
q_i=\frac{R_i}{L_i}.
\]

Aggregate restoration can then be written exactly as

\[
A
=
\frac{\sum_iL_iq_i}{\sum_iL_i},
\]

so the headline aggregate recovery is the **loss-weighted mean** local restoration ratio. Exact proportional inverse recovery requires \(q_i=A\) for all components.

We quantified directional alignment of local losses and gains with

\[
C=\frac{L\cdot R}{\lVert L\rVert\lVert R\rVert}.
\]

We also defined the exact inverse-path rebound expected if the observed aggregate rebound were distributed in proportion to the preceding local losses:

\[
R_i^{*}
=
\left(\sum_jR_j\right)
\frac{L_i}{\sum_jL_j}.
\]

The half-\(L_1\) mismatch is

\[
M=\frac{1}{2}\sum_i|R_i-R_i^{*}|.
\]

We report \(M/\sum_iR_i\) as the fraction of rebound reallocated relative to exact proportional reversal, and \(1-M/\sum_iR_i\) as inverse-path fidelity.

#### 3. State restoration

We compared the disturbance and rebound compositions with the baseline composition:

\[
D_{01}=D_{\mathrm{TV}}(p_0,p_1),
\qquad
D_{02}=D_{\mathrm{TV}}(p_0,p_2).
\]

For descriptive calibration, the fraction of the disturbance-state displacement erased by the rebound is

\[
S_{\mathrm{TV}}=1-\frac{D_{02}}{D_{01}}.
\]

\(S_{\mathrm{TV}}=1\) indicates complete return to the baseline composition, \(S_{\mathrm{TV}}=0\) indicates no reduction in compositional distance from baseline, and negative values indicate that the rebound endpoint is farther from baseline than the trough.

We also calculated the endpoint expected under exact proportional inverse reversal:

\[
n_{i,2}^{*}=n_{i,1}+R_i^{*}.
\]

Because the focal aggregate rebound restored 96.97% of the loss, this counterfactual is expected to lie very close to the pre-disturbance state. Comparing observed \(\mathbf p_2\) with \(\mathbf p_2^{*}\) therefore measures the state consequence of the structured inverse-path residual.

### Spatial-grain robustness

The six-component Ross representation distinguishes Cape Bird South, Middle, and North and Cape Crozier West and East. To test whether the path-versus-state result depended on this fine census partition, we repeated the focal calculations after aggregation to three biologically named colonies:

- Cape Royds;
- Cape Bird;
- Cape Crozier.

Aggregate abundance is unchanged by this aggregation. We recalculated local restoration, inverse-path fidelity, baseline→trough TV, baseline→rebound TV, and the exact-inverse endpoint at the three-colony grain.

This grain comparison is post-result descriptive robustness. We did not search additional aggregation schemes.

### Within-Ross calibration

We identified the three complete successive Ross triplets in which all six components declined and then all six increased:

- 1989→1990→1991;
- 1999→2001→2002;
- 2002→2003→2004.

For each, we calculated aggregate restoration, inverse-path fidelity, baseline→trough TV, baseline→rebound TV, and \(S_{\mathrm{TV}}\).

We also calculated TV distance for all 25 complete adjacent transitions in the frozen six-component Ross series. The rank of the focal 2001→2002 transition within those 25 transitions is descriptive context, not a null-hypothesis test.

### Persistent attrition at Palmer and Signy

The Palmer analysis used annual breeding-pair censuses from five Adélie breeding islands near Palmer Station from 1991–2017. The concentration test was restricted to Cormorant, Humble, and Litchfield, whose colony-code rosters remained unchanged. Observed trends in effective colony number were compared with fixed-composition simulations that preserved each observed island-total trajectory and applied the frozen Poisson and Gamma–Poisson count-error sensitivities.

The independent Signy replication used eight stable named Adélie breeding units in 1998 and 2009 and the same conceptual proportional-thinning null. These analyses ask whether persistent decline simply scaled a fixed composition or changed relative allocation among breeding units.

### Beaufort capacity release

LaRue et al. documented increased usable nesting habitat at Beaufort Island and changes in movement of banded Beaufort-born penguins toward Ross Island colonies [@larue2013].

The public Ross Sea aerial census includes an established Beaufort colony and a small/disjunct unit first reported as Beaufort Island New. For 2004→2010, we compared the observed gain of the new unit with the gain expected if island-wide growth had been allocated in proportion to the 2004 composition.

The within-island census decomposition does not identify individual movement. The inter-island movement result is an independent evidence stream.

## Results

### Ross recovered almost all lost abundance

Ross breeding abundance fell from 207,411 pairs in 1999 to 94,798 in 2001, a decline of 112,613 pairs or 54.3%. All six monitored breeding components declined.

By 2002, abundance had increased to 203,996 pairs. The gain of 109,198 pairs restored **96.97%** of the preceding aggregate loss.

By aggregate abundance alone, the system was therefore close to its pre-disturbance level after one observed rebound.

### Near-complete aggregate recovery masked strongly unequal local restoration

The 96.97% aggregate restoration was not typical of the six breeding components.

Local restoration ratios \(q_i=R_i/L_i\) were:

- Cape Bird South: **10.8%**
- Cape Bird Middle: **34.9%**
- Cape Royds: **38.7%**
- Cape Crozier East: **64.9%**
- Cape Bird North: **88.9%**
- Cape Crozier West: **109.8%**

The median local restoration was **51.8%** and the unweighted mean was **58.0%**.

Cape Crozier West accounted for **71.2% of the preceding loss and 80.6% of the rebound**. Excluding Crozier West, the remaining five components restored only **65.3%** of their combined loss.

Thus the near-complete aggregate recovery arose from differential local recovery weighted strongly toward the dominant Crozier component.

### Local rebound nevertheless strongly retraced local loss

The six-component loss and rebound vectors were almost collinear:

\[
C=0.99695.
\]

Relative to the exact inverse path scaled to the observed rebound total, the half-\(L_1\) mismatch was 10,270.6 breeding pairs, equal to **9.41%** of total rebound. Inverse-path fidelity was therefore **90.59%**.

Most absolute rebound abundance occurred in the same breeding components that had contributed most absolute loss.

The residual was strongly structured. Cape Crozier West had a positive excess of 10,270.6 pairs relative to exact inverse allocation, whereas all other components fell below their inverse-path allocations.

This is the same local-recovery heterogeneity expressed in allocation space. The loss-weighted mean absolute deviation of \(q_i\) from aggregate restoration was 0.1824; divided by \(2A\), it gives the observed 9.41% inverse-path mismatch exactly.

### Path reversal did not restore spatial state

Despite near-complete aggregate recovery and high inverse-path fidelity, the 2002 composition did not move meaningfully closer to the 1999 composition.

The baseline→trough TV distance was

\[
D_{01}=0.05089,
\]

whereas the baseline→rebound distance was

\[
D_{02}=0.04967.
\]

Thus only **2.4%** of the trough's compositional displacement from baseline was erased.

The rebound itself produced a much larger compositional movement:

\[
D_{\mathrm{TV}}(p_{2001},p_{2002})=0.09753.
\]

This was the largest of the 25 complete adjacent transitions in the frozen Ross series (median 0.03219; upper quartile 0.04444).

The effective-number summaries showed the same lack of state restoration. E6 changed from 2.056 in 1999 to 2.292 in 2001 and then to 1.819 in 2002. Rather than returning to baseline concentration, the rebound crossed past it toward greater dominance. E3 similarly changed from 1.609 to 1.729 to 1.507.

Cape Crozier West drove much of this reweighting: its share changed from 67.2% in 1999 to 62.4% in 2001 and then to 72.2% in 2002.

### Exact inverse reversal would have restored composition almost completely

The state consequence of the 9.41% path mismatch was large.

Given the observed 96.97% aggregate restoration, the endpoint expected under exact proportional inverse reversal had a TV distance of only **0.000717** (0.0717%) from the 1999 composition and E6 = **2.0589**, essentially identical to the baseline E6 = **2.0558**.

The observed 2002 endpoint was instead 0.04967 TV from baseline with E6 = 1.819.

Observed baseline distance was therefore about **69 times** the distance expected under exact inverse reversal.

Thus the residual rebound allocation was not a biologically trivial deviation around an otherwise restored state. It was the difference between near-complete state restoration and substantial reweighting toward the dominant Crozier component.

### Incomplete state restoration persisted after aggregation to three colonies

The magnitude of state restoration depended on spatial grain, but the qualitative path-versus-state result did not.

At the six-component grain:

- inverse-path fidelity = **90.59%**;
- baseline→trough TV = **5.09%**;
- baseline→rebound TV = **4.97%**;
- compositional displacement erased = **2.4%**;
- exact-inverse endpoint distance from baseline = **0.0717% TV**.

After aggregation to Royds, Bird, and Crozier:

- inverse-path fidelity = **93.27%**;
- baseline→trough TV = **4.93%**;
- baseline→rebound TV = **3.54%**;
- compositional displacement erased = **28.3%**;
- exact-inverse endpoint distance from baseline = **0.0695% TV**.

Local restoration at the three-colony grain remained unequal: Royds restored 38.7% of prior loss, Bird 68.3%, and Crozier 105.2%.

Thus coarsening reduced apparent state reorganization but did not eliminate it. Aggregation hid 28.8% of the six-component 1999→2002 TV difference, but **71.2% of the fine-grain endpoint difference remained at the Royds–Bird–Crozier scale**. At both biologically natural grains, exact proportional reversal would have returned composition almost exactly to baseline, whereas the observed endpoint remained materially farther away.

### High path fidelity without state restoration recurred in Ross

The two other complete Ross down→up episodes showed the same distinction.

For 1989→1990→1991, inverse-path fidelity was 90.9%, but the endpoint composition was 29.2% farther from baseline than the trough under the TV restoration index.

For 2002→2003→2004, inverse-path fidelity was 89.4%, while the endpoint was 53.4% farther from baseline than the trough.

Across all three episodes, inverse-path fidelity remained between 89% and 91%, yet \(S_{\mathrm{TV}}\) was +2.4%, −29.2%, and −53.4%.

These triplets are not independent replicates, but they show that the focal distinction is not produced by one unusual mismatch value: in the Ross series, high path fidelity and state restoration were consistently different properties.

### Persistent decline reweighted breeding structure at Palmer and Signy

At Palmer, effective colony number declined from 3.54 to 2.86 on Cormorant (−19.1%), from 4.62 to 2.28 on Humble (−50.6%), and from 5.78 to 1.00 on Litchfield before local extinction (−82.7%).

These declines were more negative than expected under fixed-composition proportional thinning plus the frozen count-error families. Under the 20% multiplicative-CV Gamma–Poisson sensitivity, Cormorant remained unusual (*p* = 0.0380), and no simulated slope was as negative as observed on Humble or Litchfield in 100,000 simulations (plus-one *p* = 0.000010 each).

At Signy, breeding pairs declined from 2,688 to 901 between 1998 and 2009 while effective breeding-unit number fell from 3.610 to 2.539 (−29.7%). The independent frozen replication remained supported under all three count-error families.

Persistent decline therefore reweighted breeding structure through unequal local attrition rather than proportional thinning.

### Capacity release reweighted growth at Beaufort

From 2004 to 2010, total Beaufort breeding abundance increased by 34.3%. The established main unit increased 33.6%, while the small/new unit increased from 460 to 957 pairs (+108.0%).

Given its 2004 share of 0.95%, proportional allocation of island-wide growth predicted a gain of 157.8 pairs in the small/new unit. The observed gain was 497 pairs, or **3.15 times** the proportional expectation. Its share rose to 1.48%.

Independent band/resighting evidence reported declining movement of Beaufort-born birds toward Ross Island after local nesting habitat became more available [@larue2013].

Thus changing capacity was associated with a different form of state reweighting: growth was disproportionately expressed in newly available or previously minor breeding space while inter-island export declined.

## Discussion

### Recovering where loss occurred is not the same as restoring spatial structure

The Ross natural experiment separates three questions that are often compressed into a single word, recovery.

By total abundance, recovery was nearly complete: 96.97% of the disturbance loss returned.

By path, recovery was also highly reversible: local gains strongly aligned with local losses, with 90.59% inverse-path fidelity.

By state, however, recovery was weak: only 2.4% of the compositional displacement from baseline was erased, and the rebound generated the largest adjacent compositional shift in the Ross series.

The ecological lesson is simple:

> **the population recovered where it had declined, but not in the same proportions.**

Trajectory-versus-state distinctions are well established in resilience theory [@lamothe2019]. The contribution here is a direct population-level natural experiment showing that even very high local path reversal can coexist with substantial reorganization of relative spatial structure.

### Aggregate recovery was a weighted average, not network-wide restoration

The headline 96.97% aggregate recovery is mathematically a loss-weighted mean of local restoration ratios. In Ross, those local ratios ranged tenfold, from 10.8% at Bird South to 109.8% at Crozier West. The median breeding component restored only 51.8% of its prior loss.

The aggregate therefore looked nearly complete because most shock loss occurred at the already dominant Crozier West component and that component overshot its prior loss during rebound. Removing Crozier West reduces combined restoration of the other five components to 65.3%.

This is not a reason to discard the aggregate measure; aggregate abundance is ecologically important. It is a reason to interpret it correctly. A near-complete network total can coexist with incomplete recovery of most local components when recovery is disproportionately weighted toward a dominant node.

### A structured residual can dominate the endpoint state

The 9.41% inverse-path mismatch initially appeared modest because more than 90% of rebound allocation followed the spatial footprint of loss. But the exact inverse counterfactual reveals why that interpretation is incomplete.

With 96.97% aggregate restoration, exact inverse reversal would have produced a composition only 0.0717% TV from baseline. The observed composition was 4.97% away.

The difference was structured rather than diffuse. Cape Crozier West overshot its inverse-path allocation by more than 10,000 pairs while all other components under-recovered relative to the same counterfactual. Because Crozier was already the dominant component, this residual amplified its share from 67.2% before the shock to 72.2% after the rebound.

Small fractions of total reallocation can therefore have large effects on normalized state when they are concentrated in dominant components.

### State restoration is scale dependent, but the discrepancy is not

Spatial population state depends on the grain at which breeding units are defined. This is not a nuisance unique to the present analysis; coarsening any spatial network removes within-unit heterogeneity.

Accordingly, the numerical state-restoration score increased from 2.4% at six-component resolution to 28.3% after aggregation to three colonies. The fine-grain value should therefore not be interpreted as a scale-invariant property of Ross Island.

The important result survives the change of grain. Aggregate restoration remains 96.97%, path fidelity remains above 90%, and exact inverse recovery predicts an endpoint almost indistinguishable from baseline at both scales. Moreover, 71.2% of the fine-grain baseline→rebound TV difference remains after aggregation to the three named colonies, so the endpoint discrepancy is not primarily a subcolony-partition artifact. Yet the observed endpoint remains 4.97% TV from baseline at six components and 3.54% at three colonies.

Thus the claim is not that “state recovery equals 2.4%.” It is:

> **high aggregate and path recovery did not produce complete state restoration at either biologically natural spatial grain.**

### Differential recovery is the biological bridge from path recovery to state change

Absolute losses and gains can be strongly aligned simply because large breeding components dominate both. State restoration requires an additional condition: local restoration ratios must be similar enough that relative shares return toward baseline. This expectation is consistent with metapopulation theory in which heterogeneous local demography and unevenly distributed disturbance generate emergent regional recovery outcomes [@wilson2023]. State restoration requires an additional condition: local rebound multipliers must be balanced closely enough to restore relative shares.

Ross did not satisfy that condition. Cape Crozier West restored 109.8% of its prior loss while Bird South restored only 10.8%, with the other components between those extremes. Independent demographic work shows that Ross colonies differ in recruitment, breeding propensity, reproductive performance, survival, and movement, although no single vital rate reproduces the full census ordering [@dugger2026; @schmidt2021].

Thus the rebound can be described as **differential local recovery within a path that was otherwise highly reversible in absolute space**.

This distinction avoids two misleading narratives. Breeders need not have actively redistributed from smaller to larger colonies, and the system need not have followed a wholly new recovery route. The same breeding components recovered, but at different rates.

### Decline and expansion reveal the same state principle

Palmer, Signy, and Beaufort show the broader arithmetic from opposite demographic directions.

At Palmer and Signy, all-system decline did not scale breeding units equally. Unequal local losses concentrated the remaining population beyond proportional thinning.

At Beaufort, island-wide growth did not scale breeding units equally. A small/new unit gained more than three times the abundance expected under proportional expansion after local nesting capacity increased.

The shared ecological principle is not that decline concentrates or growth spreads. It is that **relative spatial state changes whenever local demographic multipliers depart systematically from the aggregate multiplier**.

The biological causes of those unequal multipliers differ—persistent attrition, differential rebound, or changing capacity—but the monitoring consequence is the same: total abundance does not determine relative spatial structure.

### Islands filter where demographic change is expressed

The penguin systems also sharpen the island-ecology interpretation.

Ross shows that different colonies and subcolonies on the same island can respond unequally to a shared regional disturbance and rebound. Palmer and Signy show that persistent island-level decline can be internally redistributed among breeding components. Beaufort shows that increased local nesting capacity can shift growth within an island while reducing movement to another island.

An island is therefore not simply a point with an area and isolation value. For colonial marine foragers, it is a spatial boundary within which local access, terrain, and capacity influence how regional demographic change is allocated among nesting sites and whether that change is expressed as within-island redistribution or between-island movement.

### Consequences for monitoring recovery

Monitoring programs often ask whether abundance has returned to a target. Spatially structured populations require at least two additional questions.

First, **did local recovery occur where local losses occurred?** This is a path question.

Second, **did relative spatial composition return?** This is a state question.

The Ross result shows that the answer can be yes to the first while restoration of the second remains incomplete, with its apparent magnitude depending on spatial grain.

That matters for conservation because dominance structure changes exposure to local hazards. A population with the same total abundance but a larger fraction concentrated in one breeding component has less spatial redundancy than its former state. Conversely, a dramatic local loss followed by proportional rebound may restore both abundance and structure even if the temporary census decline was severe.

Recovery targets should therefore distinguish aggregate abundance, local recovery paths, and endpoint composition rather than treating them as interchangeable evidence of resilience.

### Limits and prospective test

The focal Ross path-versus-state analysis is post-result. The three complete down→up episodes are descriptive within-system calibration, not independent experiments. The state-restoration metrics were developed after the inverse-path result was known.

A prospective test would predefine:

1. a baseline–disturbance–rebound interval;
2. local breeding units;
3. aggregate restoration;
4. inverse-path fidelity;
5. endpoint compositional distance.

The key prediction would not be that high path fidelity implies state restoration. Rather, the hypothesis to test is that **structured deviations from proportional inverse recovery can produce state reorganization even when aggregate and path recovery are high**.

## Conclusion

A spatially structured population can recover its abundance and retrace the geography of its losses without restoring its former spatial state.

In Ross Island Adélie penguins, 96.97% of aggregate shock loss returned and 90.59% of rebound allocation followed the inverse spatial footprint of loss. Yet the endpoint composition did not return: the rebound produced the largest adjacent compositional shift in the series and amplified the dominant Cape Crozier component.

Persistent decline at Palmer and Signy and capacity release at Beaufort show complementary routes to the same outcome—unequal local multipliers reweight breeding structure.

For spatial populations, recovery therefore has at least three distinct dimensions: **how much returned, where it returned, and in what proportions it returned.** The last dimension is explicitly scale dependent, so recovery assessments should report the spatial grain at which state is evaluated.

## Transparency and claim boundary

- The Ross 1999→2001→2002 natural-experiment decomposition was developed after an earlier frozen 2001→2012 prediction failed.
- The path-versus-state distinction, TV state-restoration audit, and three-colony grain sensitivity are post-result.
- The other Ross down→up episodes are descriptive calibration and are not independent replicates.
- The Palmer concentration analysis and Signy replication retain their original frozen nulls.
- The Beaufort proportional-growth correction remains post-result and combines census and independent movement evidence without claiming mediation.
- No new ecological endpoint, covariate, lag, or species was opened for v0.7.
- We do not claim a new mathematical recovery framework; trajectory-versus-state distinctions are prior art.
- We do not infer individual identity from aggregate colony counts.
