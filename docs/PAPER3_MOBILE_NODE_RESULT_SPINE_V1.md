# Paper 3 result spine v1 — colony identity can persist while the breeding node moves

**Date:** 2026-10-04  
**Status:** primary interannual mobile-node diagnostic and independent within-season SAR validation completed.  
**Branch:** \`research/emperor-mobile-islands-v1\`  
**Papers 1–2 remain unchanged.**

## Central ecological question

> **What does persistence mean when the breeding “island” itself can move?**

Emperor penguins breed on fast ice and other frozen substrates whose spatial position is not fixed. Existing work has already established that emperor colonies move within seasons and that some colonies relocate across years. Paper 3 therefore does **not** claim discovery of movement.

The new ecological question is whether the identity of a breeding aggregation can remain continuous while the geographic node used to define a “site” changes enough that a fixed-patch interpretation would call the same named colony locally extinct and newly colonizing elsewhere.

This separates two state variables:

\[
C_t = \text{source-provided named-colony identity}
\]

and

\[
L_t = \text{geographic breeding-node location}.
\]

A colony can satisfy:

\[
C_{t+1}=C_t
\qquad\text{while}\qquad
L_{t+1}\ne L_t.
\]

The analysis asks how large that mismatch is at fixed spatial tolerances.

---

## 1. Interannual mobile-node result

### Source and semantic validation

The long-term analysis uses the public Macdonald et al. Zenodo data for Astrid, Mertz and SANAE, 2014/15–2023/24.

The first route-semantic hypothesis — that \`pointLon/pointLat\` must coincide with a route endpoint — failed and is retained as a failed audit.

A corrected semantic contract was then frozen **before interannual displacement was calculated**, using the publication's stated definition that route distance is measured from the colony location in the first image of each season.

The corrected source-semantic audit found:

- 71 route features;
- 30 colony × seasons;
- 10 seasons each for Astrid, Mertz and SANAE;
- 100% date parseability;
- 30/30 seasons with invariant source \`pointLon/pointLat\`;
- maximum within-season variation in the season reference point = **0 m**.

The source-supplied season point therefore serves as the annual colony-node anchor.

### Frozen radius curve

The spatial tolerances were fixed before displacement was opened:

- 0.5 km;
- 1 km;
- 2 km;
- 5 km;
- 10 km.

Across **27 consecutive-season transitions**, a fixed coordinate node would classify the named colony as leaving the previous node at:

| Node radius | Transitions outside node | False-turnover fraction |
|---|---:|---:|
| 0.5 km | 26 / 27 | 96.3% |
| 1 km | 24 / 27 | 88.9% |
| 2 km | 16 / 27 | 59.3% |
| 5 km | 8 / 27 | 29.6% |
| 10 km | 4 / 27 | 14.8% |

The empirical consecutive-season displacement distribution was:

- median = **2.30 km**;
- q90 = **11.32 km**;
- q95 = **14.52 km**.

Thus a fixed node would need a radius of roughly 14.5 km to contain 95% of the observed consecutive-season location changes in these three named colonies.

### Colony-specific routes

**Astrid** was comparatively spatially stable:

- median displacement = 1.76 km;
- q95 = 2.27 km;
- maximum = 2.41 km;
- 7/9 transitions exceeded 1 km;
- none exceeded 5 km.

**Mertz** was strongly heterogeneous:

- median = 3.91 km;
- q95 = 42.61 km;
- maximum = **63.21 km** from 2022/23 to 2023/24;
- 3/9 transitions exceeded 10 km.

**SANAE** showed recurrent multi-kilometre relocation:

- median = 5.15 km;
- q95 = 12.80 km;
- maximum = 15.72 km;
- all 9 transitions exceeded 1 km;
- 5/9 exceeded 5 km.

These differences are descriptive. With three named colonies, they do not define general colony “types.”

---

## 2. Independent within-season validation

The independent 2024 SAR data contain:

- six emperor colonies;
- 596 mapped huddles;
- 54 colony-date states;
- 48 post-anchor observation dates.

Using exactly the same frozen 0.5/1/2/5/10 km node radii, within-season movement produced:

| Node radius | Post-anchor dates appearing absent | False-absence fraction |
|---|---:|---:|
| 0.5 km | 1 / 48 | 2.1% |
| 1 km | 0 / 48 | 0% |
| 2 km | 0 / 48 | 0% |
| 5 km | 0 / 48 | 0% |
| 10 km | 0 / 48 | 0% |

The distribution of the minimum distance from the seasonal anchor to any mapped huddle on later dates had:

- median = 0.143 km;
- q90 = 0.350 km;
- q95 = **0.389 km**.

Thus, in this independent six-colony winter dataset, a 1 km node retained the colony on every post-anchor observation date.

---

## 3. The ecological result is a timescale separation

The important result is not simply that emperor penguins move.

It is that **the spatial scale needed to preserve colony-site identity differs sharply between within-season and interannual observations**.

Independent within-season SAR data:

\[
q_{95,\ within} \approx 0.39\ {\rm km}
\]

Long-term interannual season-reference data:

\[
q_{95,\ between} \approx 14.52\ {\rm km}.
\]

These values come from independent colony sets and should not be treated as a paired ratio estimate. Descriptively, however, the interannual q95 is about 37 times the within-season q95.

At the particularly interpretable 1 km radius:

- within-season: **0 / 48** later observation dates appear empty;
- interannual: **24 / 27** consecutive-season transitions leave the prior node.

Therefore:

> **Routine within-season colony movement can be absorbed by a modest fixed node, whereas annual re-establishment of a named colony often occurs beyond that node.**

This is stronger than a generic “mobile species” result. The change is in the spatial meaning of the population node across time.

---

## 4. Island-ecology interpretation

Classical empirical patch occupancy attaches persistence to a geographic unit:

\[
\text{patch } i:\quad 1 \rightarrow 0
\]

is interpreted as local extinction, while:

\[
\text{patch } j:\quad 0 \rightarrow 1
\]

is interpreted as colonization.

Dynamic-landscape theory already allows habitat amount, suitability and connectivity to vary through time. Paper 3 does not claim otherwise.

The emperor system exposes a distinct empirical state:

> **the occupied breeding node itself can be re-created at a new coordinate while the source data retain the same named-colony identity.**

A fixed-coordinate observation can therefore decompose one continuing named colony into:

\[
\text{apparent extinction at }L_t
+
\text{apparent colonization at }L_{t+1}.
\]

The biological alternative is:

\[
\text{colony identity persists}
+
\text{breeding node relocates}.
\]

This is a **relocation mode of spatial persistence**.

The term “persistence” here refers to source-provided colony identity, not demographic closure and not proof that the same individual birds remain in the aggregation.

---

## 5. Why the within-season null is important

The low within-season aliasing prevents an easy but weak story.

The result is **not**:

> emperor colonies wander so much that geographic sites are always meaningless.

Instead:

> **geographic site identity is meaningful at short temporal scales, but can fail across breeding seasons.**

That distinction makes the phenomenon ecological rather than merely cartographic.

A monitoring node can be valid for repeated observations within one breeding season and invalid as a persistent population identifier over years.

---

## 6. Relation to Papers 1 and 2

### Paper 1 — spatial contraction within persistent breeding systems

Declining Antarctic Pygoscelis populations repeatedly concentrate reproduction into fewer effective components beyond proportional thinning.

Spatial response mode:

> **contract within persistent nodes.**

### Paper 2 — changing capacity of persistent nodes

Summer-exposed terrestrial breeding opportunity changes substantially, but sites gaining more opportunity do not consistently gain relative breeding use.

Spatial lesson:

> **physical node capacity and biological use are separable.**

### Paper 3 — identity of mobile nodes

Emperor colony identity can remain source-continuous while annual breeding-node location shifts beyond ordinary fixed-site tolerances.

Spatial response mode:

> **persist through node relocation.**

Together, the Antarctic program now distinguishes three quantities that are often collapsed into “site occupancy”:

1. **population / colony identity**;
2. **geographic node identity**;
3. **allocation of breeders within or among nodes**.

---

## 7. What is and is not general

### Supported

Across the three long-term Zenodo colonies, interannual relocation is large enough that fixed nodes of 0.5–5 km frequently generate apparent turnover.

Across an independent six-colony 2024 SAR dataset, within-season false absence is negligible at radii of 1 km or larger.

### Not supported

Do not claim:

- a continent-wide probability of false turnover from three long-term colonies;
- that named colonies are demographically closed;
- that the same individual penguins moved with the node;
- that fast-ice mobility causes the contrast with Pygoscelis;
- that every emperor colony relocates annually;
- that 14.5 km is a universal correct colony radius;
- that the 63 km Mertz transition represents ordinary annual movement.

The radius curve is the result; no single radius is promoted as biologically “true.”

---

## 8. Relation to prior work

Dynamic patch models already represent landscapes whose habitat suitability, size and connectivity change through time.

Recent emperor-penguin studies already show within-season movement and major colony relocation.

The contribution here is narrower:

> **quantify the observational and ecological separation between colony identity and geographic node identity, and show that this separation is strongly time-scale dependent.**

The paper therefore belongs at the intersection of island ecology, metapopulation ecology and colonial breeding ecology rather than as another remote-sensing movement paper.

---

## Working title options

1. **Colony persistence can outlast site persistence in mobile Antarctic breeding habitat**
2. **Mobile breeding nodes decouple colony identity from site identity in emperor penguins**
3. **Persistence without a fixed place: scale-dependent breeding-node identity in emperor penguins**
4. **Annual relocation, not seasonal movement, destabilizes geographic colony identity in emperor penguins**

Option 2 is the cleanest island/metapopulation formulation.

Option 4 is the most directly tied to the empirical contrast.

---

## One-sentence conclusion

> **In emperor penguins, modest geographic nodes retain colony identity within a breeding season, but the same named colonies frequently re-establish beyond those nodes between years, showing that persistence in an ephemeral breeding landscape can be maintained through relocation rather than persistence at a fixed place.**

## Stop rule

The frozen radius curve is closed.

Do not search additional radii, classify post-hoc movement modes, or add environmental drivers to explain the relocation pattern.

Mechanistic attribution requires a separately designed environmental or demographic analysis.

The temporarily unavailable Macdonald et al. 2017–2024 PDC tracking archive remains a future external replication opportunity rather than a reason to modify the present result.
