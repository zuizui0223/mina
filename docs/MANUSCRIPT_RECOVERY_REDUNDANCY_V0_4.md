# Manuscript spine v0.4 — Aggregate recovery does not determine spatial recovery

**Status:** revised after the prospective Bird Island Gentoo recovery-allocation result. Supersedes v0.3 for paper-level interpretation.

## Working title

**Aggregate breeding recovery does not determine spatial recovery**

Alternatives:

- **Recovering colonial populations need not rebuild where they were lost**
- **Numerical rebound and spatial reorganization are distinct modes of population recovery**
- **Breeding recovery has no single spatial direction across colonial networks**

## Central question

When breeding abundance changes across a network of colonies or breeding units, does the sign and magnitude of aggregate change determine how abundance is redistributed spatially?

The answer is no.

The focal Ross natural experiment shows that almost complete aggregate rebound can fail to restore the pre-disturbance spatial allocation.

A prospective external Gentoo test then shows the complementary outcome: aggregate breeding abundance can increase while the network becomes **more** spatially even.

Thus the general result is not that recovery concentrates or spreads.

It is:

> **aggregate recovery and spatial recovery are distinct demographic dimensions.**

## Measurement boundary

All focal count series quantify breeding abundance—occupied/incubating nests or breeding-pair counts—not total adult population size.

Annual or endpoint change can therefore contain contributions from:

- breeding participation;
- abandonment;
- survival;
- recruitment;
- immigration/emigration.

The paper concerns the spatial allocation of **breeding abundance**.

## Empirical backbone

### 1. Decline discovery — Palmer/Signy

Frozen decline decomposition:

- 0/39 frozen components increased from first to last retained positive season;
- during joint N-down/E-down transitions, gross gains were ~153 versus gross losses ~7,034.

Concentration during decline is therefore generated predominantly by unequal local losses:

    differential attrition.

This establishes that concentration is a spatial state, not evidence of active aggregation.

### 2. Ross Island natural experiment — aggregate restoration without spatial reversal

Use:

- 1999: last complete pre-shock census;
- 2001: documented B-15A/C-16 breeding-disturbance trough;
- 2002: immediate rebound.

#### Aggregate mode

    N1999 = 207,411
    N2001 = 94,798
    N2002 = 203,996.

The shock removed:

    112,613

occupied breeding territories.

The immediate rebound restored:

    109,198

or:

    96.97%

of that aggregate loss.

By 2002 total breeding abundance was already:

    98.35%

of the 1999 pre-shock total.

#### Spatial/compositional mode

Local fractions of shock loss restored:

- Royds: 38.7%;
- Bird: 68.3%;
- Crozier: 105.2%.

At six-component scale:

- Royds: 38.7%;
- Bird South: 10.8%;
- Bird Middle: 34.9%;
- Bird North: 88.9%;
- Crozier West: 109.8%;
- Crozier East: 64.9%.

Thus Crozier overshot while most other nodes remained below pre-shock abundance.

If the actual 2002 total is redistributed according to the 1999 composition, observed-minus-expected residuals are:

- Royds: -1,321;
- Bird: -5,892;
- Crozier: +7,214.

Spatial redundancy likewise remains displaced:

    E3_2002 / E3_1999 = 0.9366
    E6_2002 / E6_1999 = 0.8848.

The direct result is:

> **the aggregate was almost restored, but the losses were not restored in the places where they occurred.**

### 3. Ross path through the disturbance

The same Ross system changes spatial direction through time.

1999 -> 2001:

    N down
    all six components down
    E up.

The shock temporarily equalizes breeding abundance.

2001 -> 2002:

    N up
    all six components up
    E sharply down.

The rebound reconcentrates abundance toward Crozier.

2002 -> 2012:

    N up
    E modestly up.

Thus a single system traverses three different N/E directions.

The frozen 2001–2012 recovery-deconcentration prediction remains a formal FAIL, but the biological interpretation is a shock/rebound path, not monotonic concentration.

### 4. Prospective external test — Bird Island Gentoo

This is the strongest generality check because the six-unit roster and endpoint rule were frozen before nest-count magnitudes were opened.

Frozen endpoints:

    1981 -> 2024.

Aggregate incubating nests:

    3,331 -> 4,470
    +34.2%.

Effective breeding-unit number:

    3.569 -> 4.128
    +15.7%.

So the prospective outcome is:

    N up
    E up.

Growth is strongly redistributed toward an initially small unit:

    Square Pond
    224 -> 911
    4.07x
    proportional residual +610 nests.

