# Manuscript spine v0.1 — Recovery is not the reverse of collapse

**Status:** superseded by `MANUSCRIPT_RECOVERY_REDUNDANCY_V0_2.md` after the Ross mega-iceberg shock/rebound audit.

## Working title

**Numerical recovery of breeding colonies need not restore spatial redundancy**

Alternatives:

- **Opposite demographic processes converge on spatial concentration in colonial penguins**
- **Breeding-population recovery is not the spatial reverse of collapse**
- **Unequal losses and unequal gains produce the same spatial concentration**

## One-sentence result

Across colonial penguin systems, spatial concentration in breeding abundance arose during decline through differential attrition and during numerical recovery of breeding-pair counts through differential amplification; a second recovering species showed that concentration can also follow a complete reversal of colony dominance, demonstrating that aggregate abundance, occupancy, spatial redundancy and dominant-node identity are distinct recovery dimensions.

## Biological question

When breeding abundance in a colonial population declines and later recovers, does its spatial organization retrace the same pathway in reverse?

The null intuition is simple:

    decline -> fewer/weaker breeding units -> concentration
    recovery -> regrowth of breeding units -> deconcentration.

The data reject this as a general description.

## Primary empirical backbone

### Discovery / decline side — Palmer and Signy

Five declining populations.

Frozen component decomposition shows:

- 0/39 components increased first-to-last;
- concentration is overwhelmingly produced by unequal losses;
- gross gains are negligible relative to losses during N-down/E-down transitions.

Interpretation:

    differential attrition.

### Independent frozen recovery test — Ross Island

Three biological colony nodes:

- Royds
- Bird
- Crozier.

2001-2012 frozen endpoints:

    N +270%
    all 3 colonies increase
    all 6 census components increase
    E3 -10.7%
    E6 -14.0%.

Most of the composition shift occurred in an early 2001-2002 pulse:

    breeding-pair N +115%
    E3 -12.8%
    E6 -20.6%
    Crozier share 70.8% -> 79.0%.

After 2002, E fluctuated without a clear monotonic trend. The frozen whole-phase log(E3) slope was negative but descriptively weak (p=0.246), and a post-result 2002-start sensitivity was essentially flat.

Interpretation:

    early differential amplification followed by persistence of a concentrated composition.

The preregistered recovery-deconcentration prediction failed, but the result must not be described as steady phase-long erosion.

That failure is the main result, not something to rescue.

### External species/island triangulation — Heard Island king penguins

Spit Bay North and South both increase across every observed interval.

Yet:

    E 1963 = 1.670
    E 1965 = 1.471
    E 1969 = 1.962
    E 1980 = 1.393
    E 1988 = 1.138.

Dominance changes:

    North -> South.

Interpretation:

    recovery can be non-monotonic in spatial redundancy and can reconcentrate around a new dominant node.

This is post-result triangulation, not confirmatory replication.

### Contrasting recovery case — Beaufort Island

Habitat release accompanies:

- rapid growth;
- disproportionate growth of a small/new subcolony;
- slight E increase;
- reduced inter-island export in independent movement data.

Interpretation:

    recovery can also spread when new/under-used capacity receives disproportionate growth.

## Mathematical bridge

For E = 1/sum(p_i^2),

    d log(E)/dt = 2(r_bar - r_D).

This makes concentration a statement about the spatial allocation of change in measured breeding abundance, not about whether total adult population size is increasing or decreasing.

For finite intervals:

    E1/E0 = (G_bar/G_D)^2.

Do not sell this as a new theorem.

Use it to make the ecological logic transparent.

## The conceptual advance

Existing metapopulation recovery work emphasizes:

- aggregate recovery;
- patch occupancy;
- rescue;
- local collapse;
- carrying capacity;
- relative production.

This paper adds a distinct empirical state variable:

    abundance-weighted spatial redundancy among occupied breeding nodes.

And Heard adds a necessary history variable:

    dominant-node identity / turnover.

Therefore a metapopulation can have:

    abundance recovered
    occupancy intact
    every local node growing
    spatial redundancy declining.

## Figure spine

### Figure 1 — Four recovery/collapse paths

Conceptual N-E plane with arrows:

- Palmer/Signy: N down, E down;
- Ross: N up, E down, same dominant;
- Heard: N up with non-monotonic E and dominant reversal;
- Beaufort: N up, E up.

Do not imply these four cases exhaust all possibilities.

### Figure 2 — Ross frozen test

Panels:

A. N through time, 1985-1999 and 2001-2012.
B. E3 through time.
C. E6 through time.
D. 2001 versus 2012 colony shares / proportional residuals.

Main visual message:

    all colony breeding-pair counts increased, but Crozier gained share.

### Figure 3 — Demographic arithmetic

Paired schematic:

    decline concentration:
    unequal losses

    recovery concentration:
    unequal gains.

Place the exact E identity between them.

### Figure 4 — Heard dominance reversal

North/South abundance through time plus E.

This is the clearest visual proof that numerical recovery and spatial redundancy can have different, non-monotonic trajectories.

### Figure 5 — Beaufort contrast

