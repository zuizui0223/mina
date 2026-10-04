# Antarctic island ecology synthesis v1 — identity, place and use are different state variables

**Date:** 2026-10-05  
**Status:** synthesis after closed Paper 1, closed Paper 2 H1/H2 lane, and completed Paper 3 mobile-node diagnostics.  
**Scope:** conceptual synthesis only; no new outcome search is authorized.

## Program question

> **How do populations lose, gain, and relocate space when habitat geometry, population use, and population identity do not have to move together?**

The Antarctic penguin program now separates three ecological state variables that ordinary site-based analyses often collapse:

\[
\mathcal{S}_t = \{H_t,\ U_t,\ C_t\}
\]

where:

- \(H_t\) = physical habitat / breeding-node geometry and capacity;
- \(U_t\) = realized biological use or allocation of breeders in space;
- \(C_t\) = population or source-provided colony identity.

The three papers show that the transitions of these variables can be partially independent.

---

# Paper 1 — use contracts inside persistent breeding systems

### Empirical state

For declining Antarctic Pygoscelis populations, breeding effort repeatedly concentrates into fewer effective monitored components beyond proportional thinning.

Conceptually:

\[
C_t \approx C_{t+1},
\qquad
H_t \text{ remains geographically available},
\qquad
U_t \text{ contracts}.
\]

The result is not simply abundance decline.

It is a change in the **spatial allocation of use** after conditioning on the observed abundance trajectory.

### Island-ecology contribution

Population decline need not be a uniform thinning of use across an island or breeding system.

> **A population can lose spatial support faster than it loses individuals.**

---

# Paper 2 — physical opportunity and biological use can decouple

### Empirical state

Persistent summer-exposed terrestrial opportunity changed substantially across Antarctic breeding sites:

- 77 physical sites measured;
- 57 positive, 16 negative, 4 zero primary changes.

But sites gaining more opportunity did not show a confirmed general tendency to gain relative breeding use across the frozen three-species comparison.

Conceptually:

\[
\Delta H_t \neq 0
\]

but:

\[
\Delta U_t \not\propto \Delta H_t
\]

as a transferable rule.

### Island-ecology contribution

Island area or habitat capacity should not automatically be equated with realized population use when the capacity itself changes through time.

> **More physical breeding opportunity does not guarantee more biological use.**

The marine mechanism remained unresolved because the single frozen open-water-access metric failed its measurement continuation gate before an H2 outcome was fit.

---

# Paper 3 — population identity can persist while the geographic node moves

### Empirical state

Across Astrid, Mertz and SANAE, 27 consecutive-season transitions gave a median annual breeding-node displacement of 2.30 km and q95 of 14.52 km.

A fixed node would classify the same source-named colony as leaving its previous site in:

- 26/27 transitions at 0.5 km;
- 24/27 at 1 km;
- 16/27 at 2 km;
- 8/27 at 5 km;
- 4/27 at 10 km.

Independent six-colony 2024 SAR data show the opposite short-timescale pattern:

- within-season false absence = 1/48 at 0.5 km;
- 0/48 at 1–10 km;
- q95 minimum huddle displacement = 0.389 km.

Conceptually:

\[
C_{t+1}=C_t
\]

while:

\[
L_{t+1}\ne L_t,
\]

where \(L_t\) is the geographic breeding-node location.

### Island-ecology contribution

A population can persist not by remaining at one patch but by **recreating its occupied breeding node elsewhere**.

> **Site persistence and population persistence are not the same thing in an ephemeral landscape.**

---

# The three spatial response modes

The Antarctic systems now expose three distinct modes.

## Mode I — contract within place

\[
H \approx \text{fixed},
\quad
C \approx \text{persistent},
\quad
U \downarrow \text{ and concentrates}.
\]

Observed in Paper 1.

## Mode II — capacity changes without proportional use tracking

\[
H \text{ changes},
\quad
C \text{ site-associated},
\quad
U \text{ does not consistently track }H.
\]

Observed in Paper 2.

## Mode III — persist by relocating place

\[
C \text{ persists},
\quad
L \text{ moves},
\quad
\text{fixed-site occupancy can show apparent turnover}.
\]

Observed in Paper 3.

These modes are not mutually exclusive in nature. They are a state-space vocabulary for distinguishing processes that ordinary fixed-site abundance data can conflate.

---

# Relation to existing theory

## Dynamic landscapes are not new

Keymer et al. (2000, *The American Naturalist*, doi:10.1086/303407) explicitly modeled patch creation and destruction in dynamic landscapes.

Dynamic habitat-network work later formalized changing patch number, size and connectivity.

Therefore do **not** claim that metapopulation theory assumes all habitat patches are permanent.

## Patch-tracking metapopulations are not new