The interval is mixed rather than universal-positive:

- 4/6 units increase;
- 2/6 decline.

The dominant endpoint unit remains Johnson.

Under the frozen decision logic this is Outcome B—**spreading/equalizing recovery**—and a prospective counterexample to any universal recovery-concentration rule.

### 5. Bird Island temporal audit — same network, all four directions

The contract explicitly permitted a secondary temporal audit after the primary endpoint result was recorded.

Across 42 successive complete-season transitions:

- N up / E up: 12;
- N up / E down: 9;
- N down / E up: 8;
- N down / E down: 13.

All four sign combinations occur within one consistently monitored network.

Dominant identity also changes temporarily:

- Johnson: 1981–2000;
- Lower Natural Arch: 2001–2002;
- Johnson: 2003–2004;
- Lower Natural Arch: 2005–2007;
- Johnson: 2008–2024.

Therefore even within one island and one species:

> the sign of aggregate breeding-abundance change does not determine the sign of spatial reallocation.

This temporal result is descriptive secondary evidence, not a separately preregistered frequency test.

### 6. Heard Island King penguins — external path triangulation

Post-result literature triangulation:

    1963 North/South = 13/5
    1965 = 36/9
    1969 = 49/37
    1980 = 82/400
    1988 = 215/3,100.

Both local counts increase at every observed interval.

E is non-monotonic:

    1.670 -> 1.471 -> 1.962 -> 1.393 -> 1.138.

Dominance reverses North -> South.

Heard shows that continuous positive local change can pass through equalization and then reconcentration around a new dominant node.

This is post-result triangulation, not confirmatory replication.

### 7. Beaufort Adélie — capacity-release contrast

2004 -> 2010:

- main colony +33.6%;
- new subcolony +108%;
- new-subcolony gain ~3.15x proportional expectation;
- E increases slightly.

Published movement evidence reports reduced export to Ross Island after usable nesting habitat expanded.

Beaufort is mechanistically suggestive, not a generality test.

## Mathematical bridge — common and compositional modes

For breeding unit i:

    N = sum_i n_i
    p_i = n_i / N.

With local instantaneous change:

    d n_i / dt = r_i n_i,

aggregate change is:

    d log(N)/dt = r_bar

where:

    r_bar = sum_i p_i r_i.

Composition changes as:

    d log(p_i)/dt = r_i - r_bar.

Therefore:

### Common mode

    r_bar

controls aggregate increase or decline.

### Contrast modes

    r_i - r_bar

control spatial reallocation.

If:

    r_i(t) = R(t) + q_i(t),

shared forcing R(t) cancels from compositional dynamics:

    d log(p_i)/dt = q_i - q_bar.

This gives the ecological result a simple interpretation:

> reversing the common demographic mode does not require reversal of the relative local demographic modes.

For finite intervals:

    p_i1 / p_i0 = G_i / G_bar.

Spatial composition is restored only if every local multiplication factor equals the aggregate multiplication factor.

Restoring the sum does not restore the vector.

## Why the Bird result changes the paper

Ross alone could be misread as evidence that recovery tends to concentrate.

Bird Island prospectively falsifies that interpretation.

The transferable result is instead a **decoupling**:

    aggregate mode
    !=
    compositional mode.

This is supported in three ways:

1. Ross: near-complete aggregate restoration with incomplete spatial restoration;
2. Bird prospective endpoints: positive aggregate recovery with increased E;
3. Bird temporal path: all four annual N/E sign combinations occur.

Heard and Beaufort broaden the natural-history geometry but are not needed to establish the core result.

## Immediate Ross mechanism — disturbance geometry

Published Ross studies already show that B-15A/C-16 altered:

- sea-ice persistence;
- travel distance to open water;
- migration/access routes;
- breeding dispersal;
- colony-specific apparent survival.

The immediate Ross asymmetry should therefore be interpreted first as:

    shared disturbance
    x
    colony-specific access geometry
    -> unequal breeding response.

Do not invoke configuration-mediated hysteresis as the first explanation for the 2001–2002 pulse.

## Secondary mechanism hypothesis — residual configuration memory

Prior Adélie work already establishes local frozen-herd hysteresis.

The generated cross-scale question is narrower:

> after current environment, access, abundance and usable capacity are controlled, does prior breeding configuration explain residual recovery allocation?

This remains a future hypothesis.

## Conceptual advance

Existing metapopulation-recovery theory distinguishes aggregate recovery from:

- occupancy;
- local extirpation/nonrecovery;
- production;
- rescue.

The empirical addition here is the allocation of abundance **among breeding nodes that remain monitored/occupied**.

A recovering breeding network can:

- restore its aggregate while failing to restore composition;
- increase abundance and become more even;
- increase abundance and become more concentrated;
- change dominant identity;
- traverse several of these states through time.

Therefore recovery is not one scalar quantity.

## Strongest general claim

> **Aggregate breeding recovery does not determine spatial recovery. The total and the spatial allocation of breeders are controlled by different demographic modes, so restoring total breeding abundance neither requires nor guarantees restoration of the breeding network's composition.**

## Strongest Ross-specific claim

> **Ross Island regained 96.97% of the breeding abundance lost during the documented disturbance within the immediate rebound, yet local restoration ranged from 10.8% to 109.8% across breeding components.**

## Strongest prospective generality result

> **In an independently selected Gentoo network, long-interval breeding abundance increased 34.2% while effective breeding-unit number increased 15.7%, prospectively showing that recovery can spread rather than concentrate.**

## Figure spine

### Figure 1 — Common versus compositional recovery

Schematic:

    local changes r_i
        |
        +--> common mode r_bar --> total N
        |
        +--> contrast modes r_i-r_bar --> composition p, E, dominance.

Place Ross and Bird on opposite spatial branches of positive aggregate change.

### Figure 2 — Ross natural experiment

Show:

- N;
- E3/E6;
- colony shares;

for 1999, 2001, 2002, 2012.

Annotate shock, trough, rebound.

### Figure 3 — Ross restoration fractions

Bars for six components:

    fraction of 1999->2001 loss restored by 2002.

Reference line at 1.

This is likely the most intuitive main figure.

### Figure 4 — Bird Island prospective endpoint

1981 vs 2024 six-unit shares and proportional residuals.

Show N↑ and E↑.

### Figure 5 — Bird temporal state transitions

Plot annual delta log N versus delta log E for 42 transitions with quadrants.

All four quadrants should be visible.

### Figure 6 — secondary path triangulation

Heard dominance reversal + Beaufort capacity-opening spread.

Could move to supplement if main text becomes too broad.

## Results order

1. Palmer/Signy: decline concentration is unequal attrition.
2. Ross V2 recovery-deconcentration prediction fails.
3. 2001 is a documented breeding-disturbance trough.
4. Ross restores 96.97% of aggregate loss but restoration fractions vary 10.8–109.8%.
5. Published disturbance/access geometry supplies a parsimonious mechanism for the early asymmetry.
6. Bird Island prospective recovery test yields N↑/E↑.
7. Bird temporal audit shows all four aggregate/spatial sign combinations.
8. Heard/Beaufort show additional path geometries.

## Discussion opening

> Population recovery is usually summarized by whether abundance returns, but restoring the total does not require restoring its spatial allocation. On Ross Island, occupied breeding territories returned to 98% of the last complete pre-disturbance total within the immediate rebound, yet local restoration ranged from 11% to 110% across breeding components. In an independently selected Gentoo network, positive long-term breeding-abundance change instead increased spatial redundancy. Together these results show that numerical and spatial recovery are distinct demographic dimensions.

## Novelty boundary

Do not claim:

- uneven recovery is new;
- spatial structure matters is new;
- Allee effects/hysteresis are new;
- carrying capacity matters is new;
- recovery generally concentrates;
- recovery generally spreads.

Claim:

> **the sign and near-completeness of aggregate breeding recovery do not identify the direction or completeness of spatial recovery among breeding nodes.**

## Journal fit

### Ecology

Now the strongest fit.

The paper is about:

- disturbance and rebound;
- multidimensional recovery;
- spatial population structure;
- path dependence;
- a prospective external counterexample;
- exact demographic decomposition.

### Journal of Animal Ecology

Also plausible if individual demographic mechanisms are expanded, but the current strongest contribution is broader spatial population ecology.

### Journal of Biogeography

Less natural as the primary target now. Island structure is important context, but the central contribution is recovery dynamics rather than geographic pattern.

## Next decisive extension

Do not search for a third result with the same sign.

The next high-value test asks **what predicts the contrast mode**.

Prospectively measure:

- disturbance-induced access cost;
- usable breeding capacity;
- prior configuration;
- local demographic performance;
- movement/immigration;

and predict proportional local restoration after a shared disturbance.

That would move the paper from demonstrating decoupled recovery dimensions to explaining why particular breeding nodes receive the rebound.