2004/2010 share comparison plus published movement/habitat timeline.

Use as mechanism-generating contrast, not as confirmatory support for a universal capacity model.

## Results order

1. Differential attrition produces concentration during decline.
2. Frozen Ross prediction fails: recovery also concentrates.
3. Ross concentration is differential amplification despite universal local growth.
4. The effect is present at both three-colony and six-component scales during recovery.
5. Heard triangulation shows non-monotonic recovery and dominance reversal.
6. Beaufort shows recovery can instead deconcentrate under habitat release.

## Discussion opening

Do not open with penguin natural history.

Open with:

> Recovery is often evaluated from breeding-pair abundance, but spatial recovery need not reverse spatial collapse. In our focal system, breeding-pair counts increased 3.7-fold across the frozen interval and every monitored breeding unit had a higher endpoint count; an early post-disturbance pulse shifted breeding abundance disproportionately toward the dominant colony, and the system did not show the predicted spatial deconcentration.

Then immediately contrast:

> The same concentration state had been generated during decline by the opposite demographic arithmetic: unequal losses.

## Novelty boundary

Do not claim:
- that uneven recovery is new;
- that carrying capacity matters is new;
- that Ross colonies differ demographically is new;
- that the reciprocal Simpson index is new;
- that all recovery concentrates.

Claim:

> strong recovery in breeding-pair abundance can generate or maintain spatial concentration without any local decline in breeding-pair counts, and the same concentration metric can arise from opposite local count arithmetic.

With Heard:

> endpoint concentration can also hide a complete turnover in which breeding unit is dominant.

## Relation to island biogeography

Keep island biogeography as a conceptual extension, not the opening claim.

The useful bridge is:

- classical island theory: area/capacity and isolation regulate persistence/colonisation;
- colonial breeders: one island contains multiple breeding nodes and dynamic usable capacity;
- recovery: individuals can be reallocated among those nodes without changing occupancy or island identity.

Thus islands are not simply points in a metapopulation network; they contain internal demographic networks whose redundancy can erode or turn over.

## Journal fit

Best current fit:

1. **Ecology** — strongest if framed around recovery-state mismatch and demographic arithmetic.
2. **Journal of Animal Ecology** — strong if penguin demographic mechanisms and colony structure are foregrounded.
3. **Journal of Biogeography** — possible if the island-network framing is expanded, but the present result is more population ecology than classical biogeography.

A higher generality journal would require a prospective multi-system test of the recovery-state prediction beyond the currently selected penguin systems.

## Next decisive evidence

The highest-value next dataset is not another static island-trait comparison.

It is an independent recovering colonial metapopulation with:

- >=3 fixed breeding units;
- repeated or paired abundance;
- complete local persistence;
- enough information to determine E and dominance turnover;
- preferably a dynamic capacity or vital-rate covariate.

The prospective prediction should be about the **distribution of local growth**, not simply total recovery.


## Generated mechanism for Discussion — configuration-mediated recovery hysteresis

This mechanism is **post-result and not confirmatory**.

Prior work already establishes:
- Allee-type positive density dependence in colonial seabirds;
- slow recolonization under strong Allee effects;
- Adélie "frozen herd" hysteresis caused by nest-site fidelity, fragmentation and edge-biased predation;
- slow post-iceberg recovery and elevated edge exposure at Cape Royds;
- sustained immigration during establishment of new Gentoo colonies.

Therefore do not claim that this paper discovers Allee effects or hysteresis.

The generated cross-scale hypothesis is narrower:

> local spatial memory and positive density dependence may bias where regional breeding recovery is expressed, so nodes that retain favorable configuration or sufficient social density absorb more of the recovery while fragmented nodes lag.

The post-result Ross matched-abundance comparison is consistent with this.

At ~204k breeding pairs:
- decline 1997: E3 = 1.626;
- recovery 2002: E3 = 1.507.

At ~222k breeding pairs:
- decline 1985: E3 = 1.625;
- recovery 2004: E3 = 1.413.

Thus similar total breeding abundance occurred in different spatial states.

Call this a **branch-dependence / hysteresis signature**, not proof of endogenous hysteresis. Environmental conditions, especially the B15A/C16 iceberg disturbance, differ strongly between branches.

### Mechanistic model for Discussion

Conceptually distinguish:

    B_i = breeding-pair abundance
    Z_i = spatial/social configuration
    K_i = usable breeding capacity
    I_i = immigration
    R_t = regional forcing.

A local breeding-count change can depend on:

    regional forcing
    + persistent local quality
    + positive density/configuration effects
    - crowding near usable capacity
    + movement.

If Z changes more slowly than B, decline and recovery need not follow the same spatial path.

### Prospective prediction

The decisive next test is not another count-only correlation.

At matched current breeding abundance and environment, prior fragmentation/configuration should predict subsequent breeding success or recovery.

In particular, lower perimeter-to-area ratio, lower edge exposure, and more compact breeding configuration should predict stronger recovery after controlling current B.

This is the prospective test that can separate configuration-mediated memory from simple colony-size dependence.
