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
