# Paper 3 positioning v1 — dynamic patches are known; mobile occupied-node identity is the target

## What is already established

Metapopulation theory is not restricted to permanently static landscapes.

Existing dynamic-habitat models already allow:
- habitat patches to disappear;
- new patches to be created elsewhere;
- patch suitability and area to vary through time;
- pairwise patch distances and connectivity to be time dependent.

Therefore Paper 3 must **not** claim that allowing patch geography to change is a new theoretical idea.

Representative precedents include dynamic habitat-network viability models (Drechsler & Johst 2010) and dynamic stochastic patch-occupancy models in time-varying wetlandscapes.

## The unresolved observational problem

Most dynamic-patch formulations distinguish two processes:

1. habitat-patch turnover;
2. population colonization/extinction on those patches.

The emperor-penguin case adds a third possibility that matters for empirical monitoring:

> an occupied breeding node can change geographic position while the source data continue to identify the birds as the same named colony.

That generates an identity problem.

At two observations, a monitoring database may see:

[
(x_1, occupied) ightarrow (x_1, empty)
]

and

[
(x_2, empty) ightarrow (x_2, occupied).
]

A fixed-coordinate interpretation labels this as local extinction at (x_1) plus colonization at (x_2).

An identity-aware interpretation may instead be:

[
C_t ightarrow C_{t+1},
qquad L_t 
e L_{t+1},
]

where (C) is the same named colony and (L) is its changing breeding-node location.

## Empirical estimand

Paper 3 therefore targets **coordinate-induced turnover aliasing**:

[
T_{observed}(r)
=
T_{biological}
+
T_{node movement}(r),
]

where (r) is the spatial tolerance used to define a site.

In the three Macdonald tracking colonies, named identity persists through 2017–2024 by construction of the source data. The analysis asks how much fixed-coordinate turnover would nevertheless be inferred at different spatial tolerances.

This is not a claim of demographic closure. It is a claim about observation and population-unit definition.

## Why emperor penguins are an unusually clean system

The breeding substrate can be fast ice or ice shelf rather than fixed land. Recent satellite studies provide:
- repeated within-season positions;
- multiple years for the same named colonies;
- observations of colony splitting into multiple groups;
- independent examples of longer-range relocation.

Thus node movement is observed directly rather than inferred from disappearance/reappearance alone.

## Relation to the mina program

Paper 1:
- persistent spatial units;
- decline concentrates breeding among fewer effective components.

Paper 2:
- persistent site coordinates;
- terrestrial opportunity changes but does not generally predict relative breeding redistribution.

Paper 3:
- **site coordinates themselves are a state variable**.

The progression is:

[
	ext{occupancy within fixed nodes}
ightarrow
	ext{capacity of fixed nodes}
ightarrow
	ext{identity of moving nodes}.
]

## Claim boundary

Do not say “classical metapopulation theory assumes habitat never changes.”

Say instead:

> Many empirical occupancy analyses attach persistence to fixed spatial units, while dynamic-landscape theory already recognizes changing patch structure. Emperor penguins provide a rare empirical case in which an occupied breeding node itself can move, allowing the observational contribution of node mobility to apparent colonization–extinction turnover to be quantified directly.


# Post-result novelty stress test — 2026-10-04

## What prior literature already owns

The paper must not claim novelty for any of the following.

### Dynamic habitats and patch turnover are established theory

Dynamic metapopulation and occupancy studies already model habitat patches whose suitability, existence, age, connectivity, or geographic configuration changes through time. Examples include:

- Hodgson, Moilanen & Thomas (2009, *Ecology*, doi:10.1890/08-1227.1): habitat turnover can mask connectivity–occupancy relationships.
- Falke et al. (2012, *Ecology*, doi:10.1890/11-1515.1): jointly modeled habitat change, site fidelity, colonization and extinction in a dynamic stream network.
- Johst et al. (2011, *Journal of Applied Ecology*): dynamic habitat networks explicitly allow patches to be destroyed and created at new positions.

Therefore the contribution is not “metapopulation patches can move/change.”

### Emperor-penguin mobility is established biology

