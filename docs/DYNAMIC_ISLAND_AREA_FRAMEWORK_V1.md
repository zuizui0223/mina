# Dynamic island-area framework v1

## Core distinction

For Antarctic penguins, "island area" is not one ecological quantity.

We separate four nested states:

[
A_{physical} \supseteq A_{potential} \supseteq A_{available}(t,s) \supseteq A_{occupied}(t,s)
]

where:

### 1. Physical substrate — A_physical

The geographic land, coastal substrate, ice shelf or fast-ice platform that physically exists.

For ordinary land-breeding Pygoscelis sites, this is comparatively persistent over a demographic study interval.

For emperor penguins, the breeding substrate itself can appear, disappear, fracture or relocate, so A_physical and node position can be dynamic.

### 2. Potential breeding substrate — A_potential

The subset of the physical substrate that could plausibly support terrestrial breeding based on persistent structure such as:

- rock / ice-free substrate;
- terrain;
- coastal access;
- permanent geomorphic constraints.

The earlier static Antarctic breeding-options atlas mostly operates at this level.

Its lack of a confirmatory transferable demographic rule does not test whether the **temporally available** portion changes in ways that matter.

### 3. Temporally available breeding substrate — A_available(t,s)

The part of A_potential that is usable at the biologically relevant time for species s in season t.

Important transient filters include:

- snow / ice cover;
- melt timing;
- access from the sea;
- flooding / wet ground where identifiable;
- species breeding phenology.

This quantity is intrinsically dynamic.

A rock surface that becomes snow-free in February may be "ice-free land" in a summer satellite composite but may have been unavailable when a penguin needed to establish a nest in October–December.

Therefore the ecological target is not annual minimum snow cover by default. It is **phenology-matched breeding opportunity**.

### 4. Realized breeding use — A_occupied(t,s)

The spatial support actually used by breeders.

Paper 1 measures this level indirectly through repeated census components and effective breeding-component number.

A_occupied can contract even when A_potential is unchanged or A_available expands.

---

# How the mina papers map onto the hierarchy

## Paper 1 — realized use contracts

Question:

> Does population decline simply thin breeders proportionally across established breeding space?

Result:

Breeding effort repeatedly concentrates into fewer effective monitored components beyond proportional thinning.

Level:

[
A_{occupied}
]

The generating mechanism remains unresolved.

## Closed static-place lane — potential capacity does not give a confirmed general rule

Question:

> Do fixed amount/heterogeneity/terrain descriptors explain demographic fate across Antarctic Pygoscelis?

Level:

[
A_{potential}
]

Result:

No confirmatory transferable static-place rule was established.

This is not evidence that breeding habitat is irrelevant. It says a fixed snapshot of potential capacity is not sufficient as a general explanation.

## Dynamic Paper 2D — does available area track realized use?

Question:

> When A_available changes, does breeding effort redistribute toward the sites that gain opportunity?

Key comparison:

[
\Delta A_{available} \rightarrow \Delta A_{occupied}
]

or, with the available MAPPPD data, relative demographic weight of breeding-site nodes.

The strongest Antarctic-specific outcome would be:

[
\Delta A_{available} > 0
quad\text{but}\quad
\Delta A_{occupied} < 0
]

showing that physical/terrestrial opportunity expanded while biological breeding space contracted.

## Paper 3 — when the island node itself moves

Emperor penguins extend the hierarchy because the breeding substrate is not merely filtered; its location and persistence can change.

Question:

> When A_physical is transient, does environmental deterioration produce relocation/reassembly instead of within-node contraction?

This creates a contrast between:

- persistent node -> stay and contract;
- mobile/ephemeral node -> move and reassemble.

## Paper 4 — ecological memory outlives occupied space

Penguins transport marine nutrients onto terrestrial breeding sites.

Question:

> After A_occupied contracts, how long does the terrestrial subsidy footprint remain?

This adds a fifth state:

[
A_{legacy}(t)
]

which can persist after current breeding use has disappeared.

---

# Why phenology matters

Pygoscelis breeding opportunity is time-sensitive.

External monitoring shows:

- Adélie nesting/egg laying is concentrated around November, with occupied-nest census timing commonly late November to early December;
- chinstrap laying is generally somewhat later, around late November / early December;
- gentoo phenology is more variable and can begin earlier, with substantial among-site and among-year variation.

Therefore a final dynamic-land metric should not be chosen as "minimum snow during November–March" merely because it maximizes remote-sensing coverage.

The preferred ecological quantity is:

> **the amount of potential breeding substrate exposed during the species-specific nest-establishment / laying window.**

The exact phenology windows must be frozen from external biological sources and remote-sensing support before penguin demographic outcomes are joined.

A broad November–March optical set remains useful for measurement QA and sensitivity analyses, but it is not automatically the primary biological window.

---

# Land–sea extension

For penguins, A_available itself can depend on both domains.

Terrestrial side:

[
A_{available}^{land}(t,s)
]

Marine side:

[
M_{access}(t,s)
]

where M_access represents access through the sea/ice matrix to foraging habitat during breeding.

The realized breeding-site value is therefore better represented as:

[
V_{island}(t,s)
=
f(
A_{available}^{land}(t,s),
M_{access}(t,s),
history/social\ memory
)
]

rather than as a function of static island area alone.

This is the central Antarctic-island-ecology move: **area and isolation become dynamic biological states rather than fixed map attributes.**

---

# Claim discipline

- Do not equate A_potential with nestable area.
- Do not equate summer snow-free area with availability at nest establishment.
- Do not equate A_occupied with physical habitat footprint unless direct colony polygons are available.
- Do not infer individual dispersal from redistribution among site totals.
- Do not reinterpret the old static-place null as support for the dynamic hypothesis.