Snäll et al. (2003, *Oikos*, doi:10.1034/j.1600-0706.2003.12551.x) described patch-tracking metapopulations in which patches themselves turn over and colonization tracks newly created patches.

The emperor result is different.

A patch-tracking framework usually treats disappearance of an occupied patch and occupation of another patch as patch destruction plus colonization.

Paper 3 instead has a source that explicitly preserves the same **named colony identity** while its breeding-node coordinate changes. That permits the observational decomposition itself to be tested.

## Apparent turnover from movement is also known

Occupancy studies recognize that temporary emigration or movement outside a sampling unit can be confounded with apparent local extinction and colonization. Rota et al. (2009, *Journal of Applied Ecology*, doi:10.1111/j.1365-2664.2009.01734.x) explicitly discuss this issue.

Paper 3 does not claim discovery of that statistical principle.

Its contribution is the direct empirical scale curve:

> **how large must a geographic node be, and over what timescale, before source-provided population identity and geographic site identity cease to agree?**

The independent within-season and interannual datasets make this especially informative.

---

# Program-level conceptual contribution

The program suggests that island and patch ecology should distinguish:

### 1. Habitat persistence
Does the physical breeding opportunity remain?

### 2. Site persistence
Does the same geographic node remain occupied?

### 3. Population identity persistence
Does the biological aggregation remain continuously identified as the same population/colony?

### 4. Spatial-use persistence
Does the population retain the same internal allocation of breeders?

These need not coincide.

A conventional occupancy record stores:

\[
O(x,t)\in\{0,1\}.
\]

The Antarctic program suggests a richer representation:

\[
O(x,t \mid C_t,H_t,U_t),
\]

because the meaning of absence at coordinate \(x\) differs depending on whether:

- the population disappeared;
- the population contracted elsewhere in the same breeding system;
- physical opportunity changed;
- or the occupied node relocated while colony identity persisted.

---

# The specifically Antarctic advantage

Antarctica is valuable not merely because it is extreme.

It combines unusually separable spatial processes:

- ice-free terrestrial habitat can expand or contract on ecological timescales;
- marine conditions can change independently of terrestrial breeding opportunity;
- colonial breeders create discrete, repeatedly observable spatial units;
- some penguins use geographically persistent land nodes;
- emperor penguins can use ephemeral/mobile fast-ice nodes;
- satellite monitoring preserves spatial records at scales difficult to obtain in most remote island systems.

Thus Antarctica functions as a natural laboratory for **dynamic island identity**.

---

# Strong program statement

A defensible synthesis is:

> **Population persistence, site persistence and habitat persistence are distinct spatial properties. Antarctic penguins show all three separations: breeding use can contract within a persistent site, physical opportunity can change without predictable redistribution of use, and colony identity can persist while the breeding node itself relocates.**

This is stronger and more general than “penguins respond to climate change,” while remaining inside the evidence.

---

# What remains to test independently

## Cross-taxon generality

The current evidence is Antarctic penguin-specific.

A general island-ecology rule would require analogous systems such as:

- colonial seabirds using ephemeral sand/gravel or ice-associated sites;
- pinniped breeding/haul-out sites with shifting coastal substrate;
- river or wetland colonial breeders using moving bars/islands;
- organisms in patch-tracking successional habitats where biological population identity can be independently tracked.

## Mechanism

The current program identifies spatial response modes before mechanisms.

Unresolved mechanisms include:

- individual breeding dispersal and recruitment;
- social information and site fidelity;
- marine access and food;
- substrate stability;
- demographic composition.

## Conservation implication

Monitoring units should be matched to the timescale of biological inference.

A fixed site can be a valid within-season sampling unit yet a poor multi-year population-identity unit.

The emperor result gives a concrete empirical example rather than a universal prescription.

---

# Paper sequence

### Paper 1
**How do declining populations lose space?**

Answer:
> by concentrating use beyond proportional thinning.

### Paper 2
**Does changing physical capacity explain where populations use space?**

Answer:
> not as a transferable rule in the tested Antarctic Pygoscelis networks.

### Paper 3
**What happens when the breeding node itself moves?**

Answer:
> biological colony identity can persist while fixed geographic site identity turns over.

The sequence is:

\[
\text{allocation within place}
\rightarrow
\text{capacity of place}
\rightarrow
\text{identity of place}.
\]

## Program-level working title

**Beyond fixed islands: population identity, habitat capacity and spatial persistence in Antarctic penguins**

Alternative:

**When place is not persistence: dynamic island ecology in Antarctic penguins**

## Stop rule

This synthesis authorizes no new same-data outcome search.

Paper-specific stop rules remain binding.

Further generality requires genuinely independent taxa, systems, movement data or habitat products.