Emperor colonies are not perfectly philopatric fixed demographic units. Previous work already shows relocation, high mobility, and consequences for interpreting colony-level dynamics.

Recent examples:

- Macdonald et al. (2026, *Communications Earth & Environment*, doi:10.1038/s43247-026-03906-0): repeated within-season colony positions and year-round remote tracking.
- Fretwell et al. (2026, *Communications Biology*, doi:10.1038/s42003-026-10961-y): five West Antarctic colony relocations over approximately a decade.
- Earlier satellite/genetic studies already argue against treating emperor colonies as completely isolated, perfectly philopatric units.

Therefore the contribution is not “emperor colonies move” or “dispersal matters.”

## What the present analysis adds

The empirical target is the **mapping from a continuing named biological aggregation to a geographic monitoring node**.

The frozen analysis directly evaluates:

\[
C_t=C_{t+1}
\quad\text{but}\quad
L_t \notin B_r(L_{t+1}),
\]

where \(C_t\) is source-provided named-colony identity and \(B_r\) is a fixed geographic node of radius \(r\).

This yields an observable quantity that previous relocation descriptions do not provide directly:

\[
A(r)
=
P\left(
\text{same source-named colony lies outside its prior geographic node}
\right).
\]

Across the three long-term series:

- \(A(0.5)=26/27=0.963\);
- \(A(1)=24/27=0.889\);
- \(A(2)=16/27=0.593\);
- \(A(5)=8/27=0.296\);
- \(A(10)=4/27=0.148\).

The result therefore converts colony mobility into a **population-unit consequence**: the amount of apparent local extinction/recolonization induced by fixing node coordinates.

## The independent within-season result changes the interpretation

Macdonald et al. already report that emperor colonies remain relatively stable through winter. The independent six-colony SAR validation is important because it applies the exact same frozen node radii to a separate source.

At 1 km:

- within-season: 0/48 post-anchor dates are falsely absent;
- between seasons: 24/27 source-continuous transitions leave the prior node.

These samples are independent and are not a paired estimator. The contrast nevertheless rules out the weak interpretation that fixed nodes fail simply because colonies are continuously wandering at kilometre scales.

The stronger ecological interpretation is:

> **place identity is temporally scale dependent.**

A geographic node can be a useful ecological unit within a breeding season and a poor persistent population identifier across years.

## New island-ecology object

The Antarctic program now distinguishes:

\[
\text{population identity}
\neq
\text{node identity}
\neq
\text{occupancy/allocation within nodes}.
\]

For persistent terrestrial nodes, Papers 1–2 study changes in breeder allocation and use.

For emperor penguins, Paper 3 shows that the occupied node itself can be re-established elsewhere while the source retains the same colony identity.

This is best described as **relocation-mediated persistence** or **persistence without place persistence**, not as a new form of colonization.

## Strongest defensible novelty statement

> **Emperor penguins provide a directly observed system in which source-continuous colony identity and fixed geographic site identity diverge. Quantifying that divergence shows that apparent colonization–extinction turnover depends strongly on the spatial and temporal definition of the breeding node.**

Avoid absolute “first ever” language unless a systematic literature review supports it.

## Why this is ecology rather than only monitoring methodology

The distinction changes ecological state assignment.

Under a fixed-node representation:

\[
(L_t,1)\rightarrow(L_t,0),
\qquad
(L_{t+1},0)\rightarrow(L_{t+1},1),
\]

which enters a metapopulation analysis as extinction plus colonization.

Under the source-identity representation:

\[
(C_t,L_t)\rightarrow(C_t,L_{t+1}),
\]

which is persistence through relocation.

Those representations imply different ecological histories even when based on the same observations.

Thus the issue is not merely where a satellite analyst draws a buffer. It is what process is assigned to a continuing population in a landscape where the occupied breeding substrate is ephemeral.

## Remaining generality limit

The primary interannual inference is supported by only three long-term named colonies.

The six-colony SAR source independently supports short-term stability, but it does not estimate the continent-wide frequency of relocation.

The result should therefore be framed as a demonstrated **failure mode / ecological state distinction** in an unusually clean natural system, not a numerical law for all emperor colonies.
