# Manuscript spine — island demographic coherence v1

## Working title

**Breeding islands structure annual demographic coherence within a regionally forced Adélie penguin metapopulation**

Alternative:
**Geographic islands emerge as mesoscale demographic coherence units in declining Adélie penguins**

## One-sentence contribution

Across a 27-year colony-level census, Adélie subcolonies on the same breeding island share annual demographic deviations beyond the regional year signal more strongly than subcolonies assigned to abundance- and coverage-matched pseudo-islands, showing that a geographic island corresponds to a real intermediate layer of demographic coherence even though it is not demonstrated to be a closed population or a causal coastline boundary.

## Question

For a highly mobile colonial marine predator, is a breeding island merely a convenient geographic label, or does island membership capture a real level of population dynamics between subcolonies and the regional metapopulation?

The paper does **not** ask whether regional synchrony exists. That is established background.

## What is new

Existing penguin and seabird work has shown:

- synchrony among colonies at regional scales;
- movement among colonies and metapopulation structure;
- within-colony/subcolony breeding synchrony;
- subcolony-scale habitat effects;
- island-wide versus focal-colony trend differences.

The new test is hierarchical and label-explicit:

1. remove each colony's persistent scale and variance;
2. remove the shared regional year component without using island identity;
3. ask whether co-observed colony deviations covary more strongly when they belong to the **same real island**;
4. compare the observed island assignment with static pseudo-island assignments that preserve abundance / observation-coverage structure.

Thus the novelty is not “nearby subcolonies are similar.” It is that **island identity adds a detectable demographic covariance layer after the regional component is removed**.

## Primary Palmer evidence

Dataset: Palmer LTER Adélie breeding census, 1991–2017.

### Regional context

Five neighboring island populations share a dominant long-term decline:

- PC1 of standardized log abundance: 96.4%;
- median pairwise annual island-growth correlation: 0.373;
- unique year fraction: 53.5%;
- unique island fraction: 33.0%.

These are context, not novelty.

### Missingness-robust island-year coherence

Eligible colony codes: 56.

For every colony:

- annual growth = diff(log1p breeding pairs);
- retain only adjacent-year transitions with both censuses observed;
- exclude zero-to-zero transitions;
- standardize informative growth within colony;
- subtract the mean standardized growth across all eligible colonies in each end year.

Primary statistic:

mean residual product for same-island colony-pair × year records minus the corresponding mean for different-island records.

Observed five-island result:

- within-island mean product = +0.05618;
- between-island mean product = −0.03662;
- contrast = **+0.09280**;
- 3,919 within-island and 14,148 between-island pair-year records;
- 20,000 static pseudo-island permutations;
- two-sided **p = 0.00010**.

Litchfield excluded:

- contrast = **+0.08571**;
- **p = 0.00100**.

Decision: **strong confirmation** under the frozen missingness-robust test.

### Temporal persistence

Using the same frozen all-period residualization as a descriptive split:

- 1991–2006 contrast = +0.08378;
- 2007–2017 contrast = +0.18063.

The direction therefore persists after the system has strongly declined; the late-period complete-case failure was a data-availability / identifier-continuity problem, not evidence for loss of island coherence.

## Robustness

### Not created by extinction zeros

Restricting to positive-to-positive colony transitions:

- five islands: contrast = +0.11758, p = 0.00010;
- four islands without Litchfield: contrast = +0.11980, p = 0.00010.

### Not created by one island

Leave-one-island-out contrasts remain positive in all five tests:

- drop CHR: +0.05038, p = 0.03970;
- drop COR: +0.09471, p = 0.00010;
- drop HUM: +0.08580, p = 0.00010;
- drop LIT: +0.08571, p = 0.00090;
- drop TOR: +0.15864, p = 0.00150.

Therefore the signal is not an extinction artifact and does not depend on any single island.

## Important failed hypothesis: spatial insurance

The original prediction was that subcolonies within an island might compensate for one another, stabilizing the island total.

That prediction is **not supported**.

In the complete-case exploratory hierarchy test:

- mean within-island growth synchrony phi = 0.255;
- synchrony among island-total growth = 0.441;
- hierarchy gap = +0.185;
- abundance-matched pseudo-island null mean gap = +0.341;
- upper-tail p = 0.979.

Same-island colonies are **more**, not less, coherent than expected. The island behaves more like a shared-response unit than a compensatory portfolio.

Do not resurrect “spatial insurance” as the main interpretation.

## Census-timing audit

Same-island subcolonies often share census dates, creating an observation-process concern.

A frozen audit retained only colony-pair × year records with exactly the same start census date and exactly the same end census date, then conditioned on the full schedule block.

Five-island same-island fixed effect:

- coefficient = +0.07039;
- p = 0.03980.

Without Litchfield:

- coefficient = +0.07641;
- p = 0.06180.

The effect size remains positive and similar, and exact shared census dates are insufficient to explain the five-island result. However, the strict two-analysis timing-robustness rule fails. Therefore:

- do not claim all observation-process confounding is excluded;
- report census timing explicitly as the leading remaining measurement caveat.

## What “island unit” means here

Supported:

> Island membership identifies a mesoscale layer of annual demographic coherence nested between subcolonies and the regional population.

Not supported:

- islands are demographically closed populations;
- coastline itself causes a discontinuity beyond geographic distance;
- same-island coherence is caused by dispersal;
- same-island coherence is caused by terrestrial habitat;
- same-island coherence proves local density dependence;
- island-scale aggregation produces spatial insurance.

Prefer **demographic coherence unit/layer** over **population unit** when precision matters.

## Mechanistic interpretation to discuss, not claim

The pattern is compatible with several nonexclusive island-level filters:

1. **terrestrial breeding environment** — island geomorphology, snow retention, meltwater and nest-space configuration can impose shared reproductive conditions on subcolonies;
2. **local access / phenology** — island-specific access to marine foraging and breeding chronology may synchronize annual responses;
3. **behavioral connectivity** — recruitment or redistribution among nearby subcolonies may couple them;
4. **observation process** — shared census timing is partly addressed, but observer- or island-specific protocol effects remain possible.

The strongest ecological interpretation is therefore scale structure, not mechanism identification.

## Role of prior mina results

### Keep as background / secondary evidence

- common long-term decline and divergent island endpoints;
- Litchfield extinction;
- Torgersen mapped breeding-footprint contraction;
- finite sea-ice / snowfall mechanism tests as bounded negative tests.

### N_eff

Effective colony number remains a conditional association with next-year growth, not a supported predictive pillar.

Use it only as a secondary indication that internal colony configuration changes during decline. Do not make it necessary for the island-coherence argument.

## External validation

### Signy Island

High-value next dataset:

- annual Adélie colony monitoring, 1978–2020;
- nine monitored colonies;
- CEMP-standardized methods from 1996/97;
- colony GPS information from 2006/07 onward.

Use Signy as an **independent within-island coherence replication**, not as a second same-vs-different-island test.

Predeclare:

- primary window: 1996/97 onward because CEMP methods are standardized;
- full record: sensitivity only;
- no post-result colony regrouping;
- account explicitly for known colony mergers / identifier changes.

Gentoo public data appear aggregated at island level in the released dataset, so do not promise a colony-level species contrast until raw colony counts are obtained.

## Remaining decisive spatial test

The strongest unresolved test is distance conditioning.

If a colony-code → coordinate/GIS crosswalk can be resolved, test whether island membership explains covariance after geographic distance is controlled:

same-year colony covariance ~ distance + same_island + year structure.

Until then, phrase the result as **island-label demographic coherence**, not a coastline discontinuity independent of distance.

## Figure architecture

### Figure 1 — The hierarchy being tested

Regional Palmer system → breeding island → census subcolonies.

Show that the central question is the location of the demographic boundary, not another climate correlation.

### Figure 2 — Shared region, structured islands

Top: five island trajectories / regional common decline.

Bottom: residualized colony-year deviations grouped by island.

### Figure 3 — Actual islands beat pseudo-islands

Primary island-year covariance contrast with 20,000 pseudo-island null distribution.

Show five-island and no-Litchfield estimates together.

### Figure 4 — Robustness

Compact forest plot:

- positive-to-positive only;
- leave CHR out;
- leave COR out;
- leave HUM out;
- leave LIT out;
- leave TOR out;
- exact census-schedule audit.

Visually distinguish the timing audit because its strict no-Litchfield p-value is 0.0618.

### Figure 5 — Ecological interpretation / external validation

Option A if GIS crosswalk is obtained: covariance vs distance and same-island boundary.

Option B otherwise: Torgersen mapped subcolony attrition plus a clearly labeled mechanism schematic, with Signy reserved for external validation if completed before submission.

## Manuscript logic

1. Ecologists often aggregate colonial organisms into named colonies/islands, but those boundaries need not correspond to the scale at which population fluctuations are organized.
2. Penguins are especially useful because they are highly mobile at sea but tied to discrete terrestrial breeding patches.
3. Palmer shows strong regional decline, so simple synchrony alone cannot identify the relevant demographic unit.
4. Remove the regional year signal and ask whether the residual dynamics still know which island a subcolony belongs to.
5. They do.
6. The surprising part is that the island signal reflects **coherence rather than compensation**.
7. Therefore geographic islands can remain demographic coherence layers even in a marine predator whose resource environment is regional and whose individuals are mobile.

## Stop rule

Do not open further arbitrary climate windows, topology metrics, colony-size thresholds, temporal cutoffs or residual transforms.

Only two additions can materially change the paper:

1. a frozen distance-conditioned GIS test;
2. genuinely independent Signy replication from the authoritative raw dataset.

Everything else is manuscript consolidation or clearly secondary sensitivity analysis.
